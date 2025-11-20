"""
Cell Details Tab Component for Analysis Dashboard
Displays filtered records from a specific confusion matrix cell (similar to Image Viewer)
"""

from dash import html, dcc, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import functions from image_viewer to reuse record display
from components.image_viewer import create_accordion_view, create_record_display_with_audit


def create_cell_details_tab():
    """Create the Cell Details tab layout (similar to Image Viewer but without filter controls)"""
    
    return dbc.Container([
        # Note: Using shared audit-tags-store from image_viewer for consistency
        
        # Back Button only (no header section)
        dbc.Button("← Back to Matrix", id="back-to-matrix-btn", color="light", outline=True, className="mb-2"),
        
        # Controls Panel - Filters
        dbc.Card([
            dbc.CardBody([
                html.H3("🎯 Filters", className="mb-3", style={"color": "#3b82f6"}),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed CScan Answer", html_for="cell-cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cell-cscan-answer-filter",
                            options=[],  # Will be populated dynamically
                            value=[],  # Empty = all selected
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("New CScan Answer", html_for="cell-new-cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cell-new-cscan-answer-filter",
                            options=[],  # Will be populated dynamically
                            value=[],  # Empty = all selected
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Final Answer", html_for="cell-final-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cell-final-answer-filter",
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
                        dbc.Label("Deployed Contributing Sides", html_for="cell-contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cell-contributing-side-filter",
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
                        dbc.Label("New Contributing Sides", html_for="cell-new-contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="cell-new-contributing-side-filter",
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
                        dbc.Label("Deployed Side Score Filter", html_for="cell-deployed-side-score-filter", className="fw-bold"),
                        dcc.RangeSlider(
                            id="cell-deployed-score-range-slider",
                            min=0,
                            max=100,
                            step=1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="cell-deployed-side-score-filter",
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
                        dbc.Label("New Side Score Filter", html_for="cell-new-side-score-filter", className="fw-bold"),
                        dcc.RangeSlider(
                            id="cell-new-score-range-slider",
                            min=0,
                            max=100,
                            step=1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="cell-new-side-score-filter",
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
                        dbc.Button("🔍 Apply Filters", id="cell-apply-filters-btn", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset Filters", id="cell-reset-filters-btn", color="warning", className="me-2"),
                        dbc.Button("📥 Export Audit CSV", id="cell-export-audit-btn", color="success", className=""),
                    ], className="d-flex"),
                    dbc.Col([
                        html.Span(id="cell-audit-status", className="text-muted", style={"lineHeight": "38px"})
                    ], className="text-end")
                ]),
                # Download component for audit CSV
                dcc.Download(id="cell-download-audit-csv")
            ])
        ], className="mb-4", style={"background": "linear-gradient(to bottom, #f8fafc, #f1f5f9)"}),
        
        # Stats Bar with Export Button
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span("Total Records:", className="label fw-bold me-2"),
                        html.Span("0", id="cell-total-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Filtered:", className="label fw-bold me-2"),
                        html.Span("0", id="cell-filtered-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Current:", className="label fw-bold me-2"),
                        html.Span("0", id="cell-current-index-display", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Accuracy:", className="label fw-bold me-2"),
                        html.Span("N/A", id="cell-accuracy", className="value", style={"color": "#10b981", "fontSize": "1.2em"}),
                    ], md=3),
                    dbc.Col([
                        dbc.Button("📥 Export Audit CSV", id="cell-export-audit-btn", color="success", size="sm", className="me-2"),
                        html.Span(id="cell-audit-status", className="text-muted", style={"lineHeight": "38px"})
                    ], md=3, className="text-end"),
                ])
            ])
        ], className="mb-4"),
        
        # Record Display Area
        html.Div(id="cell-record-display", children=[
            html.Div([
                html.Div(className="spinner"),
                html.P("Click on a confusion matrix cell to view records...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        ]),
        
        # Image Modal (same as image viewer)
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Image View")),
                dbc.ModalBody([
                    html.Img(id="modal-image", src="", style={"width": "100%", "height": "auto"})
                ]),
                dbc.ModalFooter([
                    dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
                ])
            ],
            id="image-modal",
            is_open=False,
            size="xl",
            centered=True
        ),
        
        # Navigation Controls (for pages of 10 records)
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("⏮️ First Page", id="cell-first-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("◀️ Prev", id="cell-prev-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-start"),
                    dbc.Col([
                        html.Div([
                            html.Span("Records ", style={"fontSize": "0.9em"}),
                            html.Span(id="cell-page-start", children="1", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span("-", style={"margin": "0 4px"}),
                            html.Span(id="cell-page-end", children="10", style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span(" of ", style={"margin": "0 8px"}),
                            html.Span(id="cell-total-filtered", children="0", style={"fontSize": "1.2em", "fontWeight": "600"}),
                        ], className="text-center", style={"lineHeight": "38px"})
                    ], md=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Next ▶️", id="cell-next-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("Last Page ⏭️", id="cell-last-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-end"),
                ])
            ])
        ], className="mt-4"),
        
    ], fluid=True, className="tab-content-container")


