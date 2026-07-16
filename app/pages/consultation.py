# pyrefly: ignore [missing-import]
import streamlit as st
import time

from app.utils.navigation import PREDICTION
from app.utils.ui import escape_html, render_html
from src.prediction.predictor import load_feature_names
from src.chatbot.memory import add_message, init_memory, get_symptoms

# Import Sprint 3 conversation manager
from src.chatbot.conversation_manager import handle_turn
from src.chatbot.conversation_state import ConversationState


def _md_to_html(text: str) -> str:
    """Safe Markdown → HTML for chat bubbles."""
    import re
    html = escape_html(text)
    html = re.sub(r'```(.*?)```', r'<pre class="chat-code"><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.*?)`', r'<code class="chat-inline-code">\1</code>', html)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = html.replace("\n", "<br>")
    return html


def _get_or_create_clinical_state():
    """Get Sprint 3 clinical state from session, create fresh if missing."""
    state = st.session_state.get("clinical_state")
    if state is None:
        state = ConversationState.fresh()
        st.session_state.clinical_state = state
    return state


def _render_clinical_panel(detected_list: list[str]) -> None:
    """Renders the right-side clinical status panel.
    Uses Sprint 3 clinical_state when available for richer data."""
    state = st.session_state.get("clinical_state")

    # ── Derive display values ─────────────────────────────────────────────
    if state is not None:
        confidence  = getattr(state, "clinical_confidence", 0.0)
        phase       = getattr(state, "phase", None)
        phase_name  = phase.value.replace("_", " ").title() if phase else "Gathering Info"
        emergency   = getattr(state, "is_emergency", False)
        severity    = getattr(state, "severity_label", None) or "Unknown"
        duration    = getattr(state, "duration", None) or "Not specified"
        symptoms    = list(getattr(state, "detected_symptoms", [])) or detected_list
        prog_pct    = getattr(state, "progress_pct", 0)
    else:
        confidence  = 0.0
        phase_name  = "Gathering Info"
        emergency   = False
        severity    = "Unknown"
        duration    = "Not specified"
        symptoms    = detected_list
        prog_pct    = min(len(detected_list) * 15, 90)

    ai_engine = st.session_state.get("ai_engine_label", "Standard Consultation")
    conf_pct  = int(confidence * 100) if confidence <= 1.0 else int(confidence)

    # ── Colors ────────────────────────────────────────────────────────────
    if emergency:
        status_color = "#EF4444"
        status_label = "⚠️ Emergency"
    elif conf_pct >= 65:
        status_color = "#10B981"
        status_label = "Good Picture"
    elif conf_pct >= 40:
        status_color = "#F59E0B"
        status_label = "Building Data"
    else:
        status_color = "#3B82F6"
        status_label = "Collecting"

    # ── Symptom chips ─────────────────────────────────────────────────────
    chips_html = ""
    if symptoms:
        for s in symptoms[:8]:
            chips_html += f"<div class='sym-chip'>{escape_html(s)}</div>"
    else:
        chips_html = "<div class='no-symptoms-msg'>Awaiting symptom detection...</div>"

    render_html(f"""
    <div class="clinical-panel">
        <div class="cp-header">
            <span class="cp-title">🩺 Clinical Status</span>
            <div class="cp-status" style="color:{status_color};border-color:{status_color}40;background:{status_color}10;">
                <div class="cp-dot" style="background:{status_color};box-shadow:0 0 8px {status_color};"></div>
                {status_label}
            </div>
        </div>

        <!-- Stage -->
        <div class="cp-section">
            <div class="cp-label">Current Stage</div>
            <div style="font-size:0.9rem;font-weight:700;color:#fff;">{phase_name}</div>
        </div>

        <!-- Consultation Progress -->
        <div class="cp-section">
            <div class="cp-label" style="display:flex;justify-content:space-between;">
                <span>Consultation Progress</span>
                <span style="color:#06B6D4;font-weight:700;">{prog_pct}%</span>
            </div>
            <div class="cp-progress-bg">
                <div class="cp-progress-fill" style="width:{prog_pct}%;background:#3B82F6;box-shadow:0 0 8px rgba(59,130,246,0.5);"></div>
            </div>
        </div>

        <!-- Clinical Confidence -->
        <div class="cp-section">
            <div class="cp-label" style="display:flex;justify-content:space-between;">
                <span>Clinical Confidence</span>
                <span style="color:{status_color};font-weight:700;">{conf_pct}%</span>
            </div>
            <div class="cp-progress-bg">
                <div class="cp-progress-fill" style="width:{conf_pct}%;background:{status_color};box-shadow:0 0 8px {status_color}88;"></div>
            </div>
        </div>

        <!-- Detected Symptoms -->
        <div class="cp-section">
            <div class="cp-label" style="display:flex;justify-content:space-between;">
                <span>Detected Symptoms</span>
                <span class="symptom-count-badge">{len(symptoms)}</span>
            </div>
            <div class="cp-chips-container">{chips_html}</div>
        </div>

        <!-- Clinical Details -->
        <div class="cp-section" style="border-bottom:none;">
            <div class="cp-profile-grid">
                <div class="cp-stat">
                    <span>DURATION</span>
                    <strong style="font-size:0.75rem;">{escape_html(duration)}</strong>
                </div>
                <div class="cp-stat">
                    <span>SEVERITY</span>
                    <strong style="font-size:0.75rem;">{escape_html(severity)}</strong>
                </div>
            </div>
        </div>

        {'<div class="cp-emergency">⚠️ Emergency detected! Please seek immediate medical attention.</div>' if emergency else ''}
    </div>
    """)


