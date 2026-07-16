# pyrefly: ignore [missing-import]
from copy import deepcopy

import streamlit as st

from app.utils.navigation import DEFAULT_PAGE_ID, normalize_page_id


DEFAULT_ANALYTICS = {
    "total_predictions": 0,
    "model_usage": {"Logistic Regression": 0, "Decision Tree": 0, "KNN": 0},
    "symptoms_detected": {},
    "predicted_diseases": {},
}

DEFAULT_PATIENT_DATA = {
    "symptoms": "",
    "duration": "",
    "age": None,
    "gender": "",
    "pain_level": 5,
    "history": "",
    "detected_symptoms": [],
}

WELCOME_MESSAGE = (
    "Hello. I am MediSense AI.\n\n"
    "Tell me what symptoms you are having, and I will help organize them "
    "before you run a prediction."
)


def init_session_state() -> None:
    """Initialize global session state variables for the app."""
    st.session_state.setdefault("logged_in", False)
    st.session_state.setdefault("is_admin", False)
    st.session_state["current_page"] = normalize_page_id(
        st.session_state.get("current_page", DEFAULT_PAGE_ID)
    )

    st.session_state.setdefault(
        "messages",
        [{"role": "assistant", "content": WELCOME_MESSAGE}],
    )
    st.session_state.setdefault("consultation_step", 1)
    st.session_state.setdefault("patient_data", deepcopy(DEFAULT_PATIENT_DATA))
    st.session_state.patient_data.setdefault("detected_symptoms", [])

    st.session_state.setdefault("selected_model", "Logistic Regression")
    st.session_state.setdefault("prediction_results", None)
    st.session_state.setdefault("prediction_history", [])
    st.session_state.setdefault("analytics", deepcopy(DEFAULT_ANALYTICS))
    st.session_state.setdefault("show_logs", False)
    # Sprint 3 clinical state (populated by conversation_manager)
    st.session_state.setdefault("clinical_state", None)
    # AI engine display label — never exposes model name
    st.session_state.setdefault("ai_engine_label", "Standard Consultation")

