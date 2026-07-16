from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st

from app.utils.navigation import (
    DEFAULT_PAGE_ID,
    get_page_options,
    normalize_page_id,
)
from app.utils.ui import escape_html, render_html


_NAV_ITEMS = [
    ("dashboard",     "🏠", "Dashboard"),
    ("consultation",  "💬", "AI Consultation"),
    ("prediction",    "🩺", "Disease Prediction"),
    ("history",       "📜", "Prediction History"),
    ("comparison",    "📊", "Model Comparison"),
    ("report",        "📄", "Medical Report"),
    ("analytics",     "📈", "Analytics"),
    ("about",         "ℹ️",  "About"),
]

_DEV_ITEMS = [
    ("developer", "👨‍💻", "Developer"),
]


def _sidebar_css() -> None:
    render_html("""
<style>
/* ── Kill default Streamlit sidebar chrome ─────────────────── */
[data-testid="stSidebar"] > div:first-child {
    background: var(--bg-primary) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    padding: 0 !important;
}
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Sidebar inner wrapper ─────────────────────────────────── */
.sb-wrap {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 1.2rem 0.9rem;
    gap: 0;
    font-family: 'Inter', system-ui, sans-serif;
}

/* ── Logo ──────────────────────────────────────────────────── */
.sb-logo {
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.2rem 0.5rem 1.4rem;
    font-size: 1.05rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.03em;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.2rem;
}
.sb-logo-dot {
    width: 9px; height: 9px;
    background: #06B6D4;
    border-radius: 50%;
    box-shadow: 0 0 10px #06B6D4;
    flex-shrink: 0;
    animation: sbGlow 3s ease-in-out infinite;
}
@keyframes sbGlow {
    0%,100% { box-shadow: 0 0 8px #06B6D4; opacity: 0.9; }
    50%      { box-shadow: 0 0 18px #06B6D4, 0 0 30px rgba(6,182,212,0.4); opacity: 1; }
}

/* ── Section label ─────────────────────────────────────────── */
.sb-section-label {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.22);
    padding: 0 0.5rem;
    margin-bottom: 0.45rem;
}

/* ── Nav item button ───────────────────────────────────────── */
.sb-nav-btn {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    width: 100%;
    padding: 0.62rem 0.75rem;
    border-radius: 10px;
    border: none;
    background: transparent;
    cursor: pointer;
    text-align: left;
    font-size: 0.875rem;
    font-weight: 500;
    color: rgba(255,255,255,0.48);
    transition: background 0.18s, color 0.18s;
    margin-bottom: 2px;
    font-family: 'Inter', system-ui, sans-serif;
}
.sb-nav-btn:hover {
    background: rgba(255,255,255,0.05);
    color: rgba(255,255,255,0.82);
}
.sb-nav-btn.active {
    background: rgba(37,99,235,0.14);
    color: #93C5FD;
    font-weight: 600;
    border: 1px solid rgba(37,99,235,0.2);
}
.sb-nav-icon {
    font-size: 1rem;
    flex-shrink: 0;
    width: 20px;
    text-align: center;
}
.sb-nav-label { flex: 1; }

/* ── Profile card ──────────────────────────────────────────── */
.sb-profile {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    padding: 0.75rem;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    margin-top: auto;
    margin-bottom: 0.6rem;
}
.sb-avatar {
    width: 34px; height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563EB, #06B6D4);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 800;
    color: #fff;
    flex-shrink: 0;
}
.sb-profile-name {
    font-size: 0.85rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.2;
}
.sb-profile-role {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.32);
}
</style>
""")


def render_sidebar() -> str:
    """Renders premium custom sidebar. Returns the selected page_id."""
    _sidebar_css()

    with st.sidebar:
        dev_mode = st.query_params.get("dev", "false").lower() == "true"

        # ── current page ──────────────────────────────────────────
        current_page = normalize_page_id(
            st.session_state.get("current_page"), dev_mode
        )
        valid_pages = get_page_options(dev_mode)
        if current_page not in valid_pages:
            current_page = DEFAULT_PAGE_ID
        st.session_state.current_page = current_page

        # ── Logo ──────────────────────────────────────────────────
        render_html("""
<div class="sb-logo">
  <div class="sb-logo-dot"></div>
  MediSense AI
</div>
""")

        # ── Navigation buttons ────────────────────────────────────
        render_html('<div class="sb-section-label">Navigation</div>')

        items = _NAV_ITEMS + (_DEV_ITEMS if dev_mode else [])
        selected = current_page

        for page_id, icon, label in items:
            is_active = page_id == current_page
            active_cls = "active" if is_active else ""
            btn_key = f"sb_nav_{page_id}"

            # Render button via st.markdown + st.button pattern
            if st.button(
                f"{icon}  {label}",
                key=btn_key,
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                selected = page_id
                st.session_state.current_page = page_id
                st.rerun()

        # ── Dev mode toggle ───────────────────────────────────────
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:1rem 0;" />',
            unsafe_allow_html=True,
        )
        if st.checkbox("Dev Mode", value=dev_mode, key="dev_toggle"):
            st.query_params["dev"] = "true"
            if not dev_mode:
                st.rerun()
        else:
            if "dev" in st.query_params:
                del st.query_params["dev"]
                if dev_mode:
                    st.rerun()

        # ── User profile ──────────────────────────────────────────
        st.markdown(
            '<hr style="border:none;border-top:1px solid rgba(255,255,255,0.06);margin:0.5rem 0;" />',
            unsafe_allow_html=True,
        )
        if "user" in st.session_state:
            user = st.session_state.user
            raw_name = str(user.get("name", "User"))
            display_name = escape_html(raw_name)
            initial = escape_html(raw_name[:1].upper() or "U")
            render_html(f"""
<div class="sb-profile">
  <div class="sb-avatar">{initial}</div>
  <div>
    <div class="sb-profile-name">{display_name}</div>
    <div class="sb-profile-role">Clinical Workspace</div>
  </div>
</div>
""")
            if st.button("Logout", key="sidebar_logout_btn", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.current_page = DEFAULT_PAGE_ID
                st.session_state.pop("user", None)
                st.rerun()

    return st.session_state.current_page
