import streamlit as st
from datetime import datetime

def render_footer() -> None:
    """Renders a premium sticky footer."""
    year = datetime.now().year
    st.markdown(
        f"""
        <style>
        .saas-footer {{
            margin-top: 3rem;
            padding: 1.4rem 2rem;
            border-top: 1px solid rgba(255,255,255,0.06);
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.8rem;
            background: rgba(5,8,22,0.7);
            backdrop-filter: blur(20px);
            font-family: 'Inter', system-ui, sans-serif;
        }}
        .footer-brand {{
            font-weight: 800;
            font-size: 0.85rem;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            letter-spacing: -0.01em;
        }}
        .footer-dot {{
            width: 6px; height: 6px;
            background: #06B6D4;
            border-radius: 50%;
            box-shadow: 0 0 8px #06B6D4;
            display: inline-block;
        }}
        .footer-center {{
            display: flex;
            align-items: center;
            gap: 1.2rem;
            flex-wrap: wrap;
        }}
        .footer-link {{
            font-size: 0.78rem;
            color: rgba(255,255,255,0.35);
            text-decoration: none;
            transition: color 0.2s;
            font-weight: 500;
        }}
        .footer-link:hover {{ color: rgba(255,255,255,0.7); }}
        .footer-right {{
            font-size: 0.75rem;
            color: rgba(255,255,255,0.25);
        }}
        .footer-pill {{
            display: inline-flex;
            align-items: center;
            gap: 4px;
            background: rgba(16,185,129,0.08);
            border: 1px solid rgba(16,185,129,0.18);
            color: #10B981;
            font-size: 0.62rem;
            font-weight: 700;
            padding: 0.18rem 0.55rem;
            border-radius: 9999px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }}
        .footer-pill-dot {{
            width: 5px; height: 5px;
            background: #10B981;
            border-radius: 50%;
            box-shadow: 0 0 5px #10B981;
        }}
        </style>
        <div class="saas-footer">
            <div class="footer-brand">
                <span class="footer-dot"></span>
                MediSense AI
            </div>
            <div class="footer-center">
                <span class="footer-link">Enterprise Clinical AI</span>
                <span class="footer-link">Enterprise Healthcare Edition</span>
                <span class="footer-pill">
                    <span class="footer-pill-dot"></span> All Systems Operational
                </span>
            </div>
            <div class="footer-right">© {year} MediSense &nbsp;·&nbsp; For professional medical use</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
