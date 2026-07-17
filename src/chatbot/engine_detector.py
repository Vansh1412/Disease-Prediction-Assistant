"""
Engine Detector
===============
Probes available AI engines in priority order and returns the name of the
best engine to use.

Priority
--------
1. Gemini   — if GEMINI_API_KEY is set (config check only, no API probe)
2. Ollama   — if server is reachable AND requested model exists
              (SKIPPED automatically on Streamlit Cloud)
3. Basic    — always available (rule-based fallback)

Detection is done once per application lifetime (cached in module state).
Call reset() to force re-detection (useful in tests).

Public API
----------
detect() → "gemini" | "ollama" | "basic"
reset()  → None
"""

import logging
from src.chatbot.config import DEFAULT_ENGINE, GEMINI_API_KEY, is_cloud_env

logger = logging.getLogger(__name__)

# Module-level cache so detection runs only once per process lifetime
_detected_engine: str | None = None


def detect(force: bool = False) -> str:
    """
    Determine and return the best available engine name.

    Parameters
    ----------
    force : re-run detection even if a cached result exists

    Returns
    -------
    "gemini" | "ollama" | "basic"
    """
    global _detected_engine

    if _detected_engine is not None and not force:
        return _detected_engine

    # ── Honour explicit override ────────────────────────────────────────────
    if DEFAULT_ENGINE in ("gemini", "ollama", "basic"):
        logger.info(
            "EngineDetector: DEFAULT_ENGINE override → '%s' (skipping auto-detect).",
            DEFAULT_ENGINE,
        )
        _detected_engine = DEFAULT_ENGINE
        return _detected_engine

    # ── Auto-detect ─────────────────────────────────────────────────────────
    _cloud = is_cloud_env()
    logger.info(
        "EngineDetector: starting auto-detection (cloud=%s) …", _cloud
    )

    # 1. Gemini — configuration check only (no API probe)
    if GEMINI_API_KEY:
        try:
            from src.chatbot import gemini_engine  # noqa: PLC0415
            if gemini_engine.is_available():
                logger.info("EngineDetector: ✅ Gemini selected (config verified).")
                _detected_engine = "gemini"
                return _detected_engine
            else:
                reason = gemini_engine.get_status()
                logger.warning(
                    "EngineDetector: Gemini config check failed — %s", reason
                )
        except Exception:
            import traceback
            logger.warning(
                "EngineDetector: Gemini import error:\n%s", traceback.format_exc()
            )
    else:
        logger.info(
            "EngineDetector: GEMINI_API_KEY not set — skipping Gemini."
        )

    # 2. Ollama — SKIP on Streamlit Cloud (no local server available)
    if _cloud:
        logger.info(
            "EngineDetector: Running on Streamlit Cloud — "
            "skipping Ollama (no local server available)."
        )
    else:
        try:
            from src.chatbot import ollama_engine  # noqa: PLC0415
            if ollama_engine.is_available():
                logger.info("EngineDetector: ✅ Ollama selected.")
                _detected_engine = "ollama"
                return _detected_engine
            else:
                logger.warning(
                    "EngineDetector: Ollama not reachable or model missing."
                )
        except Exception:
            import traceback
            logger.warning(
                "EngineDetector: Ollama probe error:\n%s", traceback.format_exc()
            )

    # 3. Basic (always succeeds)
    logger.info("EngineDetector: ✅ Clinical Assistant (Basic) selected (fallback).")
    _detected_engine = "basic"
    return _detected_engine


def reset() -> None:
    """Clear the cached detection result, forcing re-detection on next call."""
    global _detected_engine
    _detected_engine = None
    logger.debug("EngineDetector: cache cleared.")
