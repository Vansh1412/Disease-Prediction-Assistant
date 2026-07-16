# pyrefly: ignore [missing-import]
import streamlit as st
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta

from app.utils.ui import (
    PageLayout, MetricCard, EmptyState, SectionDivider, render_html
)


# ── Shared Plotly dark layout template ──────────────────────────────────────

# Base layout — does NOT include xaxis/yaxis/legend so they can be added per-chart
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=12),
    margin=dict(l=0, r=0, t=36, b=0),
    hoverlabel=dict(
        bgcolor="rgba(11,18,32,0.95)",
        bordercolor="rgba(255,255,255,0.12)",
        font=dict(color="#F8FAFC", size=13),
    ),
)

# Reusable axis/legend sub-dicts (referenced directly, never spread into PLOTLY_LAYOUT)
_XAXIS = dict(
    gridcolor="rgba(255,255,255,0.05)",
    linecolor="rgba(255,255,255,0.1)",
    zeroline=False,
)
_YAXIS = dict(
    gridcolor="rgba(255,255,255,0.05)",
    linecolor="rgba(255,255,255,0.1)",
    zeroline=False,
)
_LEGEND = dict(
    bgcolor="rgba(11,18,32,0.8)",
    bordercolor="rgba(255,255,255,0.08)",
    borderwidth=1,
    font=dict(color="#94A3B8"),
)

PLOTLY_CONFIG = dict(
    displayModeBar=True,
    displaylogo=False,
    modeBarButtonsToRemove=["select2d", "lasso2d", "autoScale2d"],
    toImageButtonOptions=dict(format="png", filename="medisense_chart", scale=2),
    responsive=True,
)

PRIMARY   = "#3B82F6"
ACCENT    = "#06B6D4"
SUCCESS   = "#22C55E"
WARNING   = "#F59E0B"
DANGER    = "#EF4444"
PURPLE    = "#8B5CF6"

PALETTE   = [PRIMARY, ACCENT, SUCCESS, WARNING, DANGER, PURPLE,
             "#EC4899", "#F97316", "#14B8A6", "#A78BFA"]


def _demo_history(n: int = 12) -> list[dict]:
    """Generate a plausible historical baseline when the session has no real data."""
    diseases = [
        "Common Cold", "Hypertension", "Diabetes", "Asthma",
        "Migraine", "Gastritis", "Anemia", "Pneumonia",
    ]
    models = ["Logistic Regression", "Decision Tree", "KNN"]
    base = datetime.now() - timedelta(days=n - 1)
    return [
        {
            "disease":    random.choice(diseases),
            "confidence": round(random.uniform(72, 99), 1),
            "model":      random.choice(models),
            "date":       (base + timedelta(days=i)).strftime("%Y-%m-%d %H:%M"),
        }
        for i in range(n)
    ]


# ── Individual chart builders ────────────────────────────────────────────────

def _chart_model_donut(model_usage: dict) -> go.Figure:
    """Animated donut for model usage split."""
    labels = list(model_usage.keys())
    values = list(model_usage.values())
    total  = sum(values) or 1

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=[PRIMARY, ACCENT, SUCCESS],
                    line=dict(color="rgba(0,0,0,0)", width=0)),
        textinfo="percent",
        textfont=dict(color="#F8FAFC", size=13),
        hovertemplate="<b>%{label}</b><br>%{value} runs · %{percent}<extra></extra>",
        pull=[0.04, 0, 0],
    ))

    fig.add_annotation(
        text=f"<b>{total}</b><br><span style='font-size:10px'>runs</span>",
        font=dict(size=22, color="#F8FAFC", family="Inter"),
        showarrow=False,
        x=0.5, y=0.5,
    )

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        title=dict(text="Model Usage Distribution", font=dict(color="#F8FAFC", size=14)),
        showlegend=True,
        legend=dict(**_LEGEND, orientation="h", x=0.5, xanchor="center", y=-0.05),
        height=320,
    )
    return fig


def _chart_symptom_bar(symptoms: dict) -> go.Figure:
    """Horizontal bar for top detected symptoms."""
    if not symptoms:
        return None
    items  = sorted(symptoms.items(), key=lambda x: x[1], reverse=True)[:8]
    labels = [i[0].replace("_", " ").title() for i in items]
    values = [i[1] for i in items]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=values,
            colorscale=[[0, "#1D4ED8"], [0.5, ACCENT], [1, SUCCESS]],
            showscale=False,
            line=dict(width=0),
        ),
        text=[str(v) for v in values],
        textposition="outside",
        textfont=dict(color="#94A3B8", size=11),
        hovertemplate="<b>%{y}</b><br>Occurrences: %{x}<extra></extra>",
    ))

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        title=dict(text="Top Detected Symptoms", font=dict(color="#F8FAFC", size=14)),
        height=320,
        xaxis=dict(**_XAXIS, title=None),
        yaxis=dict(**_YAXIS, title=None,
                   categoryorder="total ascending",
                   tickfont=dict(color="#CBD5E1", size=11)),
        bargap=0.3,
    )
    return fig