def _process_user_input(prompt: str) -> str:
    """Route through Sprint 3 manager. Returns assistant reply (always str)."""
    state = _get_or_create_clinical_state()
    try:
        result = handle_turn(prompt, state, stream=False)
        # Update session state
        st.session_state.clinical_state = result.state
        # Sync detected symptoms → patient_data for prediction page
        detected = list(getattr(result.state, "detected_symptoms", []))
        if detected:
            st.session_state.patient_data["detected_symptoms"] = detected
        reply = result.reply
        # Materialise generator if stream=False still gave one
        if not isinstance(reply, str):
            reply = "".join(reply)
        return reply
    except Exception as exc:
        return f"I encountered an issue processing your input. Please try again. ({exc})"


def render_consultation() -> None:
    """Render the AI Consultation page — premium ChatGPT-style UI with Sprint 3 integration."""
    init_memory()
    _get_or_create_clinical_state()

    user         = st.session_state.get("user", {"name": "Guest"})
    display_name = escape_html(user.get("name", "Guest").split(" ")[0])
    ai_engine    = st.session_state.get("ai_engine_label", "Clinical Assistant")

    all_symptoms = load_feature_names()
    if not all_symptoms:
        st.warning("Symptom feature data could not be loaded.")

    # ── STYLES ────────────────────────────────────────────────────────────
    render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Background animation ── */
@keyframes consultBlob1 {
    0%,100% { transform:translate(0,0) scale(1); }
    33% { transform:translate(35px,-25px) scale(1.07); }
    66% { transform:translate(-18px,18px) scale(0.94); }
}
@keyframes consultBlob2 {
    0%,100% { transform:translate(0,0) scale(1); }
    40% { transform:translate(-45px,28px) scale(1.09); }
    70% { transform:translate(28px,-18px) scale(0.91); }
}
@keyframes consultBlob3 {
    0%,100% { transform:translate(-50%,-50%) scale(1); }
    50% { transform:translate(-50%,-50%) scale(1.12); }
}
@keyframes consultParticle {
    0% { transform:translateY(110vh) rotate(0deg); opacity:0; }
    8% { opacity:1; } 92% { opacity:0.5; }
    100% { transform:translateY(-80px) rotate(720deg); opacity:0; }
}
@keyframes consultScanline { 0% { top:-4px; } 100% { top:100%; } }
@keyframes consultGridFade { 0%,100% { opacity:0.03; } 50% { opacity:0.07; } }
@keyframes consultGlowPulse { 0%,100% { opacity:0.35; transform:scale(1); } 50% { opacity:0.75; transform:scale(1.12); } }
@keyframes consultAIPulse {
    0%,100% { box-shadow:0 0 20px rgba(6,182,212,0.3),0 0 40px rgba(6,182,212,0.1); transform:scale(1); }
    50% { box-shadow:0 0 35px rgba(6,182,212,0.6),0 0 70px rgba(6,182,212,0.25); transform:scale(1.03); }
}
@keyframes consultRingPulse {
    0% { transform:scale(1); opacity:0.6; } 100% { transform:scale(2.2); opacity:0; }
}
@keyframes typingDot {
    0%,60%,100% { transform:translateY(0); opacity:0.4; }
    30% { transform:translateY(-6px); opacity:1; }
}

