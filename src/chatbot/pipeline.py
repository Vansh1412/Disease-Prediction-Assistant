"""
pipeline.py — Clinical NLP Pipeline
=====================================
The single public entry point for all NLP preprocessing.

Pipeline
--------
User Text
  → Cleaning + Tokenization        (symptom_normalizer)
  → Entity Extraction              (entity_extractor)
  → Synonym Resolution             (synonym_index — done inside entity_extractor)
  → Fuzzy Matching                 (entity_extractor)
  → Negation Detection             (negation_detector — done inside entity_extractor)
  → Temporal Detection             (temporal_parser)
  → Severity Detection             (severity_parser)
  → Body Location Detection        (location_parser)
  → Confidence Estimation          (confidence_estimator)
  → Emergency Detection            (constants.EMERGENCY_COMBINATIONS)
  → Follow-up Question Generation  (templates in this module)
  → ParseResult

Output
------
ParseResult dataclass:
  detected_symptoms   : list[str]   — canonical names (current, not negated)
  negated_symptoms    : list[str]   — canonical names of negated symptoms
  past_symptoms       : list[str]   — canonical names of past symptoms
  severity_label      : str | None
  severity_score      : int
  locations           : list[str]
  confidence          : str         — overall confidence level
  is_emergency        : bool
  emergency_message   : str | None
  followup_questions  : list[str]
  canonical_symptoms  : list[str]   — alias for detected_symptoms (for ML)
  all_entities        : list[SymptomEntity]  — raw entities for debugging
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

from src.chatbot.entity_extractor import SymptomEntity, extract_entities
from src.chatbot.temporal_parser import temporal_tag, extract_duration
from src.chatbot.severity_parser import detect_severity
from src.chatbot.location_parser import detect_locations
from src.chatbot.constants import (
    Confidence,
    EMERGENCY_COMBINATIONS,
    EMERGENCY_SINGLE_KEYWORDS,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ParseResult
# ---------------------------------------------------------------------------

@dataclass
class ParseResult:
    """Structured output of the Clinical NLP Pipeline."""
    detected_symptoms: list[str] = field(default_factory=list)
    negated_symptoms: list[str] = field(default_factory=list)
    past_symptoms: list[str] = field(default_factory=list)
    severity_label: Optional[str] = None
    severity_score: int = 0
    locations: list[str] = field(default_factory=list)
    confidence: str = Confidence.LOW
    is_emergency: bool = False
    emergency_message: Optional[str] = None
    followup_questions: list[str] = field(default_factory=list)
    all_entities: list[SymptomEntity] = field(default_factory=list)
    temporal: str = "unknown"
    duration: Optional[str] = None

    @property
    def canonical_symptoms(self) -> list[str]:
        """Alias for detected_symptoms — the list passed to the ML predictor."""
        return self.detected_symptoms


# ---------------------------------------------------------------------------
# Emergency detection
# ---------------------------------------------------------------------------

def _check_emergency(
    text: str,
    detected_symptoms: list[str],
) -> tuple[bool, str | None]:
    """
    Return (is_emergency, emergency_message).
    Checks single-keyword triggers first, then combination triggers.
    """
    lower = text.lower()

    # Single-keyword triggers
    for keyword in EMERGENCY_SINGLE_KEYWORDS:
        if keyword in lower:
            return True, (
                f"⚠️ MEDICAL EMERGENCY: You mentioned '{keyword}'. "
                "Please call emergency services immediately or go to the nearest emergency room."
            )

    # Combination triggers
    symptom_set = set(detected_symptoms)
    for required_set, message in EMERGENCY_COMBINATIONS:
        overlap = symptom_set & required_set
        # Trigger if at least 2 symptoms from the combination are present
        if len(overlap) >= 2:
            return True, message

    return False, None


# ---------------------------------------------------------------------------
# Follow-up question generation (deterministic, no LLM)
# ---------------------------------------------------------------------------

# Templates: canonical_symptom → list of follow-up questions
_FOLLOWUP_TEMPLATES: dict[str, list[str]] = {
    "chest tightness": [
        "Is the chest sensation more of a pressure, squeezing, or sharp stabbing pain?",
        "Does the sensation radiate to your left arm, jaw, or back?",
        "Are you experiencing any shortness of breath along with it?",
        "How long has this been going on?",
        "Are you sweating or feeling nauseous?",
    ],
    "shortness of breath": [
        "Is the breathlessness worse with activity or also at rest?",
        "Do you hear any wheezing when you breathe?",
        "Are you able to lie flat comfortably, or do you need to sit up?",
        "How long have you been feeling breathless?",
    ],
    "headache": [
        "Is the headache throbbing, pressure-like, or sharp?",
        "Where exactly is the pain — front, back, sides, or all over?",
        "How severe is it on a scale of 1 to 10?",
        "Is it associated with sensitivity to light or sound?",
        "How long has it been present?",
    ],
    "fever": [
        "Have you measured your temperature? If so, what was it?",
        "How long have you had the fever?",
        "Are you experiencing chills or sweating?",
        "Have you taken any fever-reducing medication?",
    ],
    "nausea": [
        "Have you actually vomited, or just felt nauseous?",
        "Is the nausea related to eating or does it occur on its own?",
        "How long have you been feeling nauseous?",
        "Is there any abdominal pain along with it?",
    ],
    "vomiting": [
        "How many times have you vomited?",
        "Is there any blood in the vomit?",
        "Are you able to keep any fluids down?",
        "How long have you been vomiting?",
    ],
    "dizziness": [
        "Does the dizziness feel like the room is spinning (vertigo) or like you might faint?",
        "Is it worse when you change position or stand up?",
        "Have you had any falls?",
        "Is it associated with nausea or hearing changes?",
    ],
    "abdominal pain": [
        "Where exactly in the abdomen is the pain?",
        "Is the pain constant or does it come and go?",
        "Is it sharp, crampy, or dull?",
        "Does it get worse after eating?",
        "Do you have any changes in your bowel habits along with it?",
    ],
    "lower abdominal pain": [
        "Is the pain constant or crampy?",
        "Does it spread to your back or groin?",
        "Are you experiencing any urinary symptoms alongside the pain?",
        "For women: is this related to your menstrual cycle?",
    ],
    "upper abdominal pain": [
        "Does the pain get worse after eating or drinking alcohol?",
        "Is there any nausea or vomiting with it?",
        "Does the pain radiate to your back?",
        "Is it burning or gnawing in character?",
    ],
    "cough": [
        "Is your cough dry or are you bringing up mucus?",
        "What colour is the mucus if any?",
        "How long have you been coughing?",
        "Is the cough worse at night or early morning?",
    ],
    "fatigue": [
        "How long have you been feeling this way?",
        "Is it present even after a good night's sleep?",
        "Are there any other symptoms accompanying the fatigue?",
        "Have you had any recent illness or stress?",
    ],
    "back pain": [
        "Is the pain in your upper, middle, or lower back?",
        "Does it radiate down your legs?",
        "Is it constant or does it come and go?",
        "Does it improve or worsen with rest?",
    ],
    "low back pain": [
        "Does the pain travel down one or both legs?",
        "Is there any numbness or tingling in your legs?",
        "Is it worse in the morning or after prolonged sitting?",
        "Have you had any recent injury or heavy lifting?",
    ],
    "sore throat": [
        "Is it painful to swallow?",
        "Is the throat visibly red or do you have white patches?",
        "Do you have a fever along with it?",
        "How long have you had the sore throat?",
    ],
    "joint pain": [
        "Which joints are affected?",
        "Are the joints swollen or red as well?",
        "Is the pain symmetrical on both sides?",
        "Is it worse in the morning and improves through the day?",
    ],
    "difficulty breathing": [
        "Is it hard to breathe in, breathe out, or both?",
        "Does it come on suddenly or has it been gradual?",
        "Any wheezing or chest tightness along with it?",
        "Have you been exposed to any allergens or smoke?",
    ],
    "insomnia": [
        "Do you have difficulty falling asleep or staying asleep?",
        "How many hours of sleep are you getting?",
        "Are you experiencing anxiety or stress that keeps you awake?",
        "How long has the sleep problem been occurring?",
    ],
    "diarrhea": [
        "How many times a day are you passing loose stool?",
        "Is there any blood or mucus in the stool?",
        "Have you eaten anything unusual recently?",
        "Are you staying hydrated?",
    ],
    "constipation": [
        "How many days have you gone without a bowel movement?",
        "Is the stool very hard when you do go?",
        "Are you drinking enough water and eating fiber?",
        "Do you have any abdominal pain with it?",
    ],
    "skin rash": [
        "Where on your body is the rash?",
        "Is it raised, flat, blistered, or scaly?",
        "Is it itchy, painful, or neither?",
        "Have you been exposed to any new products or environments?",
    ],
    "ankle swelling": [
        "Is the swelling in one ankle or both?",
        "Does pressing on the swelling leave an indent (pitting)?",
        "Does it worsen throughout the day?",
        "Do you have any chest pain or breathlessness with it?",
    ],
    "irregular heartbeat": [
        "Does your heart feel like it is racing, skipping, or fluttering?",
        "How long do the episodes last?",
        "Are you feeling dizzy or faint during the episodes?",
        "Do you have any chest pain or shortness of breath?",
    ],
    "frequent urination": [
        "How many times a day are you urinating?",
        "Is there any pain or burning when you urinate?",
        "Are you drinking more fluids than usual?",
        "Do you wake up at night to urinate?",
    ],
    "depression": [
        "How long have you been feeling this way?",
        "Are you having any thoughts of harming yourself?",
        "Are you still able to enjoy activities you used to?",
        "How is your sleep and appetite?",
    ],
    "anxiety and nervousness": [
        "How long have you been feeling anxious?",
        "Is there a specific trigger or does it feel constant?",
        "Are you having any panic attacks?",
        "Is the anxiety affecting your daily life?",
    ],
    "default": [
        "How long have you been experiencing this symptom?",
        "How would you rate the severity on a scale of 1 to 10?",
        "Is it constant or does it come and go?",
        "Have you tried any treatments or medications?",
        "Are there any other symptoms you have noticed?",
    ],
}


@lru_cache(maxsize=256)
def _get_followup_questions(canonical: str) -> list[str]:
    """Cache follow-up question lookup per canonical symptom."""
    return _FOLLOWUP_TEMPLATES.get(canonical, _FOLLOWUP_TEMPLATES["default"])


def _generate_followup(symptoms: list[str], max_questions: int = 4) -> list[str]:
    """
    Generate follow-up questions for the most prominent detected symptoms.
    Prioritizes the first symptom's template; supplements with generic if needed.
    """
    if not symptoms:
        return _FOLLOWUP_TEMPLATES["default"][:max_questions]

    questions: list[str] = []
    # Primary: questions for the first (most specific) symptom
    primary_qs = _get_followup_questions(symptoms[0])
    questions.extend(primary_qs[:max_questions])

    # Secondary: one extra question from the second symptom if available
    if len(symptoms) > 1 and len(questions) < max_questions + 1:
        secondary = _get_followup_questions(symptoms[1])
        if secondary and secondary[0] not in questions:
            questions.append(secondary[0])

    return questions[:max_questions + 1]


# ---------------------------------------------------------------------------
# Overall confidence aggregation
# ---------------------------------------------------------------------------

def _aggregate_confidence(entities: list[SymptomEntity]) -> str:
    """
    Aggregate individual entity confidences to an overall pipeline confidence.
    If the majority are HIGH → HIGH; any MEDIUM → MEDIUM; else LOW.
    """
    if not entities:
        return Confidence.LOW

    scores = [e.confidence_score for e in entities if not e.negated]
    if not scores:
        return Confidence.LOW

    avg = sum(scores) / len(scores)
    if avg >= 0.85:
        return Confidence.HIGH
    if avg >= 0.55:
        return Confidence.MEDIUM
    return Confidence.LOW


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run(
    text: str,
    dataset_symptoms: list[str] | None = None,
) -> ParseResult:
    """
    Run the full Clinical NLP Pipeline on a single user message.

    Parameters
    ----------
    text             : raw user input
    dataset_symptoms : optional list of canonical symptom names from the ML dataset.
                       If provided, only symptoms present in this list are returned.

    Returns
    -------
    ParseResult
    """
    result = ParseResult()

    if not text or not text.strip():
        return result

    # ── Step 1: Temporal tag for the whole message ─────────────────────────
    tag = temporal_tag(text)
    duration = extract_duration(text)
    
    result.temporal = tag
    result.duration = duration

    # ── Step 2: Severity ────────────────────────────────────────────────────
    sev_label, sev_score = detect_severity(text)
    result.severity_label = sev_label
    result.severity_score = sev_score

    # ── Step 3: Body locations ──────────────────────────────────────────────
    from src.chatbot.symptom_normalizer import normalize
    result.locations = detect_locations(normalize(text))

    # ── Step 4: Entity extraction ───────────────────────────────────────────
    entities = extract_entities(text, dataset_symptoms=dataset_symptoms)

    # Enrich each entity with temporal + duration
    for entity in entities:
        entity.temporal = tag
        entity.duration = duration
        entity.severity_label = sev_label
        entity.severity_score = sev_score

    result.all_entities = entities

    # ── Step 5: Partition into detected / negated / past ───────────────────
    for entity in entities:
        if entity.negated:
            result.negated_symptoms.append(entity.canonical)
        elif entity.temporal == "past":
            result.past_symptoms.append(entity.canonical)
        else:
            # current or unknown → goes to ML predictor
            result.detected_symptoms.append(entity.canonical)

    # ── Step 6: Emergency check ─────────────────────────────────────────────
    result.is_emergency, result.emergency_message = _check_emergency(
        text, result.detected_symptoms
    )

    # ── Step 7: Confidence ──────────────────────────────────────────────────
    result.confidence = _aggregate_confidence(entities)

    # ── Step 8: Follow-up questions ─────────────────────────────────────────
    result.followup_questions = _generate_followup(result.detected_symptoms)

    logger.info(
        "Pipeline: '%s...' → detected=%s negated=%s past=%s emergency=%s",
        text[:40],
        result.detected_symptoms,
        result.negated_symptoms,
        result.past_symptoms,
        result.is_emergency,
    )

    return result


def run_simple(text: str, dataset_symptoms: list[str] | None = None) -> list[str]:
    """
    Convenience wrapper: run the pipeline and return only the canonical symptom list.
    Drop-in replacement for the old parse_symptoms() function.
    """
    return run(text, dataset_symptoms=dataset_symptoms).canonical_symptoms
