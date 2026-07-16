"""
conversation_manager.py — Clinical Conversation Orchestrator
=============================================================
Sprint 3 orchestrator. Replaces the simple process_message() in
conversation.py with a full triage-style clinical conversation flow.

Public API
----------
    handle_turn(user_input, state, stream=True) → TurnResult

    TurnResult contains:
      - reply (str | Generator) — the text to show the user
      - state (ConversationState) — updated state
      - decision (ClinicalDecision) — what the engine decided
      - summary (ConversationSummary | None) — present when prediction done

Architecture
------------
Every turn follows this sequence:

  1. NLP Pipeline (Sprint 2)  — extract symptoms / meta
  2. Patient History          — update state with parsed entities
  3. Clinical Reasoning       — decide what to do next
  4. Response Assembly        — build reply from decision
  5. LLM Enrichment (optional)— rephrase / enrich if Gemini/Ollama available

Steps 1-4 are 100% deterministic. Step 5 is optional and gracefully
degrades to Basic Mode if no LLM is available.

Emergency Interruption
----------------------
If is_emergency is True at any point, the manager immediately emits the
emergency warning and stops asking routine questions.

Backward Compatibility
----------------------
Callers that previously called conversation.process_message() may
continue to do so — conversation.py is NOT modified.
The new entry point is conversation_manager.handle_turn().
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Generator, Optional, Union

from src.chatbot.conversation_state import (
    ConversationState,
    ConversationPhase,
    PredictionStatus,
    TurnRecord,
)
from src.chatbot.patient_history import update_history_from_turn
from src.chatbot.clinical_reasoning import ClinicalDecision, DecisionType, reason
from src.chatbot.conversation_summary import generate_summary, ConversationSummary
from src.chatbot.conversation_scoring import confidence_label
from src.chatbot.followup_generator import get_opening_question

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# TurnResult — what handle_turn returns
# ---------------------------------------------------------------------------

@dataclass
class TurnResult:
    """Complete output of one conversation turn."""
    reply:     Union[str, Generator]
    state:     ConversationState
    decision:  ClinicalDecision
    summary:   Optional[ConversationSummary] = None
    parse_result: Optional[object]          = None   # pipeline.ParseResult


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _run_nlp_pipeline(user_input: str, state: ConversationState):
    """
    Run Sprint 2 Clinical NLP Pipeline and return a ParseResult.
    Catches all exceptions and returns an empty result on failure.
    """
    try:
        from src.chatbot.pipeline import run as _pipeline_run
        from src.prediction.predictor import load_feature_names
        dataset_symptoms = load_feature_names() or None
        return _pipeline_run(user_input, dataset_symptoms=dataset_symptoms)
    except Exception as exc:
        logger.error("NLP pipeline failed: %s", exc, exc_info=True)
        # Return a minimal stub so the flow continues
        from src.chatbot.pipeline import ParseResult
        return ParseResult()


def _build_llm_system_prompt(state: ConversationState) -> str:
    """Build a rich system prompt that contextualises the LLM response."""
    symptom_str = ", ".join(state.detected_symptoms) or "none yet"
    conf_pct    = int(state.clinical_confidence * 100)
    return f"""You are MediSense AI, a compassionate medical triage assistant.

Current patient information:
- Age: {state.patient_age}
- Gender: {state.patient_gender}
- Confirmed symptoms: {symptom_str}
- Severity: {state.severity_label or 'not specified'}
- Duration: {state.duration or 'not specified'}
- Clinical confidence: {conf_pct}%

