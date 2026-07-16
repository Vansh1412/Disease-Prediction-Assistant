from src.prediction.predictor import predict_disease
from src.recommendation.recommendation_engine import get_recommendations
from src.chatbot.chatbot_router import ask_llm

def run_prediction_bridge(symptoms: list[str], model_name: str = "Logistic Regression (Recommended)"):
    """
    Connects the extracted symptoms to the ML models.
    Returns the prediction data and an explanation string.
    """
    top_diseases, error = predict_disease(model_name, symptoms)
    
    if error or not top_diseases:
        return None, "Error running ML models."
        
    top_disease = top_diseases[0]
    disease_name = top_disease["name"]
    confidence = top_disease["confidence"]
    
    recs = get_recommendations(disease_name, confidence)
    
    # Simple direct prompt for Qwen to explain
    explain_prompt = f"""
Our Machine Learning pipeline predicted: {disease_name} (Confidence: {confidence}%).
Symptoms analyzed: {', '.join(symptoms)}.
Recommended Specialist: {recs['specialist']}.
Home Care: {recs['home_care']}.

Explain why these symptoms match the disease in simple language.
Remind the user this is a machine learning prediction, not a clinical diagnosis.
"""
    
    explanation = ask_llm([{"role": "user", "content": explain_prompt}], stream=False)
    
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
        "explanation": explanation
    }
    
    return result, None
