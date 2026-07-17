"""
Chatbot Router
==============
The ONLY public entry point for the entire AI engine layer.

The frontend (and every other module) must use:

    from src.chatbot.chatbot_router import ask_llm, process_message

The router:
- Detects the best available engine on first call
- Routes every request to that engine
- Automatically falls back (Gemini → Basic) on failure
  Note: Ollama is skipped in the fallback chain on Streamlit Cloud
- Shows a friendly st.warning when Gemini temporarily fails
- Maintains engine state in Streamlit session_state
- Exposes status helpers: get_active_engine / is_gemini / is_ollama / is_basic
- Logs all decisions and switches

The frontend never needs to know which engine is running.
"""

import logging
import traceback
from typing import Generator, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_session_state():
    """Return Streamlit session_state if available, else a plain dict stub."""
    try:
        import streamlit as st  # type: ignore  # noqa: PLC0415
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


def _show_warning(message: str) -> None:
    """Show a Streamlit warning if inside a Streamlit context; otherwise log."""
    try:
        import streamlit as st  # type: ignore  # noqa: PLC0415
        st.warning(message)
    except Exception:
        logger.warning("ChatbotRouter: %s", message)


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


def _build_fallback_chain(start: str) -> list[str]:
    """
    Build the fallback chain starting from *start*, skipping Ollama on cloud.
    Returns an ordered list of engine names to try.
    """
    from src.chatbot.config import is_cloud_env  # noqa: PLC0415

    chain: list[str] = []
    idx = _ENGINE_ORDER.index(start) if start in _ENGINE_ORDER else 0
    for name in _ENGINE_ORDER[idx:]:
        if name == "ollama" and is_cloud_env():
            logger.info(
                "ChatbotRouter: skipping Ollama in fallback chain (cloud env)"
            )
            continue
        chain.append(name)
    return chain


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

    from src.chatbot import engine_detector  # noqa: PLC0415
    engine = engine_detector.detect()
    _set_engine(engine)
    logger.info("ChatbotRouter: engine initialised → '%s'.", engine)
    return engine


def _engine_module(name: str):
    """Return the engine module for the given name."""
    if name == "gemini":
        from src.chatbot import gemini_engine  # noqa: PLC0415
        return gemini_engine
    if name == "ollama":
        from src.chatbot import ollama_engine  # noqa: PLC0415
        return ollama_engine
    from src.chatbot import basic_engine  # noqa: PLC0415
    return basic_engine


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
    chain = _build_fallback_chain(engine_name)

    for i, current_engine in enumerate(chain):
        try:
            mod = _engine_module(current_engine)
            logger.debug(
                "ChatbotRouter: routing to '%s' (stream=%s).", current_engine, stream
            )
            result = mod.ask(messages, stream=stream)

            # For non-streaming: check if the engine returned an error string
            if not stream and isinstance(result, str) and result.startswith("Error:"):
                raise RuntimeError(result)

            if current_engine != engine_name:
                _set_engine(current_engine)

            return result

        except Exception:
            logger.error(
                "ChatbotRouter: engine '%s' failed:\n%s",
                current_engine,
                traceback.format_exc(),
            )

            # Show a friendly warning when Gemini temporarily fails
            if current_engine == "gemini":
                _show_warning(
                    "⚠️ Gemini AI is temporarily unavailable "
                    "(this may be a rate limit or network issue). "
                    "Switching to the built-in Clinical Assistant."
                )

            if i < len(chain) - 1:
                next_engine = chain[i + 1]
                logger.warning(
                    "ChatbotRouter: switching from '%s' → '%s'.",
                    current_engine,
                    next_engine,
                )
                _set_engine(next_engine)
            else:
                # Already at the last engine; return a safe error message
                err = (
                    "I'm having trouble processing your request right now. "
                    "Please try again in a moment."
                )
                logger.critical("ChatbotRouter: all engines exhausted.")
                if stream:
                    def _err_gen():
                        yield err
                    return _err_gen()
                return err


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
        import uuid  # noqa: PLC0415
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
    "Cloud AI"            when Gemini is active
    "Local AI"            when Ollama is active
    "Clinical Assistant"  when the rule-based engine is active

    Stored in st.session_state["ai_engine_label"] for UI use.
    """
    return _ss_get("ai_engine_label") or _ENGINE_LABELS.get(get_active_engine(), "Unknown")


def get_engine_badge() -> str:
    """
    Return an emoji-prefixed engine badge string for inline UI display.

    Examples
    --------
    "✨ Cloud AI"           → shown in sidebar / status bar
    "🦙 Local AI"          → shown when running locally
    "⚙️ Clinical Assistant" → shown when no LLM is connected
    """
    return _ENGINE_BADGES.get(get_active_engine(), get_active_engine())
