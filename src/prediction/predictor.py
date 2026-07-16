# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
import joblib
import pandas as pd
# pyrefly: ignore [missing-import]
import numpy as np
from pathlib import Path

MODEL_DIR = Path("models/general")
DATA_PATH = Path("data/disease_prediction/Final_Augmented_dataset_Diseases_and_Symptoms.csv")


@st.cache_resource
def load_models():
    """Loads all models and the label encoder, caching them to prevent reloading."""
    try:
        models = {
            "Logistic Regression": joblib.load(MODEL_DIR / "LogisticRegression.pkl"),
            "Decision Tree": joblib.load(MODEL_DIR / "DecisionTree.pkl"),
            "KNN": joblib.load(MODEL_DIR / "KNN.pkl")
        }
        encoder = joblib.load(MODEL_DIR / "label_encoder.pkl")
        return models, encoder
    except FileNotFoundError:
        return None, None


@st.cache_data
def load_feature_names():
    """Loads feature names from the dataset."""
    try:
        df = pd.read_csv(DATA_PATH, nrows=0)
        return df.drop(columns=["diseases"]).columns.tolist()
    except FileNotFoundError:
        return []


@st.cache_data
def load_feature_index() -> dict[str, int]:
    """Load a cached symptom-to-column index for fast vector construction."""
    return {feature: index for index, feature in enumerate(load_feature_names())}


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
    "tummy ache": "abdominal pain"
}

def extract_symptoms_from_text(text: str, all_symptoms: list[str]) -> list[str]:
    """Simple keyword and synonym matching to extract symptoms from user text."""
    detected = []
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

def predict_disease(model_name: str, user_symptoms: list[str]):
    """
    Given a model name and a list of detected symptoms,
    returns the top 3 predictions and their confidences.
    """
    models, encoder = load_models()
    if not models or not encoder:
        return None, "Models or encoder not found. Please train models first."
    
    features = load_feature_names()
    feature_index = load_feature_index()
    if not features or not feature_index:
        return None, "Dataset not found. Cannot determine features."

    # Map the display name to the actual model name
    if "Logistic" in model_name:
        model_name = "Logistic Regression"
    elif "Decision" in model_name:
        model_name = "Decision Tree"
    else:
        model_name = "KNN"
             
    model = models.get(model_name)
    if not model:
        return None, f"Model {model_name} not found."

    # Create binary feature vector
    vector = np.zeros(len(features))
    for symptom in user_symptoms:
        idx = feature_index.get(symptom)
        if idx is not None:
            vector[idx] = 1

    # Predict probabilities
    try:
        input_frame = pd.DataFrame([vector], columns=features)
        probabilities = model.predict_proba(input_frame)
    except Exception as e:
        return None, f"Prediction failed: {str(e)}"
        
    # Get top 5 indices
    top_5_idx = np.argsort(probabilities[0])[-5:][::-1]
    
    results = []
    for idx in top_5_idx:
        disease = encoder.inverse_transform([idx])[0]
        prob = probabilities[0][idx]
        results.append({
            "name": disease,
            "confidence": float(round(float(prob) * 100, 2)),
        })
        
    return results, None
