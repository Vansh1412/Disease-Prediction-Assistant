# pyrefly: ignore [missing-import]
import streamlit as st

def init_memory():
    """Initializes the streamlined conversation state."""
    if "patient_data" not in st.session_state:
        st.session_state.patient_data = {
            "age": "Unknown",
            "gender": "Unknown",
            "pain_level": 5
        }
    
    if "detected_symptoms" not in st.session_state.patient_data:
        st.session_state.patient_data["detected_symptoms"] = []
        
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "consultation_step" not in st.session_state:
        st.session_state.consultation_step = 0

def add_message(role: str, content: str):
    """Adds a message to the memory."""
    st.session_state.messages.append({"role": role, "content": content})

def get_chat_history(limit: int = 5) -> str:
    """Gets the recent chat history formatted as a string."""
    history = st.session_state.messages[-limit:]
    return "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in history])

def get_symptoms() -> list[str]:
    """Returns the list of confirmed extracted symptoms."""
    return st.session_state.patient_data.get("detected_symptoms", [])

def add_symptoms(new_symptoms: list[str]):
    """Appends new symptoms uniquely to the patient data."""
    current = st.session_state.patient_data["detected_symptoms"]
    for sym in new_symptoms:
        if sym not in current:
            current.append(sym)
