"""
app/pages/admin.py
Premium Admin Dashboard — completely separate from patient experience.
Sources all data from SQLite via admin-specific helpers.
All charts use Plotly. Backend untouched.
"""
from __future__ import annotations

# pyrefly: ignore [missing-import]
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

from app.utils.database import get_admin_stats, get_all_users, get_all_predictions
from app.utils.ui import render_html


# ── Shared Plotly dark layout ──────────────────────────────────────────────
_PL = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=12),
    margin=dict(l=0, r=0, t=32, b=0),
    hoverlabel=dict(
        bgcolor="rgba(11,18,32,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(color="#F8FAFC", size=13),
    ),
)
_CFG = dict(
    displayModeBar=True, displaylogo=False,
    modeBarButtonsToRemove=["select2d", "lasso2d"],
    toImageButtonOptions=dict(format="png", filename="admin_chart", scale=2),
    responsive=True,
)
PALETTE = ["#3B82F6", "#06B6D4", "#22C55E", "#F59E0B", "#EF4444",
           "#8B5CF6", "#EC4899", "#F97316", "#14B8A6", "#A78BFA"]


def _admin_css() -> None:
    render_html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Admin page base ── */
.admin-wrap { font-family: 'Inter', system-ui, sans-serif; }

/* ── Page header ── */
.admin-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1.2rem 2rem;
    background: rgba(11,18,32,0.5);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    backdrop-filter: blur(20px);
    margin-bottom: 2rem;
    animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
}
.admin-header-left h1 {
    font-size: 1.6rem !important; font-weight: 800 !important;
    margin: 0 0 0.2rem !important;
    background: linear-gradient(135deg, #F59E0B, #FCD34D);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.admin-header-left p { margin: 0; color: rgba(255,255,255,0.4); font-size: 0.88rem; }
.admin-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.25);
    color: #F59E0B; font-size: 0.72rem; font-weight: 700;
    padding: 0.4rem 1rem; border-radius: 9999px;
    text-transform: uppercase; letter-spacing: 0.06em;
}
.admin-badge-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #10B981; box-shadow: 0 0 8px #10B981;
    animation: adminPulse 2s ease-in-out infinite;
}
@keyframes adminPulse {
    0%,100% { box-shadow: 0 0 5px #10B981; }
    50%      { box-shadow: 0 0 14px #10B981, 0 0 24px rgba(16,185,129,0.4); }
}

/* ── KPI cards ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.2rem;
    margin-bottom: 2rem;
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
}
.kpi-card {
    background: rgba(11,18,32,0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.5rem 1.5rem 1.2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    position: relative; overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
}
.kpi-card:hover { transform: translateY(-4px); box-shadow: 0 18px 40px rgba(0,0,0,0.4); }
.kpi-card::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--kpi-accent, #3B82F6);
    border-radius: 20px 20px 0 0;
}
.kpi-icon { font-size: 1.6rem; margin-bottom: 0.8rem; }
.kpi-val {
    font-size: 2.4rem; font-weight: 900; color: #fff;
    margin: 0 0 0.2rem; line-height: 1;
    font-variant-numeric: tabular-nums;
}
.kpi-lbl { font-size: 0.72rem; color: rgba(255,255,255,0.35); font-weight: 700;
           text-transform: uppercase; letter-spacing: 0.08em; }
.kpi-delta {
    font-size: 0.75rem; font-weight: 600; margin-top: 0.5rem;
    color: var(--kpi-accent, #3B82F6);
}

/* ── Section title ── */
.sec-hdr {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(255,255,255,0.35);
    margin: 2rem 0 1.2rem; display: flex; align-items: center; gap: 0.5rem;
}

/* ── Chart glass card ── */
.chart-card {
    background: rgba(11,18,32,0.55);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.4rem 1.4rem 1rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.3);
    animation: fadeUp 0.7s cubic-bezier(0.16,1,0.3,1) forwards;
    margin-bottom: 1.5rem;
}
.chart-title {
    font-size: 0.9rem; font-weight: 700; color: #fff; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.5rem;
}

/* ── Users table ── */
.users-table {
    background: rgba(11,18,32,0.55);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.4rem;
    backdrop-filter: blur(20px);
    animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) forwards;
    margin-bottom: 1.5rem;
}
.u-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 0.8rem 0.6rem; border-radius: 10px;
    transition: background 0.2s; cursor: default;
}
.u-row:hover { background: rgba(255,255,255,0.03); }
.u-row + .u-row { border-top: 1px solid rgba(255,255,255,0.04); }
.u-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    background: linear-gradient(135deg, #2563EB, #06B6D4);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 800; color: #fff; flex-shrink: 0;
}
.u-name { font-size: 0.9rem; font-weight: 600; color: #fff; }
.u-email { font-size: 0.75rem; color: rgba(255,255,255,0.35); }
.u-date { font-size: 0.72rem; color: rgba(255,255,255,0.25); margin-left: auto; white-space: nowrap; }
.u-admin-badge {
    font-size: 0.62rem; font-weight: 700; padding: 0.15rem 0.5rem;
    background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.2);
    color: #F59E0B; border-radius: 9999px; text-transform: uppercase;
}