.consult-blob { position:fixed; border-radius:50%; filter:blur(85px); pointer-events:none; z-index:0; }
.consult-blob-1 { width:580px;height:580px;top:-140px;left:-100px; background:radial-gradient(circle,rgba(37,99,235,0.28) 0%,transparent 70%); animation:consultBlob1 13s ease-in-out infinite; }
.consult-blob-2 { width:460px;height:460px;bottom:-60px;right:-70px; background:radial-gradient(circle,rgba(6,182,212,0.22) 0%,transparent 70%); animation:consultBlob2 17s ease-in-out infinite; }
.consult-blob-3 { width:360px;height:360px;top:45%;left:50%; background:radial-gradient(circle,rgba(16,185,129,0.08) 0%,transparent 70%); animation:consultBlob3 20s ease-in-out infinite; }
.consult-grid { position:fixed;inset:0;pointer-events:none;z-index:0; background-image:linear-gradient(rgba(255,255,255,0.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.035) 1px,transparent 1px); background-size:56px 56px; animation:consultGridFade 8s ease-in-out infinite; }
.consult-glow { position:fixed;border-radius:50%;pointer-events:none;z-index:0; }
.consult-glow-1 { width:280px;height:280px;top:22%;left:8%; background:radial-gradient(circle,rgba(37,99,235,0.14) 0%,transparent 70%); animation:consultGlowPulse 6s ease-in-out infinite; }
.consult-glow-2 { width:220px;height:220px;bottom:30%;right:10%; background:radial-gradient(circle,rgba(6,182,212,0.12) 0%,transparent 70%); animation:consultGlowPulse 8s ease-in-out infinite 2s; }
.consult-particles { position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden; }
.consult-p { position:absolute;bottom:-10px;width:3px;height:3px;border-radius:50%;background:var(--cp-col,rgba(37,99,235,0.7)); animation:consultParticle var(--cp-dur,13s) linear infinite; animation-delay:var(--cp-delay,0s); left:var(--cp-x,50%); }
.consult-scanline { position:fixed;left:0;width:100%;height:2px; background:linear-gradient(90deg,transparent,rgba(6,182,212,0.1),transparent); animation:consultScanline 10s linear infinite; z-index:0; pointer-events:none; }
.consult-dna { position:fixed;font-size:1.3rem;opacity:0.1;pointer-events:none;z-index:0; animation:consultDnaFloat var(--cd-dur,10s) ease-in-out infinite; top:var(--cd-top,30%);left:var(--cd-left,80%); animation-delay:var(--cd-delay,0s); }
@keyframes consultDnaFloat { 0%,100%{transform:translateY(0) rotate(0deg);opacity:0.1;} 50%{transform:translateY(-20px) rotate(180deg);opacity:0.18;} }
.consult-content { position:relative; z-index:5; }

/* ── Segmented Control ── */
.seg-wrapper {
    background: rgba(11, 18, 32, 0.45);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 0.35rem;
    display: flex;
    gap: 0.35rem;
    margin-top: 1rem;
    margin-bottom: 0.4rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: inset 0 1px 1px rgba(255,255,255,0.03), 0 4px 12px rgba(0,0,0,0.1);
}
.seg-wrapper > div { flex: 1; }
.seg-wrapper button {
    border-radius: 6px !important;
    transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
}

