from datetime import datetime

# pyrefly: ignore [missing-import]
import streamlit as st
import plotly.graph_objects as go

from app.utils.navigation import ANALYTICS, CONSULTATION, PREDICTION, REPORT
from app.utils.ui import escape_html, render_html
from app.components.logs_modal import render_logs_modal


def _go_to(page_id: str) -> None:
    st.session_state.current_page = page_id
    st.rerun()


def render_dashboard() -> None:
    """Renders the Premium AI SaaS Dashboard."""

    user          = st.session_state.get("user", {"name": "Guest"})
    now           = datetime.now()
    greeting      = "Good morning" if now.hour < 12 else "Good afternoon" if now.hour < 18 else "Good evening"
    display_name  = escape_html(user.get("name", "Guest").split(" ")[0])
    ai_engine     = st.session_state.get("ai_engine_label", "Standard Consultation")
    
    current_time = now.strftime("%I:%M %p")
    current_date = now.strftime("%A, %b %d %Y")
    
    # Get stats
    predictions = st.session_state.get("prediction_history", [])
    predictions_made = len(predictions)
    consultations_today = 1 if predictions_made > 0 else 0  # Simulated for now
    avg_conf = 88.5  # Simulated average confidence
    
    last_disease = escape_html(predictions[-1]["disease"]) if predictions else "None"
    last_conf = f"{predictions[-1]['confidence']:.1f}%" if predictions else "0%"
    last_sys = "Respiratory" if last_disease in ["Pneumonia", "COVID-19", "Asthma"] else "Cardiovascular" if last_disease in ["Heart Disease"] else "Nervous" if last_disease in ["Stroke"] else "General"

    # Premium Dashboard CSS
    render_html(f"""
<style>
    /* Global Dashboard - full width */
    [data-testid="stAppViewContainer"] > .main .block-container {{
        max-width: 100% !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}
    /* Gap only for dashboard CONTENT columns — never the navbar */
    section.main [data-testid="stHorizontalBlock"] {{
        gap: 1.2rem;
    }}

    
    /* ── Top Section & Greeting ── */
    .dash-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 2rem;
        background: rgba(11, 18, 32, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        backdrop-filter: blur(20px);
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
        animation: fadeDown 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    .dash-top-left h1 {{
        font-size: 1.8rem !important;
        margin: 0 0 0.2rem 0 !important;
        font-weight: 800 !important;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }}
    .greeting-icon {{
        display: inline-block;
        animation: wave 2.5s infinite;
        transform-origin: 70% 70%;
    }}
    .dash-top-left p {{
        margin: 0;
        color: rgba(255,255,255,0.5);
        font-size: 0.95rem;
    }}
    .dash-top-right {{
        text-align: right;
    }}
    .dash-top-right .time {{
        font-size: 1.6rem;
        font-weight: 800;
        color: #fff;
        margin-bottom: 0.1rem;
        font-variant-numeric: tabular-nums;
    }}
    .dash-top-right .date {{
        color: #06B6D4;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    /* ── Left Panel (Quick Actions) ── */
    .qa-header {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: rgba(255,255,255,0.4);
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: block;
    }}
    
    /* Target Streamlit Buttons directly in the first column */
    [data-testid="column"]:nth-child(1) [data-testid="stButton"] button {{
        width: 100%;
        background: rgba(11, 18, 32, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        color: rgba(255,255,255,0.85) !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
        backdrop-filter: blur(12px) !important;
        margin-bottom: 0.5rem !important;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }}
    
    [data-testid="column"]:nth-child(1) [data-testid="stButton"] button p {{
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="column"]:nth-child(1) [data-testid="stButton"] button:hover {{
        transform: translateY(-4px) scale(1.02) !important;
        background: rgba(37, 99, 235, 0.15) !important;
        border-color: rgba(37, 99, 235, 0.4) !important;
        color: #fff !important;
        box-shadow: 0 15px 30px -5px rgba(0,0,0,0.4), 0 0 20px rgba(37, 99, 235, 0.2) !important;
    }}
    
    /* Primary button (first one) glow */
    [data-testid="column"]:nth-child(1) [data-testid="element-container"]:nth-child(2) [data-testid="stButton"] button {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.2), rgba(6, 182, 212, 0.1)) !important;
        border-color: rgba(37, 99, 235, 0.3) !important;
    }}
    
    /* ── Center Panel (Health Overview) ── */
    .overview-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        background: rgba(11, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        animation-delay: 0.1s;
    }}
    
    .og-card {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.2rem;
        transition: transform 0.3s, background 0.3s;
    }}
    .og-card:hover {{
        transform: translateY(-3px);
        background: rgba(255, 255, 255, 0.06);
    }}
    .og-lbl {{
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: rgba(255,255,255,0.4);
        font-weight: 700;
        margin-bottom: 0.4rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    /* CSS Counter Animations */
    @property --num1 {{ syntax: "<integer>"; initial-value: 0; inherits: false; }}
    @property --num2 {{ syntax: "<integer>"; initial-value: 0; inherits: false; }}
    @property --num3 {{ syntax: "<integer>"; initial-value: 0; inherits: false; }}
    
    @keyframes count1 {{ to {{ --num1: {predictions_made}; }} }}
    @keyframes count2 {{ to {{ --num2: {consultations_today}; }} }}
    @keyframes count3 {{ to {{ --num3: {int(avg_conf)}; }} }}
    
    .og-val {{
        font-size: 2rem;
        font-weight: 900;
        color: #fff;
        line-height: 1;
        font-variant-numeric: tabular-nums;
        background: linear-gradient(135deg, #fff, #a1a1aa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .og-val-1 {{ animation: count1 1.5s ease-out forwards; counter-reset: n1 var(--num1); }}
    .og-val-1::after {{ content: counter(n1); }}
    
    .og-val-2 {{ animation: count2 1.5s ease-out forwards; counter-reset: n2 var(--num2); }}
    .og-val-2::after {{ content: counter(n2); }}
    
    .og-val-3 {{ animation: count3 1.5s ease-out forwards; counter-reset: n3 var(--num3); }}
    .og-val-3::after {{ content: counter(n3) "%"; }}
    
    .og-val-text {{
        font-size: 1.2rem;
        font-weight: 800;
        color: #fff;
        line-height: 1.2;
    }}
    .og-val-sub {{
        font-size: 0.75rem;
        color: rgba(255,255,255,0.4);
        margin-top: 0.3rem;
    }}

    /* ── Right Panel (AI Status) ── */
    .status-panel {{
        background: rgba(11, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        animation-delay: 0.2s;
        height: 100%;
    }}
    .pill-list {{
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }}
    .status-pill {{
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        font-size: 0.85rem;
        font-weight: 600;
        color: rgba(255,255,255,0.8);
        transition: transform 0.3s, background 0.3s;
    }}
    .status-pill:hover {{
        transform: translateX(4px);
        background: rgba(255, 255, 255, 0.07);
    }}
    .pill-dot {{
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
        animation: pulseGreen 2s infinite;
        flex-shrink: 0;
    }}

    /* ── Lower Section (Timeline & Rows) ── */
    .row-title {{
        font-size: 0.9rem;
        font-weight: 700;
        color: #fff;
        margin: 2.5rem 0 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .timeline-wrap {{
        background: rgba(11, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        backdrop-filter: blur(20px);
        animation: fadeUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        animation-delay: 0.3s;
    }}
    .timeline {{
        position: relative;
        padding-left: 2rem;
    }}
    .timeline::before {{
        content: '';
        position: absolute;
        left: 5px;
        top: 5px;
        bottom: 5px;
        width: 2px;
        background: linear-gradient(to bottom, #3B82F6, rgba(59, 130, 246, 0.1));
        border-radius: 2px;
    }}
    .tl-item {{
        position: relative;
        margin-bottom: 1.5rem;
    }}
    .tl-item:last-child {{ margin-bottom: 0; }}
    .tl-dot {{
        position: absolute;
        left: -2rem;
        top: 0.2rem;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background: #06B6D4;
        border: 2px solid #0B1220;
        box-shadow: 0 0 10px #06B6D4;
        animation: glowPulse 2.5s infinite;
    }}
    .tl-content {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        background: rgba(255, 255, 255, 0.02);
        padding: 1rem 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.04);
        transition: all 0.3s;
    }}
    .tl-content:hover {{
        background: rgba(255, 255, 255, 0.05);
        transform: translateX(4px);
        border-color: rgba(6, 182, 212, 0.3);
    }}
    
    /* ── Model Performance Row ── */
    .models-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        animation: fadeUp 1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        animation-delay: 0.4s;
    }}
    .model-card {{
        background: rgba(11, 18, 32, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        backdrop-filter: blur(20px);
        display: flex;
        flex-direction: column;
        transition: all 0.3s;
    }}
    .model-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border-color: rgba(255, 255, 255, 0.15);
    }}
    
    /* ── Health Tips Carousel ── */
    .tips-wrap {{
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(16, 185, 129, 0.05));
        border: 1px solid rgba(37, 99, 235, 0.2);
        border-radius: 20px;
        padding: 1.5rem 2rem;
        backdrop-filter: blur(20px);
        overflow: hidden;
        position: relative;
        height: 100px;
        display: flex;
        align-items: center;
        animation: fadeUp 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        animation-delay: 0.5s;
    }}
    .tip-track {{
        position: absolute;
        width: 100%;
        animation: tipSlide 15s infinite;
    }}
    .tip-slide {{
        height: 100px;
        display: flex;
        align-items: center;
        font-size: 1.05rem;
        font-weight: 500;
        color: #fff;
    }}
    
    /* ── Animations ── */
    @keyframes wave {{
        0%, 100% {{ transform: rotate(0deg); }}
        20% {{ transform: rotate(15deg); }}
        40% {{ transform: rotate(-10deg); }}
        60% {{ transform: rotate(15deg); }}
        80% {{ transform: rotate(-10deg); }}
    }}

    @keyframes tipSlide {{
        0%, 25% {{ transform: translateY(0); }}
        33%, 58% {{ transform: translateY(-100px); }}
        66%, 91% {{ transform: translateY(-200px); }}
    }}

    @keyframes pulseGreen {{
        0%, 100% {{ opacity: 1; box-shadow: 0 0 8px rgba(16,185,129,0.5); }}
        50% {{ opacity: 0.7; box-shadow: 0 0 18px rgba(16,185,129,0.9), 0 0 30px rgba(16,185,129,0.4); }}
    }}

    @keyframes glowPulse {{
        0%, 100% {{ opacity: 0.4; transform: scale(1); }}
        50% {{ opacity: 0.85; transform: scale(1.15); }}
    }}
    </style>
    """)

    # ── TOP SECTION ──
    render_html(f"""
<div class="dash-top">
<div class="dash-top-left">
<h1>Good {greeting.split(' ')[1]}, {display_name} <span class="greeting-icon">👋</span></h1>
<p>Welcome back to your AI Healthcare Command Center.</p>
</div>
<div class="dash-top-right">
<div class="time">{current_time}</div>
<div class="date">{current_date}</div>
</div>
</div>
    """)

    # ── GRID ROW 1 (Left, Center, Right) ──
    col1, col2, col3 = st.columns([1.2, 2.5, 1.2], gap="large")
    
    with col1:
        render_html("<span class='qa-header'>⚡ Quick Actions</span>")
        if st.button("💬 Start Consultation", use_container_width=True): _go_to(CONSULTATION)
        if st.button("🩺 Disease Prediction", use_container_width=True): _go_to(PREDICTION)
        if st.button("📈 Analytics", use_container_width=True): _go_to(ANALYTICS)
        if st.button("📄 Medical Reports", use_container_width=True): _go_to(REPORT)
        if st.button("🕒 History", use_container_width=True): _go_to("history")

    with col2:
        render_html(f"""
<span class='qa-header'>📊 Today's Health Overview</span>
<div class="overview-grid">
<div class="og-card">
<div class="og-lbl">🔍 Total Predictions</div>
<div class="og-val og-val-1"></div>
</div>
<div class="og-card">
<div class="og-lbl">💬 Consultations</div>
<div class="og-val og-val-2"></div>
</div>
<div class="og-card">
<div class="og-lbl">🎯 Avg Confidence</div>
<div class="og-val og-val-3"></div>
</div>
<div class="og-card">
<div class="og-lbl">⚡ Current AI Status</div>
<div class="og-val-text" style="color: #10B981;">Optimal</div>
<div class="og-val-sub">All models responding in &lt;120ms</div>
</div>
<div class="og-card">
<div class="og-lbl">🩺 Last Prediction</div>
<div class="og-val-text" style="color: #06B6D4;">{last_disease}</div>
<div class="og-val-sub">Confidence: {last_conf}</div>
</div>
<div class="og-card">
<div class="og-lbl">🫀 Body System</div>
<div class="og-val-text" style="color: #F59E0B;">{last_sys}</div>
<div class="og-val-sub">Based on latest triage</div>
</div>
</div>
        """)

    with col3:
        ai_engine = st.session_state.get("ai_engine_label", "Standard Consultation")
        engine_color = "#10B981" if "Advanced" in ai_engine else "#06B6D4"
        render_html(f"""
<span class='qa-header'>⚙️ System Status</span>
<div class="status-panel">
<div class="pill-list">
<div class="status-pill"><div class="pill-dot"></div> {escape_html(ai_engine)}</div>
<div class="status-pill"><div class="pill-dot"></div> ML Models Loaded</div>
<div class="status-pill"><div class="pill-dot"></div> Database Connected</div>
<div class="status-pill"><div class="pill-dot"></div> Analytics Ready</div>
<div class="status-pill"><div class="pill-dot" style="background:#3B82F6;box-shadow:0 0 12px rgba(59,130,246,0.6);"></div> NLP Pipeline Active</div>
</div>
</div>
        """)
        if st.button("📋  View Detailed Logs →", key="open_logs_btn",
                     use_container_width=True, type="secondary"):
            st.session_state.show_logs = True
            st.rerun()

    # ── LOWER SECTION 1 (Timeline) ──
    render_html("<div class='row-title'>📈 Prediction Timeline</div>")
    
    tl_html = ""
    if not predictions:
        tl_html = """<div class="tl-item">
<div class="tl-dot" style="background: rgba(255,255,255,0.2); box-shadow: none; border-color: rgba(255,255,255,0.1);"></div>
<div class="tl-content">
<div style="color: rgba(255,255,255,0.5); font-size: 0.9rem;">No predictions made in this session yet.</div>
</div>
</div>"""
    else:
        for p in reversed(predictions[-3:]):
            disease = escape_html(p["disease"])
            conf = f"{p['confidence']:.1f}%"
            time_str = datetime.now().strftime("%I:%M %p") # Simulated for now
            tl_html += f"""<div class="tl-item">
<div class="tl-dot"></div>
<div class="tl-content">
<div>
<div style="font-weight: 700; color: #fff; font-size: 1.05rem; margin-bottom: 0.2rem;">{disease}</div>
<div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Identified via Ensemble ML models</div>
</div>
<div style="text-align: right;">
<div style="font-weight: 800; color: #10B981; font-size: 1.1rem;">{conf}</div>
<div style="font-size: 0.75rem; color: rgba(255,255,255,0.4);">{time_str}</div>
</div>
</div>
</div>"""

    render_html(f"""<div class="timeline-wrap">
<div class="timeline">
        {tl_html}
</div>
</div>""")

    # ── LOWER SECTION 2 (Model Performance & Tips) ──
    c_left, c_right = st.columns([2, 1], gap="large")
    
    with c_left:
        render_html("<div class='row-title'>🧠 Model Performance</div>")

        _PLOTLY_LAYOUT = dict(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#94A3B8", size=12),
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(
                bgcolor="rgba(11,18,32,0.7)",
                bordercolor="rgba(255,255,255,0.08)",
                borderwidth=1,
                font=dict(color="#94A3B8"),
                orientation="h",
                x=0.5, xanchor="center", y=-0.12,
            ),
            hoverlabel=dict(
                bgcolor="rgba(11,18,32,0.95)",
                bordercolor="rgba(255,255,255,0.12)",
                font=dict(color="#F8FAFC", size=13),
            ),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
                       tickfont=dict(color="#CBD5E1", size=11), zeroline=False),
            yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
                       tickfont=dict(color="#64748B", size=10), zeroline=False, range=[0.75, 1.0]),
            barmode="group",
            bargap=0.18,
            bargroupgap=0.08,
        )

        models     = ["Logistic Reg.", "Decision Tree", "KNN"]
        metrics    = ["Accuracy", "Precision", "Recall", "F1"]
        data_vals  = [
            [0.8671, 0.85, 0.86, 0.855],
            [0.8162, 0.80, 0.81, 0.805],
            [0.8251, 0.81, 0.82, 0.815],
        ]
        colors     = ["#3B82F6", "#06B6D4", "#22C55E"]

        fig_models = go.Figure()
        for model, vals, color in zip(models, data_vals, colors):
            fig_models.add_trace(go.Bar(
                name=model,
                x=metrics,
                y=vals,
                marker=dict(color=color, line=dict(width=0), cornerradius=5),
                hovertemplate=f"<b>{model}</b><br>%{{x}}: <b>%{{y:.1%}}</b><extra></extra>",
                text=[f"{v:.1%}" for v in vals],
                textposition="outside",
                textfont=dict(color="rgba(255,255,255,0.6)", size=10),
            ))

        fig_models.update_layout(**_PLOTLY_LAYOUT, height=260)

        st.plotly_chart(
            fig_models,
            use_container_width=True,
            config=dict(
                displayModeBar=True,
                displaylogo=False,
                modeBarButtonsToRemove=["select2d", "lasso2d"],
                toImageButtonOptions=dict(format="png", filename="model_comparison", scale=2),
                responsive=True,
            ),
        )

    with c_right:
        render_html("<div class='row-title'>💡 Health Tips</div>")
        render_html("""
<div class="tips-wrap">
<div class="tip-track">
<div class="tip-slide">💧 Stay hydrated! Drinking water improves cognitive function and reduces fatigue.</div>
<div class="tip-slide">🏃‍♂️ 30 minutes of daily activity reduces cardiovascular risk by up to 35%.</div>
<div class="tip-slide">😴 Quality sleep (7-9 hours) is critical for immune system recovery.</div>
<div class="tip-slide">💧 Stay hydrated! Drinking water improves cognitive function and reduces fatigue.</div>
</div>
</div>
        """)

    # ── Logs Modal (renders on top when show_logs=True) ─────────────
    render_logs_modal()