Rules:
- Speak naturally, like a caring doctor taking history.
- Ask ONLY ONE follow-up question at a time.
- Never diagnose or name specific diseases.
- Never dismiss the patient's concerns.
- Keep responses concise (2-4 sentences max).
- If an emergency question is being asked, be gentle but urgent.
"""


def _assemble_reply(
    decision:    ClinicalDecision,
    state:       ConversationState,
    user_input:  str,
    stream:      bool = True,
) -> Union[str, Generator]:
    """
    Build the reply for a given decision.

    Strategy:
    - For GREET / COLLECT / ASK_FOLLOWUP: try LLM enrichment with context,
      fall back to deterministic template text.
    - For WARN_EMERGENCY: always deterministic, no LLM.
    - For PREDICT: deterministic transition text.
    - For SUMMARISE: deterministic summary text.
    """
    # ── Emergency — always deterministic ─────────────────────────────────
    if decision.action == DecisionType.WARN_EMERGENCY:
        msg = decision.emergency_message or (
            "⚠️ MEDICAL EMERGENCY: Your symptoms require immediate medical attention. "
            "Please call emergency services (999 / 911) or go to your nearest emergency room now."
        )
        return _to_generator(msg) if stream else msg

    # ── Summary ────────────────────────────────────────────────────────────
    if decision.action == DecisionType.SUMMARISE:
        summary = generate_summary(state)
        return _to_generator(summary.formatted_text) if stream else summary.formatted_text

    # ── Prediction ready ───────────────────────────────────────────────────
    if decision.action == DecisionType.PREDICT:
        transition = (
            "Thank you for sharing all that information. Based on what you have told me, "
            "I now have a good clinical picture and I am ready to provide you with an assessment. "
            "One moment while the analysis runs…"
        )
        return _to_generator(transition) if stream else transition

    # ── Follow-up / Collect — try LLM, fall back to deterministic ─────────
    question_text = ""
    if decision.followup_questions:
        question_text = decision.followup_questions[0]

    if decision.action == DecisionType.GREET:
        question_text = question_text or get_opening_question(state)

    # Try to enrich via LLM
    try:
        from src.chatbot.chatbot_router import ask_llm
        from src.chatbot.chatbot_router import get_engine_display_name
        engine_name = get_engine_display_name()

        if engine_name.lower() != "basic":
            # Use the LLM to rephrase the question naturally in context
            symptom_ctx = ", ".join(state.detected_symptoms[:5]) or "no symptoms yet"
            asked_count = len(state.questions_asked)

            if decision.action == DecisionType.GREET:
                user_prompt = (
                    "Greet the patient warmly and ask them to describe their symptoms. "
                    "Start the consultation naturally. Do not name any disease."
                )
            elif decision.action == DecisionType.COLLECT:
                user_prompt = (
                    f"The patient said: \"{user_input}\"\n"
                    f"Known symptoms so far: {symptom_ctx}.\n"
                    f"Ask them naturally if they have any other symptoms or if there is anything else "
                    f"they would like to add. You have asked {asked_count} question(s) so far."
                )
            else:  # ASK_FOLLOWUP / CONFIRM
                user_prompt = (
                    f"The patient said: \"{user_input}\"\n"
                    f"Known symptoms so far: {symptom_ctx}.\n"
                    f"Now ask this specific follow-up question naturally: \"{question_text}\"\n"
                    f"Keep it brief, empathetic, and conversational."
                )

            system_prompt = _build_llm_system_prompt(state)
            return ask_llm(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt},
                ],
                stream=stream,
            )
    except Exception as exc:
        logger.debug("LLM enrichment unavailable (%s) — using deterministic text.", exc)

    # ── Deterministic fallback ─────────────────────────────────────────────
    if decision.action == DecisionType.GREET:
        text = (
            "Hello! I'm MediSense AI. I'll ask you a few questions to help understand "
            "your symptoms. Please describe how you are feeling today."
        )
    elif decision.action == DecisionType.COLLECT:
        if state.detected_symptoms:
            text = (
                f"I've noted: {', '.join(state.detected_symptoms)}. "
                "Are there any other symptoms you are experiencing, "
                "or anything else you'd like to add?"
            )
        else:
            text = "Could you describe what symptoms or concerns are bringing you in today?"
    elif question_text:
        text = question_text
    else:
        text = "Could you tell me more about how you are feeling?"

    return _to_generator(text) if stream else text


def _to_generator(text: str) -> Generator[str, None, None]:
    """Wrap a static string as a generator for streaming compatibility."""
    def _gen():
        yield text
    return _gen()


# ---------------------------------------------------------------------------
# State management (Streamlit session_state integration)
# ---------------------------------------------------------------------------

def get_or_create_state() -> ConversationState:
    """
    Get the clinical state from st.session_state or create a fresh one.
    Gracefully handles running outside Streamlit (e.g., in tests).
    """
    try:
        import streamlit as st
        if "clinical_state" not in st.session_state:
            st.session_state["clinical_state"] = ConversationState.fresh()
        return st.session_state["clinical_state"]
    except Exception:
        return ConversationState.fresh()


def save_state(state: ConversationState) -> None:
    """Persist state back to session_state (no-op outside Streamlit)."""
    try:
        import streamlit as st
        st.session_state["clinical_state"] = state
    except Exception:
        pass


def reset_state() -> ConversationState:
    """Clear and return a fresh consultation state."""
    fresh = ConversationState.fresh()
    try:
        import streamlit as st
        st.session_state["clinical_state"] = fresh
    except Exception:
        pass
    return fresh


# ---------------------------------------------------------------------------
# Main public API
# ---------------------------------------------------------------------------

def handle_turn(
    user_input: str,
    state:      Optional[ConversationState] = None,
    stream:     bool = True,
) -> TurnResult:
    """
    Process one conversation turn through the full clinical pipeline.

    Parameters
    ----------
    user_input : raw text from the patient
    state      : ConversationState (loaded from session if None)
    stream     : if True, reply may be a Generator; if False, always str

    Returns
    -------
    TurnResult with reply, updated state, decision, and optional summary
    """
    if state is None:
        state = get_or_create_state()

    state.turn_count += 1

    # ── Step 1: NLP Pipeline (Sprint 2) ───────────────────────────────────
    parse_result = _run_nlp_pipeline(user_input, state)

    # ── Step 2: Patient History Update ────────────────────────────────────
    update_history_from_turn(state, user_input, parse_result, state.turn_count)

    # ── Step 3: Clinical Reasoning ────────────────────────────────────────
    decision = reason(state)

    # Update prediction status in state
    if decision.action == DecisionType.WARN_EMERGENCY:
        state.prediction_status = PredictionStatus.EMERGENCY
    elif decision.action == DecisionType.PREDICT:
        state.prediction_status = PredictionStatus.PREDICTION_AVAILABLE
    elif decision.action in (DecisionType.ASK_FOLLOWUP, DecisionType.CONFIRM):
        state.prediction_status = PredictionStatus.ASKING_FOLLOWUPS
    else:
        state.prediction_status = PredictionStatus.COLLECTING_INFORMATION

    # Track questions asked
    for q in decision.followup_questions:
        state.mark_question_asked(q)

    # ── Step 4: Assemble reply ────────────────────────────────────────────
    reply = _assemble_reply(decision, state, user_input, stream=stream)

    # ── Step 5: Record turn ───────────────────────────────────────────────
    reply_text = ""
    if isinstance(reply, str):
        reply_text = reply
    # For generators we can't preview without consuming — store intent

    record = TurnRecord(
        turn_number       = state.turn_count,
        user_input        = user_input,
        assistant_reply   = reply_text,
        detected_symptoms = list(parse_result.detected_symptoms),
        negated_symptoms  = list(parse_result.negated_symptoms),
        past_symptoms     = list(parse_result.past_symptoms),
        severity_score    = parse_result.severity_score,
        locations         = list(parse_result.locations),
        temporal          = parse_result.temporal,
        duration          = parse_result.duration,
    )
    state.turn_history.append(record)

    # ── Step 6: Generate summary if prediction ready ──────────────────────
    summary: Optional[ConversationSummary] = None
    if decision.action in (DecisionType.PREDICT, DecisionType.SUMMARISE):
        summary = generate_summary(state)

    # Persist state
    save_state(state)

    return TurnResult(
        reply        = reply,
        state        = state,
        decision     = decision,
        summary      = summary,
        parse_result = parse_result,
    )


def complete_prediction(
    state:          ConversationState,
    prediction_dict: dict,
) -> ConversationSummary:
    """
    Call this after prediction_bridge runs to store the result and
    advance the conversation to the PREDICTED phase.

    Parameters
    ----------
    state           : current ConversationState
    prediction_dict : result dict from run_prediction_bridge()

    Returns
    -------
    ConversationSummary
    """
    state.prediction_result = prediction_dict
    state.prediction_ready  = True
    state.phase             = ConversationPhase.PREDICTED
    state.prediction_status = PredictionStatus.PREDICTION_COMPLETE
    save_state(state)
    return generate_summary(state)


# ---------------------------------------------------------------------------
# Convenience UI helpers (Streamlit callers)
# ---------------------------------------------------------------------------

def get_progress_percentage(state: ConversationState) -> int:
    """Return 0-100 integer for a progress bar widget."""
    return state.progress_pct


def get_status_display(state: ConversationState) -> dict:
    """
    Return a dict of display values for the sidebar / status panel.

    Keys
    ----
    progress_pct, confidence_pct, confidence_label,
    prediction_status, symptom_count, is_emergency
    """
    return {
        "progress_pct":      state.progress_pct,
        "confidence_pct":    int(state.clinical_confidence * 100),
        "confidence_label":  confidence_label(state.clinical_confidence),
        "prediction_status": state.prediction_status.value,
        "symptom_count":     state.symptom_count,
        "is_emergency":      state.is_emergency,
        "detected_symptoms": list(state.detected_symptoms),
        "phase":             state.phase.value,
    }
