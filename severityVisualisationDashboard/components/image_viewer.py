"""
Image Viewer tab for Severity Visualisation Dashboard.

Horizontal-scrolling card carousel.  Each card shows:
  - A coloured severity "score line" (top border stripe)
  - GT score badge + predicted score
  - Input image by default
  - Toggle button to swap between input ↔ prediction image

Pattern-matching callbacks (MATCH) ensure each toggle operates independently.
"""

import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, MATCH, Input, Output, State, ctx, dcc, html

from utils.data_processor import get_severity_badge_color, get_severity_label

# ── Constants ─────────────────────────────────────────────────────────────────
CARD_WIDTH = 360  # px

_SEVERITY_BORDER = {
    "High":    "#ef4444",
    "Medium":  "#f59e0b",
    "Low":     "#22c55e",
    "Unknown": "#94a3b8",
}

# ── Layout ────────────────────────────────────────────────────────────────────

def create_image_viewer_tab():
    return html.Div([

        # ── Section header ────────────────────────────────────────────────────
        html.Div([
            html.H2("Image Viewer", className="section-title"),
            html.P(
                "Review predictions alongside input images, sorted by GT severity score.",
                className="section-subtitle",
            ),
        ], className="section-header"),

        # ── Filter bar ────────────────────────────────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("GT Score Range", style={"fontWeight": 600}),
                        dcc.RangeSlider(
                            id="sev-score-range",
                            min=0, max=100, step=1,
                            value=[0, 100],
                            marks={0: "0", 25: "25", 50: "50", 75: "75", 100: "100"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ], md=5),
                    dbc.Col([
                        dbc.Label("Sort By", style={"fontWeight": 600}),
                        dbc.RadioItems(
                            id="sev-sort-order",
                            options=[
                                {"label": "Highest first", "value": "desc"},
                                {"label": "Lowest first",  "value": "asc"},
                            ],
                            value="desc",
                            inline=True,
                        ),
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Severity Filter", style={"fontWeight": 600}),
                        dbc.Checklist(
                            id="sev-severity-filter",
                            options=[
                                {"label": html.Span("High",   style={"color": "#ef4444"}), "value": "High"},
                                {"label": html.Span("Medium", style={"color": "#f59e0b"}), "value": "Medium"},
                                {"label": html.Span("Low",    style={"color": "#22c55e"}), "value": "Low"},
                            ],
                            value=["High", "Medium", "Low"],
                            inline=True,
                        ),
                    ], md=4),
                ], className="align-items-center"),
            ]),
        ], className="mb-3"),

        # ── Record count badge ────────────────────────────────────────────────
        html.Div(id="sev-viewer-count", className="mb-3"),

        # ── Horizontal scrolling card carousel ───────────────────────────────
        dbc.Card([
            dbc.CardBody([
                dcc.Loading(
                    html.Div(
                        id="sev-card-carousel",
                        style={
                            "display": "flex",
                            "flexDirection": "row",
                            "overflowX": "auto",
                            "gap": "16px",
                            "padding": "8px 4px 16px 4px",
                            "minHeight": "620px",
                            "alignItems": "flex-start",
                        },
                    ),
                    type="circle",
                ),
            ], style={"padding": "16px"}),
        ], className="mb-3"),

        # ── Full-image modal ──────────────────────────────────────────────────
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Image Preview")),
            dbc.ModalBody(html.Img(
                id="sev-modal-img",
                src="",
                style={"width": "100%", "height": "auto"},
            )),
            dbc.ModalFooter(
                dbc.Button("Close", id="sev-close-modal", className="ms-auto"),
            ),
        ], id="sev-img-modal", is_open=False, size="xl"),
    ])


# ── Card builder ──────────────────────────────────────────────────────────────

