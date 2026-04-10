"""
Report Generation tab for Severity Visualisation Dashboard.

On CSV upload:
  1. Parse & enrich the dataframe
  2. Auto-fetch image UUIDs from Redash (hardcoded config)
  3. Auto-generate and download Excel report
"""

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dcc, html

from utils.data_processor import (
    enrich_dataframe,
    fetch_uuids_from_redash,
    generate_excel_report,
    parse_csv_content,
)

# ── Redash configuration ──────────────────────────────────────────────────────
REDASH_API_KEY  = "IY2HlHUAz3ZX0Y1p2rg4vaFciUOV0MIlkJT0eyOe"
REDASH_BASE_URL = "http://redash.prv.api.cashify.in"
QUERY_ID        = "4300"

# ── Layout ────────────────────────────────────────────────────────────────────

def create_report_generation_tab():
    return html.Div([

        html.Div([
            html.H2("Report Generation", className="section-title"),
            html.P(
                "Upload a feature CSV — UUIDs are fetched from Redash automatically "
                "and the Excel report downloads immediately.",
                className="section-subtitle",
            ),
        ], className="section-header"),

        dbc.Card([
            dbc.CardHeader(html.Span([
                html.I(className="fas fa-upload me-2"),
                "Upload Feature CSV",
            ])),
            dbc.CardBody([
                dcc.Loading(
                    html.Div([
                        dcc.Upload(
                            id="sev-upload-csv",
                            children=html.Div([
                                html.I(className="fas fa-cloud-upload-alt upload-icon"),
                                html.P("Drag & drop or click to upload a feature CSV",
                                       className="upload-text mb-1"),
                                html.P(
                                    "Supports any feature-generation CSV with gt_score, "
                                    "result_image_url and input_images columns.",
                                    style={"fontSize": "0.85em", "color": "#94a3b8"},
                                ),
                            ]),
                            className="upload-area",
                            multiple=False,
                        ),
                        html.Div(id="sev-upload-status", className="mt-3"),
                    ]),
                    type="circle",
                ),
            ]),
        ], className="mb-4"),

        dcc.Download(id="sev-download-excel"),
    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_report_generation_callbacks(app):

    @app.callback(
        Output("sev-upload-status",  "children"),
        Output("sev-data-store",     "data"),
        Output("sev-download-excel", "data"),
        Input("sev-upload-csv",      "contents"),
        State("sev-upload-csv",      "filename"),
        prevent_initial_call=True,
    )
    def on_csv_upload(contents, filename):
        if contents is None:
            return "", {}, None

        # ── 1. Parse & enrich ─────────────────────────────────────────────────
        try:
            df = parse_csv_content(contents, filename)
            df = enrich_dataframe(df)
        except Exception as exc:
            return (
                dbc.Alert([html.I(className="fas fa-exclamation-circle me-2"),
                           f"Error loading CSV: {exc}"],
                          color="danger", className="py-2"),
                {}, None,
            )

        side_val     = df["side"].iloc[0]     if "side"     in df.columns else "?"
        question_val = df["question"].iloc[0] if "question" in df.columns else "?"
        n            = len(df)

        # ── 2. Fetch UUIDs from Redash ────────────────────────────────────────
        uuid_note = ""
        try:
            df, redash_rows, missing = fetch_uuids_from_redash(
                df, REDASH_BASE_URL, REDASH_API_KEY, QUERY_ID
            )
            matched   = n - missing
            uuid_note = f" · {matched:,}/{n:,} UUIDs matched"
        except Exception as exc:
            uuid_note = f" · UUID fetch failed ({exc})"

        # ── 3. Serialise & generate Excel ─────────────────────────────────────
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).replace({"None": "", "nan": ""})
        store_data = df.to_dict(orient="records")

        try:
            excel_bytes = generate_excel_report(df)
            download    = dcc.send_bytes(excel_bytes, "severity_report.xlsx")
        except Exception as exc:
            download  = None
            uuid_note += f" · Excel generation failed ({exc})"

        status = dbc.Alert([
            html.I(className="fas fa-check-circle me-2"),
            f"Loaded {filename} — {n:,} records · {side_val} · {question_val}{uuid_note}",
            html.Span(
                "  Excel downloaded" if download else "  Excel failed",
                style={"marginLeft": "12px", "fontWeight": 600,
                       "color": "#059669" if download else "#dc2626"},
            ),
        ], color="success" if download else "warning", className="py-2")

        return status, store_data, download
