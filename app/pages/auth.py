# pyrefly: ignore [missing-import]
import streamlit as st
import time

from app.utils.database import get_user_predictions, login_user, register_user
from app.utils.navigation import DEFAULT_PAGE_ID, ADMIN
from app.utils.ui import render_html


def _normalize_auth_mode() -> str:
    mode = st.session_state.get("auth_mode", "login")
    return mode if mode in {"login", "register", "admin_login"} else "login"


_AUTH_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* Auth page global */
.auth-page { font-family: 'Inter', system-ui, sans-serif; }

/* Premium Authentication Layout applied to Streamlit Column */
[data-testid="stColumn"]:nth-child(2) > div {
    background: rgba(11, 18, 32, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 24px !important;
    padding: 3rem 2.5rem !important;
    backdrop-filter: blur(20px) !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
}

.auth-header { text-align: center; margin-bottom: 2rem; }
.auth-header h1 {
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin-bottom: 0.5rem !important;
    background: linear-gradient(135deg, #fff, rgba(255,255,255,0.7));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.auth-header p { color: rgba(255,255,255,0.5) !important; font-size: 0.95rem !important; margin: 0 !important; }

/* Admin header — gold gradient */
.auth-header-admin h1 {
    background: linear-gradient(135deg, #F59E0B, #FCD34D) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}
.auth-admin-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.2);
    color: #F59E0B;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.3rem 0.85rem;
    border-radius: 9999px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

/* Input Styling Override */
div[data-baseweb="input"] {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    transition: all 0.2s !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    background: rgba(255, 255, 255, 0.08) !important;
}
div[data-baseweb="input"] input { color: #fff !important; }

/* Submit Button */
.auth-page .stButton > button,
[data-testid="stColumn"]:nth-child(2) > div .stButton > button {
    background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1rem !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: 1rem !important;
    transition: all 0.2s !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.4) !important;
}

/* Admin submit button — gold */
.admin-submit .stButton > button {
    background: linear-gradient(135deg, #D97706, #B45309) !important;
    box-shadow: 0 4px 15px rgba(217, 119, 6, 0.35) !important;
}
.admin-submit .stButton > button:hover {
    box-shadow: 0 8px 20px rgba(217, 119, 6, 0.5) !important;
}

/* Switch Mode Link */
.mode-switch { text-align: center; margin-top: 1.5rem; }
.mode-switch p { color: rgba(255,255,255,0.5) !important; font-size: 0.9rem !important; margin: 0 !important; }
.mode-switch button {
    background: none !important; border: none !important;
    color: #3B82F6 !important; font-weight: 600 !important;
    box-shadow: none !important; padding: 0 !important;
    margin: 0 !important; width: auto !important;
    display: inline !important;
}
.mode-switch button:hover {
    text-decoration: underline !important;
    transform: none !important;
    box-shadow: none !important;
    background: none !important;
}

.auth-divider {
    display: flex; align-items: center; gap: 0.8rem;
    margin: 1.5rem 0;
}
.auth-divider-line { flex: 1; height: 1px; background: rgba(255,255,255,0.07); }
.auth-divider-text { font-size: 0.75rem; color: rgba(255,255,255,0.2); font-weight: 500; }
</style>
"""


def render_auth() -> None:
    """Renders the Login, Registration, and Admin Login screens."""
    mode = _normalize_auth_mode()

    render_html(_AUTH_CSS)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:

        # ── ADMIN LOGIN ───────────────────────────────────────────────────
        if mode == "admin_login":
            render_html("""
            <div class="auth-header auth-header-admin">
                <div class="auth-admin-badge">🔐 Restricted — Admin Only</div>
                <h1>Admin Portal</h1>
                <p>Secure administrative access to MediSense AI.</p>
            </div>
            """)

            email    = st.text_input("Admin Email", key="admin_email")
            password = st.text_input("Admin Password", type="password", key="admin_password")

            render_html('<div class="admin-submit">')
            if st.button("🔐 Sign In as Administrator", key="admin_signin_btn"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    success, result = login_user(email, password)
                    if success and result.get("is_admin"):
                        st.session_state.logged_in   = True
                        st.session_state.is_admin    = True
                        st.session_state.user        = result
                        st.session_state.current_page = ADMIN
                        st.session_state.pop("auth_mode", None)
                        st.success(f"Welcome, Administrator {result['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    elif success and not result.get("is_admin"):
                        st.error("⚠️ This account does not have administrator privileges.")
                    else:
                        st.error("Invalid admin credentials.")
            render_html('</div>')

            render_html('<div class="auth-divider"><div class="auth-divider-line"></div>'
                        '<div class="auth-divider-text">OR</div>'
                        '<div class="auth-divider-line"></div></div>')

            render_html('<div class="mode-switch"><p>Not an admin?</p></div>')
            if st.button("Patient Login instead", key="goto_patient_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

        # ── PATIENT LOGIN ─────────────────────────────────────────────────
        elif mode == "login":
            render_html("""
            <div class="auth-header">
                <h1>Welcome Back</h1>
                <p>Sign in to your secure clinical workspace.</p>
            </div>
            """)

            email    = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Sign In", key="patient_signin_btn"):
                if not email or not password:
                    st.error("Please fill in all fields")
                else:
                    success, result = login_user(email, password)
                    if success:
                        st.session_state.logged_in    = True
                        st.session_state.is_admin     = result.get("is_admin", False)
                        st.session_state.user         = result
                        st.session_state.current_page = DEFAULT_PAGE_ID
                        st.session_state.prediction_history = get_user_predictions(result["id"])
                        st.session_state.pop("auth_mode", None)
                        st.success(f"Welcome back, {result['name']}!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(result)

            render_html('<div class="mode-switch"><p>Don\'t have an account?</p></div>')
            if st.button("Create one now", key="goto_register"):
                st.session_state.auth_mode = "register"
                st.rerun()

            render_html('<div class="auth-divider"><div class="auth-divider-line"></div>'
                        '<div class="auth-divider-text">OR</div>'
                        '<div class="auth-divider-line"></div></div>')
            if st.button("🔐 Admin Login", key="goto_admin_login"):
                st.session_state.auth_mode = "admin_login"
                st.rerun()

        # ── REGISTER ─────────────────────────────────────────────────────
        else:
            render_html("""
            <div class="auth-header">
                <h1>Create Account</h1>
                <p>Join the next generation AI healthcare platform.</p>
            </div>
            """)

            reg_name     = st.text_input("Full Name", key="reg_name")
            reg_email    = st.text_input("Email Address", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_confirm  = st.text_input("Confirm Password", type="password", key="reg_confirm")

            if st.button("Create Account", key="register_btn"):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all fields")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match")
                else:
                    success, result = register_user(reg_name, reg_email, reg_password)
                    if success:
                        st.success("Account created successfully! Please log in.")
                        time.sleep(1)
                        st.session_state.auth_mode = "login"
                        st.rerun()
                    else:
                        st.error(result)

            render_html('<div class="mode-switch"><p>Already have an account?</p></div>')
            if st.button("Sign in instead", key="goto_login"):
                st.session_state.auth_mode = "login"
                st.rerun()
