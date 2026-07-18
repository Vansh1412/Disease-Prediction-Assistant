# pyrefly: ignore [missing-import]
import streamlit as st
from datetime import datetime

from app.utils.database import save_prediction
from app.utils.navigation import CONSULTATION, REPORT
from app.utils.ui import escape_html, render_html
from app.utils.helpers import format_clinical_reasoning
from src.chatbot.prediction_bridge import run_prediction_bridge
from src.prediction.predictor import _available_model_names


def _render_hero_diagnosis(res: dict) -> None:
    top = res["top_diseases"][0]
    conf = max(0.0, min(float(top["confidence"]), 100.0))
    
    risk_color_map = {
        "Green": "#10B981",
        "Yellow": "#F59E0B",
        "Orange": "#F97316",
        "Red": "#EF4444"
    }
    color = risk_color_map.get(res["risk_color"], "#06B6D4")
    
    circ = 2 * 3.14159 * 50
    off = circ - (conf / 100) * circ

    render_html(f"""
    <div class="hero-card" style="border-left: 4px solid {color};">
        <div class="hero-content">
            <div class="hero-label">Primary Diagnosis Matrix</div>
            <h1 class="hero-title">{escape_html(top['name'])}</h1>
            <div class="hero-meta">
                <span class="hero-pill" style="color:{color}; background:{color}15; border: 1px solid {color}30;">
                    {escape_html(res['emergency_level'])}
                </span>
                <span class="hero-pill" style="color:rgba(255,255,255,0.7); background:rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);">
                    {escape_html(res['body_system'])}
                </span>
            </div>
        </div>
        
        <div class="hero-gauge">
            <svg width="120" height="120" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="10"></circle>
                <circle cx="60" cy="60" r="50" fill="none" stroke="{color}" stroke-width="10" 
                        stroke-dasharray="{circ}" stroke-dashoffset="{circ}" 
                        style="animation: drawCircle 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;" 
                        transform="rotate(-90 60 60)" stroke-linecap="round">
                    <animate attributeName="stroke-dashoffset" from="{circ}" to="{off}" dur="1.5s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1;"/>
                </circle>
            </svg>
            <div class="gauge-value" style="color: {color};">{conf:.1f}%</div>
        </div>
    </div>
    """)


def _render_differential_timeline(res: dict) -> None:
    # Top 5 Predictions
    diff_html = "<div class='diff-container'>"
    diff_html += "<div class='section-title'>Differential Analysis</div>"
    for d in res["top_diseases"][:5]:
        dc = max(0.0, min(float(d["confidence"]), 100.0))
        diff_html += f"""
        <div class="diff-item">
            <div class="diff-header">
                <span class="diff-name">{escape_html(d['name'])}</span>
                <span class="diff-conf">{dc:.1f}%</span>
            </div>
            <div class="diff-bar-bg">
                <div class="diff-bar-fill" style="width: {dc}%;"></div>
            </div>
        </div>
        """
    diff_html += "</div>"
    
    # Timeline
    tl_html = "<div class='tl-container'>"
    tl_html += "<div class='section-title'>System Execution Timeline</div>"
    tl_html += f"""
    <div class="tl-row">
        <div class="tl-dot"></div>
        <div class="tl-content">
            <div class="tl-time">{datetime.now().strftime('%H:%M:%S.%f')[:-3]}</div>
            <div class="tl-desc">Extracted {len(res['symptoms_used'])} clinical variables via NLP</div>
        </div>
    </div>
    <div class="tl-row">
        <div class="tl-dot"></div>
        <div class="tl-content">
            <div class="tl-time">{datetime.now().strftime('%H:%M:%S.%f')[:-3]}</div>
            <div class="tl-desc">Executed {escape_html(res['model_used'])} Algorithm</div>
        </div>
    </div>
    <div class="tl-row">
        <div class="tl-dot pulse-dot"></div>
        <div class="tl-content">
            <div class="tl-time">{datetime.now().strftime('%H:%M:%S.%f')[:-3]}</div>
            <div class="tl-desc" style="color:#fff; font-weight:600;">Diagnosis isolated with {res['top_diseases'][0]['confidence']:.1f}% confidence</div>
        </div>
    </div>
    """
    tl_html += "</div>"
    
    render_html(diff_html)
    
    # We use a trick to animate the width of diff bars using CSS animation and inline variables
    render_html("""
    <style>
    .diff-bar-fill {
        background: linear-gradient(90deg, var(--accent-blue), #60A5FA);
        height: 100%;
        border-radius: 999px;
        transition: width 1.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    </style>
    """)
    
    render_html(tl_html)


