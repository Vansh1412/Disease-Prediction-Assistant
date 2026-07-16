# pyrefly: ignore [missing-import]
"""
Sprint 1 — AI Engine Architecture Tests
========================================
Tests:
- GeminiEngine      (mocked API)
- OllamaEngine      (mocked HTTP)
- BasicEngine       (pure logic — no mocking needed)
- EngineDetector    (mocked probes)
- ChatbotRouter     (mocked engines + failover)

Existing tests in test_chatbot.py are NOT modified.
"""

import pytest
from unittest.mock import patch, MagicMock

# ── Streamlit session_state stub (required for chatbot_router) ─────────────
import streamlit as st

@pytest.fixture(autouse=True)
def _mock_st_session(monkeypatch):
    """Provide a fresh dict-backed session_state for every test."""
    class _SS(dict):
        def __getattr__(self, k):
            return self[k] if k in self else None
        def __setattr__(self, k, v):
            self[k] = v

    monkeypatch.setattr(st, "session_state", _SS(), raising=False)
    yield
    st.session_state.clear()


# ===========================================================================
# BasicEngine — no external deps, no mocking required
# ===========================================================================

class TestBasicEngine:
    def test_is_always_available(self):
        from src.chatbot.basic_engine import is_available
        assert is_available() is True

    def test_ask_returns_string_no_stream(self):
        from src.chatbot.basic_engine import ask
        result = ask([{"role": "user", "content": "I have a fever"}], stream=False)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_ask_returns_generator_when_stream(self):
        from src.chatbot.basic_engine import ask
        result = ask([{"role": "user", "content": "Hello"}], stream=True)
        assert hasattr(result, "__iter__")
        chunks = list(result)
        assert len(chunks) == 1
        assert isinstance(chunks[0], str)

    def test_greeting_response(self):
        from src.chatbot.basic_engine import ask
        result = ask([{"role": "user", "content": "Hello!"}], stream=False)
        assert "Clinical Assistant" in result

    def test_emergency_response(self):
        from src.chatbot.basic_engine import ask
        result = ask([{"role": "user", "content": "I think I am having a heart attack"}], stream=False)
        assert "EMERGENCY" in result or "emergency" in result.lower()

    def test_symptom_response(self):
        from src.chatbot.basic_engine import ask
        result = ask([{"role": "user", "content": "I have a headache and fever"}], stream=False)
        assert "Thank you for sharing" in result


# ===========================================================================
# GeminiEngine
# ===========================================================================

class TestGeminiEngine:
    def setup_method(self):
        """Reset module-level state before each test."""
        import src.chatbot.gemini_engine as ge
        ge._client = None
        ge._initialised = False
        ge._init_error = ""

    def test_initialise_missing_package(self):
        """_initialise() returns False when google-generativeai is absent."""
        import src.chatbot.gemini_engine as ge
        ge._initialised = False
        ge._client = None

        # Simulate package not installed by making the import raise ImportError
        original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def _no_genai(name, *args, **kwargs):
            if name == "google" or name == "google.genai":   # new SDK package name
                raise ImportError("No module named 'google.genai'")
            return original_import(name, *args, **kwargs)

        import builtins
        with patch.object(builtins, "__import__", side_effect=_no_genai):
            result = ge._initialise()

        assert result is False
        assert ge._client is None

    def test_is_unavailable_without_key(self):
        """is_available() returns False when GEMINI_API_KEY is empty."""
        import src.chatbot.gemini_engine as ge
        # Set state as if initialise already ran with no key
        ge._initialised = True
        ge._client = None
        ge._init_error = "GEMINI_API_KEY is not set."

        result = ge.is_available()
        assert result is False

    def test_ask_returns_error_string_when_uninitialised(self):
        import src.chatbot.gemini_engine as ge
        ge._initialised = True   # marks "already tried"
        ge._client = None        # but failed
        ge._init_error = "No key"

        result = ge.ask([{"role": "user", "content": "hi"}], stream=False)
        assert isinstance(result, str)
        assert "unavailable" in result.lower() or "gemini" in result.lower()

    def test_ask_stream_returns_generator_when_uninitialised(self):
        import src.chatbot.gemini_engine as ge
        ge._initialised = True
        ge._client = None
        ge._init_error = "No key"

        result = ge.ask([{"role": "user", "content": "hi"}], stream=True)
        assert hasattr(result, "__iter__")


# ===========================================================================
# OllamaEngine
# ===========================================================================

