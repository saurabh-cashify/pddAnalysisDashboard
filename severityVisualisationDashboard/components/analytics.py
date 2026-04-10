"""
Analytics tab for Severity Visualisation Dashboard.

Shows EDA from the loaded feature CSV:
  - Summary stat cards
  - GT Score distribution histogram
  - GT Score vs Predicted Score scatter
  - Top feature correlations with GT Score (bar)
  - Feature distribution explorer (boxplot by severity)

Reads from sev-data-store; refreshes whenever the tab becomes active
or new data is loaded.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html, no_update

from utils.data_processor import (
    compute_correlations,
    get_numeric_feature_columns,
    get_severity_label,
)

# ── Layout ────────────────────────────────────────────────────────────────────

def create_analytics_tab():
    return html.Div([

        html.Div([
            html.H2("Analytics", className="section-title"),
            html.P(
                "GT score distributions, feature correlations, and EDA from debug_dict.",
                className="section-subtitle",
            ),
        ], className="section-header"),

        html.Div(
            id="sev-analytics-content",
            children=html.Div(
                "Upload a CSV in the Report Generation tab to see analytics.",
                style={"textAlign": "center", "color": "#94a3b8", "padding": "60px"},
            ),
        ),
    ])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _stat_card(title: str, value, subtitle: str = "", color: str = "#3b82f6"):
    return dbc.Card([
        dbc.CardBody([
            html.P(title, style={"fontSize": "0.85em", "color": "#64748b",
                                  "fontWeight": 600, "marginBottom": "4px"}),
            html.H3(str(value), style={"color": color, "fontWeight": 700,
                                        "marginBottom": "4px"}),
            html.P(subtitle, style={"fontSize": "0.8em", "color": "#94a3b8",
                                     "marginBottom": 0}),
        ], style={"padding": "20px"}),
    ], className="h-100", style={"borderTop": f"4px solid {color}"})


def _build_analytics_content(df: pd.DataFrame):
    n         = len(df)
    gt        = pd.to_numeric(df["gt_score"], errors="coerce").dropna()
    high_pct  = (gt >= 67).mean() * 100
    med_pct   = ((gt >= 34) & (gt < 67)).mean() * 100
    low_pct   = (gt < 34).mean() * 100
    mean_gt   = gt.mean()
    median_gt = gt.median()

    side_val     = df["side"].iloc[0]     if "side"     in df.columns else "–"
    question_val = df["question"].iloc[0] if "question" in df.columns else "–"

    # ── Stat cards ────────────────────────────────────────────────────────────
    stat_row = dbc.Row([
        dbc.Col(_stat_card("Total Records",   f"{n:,}",          f"{side_val} · {question_val}"), md=2),
        dbc.Col(_stat_card("Mean GT Score",   f"{mean_gt:.1f}",  "avg severity"), md=2),
        dbc.Col(_stat_card("Median GT Score", f"{median_gt:.1f}","50th percentile"), md=2),
        dbc.Col(_stat_card("High Severity",   f"{high_pct:.1f}%","gt_score ≥ 67",  color="#ef4444"), md=2),
        dbc.Col(_stat_card("Medium Severity", f"{med_pct:.1f}%", "34 ≤ gt_score < 67", color="#f59e0b"), md=2),
        dbc.Col(_stat_card("Low Severity",    f"{low_pct:.1f}%", "gt_score < 34", color="#22c55e"), md=2),
    ], className="g-3 mb-4")

    # ── GT Score histogram ────────────────────────────────────────────────────
    hist_df = df[["gt_score"]].copy()
    hist_df["gt_score"] = pd.to_numeric(hist_df["gt_score"], errors="coerce")
    hist_df = hist_df.dropna()
    hist_df["severity"] = hist_df["gt_score"].apply(get_severity_label)

    fig_hist = px.histogram(
        hist_df, x="gt_score", color="severity", nbins=40,
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
        labels={"gt_score": "GT Score", "count": "Count"},
        title="GT Score Distribution",
        category_orders={"severity": ["Low", "Medium", "High"]},
    )
    fig_hist.update_layout(
        paper_bgcolor="white", plot_bgcolor="#f8fafc",
        legend_title_text="Severity", bargap=0.05,
        xaxis=dict(range=[0, 100]),
    )

    # ── GT vs Pred scatter ────────────────────────────────────────────────────
    sc_cols = [c for c in ["gt_score", "score_pred", "severity", "pdd_txn_id"] if c in df.columns]
    sc_df = df[sc_cols].copy()
    sc_df["gt_score"]    = pd.to_numeric(sc_df["gt_score"],    errors="coerce")
    sc_df["score_pred"]  = pd.to_numeric(sc_df["score_pred"],  errors="coerce")
    sc_df = sc_df.dropna(subset=["gt_score", "score_pred"])

    fig_scatter = px.scatter(
        sc_df, x="gt_score", y="score_pred",
        color="severity" if "severity" in sc_df.columns else None,
        color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
        labels={"gt_score": "GT Score", "score_pred": "Predicted Score"},
        title="GT Score vs Predicted Score",
        hover_data=["pdd_txn_id"] if "pdd_txn_id" in sc_df.columns else [],
        opacity=0.7,
    )
    fig_scatter.add_shape(
        type="line", x0=0, y0=0, x1=100, y1=100,
        line=dict(color="#94a3b8", dash="dash", width=1.5),
    )
    fig_scatter.update_layout(
        paper_bgcolor="white", plot_bgcolor="#f8fafc",
        legend_title_text="Severity",
    )

    # ── Feature correlation bar ───────────────────────────────────────────────
    corr = compute_correlations(df).dropna().head(20)
    corr_df = corr.reset_index()
    corr_df.columns = ["feature", "correlation"]
    corr_df["color"] = corr_df["correlation"].apply(
        lambda v: "#3b82f6" if v >= 0 else "#f97316"
    )

    fig_corr = go.Figure(go.Bar(
        x=corr_df["correlation"], y=corr_df["feature"],
        orientation="h",
        marker_color=corr_df["color"],
        text=corr_df["correlation"].round(3),
        textposition="outside",
    ))
    fig_corr.update_layout(
        title="Top Feature Correlations with GT Score",
        xaxis_title="Pearson r",
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="white", plot_bgcolor="#f8fafc",
        height=520,
        margin=dict(l=20, r=40, t=50, b=20),
    )

    # ── Feature distribution explorer ────────────────────────────────────────
    feat_cols = get_numeric_feature_columns(df)
    default_feat = "scratch_num_of_defects" if "scratch_num_of_defects" in feat_cols else (feat_cols[0] if feat_cols else None)

    feature_explorer = dbc.Card([
        dbc.CardHeader(html.Span([
            html.I(className="fas fa-chart-area me-2"),
            "Feature Distribution Explorer (from debug_dict)",
        ])),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select Feature"),
                    dcc.Dropdown(
                        id="sev-feat-dropdown",
                        options=[{"label": c, "value": c} for c in feat_cols],
                        value=default_feat,
                        clearable=False,
                    ),
                ], md=4),
            ], className="mb-3"),
            dcc.Graph(id="sev-feat-dist-chart"),
        ]),
    ], className="mb-4")

    return html.Div([
        stat_row,
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_hist),     md=6),
            dbc.Col(dcc.Graph(figure=fig_scatter),  md=6),
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_corr), md=12),
        ], className="mb-4"),
        feature_explorer,
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_analytics_callbacks(app):

    # Rebuild analytics whenever data changes OR user switches to this tab
    @app.callback(
        Output("sev-analytics-content", "children"),
        Input("sev-data-store", "data"),
        Input("sev-main-tabs", "active_tab"),
    )
    def update_analytics_content(store_data, active_tab):
        if active_tab != "analytics":
            return no_update
        if not store_data:
            return html.Div(
                "Upload a CSV in the Report Generation tab to see analytics.",
                style={"textAlign": "center", "color": "#94a3b8", "padding": "60px"},
            )
        df = pd.DataFrame(store_data)
        return _build_analytics_content(df)

    # Feature distribution boxplot (lives inside analytics tab)
    @app.callback(
        Output("sev-feat-dist-chart", "figure"),
        Input("sev-feat-dropdown", "value"),
        State("sev-data-store", "data"),
        prevent_initial_call=True,
    )
    def update_feature_dist(feature, store_data):
        if not store_data or not feature:
            return go.Figure()

        df = pd.DataFrame(store_data)
        if feature not in df.columns:
            return go.Figure()

        feat_df = df[[feature, "gt_score"]].copy()
        feat_df["gt_score"] = pd.to_numeric(feat_df["gt_score"], errors="coerce")
        feat_df[feature]    = pd.to_numeric(feat_df[feature],    errors="coerce")
        feat_df = feat_df.dropna(subset=[feature])
        feat_df["severity"] = feat_df["gt_score"].apply(get_severity_label)

        fig = px.box(
            feat_df, x="severity", y=feature, color="severity",
            color_discrete_map={"High": "#ef4444", "Medium": "#f59e0b", "Low": "#22c55e"},
            category_orders={"severity": ["Low", "Medium", "High"]},
            title=f"{feature}  distribution by Severity",
            points="outliers",
        )
        fig.update_layout(
            paper_bgcolor="white", plot_bgcolor="#f8fafc",
            showlegend=False,
        )
        return fig