def render_prediction() -> None:
    """Renders the AI Control Room Disease Prediction page."""
    
    symptoms = list(st.session_state.patient_data.get("detected_symptoms", []))
    
    render_html("""
    <style>
    /* Premium Animations & Layouts */
    .fade-in { animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    
    

    
    /* Control Room Header */
    .cr-header {
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
    }
    .cr-title {
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        color: #fff;
    }
    .cr-subtitle {
        color: rgba(255,255,255,0.5);
        font-size: 0.95rem;
        margin-top: 0.25rem;
    }
    
    /* Hero Card */
    .hero-card {
        background: rgba(11, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2rem 2.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .hero-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.4);
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        margin: 0 0 1rem 0;
        color: #fff;
        line-height: 1.1;
    }
    .hero-meta {
        display: flex;
        gap: 0.75rem;
    }
    .hero-pill {
        padding: 0.4rem 1rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .hero-gauge {
        position: relative;
        width: 120px;
        height: 120px;
    }
    .gauge-value {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        font-weight: 800;
    }
    
    /* Differential & Timeline Container */
    .section-title {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.6);
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .diff-container, .tl-container, .action-card {
        background: rgba(11, 18, 32, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    
    .diff-item {
        margin-bottom: 1.25rem;
    }
    .diff-item:last-child {
        margin-bottom: 0;
    }
    .diff-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.4rem;
        font-size: 0.95rem;
    }
    .diff-name {
        color: rgba(255,255,255,0.9);
        font-weight: 500;
    }
    .diff-conf {
        color: #fff;
        font-weight: 700;
    }
    .diff-bar-bg {
        width: 100%;
        height: 6px;
        background: rgba(255,255,255,0.05);
        border-radius: 999px;
        overflow: hidden;
    }
    .diff-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: #3B82F6;
        transition: width 1.5s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* Timeline */
    .tl-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
        position: relative;
    }
    .tl-row:last-child { margin-bottom: 0; }
    .tl-row:not(:last-child)::before {
        content: '';
        position: absolute;
        left: 5px;
        top: 15px;
        bottom: -15px;
        width: 2px;
        background: rgba(255,255,255,0.1);
    }
    .tl-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        border: 2px solid #0B1220;
        margin-top: 4px;
        position: relative;
        z-index: 2;
    }
    .pulse-dot {
        background: #10B981;
        box-shadow: 0 0 10px #10B981;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.8; }
    }
    .tl-content {
        flex: 1;
    }
    .tl-time {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
        margin-bottom: 0.2rem;
        font-family: monospace;
    }
    .tl-desc {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.7);
    }
    
    /* Action Cards */
    .ac-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        color: rgba(255,255,255,0.5);
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .ac-text {
        font-size: 0.95rem;
        color: rgba(255,255,255,0.9);
        line-height: 1.5;
    }
    .ac-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    
    /* Premium Action button styling override */
    [data-testid="stColumn"] [data-testid="stButton"] button {
        background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
        border: none !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
        color: #fff !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        width: 100% !important;
        font-size: 1.05rem !important;
        transition: all 0.3s !important;
    }
    [data-testid="stColumn"] button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(99, 102, 241, 0.45) !important;
    }
    
    /* Config Panel selectors target */
    div[data-testid="stHorizontalBlock"]:has(div[data-baseweb="select"]) {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    </style>
    """)

    render_html("""
    <div class="cr-header">
        <div>
            <h1 class="cr-title">🩺 Diagnostic Engine</h1>
            <div class="cr-subtitle">Statistical inference across KNN, Decision Tree, and Logistic Regression models.</div>
        </div>
    </div>
    """)

    if not symptoms:
        st.warning("No active symptom profile detected. Please complete NLU check-in first.")
        if st.button("Open AI Consultation Console", width="stretch"):
            st.session_state.current_page = CONSULTATION
            st.rerun()
        return

    # Algorithm Selector Row — only show models whose .pkl files exist
    _avail = _available_model_names()
    _model_display_options = []
    for _m in _avail:
        if _m == "Logistic Regression":
            _model_display_options.append("Logistic Regression (Recommended)")
        else:
            _model_display_options.append(_m)

    if not _model_display_options:
        st.error(
            "⚠️ No prediction models are available on this deployment. "
            "Please check server logs for details."
        )
        return

    c1, c2 = st.columns([3, 1])
    with c1:
        model_choice = st.selectbox(
            "Prediction Algorithm",
            _model_display_options,
            label_visibility="visible"
        )
        st.session_state.selected_model = model_choice
    with c2:
        # Align button
        render_html("<div style='height: 1.7rem;'></div>")
        predict_clicked = st.button("Execute Inference", width="stretch")

    if predict_clicked:
        with st.spinner(f"Running inference on {st.session_state.selected_model}..."):
            result, error = run_prediction_bridge(symptoms, st.session_state.selected_model)

        if error or not result:
            st.error(error or "Prediction completed but returned no disease categorization.")
            return
            
        top_disease_name = result["disease"]
        top_disease_conf = result["confidence"]
        
        # Analytics Tracking
        if "analytics" in st.session_state:
            st.session_state.analytics["total_predictions"] += 1
            base_model = st.session_state.selected_model.replace(" (Recommended)", "")
            if base_model in st.session_state.analytics["model_usage"]:
                st.session_state.analytics["model_usage"][base_model] += 1
            for sym in symptoms:
                st.session_state.analytics["symptoms_detected"][sym] = st.session_state.analytics["symptoms_detected"].get(sym, 0) + 1
            st.session_state.analytics["predicted_diseases"][top_disease_name] = st.session_state.analytics["predicted_diseases"].get(top_disease_name, 0) + 1

        if "prediction_history" not in st.session_state:
            st.session_state.prediction_history = []
            
        st.session_state.prediction_history.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symptoms": ", ".join(symptoms),
            "disease": top_disease_name,
            "confidence": top_disease_conf,
            "model": st.session_state.selected_model
        })
        
        if st.session_state.get("logged_in") and "user" in st.session_state:
            save_prediction(st.session_state.user["id"], symptoms, top_disease_name, top_disease_conf, st.session_state.selected_model)

        st.session_state.prediction_results = {
            "model_used": st.session_state.selected_model,
            "top_diseases": result["top_diseases"],
            "recommendation": result["recommendation"],
            "specialist": result["specialist"],
            "emergency_level": result["emergency_level"],
            "lifestyle": result["lifestyle"],
            "risk_color": result["risk_color"],
            "body_system": result["body_system"],
            "symptoms_used": symptoms,
            "xai_reasoning": result["explanation"]
        }
        
    if "prediction_results" in st.session_state and st.session_state.prediction_results:
        res = st.session_state.prediction_results
        
        render_html("<div style='margin-top: 1.5rem;'></div>")
        
        # HERO CARD
        _render_hero_diagnosis(res)
        
        col1, col2 = st.columns([1.2, 1], gap="large")
        
        with col1:
            # Differential
            _render_differential_timeline(res)
            
            # Reasoning
            render_html(f"""
            <div class="action-card" style="border-left: 4px solid #06B6D4;">
                <div class="ac-title">NLU Clinical Reasoning</div>
                <div class="ac-text" style="font-size: 0.8rem; color: rgba(255,255,255,0.5);
                     margin-bottom: 0.9rem; letter-spacing: 0.04em; text-transform: uppercase;">
                    Classifier: {escape_html(res['model_used'])}
                </div>
                <div>{format_clinical_reasoning(res['xai_reasoning'])}</div>
            </div>
            """)

        with col2:
            # Action Cards
            render_html(f"""
            <div class="action-card">
                <span class="ac-icon">👨‍⚕️</span>
                <div class="ac-title">Specialist Referral</div>
                <div class="ac-text">{escape_html(res['specialist'])}</div>
            </div>
            <div class="action-card">
                <span class="ac-icon">📋</span>
                <div class="ac-title">Recommended Actions</div>
                <div class="ac-text">{escape_html(res['recommendation'])}</div>
            </div>
            <div class="action-card">
                <span class="ac-icon">🧘‍♀️</span>
                <div class="ac-title">Lifestyle Adjustments</div>
                <div class="ac-text">{escape_html(res['lifestyle'])}</div>
            </div>
            
            <div style="background: rgba(245, 158, 11, 0.05); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
                <div style="color: #F59E0B; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; margin-bottom: 0.25rem;">⚠️ Medical Disclaimer</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.8rem; line-height: 1.5;">This telemetry dashboard generates diagnostic estimations based on predictive statistical algorithms. It does not replace professional clinical consultations. Always contact your healthcare provider with any medical questions.</div>
            </div>
            """)
            
            if st.button("Generate Official Report", width="stretch"):
                st.session_state.current_page = REPORT
                st.rerun()
