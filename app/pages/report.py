# pyrefly: ignore [missing-import]
import streamlit as st
import datetime

from app.utils.ui import escape_html, EmptyState, PageLayout
from app.utils.helpers import format_clinical_reasoning

def render_report() -> None:
    """Renders the Premium Medical Report page."""
    
    with PageLayout(
        "📄",
        "Clinical Report",
        "Printable diagnostic summary for your records."
    ):

        if not st.session_state.get("prediction_results"):
            EmptyState(
                "No prediction data found",
                "Complete the AI Consultation and Disease Prediction first to render a clinical summary report.",
                icon="📄"
            )
            return

        p_data = st.session_state.patient_data
        r_data = st.session_state.prediction_results
        user = st.session_state.get("user", {"name": "Guest Patient"})

        if not r_data.get("top_diseases"):
            st.error("Report data is incomplete. Please run prediction again.")
            return

        detected_sym = list(p_data.get("high_conf_symptoms", p_data.get("detected_symptoms", [])))
        sym_str = escape_html(", ".join(detected_sym) if detected_sym else "None")

        current_date = datetime.datetime.now().strftime("%B %d, %Y - %H:%M:%S")
        report_id = f"RPT-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"

        color_map = {
            "Green": "#10B981",
            "Yellow": "#F59E0B",
            "Orange": "#F97316",
            "Red": "#EF4444"
        }
        bar_color = color_map.get(r_data.get("risk_color", "Blue"), "#2563EB")

        top_disease = r_data["top_diseases"][0]
        patient_name = escape_html(user.get("name", "Guest Patient"))
        age = escape_html(p_data.get("age", "N/A"))
        gender = escape_html(str(p_data.get("gender", "N/A")).title())
        pain_level = escape_html(p_data.get("pain_level", "N/A"))
        model_used = escape_html(r_data.get("model_used", "N/A"))
        disease_name = escape_html(top_disease.get("name", "N/A"))
        confidence = escape_html(top_disease.get("confidence", "N/A"))
        body_system = escape_html(r_data.get("body_system", "General"))
        emergency_level = escape_html(r_data.get("emergency_level", "Unknown"))
        specialist = escape_html(r_data.get("specialist", "General Physician"))
        recommendation = escape_html(r_data.get("recommendation", "Rest and stay hydrated."))
        lifestyle = escape_html(r_data.get("lifestyle", "Monitor symptoms and seek professional care if needed."))
        # NOTE: xai must NOT be escape_html'd — format_clinical_reasoning takes raw text
        xai_raw = r_data.get("xai_reasoning", "No LLM reasoning provided.")
        xai_formatted = format_clinical_reasoning(xai_raw)
        _report_html = f"""
<div style="background: rgba(11, 18, 32, 0.7); border: 1px solid var(--border-glass); border-radius: 16px; padding: 2.5rem; max-width: 900px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">

<!-- HEADER -->
<div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid rgba(255,255,255,0.05); padding-bottom: 1.5rem; margin-bottom: 2rem;">
    <div>
        <h1 style="color: #fff; margin: 0; font-size: 2rem; font-weight: 800; display: flex; align-items: center; gap: 0.5rem;">
            <span style="color: var(--primary);">&#x1F4CC;</span> MediSense AI
        </h1>
        <p style="margin: 5px 0 0 0; color: var(--text-muted); font-size: 0.95rem;">Official Clinical Diagnostic Report</p>
    </div>
    <div style="text-align: right;">
        <div style="background: rgba(37,99,235,0.1); border: 1px solid rgba(37,99,235,0.2); padding: 8px 16px; border-radius: 8px; color: #60BDFF; font-weight: 700; font-family: monospace; letter-spacing: 1px;">{report_id}</div>
        <p style="margin: 5px 0 0 0; font-size: 0.75rem; color: var(--text-muted);">Report ID</p>
    </div>
</div>

<!-- PATIENT INFO -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; background: rgba(255,255,255,0.02); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05);">
    <div>
        <p style="margin: 0 0 8px 0; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Patient Details</p>
        <p style="margin: 0 0 5px 0; color: #fff;"><strong style="color: var(--text-muted); width: 100px; display: inline-block;">Name:</strong> {patient_name}</p>
        <p style="margin: 0 0 5px 0; color: #fff;"><strong style="color: var(--text-muted); width: 100px; display: inline-block;">Age/Gender:</strong> {age} / {gender}</p>
        <p style="margin: 0 0 5px 0; color: #fff;"><strong style="color: var(--text-muted); width: 100px; display: inline-block;">Pain Level:</strong> {pain_level}/10</p>
    </div>
    <div style="text-align: right;">
        <p style="margin: 0 0 8px 0; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px;">Session Info</p>
        <p style="margin: 0 0 5px 0; color: #fff;">{current_date} <strong style="color: var(--text-muted); margin-left: 10px;">Date</strong></p>
        <p style="margin: 0 0 5px 0; color: #fff;">{model_used} <strong style="color: var(--text-muted); margin-left: 10px;">Model</strong></p>
    </div>
</div>

<!-- CLINICAL FINDINGS -->
<div style="margin-bottom: 2.5rem;">
    <h4 style="margin: 0 0 10px 0; color: #fff; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">Clinical Findings</h4>
    <p style="margin: 10px 0 0 0; color: #fff; font-size: 0.95rem; line-height: 1.6; background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px;">
        <strong style="color: var(--text-muted); display: block; margin-bottom: 5px;">Reported Symptoms:</strong>
        {sym_str}
    </p>
</div>

<!-- DIAGNOSIS -->
<div style="margin-bottom: 2.5rem;">
    <h4 style="margin: 0 0 15px 0; color: #fff; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">Diagnostic Impression</h4>
    <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(37,99,235,0.05); border: 1px solid rgba(37,99,235,0.15); padding: 1.5rem; border-radius: 12px;">
        <div>
            <h2 style="margin: 0 0 5px 0; color: #fff; font-size: 1.8rem;">{disease_name}</h2>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <span style="background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 4px; font-size: 0.85rem; color: #fff;">Confidence: {confidence}%</span>
                <span style="color: var(--text-muted); font-size: 0.9rem;">Body System: {body_system}</span>
            </div>
        </div>
        <div style="background: {bar_color}15; border: 1px solid {bar_color}40; padding: 12px 24px; border-radius: 8px; text-align: center; min-width: 140px;">
            <strong style="color: {bar_color}; display: block; font-size: 1.1rem;">{emergency_level}</strong>
            <span style="font-size: 0.75rem; color: {bar_color}; text-transform: uppercase; opacity: 0.8;">Severity</span>
        </div>
    </div>
</div>

<!-- REASONING -->
<div style="margin-bottom: 2.5rem;">
    <h4 style="margin: 0 0 12px 0; color: #fff; font-size: 1rem; font-weight: 700; letter-spacing: -0.01em;
               border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px;">Clinical Reasoning (AI XAI)</h4>
    <div style="padding-left: 1rem; border-left: 3px solid rgba(37,99,235,0.6);">
        {xai_formatted}
    </div>
</div>

<!-- RECOMMENDATIONS -->
<div style="margin-bottom: 3rem;">
    <h4 style="margin: 0 0 15px 0; color: #fff; font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px;">Recommendations &amp; Treatment Plan</h4>
    <div style="display: grid; gap: 1rem;">
        <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">&#x1F3E5; Specialist Referral</strong>
            <span style="color: var(--text-muted);">{specialist}</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">&#x1F48A; Immediate Home Care</strong>
            <span style="color: var(--text-muted);">{recommendation}</span>
        </div>
        <div style="background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
            <strong style="color: #fff; display: block; margin-bottom: 4px;">&#x1F9D8; Lifestyle Adjustments</strong>
            <span style="color: var(--text-muted);">{lifestyle}</span>
        </div>
    </div>
</div>

<!-- FOOTER -->
<div style="display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 2rem;">
    <div style="font-size: 0.8rem; color: var(--text-muted); max-width: 60%; line-height: 1.5;">
        <strong>Disclaimer:</strong> This report is generated by an AI application using machine learning. It is not a substitute for professional medical advice, diagnosis, or treatment.
    </div>
    <div style="text-align: right;">
        <div style="border-bottom: 1px solid rgba(255,255,255,0.2); width: 200px; margin-bottom: 8px;"></div>
        <p style="margin: 0; font-size: 0.85rem; color: #fff;">Physician Signature</p>
    </div>
</div>

</div>
"""
        # .strip() ensures <div starts at column 0 — required by CommonMark
        # to treat the block as HTML rather than an indented code block.
        st.markdown(_report_html.strip(), unsafe_allow_html=True)
