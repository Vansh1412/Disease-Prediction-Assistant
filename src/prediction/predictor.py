# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import joblib
import json
import logging
import traceback
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Robust, CWD-independent paths anchored to this file's location
# ---------------------------------------------------------------------------
# src/prediction/predictor.py  →  project root is 2 levels up
_PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()
MODEL_DIR = _PROJECT_ROOT / "models" / "general"
DATA_PATH = (
    _PROJECT_ROOT
    / "data"
    / "disease_prediction"
    / "Final_Augmented_dataset_Diseases_and_Symptoms.csv"
)
FEATURE_NAMES_JSON = (
    _PROJECT_ROOT
    / "data"
    / "disease_prediction"
    / "feature_names.json"
)


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

def _available_model_names() -> list[str]:
    """
    Return the list of model display names whose .pkl files actually exist.
    This prevents the UI from offering models that are absent on Streamlit Cloud.
    """
    candidates = [
        ("Logistic Regression", MODEL_DIR / "LogisticRegression.pkl"),
        ("Decision Tree",       MODEL_DIR / "DecisionTree.pkl"),
        ("KNN",                 MODEL_DIR / "KNN.pkl"),
    ]
    available = [name for name, path in candidates if path.exists()]
    if not available:
        logger.error(
            "[Predictor] No model files found in %s — check that .pkl files "
            "are committed to git and paths are correct.",
            MODEL_DIR,
        )
    return available


@st.cache_resource
def load_models() -> tuple[dict | None, object | None]:
    """Load all available models and the label encoder."""
    try:
        candidates = {
            "Logistic Regression": MODEL_DIR / "LogisticRegression.pkl",
            "Decision Tree":       MODEL_DIR / "DecisionTree.pkl",
            "KNN":                 MODEL_DIR / "KNN.pkl",
        }
        encoder_path = MODEL_DIR / "label_encoder.pkl"

        if not encoder_path.exists():
            logger.error(
                "[Predictor] label_encoder.pkl not found at %s", encoder_path
            )
            return None, None

        encoder = joblib.load(encoder_path)
        models: dict = {}
        for name, path in candidates.items():
            if path.exists():
                try:
                    models[name] = joblib.load(path)
                    logger.info("[Predictor] Loaded model: %s from %s", name, path)
                except Exception:
                    logger.error(
                        "[Predictor] Failed to load %s:\n%s",
                        path,
                        traceback.format_exc(),
                    )
            else:
                logger.info(
                    "[Predictor] Model file absent (will be hidden from UI): %s", path
                )

        if not models:
            logger.error("[Predictor] No models could be loaded.")
            return None, encoder

        return models, encoder

    except Exception:
        logger.error("[Predictor] load_models() failed:\n%s", traceback.format_exc())
        return None, None


@st.cache_data
def load_feature_names() -> list[str]:
    """
    Load feature names.

    Priority:
    1. Pre-extracted feature_names.json  (always available, committed to git)
    2. Full CSV                          (local dev only, gitignored)

    If neither is available, returns [] and logs a detailed error.
    """
    # 1. Fast path: pre-extracted JSON (cloud-safe)
    if FEATURE_NAMES_JSON.exists():
        try:
            features: list[str] = json.loads(FEATURE_NAMES_JSON.read_text())
            logger.info(
                "[Predictor] Loaded %d feature names from %s",
                len(features),
                FEATURE_NAMES_JSON,
            )
            return features
        except Exception:
            logger.error(
                "[Predictor] Failed to parse %s:\n%s",
                FEATURE_NAMES_JSON,
                traceback.format_exc(),
            )

    # 2. Fallback: full CSV (local dev)
    if DATA_PATH.exists():
        try:
            df = pd.read_csv(DATA_PATH, nrows=0)
            features = df.drop(columns=["diseases"]).columns.tolist()
            logger.info(
                "[Predictor] Loaded %d feature names from CSV at %s",
                len(features),
                DATA_PATH,
            )
            return features
        except Exception:
            logger.error(
                "[Predictor] Failed to load feature names from CSV %s:\n%s",
                DATA_PATH,
                traceback.format_exc(),
            )

    logger.error(
        "[Predictor] No feature source found.\n"
        "  Expected JSON: %s\n"
        "  Expected CSV:  %s\n"
        "  Run scripts/extract_feature_names.py locally and commit the JSON.",
        FEATURE_NAMES_JSON,
        DATA_PATH,
    )
    return []