def register_cell_details_callbacks(app):
    """Register callbacks for cell details tab"""
    
    # Reset filters and state when switching to cell details tab
    @app.callback(
        [Output("cell-details-filtered-data-store", "data", allow_duplicate=True),
         Output("cell-details-current-page-store", "data", allow_duplicate=True),
         Output("cell-details-original-filtered-data-store", "data", allow_duplicate=True),
         Output("cell-cscan-answer-filter", "value", allow_duplicate=True),
         Output("cell-new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("cell-final-answer-filter", "value", allow_duplicate=True),
         Output("cell-contributing-side-filter", "value", allow_duplicate=True),
         Output("cell-new-contributing-side-filter", "value", allow_duplicate=True),
         Output("cell-deployed-side-score-filter", "value", allow_duplicate=True),
         Output("cell-deployed-score-range-slider", "value", allow_duplicate=True),
         Output("cell-new-side-score-filter", "value", allow_duplicate=True),
         Output("cell-new-score-range-slider", "value", allow_duplicate=True)],
        Input("main-tabs", "active_tab"),
        prevent_initial_call=True
    )
    def reset_cell_details_on_tab_switch(active_tab):
        """Reset all filters and state when switching to cell details tab"""
        from dash import callback_context, no_update
        
        # Check which input triggered this callback
        ctx = callback_context
        triggered_prop = None
        if ctx.triggered:
            triggered_prop = ctx.triggered[0]['prop_id']
        
        if active_tab == "celldetail":
            # CRITICAL: If this was triggered by a matrix click (active_tab changed to celldetail),
            # we should NOT clear the data stores - let apply_cell_filters handle it
            # Only clear if this is a manual tab switch (not from matrix click)
            # We can detect this by checking if we're switching TO celldetail from another tab
            # But if apply_cell_filters is also running, it will set the data, so we should preserve it
            
            # For now, only reset filter dropdowns, not the data stores
            # The data stores will be set by apply_cell_filters if a matrix was clicked
            return (
                no_update,  # Don't clear cell-details-filtered-data-store - let apply_cell_filters set it
                no_update,  # Don't clear cell-details-current-page-store
                no_update,  # Don't clear cell-details-original-filtered-data-store
                [],  # Reset cell-cscan-answer-filter
                [],  # Reset cell-new-cscan-answer-filter
                [],  # Reset cell-final-answer-filter
                [],  # Reset cell-contributing-side-filter
                [],  # Reset cell-new-contributing-side-filter
                [],  # Reset cell-deployed-side-score-filter
                [0, 100],  # Reset cell-deployed-score-range-slider
                [],  # Reset cell-new-side-score-filter
                [0, 100]  # Reset cell-new-score-range-slider
            )
        
        # Don't change anything if not switching to cell details tab
        from dash import no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Apply filters from matrix click and update filtered data
    @app.callback(
        [Output("cell-details-filtered-data-store", "data", allow_duplicate=True),
         Output("cell-details-current-page-store", "data", allow_duplicate=True),
         Output("cell-details-original-filtered-data-store", "data", allow_duplicate=True)],  # Store original for reset
        [Input("matrix-click-trigger", "data"),
         Input("main-tabs", "active_tab")],
        [State("data-store", "data"),
         State("matrix-filter-cscan", "data"),
         State("matrix-filter-new-cscan", "data"),
         State("matrix-filter-final", "data"),
         State("threshold-config-store", "data")],
        prevent_initial_call=True
    )
    def apply_cell_filters(matrix_trigger, active_tab, data, matrix_cscan_filter, matrix_new_cscan_filter, matrix_final_filter, threshold_config):
        """Apply filters from confusion matrix click to cell details"""
        
        from dash import callback_context, no_update
        
        # Check which input triggered this callback
        ctx = callback_context
        triggered_prop = None
        if ctx.triggered:
            triggered_prop = ctx.triggered[0]['prop_id']
        
        # CRITICAL: If matrix-click-trigger was the trigger, we MUST process (even if not on celldetail tab yet)
        # This ensures that when clicking a matrix cell, the data is filtered correctly
        is_matrix_trigger = triggered_prop and 'matrix-click-trigger' in triggered_prop
        
        # If matrix was clicked, process the filters (will switch to celldetail tab automatically)
        if is_matrix_trigger and matrix_trigger and matrix_trigger > 0:
            # Continue to filter processing below
            pass
        elif active_tab == "celldetail" and matrix_trigger and matrix_trigger > 0:
            # We're on celldetail tab and have a matrix trigger - process it
            # Continue to filter processing below
            pass
        else:
            # Not a matrix click trigger, or not on celldetail tab, or no trigger
            return no_update, no_update, no_update
        
        if not data or not isinstance(data, dict):
            return {}, 0, {}
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return {}, 0, {}
        
        # Filter records based on matrix filter stores
        # IMPORTANT: Apply filters with AND logic - all conditions must match
        filtered = records
        
        # Use the same normalization function as confusion matrix for consistency
        from utils.threshold_handler import normalize_category_for_confusion_matrix
        
        def normalize_for_comparison(value, question_name=None):
            """Normalize value for comparison - uses same function as confusion matrix"""
            if not value or value == 'N/A' or str(value).strip() == '':
                return None
            # Use the same normalization function as confusion matrix
            # Ensure question_name is not None
            qn = question_name if question_name else 'default'
            return normalize_category_for_confusion_matrix(str(value), qn)
        
        # Get question name from threshold config for proper normalization
        # Use the same detection function as confusion matrix for consistency
        from components.confusion_matrix import detect_question_name_from_config
        question_name = detect_question_name_from_config(threshold_config, data)
        if not question_name:
            # Fallback: use first available question from config
            if threshold_config and isinstance(threshold_config, dict):
                for key in threshold_config.keys():
                    if key != 'default':
                        question_name = key
                        break
        
        # Determine which model was clicked based on which filter is set
        # OLD model: matrix_cscan_filter is set (predicted) + matrix_final_filter (actual)
        # NEW model: matrix_new_cscan_filter is set (predicted) + matrix_final_filter (actual)
        
        has_old_model_filter = matrix_cscan_filter and len(matrix_cscan_filter) > 0
        has_new_model_filter = matrix_new_cscan_filter and len(matrix_new_cscan_filter) > 0
        has_final_filter = matrix_final_filter and len(matrix_final_filter) > 0
        
        # Apply filters based on which matrix was clicked
        if has_old_model_filter:
            # OLD model clicked: filter by cscan_answer (predicted) AND final_answer (actual)
            # Normalize filter values (they may already be normalized from confusion matrix, but normalize again for safety)
            normalized_cscan_filter = [normalize_for_comparison(v, question_name) for v in matrix_cscan_filter if v]
            # If filtering for "cracked or broken panel", also include "glass panel damaged"
            if "cracked or broken panel" in normalized_cscan_filter and question_name and 'physicalconditionpanel' in question_name.lower():
                normalized_cscan_filter.append("glass panel damaged")
            
            # Filter by cscan_answer
            filtered_records = []
            for r in filtered:
                norm_val = normalize_for_comparison(r.get('cscan_answer', ''), question_name)
                if norm_val is not None and norm_val in normalized_cscan_filter:
                    filtered_records.append(r)
            filtered = filtered_records
            
            if has_final_filter:
                normalized_final_filter = [normalize_for_comparison(v, question_name) for v in matrix_final_filter if v]
                # If filtering for "cracked or broken panel", also include "glass panel damaged"
                if "cracked or broken panel" in normalized_final_filter and question_name and 'physicalconditionpanel' in question_name.lower():
                    normalized_final_filter.append("glass panel damaged")
                
                # Filter by final_answer
                filtered_records = []
                for r in filtered:
                    norm_val = normalize_for_comparison(r.get('final_answer', ''), question_name)
                    if norm_val is not None and norm_val in normalized_final_filter:
                        filtered_records.append(r)
                filtered = filtered_records
        
        elif has_new_model_filter:
            # NEW model clicked: filter by new_cscan_answer (predicted) AND final_answer (actual)
            normalized_new_cscan_filter = [normalize_for_comparison(v, question_name) for v in matrix_new_cscan_filter if v]
            # If filtering for "cracked or broken panel", also include "glass panel damaged"
            if "cracked or broken panel" in normalized_new_cscan_filter and question_name and 'physicalconditionpanel' in question_name.lower():
                normalized_new_cscan_filter.append("glass panel damaged")
            
            # Filter by new_cscan_answer
            filtered_records = []
            for r in filtered:
                norm_val = normalize_for_comparison(r.get('new_cscan_answer', ''), question_name)
                if norm_val is not None and norm_val in normalized_new_cscan_filter:
                    filtered_records.append(r)
            filtered = filtered_records
            
            if has_final_filter:
                normalized_final_filter = [normalize_for_comparison(v, question_name) for v in matrix_final_filter if v]
                # If filtering for "cracked or broken panel", also include "glass panel damaged"
                if "cracked or broken panel" in normalized_final_filter and question_name and 'physicalconditionpanel' in question_name.lower():
                    normalized_final_filter.append("glass panel damaged")
                
                # Filter by final_answer
                filtered_records = []
                for r in filtered:
                    norm_val = normalize_for_comparison(r.get('final_answer', ''), question_name)
                    if norm_val is not None and norm_val in normalized_final_filter:
                        filtered_records.append(r)
                filtered = filtered_records
        
        else:
            # Fallback: if only final filter is set, apply it
            if has_final_filter:
                normalized_final_filter = [normalize_for_comparison(v, question_name) for v in matrix_final_filter]
                # If filtering for "cracked or broken panel", also include "glass panel damaged"
                if "cracked or broken panel" in normalized_final_filter and question_name and 'physicalconditionpanel' in question_name.lower():
                    normalized_final_filter.append("glass panel damaged")
                # Filter by final_answer
                filtered_records = []
                for r in filtered:
                    norm_val = normalize_for_comparison(r.get('final_answer', ''), question_name)
                    if norm_val is not None and norm_val in normalized_final_filter:
                        filtered_records.append(r)
                filtered = filtered_records
        
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
        
        # Store original matrix-filtered data for reset functionality
        return filtered_data, 0, filtered_data  # Also output to original store
    
    # Populate filter dropdowns when cell details data is loaded
    @app.callback(
        [Output("cell-cscan-answer-filter", "options"),
         Output("cell-new-cscan-answer-filter", "options"),
         Output("cell-final-answer-filter", "options")],
        Input("cell-details-filtered-data-store", "data")
    )
    def populate_cell_filter_dropdowns(filtered_data):
        """Populate filter dropdowns based on filtered data from matrix click"""
        
        if not filtered_data or not isinstance(filtered_data, dict):
            return [], [], []
        
        # Extract records from filtered data
        if "data" in filtered_data:
            records = filtered_data["data"]
        else:
            records = filtered_data if isinstance(filtered_data, list) else []
        
        if not records:
            return [], [], []
        
        # Collect unique values from the filtered records
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
        
        # Create options
        cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(cscan_answers)]
        new_cscan_options = [{"label": str(v), "value": str(v)} for v in sorted(new_cscan_answers)]
        final_options = [{"label": str(v), "value": str(v)} for v in sorted(final_answers)]
        
        return cscan_options, new_cscan_options, final_options
    
    # Apply filters to cell details data
    @app.callback(
        [Output("cell-details-filtered-data-store", "data", allow_duplicate=True),
         Output("cell-details-current-page-store", "data", allow_duplicate=True)],
        [Input("cell-apply-filters-btn", "n_clicks"),
         Input("cell-reset-filters-btn", "n_clicks")],
        [State("cell-details-filtered-data-store", "data"),
         State("cell-cscan-answer-filter", "value"),
         State("cell-new-cscan-answer-filter", "value"),
         State("cell-final-answer-filter", "value"),
         State("cell-contributing-side-filter", "value"),
         State("cell-new-contributing-side-filter", "value"),
         State("cell-deployed-side-score-filter", "value"),
         State("cell-deployed-score-range-slider", "value"),
         State("cell-new-side-score-filter", "value"),
         State("cell-new-score-range-slider", "value")],
        prevent_initial_call=True
    )
    def apply_cell_user_filters(apply_clicks, reset_clicks, current_filtered_data, cscan_filter, new_cscan_filter, final_filter, side_filter, new_side_filter, deployed_score_side_filter, deployed_score_range, new_score_side_filter, new_score_range):
        """Apply user-selected filters to the already-filtered cell details data"""
        
        ctx = callback_context
        if not ctx.triggered:
            from dash import no_update
            return no_update, no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Reset filters - restore to original matrix-filtered data
        if trigger_id == "cell-reset-filters-btn":
            # This will be handled by the reset callback that restores from original store
            from dash import no_update
            return no_update, 0
        
        # CRITICAL: Only process if apply button was actually clicked (n_clicks > 0)
        # This prevents automatic triggering when the button is re-rendered or reset
        if trigger_id == "cell-apply-filters-btn":
            if not apply_clicks or apply_clicks == 0:
                from dash import no_update
                return no_update, no_update
        
        # Apply filters
        if not current_filtered_data or not isinstance(current_filtered_data, dict):
            return {}, 0
        
        # Extract records from current filtered data (already filtered by matrix click)
        if "data" in current_filtered_data:
            records = current_filtered_data["data"]
        else:
            records = current_filtered_data if isinstance(current_filtered_data, list) else []
        
        if not records:
            return current_filtered_data, 0
        
        # Apply user filters on top of matrix-filtered data
        filtered = records
        
        # Normalize function for comparison
        def normalize_for_comparison(value):
            """Normalize value for comparison (lowercase, strip)"""
            if not value:
                return None
            return str(value).lower().strip()
        
        # Handle CScan Answer filter
        if cscan_filter and len(cscan_filter) > 0:
            normalized_cscan_filter = [normalize_for_comparison(v) for v in cscan_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('cscan_answer', '')) in normalized_cscan_filter
            ]
        
        # Handle New CScan Answer filter
        if new_cscan_filter and len(new_cscan_filter) > 0:
            normalized_new_cscan_filter = [normalize_for_comparison(v) for v in new_cscan_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('new_cscan_answer', '')) in normalized_new_cscan_filter
            ]
        
        # Handle Final Answer filter
        if final_filter and len(final_filter) > 0:
            normalized_final_filter = [normalize_for_comparison(v) for v in final_filter]
            filtered = [
                r for r in filtered 
                if normalize_for_comparison(r.get('final_answer', '')) in normalized_final_filter
            ]
        
        # Handle multi-select for deployed contributing sides
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
        
        # Handle multi-select for new contributing sides
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
        
        # Handle deployed side score filter
        # Filter applies only if range is NOT default [0, 100] OR if specific sides are selected
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
        
        # Return filtered data in same format
        if "data" in current_filtered_data:
            filtered_data = {
                "data": filtered,
                "columns": current_filtered_data.get("columns", []),
                "source": current_filtered_data.get("source", ""),
                "folder_name": current_filtered_data.get("folder_name", "")
            }
        else:
            filtered_data = filtered
        
        return filtered_data, 0
    
    # Reset filters - clear dropdown values and restore original data
    @app.callback(
        [Output("cell-cscan-answer-filter", "value", allow_duplicate=True),
         Output("cell-new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("cell-final-answer-filter", "value", allow_duplicate=True),
         Output("cell-contributing-side-filter", "value", allow_duplicate=True),
         Output("cell-new-contributing-side-filter", "value", allow_duplicate=True),
         Output("cell-deployed-side-score-filter", "value", allow_duplicate=True),
         Output("cell-deployed-score-range-slider", "value", allow_duplicate=True),
         Output("cell-new-side-score-filter", "value", allow_duplicate=True),
         Output("cell-new-score-range-slider", "value", allow_duplicate=True),
         Output("cell-details-filtered-data-store", "data", allow_duplicate=True),
         Output("cell-details-current-page-store", "data", allow_duplicate=True)],
        Input("cell-reset-filters-btn", "n_clicks"),
        State("cell-details-original-filtered-data-store", "data"),
        prevent_initial_call=True
    )
    def reset_cell_filters(n_clicks, original_data):
        """Reset filter dropdown values and restore original matrix-filtered data"""
        if n_clicks:
            if original_data:
                return [], [], [], [], [], [], [0, 100], [], [0, 100], original_data, 0
            else:
                return [], [], [], [], [], [], [0, 100], [], [0, 100], {}, 0
        from dash import no_update
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    # Update title and info based on matrix filters
    @app.callback(
        [Output("cell-detail-title", "children"),
         Output("cell-detail-info", "children")],
        [Input("matrix-filter-cscan", "data"),
         Input("matrix-filter-new-cscan", "data"),
         Input("matrix-filter-final", "data"),
         Input("main-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def update_cell_title(cscan_filter, new_cscan_filter, final_filter, active_tab):
        """Update cell details title based on matrix filters"""
        
        if active_tab != "celldetail":
            return "", "No cell selected"
        
        # Determine which model was used and what values were clicked
        predicted_val = ""
        actual_val = ""
        model_type = ""
        
        if new_cscan_filter and len(new_cscan_filter) > 0:
            predicted_val = new_cscan_filter[0] if isinstance(new_cscan_filter, list) else str(new_cscan_filter)
            model_type = "New Model"
        elif cscan_filter and len(cscan_filter) > 0:
            predicted_val = cscan_filter[0] if isinstance(cscan_filter, list) else str(cscan_filter)
            model_type = "Deployed Model"
        
        if final_filter and len(final_filter) > 0:
            actual_val = final_filter[0] if isinstance(final_filter, list) else str(final_filter)
        
        if predicted_val and actual_val:
            title = f"{predicted_val.title()} → {actual_val.title()}"
            info = f"Model: {model_type} | Predicted: {predicted_val.title()} | Actual: {actual_val.title()}"
        else:
            title = ""
            info = "Click on a confusion matrix cell to view records"
        
        return title, info
    
    # Update stats and record display
    @app.callback(
        [Output("cell-total-records", "children"),
         Output("cell-filtered-records", "children"),
         Output("cell-current-index-display", "children"),
         Output("cell-page-start", "children"),
         Output("cell-page-end", "children"),
         Output("cell-total-filtered", "children"),
         Output("cell-accuracy", "children"),
         Output("cell-record-display", "children")],
        [Input("cell-details-filtered-data-store", "data"),
         Input("cell-details-current-page-store", "data"),
         Input("image-toggle-state-store", "data"),
         Input("audit-tags-store", "data")],  # Use shared audit store
        [State("data-store", "data"),
         State("matrix-filter-cscan", "data"),
         State("matrix-filter-new-cscan", "data"),
         State("matrix-filter-final", "data")],
        prevent_initial_call=True
    )
    def update_cell_display(filtered_data, current_page, image_toggle_states, audit_tags, total_data, cscan_filter, new_cscan_filter, final_filter):
        """Update cell details display with filtered records"""
        
        # Get total records count
        if total_data and isinstance(total_data, dict) and "data" in total_data:
            total_count = len(total_data["data"])
        elif total_data and isinstance(total_data, list):
            total_count = len(total_data)
        else:
            total_count = 0
        
        # Get filtered records
        if not filtered_data or not isinstance(filtered_data, dict):
            return (str(total_count), "0", "0", "0", "0", "0", "N/A",
                    html.Div("No data loaded. Please click on a confusion matrix cell.", className="text-center text-muted py-5"))
        
        if "data" in filtered_data:
            records = filtered_data["data"]
        else:
            records = filtered_data if isinstance(filtered_data, list) else []
        
        filtered_count = len(records)
        
        if filtered_count == 0:
            return (str(total_count), "0", "0", "1", "0", "0", "N/A",
                    html.Div([
                        html.H3("No records match this cell", className="text-center text-muted"),
                        html.P("Try clicking a different confusion matrix cell", className="text-center text-muted")
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
        
        # Calculate accuracy based on which model was used
        if new_cscan_filter and len(new_cscan_filter) > 0:
            # New model: compare new_cscan_answer with final_answer
            correct = sum(1 for r in records if str(r.get('new_cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        elif cscan_filter and len(cscan_filter) > 0:
            # Old model: compare cscan_answer with final_answer
            correct = sum(1 for r in records if str(r.get('cscan_answer', '')).lower() == str(r.get('final_answer', '')).lower())
        else:
            correct = 0
        
        accuracy = f"{(correct / filtered_count * 100):.2f}%" if filtered_count > 0 else "N/A"
        
        # Note: Image toggle state is handled by update_image_toggle_state callback in image_viewer
        # No need to manually handle it here - it will trigger this callback via image-toggle-state-store
        
        # Get audit options from cscan filter options (reuse from image viewer logic)
        audit_options = []
        if total_data and isinstance(total_data, dict) and "data" in total_data:
            all_records = total_data["data"]
            audit_values = set()
            for record in all_records:
                if record.get('cscan_answer'):
                    audit_values.add(str(record['cscan_answer']))
            audit_options = [{"label": str(v), "value": str(v)} for v in sorted(audit_values)]
        
        # Create accordion view with 10 records (reuse from image_viewer)
        accordion_display = create_accordion_view(
            records,
            current_page,
            image_toggle_states or {},
            audit_tags or {},
            audit_options
        )
        
        return (
            str(total_count),
            str(filtered_count),
            str(start_idx + 1),  # current-index-display
            str(start_idx + 1),  # page-start
            str(end_idx),  # page-end
            str(filtered_count),  # total-filtered
            accuracy,
            accordion_display
        )
    
    # Navigation buttons (for pages)
    @app.callback(
        Output("cell-details-current-page-store", "data", allow_duplicate=True),
        [Input("cell-first-btn", "n_clicks"),
         Input("cell-prev-btn", "n_clicks"),
         Input("cell-next-btn", "n_clicks"),
         Input("cell-last-btn", "n_clicks")],
        [State("cell-details-filtered-data-store", "data"),
         State("cell-details-current-page-store", "data")],
        prevent_initial_call=True
    )
    def navigate_cell_records(first_clicks, prev_clicks, next_clicks, last_clicks, filtered_data, current_page):
        """Navigate pages in cell details"""
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
        if trigger_id == "cell-first-btn":
            return 0
        elif trigger_id == "cell-prev-btn":
            return max(0, current_page - 1)
        elif trigger_id == "cell-next-btn":
            return min(total_pages - 1, current_page + 1)
        elif trigger_id == "cell-last-btn":
            return total_pages - 1
        
        return current_page or 0
    
    # Note: Row expand/collapse is handled by the clientside callback in image_viewer
    # which uses pattern matching, so it works for both tabs automatically
    
    # Collapse rows only when filtering/pagination changes (not when image toggle changes)
    # This ensures rows stay expanded when toggling images in cell details
    app.clientside_callback(
        """
        function(filtered_data, current_page) {
            // Clear preserved expanded rows when filtering/pagination changes
            if (window.preservedExpandedRowsCell) {
                window.preservedExpandedRowsCell.clear();
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
        [Input("cell-details-filtered-data-store", "data"),
         Input("cell-details-current-page-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    
    # Preserve expanded rows when cell-record-display is re-rendered due to toggle state changes
    # This prevents rows from collapsing when toggle buttons are clicked in cell details
    app.clientside_callback(
        """
        function(record_display, image_toggle_states) {
            // Initialize preserved rows set if it doesn't exist (separate from image viewer)
            if (!window.preservedExpandedRowsCell) {
                window.preservedExpandedRowsCell = new Set();
            }
            
            // Before DOM changes, capture currently expanded rows
            // Use requestAnimationFrame to ensure we capture state before DOM updates
            const captureExpandedRows = function() {
                const allExpandedRows = document.querySelectorAll('[id^="row-expanded-"]');
                allExpandedRows.forEach(function(row) {
                    if (row) {
                        const computedStyle = window.getComputedStyle(row);
                        const isVisible = computedStyle.display === 'table-row' || 
                                         row.style.display === 'table-row' ||
                                         row.offsetHeight > 0;
                        if (isVisible) {
                            const match = row.id.match(/row-expanded-(\\d+)/);
                            if (match) {
                                const index = match[1];
                                window.preservedExpandedRowsCell.add(index);
                            }
                        }
                    }
                });
            };
            
            // Capture before any potential DOM changes
            captureExpandedRows();
            
            // Also capture after a micro-delay to catch any rows that might be expanded
            setTimeout(captureExpandedRows, 10);
            
            // After DOM updates, restore expanded rows with multiple attempts for reliability
            const restoreExpandedRows = function(attempt) {
                attempt = attempt || 1;
                if (window.preservedExpandedRowsCell && window.preservedExpandedRowsCell.size > 0) {
                    let restoredCount = 0;
                    window.preservedExpandedRowsCell.forEach(function(index) {
                        const expandedRow = document.getElementById('row-expanded-' + index);
                        const arrow = document.getElementById('arrow-' + index);
                        if (expandedRow && arrow) {
                            expandedRow.style.display = 'table-row';
                            arrow.style.transform = 'rotate(90deg)';
                            restoredCount++;
                        }
                    });
                    
                    // If not all rows were restored and we haven't tried too many times, try again
                    if (restoredCount < window.preservedExpandedRowsCell.size && attempt < 5) {
                        setTimeout(function() {
                            restoreExpandedRows(attempt + 1);
                        }, 50);
                    }
                }
            };
            
            // Restore after DOM updates (multiple attempts for reliability)
            setTimeout(function() {
                restoreExpandedRows(1);
            }, 50);
            
            setTimeout(function() {
                restoreExpandedRows(2);
            }, 150);
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("audit-tags-store", "data", allow_duplicate=True),
        [Input("cell-record-display", "children"),
         Input("image-toggle-state-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    
    # Note: Audit dropdown changes are handled by the callback in image_viewer
    # which uses pattern matching, so it works for both tabs automatically
    # We use the shared audit-tags-store for consistency
    
    # Export audit CSV for cell details
    @app.callback(
        [Output("cell-download-audit-csv", "data"),
         Output("cell-audit-status", "children")],
        Input("cell-export-audit-btn", "n_clicks"),
        [State("cell-details-filtered-data-store", "data"),
         State("audit-tags-store", "data")],
        prevent_initial_call=True
    )
    def export_cell_audit_csv(n_clicks, filtered_data_store, audit_tags):
        """Export audited records from cell details to CSV"""
        import pandas as pd
        from io import StringIO
        
        if not audit_tags or len(audit_tags) == 0:
            return no_update, html.Span("⚠️ No records audited yet!", style={"color": "#dc2626"})
        
        # Get filtered records (only records in this cell)
        if not filtered_data_store or not isinstance(filtered_data_store, dict):
            return no_update, html.Span("⚠️ No data loaded!", style={"color": "#dc2626"})
        
        if "data" in filtered_data_store:
            records = filtered_data_store["data"]
        else:
            records = filtered_data_store if isinstance(filtered_data_store, list) else []
        
        if not records:
            return no_update, html.Span("⚠️ No data loaded!", style={"color": "#dc2626"})
        
        # Filter to audited records and add audit_tag column
        audited_records = []
        for record in records:
            txn_id = record.get('pdd_txn_id', '')
            if txn_id in audit_tags:
                # Add audit_tag to record
                record_copy = record.copy()
                record_copy['audit_tag'] = audit_tags[txn_id]
                audited_records.append(record_copy)
        
        if not audited_records:
            return no_update, html.Span("⚠️ No audited records in this cell!", style={"color": "#dc2626"})
        
        # Create DataFrame
        df = pd.DataFrame(audited_records)
        
        # Ensure audit_tag is the last column
        cols = [c for c in df.columns if c != 'audit_tag'] + ['audit_tag']
        df = df[cols]
        
        # Convert to CSV
        csv_string = df.to_csv(index=False)
        
        from datetime import datetime
        filename = f"cell_audit_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return (
            dict(content=csv_string, filename=filename),
            html.Span(f"✅ Exported {len(audited_records)} records!", style={"color": "#059669"})
        )
    
    # Note: Copy request body callback is handled in image_viewer.py
    # It checks both filtered-data-store and cell-details-filtered-data-store
    # so it works for both image viewer and cell details pages
    
    # Back to matrix button
    @app.callback(
        Output("main-tabs", "active_tab", allow_duplicate=True),
        Input("back-to-matrix-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def back_to_matrix(n_clicks):
        """Navigate back to matrix tab"""
        if n_clicks:
            return "matrix"
        return no_update
