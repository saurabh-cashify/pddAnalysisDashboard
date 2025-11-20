"""
Image Viewer Tab Component for Analysis Dashboard
Displays filtered records with images from all sides
"""

from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def create_image_viewer_tab():
    """Create the Image Viewer tab layout"""
    
    return dbc.Container([
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
                            multi=True,
                            persistence=True,
                            persistence_type='session'
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
                            multi=True,
                            persistence=True,
                            persistence_type='session'
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
                            multi=True,
                            persistence=True,
                            persistence_type='session'
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
                            multi=True,
                            persistence=True,
                            persistence_type='session'
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
                            multi=True,
                            persistence=True,
                            persistence_type='session'
                        ),
                    ], md=6),
                ], className="mb-3"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button("🔍 Apply Filters", id="apply-filters-btn", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset Filters", id="reset-filters-btn", color="warning"),
                    ], className="d-flex")
                ])
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
                        html.Span("Filtered Records:", className="label fw-bold me-2"),
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
        
        # Navigation Controls
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("⏮️ First", id="first-btn", color="primary", outline=True),
                            dbc.Button("◀️ Previous", id="prev-btn", color="primary", outline=True),
                        ])
                    ], md=4, className="d-flex justify-content-start"),
                    dbc.Col([
                        html.Div([
                            html.Span(id="record-number", children="0", style={"fontSize": "1.3em", "fontWeight": "600"}),
                            html.Span(" of ", style={"margin": "0 8px"}),
                            html.Span(id="total-filtered", children="0", style={"fontSize": "1.3em", "fontWeight": "600"}),
                        ], className="text-center", style={"lineHeight": "38px"})
                    ], md=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Next ▶️", id="next-btn", color="primary", outline=True),
                            dbc.Button("Last ⏭️", id="last-btn", color="primary", outline=True),
                        ])
                    ], md=4, className="d-flex justify-content-end"),
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
        
    ], fluid=True, className="tab-content-container")


