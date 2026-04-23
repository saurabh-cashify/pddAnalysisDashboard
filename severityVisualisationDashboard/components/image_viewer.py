"""
Image Viewer tab for Severity Visualisation Dashboard.

Horizontal-scrolling card carousel.  Each card shows:
  - A coloured severity "score line" (top border stripe)
  - GT score badge + predicted score
  - Input image by default
  - Toggle button to swap between input ↔ prediction image

"+" buttons between cards let the user insert new images manually.
Newly inserted cards are highlighted in light yellow and carry a delete button.

Pattern-matching callbacks (MATCH) ensure each toggle operates independently.
"""

import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import ALL, MATCH, Input, Output, State, ctx, dcc, html
from dash.exceptions import PreventUpdate

from utils.data_processor import (
    generate_excel_report,
    get_severity_badge_color,
    get_severity_label,
)

# ── Constants ─────────────────────────────────────────────────────────────────
CARD_WIDTH = 360
S3_BASE    = "https://tinylabs.s3.ap-south-1.amazonaws.com/images/"

_SEVERITY_BORDER = {
    "High":    "#ef4444",
    "Medium":  "#f59e0b",
    "Low":     "#22c55e",
    "Unknown": "#94a3b8",
}

_PORTRAIT_SIDES = {"back", "front", "frontblack"}

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

        # ── Toolbar: count badge + download button ────────────────────────────
        html.Div([
            html.Div(id="sev-viewer-count"),
            dbc.Button(
                [html.I(className="fas fa-file-excel me-2"), "Download Excel"],
                id="sev-download-excel-btn",
                color="success",
                size="sm",
                outline=True,
            ),
        ], style={"display": "flex", "alignItems": "center",
                  "justifyContent": "space-between", "marginBottom": "12px"}),

        dcc.Download(id="sev-viewer-download-excel"),

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
                            "gap": "0px",
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
                style={
                    "maxHeight": "75vh",
                    "maxWidth": "100%",
                    "width": "auto",
                    "height": "auto",
                    "display": "block",
                    "margin": "0 auto",
                },
            )),
            dbc.ModalFooter(
                dbc.Button("Close", id="sev-close-modal", className="ms-auto"),
            ),
        ], id="sev-img-modal", is_open=False, size="xl"),

        # ── Add-card modal ────────────────────────────────────────────────────
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Add New Image")),
            dbc.ModalBody([
                dbc.Alert(
                    id="sev-add-score-display",
                    color="info",
                    style={"fontWeight": 600, "marginBottom": "16px"},
                ),
                dbc.Label("Image UUID", style={"fontWeight": 600}),
                dbc.Input(
                    id="sev-add-uuid-input",
                    type="text",
                    placeholder="e.g. a1b2c3d4-e5f6-...",
                    className="mb-3",
                ),
                dbc.Label("Side", style={"fontWeight": 600}),
                dbc.Select(
                    id="sev-add-side-input",
                    options=[
                        {"label": s, "value": s}
                        for s in ["front", "back", "frontblack", "left", "right", "top", "other"]
                    ],
                    value="front",
                ),
            ]),
            dbc.ModalFooter([
                dbc.Button("Add Image", id="sev-add-submit-btn", color="primary"),
                dbc.Button("Cancel",    id="sev-add-cancel-btn", color="secondary",
                           className="ms-2"),
            ]),
        ], id="sev-add-modal", is_open=False),
    ])


# ── Card builder ──────────────────────────────────────────────────────────────

