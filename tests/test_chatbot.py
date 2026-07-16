# pyrefly: ignore [missing-import]
import pytest
from unittest.mock import patch, MagicMock

from src.chatbot.memory import init_memory, get_symptoms, add_symptoms
from src.chatbot.prediction_bridge import run_prediction_bridge
from src.chatbot.conversation_manager import handle_turn
from src.chatbot.conversation_state import ConversationState

# pyrefly: ignore [missing-import]
import streamlit as st

@pytest.fixture(autouse=True)
def setup_streamlit_state():
    """Mock Streamlit session state for testing."""
    if not hasattr(st, "session_state"):
        class SessionState(dict):
            def __getattr__(self, key):
                if key in self:
                    return self[key]
                raise AttributeError
            def __setattr__(self, key, value):
                self[key] = value
                
        st.session_state = SessionState()
    
    # Clear state before each test
    st.session_state.clear()
    st.session_state.patient_data = {"detected_symptoms": [], "messages": []}
    init_memory()

# --- Memory Tests ---
def test_init_memory():
    assert "patient_data" in st.session_state
    assert "detected_symptoms" in st.session_state.patient_data
    assert "messages" in st.session_state

def test_add_symptoms():
    add_symptoms(["headache", "fever"])
    syms = get_symptoms()
    assert "headache" in syms
    assert "fever" in syms
    
    # Check deduplication
    add_symptoms(["headache", "chills"])
    syms = get_symptoms()
    assert len(syms) == 3
    assert "chills" in syms

# --- Prediction Bridge Tests ---
@patch('src.chatbot.prediction_bridge.predict_disease')
@patch('src.chatbot.prediction_bridge.get_recommendations')
@patch('src.chatbot.prediction_bridge.ask_llm')
def test_prediction_bridge(mock_ask_llm, mock_get_recs, mock_predict_disease):
    # Mock ML Prediction
    mock_predict_disease.return_value = ([
        {"name": "Migraine", "confidence": 95.0},
        {"name": "Tension Headache", "confidence": 75.0}
    ], None)
    
    # Mock Recommendations
    mock_get_recs.return_value = {
        "specialist": "Neurologist",
        "home_care": "Rest in dark room",
        "emergency_level": "Low",
        "lifestyle": "Drink water",
        "red_flags": "Vision loss",
        "risk_color": "Green",
        "body_system": "Neurological"
    }
    
    # Mock LLM Explanation
    mock_ask_llm.return_value = "This is a predicted migraine."
    
    result, error = run_prediction_bridge(["headache"], "Logistic Regression")
    
    assert error is None
    assert result["disease"] == "Migraine"
    assert result["confidence"] == 95.0
    assert result["specialist"] == "Neurologist"
    assert result["explanation"] == "This is a predicted migraine."
    assert len(result["top_diseases"]) == 2

@patch('src.chatbot.prediction_bridge.predict_disease')
def test_prediction_bridge_no_symptoms(mock_predict):
    mock_predict.return_value = ([], "No symptoms provided")
    # Should safely handle empty symptoms
    result, error = run_prediction_bridge([], "Logistic Regression")
    assert result is None
    assert error == "Error running ML models."
