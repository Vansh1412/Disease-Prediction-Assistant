"""
clinical_reasoning.py — Clinical Decision Engine
=================================================
The deterministic brain of the conversation.

Reads ConversationState and returns a structured ClinicalDecision
telling the conversation manager exactly what to do next.

This module NEVER calls an LLM.
It NEVER touches the ML prediction models.
It does NOT import from pipeline.py.

Decisions
---------
  GREET           — Send greeting, ask first question
  COLLECT         — Ask open "any other symptoms?" prompt
  ASK_FOLLOWUP    — Ask a specific follow-up question
  CONFIRM         — Confirm a specific symptom
  WARN_EMERGENCY  — Interrupt with emergency warning
  PREDICT         — Enough information, trigger ML prediction
  SUMMARISE       — Prediction done, generate summary
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.chatbot.conversation_state import ConversationState, ConversationPhase
from src.chatbot.conversation_scoring import (
    compute_score,
    THRESHOLD_COLLECTING,
    THRESHOLD_PREDICT,
    MIN_SYMPTOMS_FOR_FOLLOWUP,
    MIN_SYMPTOMS_FOR_PREDICTION,
)
from src.chatbot.followup_generator import (
    get_next_questions,
    has_more_questions,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Decision types
# ---------------------------------------------------------------------------

class DecisionType(str, Enum):
    GREET          = "greet"
    COLLECT        = "collect"
    ASK_FOLLOWUP   = "ask_followup"
    CONFIRM        = "confirm"
    WARN_EMERGENCY = "warn_emergency"
    PREDICT        = "predict"
    SUMMARISE      = "summarise"


@dataclass
class ClinicalDecision:
    """
    Structured output of the reasoning engine.

    The conversation manager reads this and acts accordingly.
    """
    action:            DecisionType
    followup_questions: list[str]     = field(default_factory=list)
    reasoning:         str            = ""   # human-readable explanation (for logs)
    confidence:        float          = 0.0
    confidence_label:  str            = ""
    prediction_ready:  bool           = False
    is_emergency:      bool           = False
    emergency_message: Optional[str]  = None


# ---------------------------------------------------------------------------
# Main reasoning function
# ---------------------------------------------------------------------------

def reason(state: ConversationState) -> ClinicalDecision:
    """
    Evaluate the current ConversationState and decide what to do next.

    Call this once per conversation turn AFTER the NLP pipeline has
    updated the state with new symptoms / metadata.

    Returns
    -------
    ClinicalDecision
    """
    # ── Always recompute confidence first ─────────────────────────────────
    score_bd = compute_score(state)
    score    = score_bd.total

    # ── 1. Emergency — highest priority ───────────────────────────────────
    if state.is_emergency:
        state.phase = ConversationPhase.EMERGENCY
        return ClinicalDecision(
            action            = DecisionType.WARN_EMERGENCY,
            reasoning         = "Emergency flag set by pipeline.",
            confidence        = score,
            confidence_label  = "Emergency",
            is_emergency      = True,
            emergency_message = state.emergency_message,
        )

    # ── 2. Already predicted → summarise ──────────────────────────────────
    if state.phase == ConversationPhase.PREDICTED:
        return ClinicalDecision(
            action           = DecisionType.SUMMARISE,
            reasoning        = "Prediction already made, generating summary.",
            confidence       = score,
            confidence_label = "Complete",
            prediction_ready = True,
        )

    # ── 3. Greeting phase ─────────────────────────────────────────────────
    if state.phase == ConversationPhase.GREETING or state.turn_count == 0:
        state.phase = ConversationPhase.COLLECTING
        return ClinicalDecision(
            action           = DecisionType.GREET,
            reasoning        = "First turn — greet the patient.",
            confidence       = 0.0,
            confidence_label = "Greeting",
        )

    # ── 4. No symptoms yet → keep collecting ──────────────────────────────
    if state.symptom_count == 0:
        return ClinicalDecision(
            action           = DecisionType.COLLECT,
            reasoning        = "No symptoms detected yet.",
            confidence       = score,
            confidence_label = "Gathering Information",
        )

    # ── 5. High confidence → predict ──────────────────────────────────────
    if (
        score >= THRESHOLD_PREDICT
        and state.symptom_count >= MIN_SYMPTOMS_FOR_PREDICTION
    ):
        state.phase           = ConversationPhase.READY_TO_PREDICT
        state.prediction_ready = True
        return ClinicalDecision(
            action           = DecisionType.PREDICT,
            reasoning        = (
                f"Score {score:.2f} >= {THRESHOLD_PREDICT} with "
                f"{state.symptom_count} symptoms."
            ),
            confidence       = score,
            confidence_label = "High Confidence",
            prediction_ready = True,
        )

    # ── 6. Medium confidence → ask follow-up ─────────────────────────────
    if (
        score >= THRESHOLD_COLLECTING
        and state.symptom_count >= MIN_SYMPTOMS_FOR_FOLLOWUP
    ):
        questions = get_next_questions(state, max_questions=1)
        if questions:
            state.phase = ConversationPhase.FOLLOWUP
            return ClinicalDecision(
                action             = DecisionType.ASK_FOLLOWUP,
                followup_questions = questions,
                reasoning          = (
                    f"Score {score:.2f}: collecting richer detail for "
                    + ", ".join(state.detected_symptoms[:3])
                ),
                confidence        = score,
                confidence_label  = "Building Clinical Picture",
            )

    # ── 7. Low confidence + has symptoms → ask first follow-up ───────────
    if state.symptom_count >= 1 and score < THRESHOLD_COLLECTING:
        questions = get_next_questions(state, max_questions=1)
        if questions:
            state.phase = ConversationPhase.FOLLOWUP
            return ClinicalDecision(
                action             = DecisionType.ASK_FOLLOWUP,
                followup_questions = questions,
                reasoning          = (
                    f"Score {score:.2f}: detected {state.symptom_count} symptom(s), "
                    "gathering more data."
                ),
                confidence        = score,
                confidence_label  = "Gathering Information",
            )

    # ── 8. Ran out of questions but still below threshold → force predict ─
    if state.symptom_count >= MIN_SYMPTOMS_FOR_FOLLOWUP and not has_more_questions(state):
        state.phase            = ConversationPhase.READY_TO_PREDICT
        state.prediction_ready  = True
        return ClinicalDecision(
            action           = DecisionType.PREDICT,
            reasoning        = "Exhausted question bank — proceeding with available data.",
            confidence       = score,
            confidence_label = "Best Available Data",
            prediction_ready = True,
        )

    # ── 9. Default: keep collecting ───────────────────────────────────────
    return ClinicalDecision(
        action           = DecisionType.COLLECT,
        reasoning        = f"Score {score:.2f}: continuing symptom collection.",
        confidence       = score,
        confidence_label = "Gathering Information",
    )


def should_predict_now(state: ConversationState) -> bool:
    """Convenience predicate — True when the engine would decide PREDICT."""
    decision = reason(state)
    return decision.action == DecisionType.PREDICT


def is_emergency_state(state: ConversationState) -> bool:
    """True when emergency flag is set regardless of other state."""
    return state.is_emergency
