# pyrefly: ignore [missing-import]
import streamlit as st

from app.utils.ui import PageLayout, SectionDivider, render_html


def render_about() -> None:
    """Renders the About page."""

    with PageLayout(
        "ℹ️",
        "About MediSense AI",
        "Clinical diagnostic assistance platform powered by machine learning algorithms.",
    ):
        # ── Platform Overview ────────────────────────────────────────────────
        render_html("""
<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:16px;padding:2rem;margin-bottom:2rem;">
<h3 style="color:#fff;margin-top:0;font-size:1.25rem;font-weight:600;">Platform Overview</h3>
<p style="color:#94A3B8;line-height:1.7;font-size:0.95rem;margin:0;">
MediSense AI is an enterprise-grade medical Web NLU application designed to classify patient symptom reports
and map them directly into disease outcomes. By separating NLU consultation context from mathematical
classification models, it provides rapid educational support to clinicians and patients alike.
</p>
</div>
""")

        col1, col2 = st.columns(2, gap="large")
        with col1:
            render_html("""
<div style="background:rgba(37,99,235,0.05);border:1px solid rgba(37,99,235,0.1);border-radius:16px;padding:1.5rem;">
<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
<span style="font-size:1.2rem;">💻</span>
<h4 style="color:#fff;margin:0;font-size:1.05rem;">SaaS Core Stack</h4>
</div>
<div style="color:#94A3B8;font-size:0.9rem;line-height:1.9;">
<div><strong style="color:#60BDFF;">Interface:</strong> Streamlit, Glassmorphic CSS</div>
<div><strong style="color:#60BDFF;">Language:</strong> Python 3.13</div>
<div><strong style="color:#60BDFF;">Data Structuring:</strong> Pandas, NumPy</div>
<div><strong style="color:#60BDFF;">ML Engine:</strong> Scikit-learn Classifier Pipelines</div>
<div><strong style="color:#60BDFF;">Charts:</strong> Plotly 6 (Interactive)</div>
</div>
</div>
""")

        with col2:
            render_html("""
<div style="background:rgba(16,185,129,0.05);border:1px solid rgba(16,185,129,0.1);border-radius:16px;padding:1.5rem;">
<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:1rem;">
<span style="font-size:1.2rem;">🧠</span>
<h4 style="color:#fff;margin:0;font-size:1.05rem;">Algorithm Ensembles</h4>
</div>
<div style="color:#94A3B8;font-size:0.9rem;line-height:1.9;">
<div><strong style="color:#34D399;">Logistic Regression:</strong> Highly optimised regression — 86.71% accuracy</div>
<div><strong style="color:#34D399;">Decision Tree:</strong> Depth-limited tree partitioning — 81.62% accuracy</div>
<div><strong style="color:#34D399;">KNN Classification:</strong> Instance-based metrics — 82.51% accuracy</div>
<div style="margin-top:0.5rem;"><strong style="color:#34D399;">Training Data:</strong> 4,920 patient symptom records</div>
<div><strong style="color:#34D399;">Feature Space:</strong> 377 binary symptom indicators</div>
</div>
</div>
""")

        render_html("<br>")
        SectionDivider()

        # ── Pipeline Architecture ────────────────────────────────────────────
        render_html("""
<div style="text-align:center;margin:2rem 0 1.5rem;">
<h4 style="color:#fff;font-size:1.25rem;margin:0;">Pipeline Flow Architecture</h4>
</div>
<div style="display:flex;flex-direction:column;align-items:center;gap:0.75rem;max-width:400px;margin:0 auto;">

<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.1);padding:1rem 2rem;border-radius:12px;width:100%;text-align:center;">
<div style="font-size:1.4rem;margin-bottom:0.3rem;">📝</div>
<strong style="color:#fff;font-size:0.9rem;">NLU Input Parser</strong>
<div style="color:#64748B;font-size:0.75rem;margin-top:0.2rem;">Qwen 2.5:3B — Ollama Local LLM</div>
</div>

<div style="color:rgba(255,255,255,0.25);font-size:1.4rem;line-height:1;">↓</div>

<div style="background:rgba(37,99,235,0.06);border:1px solid rgba(37,99,235,0.18);padding:1rem 2rem;border-radius:12px;width:100%;text-align:center;">
<div style="font-size:1.4rem;margin-bottom:0.3rem;">🧬</div>
<strong style="color:#fff;font-size:0.9rem;">Vector Representation</strong>
<div style="color:#64748B;font-size:0.75rem;margin-top:0.2rem;">377 Binary Symptom Features</div>
</div>

<div style="color:rgba(255,255,255,0.25);font-size:1.4rem;line-height:1;">↓</div>

<div style="background:rgba(16,185,129,0.06);border:1px solid rgba(16,185,129,0.18);padding:1rem 2rem;border-radius:12px;width:100%;text-align:center;">
<div style="font-size:1.4rem;margin-bottom:0.3rem;">⚙️</div>
<strong style="color:#fff;font-size:0.9rem;">Statistical Classifiers</strong>
<div style="color:#64748B;font-size:0.75rem;margin-top:0.2rem;">SKLearn — LR / DT / KNN</div>
</div>

<div style="color:rgba(255,255,255,0.25);font-size:1.4rem;line-height:1;">↓</div>

<div style="background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.18);padding:1rem 2rem;border-radius:12px;width:100%;text-align:center;">
<div style="font-size:1.4rem;margin-bottom:0.3rem;">📊</div>
<strong style="color:#fff;font-size:0.9rem;">Explainable Telemetry</strong>
<div style="color:#64748B;font-size:0.75rem;margin-top:0.2rem;">Patient Report &amp; Confidence Score</div>
</div>

</div>
""")

        render_html("<br>")
        SectionDivider()

        # ── Disclaimer ───────────────────────────────────────────────────────
        render_html("""
<div style="background:rgba(245,158,11,0.05);border:1px solid rgba(245,158,11,0.15);border-radius:12px;padding:1.25rem 1.5rem;margin-top:1.5rem;display:flex;gap:0.75rem;align-items:flex-start;">
<span style="font-size:1.3rem;flex-shrink:0;">⚠️</span>
<div>
<strong style="color:#F59E0B;font-size:0.9rem;">Medical Disclaimer</strong>
<p style="color:#94A3B8;font-size:0.85rem;margin:0.3rem 0 0;line-height:1.6;">
MediSense AI is intended for <strong style="color:#fff;">educational and research purposes only</strong>.
It does not constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare
professional for medical decisions.
</p>
</div>
</div>
""")