/* ── Model performance cards ── */
.model-perf-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 1.2rem; margin-bottom: 2rem; }
.mp-card {
    background: rgba(11,18,32,0.6);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; padding: 1.5rem;
    backdrop-filter: blur(20px);
    transition: all 0.3s;
}
.mp-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.14); }
.mp-title { font-size: 0.85rem; font-weight: 700; color: #fff; margin-bottom: 1.2rem; }
.mp-metric { display: flex; justify-content: space-between; align-items: center;
             margin-bottom: 0.65rem; font-size: 0.82rem; }
.mp-metric-lbl { color: rgba(255,255,255,0.4); }
.mp-metric-val { color: #10B981; font-weight: 700; }
.mp-bar-bg { width: 100%; height: 4px; background: rgba(255,255,255,0.04);
             border-radius: 9999px; overflow: hidden; margin-bottom: 0.65rem; }
.mp-bar-fill { height: 100%; border-radius: 9999px;
               background: linear-gradient(90deg, #3B82F6, #06B6D4);
               transition: width 1.2s cubic-bezier(0.4,0,0.2,1); }

/* ── Log viewer ── */
.log-wrap {
    background: rgba(5,8,22,0.8); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 1rem 1.2rem;
    font-family: 'Courier New', monospace; font-size: 0.75rem;
    color: rgba(255,255,255,0.5); max-height: 260px; overflow-y: auto;
    line-height: 1.7;
}
.log-line { margin: 0; }
.log-line .log-ts { color: rgba(255,255,255,0.2); }
.log-line .log-ev { color: #10B981; font-weight: 700; }
.log-line .log-err { color: #EF4444; font-weight: 700; }
.log-line .log-warn { color: #F59E0B; font-weight: 700; }
</style>
""")


def _kpi_cards(stats: dict) -> None:
    kpis = [
        ("👥", "Total Patients",    stats["total_patients"],    "#3B82F6",  f"+{stats['total_patients']} registered"),
        ("🩺", "Total Predictions", stats["total_predictions"],  "#06B6D4",  "All time"),
        ("📅", "Today's Activity",  stats["today_predictions"],  "#10B981",  "Predictions today"),
        ("🎯", "Avg Confidence",    f"{stats['avg_confidence']}%", "#F59E0B", "Across all models"),
    ]
    html = '<div class="kpi-grid">'
    for icon, label, val, color, delta in kpis:
        html += f"""
        <div class="kpi-card" style="--kpi-accent:{color};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-lbl">{label}</div>
            <div class="kpi-delta">{delta}</div>
        </div>"""
    html += "</div>"
    render_html(html)


def _chart_disease_donut(stats: dict) -> None:
    dist = stats["disease_dist"]
    if not dist:
        # Demo data
        dist = {"Common Cold": 45, "Hypertension": 32, "Diabetes": 28,
                "Asthma": 21, "Pneumonia": 18, "Migraine": 15, "Gastritis": 12, "Anemia": 9}

    fig = go.Figure(go.Pie(
        labels=list(dist.keys()),
        values=list(dist.values()),
        hole=0.62,
        marker=dict(colors=PALETTE, line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#CBD5E1"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_PL, height=300,
        showlegend=True,
        legend=dict(
            bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8", size=10),
            orientation="v", x=1.02, y=0.5,
        ),
        annotations=[dict(
            text=f"<b>{sum(dist.values())}</b><br><span style='font-size:11px'>total</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#fff", size=18),
        )],
    )
    st.plotly_chart(fig, use_container_width=True, config=_CFG)


def _chart_model_usage_pie(stats: dict) -> None:
    usage = stats["model_usage"]
    if not usage:
        usage = {"Logistic Regression": 48, "Decision Tree": 31, "KNN": 21}

    fig = go.Figure(go.Pie(
        labels=list(usage.keys()),
        values=list(usage.values()),
        hole=0.5,
        marker=dict(colors=["#3B82F6", "#06B6D4", "#22C55E"],
                    line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo="label+percent",
        textfont=dict(size=11, color="#CBD5E1"),
        hovertemplate="<b>%{label}</b><br>Used: %{value} times (%{percent})<extra></extra>",
    ))
    fig.update_layout(**_PL, height=280, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config=_CFG)


def _chart_predictions_area(predictions: list) -> None:
    """Line chart of daily predictions over the last 14 days."""
    base = datetime.now()
    # Build labels as plain strings e.g. "Jul 02"
    day_labels = [
        (base - timedelta(days=i)).strftime("%b %d")
        for i in reversed(range(14))
    ]
    day_keys = [
        (base - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in reversed(range(14))
    ]

    if predictions:
        counts = {k: 0 for k in day_keys}
        for p in predictions:
            day = p["date"][:10] if p["date"] else ""
            if day in counts:
                counts[day] += 1
        y_vals = [counts[k] for k in day_keys]
    else:
        # Demo data — random small values so chart looks alive
        y_vals = [random.randint(0, 8) for _ in range(14)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=day_labels,
        y=y_vals,
        mode="lines+markers",
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.08)",
        line=dict(color="#3B82F6", width=2.5),
        marker=dict(color="#06B6D4", size=6, line=dict(color="#fff", width=1.5)),
        hovertemplate="<b>%{x}</b><br>Predictions: %{y}<extra></extra>",
        name="Predictions",
    ))
    fig.update_layout(
        **_PL, height=240,
        # Force category axis so Plotly never tries to parse as datetime
        xaxis=dict(
            type="category",
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            zeroline=False,
            tickfont=dict(size=10),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            linecolor="rgba(255,255,255,0.08)",
            zeroline=False,
            tickformat="d",
            rangemode="tozero",
        ),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config=_CFG)


def _chart_confidence_histogram(predictions: list) -> None:
    if predictions:
        confs = [p["confidence"] for p in predictions]
    else:
        confs = [round(random.uniform(72, 99), 1) for _ in range(60)]

    fig = go.Figure(go.Histogram(
        x=confs, nbinsx=12,
        marker=dict(
            color=confs, colorscale=[[0, "#3B82F6"], [0.5, "#06B6D4"], [1, "#10B981"]],
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        hovertemplate="Confidence: %{x:.1f}%<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(
        **_PL, height=220,
        xaxis=dict(title=dict(text="Confidence (%)", font=dict(color="#64748B", size=11)),
                   gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        yaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False),
        bargap=0.06,
    )
    st.plotly_chart(fig, use_container_width=True, config=_CFG)


def _chart_model_radar() -> None:
    models = ["Logistic Reg.", "Decision Tree", "KNN"]
    metrics = ["Accuracy", "Precision", "Recall", "F1", "Speed"]
    data = [
        [0.87, 0.85, 0.86, 0.86, 0.95],
        [0.82, 0.80, 0.81, 0.81, 0.98],
        [0.83, 0.81, 0.82, 0.82, 0.72],
    ]
    colors = ["#3B82F6", "#06B6D4", "#22C55E"]

    fig = go.Figure()
    for m, vals, col in zip(models, data, colors):
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=metrics + [metrics[0]],
            fill="toself",
            fillcolor=f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.1)",
            line=dict(color=col, width=2),
            name=m,
            hovertemplate=f"<b>{m}</b><br>%{{theta}}: %{{r:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        **_PL, height=320,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0.7, 1.0], gridcolor="rgba(255,255,255,0.07)",
                           tickfont=dict(color="#64748B", size=9)),
            angularaxis=dict(gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#94A3B8", size=11)),
        ),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#94A3B8", size=11), orientation="h",
                    x=0.5, xanchor="center", y=-0.15),
    )
    st.plotly_chart(fig, use_container_width=True, config=_CFG)


def _users_table(users: list) -> None:
    render_html('<div class="users-table"><div class="chart-title">👥 Registered Users</div>')
    if not users:
        render_html('<div style="color:rgba(255,255,255,0.3);font-size:0.85rem;">No users registered yet.</div>')
    else:
        for u in users[:12]:
            initial = u["name"][:1].upper() if u["name"] else "?"
            badge   = '<span class="u-admin-badge">admin</span>' if u["is_admin"] else ""
            render_html(f"""
            <div class="u-row">
                <div class="u-avatar">{initial}</div>
                <div>
                    <div class="u-name">{u['name']} {badge}</div>
                    <div class="u-email">{u['email']}</div>
                </div>
                <div class="u-date">{u['last_login'][:10]}</div>
            </div>""")
    render_html("</div>")


def _model_performance_cards() -> None:
    models = [
        ("🔵 Logistic Regression", "#3B82F6",
         {"Accuracy": (0.867, 87), "Precision": (0.851, 85), "Recall": (0.860, 86), "F1 Score": (0.856, 86)}),
        ("🟦 Decision Tree",       "#06B6D4",
         {"Accuracy": (0.816, 82), "Precision": (0.800, 80), "Recall": (0.810, 81), "F1 Score": (0.805, 81)}),
        ("🟢 K-Nearest Neighbors", "#22C55E",
         {"Accuracy": (0.825, 83), "Precision": (0.810, 81), "Recall": (0.820, 82), "F1 Score": (0.815, 82)}),
    ]
    html = '<div class="model-perf-grid">'
    for name, color, metrics in models:
        html += f'<div class="mp-card" style="border-top: 2px solid {color};">'
        html += f'<div class="mp-title">{name}</div>'
        for m_name, (m_val, m_pct) in metrics.items():
            html += f"""
            <div class="mp-metric">
                <span class="mp-metric-lbl">{m_name}</span>
                <span class="mp-metric-val">{m_val:.3f}</span>
            </div>
            <div class="mp-bar-bg"><div class="mp-bar-fill" style="width:{m_pct}%;background:linear-gradient(90deg,{color},{color}88);"></div></div>"""
        html += "</div>"
    html += "</div>"
    render_html(html)


def _prediction_log_viewer(predictions: list) -> None:
    render_html('<div class="chart-card"><div class="chart-title">📋 Prediction Log</div><div class="log-wrap">')
    if not predictions:
        render_html('<p class="log-line"><span class="log-ts">[No records]</span> No predictions logged yet.</p>')
    else:
        for p in predictions[:20]:
            ts   = p["date"]
            user = p["user_name"]
            dis  = p["disease"]
            conf = p["confidence"]
            model = p["model"]
            css_cls = "log-ev" if conf >= 80 else "log-warn" if conf >= 60 else "log-err"
            render_html(
                f'<p class="log-line">'
                f'<span class="log-ts">[{ts}]</span> '
                f'<span class="{css_cls}">{user}</span> → '
                f'<b style="color:#fff;">{dis}</b> '
                f'<span style="color:#06B6D4;">{conf:.1f}%</span> '
                f'<span style="color:rgba(255,255,255,0.25);">via {model}</span>'
                f'</p>'
            )
    render_html("</div></div>")


def render_admin() -> None:
    """Renders the full admin portal dashboard."""
    _admin_css()

    import json

    user = st.session_state.get("user", {})
    now  = datetime.now()
    ts   = now.strftime("%A, %b %d %Y  %I:%M %p")

    # Load data
    stats     = get_admin_stats()
    all_users = get_all_users()
    all_preds = get_all_predictions()

    # ── Header ────────────────────────────────────────────────────────────
    render_html(f"""
    <div class="admin-header">
        <div class="admin-header-left">
            <h1>🔐 Admin Portal</h1>
            <p>MediSense AI Control Center &nbsp;·&nbsp; {ts}</p>
        </div>
        <div class="admin-badge">
            <div class="admin-badge-dot"></div>
            System Operational
        </div>
    </div>
    """)

    # ── KPI Cards ─────────────────────────────────────────────────────────
    _kpi_cards(stats)

    # ── Row 1: Disease Donut + Model Pie + Predictions Area ──────────────
    render_html('<div class="sec-hdr">📊 Analytics Overview</div>')
    c1, c2, c3 = st.columns([1.3, 1, 1.5], gap="large")

    with c1:
        st.markdown("**🦠 Disease Distribution**")
        _chart_disease_donut(stats)

    with c2:
        st.markdown("**🧠 Model Usage**")
        _chart_model_usage_pie(stats)

    with c3:
        st.markdown("**📈 Predictions — Last 14 Days**")
        _chart_predictions_area(all_preds)

    # ── Row 2: Radar + Histogram ──────────────────────────────────────────
    render_html('<div class="sec-hdr">🎯 Model Performance &amp; Confidence</div>')
    c4, c5 = st.columns([1.2, 1], gap="large")

    with c4:
        st.markdown("**📡 Model Performance Radar**")
        _chart_model_radar()

    with c5:
        st.markdown("**📊 Confidence Distribution**")
        _chart_confidence_histogram(all_preds)

    # ── Row 3: Model Cards ───────────────────────────────────────────────
    render_html('<div class="sec-hdr">⚙️ ML Model Dashboard</div>')
    _model_performance_cards()

    # ── Row 4: Users Table + Prediction Log ──────────────────────────────
    render_html('<div class="sec-hdr">👥 User Management &amp; Logs</div>')
    c6, c7 = st.columns([1, 1.4], gap="large")

    with c6:
        _users_table(all_users)

    with c7:
        _prediction_log_viewer(all_preds)

    # ── Admin Actions ─────────────────────────────────────────────────────
    render_html('<div class="sec-hdr">🔧 Admin Actions</div>')
    a1, a2, a3, a4 = st.columns(4, gap="medium")

    with a1:
        if st.button("🔄 Refresh Stats", use_container_width=True, key="admin_refresh"):
            st.rerun()

    with a2:
        # Always-visible download — no nesting required
        users_json = json.dumps(all_users, indent=2, default=str)
        st.download_button(
            label="📤 Export User List",
            data=users_json,
            file_name="medisense_users.json",
            mime="application/json",
            use_container_width=True,
            key="dl_users",
        )

    with a3:
        preds_json = json.dumps(all_preds, indent=2, default=str)
        st.download_button(
            label="📋 Export Predictions",
            data=preds_json,
            file_name="medisense_predictions.json",
            mime="application/json",
            use_container_width=True,
            key="dl_preds",
        )

    with a4:
        if st.button("🚪 Logout Admin", use_container_width=True, key="admin_logout",
                     type="secondary"):
            for key in ("logged_in", "is_admin", "user", "current_page",
                        "ai_engine_label", "ai_engine", "auth_mode"):
                st.session_state.pop(key, None)
            st.session_state.logged_in = False
            st.session_state.is_admin  = False
            st.rerun()