def _make_card(record: dict, card_idx: int, is_new: bool = False) -> dbc.Card:
    """Build a single severity card. New/manually-added cards get a yellow tint."""
    gt_raw      = record.get("gt_score")
    sp_raw      = record.get("score_pred")
    txn_id      = str(record.get("pdd_txn_id", ""))
    raw_uuid    = record.get("image_uuid", "")
    image_uuid  = str(raw_uuid) if raw_uuid and str(raw_uuid) not in ("", "nan", "None") else ""
    side        = str(record.get("side", ""))
    question    = str(record.get("question", ""))
    input_url   = str(record.get("input_image_url", ""))
    result_url  = str(record.get("result_image_url", ""))
    card_id     = record.get("_id", card_idx)   # stable id for delete

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

    img_height = "460px" if side.lower() in _PORTRAIT_SIDES else "420px"

    url_stores = html.Div([
        html.Span(
            input_url,
            id={"type": "sev-input-url",  "index": card_idx},
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

    # ── Score row (with delete button for new cards) ──────────────────────────
    score_left = html.Div([
        dbc.Badge(
            gt_display,
            color=badge_color,
            style={"fontSize": "1.15em", "padding": "6px 10px", "fontWeight": 700},
        ),
        html.Span(" GT", style={"fontSize": "0.75em", "color": "#64748b", "marginLeft": "4px"}),
        html.Span(
            f"  pred: {sp_display}",
            style={"fontSize": "0.75em", "color": "#94a3b8", "marginLeft": "8px"},
        ),
    ], className="d-flex align-items-center")

    delete_btn = html.Button(
        "×",
        id={"type": "sev-delete-btn", "index": card_id},
        n_clicks=0,
        title="Remove this card",
        style={
            "border": "none",
            "background": "transparent",
            "color": "#ef4444",
            "fontSize": "1.3em",
            "lineHeight": "1",
            "cursor": "pointer",
            "padding": "0 2px",
            "fontWeight": 700,
        },
    ) if is_new else None

    score_row = html.Div(
        [score_left, delete_btn] if delete_btn else [score_left],
        className="d-flex align-items-center justify-content-between mb-2",
    )

    # ── ID row ────────────────────────────────────────────────────────────────
    new_badge = dbc.Badge(
        "NEW",
        color="warning",
        text_color="dark",
        style={"fontSize": "0.65em", "marginLeft": "6px", "verticalAlign": "middle"},
    ) if is_new else None

    id_row = html.Div(
        [
            html.P(
                image_uuid if image_uuid else txn_id,
                title=f"uuid: {image_uuid}\ntxn: {txn_id}" if image_uuid else txn_id,
                style={
                    "fontSize": "0.72em",
                    "color": "#1e40af" if image_uuid else "#64748b",
                    "marginBottom": "0", "fontFamily": "monospace",
                    "whiteSpace": "nowrap", "overflow": "hidden",
                    "textOverflow": "ellipsis",
                    "fontWeight": 600 if image_uuid else 400,
                },
            ),
            *(([new_badge]) if new_badge else []),
        ],
        className="d-flex align-items-center mb-1",
        style={"gap": "4px"},
    )

    card_bg     = "#fef9c3" if is_new else "white"
    card_border = "2px solid #fbbf24" if is_new else "1px solid #e2e8f0"

    return dbc.Card(
        [
            html.Div(style={
                "height": "6px",
                "background": border_color,
                "borderRadius": "8px 8px 0 0",
            }),
            dbc.CardBody([
                score_row,
                id_row,
                html.Div([
                    dbc.Badge(side, color="info", className="me-1",
                              style={"fontSize": "0.7em"}),
                    dbc.Badge(question[:20] if question else "",
                              color="light", text_color="dark",
                              style={"fontSize": "0.7em"}),
                ], className="mb-2"),
                url_stores,
                image_el,
                html.Div(toggle_btn, className="mt-2"),
            ], style={"padding": "12px"}),
        ],
        style={
            "minWidth": f"{CARD_WIDTH}px",
            "maxWidth": f"{CARD_WIDTH}px",
            "flexShrink": 0,
            "borderRadius": "8px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
            "border": card_border,
            "background": card_bg,
            "margin": "0 8px",
        },
    )


# ── Plus button builder ───────────────────────────────────────────────────────

def _make_plus_btn(gap_idx: int, score_a: float, score_b: float) -> html.Div:
    """Render a '+' button between two cards that opens the add-card modal."""
    midpoint = round((float(score_a) + float(score_b)) / 2, 4)
    return html.Div(
        [
            html.Span(
                str(score_a),
                id={"type": "sev-gap-left",  "index": gap_idx},
                style={"display": "none"},
            ),
            html.Span(
                str(score_b),
                id={"type": "sev-gap-right", "index": gap_idx},
                style={"display": "none"},
            ),
            html.Button(
                "+",
                id={"type": "sev-add-btn", "index": gap_idx},
                n_clicks=0,
                title=f"Insert image with score ≈ {midpoint}",
                style={
                    "width": "28px",
                    "height": "28px",
                    "borderRadius": "50%",
                    "border": "2px dashed #94a3b8",
                    "background": "white",
                    "color": "#64748b",
                    "fontSize": "1.1em",
                    "lineHeight": "1",
                    "cursor": "pointer",
                    "display": "flex",
                    "alignItems": "center",
                    "justifyContent": "center",
                    "padding": "0",
                    "transition": "all 0.15s",
                },
            ),
        ],
        style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "flexShrink": 0,
            "alignSelf": "center",
            "padding": "0 4px",
        },
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _next_card_id(existing_cards: list) -> int:
    """Return an ID one higher than any existing _id in the store."""
    if not existing_cards:
        return 0
    return max((c.get("_id", -1) for c in existing_cards), default=-1) + 1


def _build_combined_df(store_data, added_cards, score_range, sev_filter):
    """Merge CSV records + manually added cards, apply filters, return DataFrame."""
    lo, hi = score_range
    frames = []

    if store_data:
        df = pd.DataFrame(store_data)
        df["gt_score"] = pd.to_numeric(df["gt_score"], errors="coerce")
        df = df[(df["gt_score"] >= lo) & (df["gt_score"] <= hi)]
        if sev_filter:
            df["_sev"] = df["gt_score"].apply(get_severity_label)
            df = df[df["_sev"].isin(sev_filter)]
        df["_is_new"] = False
        frames.append(df)

    if added_cards:
        adf = pd.DataFrame(added_cards)
        adf["gt_score"] = pd.to_numeric(adf["gt_score"], errors="coerce")
        adf = adf[(adf["gt_score"] >= lo) & (adf["gt_score"] <= hi)]
        if sev_filter:
            adf["_sev"] = adf["gt_score"].apply(get_severity_label)
            adf = adf[adf["_sev"].isin(sev_filter)]
        adf["_is_new"] = True
        frames.append(adf)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_image_viewer_callbacks(app):

    # ── Render carousel ──────────────────────────────────────────────────────
    @app.callback(
        Output("sev-card-carousel", "children"),
        Output("sev-viewer-count",  "children"),
        Input("sev-score-range",       "value"),
        Input("sev-sort-order",        "value"),
        Input("sev-severity-filter",   "value"),
        Input("sev-data-store",        "data"),
        Input("sev-added-cards-store", "data"),
    )
    def render_carousel(score_range, sort_order, sev_filter, store_data, added_cards):
        if not store_data and not added_cards:
            return (
                html.Div(
                    "Upload a CSV in the Report Generation tab to view images.",
                    style={"color": "#94a3b8", "padding": "40px",
                           "textAlign": "center", "width": "100%"},
                ),
                "",
            )

        combined = _build_combined_df(store_data, added_cards, score_range, sev_filter)
        combined = combined.sort_values(
            "gt_score", ascending=(sort_order == "asc")
        ).reset_index(drop=True)

        if combined.empty:
            return (
                html.Div(
                    "No records match the current filters.",
                    style={"color": "#94a3b8", "padding": "40px",
                           "textAlign": "center", "width": "100%"},
                ),
                "",
            )

        items   = []
        gap_idx = 0

        for i, (_, row) in enumerate(combined.iterrows()):
            record = row.to_dict()
            is_new = bool(record.get("_is_new", False))

            if i > 0:
                prev_score = combined.iloc[i - 1]["gt_score"]
                curr_score = row["gt_score"]
                items.append(_make_plus_btn(gap_idx, prev_score, curr_score))
                gap_idx += 1

            items.append(_make_card(record, i, is_new))

        total = len(combined)
        new_count = int(combined["_is_new"].sum()) if "_is_new" in combined.columns else 0

        count_parts = [dbc.Badge(f"{total:,} records", color="primary")]
        if new_count:
            count_parts.append(
                dbc.Badge(f"+{new_count} manually added", color="warning",
                          text_color="dark", className="ms-2")
            )

        return items, html.Span(count_parts)

    # ── Open add-card modal on "+" click ────────────────────────────────────
    @app.callback(
        Output("sev-add-modal",         "is_open"),
        Output("sev-gap-store",         "data"),
        Output("sev-add-score-display", "children"),
        Output("sev-add-uuid-input",    "value"),
        Input({"type": "sev-add-btn",   "index": ALL}, "n_clicks"),
        State({"type": "sev-gap-left",  "index": ALL}, "children"),
        State({"type": "sev-gap-right", "index": ALL}, "children"),
        prevent_initial_call=True,
    )
    def open_add_modal(all_clicks, left_scores, right_scores):
        if not ctx.triggered or not any(c for c in (all_clicks or []) if c):
            raise PreventUpdate

        triggered_id = ctx.triggered_id
        if not triggered_id:
            raise PreventUpdate

        gap_idx = triggered_id["index"]

        for inp_info, ls, rs in zip(ctx.inputs_list[0], left_scores, right_scores):
            if inp_info["id"]["index"] == gap_idx:
                try:
                    left  = float(ls)
                    right = float(rs)
                except (TypeError, ValueError):
                    raise PreventUpdate
                midpoint = round((left + right) / 2, 4)
                gap_data = {"left": left, "right": right, "midpoint": midpoint}
                msg = (
                    f"New image will be assigned score: {midpoint}  "
                    f"(midpoint of {left} and {right})"
                )
                return True, gap_data, msg, ""

        raise PreventUpdate

    # ── Cancel add-card modal ────────────────────────────────────────────────
    @app.callback(
        Output("sev-add-modal", "is_open", allow_duplicate=True),
        Input("sev-add-cancel-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def cancel_add_modal(_):
        return False

    # ── Submit new card ───────────────────────────────────────────────────────
    @app.callback(
        Output("sev-added-cards-store", "data"),
        Output("sev-add-modal", "is_open", allow_duplicate=True),
        Input("sev-add-submit-btn",    "n_clicks"),
        State("sev-add-uuid-input",    "value"),
        State("sev-add-side-input",    "value"),
        State("sev-gap-store",         "data"),
        State("sev-added-cards-store", "data"),
        prevent_initial_call=True,
    )
    def submit_new_card(n_clicks, uuid_val, side_val, gap_data, existing_cards):
        if not n_clicks or not uuid_val or not str(uuid_val).strip() or not gap_data:
            raise PreventUpdate

        uuid_clean = str(uuid_val).strip()
        score      = gap_data["midpoint"]
        image_url  = f"{S3_BASE}{uuid_clean}.png"

        cards = list(existing_cards or [])
        new_record = {
            "_id":              _next_card_id(cards),
            "gt_score":         score,
            "score_pred":       None,
            "image_uuid":       uuid_clean,
            "side":             side_val or "front",
            "question":         "",
            "pdd_txn_id":       "",
            "input_image_url":  image_url,
            "result_image_url": "",
        }
        cards.append(new_record)
        return cards, False

    # ── Delete a manually added card ──────────────────────────────────────────
    @app.callback(
        Output("sev-added-cards-store", "data", allow_duplicate=True),
        Input({"type": "sev-delete-btn", "index": ALL}, "n_clicks"),
        State("sev-added-cards-store", "data"),
        prevent_initial_call=True,
    )
    def delete_added_card(all_clicks, existing_cards):
        if not ctx.triggered or not any(c for c in (all_clicks or []) if c):
            raise PreventUpdate

        triggered_id = ctx.triggered_id
        if not triggered_id:
            raise PreventUpdate

        target_id = triggered_id["index"]
        cards = [c for c in (existing_cards or []) if c.get("_id") != target_id]
        return cards

    # ── Download Excel (CSV + manually added cards) ───────────────────────────
    @app.callback(
        Output("sev-viewer-download-excel", "data"),
        Input("sev-download-excel-btn",    "n_clicks"),
        State("sev-data-store",            "data"),
        State("sev-added-cards-store",     "data"),
        prevent_initial_call=True,
    )
    def download_excel(n_clicks, store_data, added_cards):
        if not n_clicks:
            raise PreventUpdate
        if not store_data and not added_cards:
            raise PreventUpdate

        frames = []

        if store_data:
            df = pd.DataFrame(store_data)
            df["_is_new"] = False
            frames.append(df)

        if added_cards:
            adf = pd.DataFrame(added_cards)
            adf["_is_new"] = True
            frames.append(adf)

        combined = pd.concat(frames, ignore_index=True)
        combined["gt_score"] = pd.to_numeric(combined["gt_score"], errors="coerce")
        combined = combined.sort_values("gt_score", ascending=False).reset_index(drop=True)

        # Ensure required columns exist
        for col in ["image_uuid", "pdd_txn_id", "side", "question",
                    "score_pred", "input_image_url", "result_image_url"]:
            if col not in combined.columns:
                combined[col] = ""

        for col in combined.select_dtypes(include="object").columns:
            combined[col] = combined[col].astype(str).replace({"None": "", "nan": ""})

        excel_bytes = generate_excel_report(combined)
        return dcc.send_bytes(excel_bytes, "severity_report_updated.xlsx")

    # ── Per-card image toggle (MATCH pattern) ────────────────────────────────
    @app.callback(
        Output({"type": "sev-card-img",   "index": MATCH}, "src"),
        Output({"type": "sev-toggle-btn", "index": MATCH}, "children"),
        Output({"type": "sev-toggle-btn", "index": MATCH}, "color"),
        Input({"type":  "sev-toggle-btn", "index": MATCH}, "n_clicks"),
        State({"type":  "sev-input-url",  "index": MATCH}, "children"),
        State({"type":  "sev-result-url", "index": MATCH}, "children"),
        prevent_initial_call=True,
    )
    def toggle_image(n_clicks, input_url, result_url):
        if n_clicks and n_clicks % 2 == 1:
            return result_url or "", "Show Input",      "warning"
        return input_url or "",  "Show Prediction", "secondary"

    # ── Image click → open full-image modal ──────────────────────────────────
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
            comp_id     = json.loads(triggered["prop_id"].rsplit(".", 1)[0])
            clicked_idx = comp_id["index"]
        except Exception:
            return False, ""
        for inp, src in zip(ctx.inputs_list[0], all_srcs):
            if inp["id"]["index"] == clicked_idx:
                return True, src or ""
        return False, ""

    # ── Close full-image modal ───────────────────────────────────────────────
    @app.callback(
        Output("sev-img-modal",  "is_open", allow_duplicate=True),
        Input("sev-close-modal", "n_clicks"),
        prevent_initial_call=True,
    )
    def close_modal(_):
        return False
