import logging
import traceback

from src.prediction.predictor import predict_disease
from src.recommendation.recommendation_engine import get_recommendations
from src.chatbot.chatbot_router import ask_llm

logger = logging.getLogger(__name__)


def run_prediction_bridge(
    symptoms: list[str],
    model_name: str = "Logistic Regression (Recommended)",
):
    """
    Connects the extracted symptoms to the ML models.

    Returns
    -------
    (result_dict, None)   on success
    (None, error_message) on failure  — error_message is the real error,
                                        not a generic placeholder.
    """
    try:
        top_diseases, error = predict_disease(model_name, symptoms)
    except Exception:
        tb = traceback.format_exc()
        logger.error("[PredictionBridge] predict_disease() raised:\n%s", tb)
        return None, f"ML inference raised an exception — see server logs."

    if error:
        logger.error("[PredictionBridge] predict_disease() returned error: %s", error)
        return None, error

    if not top_diseases:
        msg = "Prediction returned no results."
        logger.error("[PredictionBridge] %s", msg)
        return None, msg

    top_disease = top_diseases[0]
    disease_name = top_disease["name"]
    confidence = top_disease["confidence"]

    try:
        recs = get_recommendations(disease_name, confidence)
    except Exception:
        tb = traceback.format_exc()
        logger.error("[PredictionBridge] get_recommendations() raised:\n%s", tb)
        recs = {
            "specialist": "General Physician",
            "home_care": "Please consult a doctor.",
            "emergency_level": "Unknown",
            "lifestyle": "Maintain a healthy lifestyle.",
            "risk_color": "Yellow",
            "body_system": "General",
        }

    # Ask the LLM to explain the prediction
    explain_prompt = (
        f"Our Machine Learning pipeline predicted: {disease_name} "
        f"(Confidence: {confidence}%).\n"
        f"Symptoms analyzed: {', '.join(symptoms)}.\n"
        f"Recommended Specialist: {recs['specialist']}.\n"
        f"Home Care: {recs['home_care']}.\n\n"
        "Explain why these symptoms match the disease in simple language. "
        "Remind the user this is a machine learning prediction, not a clinical diagnosis."
    )

    try:
        explanation = ask_llm(
            [{"role": "user", "content": explain_prompt}], stream=False
        )
    except Exception:
        tb = traceback.format_exc()
        logger.error("[PredictionBridge] ask_llm() raised:\n%s", tb)
        explanation = (
            f"The ML model predicted **{disease_name}** with "
            f"{confidence:.1f}% confidence based on the reported symptoms."
        )

    result = {
        "disease": disease_name,
        "confidence": confidence,
        "top_diseases": top_diseases,
        "recommendation": recs["home_care"],
        "specialist": recs["specialist"],
        "emergency_level": recs["emergency_level"],
        "lifestyle": recs["lifestyle"],
        "risk_color": recs["risk_color"],
        "body_system": recs["body_system"],
        "explanation": explanation,
    }

    return result, None
