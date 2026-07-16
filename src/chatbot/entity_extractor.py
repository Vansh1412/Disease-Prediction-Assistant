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

    # ── Pass 2: Fuzzy match for unresolved candidates ─────────────────────
    # Only try candidates that were not already exactly matched
    unresolved = [c for c in candidates if c not in exact_matched_phrases and len(c) > 3]

    for candidate in unresolved:
        # Skip if we already have enough high-confidence matches for short inputs
        best_phrase, ratio = _fuzzy_match(
            candidate, phrase_corpus, threshold=FUZZY_LOW_THRESHOLD
        )
        if not best_phrase or ratio < FUZZY_LOW_THRESHOLD:
            continue

        canonical = get_canonical(best_phrase)
        if not canonical or canonical in matched_canonicals:
            continue
        if dataset_symptoms and canonical not in dataset_symptoms:
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
    # e.g. user says "pain in my arm" but "pain" alone doesn't resolve
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

    logger.debug(
        "EntityExtractor: extracted %d entities (%d negated) from '%s'.",
        len(entities),
        sum(1 for e in entities if e.negated),
        text[:60],
    )
    return entities
