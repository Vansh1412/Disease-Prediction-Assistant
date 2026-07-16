"""
patient_history.py — Patient History Tracker
=============================================
Maintains a structured clinical history for the current consultation.

Responsibilities
----------------
- Track timeline of symptom appearances across turns
- Record medications, allergies, and medical history mentions
- Provide a queryable history object (no Streamlit dependency)
- Detect demographic mentions (age, gender) in free text

This module reads and writes ConversationState — it does NOT own state.
It provides helper functions called by the conversation_manager.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional

from src.chatbot.conversation_state import ConversationState

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Timeline entry
# ---------------------------------------------------------------------------

@dataclass
class SymptomTimelineEntry:
    turn:     int
    symptom:  str
    temporal: str = "current"   # current | past | unknown
    duration: Optional[str] = None
    negated:  bool = False


# ---------------------------------------------------------------------------
# Medication / allergy patterns
# ---------------------------------------------------------------------------

_MEDICATION_PATTERNS: list[str] = [
    r"\b(paracetamol|acetaminophen|tylenol)\b",
    r"\b(ibuprofen|advil|nurofen)\b",
    r"\b(aspirin)\b",
    r"\b(antibiotic[s]?)\b",
    r"\b(naproxen|aleve)\b",
    r"\b(omeprazole|pantoprazole|lansoprazole)\b",
    r"\b(metformin|insulin)\b",
    r"\b(antidepressant[s]?)\b",
    r"\b(antihistamine[s]?)\b",
    r"\b(steroid[s]?|prednisone|prednisolone)\b",
    r"\b(blood pressure|bp)\s+(medication|tablet|pill|medicine)\b",
    r"\b(inhaler|salbutamol|albuterol|ventolin)\b",
    r"\b(codeine|tramadol|morphine|opioid[s]?)\b",
]

_ALLERGY_PATTERNS: list[str] = [
    r"allergic?\s+to\s+([\w\s]+)",
    r"allergy\s+to\s+([\w\s]+)",
    r"([\w\s]+)\s+allergy",
    r"react[s]?\s+to\s+([\w\s]+)",
    r"can\s?not\s+take\s+([\w\s]+)",
]

_HISTORY_PATTERNS: list[str] = [
    r"\b(diabete[s]?|diabetic)\b",
    r"\b(hypertension|high blood pressure)\b",
    r"\b(asthma)\b",
    r"\b(heart disease|heart attack|cardiac)\b",
    r"\b(stroke)\b",
    r"\b(kidney disease|renal)\b",
    r"\b(liver disease|hepatitis)\b",
    r"\b(cancer|tumou?r)\b",
    r"\b(arthritis|rheumatoid)\b",
    r"\b(thyroid)\b",
    r"\b(epilepsy|seizure disorder)\b",
    r"\b(depression|anxiety disorder)\b",
    r"\b(chronic obstructive|COPD|emphysema)\b",
]

# Patterns for detecting age and gender
_AGE_PATTERN    = re.compile(r"\b(?:i\s+am|im|i'm|age[d]?|aged?)\s*(\d{1,3})\b", re.IGNORECASE)
_NUMBER_AGE     = re.compile(r"\b(\d{1,3})\s*(?:year[s]?|yr[s]?)\s+old\b", re.IGNORECASE)
_MALE_PATTERN   = re.compile(r"\b(male|man|boy|gentleman|he|him|his)\b", re.IGNORECASE)
_FEMALE_PATTERN = re.compile(r"\b(female|woman|girl|lady|she|her)\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# History update
# ---------------------------------------------------------------------------

def update_history_from_turn(
    state: ConversationState,
    user_input: str,
    parse_result,           # pipeline.ParseResult — imported lazily to avoid circular
    turn_number: int,
) -> None:
    """
    Update the ConversationState with information extracted from a single turn.

    Parameters
    ----------
    state        : ConversationState to update
    user_input   : raw user message
    parse_result : pipeline.ParseResult from Sprint 2
    turn_number  : current turn count
    """
    # ── Symptoms ───────────────────────────────────────────────────────────
    for symptom in parse_result.detected_symptoms:
        state.add_symptom(symptom)

    for symptom in parse_result.negated_symptoms:
        if symptom not in state.negated_symptoms:
            state.negated_symptoms.append(symptom)

    for symptom in parse_result.past_symptoms:
        if symptom not in state.past_symptoms:
            state.past_symptoms.append(symptom)

    # ── Clinical enrichment ────────────────────────────────────────────────
    duration = parse_result.duration
    if duration and state.duration is None:
        state.duration = duration

    new_severity = parse_result.severity_score
    if new_severity > state.severity_score:
        state.severity_score = new_severity
        state.severity_label = parse_result.severity_label

    for loc in parse_result.locations:
        if loc not in state.body_locations:
            state.body_locations.append(loc)

    # ── Emergency ─────────────────────────────────────────────────────────
    if parse_result.is_emergency:
        state.is_emergency     = True
        state.emergency_message = parse_result.emergency_message

    # ── Demographics ──────────────────────────────────────────────────────
    _detect_demographics(state, user_input)

    # ── Medications ───────────────────────────────────────────────────────
    _detect_medications(state, user_input)

    # ── Allergies ─────────────────────────────────────────────────────────
    _detect_allergies(state, user_input)

    # ── Medical history ───────────────────────────────────────────────────
    _detect_medical_history(state, user_input)

    # ── Track answer ──────────────────────────────────────────────────────
    if user_input.strip():
        state.answers_given.append(user_input.strip())


def _detect_demographics(state: ConversationState, text: str) -> None:
    """Parse age and gender from free text if not already known."""
    if state.patient_age == "Unknown":
        m = _AGE_PATTERN.search(text) or _NUMBER_AGE.search(text)
        if m:
            age_val = m.group(1)
            try:
                age_int = int(age_val)
                if 0 < age_int < 130:
                    state.patient_age = str(age_int)
                    state.add_note(f"Patient age detected: {age_int}")
            except ValueError:
                pass

    if state.patient_gender == "Unknown":
        if _FEMALE_PATTERN.search(text):
            state.patient_gender = "Female"
            state.add_note("Patient gender detected: Female")
        elif _MALE_PATTERN.search(text):
            state.patient_gender = "Male"
            state.add_note("Patient gender detected: Male")


def _detect_medications(state: ConversationState, text: str) -> None:
    """Detect medication mentions and add to history."""
    lower = text.lower()
    for pattern in _MEDICATION_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            med = m.group(0).strip()
            if med not in state.medications_mentioned:
                state.medications_mentioned.append(med)
                state.add_note(f"Medication mentioned: {med}")


def _detect_allergies(state: ConversationState, text: str) -> None:
    """Detect allergy mentions."""
    lower = text.lower()
    for pattern in _ALLERGY_PATTERNS:
        m = re.search(pattern, lower)
        if m:
            try:
                allergen = m.group(1).strip()
                if allergen and allergen not in state.allergies_mentioned:
                    state.allergies_mentioned.append(allergen)
                    state.add_note(f"Allergy mentioned: {allergen}")
            except IndexError:
                pass


def _detect_medical_history(state: ConversationState, text: str) -> None:
    """Detect mentions of pre-existing conditions."""
    lower = text.lower()
    for pattern in _HISTORY_PATTERNS:
        m = re.search(pattern, lower, re.IGNORECASE)
        if m:
            condition = m.group(0).strip()
            if condition not in state.medical_history:
                state.medical_history.append(condition)
                state.add_note(f"Medical history mentioned: {condition}")


# ---------------------------------------------------------------------------
# History query helpers
# ---------------------------------------------------------------------------

def get_active_symptoms(state: ConversationState) -> list[str]:
    """Return symptoms that are currently active (not negated, not past-only)."""
    negated = set(state.negated_symptoms)
    past    = set(state.past_symptoms)
    return [s for s in state.detected_symptoms if s not in negated]


def get_symptom_summary(state: ConversationState) -> str:
    """Return a compact one-line symptom summary for prompting."""
    active = get_active_symptoms(state)
    if not active:
        return "No symptoms confirmed."
    parts = [f"• {s}" for s in active]
    if state.duration:
        parts.append(f"• Duration: {state.duration}")
    if state.severity_label:
        parts.append(f"• Severity: {state.severity_label}")
    if state.body_locations:
        parts.append(f"• Locations: {', '.join(state.body_locations)}")
    return "\n".join(parts)