@st.cache_data
def load_feature_index() -> dict[str, int]:
    """Load a cached symptom-to-column index for fast vector construction."""
    return {feature: index for index, feature in enumerate(load_feature_names())}


# ---------------------------------------------------------------------------
# Synonym normalisation
# ---------------------------------------------------------------------------

SYNONYMS = {
    "high temperature": "fever",
    "stomach ache": "abdominal pain",
    "throwing up": "vomiting",
    "puking": "vomiting",
    "dizzy": "dizziness",
    "can't sleep": "insomnia",
    "heart racing": "palpitations",
    "breathing fast": "shortness of breath",
    "runny nose": "coryza",
    "stuffed nose": "nasal congestion",
    "head hurts": "headache",
    "tired": "fatigue",
    "exhausted": "fatigue",
    "tummy ache": "abdominal pain",
}


def extract_symptoms_from_text(text: str, all_symptoms: list[str]) -> list[str]:
    """Simple keyword and synonym matching to extract symptoms from user text."""
    detected: list[str] = []
    text_lower = text.lower()

    # Check synonyms first
    for phrase, mapped_symptom in SYNONYMS.items():
        if phrase in text_lower:
            if mapped_symptom in all_symptoms:
                detected.append(mapped_symptom)

    # Check exact matches
    for symptom in all_symptoms:
        if symptom in text_lower and symptom not in detected:
            detected.append(symptom)

    return detected


# ---------------------------------------------------------------------------
# Prediction
# ---------------------------------------------------------------------------

def predict_disease(model_name: str, user_symptoms: list[str]):
    """
    Given a model name and a list of detected symptoms,
    returns (top_5_results, None) on success or (None, error_message) on failure.
    Prints the full traceback on every failure.
    """
    try:
        models, encoder = load_models()
        if not models:
            msg = (
                f"No models loaded. MODEL_DIR={MODEL_DIR} — "
                "check that model .pkl files exist and paths are correct."
            )
            logger.error("[Predictor] %s", msg)
            return None, msg

        if encoder is None:
            msg = f"Label encoder not found at {MODEL_DIR / 'label_encoder.pkl'}"
            logger.error("[Predictor] %s", msg)
            return None, msg

        features = load_feature_names()
        feature_index = load_feature_index()
        if not features:
            msg = (
                f"Feature names could not be loaded. "
                f"JSON path: {FEATURE_NAMES_JSON}, CSV path: {DATA_PATH}"
            )
            logger.error("[Predictor] %s", msg)
            return None, msg

        # Normalise display name to internal key
        if "Logistic" in model_name:
            key = "Logistic Regression"
        elif "Decision" in model_name:
            key = "Decision Tree"
        else:
            key = "KNN"

        model = models.get(key)
        if not model:
            available = list(models.keys())
            msg = (
                f"Model '{key}' is not available on this deployment. "
                f"Available models: {available}"
            )
            logger.error("[Predictor] %s", msg)
            return None, msg

        # Build binary feature vector
        vector = np.zeros(len(features))
        matched: list[str] = []
        for symptom in user_symptoms:
            idx = feature_index.get(symptom)
            if idx is not None:
                vector[idx] = 1
                matched.append(symptom)

        logger.info(
            "[Predictor] Running %s with %d/%d symptoms matched",
            key,
            len(matched),
            len(user_symptoms),
        )

        input_frame = pd.DataFrame([vector], columns=features)
        probabilities = model.predict_proba(input_frame)

        # Return top 5
        top_5_idx = np.argsort(probabilities[0])[-5:][::-1]
        results = []
        for i in top_5_idx:
            disease = encoder.inverse_transform([i])[0]
            prob = probabilities[0][i]
            results.append({
                "name": disease,
                "confidence": float(round(float(prob) * 100, 2)),
            })

        return results, None

    except Exception:
        logger.error(
            "[Predictor] predict_disease() raised an unhandled exception:\n%s",
            traceback.format_exc(),
        )
        return None, f"Prediction failed — see server logs for the full traceback."
