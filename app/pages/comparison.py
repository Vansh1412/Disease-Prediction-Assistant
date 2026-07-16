# pyrefly: ignore [missing-import]
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from app.utils.ui import PageLayout, SectionDivider, render_html

# Base layout - keys that NEVER need to be overridden per-chart
_BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#94A3B8", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    hoverlabel=dict(bgcolor="rgba(11,18,32,0.95)", bordercolor="rgba(255,255,255,0.12)",
                    font=dict(color="#F8FAFC", size=13)),
)

# Reusable sub-dicts for axes and legend — referenced directly, never spread into layout
_XAXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
              tickfont=dict(color="#CBD5E1", size=11), zeroline=False)
_YAXIS = dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)",
              tickfont=dict(color="#64748B", size=10), zeroline=False)
_LEGEND = dict(bgcolor="rgba(11,18,32,0.7)", bordercolor="rgba(255,255,255,0.08)",
               borderwidth=1, font=dict(color="#94A3B8"))

_CFG = dict(
    displayModeBar=True, displaylogo=False,
    modeBarButtonsToRemove=["select2d", "lasso2d"],
    toImageButtonOptions=dict(format="png", filename="model_comparison", scale=2),
    responsive=True,
)


@st.cache_data(show_spinner=False)
def _data() -> pd.DataFrame:
    return pd.DataFrame({
        "Model":                ["Logistic Regression", "Decision Tree", "KNN"],
        "Accuracy":             [0.8671, 0.8162, 0.8251],
        "Precision":            [0.8500, 0.8000, 0.8100],
        "Recall":               [0.8600, 0.8100, 0.8200],
        "F1 Score":             [0.8550, 0.8050, 0.8150],
        "Training Time (sec)":  [263.54, 26.54, 0.90],
        "Prediction Time (sec)": [0.050, 0.010, 0.150],
    })


def render_comparison() -> None:
    """Renders the Model Comparison page with interactive Plotly charts."""

    with PageLayout(
        "📊",
        "Model Comparison",
        "Performance benchmarks across all three machine learning classifiers.",
    ):

        df = _data()
        models  = df["Model"].tolist()
        palette = ["#3B82F6", "#06B6D4", "#22C55E"]

        # ── Row 1: data table | accuracy bar ─────────────────────────────────
        col1, col2 = st.columns([1.2, 1], gap="large")

        with col1:
            render_html("<h3>Performance Telemetry Matrix</h3>")
            with st.container(border=True):
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Accuracy":  st.column_config.NumberColumn(format="%.4f"),
                        "Precision": st.column_config.NumberColumn(format="%.4f"),
                        "Recall":    st.column_config.NumberColumn(format="%.4f"),
                        "F1 Score":  st.column_config.NumberColumn(format="%.4f"),
                        "Training Time (sec)":   st.column_config.NumberColumn(format="%.2f"),
                        "Prediction Time (sec)": st.column_config.NumberColumn(format="%.4f"),
                    },
                )

        with col2:
            render_html("<h3>Accuracy Comparison</h3>")
            with st.container(border=True):
                fig_acc = go.Figure(go.Bar(
                    x=models,
                    y=df["Accuracy"].tolist(),
                    marker=dict(color=palette, cornerradius=6, line=dict(width=0)),
                    text=[f"{v:.2%}" for v in df["Accuracy"]],
                    textposition="outside",
                    textfont=dict(color="#94A3B8", size=11),
                    hovertemplate="<b>%{x}</b><br>Accuracy: <b>%{y:.2%}</b><extra></extra>",
                ))
                # Step 1: apply base layout
                fig_acc.update_layout(**_BASE_LAYOUT)
                # Step 2: apply per-chart overrides (no key conflicts)
                fig_acc.update_layout(
                    title=dict(text="Model Accuracy", font=dict(color="#F8FAFC", size=13)),
                    height=290,
                    showlegend=False,
                    xaxis=_XAXIS,
                    yaxis=dict(**_YAXIS, range=[0.78, 0.90], tickformat=".0%"),
                )
                st.plotly_chart(fig_acc, use_container_width=True, config=_CFG)


        SectionDivider()

        # ── Row 2: grouped bar (4 metrics) | timing scatter ──────────────────
        r2c1, r2c2 = st.columns([1.6, 1], gap="large")

        with r2c1:
            render_html("<h3>Multi-Metric Comparison</h3>")
            with st.container(border=True):
                metrics = ["Accuracy", "Precision", "Recall", "F1 Score"]
                fig_multi = go.Figure()
                for model, color in zip(models, palette):
                    row = df[df["Model"] == model].iloc[0]
                    fig_multi.add_trace(go.Bar(
                        name=model,
                        x=metrics,
                        y=[row[m] for m in metrics],
                        marker=dict(color=color, line=dict(width=0), cornerradius=5),
                        hovertemplate=f"<b>{model}</b><br>%{{x}}: <b>%{{y:.2%}}</b><extra></extra>",
                    ))
                fig_multi.update_layout(**_BASE_LAYOUT)
                fig_multi.update_layout(
                    barmode="group", bargap=0.18, bargroupgap=0.06,
                    height=280,
                    xaxis=_XAXIS,
                    yaxis=dict(**_YAXIS, range=[0.78, 0.90], tickformat=".0%"),
                    legend=dict(**_LEGEND, orientation="h", x=0.5, xanchor="center", y=-0.15),
                )
                st.plotly_chart(fig_multi, use_container_width=True, config=_CFG)

        with r2c2:
            render_html("<h3>Speed vs Accuracy</h3>")
            with st.container(border=True):
                fig_speed = go.Figure()
                for model, color in zip(models, palette):
                    row = df[df["Model"] == model].iloc[0]
                    fig_speed.add_trace(go.Scatter(
                        x=[row["Prediction Time (sec)"]],
                        y=[row["Accuracy"]],
                        mode="markers+text",
                        marker=dict(size=18, color=color,
                                    line=dict(color="#0B1220", width=2),
                                    symbol="circle"),
                        text=[model.split()[0]],
                        textposition="top center",
                        textfont=dict(color="#F8FAFC", size=10),
                        name=model,
                        hovertemplate=(
                            f"<b>{model}</b><br>"
                            "Pred time: <b>%{x:.3f}s</b><br>"
                            "Accuracy: <b>%{y:.2%}</b><extra></extra>"
                        ),
                    ))
                fig_speed.update_layout(**_BASE_LAYOUT)
                fig_speed.update_layout(
                    height=280,
                    showlegend=False,
                    xaxis=dict(**_XAXIS,
                               title=dict(text="Prediction Time (s)",
                                          font=dict(color="#64748B", size=11))),
                    yaxis=dict(**_YAXIS, tickformat=".0%",
                               range=[0.78, 0.90],
                               title=dict(text="Accuracy",
                                          font=dict(color="#64748B", size=11))),
                )
                st.plotly_chart(fig_speed, use_container_width=True, config=_CFG)