def _chart_confidence_gauge(avg_conf: float) -> go.Figure:
    """Radial gauge for average confidence."""
    color = SUCCESS if avg_conf >= 85 else WARNING if avg_conf >= 70 else DANGER

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_conf,
        number=dict(suffix="%", font=dict(color="#F8FAFC", size=36, family="Inter")),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=0, tickcolor="rgba(0,0,0,0)",
                      tickfont=dict(color="#64748B")),
            bar=dict(color=color, thickness=0.22),
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
            steps=[
                dict(range=[0, 70],   color="rgba(239,68,68,0.08)"),
                dict(range=[70, 85],  color="rgba(245,158,11,0.08)"),
                dict(range=[85, 100], color="rgba(34,197,94,0.10)"),
            ],
            threshold=dict(
                line=dict(color=color, width=3),
                thickness=0.75, value=avg_conf,
            ),
        ),
        title=dict(text="Avg Confidence", font=dict(color="#94A3B8", size=13)),
    ))

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        height=240,
        margin=dict(l=20, r=20, t=40, b=10),
    )
    return fig


def _chart_disease_bar(diseases: dict) -> go.Figure:
    """Vertical bar for predicted disease frequency."""
    if not diseases:
        return None
    items  = sorted(diseases.items(), key=lambda x: x[1], reverse=True)[:7]
    labels = [i[0][:20] + "…" if len(i[0]) > 20 else i[0] for i in items]
    values = [i[1] for i in items]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=PALETTE[:len(labels)],
            line=dict(width=0),
            cornerradius=6,
        ),
        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
    ))

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        title=dict(text="Predicted Disease Frequency", font=dict(color="#F8FAFC", size=14)),
        height=280,
        xaxis=dict(**_XAXIS, tickfont=dict(color="#94A3B8", size=10)),
        yaxis=dict(**_YAXIS, title=None, tickfont=dict(color="#64748B")),
        bargap=0.25,
    )
    return fig


def _chart_confidence_timeline(history: list[dict]) -> go.Figure:
    """Scatter + line for confidence over time."""
    dates  = [h.get("date", "") for h in history]
    confs  = [float(h.get("confidence", 0)) for h in history]
    labels = [h.get("disease", "") for h in history]

    # Colour by confidence band
    clrs = [SUCCESS if c >= 85 else WARNING if c >= 70 else DANGER for c in confs]

    fig = go.Figure()
    # Area fill
    fig.add_trace(go.Scatter(
        x=dates, y=confs,
        fill="tozeroy",
        fillcolor="rgba(59,130,246,0.07)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    ))
    # Line
    fig.add_trace(go.Scatter(
        x=dates, y=confs,
        mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5, shape="spline"),
        marker=dict(color=clrs, size=9, line=dict(color="#0B1220", width=2)),
        name="Confidence",
        text=labels,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Confidence: <b>%{y:.1f}%</b><br>"
            "Date: %{x}<extra></extra>"
        ),
    ))

    # Threshold lines
    for level, color, label in [(85, SUCCESS, "High"), (70, WARNING, "Moderate")]:
        fig.add_hline(
            y=level, line=dict(color=color, dash="dot", width=1.2),
            annotation_text=label, annotation_position="right",
            annotation_font=dict(color=color, size=10),
        )

    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        title=dict(text="Prediction Confidence Over Time", font=dict(color="#F8FAFC", size=14)),
        height=280,
        showlegend=False,
        xaxis=dict(**_XAXIS, tickfont=dict(color="#64748B", size=10), title=None),
        yaxis=dict(**_YAXIS, title=None, range=[50, 105], tickfont=dict(color="#64748B")),
    )
    return fig


