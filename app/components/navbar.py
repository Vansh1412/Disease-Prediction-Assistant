"""
app/components/navbar.py
Premium sticky navbar — avatar, engine badge, active highlight.
Never exposes AI model internals — shows "Advanced AI" or "Standard Consultation".
"""
from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st
from app.utils.navigation import DEFAULT_PAGE_ID, get_page_options, get_page_label

_LABELS: dict[str, str] = {
    "dashboard":    "Dashboard",
    "consultation": "Consult",
    "prediction":   "Predict",
    "history":      "History",
    "comparison":   "Compare",
    "report":       "Report",
    "analytics":    "Analytics",
    "about":        "About",
    "developer":    "Dev",
    "admin":        "Admin",
}

_NAV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Sticky navbar wrapper ───────────────────────────────────── */
[data-key="medisense-nav"] {
    background: rgba(5, 8, 22, 0.97) !important;
    border-bottom: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    padding: 0.18rem 0.8rem !important;
    margin: 0 0 1.1rem 0 !important;
    border-radius: 0 !important;
    box-shadow: 0 2px 24px rgba(0,0,0,0.55) !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    width: 100% !important;
    box-sizing: border-box !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}

[data-key="medisense-nav"] > div,
[data-key="medisense-nav"] [data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 2px !important;
    align-items: center !important;
    overflow: visible !important;
    width: 100% !important;
}

/* Nav buttons — base style */
[data-key="medisense-nav"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: rgba(255,255,255,0.45) !important;
    font-weight: 500 !important;
    font-size: 0.72rem !important;
    padding: 0.2rem 0.45rem !important;
    border-radius: 6px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    height: 28px !important;
    min-height: 0 !important;
    line-height: 1 !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
[data-key="medisense-nav"] .stButton > button:hover {
    color: #fff !important;
    background: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.1) !important;
}

/* Active page button */
[data-key="medisense-nav"] .stButton > button[kind="primary"],
[data-key="medisense-nav"] .stButton > button[data-testid="stBaseButton-primary"] {
    color: #60BDFF !important;
    background: rgba(37, 99, 235, 0.15) !important;
    border-color: rgba(37, 99, 235, 0.3) !important;
    font-weight: 700 !important;
}

/* Brand column */
.ms-nav-brand {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 800;
    font-size: 0.86rem;
    color: #fff;
    white-space: nowrap;
    padding: 0 0.3rem;
    letter-spacing: -0.01em;
    user-select: none;
    font-family: 'Inter', system-ui, sans-serif;
}
.ms-nav-dot {
    width: 7px; height: 7px;
    background: #06B6D4;
    border-radius: 50%;
    box-shadow: 0 0 8px #06B6D4;
    flex-shrink: 0;
    animation: msNavDotPulse 3s ease-in-out infinite;
}
@keyframes msNavDotPulse {
    0%,100% { box-shadow: 0 0 5px #06B6D4; }
    50%      { box-shadow: 0 0 14px #06B6D4, 0 0 26px rgba(6,182,212,0.45); }
}

/* Engine badge */
.ms-engine-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(6,182,212,0.08);
    border: 1px solid rgba(6,182,212,0.2);
    color: #06B6D4;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    white-space: nowrap;
    animation: msNavDotPulse 4s ease-in-out infinite;
    font-family: 'Inter', system-ui, sans-serif;
}
.ms-engine-dot {
    width: 5px; height: 5px;
    background: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 6px #10B981;
    animation: msNavDotPulse 2s ease-in-out infinite;
}

/* Admin badge */
.ms-admin-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: rgba(245,158,11,0.1);
    border: 1px solid rgba(245,158,11,0.25);
    color: #F59E0B;
    font-size: 0.62rem;
    font-weight: 700;
    padding: 0.2rem 0.55rem;
    border-radius: 9999px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    white-space: nowrap;
}

/* User avatar */
.ms-nav-avatar {
    width: 26px; height: 26px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563EB, #06B6D4);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.72rem;
    font-weight: 800;
    color: #fff;
    flex-shrink: 0;
    box-shadow: 0 0 10px rgba(37,99,235,0.4);
}

/* Logout button — subtle red tint */
[data-key="medisense-nav"] [data-testid="column"]:last-child .stButton > button {
    color: rgba(239,68,68,0.6) !important;
    border-color: rgba(239,68,68,0.15) !important;
    font-size: 0.69rem !important;
}
[data-key="medisense-nav"] [data-testid="column"]:last-child .stButton > button:hover {
    color: #EF4444 !important;
    background: rgba(239,68,68,0.08) !important;
    border-color: rgba(239,68,68,0.3) !important;
}
</style>
"""



def render_navbar() -> str:
    """
    Renders the premium sticky navbar.
    Returns the current page_id to render.

    Both patients and admin users see all page tabs.
    Admin users also get an extra 'Admin' tab at the end.
    All buttons work for everyone.
    """
    is_admin = st.session_state.get("is_admin", False)
    dev_mode = st.query_params.get("dev", "false").lower() == "true"

    # Build page list: normal pages + Admin tab for admin users
    pages = get_page_options(dev_mode)
    if is_admin and "admin" not in pages:
        pages = pages + ["admin"]

    current = st.session_state.get("current_page", DEFAULT_PAGE_ID)
    if current not in pages:
        current = DEFAULT_PAGE_ID

    st.markdown(_NAV_CSS, unsafe_allow_html=True)

    selected = current

    with st.container(key="medisense-nav"):
        # brand | page cols | logout
        col_ratios = [2.2] + [1.2] * len(pages) + [1.0]
        cols = st.columns(col_ratios)

        # Brand
        with cols[0]:
            st.markdown(
                '<div class="ms-nav-brand">'
                '<div class="ms-nav-dot"></div>MediSense AI'
                '</div>',
                unsafe_allow_html=True,
            )

        # Page buttons — all clickable for everyone
        for i, page_id in enumerate(pages):
            label     = _LABELS.get(page_id, get_page_label(page_id).split(" ", 1)[-1])
            is_active = page_id == current
            with cols[i + 1]:
                if st.button(
                    label,
                    key=f"nav_{page_id}",
                    type="primary" if is_active else "secondary",
                    use_container_width=True,
                ):
                    selected = page_id
                    st.session_state.current_page = selected
                    st.rerun()

        # Exit
        with cols[-1]:
            if st.button("Exit", key="nav_logout",
                         type="secondary", use_container_width=True):
                for key in ("logged_in", "is_admin", "user", "current_page",
                            "ai_engine_label", "ai_engine", "auth_mode",
                            "clinical_state", "prediction_results", "messages"):
                    st.session_state.pop(key, None)
                st.session_state.logged_in = False
                st.session_state.current_page = DEFAULT_PAGE_ID
                st.rerun()

    return selected
