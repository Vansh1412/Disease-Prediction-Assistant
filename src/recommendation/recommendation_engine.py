def get_recommendations(disease_name, confidence):
    """
    Returns recommendations, body system, and risk levels based on the predicted disease.
    """
    disease_lower = disease_name.lower()
    
    # Default fallback
    rec = {
        "specialist": "General Physician",
        "severity": "Moderate",
        "emergency_level": "Low",
        "risk_color": "Yellow",
        "body_system": "General",
        "home_care": "Rest and stay hydrated.",
        "lifestyle": "Maintain a healthy diet and monitor your symptoms."
    }
    
    if "fever" in disease_lower or "cold" in disease_lower or "flu" in disease_lower or "infection" in disease_lower:
        rec.update({
            "severity": "Mild",
            "emergency_level": "Low",
            "risk_color": "Green",
            "body_system": "General/Immunological",
            "home_care": "Take plenty of rest, drink warm fluids, and take over-the-counter fever reducers if necessary.",
            "lifestyle": "Wash hands frequently and avoid close contact with others to prevent spreading."
        })
    elif "heart" in disease_lower or "cardio" in disease_lower or "chest" in disease_lower or "myocardial" in disease_lower:
        rec.update({
            "specialist": "Cardiologist",
            "severity": "High",
            "emergency_level": "Emergency",
            "risk_color": "Red",
            "body_system": "Cardiovascular",
            "home_care": "Avoid physical exertion. If experiencing acute chest pain, call emergency services immediately.",
            "lifestyle": "Follow a heart-healthy diet, exercise regularly (as advised by a doctor), and avoid smoking."
        })
    elif "diabetes" in disease_lower or "thyroid" in disease_lower:
        rec.update({
            "specialist": "Endocrinologist",
            "severity": "Moderate",
            "emergency_level": "Low",
            "risk_color": "Yellow",
            "body_system": "Endocrine",
            "home_care": "Monitor blood sugar levels regularly. Stay hydrated.",
            "lifestyle": "Adopt a low-sugar diet and maintain an active lifestyle."
        })
    elif "skin" in disease_lower or "acne" in disease_lower or "rash" in disease_lower or "melanoma" in disease_lower:
        rec.update({
            "specialist": "Dermatologist",
            "severity": "Mild",
            "emergency_level": "Low",
            "risk_color": "Green",
            "body_system": "Dermatological",
            "home_care": "Keep the affected area clean and dry. Avoid scratching.",
            "lifestyle": "Use sunscreen and avoid harsh chemicals on the skin."
        })
    elif "asthma" in disease_lower or "breath" in disease_lower or "lung" in disease_lower or "pneumonia" in disease_lower:
        rec.update({
            "specialist": "Pulmonologist",
            "severity": "High",
            "emergency_level": "High",
            "risk_color": "Orange",
            "body_system": "Respiratory",
            "home_care": "Keep inhalers nearby. Avoid known triggers. Rest upright if breathing is difficult.",
            "lifestyle": "Ensure good indoor air quality and avoid smoking or secondhand smoke."
        })
    elif "stomach" in disease_lower or "gastric" in disease_lower or "ulcer" in disease_lower or "bowel" in disease_lower:
        rec.update({
            "specialist": "Gastroenterologist",
            "severity": "Moderate",
            "emergency_level": "Moderate",
            "risk_color": "Yellow",
            "body_system": "Gastrointestinal",
            "home_care": "Eat a bland diet and stay hydrated. Avoid spicy or fatty foods.",
            "lifestyle": "Maintain a balanced diet rich in fiber and eat smaller, frequent meals."
        })
    elif "brain" in disease_lower or "neuro" in disease_lower or "stroke" in disease_lower or "seizure" in disease_lower:
        rec.update({
            "specialist": "Neurologist",
            "severity": "High",
            "emergency_level": "Emergency",
            "risk_color": "Red",
            "body_system": "Neurological",
            "home_care": "Seek immediate medical attention if symptoms are acute. Ensure the patient is safe from injury.",
            "lifestyle": "Manage stress, get adequate sleep, and attend all medical follow-ups."
        })
    elif "bone" in disease_lower or "muscle" in disease_lower or "joint" in disease_lower or "arthritis" in disease_lower:
        rec.update({
            "specialist": "Orthopedist / Rheumatologist",
            "severity": "Moderate",
            "emergency_level": "Low",
            "risk_color": "Yellow",
            "body_system": "Musculoskeletal",
            "home_care": "Rest the affected area. Apply ice or heat as appropriate.",
            "lifestyle": "Engage in low-impact exercises like swimming and maintain a healthy weight."
        })
        
    return rec
