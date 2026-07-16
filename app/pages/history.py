import json

import streamlit as st
import pandas as pd

from app.utils.ui import (
    PageLayout, EmptyState, SecondaryButton
)


def _format_symptoms(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            return value
        if isinstance(decoded, list):
            return ", ".join(str(item) for item in decoded)
    return str(value)


def render_history() -> None:
    """Renders the Prediction History page."""

    with PageLayout(
        "📜",
        "Prediction History",
        "Review past AI predictions from this workspace."
    ):

        if "prediction_history" not in st.session_state or not st.session_state.prediction_history:
            EmptyState(
                "No prediction history yet",
                "Complete an AI Consultation and run a prediction to populate this history console.",
                icon="📜"
            )
            return

        # Render workspace control actions
        col1, col2 = st.columns([4, 1])
        with col2:
            if SecondaryButton("Clear History Log", key="history_clear_log"):
                st.session_state.prediction_history = []
                st.rerun()

        if st.session_state.prediction_history:
            history_df = pd.DataFrame(st.session_state.prediction_history)
            if "symptoms" in history_df:
                history_df["symptoms"] = history_df["symptoms"].apply(_format_symptoms)
                
            # Rename columns for display
            history_df = history_df.rename(columns={
                "date": "Date & Time",
                "symptoms": "Reported Symptoms",
                "disease": "Predicted Disease",
                "confidence": "Confidence (%)",
                "model": "Model Used"
            })

            with st.container(border=True):
                st.dataframe(
                    history_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Confidence (%)": st.column_config.ProgressColumn(
                            "Confidence (%)",
                            help="The model's prediction confidence score",
                            format="%.2f",
                            min_value=0,
                            max_value=100,
                        ),
                        "Date & Time": st.column_config.DatetimeColumn(
                            "Date & Time",
                            format="D MMM YYYY, h:mm a",
                        ),
                        "Reported Symptoms": st.column_config.TextColumn(
                            "Reported Symptoms",
                            width="large"
                        ),
                        "Predicted Disease": st.column_config.TextColumn(
                            "Predicted Disease",
                            width="medium"
                        )
                    },
                )
