"""
conversation_state.py — Clinical Session State
================================================
A pure-Python dataclass that holds the complete clinical state for one
consultation session.  No Streamlit, no LLM, no network calls.

Designed to be stored in st.session_state["clinical_state"] by the
conversation manager; serialisable to dict for persistence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ConversationPhase(str, Enum):
    """Tracks where in the consultation flow we currently are."""
    GREETING          = "greeting"
    COLLECTING        = "collecting"      # Gathering initial symptoms
    FOLLOWUP          = "followup"        # Targeted follow-up questions
    READY_TO_PREDICT  = "ready_to_predict"
    PREDICTED         = "predicted"
    SUMMARY           = "summary"
    EMERGENCY         = "emergency"


class PredictionStatus(str, Enum):
    COLLECTING_INFORMATION = "Collecting Information"
    ASKING_FOLLOWUPS       = "Asking Follow-ups"
    PREDICTION_AVAILABLE   = "Prediction Available"
    PREDICTION_COMPLETE    = "Prediction Complete"
    EMERGENCY              = "Emergency"


# ---------------------------------------------------------------------------
# Per-turn record
# ---------------------------------------------------------------------------

@dataclass
class TurnRecord:
    """A single conversation exchange."""
    turn_number:     int
    user_input:      str
    assistant_reply: str
    detected_symptoms: list[str]  = field(default_factory=list)
    negated_symptoms:  list[str]  = field(default_factory=list)
    past_symptoms:     list[str]  = field(default_factory=list)
    severity_score:    int        = 0
    locations:         list[str]  = field(default_factory=list)
    temporal:          str        = "unknown"
    duration:          Optional[str] = None


# ---------------------------------------------------------------------------
# Core state object
# ---------------------------------------------------------------------------

@dataclass
class ConversationState:
    """
    Complete clinical state for one consultation session.

    All fields are plain Python types so the object can be stored in
    st.session_state and serialised without issue.
    """

    # ── Demographics ──────────────────────────────────────────────────────
    patient_age:    str = "Unknown"
    patient_gender: str = "Unknown"

    # ── Symptom collections ───────────────────────────────────────────────
    detected_symptoms:  list[str] = field(default_factory=list)   # current, confirmed
    negated_symptoms:   list[str] = field(default_factory=list)   # "I don't have…"
    past_symptoms:      list[str] = field(default_factory=list)   # temporal past
    resolved_symptoms:  list[str] = field(default_factory=list)   # no longer present

    # ── Clinical enrichment ───────────────────────────────────────────────
    duration:       Optional[str] = None      # "3 days", "since yesterday"
    severity_label: Optional[str] = None      # "mild", "severe", …
    severity_score: int           = 0         # 0–4
    body_locations: list[str]     = field(default_factory=list)

    # ── Demographics mentioned ────────────────────────────────────────────
    medications_mentioned: list[str] = field(default_factory=list)
    allergies_mentioned:   list[str] = field(default_factory=list)
    medical_history:       list[str] = field(default_factory=list)

    # ── Emergency ─────────────────────────────────────────────────────────
    is_emergency:      bool          = False
    emergency_message: Optional[str] = None

    # ── Conversation metadata ─────────────────────────────────────────────
    phase:              ConversationPhase = ConversationPhase.GREETING
    prediction_status:  PredictionStatus  = PredictionStatus.COLLECTING_INFORMATION
    turn_count:         int               = 0
    questions_asked:    list[str]         = field(default_factory=list)  # exact text
    answers_given:      list[str]         = field(default_factory=list)
    turn_history:       list[TurnRecord]  = field(default_factory=list)

    # ── Confidence ────────────────────────────────────────────────────────
    clinical_confidence:  float = 0.0    # 0.0–1.0
    confidence_breakdown: dict  = field(default_factory=dict)

    # ── Prediction ────────────────────────────────────────────────────────
    prediction_result: Optional[dict] = None
    prediction_ready:  bool           = False

    # ── Clinical notes ────────────────────────────────────────────────────
    clinical_notes: list[str] = field(default_factory=list)

    # ── Progress ──────────────────────────────────────────────────────────
    @property
    def progress_pct(self) -> int:
        """
        Rough consultation progress percentage (0-100).
        Derived from clinical_confidence, capped at 90 until prediction done.
        """
        if self.phase == ConversationPhase.PREDICTED:
            return 100
        if self.phase == ConversationPhase.EMERGENCY:
            return 100
        return min(90, int(self.clinical_confidence * 100))

    @property
    def symptom_count(self) -> int:
        return len(self.detected_symptoms)

    def add_symptom(self, symptom: str) -> None:
        if symptom and symptom not in self.detected_symptoms:
            self.detected_symptoms.append(symptom)

    def add_note(self, note: str) -> None:
        self.clinical_notes.append(note)

    def mark_question_asked(self, question: str) -> None:
        if question not in self.questions_asked:
            self.questions_asked.append(question)

    def to_dict(self) -> dict:
        """Serialise to a plain dict (for persistence / debugging)."""
        return {
            "patient_age":         self.patient_age,
            "patient_gender":      self.patient_gender,
            "detected_symptoms":   self.detected_symptoms,
            "negated_symptoms":    self.negated_symptoms,
            "past_symptoms":       self.past_symptoms,
            "resolved_symptoms":   self.resolved_symptoms,
            "duration":            self.duration,
            "severity_label":      self.severity_label,
            "severity_score":      self.severity_score,
            "body_locations":      self.body_locations,
            "medications_mentioned": self.medications_mentioned,
            "allergies_mentioned": self.allergies_mentioned,
            "medical_history":     self.medical_history,
            "is_emergency":        self.is_emergency,
            "emergency_message":   self.emergency_message,
            "phase":               self.phase.value,
            "prediction_status":   self.prediction_status.value,
            "turn_count":          self.turn_count,
            "questions_asked":     self.questions_asked,
            "clinical_confidence": self.clinical_confidence,
            "confidence_breakdown": self.confidence_breakdown,
            "prediction_ready":    self.prediction_ready,
            "clinical_notes":      self.clinical_notes,
        }

    @classmethod
    def fresh(cls) -> "ConversationState":
        """Create a new, empty consultation state."""
        return cls()
