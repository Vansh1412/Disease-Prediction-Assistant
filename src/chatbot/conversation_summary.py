"""
conversation_summary.py — Clinical Summary Generator
=====================================================
Generates a structured end-of-consultation summary.

The summary is built entirely from ConversationState — no LLM required
(though the manager may optionally enrich with an LLM explanation).

Output
------
ConversationSummary dataclass with:
  - Detected symptoms
  - Duration and severity
  - Body systems involved
  - Emergency status
  - Clinical confidence
  - Prediction result (if available)
  - Suggested next steps
  - Formatted text summary
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from src.chatbot.conversation_state import ConversationState
from src.chatbot.conversation_scoring import confidence_label
from src.chatbot.patient_history import get_active_symptoms

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Body system inference
# ---------------------------------------------------------------------------

_SYMPTOM_TO_SYSTEM: dict[str, str] = {
    # Cardiac
    "chest pain":            "Cardiovascular",
    "chest tightness":       "Cardiovascular",
    "irregular heartbeat":   "Cardiovascular",
    "palpitations":          "Cardiovascular",
    "jaw pain":              "Cardiovascular",
    "arm pain":              "Cardiovascular",
    "shortness of breath":   "Respiratory / Cardiovascular",

    # Respiratory
    "cough":                 "Respiratory",
    "difficulty breathing":  "Respiratory",
    "wheezing":              "Respiratory",

    # Neurological
    "headache":              "Neurological",
    "dizziness":             "Neurological",
    "seizures":              "Neurological",
    "loss of consciousness": "Neurological",
    "arm weakness":          "Neurological",
    "slurred speech":        "Neurological",
    "memory loss":           "Neurological",

    # Gastrointestinal
    "nausea":                "Gastrointestinal",
    "vomiting":              "Gastrointestinal",
    "diarrhea":              "Gastrointestinal",
    "diarrhoea":             "Gastrointestinal",
    "abdominal pain":        "Gastrointestinal",
    "lower abdominal pain":  "Gastrointestinal",
    "upper abdominal pain":  "Gastrointestinal",
    "constipation":          "Gastrointestinal",
    "blood in stool":        "Gastrointestinal",
    "vomiting blood":        "Gastrointestinal",

    # Musculoskeletal
    "back pain":             "Musculoskeletal",
    "low back pain":         "Musculoskeletal",
    "joint pain":            "Musculoskeletal",
    "neck pain":             "Musculoskeletal",
    "knee pain":             "Musculoskeletal",
    "shoulder pain":         "Musculoskeletal",
    "muscle pain":           "Musculoskeletal",

    # Dermatological
    "skin rash":             "Dermatological",
    "itching":               "Dermatological",
    "hives":                 "Dermatological",
    "skin peeling":          "Dermatological",

    # Psychiatric / Neuropsychiatric
    "depression":            "Psychiatric",
    "anxiety and nervousness": "Psychiatric",
    "insomnia":              "Psychiatric",
    "suicidal thoughts":     "Psychiatric",

    # General / Systemic
    "fever":                 "General / Infectious",
    "fatigue":               "General / Systemic",
    "night sweats":          "General / Infectious",
    "unintentional weight loss": "General / Systemic",

    # Urinary
    "frequent urination":    "Urological",
    "urinary burning":       "Urological",
    "blood in urine":        "Urological",

    # Endocrine
    "excessive thirst":      "Endocrine",
    "excessive hunger":      "Endocrine",
}


def _infer_body_systems(symptoms: list[str]) -> list[str]:
    """Return deduplicated body systems for the given symptom list."""
    systems: list[str] = []
    for s in symptoms:
        system = _SYMPTOM_TO_SYSTEM.get(s)
        if system and system not in systems:
            systems.append(system)
    return systems


# ---------------------------------------------------------------------------
# Suggested next step logic
# ---------------------------------------------------------------------------

def _suggest_next_step(state: ConversationState) -> str:
    if state.is_emergency:
        return "🚨 URGENT: Call emergency services (999 / 911) or go to the nearest emergency room immediately."

    if state.prediction_result:
        er = state.prediction_result.get("emergency_level", "").lower()
        specialist = state.prediction_result.get("specialist", "")
        if er in ("high", "critical"):
            return "Seek immediate medical attention. Consider visiting A&E or calling your doctor today."
        if specialist:
            return f"Consider consulting a {specialist} for a formal evaluation."

    if state.clinical_confidence >= 0.65:
        return "Consider consulting a healthcare professional with this symptom summary."
    return "Continue describing your symptoms or consult a healthcare professional if concerned."


# ---------------------------------------------------------------------------
# Summary dataclass
# ---------------------------------------------------------------------------

@dataclass
class ConversationSummary:
    """Structured end-of-consultation summary."""
    patient_age:          str
    patient_gender:       str
    active_symptoms:      list[str]
    negated_symptoms:     list[str]
    past_symptoms:        list[str]
    duration:             Optional[str]
    severity_label:       Optional[str]
    severity_score:       int
    body_locations:       list[str]
    body_systems:         list[str]
    medications_mentioned: list[str]
    allergies_mentioned:  list[str]
    medical_history:      list[str]
    is_emergency:         bool
    emergency_message:    Optional[str]
    clinical_confidence:  float
    confidence_label:     str
    prediction_result:    Optional[dict]
    prediction_ready:     bool
    turn_count:           int
    suggested_next_step:  str
    clinical_notes:       list[str]
    formatted_text:       str = field(init=False)

    def __post_init__(self) -> None:
        self.formatted_text = self._build_formatted_text()

    def _build_formatted_text(self) -> str:
        lines = [
            "═══════════════════════════════════════",
            "       MEDISENSE AI — CLINICAL SUMMARY",
            "═══════════════════════════════════════",
            "",
        ]

        # Patient profile
        lines.append("📋 PATIENT PROFILE")
        lines.append(f"   Age    : {self.patient_age}")
        lines.append(f"   Gender : {self.patient_gender}")
        lines.append("")

        # Emergency banner
        if self.is_emergency:
            lines.append("🚨 EMERGENCY ALERT")
            lines.append(f"   {self.emergency_message or 'Seek immediate medical attention.'}")
            lines.append("")

        # Symptoms
        lines.append("🔍 DETECTED SYMPTOMS")
        if self.active_symptoms:
            for s in self.active_symptoms:
                lines.append(f"   ✓ {s}")
        else:
            lines.append("   None confirmed")
        lines.append("")

        if self.negated_symptoms:
            lines.append("✗ EXCLUDED SYMPTOMS (patient denied)")
            for s in self.negated_symptoms:
                lines.append(f"   ✗ {s}")
            lines.append("")

        if self.past_symptoms:
            lines.append("⏮ PAST / RESOLVED SYMPTOMS")
            for s in self.past_symptoms:
                lines.append(f"   ◷ {s}")
            lines.append("")

        # Clinical details
        lines.append("📊 CLINICAL DETAILS")
        lines.append(f"   Duration       : {self.duration or 'Not specified'}")
        lines.append(f"   Severity       : {self.severity_label or 'Not specified'} "
                     f"({'⬛' * self.severity_score + '□' * (4 - self.severity_score)})")
        lines.append(f"   Body Locations : {', '.join(self.body_locations) or 'Not specified'}")
        lines.append(f"   Body Systems   : {', '.join(self.body_systems) or 'Unknown'}")
        lines.append("")

        # Medications / allergies / history
        if self.medications_mentioned:
            lines.append(f"💊 MEDICATIONS MENTIONED: {', '.join(self.medications_mentioned)}")
        if self.allergies_mentioned:
            lines.append(f"⚠  ALLERGIES MENTIONED: {', '.join(self.allergies_mentioned)}")
        if self.medical_history:
            lines.append(f"📁 MEDICAL HISTORY: {', '.join(self.medical_history)}")
        if self.medications_mentioned or self.allergies_mentioned or self.medical_history:
            lines.append("")

        # Confidence
        conf_pct = int(self.clinical_confidence * 100)
        bar_filled = int(conf_pct / 10)
        bar = "■" * bar_filled + "□" * (10 - bar_filled)
        lines.append("📈 CONSULTATION CONFIDENCE")
        lines.append(f"   [{bar}] {conf_pct}% — {self.confidence_label}")
        lines.append("")

        # Prediction
        if self.prediction_result:
            disease  = self.prediction_result.get("disease", "Unknown")
            pred_pct = self.prediction_result.get("confidence", 0)
            lines.append("🔬 PREDICTION RESULT")
            lines.append(f"   Likely Condition : {disease}")
            lines.append(f"   Model Confidence : {pred_pct:.1f}%")
            specialist = self.prediction_result.get("specialist", "")
            if specialist:
                lines.append(f"   Specialist       : {specialist}")
            lines.append("")

        # Next step
        lines.append("➡ SUGGESTED NEXT STEP")
        lines.append(f"   {self.suggested_next_step}")
        lines.append("")

        lines.append("═══════════════════════════════════════")
        lines.append("⚕  This is an AI assessment, not a medical diagnosis.")
        lines.append("   Always consult a qualified healthcare professional.")
        lines.append("═══════════════════════════════════════")

        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "patient_age":          self.patient_age,
            "patient_gender":       self.patient_gender,
            "active_symptoms":      self.active_symptoms,
            "negated_symptoms":     self.negated_symptoms,
            "past_symptoms":        self.past_symptoms,
            "duration":             self.duration,
            "severity_label":       self.severity_label,
            "severity_score":       self.severity_score,
            "body_locations":       self.body_locations,
            "body_systems":         self.body_systems,
            "is_emergency":         self.is_emergency,
            "clinical_confidence":  self.clinical_confidence,
            "confidence_label":     self.confidence_label,
            "prediction_result":    self.prediction_result,
            "prediction_ready":     self.prediction_ready,
            "turn_count":           self.turn_count,
            "suggested_next_step":  self.suggested_next_step,
        }


# ---------------------------------------------------------------------------
# Public generator
# ---------------------------------------------------------------------------

def generate_summary(state: ConversationState) -> ConversationSummary:
    """
    Build and return a ConversationSummary from the current ConversationState.

    Safe to call at any point in the conversation — returns best-effort summary.
    """
    active_symptoms = get_active_symptoms(state)
    body_systems    = _infer_body_systems(active_symptoms)
    next_step       = _suggest_next_step(state)
    conf_label      = confidence_label(state.clinical_confidence)

    summary = ConversationSummary(
        patient_age           = state.patient_age,
        patient_gender        = state.patient_gender,
        active_symptoms       = active_symptoms,
        negated_symptoms      = state.negated_symptoms,
        past_symptoms         = state.past_symptoms,
        duration              = state.duration,
        severity_label        = state.severity_label,
        severity_score        = state.severity_score,
        body_locations        = state.body_locations,
        body_systems          = body_systems,
        medications_mentioned = state.medications_mentioned,
        allergies_mentioned   = state.allergies_mentioned,
        medical_history       = state.medical_history,
        is_emergency          = state.is_emergency,
        emergency_message     = state.emergency_message,
        clinical_confidence   = state.clinical_confidence,
        confidence_label      = conf_label,
        prediction_result     = state.prediction_result,
        prediction_ready      = state.prediction_ready,
        turn_count            = state.turn_count,
        suggested_next_step   = next_step,
        clinical_notes        = state.clinical_notes,
    )

    logger.info(
        "Summary generated: %d symptoms, confidence=%.2f, emergency=%s",
        len(active_symptoms),
        state.clinical_confidence,
        state.is_emergency,
    )
    return summary