/* ── Hero ── */
.chat-hero { margin-bottom:0.5rem; animation:fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards; }
.chat-hero h1 { font-size:1.8rem!important;font-weight:800!important;margin:0 0 0.35rem 0!important; background:linear-gradient(135deg,#fff 0%,rgba(255,255,255,0.72) 100%); -webkit-background-clip:text;-webkit-text-fill-color:transparent; }
.chat-hero p { color:rgba(255,255,255,0.42);font-size:0.9rem;margin:0; }

/* ── AI Pulse ── */
.ai-pulse-ring { position:relative;width:52px;height:52px;display:inline-flex;align-items:center;justify-content:center;flex-shrink:0; }
.ai-pulse-core { width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,#3B82F6,#06B6D4);display:flex;align-items:center;justify-content:center;font-size:1.2rem;position:relative;z-index:2;animation:consultAIPulse 3s ease-in-out infinite; }
.ai-pulse-ring::before,.ai-pulse-ring::after { content:'';position:absolute;border-radius:16px;border:2px solid rgba(6,182,212,0.4);inset:-4px;animation:consultRingPulse 2.5s ease-out infinite; }
.ai-pulse-ring::after { animation-delay:1.25s; }

/* ── Chat messages ── */
[data-testid="stChatMessage"] { border-radius:16px!important; }
[data-testid="stChatMessage"][data-testid*="user"] { background:rgba(37,99,235,0.08)!important; border:1px solid rgba(37,99,235,0.15)!important; }
[data-testid="stChatMessage"][data-testid*="assistant"] { background:rgba(11,18,32,0.4)!important; border:1px solid rgba(255,255,255,0.05)!important; }

/* ── Chat Input Override ── */
div[data-testid="stChatInput"] {
    border:1px solid rgba(255,255,255,0.08)!important; border-radius:14px!important;
    background:rgba(11,18,32,0.6)!important; box-shadow:0 8px 24px rgba(0,0,0,0.3)!important;
    transition:all 0.3s!important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color:rgba(59,130,246,0.6)!important;
    box-shadow:0 0 0 3px rgba(59,130,246,0.12),0 8px 24px rgba(0,0,0,0.3)!important;
}
div[data-testid="stChatInput"] textarea { color:#fff!important; font-family:'Inter',system-ui,sans-serif!important; }

/* ── Suggestion chips ── */
.chips-section { padding:0;border-top:1px solid rgba(255,255,255,0.04);margin-top:0.5rem; }
.chips-section [data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
    background:rgba(255,255,255,0.02)!important; border:1px solid rgba(255,255,255,0.07)!important;
    border-radius:9999px!important; padding:0.42rem 0.9rem!important;
    color:rgba(255,255,255,0.6)!important; font-size:0.82rem!important; transition:all 0.2s!important;
}
.chips-section [data-testid="stHorizontalBlock"] [data-testid="stButton"] button:hover {
    background:rgba(6,182,212,0.08)!important; color:#06B6D4!important;
    border-color:rgba(6,182,212,0.3)!important; transform:translateY(-2px)!important;
}

/* ── Clinical Panel ── */
.clinical-panel {
    background:rgba(11,18,32,0.65); border:1px solid rgba(255,255,255,0.07);
    border-radius:24px; padding:1.4rem;
    backdrop-filter:blur(24px);
    box-shadow:0 20px 40px rgba(0,0,0,0.4),0 0 0 1px rgba(6,182,212,0.05);
    animation:fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) forwards;
    position:sticky; top:70px;
}
.cp-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:1.25rem; }
.cp-title { font-size:0.95rem;font-weight:700;color:#fff; }
.cp-status { display:flex;align-items:center;gap:0.4rem;padding:0.25rem 0.7rem;border-radius:9999px; font-size:0.68rem;font-weight:700;text-transform:uppercase;border:1px solid; }
.cp-dot { width:6px;height:6px;border-radius:50%;animation:consultGlowPulse 2s infinite; }
.cp-section { padding:0.85rem 0;border-bottom:1px solid rgba(255,255,255,0.04); }
.cp-label { font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em; color:rgba(255,255,255,0.3);font-weight:700;margin-bottom:0.7rem; }
.cp-ai-badge { display:inline-flex;align-items:center;gap:5px;background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.18);color:#06B6D4;font-size:0.8rem;font-weight:600;padding:0.3rem 0.75rem;border-radius:9999px; }
.cp-profile-grid { display:grid;grid-template-columns:repeat(2,1fr);gap:0.4rem; }
.cp-stat { background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.04);border-radius:10px;padding:0.65rem;text-align:center; }
.cp-stat span { display:block;font-size:0.58rem;color:rgba(255,255,255,0.3);margin-bottom:0.15rem;text-transform:uppercase;letter-spacing:0.06em; }
.cp-stat strong { font-size:0.8rem;color:#fff; }
.cp-chips-container { display:flex;flex-wrap:wrap;gap:0.35rem; }
.sym-chip { background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.18);color:#06B6D4;padding:0.28rem 0.6rem;border-radius:7px;font-size:0.78rem;font-weight:500;transition:all 0.2s; }
.sym-chip:hover { background:rgba(6,182,212,0.18);transform:translateY(-1px); }
.no-symptoms-msg { font-size:0.8rem;color:rgba(255,255,255,0.3);font-style:italic; }
.symptom-count-badge { color:#06B6D4;font-weight:700; }
.cp-progress-bg { width:100%;height:5px;background:rgba(255,255,255,0.04);border-radius:9999px;overflow:hidden;margin-top:0.4rem; }
.cp-progress-fill { height:100%;border-radius:9999px;transition:width 1s cubic-bezier(0.4,0,0.2,1); }
.cp-emergency { margin-top:0.8rem;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-radius:10px;padding:0.7rem 0.9rem;color:#EF4444;font-size:0.82rem;font-weight:600; }

/* ── Route button ── */
.route-btn-container [data-testid="stButton"] button {
    background:linear-gradient(135deg,#10B981,#059669)!important; border:none!important;
    box-shadow:0 6px 18px rgba(16,185,129,0.3)!important; color:#fff!important;
    font-weight:700!important; border-radius:12px!important; padding:0.75rem!important;
    margin-top:0.75rem!important; transition:all 0.3s!important;
}
.route-btn-container [data-testid="stButton"] button:hover {
    transform:translateY(-2px)!important; box-shadow:0 10px 24px rgba(16,185,129,0.42)!important;
}

/* ── Code in chat ── */
.chat-code { background:rgba(0,0,0,0.4)!important;padding:0.5rem 0.8rem;border-radius:8px;font-family:monospace;font-size:0.82rem;color:#06B6D4; }
.chat-inline-code { background:rgba(0,0,0,0.3)!important;padding:0.12rem 0.28rem;border-radius:4px;font-family:monospace; }

/* ── Suggested prompts label ── */
.suggested-title { font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(255,255,255,0.3);margin-bottom:0.5rem;font-weight:700;padding:0.8rem 0 0; }
</style>

<!-- 3D Background -->
<div class="consult-blob consult-blob-1"></div>
<div class="consult-blob consult-blob-2"></div>
<div class="consult-blob consult-blob-3"></div>
<div class="consult-grid"></div>
<div class="consult-glow consult-glow-1"></div>
<div class="consult-glow consult-glow-2"></div>
<div class="consult-particles">
    <div class="consult-p" style="--cp-x:7%;  --cp-dur:15s;--cp-delay:0s; --cp-col:rgba(37,99,235,0.7);"></div>
    <div class="consult-p" style="--cp-x:19%; --cp-dur:19s;--cp-delay:2s; --cp-col:rgba(6,182,212,0.65);"></div>
    <div class="consult-p" style="--cp-x:33%; --cp-dur:12s;--cp-delay:4s; --cp-col:rgba(37,99,235,0.55);"></div>
    <div class="consult-p" style="--cp-x:48%; --cp-dur:22s;--cp-delay:1s; --cp-col:rgba(16,185,129,0.65);"></div>
    <div class="consult-p" style="--cp-x:62%; --cp-dur:16s;--cp-delay:6s; --cp-col:rgba(37,99,235,0.8);"></div>
    <div class="consult-p" style="--cp-x:75%; --cp-dur:11s;--cp-delay:3s; --cp-col:rgba(6,182,212,0.75);"></div>
    <div class="consult-p" style="--cp-x:88%; --cp-dur:20s;--cp-delay:5s; --cp-col:rgba(16,185,129,0.55);"></div>
</div>
<div class="consult-dna" style="--cd-top:12%;--cd-left:3%;  --cd-dur:11s;--cd-delay:0s;">🧬</div>
<div class="consult-dna" style="--cd-top:65%;--cd-left:92%;--cd-dur:14s;--cd-delay:3s;">🫀</div>
<div class="consult-dna" style="--cd-top:82%;--cd-left:5%;  --cd-dur:9s; --cd-delay:5s;">🧬</div>
<div class="consult-scanline"></div>
""")

    # ── HERO ──────────────────────────────────────────────────────────────
    render_html(f"""
    <div class="chat-hero consult-content">
        <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.4rem;">
            <div class="ai-pulse-ring"><div class="ai-pulse-core">🩺</div></div>
            <div>
                <h1>AI Clinical Consultation</h1>
                <p>Describe your symptoms naturally</p>
            </div>
        </div>
    </div>
    """)

    # ── ENGINE SELECTOR ───────────────────────────────────────────────────
    if "engine_gemini_ok" not in st.session_state:
        from src.chatbot import gemini_engine
        st.session_state.engine_gemini_ok = gemini_engine.is_available()
    if "engine_ollama_ok" not in st.session_state:
        from src.chatbot import ollama_engine
        st.session_state.engine_ollama_ok = ollama_engine.is_available()
        
    gemini_ok = st.session_state.engine_gemini_ok
    ollama_ok = st.session_state.engine_ollama_ok
    current_eng = st.session_state.get("ai_engine", "basic")

    render_html('<div class="seg-wrapper consult-content">')
    seg_cols = st.columns(3)
    
    gem_label = "✨ Cloud AI"
    if current_eng == "gemini":
        active_model = st.session_state.get("ai_model", "")
        if active_model:
            gem_label = f"✨ Cloud AI\nModel: {active_model}"

    with seg_cols[0]:
        if st.button(gem_label, key="seg_gem", disabled=not gemini_ok, type="primary" if current_eng == "gemini" else "secondary", use_container_width=True, help="Cloud configuration missing" if not gemini_ok else ""):
            st.session_state.ai_engine = "gemini"
            st.session_state.ai_engine_label = "Cloud AI Consultation"
            st.rerun()
    with seg_cols[1]:
        if st.button("🦙 Local AI", key="seg_oll", disabled=not ollama_ok, type="primary" if current_eng == "ollama" else "secondary", use_container_width=True, help="Local AI server unreachable" if not ollama_ok else ""):
            st.session_state.ai_engine = "ollama"
            st.session_state.ai_engine_label = "Local AI Consultation"
            st.rerun()
    with seg_cols[2]:
        if st.button("⚙️ Clinical Assistant", key="seg_bas", type="primary" if current_eng == "basic" else "secondary", use_container_width=True):
            st.session_state.ai_engine = "basic"
            st.session_state.ai_engine_label = "Clinical Assistant"
            st.rerun()
    render_html('</div>')

    # ── LAYOUT ────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2.3, 1], gap="large")

    with col1:
        # Chat history container
        chat_box = st.container(height=500)
        with chat_box:
            msgs = st.session_state.get("messages", [])
            if not msgs:
                st.info(f"How are you feeling today, {display_name}? "
                        "Tell me about any pain, tightness, fever, or other sensations.")
            else:
                for msg in msgs:
                    avatar = "👤" if msg["role"] == "user" else "🤖"
                    with st.chat_message(msg["role"], avatar=avatar):
                        st.markdown(msg["content"])

        # Suggestion chips
        render_html('<div class="chips-section"><div class="suggested-title">💡 Suggested Prompts</div></div>')
        chips_cols = st.columns([1, 1, 1])
        prompt = None
        with chips_cols[0]:
            if st.button("Chest feels tight", use_container_width=True, key="chip1"):
                prompt = "My chest feels tight and heavy, and I feel nauseous."
        with chips_cols[1]:
            if st.button("Throbbing headache", use_container_width=True, key="chip2"):
                prompt = "I have a throbbing headache, stiff neck, and a light fever."
        with chips_cols[2]:
            if st.button("Stomach pain & vomiting", use_container_width=True, key="chip3"):
                prompt = "I've had severe stomach pain, acid reflux, and vomiting since yesterday."

        # Chat input
        user_input = st.chat_input("Describe how you are feeling...")
        if user_input:
            prompt = user_input

        # Route to prediction button
        current_symptoms = get_symptoms()
        if len(current_symptoms) >= 1:
            render_html('<div class="route-btn-container">')
            if st.button("🔬 Run Diagnostic Prediction →",
                         key="consult_goto_predict", use_container_width=True):
                st.success("Clinical profile saved! Routing to Predictor...")
                time.sleep(0.8)
                st.session_state.current_page = PREDICTION
                st.rerun()
            render_html('</div>')

        # Handle prompt
        if prompt:
            add_message("user", prompt)
            with chat_box:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner(""):
                        reply = _process_user_input(prompt)
                    st.markdown(reply)
                    add_message("assistant", reply)
            st.rerun()

    with col2:
        _render_clinical_panel(get_symptoms())