def _chart_model_radar(model_usage: dict) -> go.Figure:
    """Radar comparing three models across simulated KPIs."""
    models_data = {
        "Logistic Regression": [86.71, 85.0, 86.0, 85.5, 95, 91],
        "Decision Tree":       [81.62, 80.0, 81.0, 80.5, 98, 88],
        "KNN":                 [82.51, 81.0, 82.0, 81.5, 86, 89],
    }
    categories = ["Accuracy", "Precision", "Recall", "F1", "Speed", "Confidence"]
    colors     = [PRIMARY, ACCENT, SUCCESS]

    def _hex_to_rgba(hex_color: str, alpha: float = 0.12) -> str:
        """Convert #RRGGBB hex to rgba(r,g,b,alpha) string."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"

    fig = go.Figure()
    for (name, vals), color in zip(models_data.items(), colors):
        fill_rgba = _hex_to_rgba(color, 0.12)
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=fill_rgba,
            line=dict(color=color, width=2),
            name=name,
            hovertemplate=f"<b>{name}</b><br>%{{theta}}: %{{r:.1f}}<extra></extra>",
        ))


    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                visible=True, range=[75, 100],
                gridcolor="rgba(255,255,255,0.07)",
                linecolor="rgba(255,255,255,0.07)",
                tickfont=dict(color="#64748B", size=9),
                showticklabels=True,
            ),
            angularaxis=dict(
                tickfont=dict(color="#CBD5E1", size=11),
                gridcolor="rgba(255,255,255,0.07)",
                linecolor="rgba(255,255,255,0.07)",
            ),
        ),
        title=dict(text="Multi-Model Performance Radar", font=dict(color="#F8FAFC", size=14)),
        height=340,
        showlegend=True,
        legend=dict(**_LEGEND, orientation="h", x=0.5, xanchor="center", y=-0.08),
    )
    return fig


# ── Page render ─────────────────────────────────────────────────────────────

def render_analytics() -> None:
    """Renders the premium interactive Analytics Dashboard."""

    with PageLayout(
        "📈",
        "Analytics & Metrics",
        "Real-time diagnostic telemetry, algorithm usage, and clinical symptom distributions.",
    ):

        # ── Data sources ──────────────────────────────────────────────────────
        stats = st.session_state.get("analytics", {
            "total_predictions": 0,
            "model_usage":       {"Logistic Regression": 0, "Decision Tree": 0, "KNN": 0},
            "symptoms_detected": {},
            "predicted_diseases": {},
        })

        raw_history = st.session_state.get("prediction_history", [])
        has_data    = stats["total_predictions"] > 0

        # Use baseline data when session is empty so charts are never blank on first visit
        if not has_data:
            demo = _demo_history(12)
            model_usage = {"Logistic Regression": 5, "Decision Tree": 4, "KNN": 3}
            symptoms    = {
                "headache": 8, "fever": 7, "cough": 6, "fatigue": 5,
                "nausea": 4, "joint_pain": 3, "chest_tightness": 3, "vomiting": 2,
            }
            diseases = {
                "Common Cold": 4, "Hypertension": 3, "Diabetes": 3,
                "Migraine": 2, "Asthma": 1, "Gastritis": 1,
            }
            history  = demo
            total    = 12
            avg_conf = round(sum(h["confidence"] for h in demo) / len(demo), 1)
        else:
            model_usage = stats["model_usage"]
            symptoms    = stats["symptoms_detected"]
            diseases    = stats["predicted_diseases"]
            history     = raw_history
            total       = stats["total_predictions"]
            avg_conf    = (
                round(sum(h.get("confidence", 0) for h in raw_history) / len(raw_history), 1)
                if raw_history else 0
            )

        top_model   = max(model_usage, key=model_usage.get)
        top_disease = max(diseases, key=diseases.get) if diseases else "None"

        # ── Baseline banner ───────────────────────────────────────────────────
        if not has_data:
            render_html("""
            <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);
                        border-radius:12px;padding:0.7rem 1.2rem;margin-bottom:1.5rem;
                        display:flex;align-items:center;gap:0.6rem;font-size:0.85rem;color:#F59E0B;">
                <span>⚠</span>
                <span>Showing <strong>baseline data</strong> — run a prediction to populate live telemetry.</span>
            </div>
            """)

        # ── KPI row ───────────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            MetricCard("Total Diagnostics", str(total), delta="This session", delta_positive=True)
        with c2:
            MetricCard("Primary Model", top_model, delta="Highest usage", delta_positive=True)
        with c3:
            MetricCard("Top Condition", top_disease, delta="Most predicted", delta_positive=True)
        with c4:
            MetricCard("Avg Confidence", f"{avg_conf}%",
                       delta="↑ Excellent" if avg_conf >= 85 else "Moderate",
                       delta_positive=avg_conf >= 85)

        SectionDivider()

        # ── Row 1: Donut | Gauge | Symptom bar ───────────────────────────────
        r1c1, r1c2, r1c3 = st.columns([1.4, 0.9, 1.7], gap="medium")

        with r1c1:
            with st.container(border=True):
                fig_donut = _chart_model_donut(model_usage)
                st.plotly_chart(fig_donut, use_container_width=True, config=PLOTLY_CONFIG)

        with r1c2:
            with st.container(border=True):
                fig_gauge = _chart_confidence_gauge(avg_conf)
                st.plotly_chart(fig_gauge, use_container_width=True, config=PLOTLY_CONFIG)

        with r1c3:
            with st.container(border=True):
                fig_syms = _chart_symptom_bar(symptoms)
                if fig_syms:
                    st.plotly_chart(fig_syms, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    EmptyState("No symptom data", "Run a consultation to populate.", icon="🩺")


        SectionDivider()

        # ── Row 2: Confidence timeline | Disease frequency ────────────────────
        r2c1, r2c2 = st.columns([1.6, 1], gap="medium")

        with r2c1:
            with st.container(border=True):
                fig_timeline = _chart_confidence_timeline(history)
                st.plotly_chart(fig_timeline, use_container_width=True, config=PLOTLY_CONFIG)

        with r2c2:
            with st.container(border=True):
                fig_diseases = _chart_disease_bar(diseases)
                if fig_diseases:
                    st.plotly_chart(fig_diseases, use_container_width=True, config=PLOTLY_CONFIG)
                else:
                    EmptyState("No disease data", "Run a prediction first.", icon="📊")


        SectionDivider()

        # ── Row 3: Full-width radar ───────────────────────────────────────────
        with st.container(border=True):
            fig_radar = _chart_model_radar(model_usage)
            st.plotly_chart(fig_radar, use_container_width=True, config=PLOTLY_CONFIG)