def create_record_display(record, current_index, image_toggle_states, comparison_mode='split'):
    """Create the display for a single record"""
    
    sides = ['top', 'bottom', 'right', 'left', 'back', 'front']
    
    # Parse contributing sides for highlighting
    contributing_sides_list = [s.strip().lower() for s in str(record.get('contributing_sides', '')).split(',') if s.strip()]
    new_contributing_sides_list = [s.strip().lower() for s in str(record.get('new_contributing_sides', '')).split(',') if s.strip()]
    
    # Record Header with Enhanced Details
    header = dbc.Card([
        dbc.CardBody([
            html.H2("📋 Record Details", className="mb-3", style={"color": "#ffffff", "fontWeight": "600"}),
            # Row 1: Transaction and Date
            dbc.Row([
                dbc.Col([
                    html.Strong("Transaction ID: ", style={"color": "#e0f2fe"}),
                    html.Span(record.get('pdd_txn_id', 'N/A'), style={"color": "#ffffff", "fontWeight": "500"})
                ], md=6),
                dbc.Col([
                    html.Strong("Quote Date: ", style={"color": "#e0f2fe"}),
                    html.Span(record.get('quote_date', 'N/A'), style={"color": "#ffffff", "fontWeight": "500"})
                ], md=6),
            ], className="mb-3"),
            
            # Row 2: Contributing Sides
            dbc.Row([
                dbc.Col([
                    html.Strong("Contributing Sides: ", style={"color": "#e0f2fe"}),
                    html.Span(
                        record.get('contributing_sides', 'N/A'), 
                        style={
                            "color": "#fbbf24",  # Bright yellow for visibility
                            "fontWeight": "700",
                            "fontSize": "1.05em",
                            "backgroundColor": "rgba(251, 191, 36, 0.15)",
                            "padding": "4px 10px",
                            "borderRadius": "4px"
                        }
                    )
                ], md=6),
                dbc.Col([
                    html.Strong("New Contributing Sides: ", style={"color": "#e0f2fe"}),
                    html.Span(
                        record.get('new_contributing_sides', 'N/A'), 
                        style={
                            "color": "#34d399",  # Bright green for visibility
                            "fontWeight": "700",
                            "fontSize": "1.05em",
                            "backgroundColor": "rgba(52, 211, 153, 0.15)",
                            "padding": "4px 10px",
                            "borderRadius": "4px"
                        }
                    )
                ], md=6),
            ], className="mb-3"),
            
            # Row 3: Answers
            dbc.Row([
                dbc.Col([
                    html.Strong("Deployed CScan: ", style={"color": "#e0f2fe"}),
                    dbc.Badge(
                        record.get('cscan_answer', 'N/A'), 
                        color="light", 
                        className="ms-1",
                        style={"color": "#0c4a6e", "fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
                dbc.Col([
                    html.Strong("New CScan: ", style={"color": "#e0f2fe"}),
                    dbc.Badge(
                        record.get('new_cscan_answer', 'N/A'), 
                        color="success", 
                        className="ms-1",
                        style={"fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
                dbc.Col([
                    html.Strong("Final Answer: ", style={"color": "#e0f2fe"}),
                    dbc.Badge(
                        record.get('final_answer', 'N/A'), 
                        color="warning", 
                        className="ms-1",
                        style={"fontSize": "0.95em", "fontWeight": "600"}
                    )
                ], md=4),
            ], className="mb-3"),
            
            # Row 4: QC and Auditor Answers
            dbc.Row([
                dbc.Col([
                    html.Strong("QC Answer: ", style={"color": "#e0f2fe"}),
                    html.Span(record.get('qc_answer', 'N/A'), style={"color": "#ffffff", "fontWeight": "500"})
                ], md=6),
                dbc.Col([
                    html.Strong("Auditor Answer: ", style={"color": "#e0f2fe"}),
                    html.Span(record.get('auditor_answer', 'N/A'), style={"color": "#ffffff", "fontWeight": "500"})
                ], md=6),
            ]),
        ], style={"padding": "1.5rem"})
    ], className="mb-4", style={
        "background": "linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%)",
        "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        "border": "none"
    })
    
    # Images Grid
    images_grid = []
    for side in sides:
        old_score = float(record.get(f'{side}_score', 0) or 0)
        new_score_val = record.get(f'new_{side}_score')
        new_score = float(new_score_val) if new_score_val not in [None, '', 'N/A'] else None
        
        old_result_url = record.get(f'{side}_result_url', '')
        new_result_url = record.get(f'new_{side}_result_image_url', '')
        input_image_url = record.get(f'{side}_image_url', '')
        
        # Get UUIDs for display
        side_uuid = record.get(f'{side}_uuid', 'N/A')
        
        has_new = new_result_url and new_score is not None
        
        # Check if this side is in contributing sides for highlighting
        is_contributing = side.lower() in contributing_sides_list
        is_new_contributing = side.lower() in new_contributing_sides_list
        
        # Get current toggle state for this side
        current_image_mode = image_toggle_states.get(side, 'result')
        
        # Determine which URLs to display
        display_old_url = input_image_url if current_image_mode == 'input' else old_result_url
        display_new_url = input_image_url if current_image_mode == 'input' else new_result_url
        image_label = 'Input Image' if current_image_mode == 'input' else 'Result'
        
        # Professional Card Design
        card_content = []
        
        # Highlighting colors
        deployed_badge_color = "warning" if is_contributing else "light"
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
        control_row = html.Div([
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        f"🔄 {'Input' if current_image_mode == 'result' else 'Result'}",
                        id={"type": "image-toggle-btn", "side": side},
                        color="info",
                        size="sm",
                        outline=True,
                        className="w-100"
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
                            "padding": "6px",
                            "color": "#0c4a6e" if deployed_badge_color == "light" else "white"
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
        if has_new:
            # Side by side comparison (both deployed and new exist)
            image_body = html.Div([
                dbc.Row([
                    dbc.Col([
                        html.Div(f"Deployed {image_label}", className="text-center fw-bold mb-2", style={"color": "#475569", "fontSize": "0.9em"}),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_old_url if display_old_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxHeight": "450px",  # Increased from 300px
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "old"},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff"}
                            ) if display_old_url else html.Div(
                                "No image", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "200px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"})
                        ])
                    ], md=6),
                    dbc.Col([
                        html.Div(f"New {image_label}", className="text-center fw-bold mb-2", style={"color": "#475569", "fontSize": "0.9em"}),
                        html.Div([
                            html.Div(
                                html.Img(
                                    src=display_new_url if display_new_url else "",
                                    style={
                                        "width": "100%", 
                                        "maxHeight": "450px",  # Increased from 300px
                                        "objectFit": "contain",
                                        "borderRadius": "8px",
                                        "border": "1px solid #e2e8f0"
                                    },
                                    className="hover-shadow"
                                ),
                                id={"type": "image-clickable", "side": side, "version": "new"},
                                n_clicks=0,
                                style={"cursor": "pointer", "background": "#ffffff"}
                            ) if display_new_url else html.Div(
                                f"No new {image_label.lower()}", 
                                className="text-muted text-center p-4", 
                                style={
                                    "border": "2px dashed #cbd5e1",
                                    "borderRadius": "8px",
                                    "minHeight": "200px",
                                    "display": "flex",
                                    "alignItems": "center",
                                    "justifyContent": "center",
                                    "background": "#f8fafc"
                                }
                            ),
                            html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"})
                        ])
                    ], md=6),
                ])
            ], style={"padding": "1.25rem", "background": "#ffffff"})
        else:
            # Single image view (only deployed exists)
            image_body = html.Div([
                html.Div(f"Deployed {image_label}", className="text-center fw-bold mb-3", style={"color": "#475569", "fontSize": "0.9em"}),
                html.Div([
                    html.Div(
                        html.Img(
                            src=display_old_url if display_old_url else "",
                            style={
                                "width": "100%", 
                                "maxHeight": "450px",  # Increased from 300px
                                "objectFit": "contain",
                                "borderRadius": "8px",
                                "border": "1px solid #e2e8f0"
                            },
                            className="hover-shadow"
                        ),
                        id={"type": "image-clickable", "side": side, "version": "single"},
                        n_clicks=0,
                        style={"cursor": "pointer", "background": "#ffffff"}
                    ) if display_old_url else html.Div(
                        "No image available", 
                        className="text-muted text-center p-4", 
                        style={
                            "border": "2px dashed #cbd5e1",
                            "borderRadius": "8px",
                            "minHeight": "200px",
                            "display": "flex",
                            "alignItems": "center",
                            "justifyContent": "center",
                            "background": "#f8fafc"
                        }
                    ),
                    html.Small(f"UUID: {side_uuid}", className="text-muted d-block text-center mt-2", style={"fontSize": "0.7em", "wordBreak": "break-all"})
                ])
            ], style={"padding": "1.25rem", "background": "#ffffff"})
        
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
    
    # Combine all elements with professional styling
    return html.Div([
        header,
        html.H3(
            "📷 Images",
            className="mb-4 mt-4",
            style={
                "color": "#1e40af",
                "fontWeight": "600",
                "fontSize": "1.5em",
                "borderBottom": "3px solid #3b82f6",
                "paddingBottom": "8px",
                "display": "inline-block"
            }
        ),
        dbc.Row(images_grid, className="g-4")
    ])


def register_image_viewer_callbacks(app):
    """Register callbacks for image viewer tab"""
    
    # Populate filter dropdowns when data is loaded
    @app.callback(
        [Output("cscan-answer-filter", "options"),
         Output("new-cscan-answer-filter", "options"),
         Output("final-answer-filter", "options")],
        Input("data-store", "data")
    )
    def populate_filter_dropdowns(data):
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
                cscan_answers.add(record['cscan_answer'])
            if record.get('new_cscan_answer'):
                new_cscan_answers.add(record['new_cscan_answer'])
            if record.get('final_answer'):
                final_answers.add(record['final_answer'])
        
        # Create options without "All" option (empty list = all selected)
        cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(cscan_answers)]
        new_cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(new_cscan_answers)]
        final_options = [{"label": str(v), "value": str(v)} for v in sorted(final_answers)]
        
        return cscan_options, new_cscan_options, final_options
    
    # Apply filters and update filtered data
    @app.callback(
        [Output("filtered-data-store", "data"),
         Output("current-index-store", "data")],
        [Input("apply-filters-btn", "n_clicks"),
         Input("reset-filters-btn", "n_clicks")],
        [State("data-store", "data"),
         State("cscan-answer-filter", "value"),
         State("new-cscan-answer-filter", "value"),
         State("final-answer-filter", "value"),
         State("contributing-side-filter", "value"),
         State("new-contributing-side-filter", "value")]
    )
    def apply_filters(apply_clicks, reset_clicks, data, cscan_filter, new_cscan_filter, final_filter, side_filter, new_side_filter):
        ctx = callback_context
        if not ctx.triggered:
            # Initial load - no filters
            return data, 0
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset filters
        if trigger_id == "reset-filters-btn":
            return data, 0
        
        # Apply filters
        if not data or not isinstance(data, dict):
            return {}, 0
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return {}, 0
        
        # Filter records
        filtered = records
        
        # Handle CScan Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if cscan_filter and len(cscan_filter) > 0:
            filtered = [r for r in filtered if str(r.get('cscan_answer', '')) in cscan_filter]
        
        # Handle New CScan Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if new_cscan_filter and len(new_cscan_filter) > 0:
            filtered = [r for r in filtered if str(r.get('new_cscan_answer', '')) in new_cscan_filter]
        
        # Handle Final Answer filter: Empty = all selected (filter off), non-empty = apply filter
        if final_filter and len(final_filter) > 0:
            filtered = [r for r in filtered if str(r.get('final_answer', '')) in final_filter]
        
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
        
        return filtered_data, 0
    
    # Update stats and record display
    @app.callback(
        [Output("total-records", "children"),
         Output("filtered-records", "children"),
         Output("current-index-display", "children"),
         Output("record-number", "children"),
         Output("total-filtered", "children"),
         Output("old-accuracy", "children"),
         Output("new-accuracy", "children"),
         Output("record-display", "children")],
        [Input("filtered-data-store", "data"),
         Input("current-index-store", "data"),
         Input("image-toggle-state-store", "data"),
         Input({"type": "image-toggle-btn", "side": ALL}, "n_clicks")],
        [State("data-store", "data")]
    )
    def update_display(filtered_data, current_index, image_toggle_states, n_clicks_list, total_data):
        # Get total records count
        if total_data and isinstance(total_data, dict) and "data" in total_data:
            total_count = len(total_data["data"])
        elif total_data and isinstance(total_data, list):
            total_count = len(total_data)
        else:
            total_count = 0
        
        # Get filtered records
        if not filtered_data or not isinstance(filtered_data, dict):
            return (str(total_count), "0", "0", "0", "0", "N/A", "N/A", 
                    html.Div("No data loaded. Please load a CSV file.", className="text-center text-muted py-5"))
        
        if "data" in filtered_data:
            records = filtered_data["data"]
        else:
            records = filtered_data if isinstance(filtered_data, list) else []
        
        filtered_count = len(records)
        
        if filtered_count == 0:
            return (str(total_count), "0", "0", "0", "0", "N/A", "N/A",
                    html.Div([
                        html.H3("No records match your filters", className="text-center text-muted"),
                        html.P("Try adjusting your filter criteria", className="text-center text-muted")
                    ], className="py-5"))
        
        # Ensure current_index is within bounds
        if current_index >= filtered_count:
            current_index = filtered_count - 1
        if current_index < 0:
            current_index = 0
        
        # Get current record
        record = records[current_index]
        
        # Calculate accuracies
        correct_old = sum(1 for r in records if str(r.get('cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        correct_new = sum(1 for r in records if str(r.get('new_cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        
        old_acc = f"{(correct_old / filtered_count * 100):.2f}%" if filtered_count > 0 else "N/A"
        new_acc = f"{(correct_new / filtered_count * 100):.2f}%" if filtered_count > 0 else "N/A"
        
        # Handle image toggle button clicks
        ctx = callback_context
        if ctx.triggered:
            trigger = ctx.triggered[0]['prop_id']
            if 'image-toggle-btn' in trigger:
                # Parse the clicked button's side
                import json
                try:
                    trigger_dict = json.loads(trigger.split('.')[0])
                    clicked_side = trigger_dict.get('side')
                    if clicked_side and image_toggle_states:
                        # Toggle the state
                        current_state = image_toggle_states.get(clicked_side, 'result')
                        new_state = 'input' if current_state == 'result' else 'result'
                        image_toggle_states[clicked_side] = new_state
                except:
                    pass
        
        # Create record display
        record_display = create_record_display(record, current_index, image_toggle_states or {})
        
        return (
            str(total_count),
            str(filtered_count),
            str(current_index + 1),
            str(current_index + 1),
            str(filtered_count),
            old_acc,
            new_acc,
            record_display
        )
    
    # Navigation buttons
    @app.callback(
        Output("current-index-store", "data", allow_duplicate=True),
        [Input("first-btn", "n_clicks"),
         Input("prev-btn", "n_clicks"),
         Input("next-btn", "n_clicks"),
         Input("last-btn", "n_clicks")],
        [State("filtered-data-store", "data"),
         State("current-index-store", "data")],
        prevent_initial_call=True
    )
    def navigate_records(first_clicks, prev_clicks, next_clicks, last_clicks, filtered_data, current_index):
        ctx = callback_context
        if not ctx.triggered:
            return current_index
        
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
        
        # Navigate
        if trigger_id == "first-btn":
            return 0
        elif trigger_id == "prev-btn":
            return max(0, current_index - 1)
        elif trigger_id == "next-btn":
            return min(filtered_count - 1, current_index + 1)
        elif trigger_id == "last-btn":
            return filtered_count - 1
        
        return current_index
    
    # Update image toggle state store when buttons are clicked
    @app.callback(
        Output("image-toggle-state-store", "data", allow_duplicate=True),
        Input({"type": "image-toggle-btn", "side": ALL}, "n_clicks"),
        State("image-toggle-state-store", "data"),
        prevent_initial_call=True
    )
    def update_image_toggle_state(n_clicks_list, current_states):
        ctx = callback_context
        if not ctx.triggered:
            return current_states
        
        trigger = ctx.triggered[0]['prop_id']
        current_states = current_states or {
            'top': 'result', 'bottom': 'result', 'left': 'result',
            'right': 'result', 'back': 'result', 'front': 'result'
        }
        
        if 'image-toggle-btn' in trigger:
            import json
            try:
                trigger_dict = json.loads(trigger.split('.')[0])
                clicked_side = trigger_dict.get('side')
                if clicked_side:
                    current_state = current_states.get(clicked_side, 'result')
                    new_state = 'input' if current_state == 'result' else 'result'
                    current_states[clicked_side] = new_state
            except:
                pass
        
        return current_states
    
    # Modal for full image view
    @app.callback(
        [Output("image-modal", "is_open"),
         Output("modal-image", "src")],
        [Input({"type": "image-clickable", "side": ALL, "version": ALL}, "n_clicks"),
         Input("close-modal", "n_clicks")],
        [State("filtered-data-store", "data"),
         State("current-index-store", "data"),
         State("image-toggle-state-store", "data"),
         State("image-modal", "is_open")],
        prevent_initial_call=True
    )
    def toggle_image_modal(n_clicks_list, close_clicks, filtered_data, current_index, image_states, is_open):
        ctx = callback_context
        if not ctx.triggered:
            return False, ""
        
        trigger = ctx.triggered[0]['prop_id']
        trigger_value = ctx.triggered[0].get('value')
        
        # Don't open modal if this is just component creation (value will be None or 0)
        if trigger_value is None or trigger_value == 0:
            from dash import no_update
            return no_update
        
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
                
                if not filtered_data or not isinstance(filtered_data, dict):
                    return False, ""
                
                if "data" in filtered_data:
                    records = filtered_data["data"]
                else:
                    records = filtered_data if isinstance(filtered_data, list) else []
                
                if not records or current_index >= len(records):
                    return False, ""
                
                record = records[current_index]
                
                # Get the correct URL
                current_mode = image_states.get(side, 'result') if image_states else 'result'
                
                if current_mode == 'input':
                    url = record.get(f'{side}_image_url', '')
                else:
                    if version == 'new' or version == 'single':
                        url = record.get(f'new_{side}_result_image_url', '') or record.get(f'{side}_result_url', '')
                    else:
                        url = record.get(f'{side}_result_url', '')
                
                return True, url if url else ""
            except:
                return False, ""
        
        return False, ""
