# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import platform
import sklearn
import os
from pathlib import Path
from datetime import datetime

from app.utils.ui import render_metric_card, render_page_header


@st.cache_data(show_spinner=False)
def _dataset_metrics() -> dict[str, int]:
    data_path = Path("data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv")
    if not data_path.exists():
        return {"samples": 0, "symptoms": 0, "diseases": 0}

    try:
        header = pd.read_csv(data_path, nrows=0)
        diseases = pd.read_csv(data_path, usecols=["diseases"]) if "diseases" in header.columns else pd.DataFrame()
    except (OSError, ValueError, pd.errors.ParserError):
        return {"samples": 0, "symptoms": 0, "diseases": 0}

    return {
        "samples": len(diseases),
        "symptoms": max(len(header.columns) - 1, 0),
        "diseases": diseases["diseases"].nunique() if "diseases" in diseases else 0,
    }


@st.cache_data(show_spinner=False)
def _model_metrics() -> dict[str, str]:
    best_model = "Logistic Regression"
    best_acc = "N/A"
    results_path = Path("reports/model_results.csv")
    if results_path.exists():
        try:
            res_df = pd.read_csv(results_path)
            best_idx = res_df['Accuracy'].idxmax()
            best_model = res_df.loc[best_idx, 'Model']
            best_acc = f"{res_df.loc[best_idx, 'Accuracy'] * 100:.2f}%"
        except (OSError, KeyError, ValueError, pd.errors.ParserError):
            pass

    model_path = Path("models/general/LogisticRegression.pkl")
    training_date = "N/A"
    if model_path.exists():
        mtime = os.path.getmtime(model_path)
        training_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

    return {"best_model": best_model, "best_acc": best_acc, "training_date": training_date}


def render_developer() -> None:
    """Renders the Hidden Developer Dashboard."""

    render_page_header(
        "👨‍💻",
        "Developer Dashboard",
        "System diagnostics and machine learning pipeline metrics.",
    )

    dataset = _dataset_metrics()
    models = _model_metrics()
    py_version = platform.python_version()
    st_version = st.__version__
    sk_version = sklearn.__version__
    predictions_made = len(st.session_state.get("prediction_history", []))

    # UI Layout
    st.markdown("### 📊 Dataset Details")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Dataset Size", f"{dataset['samples']} records")
    with c2:
        render_metric_card("Total Diseases", dataset["diseases"], accent="#10b981")
    with c3:
        render_metric_card("Total Symptoms", dataset["symptoms"], accent="#f59e0b")

    st.markdown("### 🧠 Machine Learning Engine")
    c4, c5, c6 = st.columns(3)
    with c4:
        render_metric_card("Best Performing Model", models["best_model"])
    with c5:
        render_metric_card("Highest Accuracy", models["best_acc"], accent="#10b981")
    with c6:
        render_metric_card("Last Training Run", models["training_date"], accent="#f59e0b")

    st.markdown("### ⚙️ System Environment")
    c7, c8, c9 = st.columns(3)
    with c7:
        render_metric_card("Python Version", py_version)
    with c8:
        render_metric_card("Scikit-Learn Version", sk_version)
    with c9:
        render_metric_card("Streamlit Version", st_version)

    st.markdown("### 🔄 Active Session")
    render_metric_card("Predictions Made", predictions_made, helper="Current session")
