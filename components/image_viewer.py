"""
Image Viewer Tab Component for Analysis Dashboard
Displays filtered records with images from all sides
"""

from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH, no_update
import dash
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def create_image_viewer_tab():
    """Create the Image Viewer tab layout"""
    
    return dbc.Container([
        # Note: audit-tags-store is now in the main app layout for sharing with Cell Details tab
        
        # Controls Panel
        dbc.Card([
            dbc.CardBody([
                html.H3("🎯 Filters", className="mb-3", style={"color": "#3b82f6"}),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed CScan Answer", html_for="cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cscan-answer-filter",
                            options=[],  # Will be populated dynamically
                            value=[],  # Empty = all selected
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("New CScan Answer", html_for="new-cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="new-cscan-answer-filter",
                            options=[],  # Will be populated dynamically
                            value=[],  # Empty = all selected
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Final Answer", html_for="final-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="final-answer-filter",
                            options=[],  # Will be populated dynamically
                            value=[],  # Empty = all selected
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed Contributing Sides", html_for="contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="contributing-side-filter",
                            options=[
                                {"label": "(Blank)", "value": "_blank_"},
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],  # Empty by default (means all selected when filter applied)
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("New Contributing Sides", html_for="new-contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="new-contributing-side-filter",
                            options=[
                                {"label": "(Blank)", "value": "_blank_"},
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],  # Empty by default (means all selected when filter applied)
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed Side Score Filter", html_for="deployed-side-score-filter", className="fw-bold"),
                        dcc.RangeSlider(
                            id="deployed-score-range-slider",
                            min=0,
                            max=100,
                            step=1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="deployed-side-score-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],  # Empty = all sides
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("New Side Score Filter", html_for="new-side-score-filter", className="fw-bold"),
                        dcc.RangeSlider(
                            id="new-score-range-slider",
                            min=0,
                            max=100,
                            step=1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="new-side-score-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],  # Empty = all sides
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button("🔍 Apply Filters", id="apply-filters-btn", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset Filters", id="reset-filters-btn", color="warning", className="me-2"),
                        dbc.Button("📥 Export Audit CSV", id="export-audit-btn", color="success", className=""),
                    ], className="d-flex"),
                    dbc.Col([
                        html.Span(id="audit-status", className="text-muted", style={"lineHeight": "38px"})
                    ], className="text-end")
                ]),
                # Download component for audit CSV
                dcc.Download(id="download-audit-csv")
            ])
        ], className="mb-4", style={"background": "linear-gradient(to bottom, #f8fafc, #f1f5f9)"}),
        
        # Stats Bar
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span("Total Records:", className="label fw-bold me-2"),
                        html.Span("0", id="total-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Filtered:", className="label fw-bold me-2"),
                        html.Span("0", id="filtered-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Current:", className="label fw-bold me-2"),
                        html.Span("0", id="current-index-display", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Old Accuracy:", className="label fw-bold me-2"),
                        html.Span("N/A", id="old-accuracy", className="value", style={"color": "#10b981", "fontSize": "1.2em"}),
                    ], md=3),
                    dbc.Col([
                        html.Span("New Accuracy:", className="label fw-bold me-2"),
                        html.Span("N/A", id="new-accuracy", className="value", style={"color": "#10b981", "fontSize": "1.2em"}),
                    ], md=3),
                ])
            ])
        ], className="mb-4"),
        
        # Record Display Area
        html.Div(id="record-display", children=[
            html.Div([
                html.Div(className="spinner"),
                html.P("Load data to view records...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        ]),
        
        # Navigation Controls (for pages of 10 records) - MOVED TO BOTTOM
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("⏮️ First Page", id="first-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("◀️ Prev", id="prev-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-start"),
                    dbc.Col([
                        html.Div([
                            html.Span("Records ", style={"fontSize": "0.9em"}),
                            html.Span(id="page-start", children="1", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span("-", style={"margin": "0 4px"}),
                            html.Span(id="page-end", children="10", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span(" of ", style={"margin": "0 8px"}),
                            html.Span(id="total-filtered", children="0", style={"fontSize": "1.2em", "fontWeight": "600"}),
                        ], className="text-center", style={"lineHeight": "38px"})
                    ], md=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Next ▶️", id="next-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("Last Page ⏭️", id="last-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-end"),
                ])
            ])
        ], className="mt-4"),
        
        # Image Modal (for expanded image view) - using shared modal from app.py with gamma slider
        # Modal removed here to use the one in app.py
        
    ], fluid=True, className="tab-content-container")


def create_accordion_view(records, page_index, image_toggle_states, audit_tags, audit_options):
    """
    Create table-based collapsible view showing up to 10 records per page
    
    Args:
        records: List of all filtered records
        page_index: Current page (0-based)
        image_toggle_states: Dict of image toggle states
        audit_tags: Dict of {txn_id: audit_value}
        audit_options: List of dropdown options for audit
        
    Returns:
        Table with collapsible rows
    """
    start_idx = page_index * 10
    end_idx = min(start_idx + 10, len(records))
    page_records = records[start_idx:end_idx]
    
    if not page_records:
        return html.Div("No records to display", className="text-center text-muted py-5")
    
    # Create table rows
    table_rows = []
    for i, record in enumerate(page_records):
        global_index = start_idx + i
        txn_id = record.get('pdd_txn_id', '')
        current_audit = audit_tags.get(txn_id, None) if audit_tags else None
        
        # Get data
        date = record.get('quote_date', 'N/A')
        cscan = record.get('cscan_answer', 'N/A')
        new_cscan = record.get('new_cscan_answer', 'N/A')
        final = record.get('final_answer', 'N/A')
        contrib_deployed = record.get('contributing_sides') or None
        contrib_new = record.get('new_contributing_sides') or None
        
        # Format contributing sides for display
        contrib_deployed_display = contrib_deployed if contrib_deployed else '-'
        contrib_new_display = contrib_new if contrib_new else '-'
        
        # Create collapsible row header with arrow on left
        row_header = html.Tr([
            html.Td(
                html.Div([
                    html.Span("▶", id=f"arrow-{global_index}", style={
                        "display": "inline-block",
                        "transition": "transform 0.3s ease",
                        "marginRight": "8px",
                        "color": "#3b82f6",
                        "fontSize": "0.8em",
                        "cursor": "pointer"
                    }),
                    html.Span(date, style={"cursor": "pointer"})
                ], id={"type": "expand-row", "index": global_index}, n_clicks=0, style={"display": "flex", "alignItems": "center"}),
                style={"cursor": "pointer", "width": "130px"}
            ),
            html.Td(cscan),
            html.Td(new_cscan if new_cscan != 'N/A' else '-'),
            html.Td(final),
            html.Td(contrib_deployed_display),
            html.Td(contrib_new_display),
        ], className="clickable-row", id=f"row-header-{global_index}")
        
        # Create full record content (hidden by default)
        # Use txn_id as the unique identifier for toggle states instead of global_index
        record_content = create_record_display_with_audit(
            record, 
            global_index,  # Still used for UI elements like expand/collapse
            txn_id,  # Use txn_id as the key for toggle states
            image_toggle_states or {}, 
            audit_options,
            current_audit
        )
        
        # Expandable row content
        row_expanded = html.Tr([
            html.Td(
                record_content,
                colSpan=6,
                style={"padding": "0", "background": "#f8fafc"}
            )
        ], id=f"row-expanded-{global_index}", style={"display": "none"}, className="expanded-row")
        
        table_rows.append(row_header)
        table_rows.append(row_expanded)
    
    # Create table with professional styling
    return html.Div([
        html.Table([
            html.Thead([
                html.Tr([
                    html.Th("Quote Date"),
                    html.Th("Deployed CScan"),
                    html.Th("New CScan"),
                    html.Th("Final Answer"),
                    html.Th("Deployed Contributing Sides"),
                    html.Th("New Contributing Sides"),
                ])
            ]),
            html.Tbody(table_rows)
        ], className="records-table")
    ], className="records-table-container", id="accordion-container")


def create_record_display_with_audit(record, current_index, record_id, image_toggle_states, audit_options, current_audit_value):
    """Create the display for a single record"""
    
    sides = ['top', 'bottom', 'right', 'left', 'back', 'front']
    
    # Parse contributing sides for highlighting
    contributing_sides_list = [s.strip().lower() for s in str(record.get('contributing_sides', '')).split(',') if s.strip()]
    new_contributing_sides_list = [s.strip().lower() for s in str(record.get('new_contributing_sides', '')).split(',') if s.strip()]
    
    # Record Header with Light Background (matching filters)
    header = dbc.Card([
        dbc.CardBody([
            html.H2("📋 Record Details", className="mb-3", style={"color": "#1e40af", "fontWeight": "600"}),
            # Row 1: Transaction and Date
            dbc.Row([
                dbc.Col([
                    html.Strong("Transaction ID: ", style={"color": "#475569"}),
                    html.Span(record.get('pdd_txn_id', 'N/A'), style={"color": "#1e293b", "fontWeight": "500"})
                ], md=6),
                dbc.Col([
                    html.Strong("Quote Date: ", style={"color": "#475569"}),
                    html.Span(record.get('quote_date', 'N/A'), style={"color": "#1e293b", "fontWeight": "500"})
                ], md=6),
            ], className="mb-3"),
            
            # Row 2: Contributing Sides
            dbc.Row([
                dbc.Col([
                    html.Strong("Contributing Sides: ", style={"color": "#475569"}),
                    html.Span(
                        record.get('contributing_sides', 'N/A'), 
                        style={
                            "color": "#dc2626",  # Red for high contrast on light
                            "fontWeight": "700",
                            "fontSize": "1.05em",
                            "backgroundColor": "#fef2f2",
                            "padding": "4px 10px",
                            "borderRadius": "4px",
                            "border": "1px solid #fecaca"
                        }
                    )
                ], md=6),
                dbc.Col([
                    html.Strong("New Contributing Sides: ", style={"color": "#475569"}),
                    html.Span(
                        record.get('new_contributing_sides', 'N/A'), 
                        style={
                            "color": "#059669",  # Green for high contrast on light
                            "fontWeight": "700",
                            "fontSize": "1.05em",
                            "backgroundColor": "#f0fdf4",
                            "padding": "4px 10px",
                            "borderRadius": "4px",
                            "border": "1px solid #bbf7d0"
                        }
                    )
                ], md=6),
            ], className="mb-3"),
            
            # Row 3: Answers
            dbc.Row([
                dbc.Col([
                    html.Strong("Deployed CScan: ", style={"color": "#475569"}),
                    dbc.Badge(
                        record.get('cscan_answer', 'N/A'), 
                        color="info", 
                        className="ms-1",
                        style={"fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
                dbc.Col([
                    html.Strong("New CScan: ", style={"color": "#475569"}),
                    dbc.Badge(
                        record.get('new_cscan_answer', 'N/A'), 
                        color="success", 
                        className="ms-1",
                        style={"fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
                dbc.Col([
                    html.Strong("Final Answer: ", style={"color": "#475569"}),
                    dbc.Badge(
                        record.get('final_answer', 'N/A'), 
                        color="warning", 
                        className="ms-1",
                        style={"fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
            ], className="mb-3"),
            
            # Row 4: QC, Auditor, and Audit Dropdown
            dbc.Row([
                dbc.Col([
                    html.Strong("QC Answer: ", style={"color": "#475569"}),
                    html.Span(record.get('qc_answer', 'N/A'), style={"color": "#1e293b", "fontWeight": "500"})
                ], md=3),
                dbc.Col([
                    html.Strong("Auditor Answer: ", style={"color": "#475569"}),
                    html.Span(record.get('auditor_answer', 'N/A'), style={"color": "#1e293b", "fontWeight": "500"})
                ], md=3),
                dbc.Col([
                    html.Div([
                        html.Strong("Audit Image: ", style={"color": "#475569", "marginRight": "10px", "whiteSpace": "nowrap"}),
                        html.Div([
                            dcc.Dropdown(
                                id={"type": "audit-dropdown", "txn_id": record.get('pdd_txn_id', '')},
                                options=audit_options,
                                value=current_audit_value,
                                placeholder="Select audit result...",
                                clearable=True,
                                style={"minWidth": "200px"}
                            )
                        ], style={"flex": "1"})
                    ], style={"display": "flex", "alignItems": "center"})
                ], md=6),
            ]),
        ], style={"padding": "1.5rem"})
    ], className="mb-3", style={
        "background": "linear-gradient(to bottom, #f8fafc, #f1f5f9)",  # Same as filters
        "boxShadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
        "border": "1px solid #e2e8f0"
    })
    
    # Images Grid
    images_grid = []
    for side in sides:
        # Check if image URL exists for this side - skip if missing
        input_image_url = record.get(f'{side}_image_url', '')
        
        # Skip this side if image URL is missing/empty/invalid
        # Check for None, empty string, whitespace-only strings, or placeholder values
        if not input_image_url:
            continue
        if isinstance(input_image_url, str):
            url_clean = input_image_url.strip().lower()
            if url_clean == '' or url_clean in ['n/a', 'na', 'null', 'none', '-']:
                continue
        
        old_score = float(record.get(f'{side}_score', 0) or 0)
        new_score_val = record.get(f'new_{side}_score')
        new_score = float(new_score_val) if new_score_val not in [None, '', 'N/A'] else None
        
        old_result_url = record.get(f'{side}_result_url', '')
        new_result_url = record.get(f'new_{side}_result_image_url', '')
        
        # Get UUIDs and request body for display
        side_uuid = record.get(f'{side}_uuid', 'N/A')
        side_request_body = record.get(f'{side}_request_body', '')
        
        # For front side, also get front_black data
        front_black_image_url = None
        front_black_uuid = None
        if side == 'front':
            front_black_image_url = record.get('front_black_image_url', '')
            front_black_uuid = record.get('front_black_uuid', '')
            # If front_black_uuid is missing or empty, try to generate from UUID pattern
            # Check if it exists in the record, otherwise use 'N/A'
            if not front_black_uuid or (isinstance(front_black_uuid, str) and front_black_uuid.strip() == ''):
                # Try to construct from other UUID columns if available
                # This is a fallback - ideally the data should have front_black_uuid from Redash
                front_black_uuid = 'N/A'
        
        has_new = new_result_url and new_score is not None
        
        # Check if this side is in contributing sides for highlighting
        is_contributing = side.lower() in contributing_sides_list
        is_new_contributing = side.lower() in new_contributing_sides_list
        
        # Get current toggle state for this side and record (always default to 'result')
        # Handle None, empty dict, or missing key cases
        # State structure: {record_id: {side: 'input'|'result'}}
        if not image_toggle_states or not isinstance(image_toggle_states, dict):
            current_image_mode = 'result'
        else:
            # Get state for this specific record using record_id (txn_id)
            record_states = image_toggle_states.get(record_id, {})
            if isinstance(record_states, dict):
                current_image_mode = record_states.get(side)
                if current_image_mode not in ['input', 'result']:
                    current_image_mode = 'result'
            else:
                current_image_mode = 'result'
        
        # Determine which URLs to display
        display_old_url = input_image_url if current_image_mode == 'input' else old_result_url
        display_new_url = input_image_url if current_image_mode == 'input' else new_result_url
        image_label = 'Input Image' if current_image_mode == 'input' else 'Result'
        
        # Special handling for front side in input mode: show both front and front_black
        show_front_black = (side == 'front' and current_image_mode == 'input' and 
                           front_black_image_url and 
                           isinstance(front_black_image_url, str) and 
                           front_black_image_url.strip() != '' and
                           front_black_image_url.strip().lower() not in ['n/a', 'na', 'null', 'none', '-'])
        
        # Professional Card Design
        card_content = []
        
        # Highlighting colors - match deployed to new score color scheme
        deployed_badge_color = "danger" if is_contributing else "success"
        new_badge_color = "danger" if is_new_contributing else "success"
        
        # Top row: Side name with professional background
        side_header = html.Div([
            html.Div([
                html.Span(
                    f"📷 {side.upper()}",
                    style={
                        "fontSize": "1.15em",
                        "fontWeight": "700",
                        "color": "#ffffff",
                        "letterSpacing": "0.5px"
                    }
                )
            ], className="text-center py-2")
        ], style={
            "background": "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)",
            "borderTopLeftRadius": "8px",
            "borderTopRightRadius": "8px"
        })
        card_content.append(side_header)
        
        # Second row: Toggle button and scores
        # Button shows what it will switch TO, with clear active/inactive styling
        is_showing_result = (current_image_mode == 'result')
        
        control_row = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Span(
                        f"🔄 {'Input' if is_showing_result else 'Result'}",
                        id={"type": "image-toggle-btn", "side": side, "record_id": record_id},
                        n_clicks=0,
                        className="badge w-100 d-block text-center",
                        style={
                            "background": "#1e40af" if is_showing_result else "#f8fafc",
                            "color": "#ffffff" if is_showing_result else "#475569",
                            "border": f"2px solid {'#1e40af' if is_showing_result else '#cbd5e1'}",
                            "fontWeight": "600",
                            "fontSize": "0.85em",
                            "padding": "6px",
                            "cursor": "pointer",
                            "userSelect": "none"
                        },
                        **{"data-stop-propagation": "true"}
                    )
                ], width=4),
                dbc.Col([
                    dbc.Badge(
                        f"Deployed: {old_score:.2f}", 
                        color=deployed_badge_color, 
                        className="w-100",
                        style={
                            "fontSize": "0.85em",
                            "fontWeight": "bold" if is_contributing else "600",
                            "padding": "6px"
                        }
                    )
                ], width=4),
                dbc.Col([
                    dbc.Badge(
                        f"New: {new_score:.2f}" if has_new else "N/A", 
                        color=new_badge_color if has_new else "secondary",
                        className="w-100",
                        style={
                            "fontSize": "0.85em",
                            "fontWeight": "bold" if (has_new and is_new_contributing) else "600",
                            "padding": "6px"
                        }
                    )
                ], width=4),
            ], className="g-2")
        ], style={"padding": "12px", "background": "#f8fafc", "borderBottom": "1px solid #e2e8f0"})
        card_content.append(control_row)
        
        # Images - Auto show side-by-side if both exist, else single
        # Special case: Front side in input mode with front_black
        if show_front_black:
            # Show front and front_black side by side in input mode
            image_body = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            "Front Input", 
                            className="text-center mb-2", 
                            style={
                                "color": "#1e40af", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_old_url if display_old_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "old", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if display_old_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                        ])
                    ], md=6),
                    dbc.Col([
                        html.Div(
                            "Front Black Input", 
                            className="text-center mb-2", 
                            style={
                                "color": "#059669", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=front_black_image_url if front_black_image_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": "front_black", "version": "old", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if front_black_image_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {front_black_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                        ])
                    ], md=6),
                ])
            ], style={"padding": "1.5rem", "background": "#ffffff", "minHeight": "650px", "overflow": "hidden"})
        elif has_new:
            # Side by side comparison (both deployed and new exist)
            image_body = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            f"Deployed {image_label}", 
                            className="text-center mb-2", 
                            style={
                                "color": "#1e40af", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_old_url if display_old_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "old", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if display_old_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                            *([dbc.Button(
                                "📋 Copy Request Body",
                                id={"type": "copy-request-body-btn", "side": side, "record_id": record_id},
                                size="sm",
                                color="secondary",
                                className="mt-1",
                                style={"fontSize": "0.7em", "width": "100%"}
                            )] if side_request_body else [])
                        ])
                    ], md=6),
                    dbc.Col([
                        html.Div(
                            f"New {image_label}", 
                            className="text-center mb-2", 
                            style={
                                "color": "#059669", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_new_url if display_new_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "new", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if display_new_url else html.Div(
                                f"No new {image_label.lower()}", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                            *([dbc.Button(
                                "📋 Copy Request Body",
                                id={"type": "copy-request-body-btn", "side": side, "record_id": record_id},
                                size="sm",
                                color="secondary",
                                className="mt-1",
                                style={"fontSize": "0.7em", "width": "100%"}
                            )] if side_request_body else [])
                        ])
                    ], md=6),
                ])
            ], style={"padding": "1.5rem", "background": "#ffffff", "minHeight": "650px", "overflow": "hidden"})
        elif show_front_black and not has_new:
            # Single view with front_black (input mode, no new model)
            image_body = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div(
                            "Front Input", 
                            className="text-center mb-2", 
                            style={
                                "color": "#1e40af", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_old_url if display_old_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "single", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if display_old_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                        ])
                    ], md=6),
                    dbc.Col([
                        html.Div(
                            "Front Black Input", 
                            className="text-center mb-2", 
                            style={
                                "color": "#059669", 
                                "fontSize": "0.9em", 
                                "fontWeight": "700",
                                "textTransform": "uppercase",
                                "letterSpacing": "0.5px"
                            }
                        ),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=front_black_image_url if front_black_image_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxWidth": "100%",
                                        "maxHeight": "600px",
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": "front_black", "version": "single", "record_id": record_id},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                            ) if front_black_image_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "300px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {front_black_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                        ])
                    ], md=6),
                ])
            ], style={"padding": "1.5rem", "background": "#ffffff", "minHeight": "650px", "overflow": "hidden"})
        else:
            # Single image view (only deployed exists) - match dual view sizing
            image_body = html.Div([
                html.Div(
                    f"Deployed {image_label}", 
                    className="text-center mb-2", 
                    style={
                        "color": "#1e40af", 
                        "fontSize": "0.9em", 
                        "fontWeight": "700",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.5px"
                    }
                ),
                html.Div([
                    html.Div(
                        html.Img(
                            src=display_old_url if display_old_url else "",
                            style={
                                "width": "100%", 
                                "maxWidth": "100%",
                                "maxHeight": "600px",  # Match dual view height
                                "objectFit": "contain",
                                "borderRadius": "8px",
                                "border": "1px solid #e2e8f0"
                            },
                            className="hover-shadow"
                        ),
                        id={"type": "image-clickable", "side": side, "version": "single", "record_id": record_id},
                        n_clicks=0,
                        style={"cursor": "pointer", "background": "#ffffff", "width": "100%", "maxWidth": "100%"}
                    ) if display_old_url else html.Div(
                        "No image", 
                        className="text-muted text-center p-4", 
                        style={
                            "border": "2px dashed #cbd5e1",
                            "borderRadius": "8px",
                            "minHeight": "300px",  # Match dual view placeholder height
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "background": "#f8fafc"
                        }
                    ),
                    html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"}),
                    *([dbc.Button(
                        "📋 Copy Request Body",
                        id={"type": "copy-request-body-btn", "side": side, "record_id": record_id},
                        size="sm",
                        color="secondary",
                        className="mt-1",
                        style={"fontSize": "0.7em", "width": "100%"}
                    )] if side_request_body else [])
                ])
            ], style={"padding": "1.5rem", "background": "#ffffff", "minHeight": "650px", "overflow": "hidden"})
        
        card_content.append(image_body)
        
        # Create professional card with enhanced styling
        image_card = dbc.Col([
            dbc.Card(
                card_content,
                className="mb-4",
                style={
                    "height": "100%",
                    "borderRadius": "8px",
                    "border": "1px solid #e2e8f0",
                    "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.06), 0 4px 8px rgba(0, 0, 0, 0.04)",
                    "transition": "all 0.2s ease",
                    "overflow": "hidden"
                }
            )
        ], md=6, lg=4)
        
        images_grid.append(image_card)
    
    # Combine all elements - directly show images below details
    return html.Div([
        header,
        dbc.Row(images_grid, className="g-4 mt-2")
    ])


