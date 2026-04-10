"""
Severity Visualisation Dashboard
=================================
Three-tab Dash application:
  1. Report Generation — CSV upload + Excel export
  2. Analytics         — EDA, score distributions, feature correlations
  3. Image Viewer      — horizontal card carousel with image toggle
"""

import os

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html

from components import (
    create_analytics_tab,
    create_image_viewer_tab,
    create_report_generation_tab,
    register_analytics_callbacks,
    register_image_viewer_callbacks,
    register_report_generation_callbacks,
)

# ── App initialisation ────────────────────────────────────────────────────────

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
    ],
    suppress_callback_exceptions=True,
    assets_folder="assets",
)
app.title = "Severity Visualisation Dashboard"
server = app.server   # expose for gunicorn


# ── Header ────────────────────────────────────────────────────────────────────

def _header():
    return dbc.Container(
        html.Div([
            html.H1("Severity Visualisation Dashboard", className="dashboard-title"),
            html.P(
                "GT Score Analysis · Feature EDA · Prediction Review",
                className="dashboard-subtitle",
            ),
        ], className="dashboard-header"),
        fluid=True,
        className="header-container",
    )


# ── Tab navigation ────────────────────────────────────────────────────────────

def _tabs():
    return dbc.Tabs(
        [
            dbc.Tab(label="📊 Report Generation", tab_id="report"),
            dbc.Tab(label="📈 Analytics",          tab_id="analytics"),
            dbc.Tab(label="📷 Image Viewer",        tab_id="viewer"),
        ],
        id="sev-main-tabs",
        active_tab="report",
        className="tab-navigation",
        style={"width": "100%"},
    )


# ── Layout ────────────────────────────────────────────────────────────────────

app.layout = dbc.Container(
    [
        # Shared data store (JSON string, records-orient)
        dcc.Store(id="sev-data-store", data={}),
        _header(),
        _tabs(),

        html.Div(
            id="sev-tab-content",
            className="tab-content-container",
            children=create_report_generation_tab(),
        ),
    ],
    fluid=True,
    className="main-container",
)


# ── Tab routing ───────────────────────────────────────────────────────────────

@app.callback(
    Output("sev-tab-content", "children"),
    Input("sev-main-tabs", "active_tab"),
)
def render_tab(tab):
    if tab == "analytics":
        return create_analytics_tab()
    if tab == "viewer":
        return create_image_viewer_tab()
    return create_report_generation_tab()


# ── Register callbacks ────────────────────────────────────────────────────────

register_report_generation_callbacks(app)
register_analytics_callbacks(app)
register_image_viewer_callbacks(app)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8051))
    host = os.getenv("HOST", "0.0.0.0")

    print("=" * 55)
    print("  Severity Visualisation Dashboard")
    print("=" * 55)
    print(f"  http://localhost:{port}")
    print("=" * 55)
    app.run(debug=False, host=host, port=port)
