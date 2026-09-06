"""
entity_extractor.py — Symptom Entity Extraction
================================================
The main symptom-finding engine.

Algorithm
---------
1. Normalize & tokenize text into n-gram candidates
2. Exact match each candidate against the synonym index → HIGH confidence
3. Fuzzy match unresolved candidates against the phrase corpus → MEDIUM/LOW
4. Apply negation detection per clause
5. Apply location enrichment for generic symptom tokens
6. Return SymptomEntity objects

This module is the only one that calls:
  - symptom_normalizer
  - synonym_index
  - negation_detector
  - location_parser
  - confidence_estimator

And optionally (if installed):
  - rapidfuzz  (graceful fallback to stdlib difflib if unavailable)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SymptomEntity:
    """Structured representation of a detected symptom."""
    canonical: str                    # Canonical dataset symptom name
    matched_phrase: str               # The user phrase that triggered this
    confidence: str                   # "high" | "medium" | "low"
    confidence_score: float           # 0.0 – 1.0
    negated: bool = False             # True if the symptom was negated
    severity_label: Optional[str] = None
    severity_score: int = 0
    locations: list[str] = field(default_factory=list)
    temporal: str = "unknown"         # "current" | "past" | "unknown"
    duration: Optional[str] = None
    fuzzy_ratio: Optional[int] = None # RapidFuzz score if fuzzy path was used


# ---------------------------------------------------------------------------
# Fuzzy backend (rapidfuzz preferred, difflib fallback)
# ---------------------------------------------------------------------------

def _fuzzy_match(
    query: str,
    corpus: list[str],
    threshold: int,
) -> tuple[str | None, int]:
    """
    Find the best match for query in corpus above threshold.
    Returns (best_phrase, score) or (None, 0).
    """
    try:
        from rapidfuzz import process, fuzz  # type: ignore
        result = process.extractOne(
            query,
            corpus,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=threshold,
        )
        if result:
            return result[0], int(result[1])
        return None, 0
    except ImportError:
        # Fallback: difflib SequenceMatcher
        import difflib
        matches = difflib.get_close_matches(query, corpus, n=1, cutoff=threshold / 100)
        if matches:
            # Approximate score
            ratio = difflib.SequenceMatcher(None, query, matches[0]).ratio()
            return matches[0], int(ratio * 100)
        return None, 0


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_entities(
    text: str,
    dataset_symptoms: list[str] | None = None,
) -> list[SymptomEntity]:
    """
    Extract symptom entities from raw user text.

    Parameters
    ----------
    text             : raw user text
    dataset_symptoms : optional list of canonical symptom names from the dataset.
                       If provided, matched canonicals are validated against it.

    Returns
    -------
    list[SymptomEntity] — may include negated entities (caller must filter)
    """
    from src.chatbot.symptom_normalizer import normalize, tokenize
    from src.chatbot.synonym_index import get_canonical, all_phrases
    from src.chatbot.negation_detector import is_negated, split_clauses
    from src.chatbot.location_parser import detect_locations, enrich_symptom_with_location
    from src.chatbot.confidence_estimator import confidence_score, estimate_from_fuzzy_score
    from src.chatbot.constants import (
        Confidence, FUZZY_LOW_THRESHOLD
    )

    normalized = normalize(text)
    candidates = tokenize(normalized)
    phrase_corpus = all_phrases()

    # Detect locations once for the whole text
    locations = detect_locations(normalized)

    # Clause-split for negation scope
    clauses = split_clauses(normalized)

    entities: list[SymptomEntity] = []
    matched_canonicals: set[str] = set()   # prevent duplicate canonicals

    def _check_negated(phrase: str) -> bool:
        """Check phrase against all clauses."""
        for clause in clauses:
            if phrase in clause:
                return is_negated(phrase, clause)
        return is_negated(phrase, normalized)

    # ── Pass 1: Exact / dictionary match ──────────────────────────────────
    exact_matched_phrases: set[str] = set()
    for candidate in candidates:
        canonical = get_canonical(candidate)
        if canonical and canonical not in matched_canonicals:
            # Validate against dataset if provided
            if dataset_symptoms and canonical not in dataset_symptoms:
                continue
            negated = _check_negated(candidate)
            matched_canonicals.add(canonical)
            exact_matched_phrases.add(candidate)
            entities.append(SymptomEntity(
                canonical=canonical,
                matched_phrase=candidate,
                confidence=Confidence.HIGH,
                confidence_score=confidence_score(Confidence.HIGH),
                negated=negated,
                locations=locations,
                temporal="unknown",   # set by temporal_parser in pipeline
                duration=None,
            ))

    # ── Body-part word lookup (used to validate fuzzy matches) ────────────
    # Build a flat set of every body-part keyword from constants.BODY_LOCATIONS
    # so we can check: "does this matched symptom mention a body part that the
    # user never said?"
    from src.chatbot.constants import BODY_LOCATIONS as _BODY_LOCATIONS
    _BODY_PART_WORDS: set[str] = set()
    for _loc_label, _loc_phrases in _BODY_LOCATIONS.items():
        for _ph in _loc_phrases:
            _BODY_PART_WORDS.update(_ph.lower().split())
    # Remove very short / ambiguous words from the set
    _BODY_PART_WORDS -= {"the", "of", "in", "or", "and", "a", "an",
                         "eye", "ear", "leg", "arm", "hip", "lip"}

    # ── Pass 2: Fuzzy match for unresolved candidates ─────────────────────
    # Only try candidates that were not already exactly matched.
    # Guard: skip single tokens that are very generic (e.g. "pain", "feeling")
    # to prevent them fuzzy-matching specific multi-word symptoms like "arm pain".
    _GENERIC_SINGLE_TOKENS = {
        "pain", "ache", "feeling", "ill", "sick", "hurt", "hurts",
        "sore", "bad", "poor", "sensation", "discomfort", "problem", "issue",
    }
    unresolved = [
        c for c in candidates
        if c not in exact_matched_phrases
        and len(c) >= 8                        # minimum 8 chars avoids junk n-grams
        and c not in _GENERIC_SINGLE_TOKENS    # skip standalone generic words
    ]

    for candidate in unresolved:
        best_phrase, ratio = _fuzzy_match(
            candidate, phrase_corpus, threshold=FUZZY_LOW_THRESHOLD
        )
        if not best_phrase or ratio < FUZZY_LOW_THRESHOLD:
            continue

        # Length-ratio guard: don't match a short candidate to a much longer phrase.
        # E.g. "in chest" (2 words) should not match "congestion in chest" (3 words).
        candidate_words = len(candidate.split())
        best_phrase_words = len(best_phrase.split())
        if best_phrase_words > candidate_words + 1:
            logger.debug(
                "Fuzzy skip (length): '%s' (%d words) vs phrase '%s' (%d words).",
                candidate, candidate_words, best_phrase, best_phrase_words,
            )
            continue

        canonical = get_canonical(best_phrase)
        if not canonical or canonical in matched_canonicals:
            continue
        if dataset_symptoms and canonical not in dataset_symptoms:
            continue

        # ── Body-part coherence check ──────────────────────────────────────
        # If the matched canonical symptom name contains a body-part keyword
        # (e.g. "groin", "finger", "hand") that does NOT appear anywhere in
        # the user's original text or detected locations, reject the match.
        # This is the key fix for "pain in chest" → "groin pain" false matches.
        canonical_words = set(canonical.lower().split())
        body_parts_in_canonical = canonical_words & _BODY_PART_WORDS
        if body_parts_in_canonical:
            user_text_lower = normalized.lower()
            user_locations_lower = {loc.lower() for loc in locations}
            any_body_part_in_text = any(
                bp in user_text_lower or bp in user_locations_lower
                for bp in body_parts_in_canonical
            )
            if not any_body_part_in_text:
                logger.debug(
                    "Fuzzy skip (coherence): canonical '%s' has body parts %s "
                    "not found in user text '%s'.",
                    canonical, body_parts_in_canonical, normalized[:60],
                )
                continue

        conf_level = estimate_from_fuzzy_score(ratio)
        negated = _check_negated(candidate)
        matched_canonicals.add(canonical)
        entities.append(SymptomEntity(
            canonical=canonical,
            matched_phrase=candidate,
            confidence=conf_level,
            confidence_score=confidence_score(conf_level),
            negated=negated,
            locations=locations,
            temporal="unknown",
            duration=None,
            fuzzy_ratio=ratio,
        ))


    # ── Pass 3: Location enrichment for generic terms ─────────────────────
    # e.g. user says "pain in my arm" but "pain" alone doesn't resolve.
    # Only enriches using body locations that actually appear in the user's text.
    _GENERIC_SYMPTOMS = {"pain", "ache", "weakness", "swelling", "stiffness", "cramp"}
    for candidate in candidates:
        if candidate in _GENERIC_SYMPTOMS and locations:
            enriched = enrich_symptom_with_location(candidate, locations)
            for enriched_symptom in enriched:
                if enriched_symptom and enriched_symptom not in matched_canonicals:
                    if dataset_symptoms and enriched_symptom not in dataset_symptoms:
                        continue
                    matched_canonicals.add(enriched_symptom)
                    negated = _check_negated(candidate)
                    entities.append(SymptomEntity(
                        canonical=enriched_symptom,
                        matched_phrase=f"{candidate} [{locations}]",
                        confidence=Confidence.MEDIUM,
                        confidence_score=confidence_score(Confidence.MEDIUM),
                        negated=negated,
                        locations=locations,
                        temporal="unknown",
                        duration=None,
                    ))

    # ── Pass 4: Final body-part coherence filter ───────────────────────────
    # Remove any entity whose canonical name contains a body-part word that
    # does NOT appear in the user's text or detected locations.
    # This is the safety net that catches any false positives that slipped
    # through Passes 1–3 (e.g. exact-match synonyms for wrong body parts).
    user_text_lower = normalized.lower()
    user_locations_lower = {loc.lower() for loc in locations}
    filtered_entities: list[SymptomEntity] = []
    for ent in entities:
        canon_words = set(ent.canonical.lower().split())
        body_parts_in_canon = canon_words & _BODY_PART_WORDS
        if body_parts_in_canon:
            # At least one body-part word in the canonical must be present
            # in what the user actually said or in detected locations.
            found = any(
                bp in user_text_lower or bp in user_locations_lower
                for bp in body_parts_in_canon
            )
            if not found:
                logger.debug(
                    "Pass 4 filter: removed '%s' (body parts %s absent from text).",
                    ent.canonical, body_parts_in_canon,
                )
                continue
        filtered_entities.append(ent)
    entities = filtered_entities

    logger.debug(
        "EntityExtractor: extracted %d entities (%d negated) from '%s'.",
        len(entities),
        sum(1 for e in entities if e.negated),
        text[:60],
    )
    return entities