def _make_card(record: dict, card_idx: int) -> dbc.Card:
    """Build a single severity card."""
    gt_raw      = record.get("gt_score")
    sp_raw      = record.get("score_pred")
    txn_id      = str(record.get("pdd_txn_id", ""))
    raw_uuid    = record.get("image_uuid", "")
    image_uuid  = str(raw_uuid) if raw_uuid and str(raw_uuid) not in ("", "nan", "None") else ""
    side        = str(record.get("side", ""))
    question    = str(record.get("question", ""))
    input_url   = str(record.get("input_image_url", ""))
    result_url  = str(record.get("result_image_url", ""))

    try:
        gt_score = round(float(gt_raw), 1)
    except (TypeError, ValueError):
        gt_score = None
    try:
        sp_score = round(float(sp_raw), 1)
    except (TypeError, ValueError):
        sp_score = None

    severity     = get_severity_label(gt_score)
    badge_color  = get_severity_badge_color(gt_score)
    border_color = _SEVERITY_BORDER.get(severity, "#94a3b8")

    gt_display = f"{gt_score}" if gt_score is not None else "–"
    sp_display = f"{sp_score}" if sp_score is not None else "–"

    # Image height: portrait sides (back/front) get more room; landscape sides less
    _portrait_sides = {"back", "front", "frontblack"}
    img_height = "460px" if side.lower() in _portrait_sides else "320px"

    # hidden spans to store URLs (read by pattern-matching callback)
    url_stores = html.Div([
        html.Span(
            input_url,
            id={"type": "sev-input-url", "index": card_idx},
            style={"display": "none"},
        ),
        html.Span(
            result_url,
            id={"type": "sev-result-url", "index": card_idx},
            style={"display": "none"},
        ),
    ])

    image_el = html.Img(
        src=input_url or "",
        id={"type": "sev-card-img", "index": card_idx},
        style={
            "width": "100%",
            "height": img_height,
            "objectFit": "contain",
            "borderRadius": "6px",
            "cursor": "pointer",
            "border": "1px solid #e2e8f0",
        },
        n_clicks=0,
        title=txn_id,
    )

    toggle_btn = dbc.Button(
        "Show Prediction",
        id={"type": "sev-toggle-btn", "index": card_idx},
        size="sm",
        color="secondary",
        outline=True,
        n_clicks=0,
        style={"width": "100%", "fontSize": "0.78em"},
        disabled=not bool(result_url),
    )

    return dbc.Card(
        [
            # Score line stripe
            html.Div(style={
                "height": "6px",
                "background": border_color,
                "borderRadius": "8px 8px 0 0",
            }),
            dbc.CardBody([
                # Scores row
                html.Div([
                    dbc.Badge(
                        gt_display,
                        color=badge_color,
                        style={"fontSize": "1.15em", "padding": "6px 10px",
                               "fontWeight": 700},
                    ),
                    html.Span(" GT", style={"fontSize": "0.75em", "color": "#64748b",
                                            "marginLeft": "4px"}),
                    html.Span(
                        f"  pred: {sp_display}",
                        style={"fontSize": "0.75em", "color": "#94a3b8",
                               "marginLeft": "8px"},
                    ),
                ], className="d-flex align-items-center mb-2"),

                # ID row — image_uuid if available, else pdd_txn_id
                html.P(
                    image_uuid if image_uuid else txn_id,
                    title=f"uuid: {image_uuid}\ntxn: {txn_id}" if image_uuid else txn_id,
                    style={
                        "fontSize": "0.72em",
                        "color": "#1e40af" if image_uuid else "#64748b",
                        "marginBottom": "4px", "fontFamily": "monospace",
                        "whiteSpace": "nowrap", "overflow": "hidden",
                        "textOverflow": "ellipsis",
                        "fontWeight": 600 if image_uuid else 400,
                    },
                ),
                html.Div([
                    dbc.Badge(side, color="info", className="me-1",
                              style={"fontSize": "0.7em"}),
                    dbc.Badge(question[:20] if question else "",
                              color="light", text_color="dark",
                              style={"fontSize": "0.7em"}),
                ], className="mb-2"),

                # Image
                url_stores,
                image_el,

                # Toggle
                html.Div(toggle_btn, className="mt-2"),
            ], style={"padding": "12px"}),
        ],
        style={
            "minWidth": f"{CARD_WIDTH}px",
            "maxWidth": f"{CARD_WIDTH}px",
            "flexShrink": 0,
            "borderRadius": "8px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "border": "1px solid #e2e8f0",
        },
    )


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_image_viewer_callbacks(app):

    # ── Render carousel ──────────────────────────────────────────────────────
    @app.callback(
        Output("sev-card-carousel", "children"),
        Output("sev-viewer-count", "children"),
        Input("sev-score-range", "value"),
        Input("sev-sort-order", "value"),
        Input("sev-severity-filter", "value"),
        Input("sev-data-store", "data"),
    )
    def render_carousel(score_range, sort_order, sev_filter, store_data):
        if not store_data:
            return (
                html.Div("Upload a CSV in the Report Generation tab to view images.",
                         style={"color": "#94a3b8", "padding": "40px",
                                "textAlign": "center", "width": "100%"}),
                "",
            )

        df = pd.DataFrame(store_data)
        df["gt_score"] = pd.to_numeric(df["gt_score"], errors="coerce")

        lo, hi = score_range
        df = df[(df["gt_score"] >= lo) & (df["gt_score"] <= hi)]

        if sev_filter:
            df["_sev"] = df["gt_score"].apply(get_severity_label)
            df = df[df["_sev"].isin(sev_filter)]

        df = df.sort_values("gt_score", ascending=(sort_order == "asc")).reset_index(drop=True)

        total = len(df)

        if df.empty:
            cards = [html.Div("No records match the current filters.",
                              style={"color": "#94a3b8", "padding": "40px",
                                     "textAlign": "center", "width": "100%"})]
        else:
            cards = [
                _make_card(row.to_dict(), i)
                for i, (_, row) in enumerate(df.iterrows())
            ]

        count_badge = dbc.Badge(f"{total:,} records", color="primary")

        return cards, count_badge

    # ── Per-card image toggle (MATCH pattern) ────────────────────────────────
    @app.callback(
        Output({"type": "sev-card-img",    "index": MATCH}, "src"),
        Output({"type": "sev-toggle-btn",  "index": MATCH}, "children"),
        Output({"type": "sev-toggle-btn",  "index": MATCH}, "color"),
        Input({"type":  "sev-toggle-btn",  "index": MATCH}, "n_clicks"),
        State({"type":  "sev-input-url",   "index": MATCH}, "children"),
        State({"type":  "sev-result-url",  "index": MATCH}, "children"),
        prevent_initial_call=True,
    )
    def toggle_image(n_clicks, input_url, result_url):
        if n_clicks and n_clicks % 2 == 1:
            return result_url or "", "Show Input",      "warning"
        return input_url or "",  "Show Prediction", "secondary"

    # ── Image click → open modal (ALL avoids MATCH/Output mismatch) ─────────
    @app.callback(
        Output("sev-img-modal", "is_open"),
        Output("sev-modal-img", "src"),
        Input({"type": "sev-card-img", "index": ALL}, "n_clicks"),
        State({"type": "sev-card-img", "index": ALL}, "src"),
        prevent_initial_call=True,
    )
    def open_modal(all_clicks, all_srcs):
        if not ctx.triggered or not any(c for c in (all_clicks or [])):
            return False, ""
        triggered = ctx.triggered[0]
        if not triggered.get("value"):
            return False, ""
        try:
            comp_id = json.loads(triggered["prop_id"].rsplit(".", 1)[0])
            clicked_idx = comp_id["index"]
        except Exception:
            return False, ""
        for inp, src in zip(ctx.inputs_list[0], all_srcs):
            if inp["id"]["index"] == clicked_idx:
                return True, src or ""
        return False, ""

    # ── Close modal ──────────────────────────────────────────────────────────
    @app.callback(
        Output("sev-img-modal",  "is_open", allow_duplicate=True),
        Input("sev-close-modal", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal(n):
        return False
