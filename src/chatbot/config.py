"""
AI Engine Configuration
=======================
Loads environment variables from .env and exposes typed settings
for Gemini, Ollama, and the engine selector.

Never hardcode credentials here.
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_env_path, override=False)

# ── Gemini ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")

# ── Ollama ──────────────────────────────────────────────────────────────────
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "60"))

# ── Engine selector ─────────────────────────────────────────────────────────
# Accepted values: "gemini" | "ollama" | "basic" | "auto"
# "auto" means the detector will probe and pick the best available engine.
DEFAULT_ENGINE: str = os.getenv("DEFAULT_ENGINE", "auto").lower()

# ── LLM generation defaults ─────────────────────────────────────────────────
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_TOP_P: float = float(os.getenv("LLM_TOP_P", "0.9"))
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "256"))
