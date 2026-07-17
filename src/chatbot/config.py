"""
AI Engine Configuration
=======================
Loads credentials from (in priority order):
  1. Streamlit secrets  (st.secrets) — used on Streamlit Cloud
  2. Environment variables           — used locally and in .env

Never hardcode credentials here.
"""

import os
import logging

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env from the project root (two levels up from this file)
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_env_path, override=False)


def _read_secret(key: str, default: str = "") -> str:
    """
    Read a secret from st.secrets first (Streamlit Cloud), then os.getenv.
    Falls back to *default* if neither is set.
    Safe to call outside Streamlit context.
    """
    # Try st.secrets (available only inside a running Streamlit app)
    try:
        import streamlit as st  # noqa: PLC0415
        value = st.secrets.get(key, "")
        if value:
            return str(value)
    except Exception:
        # st not installed, not running inside Streamlit, or secrets not configured
        pass

    return os.getenv(key, default)


def is_cloud_env() -> bool:
    """
    Return True when running on Streamlit Community Cloud.

    Streamlit Cloud sets the STREAMLIT_SHARING_MODE environment variable
    and also mounts the app at /mount/src. We check both signals.
    """
    if os.getenv("STREAMLIT_SHARING_MODE"):
        return True
    # Secondary check: home directory on Streamlit Cloud is /home/appuser
    if os.path.exists("/mount/src"):
        return True
    return False


# ── Gemini ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = _read_secret("GEMINI_API_KEY")
GEMINI_MODEL: str = _read_secret("GEMINI_MODEL")

# ── Ollama ──────────────────────────────────────────────────────────────────
OLLAMA_HOST: str = _read_secret("OLLAMA_HOST") or "http://localhost:11434"
OLLAMA_MODEL: str = _read_secret("OLLAMA_MODEL") or "qwen2.5:3b"
OLLAMA_TIMEOUT: int = int(_read_secret("OLLAMA_TIMEOUT") or "60")

# ── Engine selector ─────────────────────────────────────────────────────────
# Accepted values: "gemini" | "ollama" | "basic" | "auto"
# "auto" means the detector will probe and pick the best available engine.
DEFAULT_ENGINE: str = (_read_secret("DEFAULT_ENGINE") or "auto").lower()

# ── LLM generation defaults ─────────────────────────────────────────────────
LLM_TEMPERATURE: float = float(_read_secret("LLM_TEMPERATURE") or "0.2")
LLM_TOP_P: float = float(_read_secret("LLM_TOP_P") or "0.9")
LLM_MAX_TOKENS: int = int(_read_secret("LLM_MAX_TOKENS") or "256")

# ── Log effective configuration (key presence only, never value) ────────────
logger.debug(
    "Config loaded — GEMINI_API_KEY=%s, GEMINI_MODEL=%r, DEFAULT_ENGINE=%r, cloud=%s",
    "SET" if GEMINI_API_KEY else "MISSING",
    GEMINI_MODEL or "(auto-select)",
    DEFAULT_ENGINE,
    is_cloud_env(),
)
