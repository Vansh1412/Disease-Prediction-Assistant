"""
conversation_scoring.py — Clinical Confidence Scoring Engine
=============================================================
Computes a numeric confidence score (0.0–1.0) representing how much
clinical information has been gathered and how specific it is.

Score is COMPLETELY DETERMINISTIC — no LLM, no ML models.

Score Components
----------------
  symptom_coverage   (0–0.35)  Number and specificity of symptoms
  duration_score     (0–0.15)  Duration of illness provided
  severity_score     (0–0.15)  Severity quantified
  specificity_score  (0–0.20)  Diagnostic specificity of symptom set
  consistency_score  (0–0.10)  Internal coherence
  engagement_score   (0–0.05)  Patient engagement / answers given

Thresholds (configurable)
--------------------------
  < 0.45  → COLLECTING      — Need more symptoms
  0.45–0.65 → FOLLOWUP      — Have baseline, want richer detail
  0.65–0.80 → GOOD          — Good data; can attempt prediction
  > 0.80  → HIGH            — High confidence, predict now
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from src.chatbot.conversation_state import ConversationState

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Thresholds (all configurable by changing these constants)
# ---------------------------------------------------------------------------

THRESHOLD_COLLECTING  = 0.45   # below → keep collecting
THRESHOLD_FOLLOWUP    = 0.65   # 0.45–0.65 → ask follow-ups
THRESHOLD_PREDICT     = 0.80   # above → ready to predict

# Minimum symptoms required before scoring above THRESHOLD_COLLECTING
MIN_SYMPTOMS_FOR_FOLLOWUP = 2
MIN_SYMPTOMS_FOR_PREDICTION = 3

# ---------------------------------------------------------------------------
# High-specificity symptoms — symptoms that carry strong diagnostic weight
# ---------------------------------------------------------------------------

_HIGH_SPECIFICITY_SYMPTOMS: frozenset[str] = frozenset({
    "chest tightness", "chest pain", "shortness of breath", "difficulty breathing",
    "irregular heartbeat", "palpitations", "jaw pain", "arm pain",
    "slurred speech", "arm weakness", "facial droop", "sudden severe headache",
    "thunderclap headache", "loss of consciousness", "seizures",
    "vomiting blood", "blood in stool",
    "skin rash", "hives", "anaphylaxis",
    "high fever", "fever", "rigors", "night sweats",
    "jaundice", "dark urine", "pale stools",
    "unintentional weight loss", "fatigue",
    "frequent urination", "excessive thirst",
    "urinary burning", "flank pain",
    "rectal bleeding", "blood in urine",
    "joint swelling", "morning stiffness",
    "depression", "anxiety and nervousness", "suicidal thoughts",
    "dizziness", "fainting",
})

# Symptom groups that are highly specific to a single body system
_BODY_SYSTEM_SPECIFICITY: dict[str, list[str]] = {
    "cardiac":      ["chest pain", "chest tightness", "irregular heartbeat", "palpitations",
                     "shortness of breath", "jaw pain", "arm pain"],
    "neurological": ["headache", "dizziness", "seizures", "loss of consciousness",
                     "arm weakness", "facial droop", "slurred speech"],
    "respiratory":  ["cough", "shortness of breath", "difficulty breathing",
                     "wheezing", "chest tightness"],
    "gastrointestinal": ["nausea", "vomiting", "diarrhoea", "abdominal pain",
                         "lower abdominal pain", "upper abdominal pain",
                         "constipation", "blood in stool"],
    "musculoskeletal":  ["back pain", "low back pain", "joint pain", "muscle pain",
                         "neck pain", "knee pain", "shoulder pain"],
    "psychiatric":  ["depression", "anxiety and nervousness", "insomnia",
                     "suicidal thoughts", "panic attacks"],
}


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for transparency."""
    symptom_coverage:  float = 0.0
    duration_score:    float = 0.0
    severity_score:    float = 0.0
    specificity_score: float = 0.0
    consistency_score: float = 0.0
    engagement_score:  float = 0.0

    @property
    def total(self) -> float:
        return round(
            self.symptom_coverage
            + self.duration_score
            + self.severity_score
            + self.specificity_score
            + self.consistency_score
            + self.engagement_score,
            4,
        )

    def to_dict(self) -> dict:
        return {
            "symptom_coverage":  round(self.symptom_coverage, 3),
            "duration_score":    round(self.duration_score, 3),
            "severity_score":    round(self.severity_score, 3),
            "specificity_score": round(self.specificity_score, 3),
            "consistency_score": round(self.consistency_score, 3),
            "engagement_score":  round(self.engagement_score, 3),
            "total":             round(self.total, 3),
        }


