from __future__ import annotations

import importlib
import sys
from pathlib import Path

# pyrefly: ignore [missing-import]
import streamlit as st

ROOT_DIR = str(Path(__file__).parent.parent)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# Configure the page first (Must be the first Streamlit command)
st.set_page_config(
    page_title="MediSense AI - Intelligent Disease Prediction Platform",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.utils.helpers import load_css
from app.utils.session_state import init_session_state
from app.utils.database import init_db
from app.components.navbar import render_navbar
from app.components.footer import render_footer
from app.utils.navigation import DEFAULT_PAGE_ID, PAGE_BY_ID


def _render(module_name: str, function_name: str) -> None:
    module = importlib.import_module(module_name)
    render_func = getattr(module, function_name)
    render_func()


def _render_page(page_id: str) -> None:
    page = PAGE_BY_ID.get(page_id, PAGE_BY_ID[DEFAULT_PAGE_ID])
    _render(page.module, page.function)


def main() -> None:
    init_db()
    init_session_state()

    root_path = Path(__file__).parent.parent
    load_css(str(root_path / "app" / "styles" / "theme.css"))

    # ── Handle iframe button navigation via query params ──────────────────
    lp_action = st.query_params.get("lp_action", "")
    if lp_action in ("register", "login", "admin_login") and not st.session_state.logged_in:
        st.session_state.auth_mode = lp_action
        del st.query_params["lp_action"]
        st.rerun()

    # Inject global full-screen overrides before any page renders
    st.markdown("""
        <style>
            /* Hide sidebar & controls */
            [data-testid="stSidebar"]        { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
            /* Full viewport — remove all inner padding boxes */
            [data-testid="stAppViewContainer"] { padding: 0 !important; }
            [data-testid="stMain"]            { padding: 0 !important; max-width: 100% !important; }
            [data-testid="stMainBlockContainer"] { max-width: 100% !important; padding: 0 !important; }
            section.main > div.block-container { max-width: 100% !important; padding: 0 1.5rem 3rem !important; }
            body, html { overflow-x: hidden !important; }
        </style>
        <script>
        (function() {
            if (document.getElementById('ms-bg-layer')) return;
            var layer = document.createElement('div');
            layer.id = 'ms-bg-layer';
            layer.innerHTML =
                '<div class="blob blob-1"></div>' +
                '<div class="blob blob-2"></div>' +
                '<div class="blob blob-3"></div>' +
                '<div class="blob blob-4"></div>' +
                '<div class="blob blob-5"></div>';
            document.body.prepend(layer);
        })();
        </script>
    """, unsafe_allow_html=True)

    # ── Resolve AI engine display name (never exposes model internals) ────
    try:
        from src.chatbot.chatbot_router import get_active_engine
        _engine = get_active_engine().lower()
        if _engine in ("gemini", "ollama"):
            st.session_state.ai_engine_label = "Advanced AI Consultation"
        else:
            st.session_state.ai_engine_label = "Standard Consultation"
    except Exception:
        st.session_state.ai_engine_label = "Standard Consultation"

    if not st.session_state.logged_in:
        if "auth_mode" not in st.session_state:
            _render("app.pages.landing", "render_landing")
        else:
            _render("app.pages.auth", "render_auth")
    else:
        # ── All logged-in users: navbar drives page selection ─────────────
        page_id = render_navbar()
        _render_page(page_id)
        render_footer()


if __name__ == "__main__":
    main()
