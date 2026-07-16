"""
Basic Rule-Based Engine
=======================
Sprint 1 placeholder.  No LLM is used.

Returns canned contextual responses based on simple keyword detection so
the application remains functional when neither Gemini nor Ollama is
available.

Sprint 2 will replace the keyword map with a full medical dictionary
and NLP-free symptom matching pipeline.

Never raises exceptions.
"""

import logging
from typing import Generator, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sprint 1 placeholder responses
# Sprint 2: replace with symptom-aware medical dictionary.
# ---------------------------------------------------------------------------

_EMERGENCY_KEYWORDS = {
    "heart attack", "stroke", "can't breathe", "cannot breathe",
    "severe chest pain", "loss of consciousness", "anaphylaxis",
    "suicide", "kill myself", "bleeding out",
}

_GREETING_KEYWORDS = {"hello", "hi", "hey", "good morning", "good evening", "greetings"}

_FAREWELL_KEYWORDS = {"bye", "goodbye", "see you", "take care"}


def _classify(text: str) -> str:
    """Classify user input into a coarse category."""
    lower = text.lower()

    if any(kw in lower for kw in _EMERGENCY_KEYWORDS):
        return "emergency"

    if any(kw in lower for kw in _GREETING_KEYWORDS):
        return "greeting"

    if any(kw in lower for kw in _FAREWELL_KEYWORDS):
        return "farewell"

    # Assume anything else is a symptom report
    return "symptom"


def is_available() -> bool:
    """Basic engine is always available — it has no external dependencies."""
    return True


def ask(
    messages: list[dict],
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """
    Generate a rule-based placeholder response.

    Parameters
    ----------
    messages : list of {"role": str, "content": str}
    stream   : if True, returns a generator (single chunk for simplicity)

    Returns
    -------
    str | Generator[str, None, None]
    """
    # Use the last user message for classification
    user_text = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_text = msg.get("content", "")
            break

    category = _classify(user_text)
    response = _build_response(category)

    logger.debug("BasicEngine: category='%s'", category)

    if stream:
        def _gen() -> Generator[str, None, None]:
            yield response
        return _gen()
    return response


def _build_response(category: str) -> str:
    """Map category to a professional clinical response string."""
    if category == "emergency":
        return (
            "⚠️ **MEDICAL EMERGENCY WARNING:** You have described symptoms that "
            "may require immediate medical attention. Please consider calling emergency services "
            "(e.g., 911 / 112) or visiting your nearest emergency room."
        )

    if category == "greeting":
        return (
            "Hello! I am your Clinical Assistant. To help me understand what you're "
            "experiencing, could you please describe the main symptoms or concerns "
            "that brought you here today?"
        )

    if category == "farewell":
        return (
            "Take care! Remember to consult a qualified healthcare professional for any "
            "medical concerns. Goodbye! 👋"
        )

    # Default: symptom report
    return (
        "Thank you for sharing. Could you provide a bit more detail? "
        "For example, how long have you been experiencing this, or is there any other "
        "pain or discomfort you'd like to share?"
    )