class TestOllamaEngine:
    @patch("src.chatbot.ollama_engine._session")
    def test_is_available_when_server_up_and_model_present(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"models": [{"name": "qwen2.5:3b"}]}
        mock_session.get.return_value = mock_resp

        from src.chatbot.ollama_engine import is_available
        with patch("src.chatbot.ollama_engine.OLLAMA_MODEL", "qwen2.5:3b"):
            assert is_available() is True

    @patch("src.chatbot.ollama_engine._session")
    def test_is_unavailable_when_server_down(self, mock_session):
        import requests
        mock_session.get.side_effect = requests.exceptions.ConnectionError("refused")

        from src.chatbot.ollama_engine import is_available
        assert is_available() is False

    @patch("src.chatbot.ollama_engine._session")
    def test_ask_non_stream(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"message": {"content": "Hello from Ollama"}}
        mock_session.post.return_value = mock_resp

        from src.chatbot.ollama_engine import ask
        result = ask([{"role": "user", "content": "hi"}], stream=False)
        assert result == "Hello from Ollama"

    @patch("src.chatbot.ollama_engine._session")
    def test_ask_returns_error_string_on_connection_failure(self, mock_session):
        import requests
        mock_session.post.side_effect = requests.exceptions.ConnectionError("refused")

        from src.chatbot.ollama_engine import ask
        result = ask([{"role": "user", "content": "hi"}], stream=False)
        assert "Error:" in result

    @patch("src.chatbot.ollama_engine._session")
    def test_ask_stream_returns_generator(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.iter_lines.return_value = [
            b'{"message": {"content": "chunk1"}}',
            b'{"message": {"content": "chunk2"}}',
        ]
        mock_session.post.return_value = mock_resp

        from src.chatbot.ollama_engine import ask
        result = ask([{"role": "user", "content": "hi"}], stream=True)
        chunks = list(result)
        assert chunks == ["chunk1", "chunk2"]


# ===========================================================================
# EngineDetector
# ===========================================================================

class TestEngineDetector:
    def setup_method(self):
        from src.chatbot import engine_detector
        engine_detector.reset()

    def test_selects_gemini_when_available(self):
        from src.chatbot import engine_detector
        with patch("src.chatbot.engine_detector.GEMINI_API_KEY", "fake-key"), \
             patch("src.chatbot.engine_detector.DEFAULT_ENGINE", "auto"), \
             patch("src.chatbot.gemini_engine.is_available", return_value=True):
            result = engine_detector.detect(force=True)
        assert result == "gemini"

    def test_falls_back_to_ollama_when_gemini_unavailable(self):
        from src.chatbot import engine_detector
        with patch("src.chatbot.engine_detector.GEMINI_API_KEY", "fake-key"), \
             patch("src.chatbot.engine_detector.DEFAULT_ENGINE", "auto"), \
             patch("src.chatbot.gemini_engine.is_available", return_value=False), \
             patch("src.chatbot.ollama_engine.is_available", return_value=True):
            result = engine_detector.detect(force=True)
        assert result == "ollama"

    def test_falls_back_to_basic_when_all_unavailable(self):
        from src.chatbot import engine_detector
        with patch("src.chatbot.engine_detector.GEMINI_API_KEY", ""), \
             patch("src.chatbot.engine_detector.DEFAULT_ENGINE", "auto"), \
             patch("src.chatbot.ollama_engine.is_available", return_value=False):
            result = engine_detector.detect(force=True)
        assert result == "basic"

    def test_honours_explicit_override(self):
        from src.chatbot import engine_detector
        with patch("src.chatbot.engine_detector.DEFAULT_ENGINE", "basic"):
            result = engine_detector.detect(force=True)
        assert result == "basic"

    def test_caching(self):
        from src.chatbot import engine_detector
        with patch("src.chatbot.engine_detector.GEMINI_API_KEY", ""), \
             patch("src.chatbot.engine_detector.DEFAULT_ENGINE", "auto"), \
             patch("src.chatbot.ollama_engine.is_available", return_value=False):
            first = engine_detector.detect(force=True)
            second = engine_detector.detect()   # should use cache
        assert first == second == "basic"

    def test_reset_clears_cache(self):
        from src.chatbot import engine_detector
        engine_detector._detected_engine = "gemini"
        engine_detector.reset()
        assert engine_detector._detected_engine is None


# ===========================================================================
# ChatbotRouter — failover
# ===========================================================================

class TestChatbotRouter:
    def setup_method(self):
        from src.chatbot import engine_detector
        engine_detector.reset()
        # Clear session state
        try:
            st.session_state.clear()
        except Exception:
            pass

    def test_ask_llm_uses_active_engine(self):
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "basic"

        result = chatbot_router.ask_llm(
            [{"role": "user", "content": "I feel dizzy"}], stream=False
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_ask_llm_failover_gemini_to_ollama(self):
        """If Gemini raises, router should fall back to Ollama."""
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "gemini"
        st.session_state["ai_engine"] = "gemini"

        with patch("src.chatbot.gemini_engine.ask", side_effect=RuntimeError("API quota exceeded")), \
             patch("src.chatbot.ollama_engine.ask", return_value="Ollama response"):
            result = chatbot_router.ask_llm(
                [{"role": "user", "content": "hi"}], stream=False
            )

        assert result == "Ollama response"
        assert st.session_state.get("ai_engine") == "ollama"

    def test_ask_llm_failover_ollama_to_basic(self):
        """If Ollama raises, router should fall back to Basic."""
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "ollama"
        st.session_state["ai_engine"] = "ollama"

        with patch("src.chatbot.ollama_engine.ask", side_effect=RuntimeError("connection refused")):
            result = chatbot_router.ask_llm(
                [{"role": "user", "content": "I have a fever"}], stream=False
            )

        assert isinstance(result, str)
        assert st.session_state.get("ai_engine") == "basic"

    def test_status_helpers_gemini(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "gemini"
        assert chatbot_router.get_active_engine() == "gemini"
        assert chatbot_router.is_gemini() is True
        assert chatbot_router.is_ollama() is False
        assert chatbot_router.is_basic() is False

    def test_status_helpers_ollama(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "ollama"
        assert chatbot_router.is_gemini() is False
        assert chatbot_router.is_ollama() is True
        assert chatbot_router.is_basic() is False

    def test_status_helpers_basic(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "basic"
        assert chatbot_router.is_gemini() is False
        assert chatbot_router.is_ollama() is False
        assert chatbot_router.is_basic() is True

    def test_init_session_assigns_conversation_id(self):
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "basic"
        chatbot_router.init_session()
        cid = st.session_state.get("ai_conversation_id")
        assert cid is not None
        assert len(cid) > 0

    def test_ask_llm_stream_basic(self):
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "basic"
        st.session_state["ai_engine"] = "basic"

        result = chatbot_router.ask_llm(
            [{"role": "user", "content": "Hello"}], stream=True
        )
        assert hasattr(result, "__iter__")
        chunks = list(result)
        assert len(chunks) >= 1


# ===========================================================================
# Engine Status — display helpers (improvement #3)
# ===========================================================================

class TestEngineStatus:
    def setup_method(self):
        from src.chatbot import engine_detector
        engine_detector.reset()
        try:
            st.session_state.clear()
        except Exception:
            pass

    def test_get_engine_display_name_gemini(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "gemini"
        st.session_state["ai_engine_label"] = "Gemini AI"
        assert chatbot_router.get_engine_display_name() == "Gemini AI"

    def test_get_engine_display_name_ollama(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "ollama"
        st.session_state["ai_engine_label"] = "Ollama (Qwen)"
        assert chatbot_router.get_engine_display_name() == "Ollama (Qwen)"

    def test_get_engine_display_name_basic(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "basic"
        st.session_state["ai_engine_label"] = "Basic Mode"
        assert chatbot_router.get_engine_display_name() == "Basic Mode"

    def test_get_engine_badge_contains_emoji(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "gemini"
        badge = chatbot_router.get_engine_badge()
        assert "Cloud AI" in badge
        assert len(badge) > 6   # must have more than just the name

    def test_get_engine_badge_ollama(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "ollama"
        badge = chatbot_router.get_engine_badge()
        assert "Local AI" in badge

    def test_get_engine_badge_basic(self):
        from src.chatbot import chatbot_router
        st.session_state["ai_engine"] = "basic"
        badge = chatbot_router.get_engine_badge()
        assert "Clinical Assistant" in badge

    def test_session_state_label_written_on_engine_resolution(self):
        """Resolving the engine must write ai_engine_label alongside ai_engine."""
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "basic"  # pre-seed so no probe runs
        chatbot_router.init_session()
        assert st.session_state.get("ai_engine") == "basic"
        assert st.session_state.get("ai_engine_label") == "Clinical Assistant"

    def test_session_state_label_updated_on_failover(self):
        """Failing over must update both ai_engine and ai_engine_label."""
        from src.chatbot import chatbot_router, engine_detector
        engine_detector._detected_engine = "ollama"
        st.session_state["ai_engine"] = "ollama"
        st.session_state["ai_engine_label"] = "Local AI"

        with patch("src.chatbot.ollama_engine.ask", side_effect=RuntimeError("down")):
            chatbot_router.ask_llm([{"role": "user", "content": "hi"}], stream=False)

        assert st.session_state.get("ai_engine") == "basic"
        assert st.session_state.get("ai_engine_label") == "Clinical Assistant"