# ---------------------------------------------------------------------------
# Scoring functions (each returns a float in their stated range)
# ---------------------------------------------------------------------------

def _score_symptom_coverage(state: ConversationState) -> float:
    """Max 0.35. More symptoms = higher score, with diminishing returns."""
    n = len(state.detected_symptoms)
    if n == 0:
        return 0.0
    if n == 1:
        return 0.10
    if n == 2:
        return 0.18
    if n == 3:
        return 0.25
    if n == 4:
        return 0.30
    # 5+ symptoms
    return min(0.35, 0.30 + (n - 4) * 0.02)


def _score_duration(state: ConversationState) -> float:
    """Max 0.15. Having a duration string is a strong signal."""
    if state.duration is None:
        return 0.0
    lower = state.duration.lower()
    # "3 days", "2 weeks" etc → full score
    if any(unit in lower for unit in ["day", "week", "month", "hour", "year"]):
        return 0.15
    # "since yesterday" → partial
    if "since" in lower or "yesterday" in lower:
        return 0.10
    return 0.05


def _score_severity(state: ConversationState) -> float:
    """Max 0.15. A specified severity level is a signal."""
    s = state.severity_score
    if s == 0:
        return 0.0
    if s == 1:
        return 0.05    # mild
    if s == 2:
        return 0.08    # moderate
    if s == 3:
        return 0.12    # severe
    return 0.15        # extreme


def _score_specificity(state: ConversationState) -> float:
    """
    Max 0.20. Measures how diagnostically specific the symptom set is.
    High-specificity symptoms score higher.
    Body-system coherence (symptoms from same system) scores higher.
    """
    symptoms = set(state.detected_symptoms)
    if not symptoms:
        return 0.0

    # High-specificity bonus
    hs_count = len(symptoms & _HIGH_SPECIFICITY_SYMPTOMS)
    hs_bonus = min(0.12, hs_count * 0.04)

    # Body system coherence
    best_overlap = 0
    for system_symptoms in _BODY_SYSTEM_SPECIFICITY.values():
        overlap = len(symptoms & set(system_symptoms))
        best_overlap = max(best_overlap, overlap)
    coherence_bonus = min(0.08, best_overlap * 0.03)

    return min(0.20, hs_bonus + coherence_bonus)


def _score_consistency(state: ConversationState) -> float:
    """
    Max 0.10. Rewards absence of contradictions (negating symptoms that
    also appear as detected, or no information conflicts).
    """
    detected = set(state.detected_symptoms)
    negated  = set(state.negated_symptoms)
    # Penalise if a symptom appears in both detected and negated
    contradictions = len(detected & negated)
    if contradictions > 0:
        return max(0.0, 0.10 - contradictions * 0.05)
    # No contradictions + some information = good
    if state.turn_count >= 2:
        return 0.10
    return 0.05


def _score_engagement(state: ConversationState) -> float:
    """Max 0.05. Rewards having answered follow-up questions."""
    answers = len(state.answers_given)
    if answers == 0:
        return 0.0
    if answers == 1:
        return 0.02
    if answers == 2:
        return 0.03
    return min(0.05, 0.03 + (answers - 2) * 0.01)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_score(state: ConversationState) -> ScoreBreakdown:
    """
    Compute the full clinical confidence score breakdown for a state.
    Updates state.clinical_confidence and state.confidence_breakdown.

    Returns
    -------
    ScoreBreakdown
    """
    bd = ScoreBreakdown(
        symptom_coverage  = _score_symptom_coverage(state),
        duration_score    = _score_duration(state),
        severity_score    = _score_severity(state),
        specificity_score = _score_specificity(state),
        consistency_score = _score_consistency(state),
        engagement_score  = _score_engagement(state),
    )
    # Persist back into state
    state.clinical_confidence    = bd.total
    state.confidence_breakdown   = bd.to_dict()

    logger.debug("ConversationScore: %s", bd.to_dict())
    return bd


def confidence_label(score: float) -> str:
    """Return a human-readable label for a confidence score."""
    if score < THRESHOLD_COLLECTING:
        return "Gathering Information"
    if score < THRESHOLD_FOLLOWUP:
        return "Building Clinical Picture"
    if score < THRESHOLD_PREDICT:
        return "Good Clinical Picture"
    return "High Confidence"


def progress_percentage(state: ConversationState) -> int:
    """Return consultation progress as 0-100 integer."""
    return min(100, int(state.clinical_confidence * 100))