def register_image_viewer_callbacks(app):
    """Register callbacks for image viewer tab"""
    
    # Reset filters and state when switching to viewer tab
    @app.callback(
        [Output("filtered-data-store", "data", allow_duplicate=True),
         Output("current-index-store", "data", allow_duplicate=True),
         Output("cscan-answer-filter", "value", allow_duplicate=True),
         Output("new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("final-answer-filter", "value", allow_duplicate=True),
         Output("contributing-side-filter", "value", allow_duplicate=True),
         Output("new-contributing-side-filter", "value", allow_duplicate=True),
         Output("deployed-side-score-filter", "value", allow_duplicate=True),
         Output("deployed-score-range-slider", "value", allow_duplicate=True),
         Output("new-side-score-filter", "value", allow_duplicate=True),
         Output("new-score-range-slider", "value", allow_duplicate=True),
         Output("image-toggle-state-store", "data", allow_duplicate=True),
         Output("expanded-rows-store", "data", allow_duplicate=True)],
        Input("main-tabs", "active_tab"),
        [State("data-store", "data")],
        prevent_initial_call=True
    )
    def reset_viewer_on_tab_switch(active_tab, data):
        """Reset all filters and state when switching to viewer tab"""
        if active_tab == "viewer":
            # Ensure data is in the correct format for filtered-data-store
            if data and isinstance(data, dict):
                filtered_data = data  # Use data as-is (already in correct format)
            elif data and isinstance(data, list):
                filtered_data = {"data": data}  # Wrap list in dict format
            else:
                filtered_data = {}
            
            # Reset all filters to defaults and reset filtered data to original data
            return (
                filtered_data,  # Reset filtered data to original data
                0,  # Reset page to 0
                [],  # Reset cscan-answer-filter
                [],  # Reset new-cscan-answer-filter
                [],  # Reset final-answer-filter
                [],  # Reset contributing-side-filter
                [],  # Reset new-contributing-side-filter
                [],  # Reset deployed-side-score-filter
                [0, 100],  # Reset deployed-score-range-slider
                [],  # Reset new-side-score-filter
                [0, 100],  # Reset new-score-range-slider
                {},  # Reset image-toggle-state-store
                {}  # Reset expanded-rows-store
            )
        
        # Don't change anything if not switching to viewer tab
        from dash import no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Sync matrix filter stores to dropdown values when confusion matrix is clicked
    @app.callback(
        [Output("cscan-answer-filter", "value", allow_duplicate=True),
         Output("new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("final-answer-filter", "value", allow_duplicate=True)],
        [Input("matrix-filter-cscan", "data"),
         Input("matrix-filter-new-cscan", "data"),
         Input("matrix-filter-final", "data")],
        prevent_initial_call=True
    )
    def sync_matrix_filters_to_dropdowns(cscan_filter, new_cscan_filter, final_filter):
        """Sync filter values from matrix click stores to dropdown components"""
        # Only sync if values are not empty (matrix click happened)
        if cscan_filter or new_cscan_filter or final_filter:
            return cscan_filter or [], new_cscan_filter or [], final_filter or []
        from dash import no_update
        return no_update, no_update, no_update
    
    # Populate filter dropdowns when data is loaded
    @app.callback(
        [Output("cscan-answer-filter", "options"),
         Output("new-cscan-answer-filter", "options"),
         Output("final-answer-filter", "options")],
        Input("data-store", "data")
    )
    def populate_filter_dropdowns(data):
        """Populate filter dropdowns when data is loaded"""
        
        if not data or not isinstance(data, dict):
            return [], [], []
        
        # Extract data records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return [], [], []
        
        # Collect unique values
        cscan_answers = set()
        new_cscan_answers = set()
        final_answers = set()
        
        for record in records:
            if record.get('cscan_answer'):
                cscan_answers.add(str(record['cscan_answer']))
            if record.get('new_cscan_answer'):
                new_cscan_answers.add(str(record['new_cscan_answer']))
            if record.get('final_answer'):
                final_answers.add(str(record['final_answer']))
        
        # Create options without "All" option (empty list = all selected)
        cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(cscan_answers)]
        new_cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(new_cscan_answers)]
        final_options = [{"label": str(v), "value": str(v)} for v in sorted(final_answers)]
        
        return cscan_options, new_cscan_options, final_options
    
    # Apply filters and update filtered data (returns page 0)
    @app.callback(
        [Output("filtered-data-store", "data"),
         Output("current-index-store", "data"),  # This now stores page number
         Output("cscan-answer-filter", "value", allow_duplicate=True),
         Output("new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("final-answer-filter", "value", allow_duplicate=True),
         Output("contributing-side-filter", "value", allow_duplicate=True),
         Output("new-contributing-side-filter", "value", allow_duplicate=True),
         Output("deployed-side-score-filter", "value", allow_duplicate=True),
         Output("deployed-score-range-slider", "value", allow_duplicate=True),
         Output("new-side-score-filter", "value", allow_duplicate=True),
         Output("new-score-range-slider", "value", allow_duplicate=True)],
        [Input("apply-filters-btn", "n_clicks"),
         Input("reset-filters-btn", "n_clicks"),
         Input("matrix-click-trigger", "data")],  # Also triggered by confusion matrix clicks
        [State("data-store", "data"),
         State("main-tabs", "active_tab"),  # Check which tab is active
         State("cscan-answer-filter", "value"),
         State("new-cscan-answer-filter", "value"),
         State("final-answer-filter", "value"),
         State("contributing-side-filter", "value"),
         State("new-contributing-side-filter", "value"),
         State("deployed-side-score-filter", "value"),
         State("deployed-score-range-slider", "value"),
         State("new-side-score-filter", "value"),
         State("new-score-range-slider", "value"),
         State("matrix-filter-cscan", "data"),  # Filter values from matrix click
         State("matrix-filter-new-cscan", "data"),  # Filter values from matrix click
         State("matrix-filter-final", "data")],  # Filter values from matrix click
        prevent_initial_call=True  # Prevent running on initial load when component doesn't exist
    )
    def apply_filters(apply_clicks, reset_clicks, matrix_trigger, data, active_tab, cscan_filter, new_cscan_filter, final_filter, side_filter, new_side_filter, deployed_score_side_filter, deployed_score_range, new_score_side_filter, new_score_range, matrix_cscan_filter, matrix_new_cscan_filter, matrix_final_filter):
        ctx = callback_context
        if not ctx.triggered:
            # Should not happen with prevent_initial_call=True, but safety check
            from dash import no_update
            return data if data else {}, 0, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        # Only process if we're on the viewer tab (ignore matrix clicks when on celldetail tab)
        if active_tab != "viewer":
            from dash import no_update
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset filters - clear all dropdown values and reset data
        if trigger_id == "reset-filters-btn":
            return data, 0, [], [], [], [], [], [], [0, 100], [], [0, 100]  # 11 outputs: data, page, 5 filters, deployed_side_score_filter, deployed_score_range, new_side_score_filter, new_score_range
        
        # If triggered by matrix click, use matrix filter stores instead of dropdown values
        if trigger_id == "matrix-click-trigger" and matrix_trigger and matrix_trigger > 0:
            # Use matrix filter stores (these are already normalized)
            cscan_filter = matrix_cscan_filter if matrix_cscan_filter else []
            new_cscan_filter = matrix_new_cscan_filter if matrix_new_cscan_filter else []
            final_filter = matrix_final_filter if matrix_final_filter else []
            # Contributing side filters not set from matrix clicks
            side_filter = []
            new_side_filter = []
            # Score filters not set from matrix clicks
            deployed_score_side_filter = []
            deployed_score_range = [0, 100]
            new_score_side_filter = []
            new_score_range = [0, 100]
        
        # Apply filters
        if not data or not isinstance(data, dict):
            from dash import no_update
            return {}, 0, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            from dash import no_update
            return {}, 0, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        # Filter records
        filtered = records
        
        # Normalize function for comparison (same as confusion matrix)
        def normalize_for_comparison(value):
            """Normalize value for comparison (lowercase, strip)"""
            if not value:
                return None
            return str(value).lower().strip()
        
        # Handle CScan Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if cscan_filter and len(cscan_filter) > 0:
            # Normalize filter values
            normalized_cscan_filter = [normalize_for_comparison(v) for v in cscan_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('cscan_answer', '')) in normalized_cscan_filter
            ]
        
        # Handle New CScan Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if new_cscan_filter and len(new_cscan_filter) > 0:
            # Normalize filter values
            normalized_new_cscan_filter = [normalize_for_comparison(v) for v in new_cscan_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('new_cscan_answer', '')) in normalized_new_cscan_filter
            ]
        
        # Handle Final Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if final_filter and len(final_filter) > 0:
            # Normalize filter values
            normalized_final_filter = [normalize_for_comparison(v) for v in final_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('final_answer', '')) in normalized_final_filter
            ]
        
        # Handle multi-select for deployed contributing sides
        # Empty = all selected (filter off), non-empty = apply filter
        if side_filter and len(side_filter) > 0:
            def matches_side_filter(record):
                contributing_sides = str(record.get('contributing_sides', '')).lower()
                # Check for blank
                if '_blank_' in side_filter:
                    if not contributing_sides or contributing_sides.strip() == '':
                        return True
                # Check for any selected side
                return any(side in contributing_sides for side in side_filter if side != '_blank_')
            
            filtered = [r for r in filtered if matches_side_filter(r)]
        # If empty list, don't filter (all selected by default)
        
        # Handle multi-select for new contributing sides
        # Empty = all selected (filter off), non-empty = apply filter
        if new_side_filter and len(new_side_filter) > 0:
            def matches_new_side_filter(record):
                new_contributing_sides = str(record.get('new_contributing_sides', '')).lower()
                # Check for blank
                if '_blank_' in new_side_filter:
                    if not new_contributing_sides or new_contributing_sides.strip() == '':
                        return True
                # Check for any selected side
                return any(side in new_contributing_sides for side in new_side_filter if side != '_blank_')
            
            filtered = [r for r in filtered if matches_new_side_filter(r)]
        # If empty list, don't filter (all selected by default)
        
        # Handle deployed side score filter
        # Filter applies only if range is NOT default [0, 100] OR if specific sides are selected
        # This prevents filtering out all records when using default range
        if deployed_score_range and isinstance(deployed_score_range, list) and len(deployed_score_range) == 2:
            score_min, score_max = deployed_score_range[0], deployed_score_range[1]
            # Only apply filter if range is not default [0, 100] OR if specific sides are selected
            is_default_range = score_min == 0 and score_max == 100
            has_side_filter = deployed_score_side_filter and len(deployed_score_side_filter) > 0
            
            if not is_default_range or has_side_filter:
                def matches_deployed_score_filter(record):
                    # Determine which sides to check
                    sides_to_check = ['top', 'bottom', 'left', 'right', 'back', 'front']
                    if deployed_score_side_filter and len(deployed_score_side_filter) > 0:
                        sides_to_check = deployed_score_side_filter
                    
                    # Check if any of the selected sides has a deployed score within the range
                    for side in sides_to_check:
                        score_col = f"{side}_score"
                        if score_col in record:
                            score_val = record[score_col]
                            # Handle None, NaN, or empty values
                            if score_val is not None and score_val != '':
                                try:
                                    score_float = float(score_val)
                                    # Check if score is within range (inclusive)
                                    if score_min <= score_float <= score_max:
                                        return True
                                except (ValueError, TypeError):
                                    continue
                    return False
                
                filtered = [r for r in filtered if matches_deployed_score_filter(r)]
        
        # Handle new side score filter
        # Filter applies only if range is NOT default [0, 100] OR if specific sides are selected
        # Also check if new model data exists in the records (has new_{side}_score columns)
        if new_score_range and isinstance(new_score_range, list) and len(new_score_range) == 2:
            score_min, score_max = new_score_range[0], new_score_range[1]
            # Only apply filter if range is not default [0, 100] OR if specific sides are selected
            is_default_range = score_min == 0 and score_max == 100
            has_side_filter = new_score_side_filter and len(new_score_side_filter) > 0
            
            # Check if any record has new model score columns (to determine if new model data exists)
            has_new_model_data = False
            if filtered:
                sample_record = filtered[0]
                for side in ['top', 'bottom', 'left', 'right', 'back', 'front']:
                    if f"new_{side}_score" in sample_record:
                        has_new_model_data = True
                        break
            
            # Only apply filter if:
            # 1. Range is not default [0, 100] OR specific sides are selected
            # 2. AND new model data exists in the records
            if (not is_default_range or has_side_filter) and has_new_model_data:
                def matches_new_score_filter(record):
                    # Determine which sides to check
                    sides_to_check = ['top', 'bottom', 'left', 'right', 'back', 'front']
                    if new_score_side_filter and len(new_score_side_filter) > 0:
                        sides_to_check = new_score_side_filter
                    
                    # Check if any of the selected sides has a new score within the range
                    for side in sides_to_check:
                        score_col = f"new_{side}_score"
                        if score_col in record:
                            score_val = record[score_col]
                            # Handle None, NaN, or empty values
                            if score_val is not None and score_val != '':
                                try:
                                    score_float = float(score_val)
                                    # Check if score is within range (inclusive)
                                    if score_min <= score_float <= score_max:
                                        return True
                                except (ValueError, TypeError):
                                    continue
                    return False
                
                filtered = [r for r in filtered if matches_new_score_filter(r)]
        
        # Return filtered data in same format as input
        if "data" in data:
            filtered_data = {
                "data": filtered,
                "columns": data.get("columns", []),
                "source": data.get("source", ""),
                "folder_name": data.get("folder_name", "")
            }
        else:
            filtered_data = filtered
        
        # Return filtered data, page 0, and no_update for dropdowns (they stay as user set them)
        # 11 outputs: filtered_data, page, cscan_filter, new_cscan_filter, final_filter, side_filter, new_side_filter, deployed_side_score_filter, deployed_score_range, new_side_score_filter, new_score_range
        from dash import no_update
        return filtered_data, 0, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Update stats and record display
    @app.callback(
        [Output("total-records", "children"),
         Output("filtered-records", "children"),
         Output("current-index-display", "children"),
         Output("page-start", "children"),
         Output("page-end", "children"),
         Output("total-filtered", "children"),
         Output("old-accuracy", "children"),
         Output("new-accuracy", "children"),
         Output("record-display", "children")],
        [Input("filtered-data-store", "data"),
         Input("current-index-store", "data"),  # Now page number
         Input("image-toggle-state-store", "data"),
         Input("audit-tags-store", "data")],
        [State("data-store", "data"),
         State("cscan-answer-filter", "options")],  # For audit dropdown options
        prevent_initial_call=True  # Prevent running when Image Viewer tab isn't rendered
    )
    def update_display(filtered_data, current_page, image_toggle_states, audit_tags, total_data, audit_options):
        # Get total records count
        if total_data and isinstance(total_data, dict) and "data" in total_data:
            total_count = len(total_data["data"])
        elif total_data and isinstance(total_data, list):
            total_count = len(total_data)
        else:
            total_count = 0
        
        # Get filtered records
        if not filtered_data or not isinstance(filtered_data, dict):
            return (str(total_count), "0", "0", "0", "0", "0", "N/A", "N/A", 
                    html.Div("No data loaded. Please load a CSV file.", className="text-center text-muted py-5"))
        
        if "data" in filtered_data:
            records = filtered_data["data"]
        else:
            records = filtered_data if isinstance(filtered_data, list) else []
        
        filtered_count = len(records)
        
        if filtered_count == 0:
            return (str(total_count), "0", "0", "1", "0", "0", "N/A", "N/A",
                    html.Div([
                        html.H3("No records match your filters", className="text-center text-muted"),
                        html.P("Try adjusting your filter criteria", className="text-center text-muted")
                    ], className="py-5"))
        
        # Ensure current_page is within bounds
        total_pages = (filtered_count + 9) // 10  # Ceiling division
        if current_page >= total_pages:
            current_page = total_pages - 1
        if current_page < 0:
            current_page = 0
        
        # Calculate page boundaries
        start_idx = current_page * 10
        end_idx = min(start_idx + 10, filtered_count)
        
        # Calculate accuracies
        correct_old = sum(1 for r in records if str(r.get('cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        correct_new = sum(1 for r in records if str(r.get('new_cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        
        old_acc = f"{(correct_old / filtered_count * 100):.2f}%" if filtered_count > 0 else "N/A"
        new_acc = f"{(correct_new / filtered_count * 100):.2f}%" if filtered_count > 0 else "N/A"
        
        # Ensure image toggle states structure is valid
        # State structure: {record_index: {side: 'input'|'result'}}
        # No need to initialize all records - they'll default to 'result' when accessed
        if not image_toggle_states or not isinstance(image_toggle_states, dict):
            image_toggle_states = {}
        
        # Create accordion view with 10 records
        accordion_display = create_accordion_view(
            records,
            current_page,
            image_toggle_states,
            audit_tags or {},
            audit_options or []
        )
        
        return (
            str(total_count),
            str(filtered_count),
            str(start_idx + 1),  # current-index-display (for compatibility)
            str(start_idx + 1),  # page-start
            str(end_idx),  # page-end
            str(filtered_count),  # total-filtered
            old_acc,
            new_acc,
            accordion_display
        )
    
    # Navigation buttons (for pages)
    @app.callback(
        Output("current-index-store", "data", allow_duplicate=True),
        [Input("first-btn", "n_clicks"),
         Input("prev-btn", "n_clicks"),
         Input("next-btn", "n_clicks"),
         Input("last-btn", "n_clicks")],
        [State("filtered-data-store", "data"),
         State("current-index-store", "data")],  # Now page number
        prevent_initial_call=True
    )
    def navigate_records(first_clicks, prev_clicks, next_clicks, last_clicks, filtered_data, current_page):
        ctx = callback_context
        if not ctx.triggered:
            return current_page or 0
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Get filtered count
        if not filtered_data or not isinstance(filtered_data, dict):
            return 0
        
        if "data" in filtered_data:
            records = filtered_data["data"]
        else:
            records = filtered_data if isinstance(filtered_data, list) else []
        
        filtered_count = len(records)
        if filtered_count == 0:
            return 0
        
        # Calculate total pages
        total_pages = (filtered_count + 9) // 10  # Ceiling division
        
        # Navigate pages
        if trigger_id == "first-btn":
            return 0
        elif trigger_id == "prev-btn":
            return max(0, current_page - 1)
        elif trigger_id == "next-btn":
            return min(total_pages - 1, current_page + 1)
        elif trigger_id == "last-btn":
            return total_pages - 1
        
        return current_page or 0
    
    # Update image toggle state store when buttons are clicked
    @app.callback(
        Output("image-toggle-state-store", "data", allow_duplicate=True),
        Input({"type": "image-toggle-btn", "side": ALL, "record_id": ALL}, "n_clicks"),
        State("image-toggle-state-store", "data"),
        prevent_initial_call=True
    )
    def update_image_toggle_state(n_clicks_list, current_states):
        ctx = callback_context
        if not ctx.triggered:
            return current_states or {}
        
        trigger = ctx.triggered[0]['prop_id']
        
        # Initialize current_states if needed
        if not current_states or not isinstance(current_states, dict):
            current_states = {}
        
        if 'image-toggle-btn' in trigger:
            import json
            try:
                trigger_dict = json.loads(trigger.split('.')[0])
                clicked_side = trigger_dict.get('side')
                record_id = trigger_dict.get('record_id')
                
                if clicked_side and record_id is not None:
                    # Get or create state for this record using record_id (txn_id)
                    if record_id not in current_states:
                        current_states[record_id] = {}
                    
                    record_state = current_states[record_id]
                    if not isinstance(record_state, dict):
                        record_state = {}
                        current_states[record_id] = record_state
                    
                    # Toggle the state for this specific record and side
                    current_state = record_state.get(clicked_side, 'result')
                    new_state = 'input' if current_state == 'result' else 'result'
                    record_state[clicked_side] = new_state
            except Exception as e:
                import traceback
                print(f"❌ Error updating toggle state: {e}")
                print(traceback.format_exc())
        
        return current_states
    
    # Modal for full image view - works for both Image Viewer and Cell Details tabs
    @app.callback(
        [Output("image-modal", "is_open"),
         Output("modal-image", "src")],
        [Input({"type": "image-clickable", "side": ALL, "version": ALL, "record_id": ALL}, "n_clicks"),
         Input("close-modal", "n_clicks")],
        [State("filtered-data-store", "data"),  # Image viewer data
         State("cell-details-filtered-data-store", "data"),  # Cell details data
         State("tweaker-changed-records-store", "data"),  # Tweaker data
         State("current-index-store", "data"),  # This is now page number (image viewer)
         State("cell-details-current-page-store", "data"),  # Cell details page
         State("tweaker-current-page-store", "data"),  # Tweaker page
         State("image-toggle-state-store", "data"),
         State("tweaker-image-toggle-state-store", "data"),  # Tweaker image toggle states
         State("image-modal", "is_open"),
         State("main-tabs", "active_tab")],  # Check which tab is active
        prevent_initial_call=True
    )
    def toggle_image_modal(n_clicks_list, close_clicks, filtered_data, cell_details_filtered_data, tweaker_changed_records_data, current_page, cell_details_page, tweaker_page, image_states, tweaker_image_states, is_open, active_tab):
        ctx = callback_context
        if not ctx.triggered:
            return False, ""
        
        trigger = ctx.triggered[0]['prop_id']
        trigger_value = ctx.triggered[0].get('value')
        
        # Don't open modal if this is just component creation (value will be None or 0)
        if trigger_value is None or trigger_value == 0:
            from dash import no_update
            return no_update, no_update
        
        # Close modal
        if "close-modal" in trigger:
            return False, ""
        
        # Open modal with clicked image (only if actually clicked, not just created)
        if "image-clickable" in trigger and trigger_value:
            import json
            try:
                trigger_dict = json.loads(trigger.split('.')[0])
                side = trigger_dict.get('side')
                version = trigger_dict.get('version')
                record_id = trigger_dict.get('record_id')
                
                # Try to get records based on active tab, then fallback
                records = None
                
                # Prioritize based on active tab
                if active_tab == "viewer":
                    # Image viewer tab - use filtered_data first
                    if filtered_data:
                        if isinstance(filtered_data, dict):
                            if "data" in filtered_data and filtered_data["data"]:
                                records = filtered_data["data"]
                        elif isinstance(filtered_data, list) and len(filtered_data) > 0:
                            records = filtered_data
                    # Fallback to cell details if image viewer has no data
                    if not records and cell_details_filtered_data:
                        if isinstance(cell_details_filtered_data, dict):
                            if "data" in cell_details_filtered_data and cell_details_filtered_data["data"]:
                                records = cell_details_filtered_data["data"]
                        elif isinstance(cell_details_filtered_data, list) and len(cell_details_filtered_data) > 0:
                            records = cell_details_filtered_data
                elif active_tab == "celldetail":
                    # Cell details tab - use cell_details_filtered_data first
                    if cell_details_filtered_data:
                        if isinstance(cell_details_filtered_data, dict):
                            if "data" in cell_details_filtered_data and cell_details_filtered_data["data"]:
                                records = cell_details_filtered_data["data"]
                        elif isinstance(cell_details_filtered_data, list) and len(cell_details_filtered_data) > 0:
                            records = cell_details_filtered_data
                    # Fallback to image viewer if cell details has no data
                    if not records and filtered_data:
                        if isinstance(filtered_data, dict):
                            if "data" in filtered_data and filtered_data["data"]:
                                records = filtered_data["data"]
                        elif isinstance(filtered_data, list) and len(filtered_data) > 0:
                            records = filtered_data
                elif active_tab == "tweaker":
                    # Tweaker tab - use tweaker_changed_records_data
                    if tweaker_changed_records_data:
                        if isinstance(tweaker_changed_records_data, dict):
                            # Get filtered records if available, otherwise all changed records
                            records = tweaker_changed_records_data.get("filtered", [])
                            if not records:
                                records = tweaker_changed_records_data.get("data", [])
                        elif isinstance(tweaker_changed_records_data, list) and len(tweaker_changed_records_data) > 0:
                            records = tweaker_changed_records_data
                else:
                    # Unknown tab - try all (including tweaker as fallback)
                    if filtered_data:
                        if isinstance(filtered_data, dict):
                            if "data" in filtered_data and filtered_data["data"]:
                                records = filtered_data["data"]
                        elif isinstance(filtered_data, list) and len(filtered_data) > 0:
                            records = filtered_data
                    if not records and cell_details_filtered_data:
                        if isinstance(cell_details_filtered_data, dict):
                            if "data" in cell_details_filtered_data and cell_details_filtered_data["data"]:
                                records = cell_details_filtered_data["data"]
                        elif isinstance(cell_details_filtered_data, list) and len(cell_details_filtered_data) > 0:
                            records = cell_details_filtered_data
                    if not records and tweaker_changed_records_data:
                        if isinstance(tweaker_changed_records_data, dict):
                            records = tweaker_changed_records_data.get("filtered", [])
                            if not records:
                                records = tweaker_changed_records_data.get("data", [])
                        elif isinstance(tweaker_changed_records_data, list) and len(tweaker_changed_records_data) > 0:
                            records = tweaker_changed_records_data
                
                if not records:
                    return False, ""
                
                # Find record by matching pdd_txn_id
                record = None
                for r in records:
                    if str(r.get('pdd_txn_id', '')) == str(record_id):
                        record = r
                        break
                
                if record is None:
                    return False, ""
                
                # Get the correct URL - use record-specific state
                # State structure: {record_id: {side: 'input'|'result'}}
                # For front_black, check the toggle state for 'front' since they share the same toggle
                state_side = 'front' if side == 'front_black' else side
                
                # Check tweaker image states if on tweaker tab, otherwise use regular image states
                if active_tab == "tweaker" and tweaker_image_states and isinstance(tweaker_image_states, dict):
                    record_states = tweaker_image_states.get(record_id, {})
                    if isinstance(record_states, dict):
                        current_mode = record_states.get(state_side, 'result')
                    else:
                        current_mode = 'result'
                elif image_states and isinstance(image_states, dict):
                    record_states = image_states.get(record_id, {})
                    if isinstance(record_states, dict):
                        current_mode = record_states.get(state_side, 'result')
                    else:
                        current_mode = 'result'
                else:
                    current_mode = 'result'
                
                if current_mode == 'input':
                    # Handle front_black side
                    if side == 'front_black':
                        url = record.get('front_black_image_url', '')
                    else:
                        url = record.get(f'{side}_image_url', '')
                else:
                    if version == 'new':
                        url = record.get(f'new_{side}_result_image_url', '') or record.get(f'{side}_result_url', '')
                    elif version == 'single':
                        url = record.get(f'{side}_result_url', '')
                    else:  # version == 'old'
                        url = record.get(f'{side}_result_url', '')
                
                if url:
                    return True, url
                else:
                    return False, ""
            except Exception as e:
                import traceback
                print(f"❌ Error in toggle_image_modal: {e}")
                print(traceback.format_exc())
                return False, ""
        
        return False, ""
    
    # Store expanded row states to preserve them across re-renders
    @app.callback(
        Output("expanded-rows-store", "data", allow_duplicate=True),
        Input({"type": "expand-row", "index": ALL}, "n_clicks"),
        State("expanded-rows-store", "data"),
        prevent_initial_call=True
    )
    def update_expanded_rows(n_clicks_list, current_expanded):
        # This callback is kept for tracking, but rows always start collapsed
        # No need to preserve state - rows are recreated with display: none
        from dash import callback_context
        ctx = callback_context
        if not ctx.triggered:
            return {}
        
        trigger = ctx.triggered[0]['prop_id']
        if 'expand-row' not in trigger:
            return {}
        
        # Don't preserve expanded state - rows always start collapsed when DOM is rebuilt
        # This ensures no auto-expansion happens
        return {}
    
    # Collapse rows only when filtering/pagination changes (not when image toggle changes)
    # This ensures rows stay expanded when toggling images
    app.clientside_callback(
        """
        function(filtered_data, current_page) {
            // Clear preserved expanded rows when filtering/pagination changes
            if (window.preservedExpandedRows) {
                window.preservedExpandedRows.clear();
            }
            
            // Only collapse rows when filtered_data or current_page changes (filtering/pagination)
            // NOT when image-toggle-state-store changes
            setTimeout(function() {
                const allExpandedRows = document.querySelectorAll('[id^="row-expanded-"]');
                const allArrows = document.querySelectorAll('[id^="arrow-"]');
                
                // Collapse all rows when filtering/pagination changes
                allExpandedRows.forEach(function(row) {
                    if (row) {
                        row.style.display = 'none';
                    }
                });
                allArrows.forEach(function(arrow) {
                    if (arrow) {
                        arrow.style.transform = 'rotate(0deg)';
                    }
                });
            }, 100);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("audit-tags-store", "data", allow_duplicate=True),
        [Input("filtered-data-store", "data"),
         Input("current-index-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    
    # Preserve expanded rows when record-display is re-rendered due to toggle state changes
    # This prevents rows from collapsing when toggle buttons are clicked
    app.clientside_callback(
        """
        function(record_display, image_toggle_states) {
            // Initialize preserved rows set if it doesn't exist
            if (!window.preservedExpandedRows) {
                window.preservedExpandedRows = new Set();
            }
            
            // Before DOM changes, capture currently expanded rows
            const allExpandedRows = document.querySelectorAll('[id^="row-expanded-"]');
            allExpandedRows.forEach(function(row) {
                if (row && row.style.display === 'table-row') {
                    const match = row.id.match(/row-expanded-(\\d+)/);
                    if (match) {
                        const index = match[1];
                        window.preservedExpandedRows.add(index);
                    }
                }
            });
            
            // After a short delay (to allow DOM to update), restore expanded rows
            setTimeout(function() {
                if (window.preservedExpandedRows && window.preservedExpandedRows.size > 0) {
                    window.preservedExpandedRows.forEach(function(index) {
                        const expandedRow = document.getElementById('row-expanded-' + index);
                        const arrow = document.getElementById('arrow-' + index);
                        if (expandedRow && arrow) {
                            expandedRow.style.display = 'table-row';
                            arrow.style.transform = 'rotate(90deg)';
                        }
                    });
                }
            }, 50);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("audit-tags-store", "data", allow_duplicate=True),
        [Input("record-display", "children"),
         Input("image-toggle-state-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    
    # Set up event delegation to prevent toggle button clicks from collapsing rows
    # This runs once on initial load
    app.clientside_callback(
        """
        function(record_display) {
            // Set up event delegation to stop propagation on toggle button clicks
            // Don't clone/replace buttons - that breaks Dash's event tracking
            if (!window.toggleButtonPropagationHandler) {
                window.toggleButtonPropagationHandler = function(e) {
                    // Check if click is on or inside a toggle button
                    const target = e.target;
                    const toggleBtn = target.closest ? target.closest('[id*="image-toggle-btn"]') : null;
                    if (toggleBtn) {
                        // Set flag so row expand/collapse handler knows to ignore this click
                        window.lastClickWasToggleButton = true;
                        // Also record the timestamp for additional safety check
                        window.lastToggleButtonClickTime = Date.now();
                        // Stop propagation to prevent row collapse
                        // This runs in bubble phase, so Dash has already handled the click
                        e.stopPropagation();
                        // Clear flag after a short delay to reset for next click
                        setTimeout(function() {
                            window.lastClickWasToggleButton = false;
                        }, 250);
                    } else {
                        // Not a toggle button click, clear flag
                        window.lastClickWasToggleButton = false;
                    }
                };
                // Use bubble phase (false) so Dash handles the click first, then we stop propagation
                document.addEventListener('click', window.toggleButtonPropagationHandler, false);
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("audit-tags-store", "data", allow_duplicate=True),
        Input("record-display", "children"),
        prevent_initial_call='initial_duplicate'
    )
    
    # Handle row expand/collapse - only on arrow/row header click
    # Ignore clicks that come from toggle buttons
    app.clientside_callback(
        """
        function(n_clicks_list) {
            if (!n_clicks_list || n_clicks_list.length === 0) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            // Find which row was clicked
            const ctx = window.dash_clientside.callback_context;
            if (!ctx.triggered || ctx.triggered.length === 0) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            const triggered = ctx.triggered[0];
            const propId = triggered.prop_id;
            
            // Only handle expand-row clicks, ignore other clicks
            if (!propId || !propId.includes('expand-row')) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            // Check if the click actually came from a toggle button
            // This prevents row collapse when toggle button is clicked
            // First check the flag set by event delegation handler
            if (window.lastClickWasToggleButton) {
                window.lastClickWasToggleButton = false;
                throw window.dash_clientside.PreventUpdate;
            }
            
            // Additional safety check: verify the click didn't come from inside a toggle button
            // by checking if any toggle button was recently clicked (within last 200ms)
            // This handles cases where the flag might not be set correctly
            const now = Date.now();
            if (window.lastToggleButtonClickTime && (now - window.lastToggleButtonClickTime) < 200) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            // Extract the index from the prop_id
            const match = propId.match(/"index":(\\d+)/);
            if (!match) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            const index = match[1];
            const expandedRow = document.getElementById(`row-expanded-${index}`);
            const arrow = document.getElementById(`arrow-${index}`);
            
            // Final safety check: if the expanded row contains any toggle buttons that were just clicked,
            // don't collapse the row. This prevents collapse when clicking toggle buttons.
            if (expandedRow && expandedRow.style.display === 'table-row') {
                // Row is currently expanded - check if any toggle button inside it was recently clicked
                const toggleButtons = expandedRow.querySelectorAll('[id*="image-toggle-btn"]');
                if (toggleButtons.length > 0 && window.lastToggleButtonClickTime) {
                    const timeSinceToggle = now - window.lastToggleButtonClickTime;
                    if (timeSinceToggle < 300) {
                        // A toggle button was clicked recently, don't collapse
                        throw window.dash_clientside.PreventUpdate;
                    }
                }
            }
            
            if (expandedRow && arrow) {
                const isHidden = expandedRow.style.display === 'none' || !expandedRow.style.display;
                expandedRow.style.display = isHidden ? 'table-row' : 'none';
                // Rotate arrow: ▶ (closed) → ▼ (open)
                arrow.style.transform = isHidden ? 'rotate(90deg)' : 'rotate(0deg)';
            }
            
            throw window.dash_clientside.PreventUpdate;
        }
        """,
        Output("audit-tags-store", "data", allow_duplicate=True),
        Input({"type": "expand-row", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    
    # Handle audit dropdown changes (works for both Image Viewer and Cell Details tabs)
    @app.callback(
        Output("audit-tags-store", "data", allow_duplicate=True),
        Input({"type": "audit-dropdown", "txn_id": ALL}, "value"),
        State({"type": "audit-dropdown", "txn_id": ALL}, "id"),
        State("audit-tags-store", "data"),
        State("main-tabs", "active_tab"),  # Check which tab is active
        prevent_initial_call=True
    )
    def update_audit_tags(values, ids, current_tags, active_tab):
        """Store audit selections (works for both Image Viewer and Cell Details tabs)"""
        # This callback works for both tabs since it uses pattern matching
        if not values or not ids:
            return current_tags or {}
        
        audit_tags = current_tags or {}
        
        # Update audit tags for each dropdown
        for value, id_dict in zip(values, ids):
            txn_id = id_dict.get('txn_id', '')
            if txn_id:
                if value:
                    audit_tags[txn_id] = value
                elif txn_id in audit_tags:
                    # Clear if value is None
                    del audit_tags[txn_id]
        
        return audit_tags
    
    # Export audit CSV
    @app.callback(
        [Output("download-audit-csv", "data"),
         Output("audit-status", "children")],
        Input("export-audit-btn", "n_clicks"),
        [State("data-store", "data"),
         State("audit-tags-store", "data")],
        prevent_initial_call=True
    )
    def export_audit_csv(n_clicks, data_store, audit_tags):
        """Export audited records to CSV"""
        import pandas as pd
        from io import StringIO
        
        if not audit_tags or len(audit_tags) == 0:
            return no_update, html.Span("⚠️ No records audited yet!", style={"color": "#dc2626"})
        
        # Get all records
        if not data_store or not isinstance(data_store, dict):
            return no_update, html.Span("⚠️ No data loaded!", style={"color": "#dc2626"})
        
        if "data" in data_store:
            all_records = data_store["data"]
        else:
            all_records = data_store if isinstance(data_store, list) else []
        
        if not all_records:
            return no_update, html.Span("⚠️ No data loaded!", style={"color": "#dc2626"})
        
        # Filter to audited records and add audit_tag column
        audited_records = []
        for record in all_records:
            txn_id = record.get('pdd_txn_id', '')
            if txn_id in audit_tags:
                # Add audit_tag to record
                record_copy = record.copy()
                record_copy['audit_tag'] = audit_tags[txn_id]
                audited_records.append(record_copy)
        
        if not audited_records:
            return no_update, html.Span("⚠️ No matching records!", style={"color": "#dc2626"})
        
        # Create DataFrame
        df = pd.DataFrame(audited_records)
        
        # Ensure audit_tag is the last column
        cols = [c for c in df.columns if c != 'audit_tag'] + ['audit_tag']
        df = df[cols]
        
        # Convert to CSV
        csv_string = df.to_csv(index=False)
        
        from datetime import datetime
        filename = f"audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return (
            dict(content=csv_string, filename=filename),
            html.Span(f"✅ Exported {len(audited_records)} records!", style={"color": "#059669"})
        )
    
    # Copy request body to clipboard (works for both image viewer and cell details)
    @app.callback(
        Output("clipboard-copy-dummy-store", "data", allow_duplicate=True),
        Input({"type": "copy-request-body-btn", "side": ALL, "record_id": ALL}, "n_clicks"),
        [State("filtered-data-store", "data"),
         State("cell-details-filtered-data-store", "data")],
        prevent_initial_call=True
    )
    def get_request_body_for_copy(n_clicks_list, filtered_data, cell_details_filtered_data):
        """Get request body from record and store it for clipboard copy (works for both tabs)"""
        from dash import callback_context, no_update
        
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        # Get which button was clicked
        trigger = ctx.triggered[0]['prop_id']
        if not trigger or '.n_clicks' not in trigger:
            return no_update
        
        # Parse button ID to get side and record_id
        import json
        try:
            button_id_str = trigger.split('.')[0]
            button_id = json.loads(button_id_str)
            side = button_id.get('side')
            record_id = button_id.get('record_id')
            
            if not side or record_id is None:
                return no_update
            
            # Try image viewer data store first
            records = None
            if filtered_data and isinstance(filtered_data, dict):
                records = filtered_data.get("data", []) if "data" in filtered_data else filtered_data if isinstance(filtered_data, list) else []
            elif filtered_data and isinstance(filtered_data, list):
                records = filtered_data
            
            # If not found, try cell details data store
            if not records or len(records) == 0:
                if cell_details_filtered_data and isinstance(cell_details_filtered_data, dict):
                    records = cell_details_filtered_data.get("data", []) if "data" in cell_details_filtered_data else cell_details_filtered_data if isinstance(cell_details_filtered_data, list) else []
                elif cell_details_filtered_data and isinstance(cell_details_filtered_data, list):
                    records = cell_details_filtered_data
            
            if not records:
                return no_update
            
            # Find the record by record_id (pdd_txn_id)
            for record in records:
                if record.get('pdd_txn_id') == record_id:
                    # Get request body for this side
                    request_body = record.get(f'{side}_request_body', '')
                    if request_body:
                        # Return the request body to be copied
                        return request_body
                    break
            
            return no_update
        except (json.JSONDecodeError, KeyError, AttributeError):
            return no_update
    
    # Clientside callback to copy to clipboard
    app.clientside_callback(
        """
        function(request_body) {
            if (!request_body) {
                throw window.dash_clientside.PreventUpdate;
            }
            
            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(request_body).then(function() {
                    // Optional: Show a brief notification
                    console.log('Request body copied to clipboard');
                }).catch(function(err) {
                    console.error('Failed to copy:', err);
                });
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = request_body;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    console.log('Request body copied to clipboard (fallback)');
                } catch (err) {
                    console.error('Failed to copy:', err);
                }
                document.body.removeChild(textArea);
            }
            
            // Return null to prevent updating the store
            return null;
        }
        """,
        Output("clipboard-copy-dummy-store", "data", allow_duplicate=True),
        Input("clipboard-copy-dummy-store", "data"),
        prevent_initial_call=True
        )
