"""
Chatbot Router
==============
The ONLY public entry point for the entire AI engine layer.

The frontend (and every other module) must use:

    from src.chatbot.chatbot_router import ask_llm, process_message

The router:
- Detects the best available engine on first call
- Routes every request to that engine
- Automatically falls back (Gemini → Ollama → Basic) on failure
- Maintains engine state in Streamlit session_state
- Exposes status helpers: get_active_engine / is_gemini / is_ollama / is_basic
- Logs all decisions and switches

The frontend never needs to know which engine is running.
"""

import logging
from typing import Generator, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_session_state():
    """Return Streamlit session_state if available, else a plain dict stub."""
    try:
        import streamlit as st  # type: ignore
        return st.session_state
    except Exception:
        # Outside Streamlit (e.g. unit tests) — use a module-level dict
        return _fallback_state


_fallback_state: dict = {}


def _ss_get(key: str, default=None):
    state = _get_session_state()
    if hasattr(state, "__getitem__"):
        return state.get(key, default)
    return getattr(state, key, default)


def _ss_set(key: str, value) -> None:
    state = _get_session_state()
    try:
        state[key] = value
    except Exception:
        setattr(state, key, value)


# ---------------------------------------------------------------------------
# Engine resolution (with failover)
# ---------------------------------------------------------------------------

_ENGINE_LABELS: dict[str, str] = {
    "gemini": "Cloud AI",
    "ollama": "Local AI",
    "basic":  "Clinical Assistant",
}

_ENGINE_BADGES: dict[str, str] = {
    "gemini": "✨ Cloud AI",
    "ollama": "🦙 Local AI",
    "basic":  "⚙️ Clinical Assistant",
}

_ENGINE_ORDER = ("gemini", "ollama", "basic")


def _set_engine(name: str) -> None:
    """Write both ai_engine and ai_engine_label to session_state atomically."""
    _ss_set("ai_engine", name)
    _ss_set("ai_engine_label", _ENGINE_LABELS.get(name, name))
    
    try:
        mod = _engine_module(name)
        if hasattr(mod, "get_active_model"):
            model_name = mod.get_active_model()
            _ss_set("ai_model", model_name)
        else:
            _ss_set("ai_model", "")
    except Exception:
        pass


def _resolve_engine() -> str:
    """
    Return the name of the currently active engine, initialising it if needed.
    Persists the active engine name in session_state["ai_engine"].
    """
    current = _ss_get("ai_engine")
    if current:
        return current

    from src.chatbot import engine_detector
    engine = engine_detector.detect()
    _set_engine(engine)
    logger.info("ChatbotRouter: engine initialised → '%s'.", engine)
    return engine


def _engine_module(name: str):
    """Return the engine module for the given name."""
    if name == "gemini":
        from src.chatbot import gemini_engine
        return gemini_engine
    if name == "ollama":
        from src.chatbot import ollama_engine
        return ollama_engine
    from src.chatbot import basic_engine
    return basic_engine


def _next_engine(current: str) -> str | None:
    """Return the next engine in the fallback chain, or None if already at Basic."""
    idx = _ENGINE_ORDER.index(current) if current in _ENGINE_ORDER else len(_ENGINE_ORDER)
    if idx + 1 < len(_ENGINE_ORDER):
        return _ENGINE_ORDER[idx + 1]
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ask_llm(
    messages: list[dict],
    stream: bool = False,
) -> Union[str, Generator[str, None, None]]:
    """
    Route an LLM request through the best available engine with automatic
    failover.

    Parameters
    ----------
    messages : list of {"role": str, "content": str}
    stream   : if True, returns a generator yielding text chunks

    Returns
    -------
    str | Generator[str, None, None]

    This function NEVER raises an exception.
    """
    engine_name = _resolve_engine()

    while True:
        try:
            mod = _engine_module(engine_name)
            logger.debug("ChatbotRouter: routing to '%s' (stream=%s).", engine_name, stream)
            result = mod.ask(messages, stream=stream)

            # For non-streaming: check if the engine returned an error string
            if not stream and isinstance(result, str) and result.startswith("Error:"):
                raise RuntimeError(result)

            return result

        except Exception as exc:
            logger.error(
                "ChatbotRouter: engine '%s' failed — %s. Attempting fallback …",
                engine_name, exc,
            )
            next_engine = _next_engine(engine_name)
            if next_engine is None:
                # Already at Basic; return a safe error message
                err = (
                    "I'm having trouble processing your request right now. "
                    "Please try again in a moment."
                )
                logger.critical("ChatbotRouter: all engines exhausted.")
                if stream:
                    def _err_gen(): yield err
                    return _err_gen()
                return err

            logger.warning(
                "ChatbotRouter: switching from '%s' → '%s'.", engine_name, next_engine
            )
            engine_name = next_engine
            _set_engine(engine_name)


# ---------------------------------------------------------------------------
# Session state management
# ---------------------------------------------------------------------------

def init_session() -> None:
    """
    Initialise all AI-engine-related session state keys.
    Call once at application start-up (idempotent).
    """
    if not _ss_get("ai_engine"):
        _resolve_engine()
    if _ss_get("ai_conversation_id") is None:
        import uuid
        _ss_set("ai_conversation_id", str(uuid.uuid4()))
        logger.debug("ChatbotRouter: new conversation id assigned.")


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_active_engine() -> str:
    """Return the name of the currently active engine."""
    return _ss_get("ai_engine") or _resolve_engine()


def is_gemini() -> bool:
    """Return True if Gemini is the active engine."""
    return get_active_engine() == "gemini"


def is_ollama() -> bool:
    """Return True if Ollama is the active engine."""
    return get_active_engine() == "ollama"


def is_basic() -> bool:
    """Return True if the Basic rule-based engine is active."""
    return get_active_engine() == "basic"


def get_engine_display_name() -> str:
    """
    Return a human-friendly engine name suitable for UI display.

    Examples
    --------
    "Gemini AI"       when Gemini is active
    "Ollama (Qwen)"   when Ollama is active
    "Basic Mode"      when the rule-based engine is active

    Stored in st.session_state["ai_engine_label"] for Sprint 4 UI use.
    """
    return _ss_get("ai_engine_label") or _ENGINE_LABELS.get(get_active_engine(), "Unknown")


def get_engine_badge() -> str:
    """
    Return an emoji-prefixed engine badge string for inline UI display.

    Examples
    --------
    "\u2728 Gemini AI"        → shown in sidebar / status bar
    "🦙 Ollama (Qwen)"   → shown when running locally
    "⚙️ Basic Mode"       → shown when no LLM is connected
    """
    return _ENGINE_BADGES.get(get_active_engine(), get_active_engine())
