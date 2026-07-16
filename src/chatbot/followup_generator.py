"""
followup_generator.py — Deterministic Follow-up Question Generator
===================================================================
Selects the next best follow-up question given the current
ConversationState.

Rules
-----
1. Never repeat a question already asked (tracked in state.questions_asked).
2. Prioritise red-flag questions for high-severity symptoms.
3. Ask demographic questions (age, gender) if still unknown after turn 2.
4. Cycle through: primary → secondary → confirmation for each symptom.
5. Fall back to default group when a symptom has no dedicated entry.
6. Return at most max_questions questions per call.

No LLM, no network, no imports from pipeline.py.
"""

from __future__ import annotations

import logging

from src.chatbot.conversation_state import ConversationState
from src.chatbot.question_bank import (
    QUESTION_BANK,
    DEMOGRAPHIC_QUESTIONS,
    get_questions_for_symptom,
)

logger = logging.getLogger(__name__)

# Priority order within a group
_TIER_ORDER = ["red_flag", "primary", "secondary", "confirmation"]


def _flatten_ordered(group: dict[str, list[str]]) -> list[str]:
    """Flatten a question group into a priority-ordered list."""
    result = []
    for tier in _TIER_ORDER:
        result.extend(group.get(tier, []))
    return result


def get_next_questions(
    state: ConversationState,
    max_questions: int = 1,
) -> list[str]:
    """
    Return up to max_questions follow-up questions, none already asked.

    Selection priority
    ------------------
    1. Red-flag questions if severity_score >= 3 or is_emergency context.
    2. Demographic gap (age/gender) after turn 2.
    3. Primary questions for the most recently added symptom.
    4. Secondary / confirmation for earlier symptoms.
    5. Default group catch-all.

    Parameters
    ----------
    state         : current ConversationState
    max_questions : how many questions to return (default 1)

    Returns
    -------
    list[str] of new question strings
    """
    asked = set(state.questions_asked)
    selected: list[str] = []

    def _pick(candidates: list[str]) -> bool:
        """Pick first unseen candidate; return True if found."""
        for q in candidates:
            if q not in asked and q not in selected:
                selected.append(q)
                return True
        return False

    # ── 1. Red-flag questions when severity is high ────────────────────────
    if state.severity_score >= 3 or state.is_emergency:
        for symptom in state.detected_symptoms:
            group = get_questions_for_symptom(symptom)
            if _pick(group.get("red_flag", [])):
                if len(selected) >= max_questions:
                    return selected

    # ── 2. Demographic gap (after turn 2) ─────────────────────────────────
    if state.turn_count >= 2:
        if state.patient_age == "Unknown":
            q = DEMOGRAPHIC_QUESTIONS["age"]
            if q not in asked and q not in selected:
                selected.append(q)
                if len(selected) >= max_questions:
                    return selected
        if state.patient_gender == "Unknown":
            q = DEMOGRAPHIC_QUESTIONS["gender"]
            if q not in asked and q not in selected:
                selected.append(q)
                if len(selected) >= max_questions:
                    return selected

    # ── 3. Ordered questions for each detected symptom ─────────────────────
    # Most recently detected symptom gets priority
    for symptom in reversed(state.detected_symptoms):
        group = get_questions_for_symptom(symptom)
        ordered = _flatten_ordered(group)
        if _pick(ordered):
            if len(selected) >= max_questions:
                return selected

    # ── 4. Default group if nothing yet ───────────────────────────────────
    if not selected:
        default_ordered = _flatten_ordered(QUESTION_BANK["default"])
        _pick(default_ordered)

    return selected


def get_targeted_followup(
    state: ConversationState,
    focus_symptom: str,
    max_questions: int = 2,
) -> list[str]:
    """
    Return questions specifically targeting one symptom.
    Used when clinical_reasoning decides to drill into a specific symptom.
    """
    asked = set(state.questions_asked)
    group = get_questions_for_symptom(focus_symptom)
    ordered = _flatten_ordered(group)
    return [q for q in ordered if q not in asked][:max_questions]


def get_opening_question(state: ConversationState) -> str:
    """Return the greeting question (always first, never repeated)."""
    from src.chatbot.question_bank import OPENING_QUESTIONS
    return OPENING_QUESTIONS[0]


def has_more_questions(state: ConversationState) -> bool:
    """Return True if there are still unanswered questions in the bank."""
    asked = set(state.questions_asked)
    for symptom in state.detected_symptoms:
        group = get_questions_for_symptom(symptom)
        ordered = _flatten_ordered(group)
        if any(q not in asked for q in ordered):
            return True
    # Check defaults too
    default = _flatten_ordered(QUESTION_BANK["default"])
    return any(q not in asked for q in default)


def format_question_for_llm(
    question: str,
    state: ConversationState,
    use_llm: bool = False,
) -> str:
    """
    Format a deterministic question for delivery.

    If use_llm=True, a caller may wrap this with ask_llm for rephrasing.
    By default, return the question as-is (Basic Mode compatible).
    """
    return question
