"""
Threshold Tweaker Tab Component for Analysis Dashboard
Allows users to adjust thresholds and see real-time impact on confusion matrix
with full analysis capabilities similar to Image Viewer
"""

from dash import html, dcc, Input, Output, State, callback_context, ALL, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pathlib import Path
import sys
import pandas as pd
import copy
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.data_loader import prepare_matrix_data, create_confusion_matrix_plot
from utils.threshold_handler import (
    load_threshold_config,
    get_category_from_score,
    get_severity_order_from_thresholds,
    get_category_order_from_threshold,
    normalize_category_for_confusion_matrix
)
from components.image_viewer import create_accordion_view, create_record_display_with_audit


def validate_and_adjust_thresholds(side_thresholds: dict) -> dict:
    """
    Validate and adjust thresholds to ensure:
    1. No gaps: thresholds cover entire 0-100 range continuously
    2. No overlaps: each category's max equals next category's min
    3. First category starts at 0, last category ends at 100
    
    Args:
        side_thresholds: Dict mapping category names to [min, max] lists
        
    Returns:
        Adjusted side_thresholds dict with validated thresholds
    """
    if not side_thresholds:
        return side_thresholds
    
    # Get category order from dict keys (preserves insertion order from threshold.json)
    categories = list(side_thresholds.keys())
    
    if len(categories) == 0:
        return side_thresholds
    
    # Special case: only one category
    if len(categories) == 1:
        return {categories[0]: [0, 100]}
    
    # Create a copy to avoid modifying original
    adjusted_thresholds = {}
    
    # Step 1: Ensure first category starts at 0
    first_category = categories[0]
    first_min, first_max = side_thresholds[first_category]
    # Clamp first_max to valid range, but ensure it's at least 1
    first_max = max(1, min(100, first_max))
    adjusted_thresholds[first_category] = [0, first_max]
    
    # Step 2: Build continuous thresholds for middle categories
    # Process from first to second-to-last category
    for i in range(1, len(categories) - 1):
        category = categories[i]
        prev_category = categories[i-1]
        
        # Previous category's max becomes this category's min
        prev_min, prev_max = adjusted_thresholds[prev_category]
        adjusted_min = prev_max
        
        # Use original max from user's input, but ensure it's valid
        original_min, original_max = side_thresholds[category]
        # Adjusted max should be at least min + 1, and at most 100
        # We'll let the last category handle the final adjustment
        adjusted_max = max(adjusted_min + 1, min(100, original_max))
        
        adjusted_thresholds[category] = [int(adjusted_min), int(adjusted_max)]
    
    # Step 3: Ensure last category ends at 100
    last_category = categories[-1]
    prev_category = categories[-2]
    
    # Previous category's max becomes this category's min
    prev_min, prev_max = adjusted_thresholds[prev_category]
    adjusted_min = prev_max
    
    # Last category must end at 100
    adjusted_max = 100
    
    # Ensure min < max
    if adjusted_min >= adjusted_max:
        # If previous category's max is >= 100, we need to adjust it
        # Move the boundary back
        adjusted_min = max(0, 99)
        adjusted_thresholds[prev_category] = [adjusted_thresholds[prev_category][0], int(adjusted_min)]
    
    adjusted_thresholds[last_category] = [int(adjusted_min), 100]
    
    return adjusted_thresholds


def create_threshold_tweaker_tab():
    """Create the Threshold Tweaker tab layout with Image Viewer-like UI/UX"""
    
    return dbc.Container([
        # Header Card - matching confusion matrix tab style
        dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    # Title and Description on Left
                    dbc.Col([
                        html.H2("🎛️ Threshold Tweaker", className="mb-2", style={
                    "fontWeight": "700",
                    "fontSize": "2em",
                    "letterSpacing": "-0.5px"
                }),
                html.P([
                    html.I(className="fas fa-sliders-h me-2"),
                    "Adjust thresholds and see real-time impact on confusion matrix"
                        ], className="mb-0", style={
                    "fontSize": "1.1em",
                    "fontWeight": "500",
                    "opacity": "0.95"
                        })
                    ], md=9),
                    # Model Toggle on Right
                    dbc.Col([
                    dbc.ButtonGroup([
                            dbc.Button(
                                "📊 Deployed Model", 
                                id="tweaker-old-model-btn", 
                                outline=True, 
                                color="light", 
                                size="md",
                                className="tweaker-model-btn",
                                active=True,  # Default to deployed model
                                style={
                                    "backgroundColor": "#1e40af",
                                    "borderColor": "#1e40af",
                                    "color": "white",
                                    "fontWeight": "700",
                                    "boxShadow": "0 4px 12px rgba(30, 64, 175, 0.4)",
                                    "transition": "all 0.3s ease",
                                    "whiteSpace": "nowrap"
                                },
                                title="Deployed Model (CScan vs Final)"
                            ),
                            dbc.Button(
                                "⚡ New Model", 
                                id="tweaker-new-model-btn", 
                                outline=True,
                                color="light", 
                                size="md",
                                className="tweaker-model-btn",
                                active=False,  # Default to deployed model
                                style={
                                    "backgroundColor": "white",
                                    "borderColor": "white",
                                    "color": "#1e40af",
                                    "fontWeight": "600",
                                    "transition": "all 0.3s ease",
                                    "whiteSpace": "nowrap"
                                },
                                title="New Model (New CScan vs Final)"
                            )
                        ], style={"whiteSpace": "nowrap"})
                    ], md=3, className="d-flex justify-content-end")
                ], className="align-items-center")
            ], style={"padding": "2rem"})
        ], className="mb-4", style={
            "background": "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)", 
            "color": "white",
            "border": "none",
            "borderRadius": "12px",
            "boxShadow": "0 8px 16px rgba(30, 64, 175, 0.2)"
        }),
        
        # Dual Matrix View
        dbc.Row([
            # Reference Matrix (Left)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3(
                            id="tweaker-ref-matrix-header",
                            children="Deployed Model (Reference Matrix)",
                            className="mb-0", 
                            style={"fontSize": "1.5em", "fontWeight": "600", "color": "#1e293b"}
                        ),
                        style={
                            "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                            "borderBottom": "3px solid #3b82f6",
                            "padding": "1.2rem"
                        }
                    ),
                    dbc.CardBody([
                        html.Div(id="tweaker-reference-matrix", style={"minHeight": "500px"}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Span("Accuracy: ", className="fw-bold me-2"),
                                    html.Span("0%", id="tweaker-ref-accuracy", style={"color": "#3b82f6", "fontSize": "1.2em", "fontWeight": "600"})
                                ])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.Span("Samples: ", className="fw-bold me-2"),
                                    html.Span("0", id="tweaker-ref-total", style={"color": "#3b82f6", "fontSize": "1.2em", "fontWeight": "600"})
                                ])
                            ], md=6),
                        ])
                    ])
                ], className="shadow-sm")
            ], md=6),
            
            # Adjusted Matrix (Right)
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3(
                            id="tweaker-adj-matrix-header",
                            children="Deployed Model (Adjusted Matrix)",
                            className="mb-0", 
                            style={"fontSize": "1.5em", "fontWeight": "600", "color": "#1e293b"}
                        ),
                        style={
                        "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                            "borderBottom": "3px solid #3b82f6",
                            "padding": "1.2rem"
                        }
                    ),
                    dbc.CardBody([
                        html.Div(id="tweaker-adjusted-matrix", style={"minHeight": "500px"}),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Span("Accuracy: ", className="fw-bold me-2"),
                                    html.Span("0%", id="tweaker-adj-accuracy", style={"color": "#3b82f6", "fontSize": "1.2em", "fontWeight": "600"})
                                ])
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.Span("Samples: ", className="fw-bold me-2"),
                                    html.Span("0", id="tweaker-adj-total", style={"color": "#3b82f6", "fontSize": "1.2em", "fontWeight": "600"})
                                ])
                            ], md=6),
                        ]),
                        # Hidden element for tweaker-changed (used by callbacks but not displayed)
                        html.Div(id="tweaker-changed", style={"display": "none"})
                    ])
                ], className="shadow-sm")
            ], md=6),
        ], className="mb-4"),
        
        # Threshold Controls Panel
        dbc.Card([
            dbc.CardHeader(
                html.H3("⚙️ Adjust Thresholds", className="mb-0", style={
                    "color": "#1e40af", 
                    "fontWeight": "600",
                    "fontSize": "1.5em"
                }),
                style={
                    "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                    "borderBottom": "3px solid #3b82f6",
                    "padding": "1.2rem"
                }
            ),
            dbc.CardBody([
                # Impact Summary
                html.H5("📊 Impact Summary", className="mb-3", style={"color": "#3b82f6"}),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("Records Changed: ", className="fw-bold me-2"),
                            html.Span("0", id="impact-changed", style={"color": "#3b82f6", "fontSize": "1.3em", "fontWeight": "700"})
                        ])
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.Span("Accuracy Delta: ", className="fw-bold me-2"),
                            html.Span("0%", id="impact-delta", style={"color": "#3b82f6", "fontSize": "1.3em", "fontWeight": "700"})
                        ])
                    ], md=4),
                    dbc.Col([
                        html.Div([
                            html.Span("Original Accuracy: ", className="fw-bold me-2"),
                            html.Span("0%", id="impact-original", style={"color": "#3b82f6", "fontSize": "1.3em", "fontWeight": "700"})
                        ])
                    ], md=4),
                ], className="mb-3"),
                
                # Action Buttons
                dbc.Row([
                    dbc.Col([
                        dbc.Button("🎯 Optimize Thresholds", id="optimize-all-thresholds-btn", color="primary", className="me-2"),
                        dbc.Button("🎯 Optimize Selected Side", id="optimize-selected-side-btn", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset to Original", id="reset-thresholds-btn", color="warning", className="me-2"),
                        # Loading indicator (hidden by default)
                        html.Div(id="optimization-loading", style={"display": "none"}, children=[
                            dbc.Spinner(html.Div(id="optimization-status"), size="sm", color="primary"),
                            html.Span("Optimizing thresholds...", className="ms-2", style={"color": "#3b82f6"})
                        ])
                    ], className="d-flex align-items-center")
                ], className="mb-4"),
                
                html.Hr(),
                
                # Side Selector
                html.Label("Select Side:", className="fw-bold mb-3", style={"color": "#3b82f6", "fontSize": "1.1em"}),
                dbc.ButtonGroup([
                    dbc.Button("Back", id={"type": "tweaker-side-selector", "side": "back"}, outline=True, color="primary", size="sm", active=True),
                    dbc.Button("Left", id={"type": "tweaker-side-selector", "side": "left"}, outline=True, color="primary", size="sm"),
                    dbc.Button("Right", id={"type": "tweaker-side-selector", "side": "right"}, outline=True, color="primary", size="sm"),
                    dbc.Button("Top", id={"type": "tweaker-side-selector", "side": "top"}, outline=True, color="primary", size="sm"),
                    dbc.Button("Bottom", id={"type": "tweaker-side-selector", "side": "bottom"}, outline=True, color="primary", size="sm"),
                ], className="mb-4"),
                
                # Threshold Sliders
                html.Div(id="threshold-sliders")
            ])
        ], className="mb-4 shadow-sm"),
        
        # Filters for Changed Records (similar to Image Viewer)
        dbc.Card([
            dbc.CardBody([
                html.H3("🎯 Filters", className="mb-3", style={"color": "#3b82f6"}),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed CScan Answer", html_for="tweaker-cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="tweaker-cscan-answer-filter",
                            options=[],
                            value=[],
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("New CScan Answer", html_for="tweaker-new-cscan-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="tweaker-new-cscan-answer-filter",
                            options=[],
                            value=[],
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                    dbc.Col([
                        dbc.Label("Final Answer", html_for="tweaker-final-answer-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="tweaker-final-answer-filter",
                            options=[],
                            value=[],
                            placeholder="All answers (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=4),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Contributing Sides", html_for="tweaker-contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="tweaker-contributing-side-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"},
                                {"label": "Blank", "value": "_blank_"}
                            ],
                            value=[],
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("New Contributing Sides", html_for="tweaker-new-contributing-side-filter", className="fw-bold"),
                        dcc.Dropdown(
                            id="tweaker-new-contributing-side-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"},
                                {"label": "Blank", "value": "_blank_"}
                            ],
                            value=[],
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Deployed Side Score Filter", html_for="tweaker-deployed-score-range-slider", className="fw-bold"),
                        dcc.RangeSlider(
                            id="tweaker-deployed-score-range-slider",
                            min=0,
                            max=100,
                            step=0.1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="tweaker-deployed-side-score-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                    dbc.Col([
                        dbc.Label("New Side Score Filter", html_for="tweaker-new-score-range-slider", className="fw-bold"),
                        dcc.RangeSlider(
                            id="tweaker-new-score-range-slider",
                            min=0,
                            max=100,
                            step=0.1,
                            value=[0, 100],
                            marks={i: str(i) for i in range(0, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": False}
                        ),
                        dcc.Dropdown(
                            id="tweaker-new-side-score-filter",
                            options=[
                                {"label": "Top", "value": "top"},
                                {"label": "Bottom", "value": "bottom"},
                                {"label": "Left", "value": "left"},
                                {"label": "Right", "value": "right"},
                                {"label": "Back", "value": "back"},
                                {"label": "Front", "value": "front"}
                            ],
                            value=[],
                            placeholder="All sides (filter off)",
                            clearable=True,
                            multi=True
                        ),
                    ], md=6),
                ], className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        dbc.Button("🔍 Apply Filters", id="tweaker-apply-filters-btn", color="primary", className="me-2"),
                        dbc.Button("🔄 Reset Filters", id="tweaker-reset-filters-btn", color="warning", className="me-2"),
                    ], className="d-flex"),
                ]),
            ])
        ], className="mb-4", style={"background": "linear-gradient(to bottom, #f8fafc, #f1f5f9)"}),
        
        # Changed Records Display (similar to Image Viewer) - visible by default
        html.Div(id="tweaker-changed-records-display", children=[
        html.Div([
                html.Div(className="spinner"),
                html.P("Loading changed records...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        ]),
        
    ], fluid=True, className="tab-content-container")


def register_threshold_tweaker_callbacks(app):
    """Register callbacks for threshold tweaker tab"""
    
    # Show loading indicator when optimization buttons are clicked
    @app.callback(
        Output("optimization-loading", "style", allow_duplicate=True),
        [Input("optimize-all-thresholds-btn", "n_clicks"),
         Input("optimize-selected-side-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def show_optimization_loader(optimize_all_clicks, optimize_side_clicks):
        """Show loading indicator immediately when optimization button is clicked"""
        ctx = callback_context
        if not ctx.triggered:
            return {"display": "none"}
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id in ["optimize-all-thresholds-btn", "optimize-selected-side-btn"]:
            print(f"📊 Showing optimization loader for {trigger_id}")
            return {"display": "flex", "alignItems": "center", "gap": "10px"}
        
        return {"display": "none"}
    
    # Model toggle - handle clicks (only updates model store, button states handled by initialize callback)
    @app.callback(
        Output("tweaker-model-store", "data", allow_duplicate=True),
        [Input("tweaker-old-model-btn", "n_clicks"),
         Input("tweaker-new-model-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def switch_tweaker_model(old_clicks, new_clicks):
        """Switch between old and new model - only updates the model store"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == "tweaker-old-model-btn":
            print("🔄 Switched to Deployed Model")
            return "old"
        else:
            print("🔄 Switched to New Model")
            return "new"
    
    # Update model toggle button states based on model store
    @app.callback(
        [Output("tweaker-old-model-btn", "active", allow_duplicate=True),
         Output("tweaker-old-model-btn", "style", allow_duplicate=True),
         Output("tweaker-new-model-btn", "active", allow_duplicate=True),
         Output("tweaker-new-model-btn", "style", allow_duplicate=True)],
        [Input("tweaker-model-store", "data"),
         Input("main-tabs", "active_tab")],
        prevent_initial_call='initial_duplicate'
    )
    def update_model_toggle_buttons(model, active_tab):
        """Update model toggle button states based on model store value"""
        # Only update when on tweaker tab
        if active_tab != "tweaker":
            return no_update, no_update, no_update, no_update
        
        # Normalize model value
        if not model:
            model = "old"  # Default to deployed model
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid
        
        if model == "old":
            old_style = {
                "backgroundColor": "#1e40af",
                "borderColor": "#1e40af",
                "color": "white",
                "fontWeight": "700",
                "boxShadow": "0 4px 12px rgba(30, 64, 175, 0.4)",
                "transition": "all 0.3s ease",
                "whiteSpace": "nowrap"
            }
            new_style = {
                "backgroundColor": "white",
                "borderColor": "white",
                "color": "#1e40af",
                "fontWeight": "600",
                "transition": "all 0.3s ease",
                "whiteSpace": "nowrap"
            }
            return True, old_style, False, new_style
        else:
            old_style = {
                "backgroundColor": "white",
                "borderColor": "white",
                "color": "#1e40af",
                "fontWeight": "600",
                "transition": "all 0.3s ease",
                "whiteSpace": "nowrap"
            }
            new_style = {
                "backgroundColor": "#1e40af",
                "borderColor": "#1e40af",
                "color": "white",
                "fontWeight": "700",
                "boxShadow": "0 4px 12px rgba(30, 64, 175, 0.4)",
                "transition": "all 0.3s ease",
                "whiteSpace": "nowrap"
            }
            return False, old_style, True, new_style
    
    # Side selector
    @app.callback(
        [Output("tweaker-current-side-store", "data"),
         Output({"type": "tweaker-side-selector", "side": ALL}, "active")],
        Input({"type": "tweaker-side-selector", "side": ALL}, "n_clicks"),
        State("tweaker-current-side-store", "data"),
        prevent_initial_call=True
    )
    def select_side_tweaker(n_clicks_list, current_side):
        """Select side for threshold adjustment"""
        ctx = callback_context
        if not ctx.triggered:
            return current_side, [False] * len(n_clicks_list)
        
        trigger = ctx.triggered[0]['prop_id']
        import json
        trigger_dict = json.loads(trigger.split('.')[0])
        selected_side = trigger_dict.get('side')
        
        # Create active states for all buttons
        sides = ['back', 'left', 'right', 'top', 'bottom']
        active_states = [s == selected_side for s in sides]
        
        print(f"🎯 Selected side: {selected_side}")
        return selected_side, active_states
    
    # Initialize matrices on first load (only when tweaker tab is active)
    @app.callback(
        [Output("tweaker-reference-matrix", "children", allow_duplicate=True),
         Output("tweaker-adjusted-matrix", "children", allow_duplicate=True),
         Output("tweaker-ref-accuracy", "children", allow_duplicate=True),
         Output("tweaker-ref-total", "children", allow_duplicate=True),
         Output("tweaker-adj-accuracy", "children", allow_duplicate=True),
         Output("tweaker-adj-total", "children", allow_duplicate=True),
         Output("tweaker-changed", "children", allow_duplicate=True),
         Output("impact-changed", "children", allow_duplicate=True),
         Output("impact-delta", "children", allow_duplicate=True),
         Output("impact-original", "children", allow_duplicate=True),
         Output("tweaker-ref-matrix-header", "children", allow_duplicate=True),
         Output("tweaker-adj-matrix-header", "children", allow_duplicate=True),
         Output("adjusted-thresholds-store", "data", allow_duplicate=True)],
        [Input("main-tabs", "active_tab"),
         Input("data-store", "data"),
         Input("threshold-config-store", "data")],
        [State("tweaker-model-store", "data"),
         State("adjusted-thresholds-store", "data")],
        prevent_initial_call='initial_duplicate'
    )
    def initialize_tweaker_matrices(active_tab, data, threshold_config, model, adjusted_thresholds):
        """Initialize matrices when data is first loaded and tweaker tab is active"""
        
        # Only initialize if we're on the tweaker tab - check this FIRST
        if active_tab != "tweaker":
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        if not threshold_config or not data:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        # Initialize adjusted thresholds to original if not set
        if not adjusted_thresholds:
            adjusted_thresholds = copy.deepcopy(threshold_config)
        
        # Normalize model value FIRST - handle None and ensure it's either "old" or "new"
        # This ensures we use the correct model from the start
        if not model:
            model = "old"  # Default to deployed model if not set
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid value
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    break
        
        if not question_name:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update
        
        # Determine model name for headers
        model_name = "Deployed Model" if model == "old" else "New Model"
        ref_header = f"{model_name} (Reference Matrix)"
        adj_header = f"{model_name} (Adjusted Matrix)"
        
        # Recalculate and return matrices
        results = recalculate_and_update_matrices(
            data, threshold_config, adjusted_thresholds, question_name, model
        )
        
        # Return results plus headers and adjusted_thresholds
        return results + (ref_header, adj_header, adjusted_thresholds,)
    
    # Load threshold inputs for selected side
    @app.callback(
        Output("threshold-sliders", "children"),
        [Input("tweaker-current-side-store", "data"),
         Input("threshold-config-store", "data"),
         Input("tweaker-model-store", "data"),
         Input("adjusted-thresholds-store", "data")],
        [State("data-store", "data")],
        prevent_initial_call=False
    )
    def load_threshold_sliders(selected_side, threshold_config, model, adjusted_thresholds, data):
        """Load threshold input boxes for the selected side"""
        
        if not threshold_config:
            return html.Div("No threshold configuration loaded", className="text-muted")
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        # This ensures we use the correct question that was selected when generating the report
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
            if question_name:
                print(f"✓ load_threshold_sliders: Using question_name from data-store: {question_name}")
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    print(f"⚠️ load_threshold_sliders: Question name not in data-store, detected from threshold_config: {question_name}")
                    break
        
        if not question_name:
            return html.Div("No question configuration found", className="text-muted")
        
        # Use adjusted thresholds if available, otherwise use original
        if adjusted_thresholds and question_name in adjusted_thresholds:
            question_thresholds = adjusted_thresholds[question_name]
        else:
            question_thresholds = threshold_config.get(question_name, {})
        
        if selected_side not in question_thresholds:
            return html.Div(f"No thresholds available for {selected_side} side", className="text-muted")
        
        side_thresholds = question_thresholds[selected_side]
        categories = list(side_thresholds.keys())
        
        sliders = []
        for category in categories:
            min_val, max_val = side_thresholds[category]
            
            slider_group = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Span(category, className="fw-bold", style={"fontSize": "1.1em", "color": "#1e40af"}),
                        html.Span(id={"type": "tweaker-value-display", "side": selected_side, "category": category},
                                 children=f" [{int(min_val)}, {int(max_val)}]",
                                 className="ms-2", style={"color": "#3b82f6", "fontWeight": "600"})
                    ], className="mb-3"),
                    
                    dcc.RangeSlider(
                        id={"type": "threshold-range-slider", "side": selected_side, "category": category},
                                min=0,
                                max=100,
                                step=1,
                        value=[int(min_val), int(max_val)],
                        marks={i: str(i) for i in range(0, 101, 20)},
                        tooltip={"placement": "bottom", "always_visible": False}
                    )
                ])
            ], className="mb-3")
            
            sliders.append(slider_group)
        
        return html.Div(sliders)
    
    # Update threshold values from range sliders
    @app.callback(
        Output("adjusted-thresholds-store", "data", allow_duplicate=True),
        Input({"type": "threshold-range-slider", "side": ALL, "category": ALL}, "value"),
        [State("threshold-config-store", "data"),
         State("adjusted-thresholds-store", "data"),
         State({"type": "threshold-range-slider", "side": ALL, "category": ALL}, "id"),
         State("main-tabs", "active_tab"),
         State("data-store", "data")],
        prevent_initial_call=True
    )
    def update_thresholds_from_sliders(slider_values, threshold_config, adjusted_thresholds, slider_ids, active_tab, data):
        """Update thresholds from range slider values"""
        
        # Only update if we're on the tweaker tab
        if active_tab != "tweaker":
            return no_update
        
        if not threshold_config:
            return no_update
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        # This ensures we use the correct question that was selected when generating the report
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    break
        
        if not question_name:
            return no_update
        
        # Initialize adjusted thresholds if needed
        if not adjusted_thresholds:
            adjusted_thresholds = copy.deepcopy(threshold_config)
        elif question_name not in adjusted_thresholds:
            adjusted_thresholds = copy.deepcopy(threshold_config)
        
        # Update thresholds based on slider IDs and values
        question_thresholds = adjusted_thresholds.get(question_name, {})
        
        # Track which sides were modified
        modified_sides = set()
        
        for slider_id, slider_value in zip(slider_ids, slider_values):
            if slider_value is None or not isinstance(slider_value, list) or len(slider_value) != 2:
                continue
            
            try:
                min_val = max(0, min(100, int(float(slider_value[0]))))
                max_val = max(0, min(100, int(float(slider_value[1]))))
                
                # Ensure min < max (for integers, subtract/add 1)
                if min_val >= max_val:
                    min_val = max(0, max_val - 1)
                    max_val = min(100, min_val + 1)
            except (ValueError, TypeError, IndexError):
                continue
            
            side = slider_id.get('side')
            category = slider_id.get('category')
            
            if side and category and side in question_thresholds:
                if category in question_thresholds[side]:
                    question_thresholds[side][category] = [int(min_val), int(max_val)]
                    modified_sides.add(side)
        
        # Validate and adjust thresholds for all modified sides
        for side in modified_sides:
            if side in question_thresholds:
                original_thresholds = copy.deepcopy(question_thresholds[side])
                validated_thresholds = validate_and_adjust_thresholds(question_thresholds[side])
                question_thresholds[side] = validated_thresholds
                
                # Log if adjustments were made
                if original_thresholds != validated_thresholds:
                    print(f"✅ Validated and adjusted thresholds for {question_name}/{side}")
                    for cat in validated_thresholds:
                        orig = original_thresholds.get(cat, [0, 0])
                        new = validated_thresholds[cat]
                        if orig != new:
                            print(f"   {cat}: {orig} → {new}")
        
        print(f"🔧 Updated thresholds for {question_name}")
        return adjusted_thresholds
    
    # Update threshold value display text
    @app.callback(
        Output({"type": "tweaker-value-display", "side": ALL, "category": ALL}, "children", allow_duplicate=True),
        Input("adjusted-thresholds-store", "data"),
        [State("tweaker-current-side-store", "data"),
         State("threshold-config-store", "data"),
         State("data-store", "data")],
        prevent_initial_call=True
    )
    def update_threshold_value_display(adjusted_thresholds, current_side, threshold_config, data):
        """Update the threshold value display text when thresholds change"""
        
        if not adjusted_thresholds or not threshold_config:
            return no_update
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        # This ensures we use the correct question that was selected when generating the report
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    break
        
        if not question_name or question_name not in adjusted_thresholds:
            return no_update
        
        question_thresholds = adjusted_thresholds.get(question_name, {})
        if current_side not in question_thresholds:
            return no_update
        
        side_thresholds = question_thresholds[current_side]
        categories = list(side_thresholds.keys())
        
        displays = []
        for category in categories:
            min_val, max_val = side_thresholds[category]
            displays.append(f" [{int(min_val)}, {int(max_val)}]")
        
        return displays
    
    # Recalculate and update matrices when thresholds or model changes
    @app.callback(
        [Output("tweaker-reference-matrix", "children", allow_duplicate=True),
         Output("tweaker-adjusted-matrix", "children", allow_duplicate=True),
         Output("tweaker-ref-accuracy", "children", allow_duplicate=True),
         Output("tweaker-ref-total", "children", allow_duplicate=True),
         Output("tweaker-adj-accuracy", "children", allow_duplicate=True),
         Output("tweaker-adj-total", "children", allow_duplicate=True),
         Output("tweaker-changed", "children", allow_duplicate=True),
         Output("impact-changed", "children", allow_duplicate=True),
         Output("impact-delta", "children", allow_duplicate=True),
         Output("impact-original", "children", allow_duplicate=True),
         Output("tweaker-ref-matrix-header", "children", allow_duplicate=True),
         Output("tweaker-adj-matrix-header", "children", allow_duplicate=True),
         Output("adjusted-thresholds-store", "data", allow_duplicate=True),
         Output("optimization-loading", "style", allow_duplicate=True)],
        [Input("main-tabs", "active_tab"),
         Input("adjusted-thresholds-store", "data"),
         Input("reset-thresholds-btn", "n_clicks"),
         Input("optimize-all-thresholds-btn", "n_clicks"),
         Input("optimize-selected-side-btn", "n_clicks"),
         Input("tweaker-model-store", "data")],
        [State("threshold-config-store", "data"),
         State("data-store", "data"),
         State("tweaker-current-side-store", "data")],
        prevent_initial_call=True
    )
    def recalculate_matrices(active_tab, adjusted_thresholds, reset_clicks, optimize_all_clicks, optimize_side_clicks, model, threshold_config, data, selected_side):
        """Recalculate confusion matrices when thresholds change"""
        
        # Default loading style (hidden)
        loading_style = {"display": "none"}
        
        # Only update if we're on the tweaker tab - check this FIRST
        if active_tab != "tweaker":
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
        
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Normalize model value FIRST - this ensures we use the updated model value
        # when the model store changes
        if not model:
            model = "old"  # Default to deployed model if not set
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid value
        
        # Reset thresholds
        if trigger_id == "reset-thresholds-btn":
            adjusted_thresholds = threshold_config
        
        # Optimize thresholds
        elif trigger_id in ["optimize-all-thresholds-btn", "optimize-selected-side-btn"]:
            # Show loading indicator immediately
            loading_style = {"display": "flex", "alignItems": "center", "gap": "10px"}
            print(f"🔄 Starting optimization for {'selected side' if trigger_id == 'optimize-selected-side-btn' else 'all sides'} (Model: {model})")
            
            if not threshold_config or not data:
                loading_style = {"display": "none"}
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
            
            # Determine question name - prioritize question_name from data-store (set during report generation)
            question_name = None
            if data and isinstance(data, dict) and 'question_name' in data:
                question_name = data['question_name']
            
            # Fallback: detect from threshold_config if not in data-store
            if not question_name:
                for key in threshold_config.keys():
                    if 'physicalcondition' in key.lower():
                        question_name = key
                        break
            
            if not question_name:
                loading_style = {"display": "none"}
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
            
            # Get current selected side if optimizing selected side only
            optimize_side = None
            if trigger_id == "optimize-selected-side-btn":
                optimize_side = selected_side
                if not optimize_side:
                    print("⚠️ No side selected for optimization")
                    loading_style = {"display": "none"}
                    return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
            
            # Normalize model value
            if not model:
                model = "old"
            elif model not in ["old", "new"]:
                model = "old"
            
            # Optimize thresholds (this may take time)
            try:
                print(f"⚙️ Running optimization algorithm...")
                optimized_thresholds = optimize_thresholds_for_accuracy(
                    data, threshold_config, adjusted_thresholds, question_name, model, optimize_side
                )
                adjusted_thresholds = optimized_thresholds
                print(f"✅ Optimization complete! Updated thresholds for {question_name}")
            except Exception as e:
                print(f"❌ Error during optimization: {e}")
                import traceback
                traceback.print_exc()
                loading_style = {"display": "none"}
                return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
            
            # Hide loading indicator after optimization completes
            loading_style = {"display": "none"}
        
        # Handle model change - recalculate matrices when model store changes
        # This ensures matrices update when switching between Deployed and New models
        if trigger_id == "tweaker-model-store":
            # Model changed - proceed to recalculate matrices with new model
            print(f"🔄 Model store changed to: {model}")
            # Initialize adjusted_thresholds if not set
            if not adjusted_thresholds and threshold_config:
                adjusted_thresholds = copy.deepcopy(threshold_config)
            # Continue to recalculate matrices below (don't return early)
        
        if not threshold_config or not data:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
        
        # Initialize adjusted_thresholds if not set (for model changes or initial load)
        if not adjusted_thresholds:
            adjusted_thresholds = copy.deepcopy(threshold_config)
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        # This ensures we use the correct question that was selected when generating the report
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
            if question_name:
                print(f"✓ Using question_name from data-store: {question_name}")
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    print(f"⚠️ Question name not in data-store, detected from threshold_config: {question_name}")
                    break
        
        if not question_name:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, loading_style
        
        # Model normalization already done above, so we can use it directly here
        
        # Determine model name for headers
        model_name = "Deployed Model" if model == "old" else "New Model"
        ref_header = f"{model_name} (Reference Matrix)"
        adj_header = f"{model_name} (Adjusted Matrix)"
        
        # Recalculate classifications and generate matrices
        results = recalculate_and_update_matrices(
            data, threshold_config, adjusted_thresholds, question_name, model
        )
        
        # Return results plus headers, updated thresholds, and loading style (14 outputs total)
        return results + (ref_header, adj_header, adjusted_thresholds, loading_style,)
    
    # Helper function to recalculate and update matrices
    def recalculate_and_update_matrices(data, original_thresholds, adjusted_thresholds, question_name, model):
        """Recalculate classifications and update confusion matrices"""
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            no_data_msg = html.Div([
                html.H4("No data available", className="text-muted text-center"),
                html.P("Please load data from the Report Generation tab", className="text-center text-muted")
            ], className="py-5")
            return (
                no_data_msg,
                no_data_msg,
                "0%",
                "0",
                "0%",
                "0",
                "0",
                "0",
                "0%",
                "0%"
            )
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(records)
        
        # Normalize model value - handle None and ensure it's either "old" or "new"
        if not model:
            model = "old"  # Default to deployed model if not set
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid value
        
        # Determine which answer column to use based on model
        if model == "new":
            score_prefix = "new_"
            original_answer_col = "new_cscan_answer"
            adjusted_answer_col = "adjusted_new_cscan_answer"
        else:  # model == "old"
            score_prefix = ""
            original_answer_col = "cscan_answer"
            adjusted_answer_col = "adjusted_cscan_answer"
        
        # Check if required columns exist and have data
        if original_answer_col not in df.columns:
            no_data_msg = html.Div([
                html.H4("No data available", className="text-muted text-center"),
                html.P(f"'{original_answer_col}' column not found in the dataset. Please ensure the data contains the required columns.", className="text-center text-muted")
            ], className="py-5")
            return (
                no_data_msg,
                no_data_msg,
                "0%",
                "0",
                "0%",
                "0",
                "0",
                "0",
                "0%",
                "0%"
            )
        
        # Check if column has any non-null values
        if df[original_answer_col].isna().all() or (df[original_answer_col].astype(str).str.strip() == '').all():
            no_data_msg = html.Div([
                html.H4("No data available", className="text-muted text-center"),
                html.P(f"'{original_answer_col}' column exists but contains no valid data.", className="text-center text-muted")
            ], className="py-5")
            return (
                no_data_msg,
                no_data_msg,
                "0%",
                "0",
                "0%",
                "0",
                "0",
                "0",
                "0%",
                "0%"
            )
        
        # Store original answers if not already stored
        if adjusted_answer_col not in df.columns:
            df[adjusted_answer_col] = df[original_answer_col]
        
        # Recalculate answers with adjusted thresholds
        question_thresholds = adjusted_thresholds.get(question_name, {})
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        adjusted_answers = []
        changed_count = 0
        
        for idx, row in df.iterrows():
            side_categories = []
            
            for side in sides:
                if side not in question_thresholds:
                    continue
                
                score_col = f"{score_prefix}{side}_score"
                if score_col not in df.columns:
                    continue
                
                score = row[score_col]
                if pd.isna(score):
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(float(score), side_thresholds)
                
                if category:
                    side_categories.append(category)
            
            # Determine final answer based on severity priority
            if not side_categories:
                adjusted_answer = None
            else:
                # Find highest severity category
                adjusted_answer = None
                for cat in severity_order:
                    if cat in side_categories:
                        adjusted_answer = cat
                        break
                
                if not adjusted_answer:
                    adjusted_answer = side_categories[0] if side_categories else None
            
            adjusted_answers.append(adjusted_answer)
            
            # Check if changed
            original_answer = row[original_answer_col]
            if original_answer and str(original_answer).strip() and original_answer != adjusted_answer:
                changed_count += 1
        
        df[adjusted_answer_col] = adjusted_answers
        
        # Generate reference matrix (original thresholds)
        original_df = pd.DataFrame(records)
        # Ensure we have a valid threshold_config dict with the question_name for ordering
        if question_name not in original_thresholds:
            print(f"⚠️ Warning: question_name '{question_name}' not found in original_thresholds")
        
        reference_matrix_data = prepare_matrix_data(
            original_df,
            original_answer_col,
            'final_answer',
            question_name,
            original_thresholds  # Use original thresholds for category ordering
        )
        
        # Generate adjusted matrix (adjusted thresholds)
        # IMPORTANT: Use original_thresholds for category ordering to ensure consistent label order
        # The adjusted_thresholds are only used for calculating adjusted answers, not for ordering
        # Both matrices must use the same threshold_config to get the same category order from threshold.json
        adjusted_matrix_data = prepare_matrix_data(
            df,  # Use DataFrame with adjusted answers
            adjusted_answer_col,
            'final_answer',
            question_name,
            original_thresholds  # Use original thresholds for consistent category ordering (same as reference matrix)
        )
        
        # Debug: Print label orders to verify they match
        if reference_matrix_data.get('labels') and adjusted_matrix_data.get('labels'):
            ref_labels = reference_matrix_data['labels']
            adj_labels = adjusted_matrix_data['labels']
            print(f"📊 Reference matrix labels ({len(ref_labels)}): {ref_labels}")
            print(f"📊 Adjusted matrix labels ({len(adj_labels)}): {adj_labels}")
            if ref_labels != adj_labels:
                print(f"⚠️ WARNING: Label orders don't match!")
            else:
                print(f"✓ Label orders match")
        
        # Create plots as Dash Graph components
        reference_fig = create_confusion_matrix_plot(reference_matrix_data, f"ref-{question_name}", "Reference Matrix")
        adjusted_fig = create_confusion_matrix_plot(adjusted_matrix_data, f"adj-{question_name}", "Adjusted Matrix")
        
        reference_plot = dcc.Graph(figure=reference_fig, config={'displayModeBar': True, 'displaylogo': False})
        adjusted_plot = dcc.Graph(figure=adjusted_fig, config={'displayModeBar': True, 'displaylogo': False})
        
        # Calculate metrics
        ref_accuracy = reference_matrix_data.get('accuracy', 0)
        ref_total = reference_matrix_data.get('total', 0)
        adj_accuracy = adjusted_matrix_data.get('accuracy', 0)
        adj_total = adjusted_matrix_data.get('total', 0)
        accuracy_delta = adj_accuracy - ref_accuracy
        
        return (
            reference_plot,
            adjusted_plot,
            f"{ref_accuracy:.2f}%",
            str(ref_total),
            f"{adj_accuracy:.2f}%",
            str(adj_total),
            str(changed_count),
            str(changed_count),
            f"{accuracy_delta:+.2f}%",
            f"{ref_accuracy:.2f}%"
        )
    
    # Optimize thresholds for maximum accuracy
    def optimize_thresholds_for_accuracy(data, original_thresholds, current_thresholds, question_name, model, selected_side=None):
        """
        Optimize thresholds using coordinate descent with grid search.
        
        Args:
            data: Data dictionary with records
            original_thresholds: Original threshold configuration
            current_thresholds: Current adjusted thresholds
            question_name: Question name (e.g., 'physicalConditionPanel')
            model: Model type ('old' or 'new')
            selected_side: If provided, only optimize this side. Otherwise optimize all sides.
            
        Returns:
            Optimized threshold configuration
        """
        import copy
        from utils.threshold_handler import get_category_from_score, get_severity_order_from_thresholds
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return current_thresholds
        
        df = pd.DataFrame(records)
        
        # Normalize model value - handle None and ensure it's either "old" or "new"
        if not model:
            model = "old"  # Default to deployed model if not set
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid value
        
        # Determine which answer column to use based on model
        if model == "new":
            score_prefix = "new_"
            answer_col = "adjusted_new_cscan_answer"
        else:  # model == "old"
            score_prefix = ""
            answer_col = "adjusted_cscan_answer"
        
        # Get ground truth column
        actual_col = "final_answer"
        
        if actual_col not in df.columns:
            return current_thresholds
        
        # Deep copy current thresholds
        optimized_thresholds = copy.deepcopy(current_thresholds)
        question_thresholds = optimized_thresholds.get(question_name, {})
        
        # Determine which sides to optimize
        sides_to_optimize = [selected_side] if selected_side and selected_side in question_thresholds else list(question_thresholds.keys())
        
        # Grid search parameters
        step_size = 10  # Search in steps of 10 for efficiency
        min_score = 0
        max_score = 100
        
        # Optimize each side
        for side in sides_to_optimize:
            if side not in question_thresholds:
                continue
            
            side_thresholds = question_thresholds[side]
            categories = list(side_thresholds.keys())
            
            if len(categories) == 0:
                continue
            
            best_accuracy = -1
            best_thresholds = copy.deepcopy(side_thresholds)
            
            # Generate candidate threshold combinations
            # For each category, try different min/max values
            candidates = generate_threshold_candidates(side_thresholds, step_size, min_score, max_score)
            
            # Evaluate each candidate
            for candidate_thresholds in candidates:
                # Test this candidate
                test_thresholds = copy.deepcopy(optimized_thresholds)
                test_thresholds[question_name][side] = candidate_thresholds
                
                # Calculate accuracy with these thresholds
                accuracy = evaluate_threshold_accuracy(
                    df, test_thresholds, question_name, model, score_prefix, answer_col, actual_col
                )
                
                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_thresholds = candidate_thresholds
            
            # Update with best thresholds for this side
            optimized_thresholds[question_name][side] = best_thresholds
        
        return optimized_thresholds
    
    def generate_threshold_candidates(side_thresholds, step_size, min_score, max_score):
        """
        Generate candidate threshold combinations for a side.
        Maintains category order and ensures min < max.
        """
        import copy
        
        categories = list(side_thresholds.keys())
        if len(categories) == 0:
            return []
        
        # For simplicity, we'll use a constrained search:
        # Try adjusting boundaries between categories
        # This is more efficient than full grid search
        
        candidates = []
        
        # Strategy: Try shifting category boundaries
        # For each category, try adjusting min and max by ±step_size
        for cat_idx, cat in enumerate(categories):
            min_val, max_val = side_thresholds[cat]
            
            # Try different min values
            for min_adj in [-step_size, -step_size//2, 0, step_size//2, step_size]:
                new_min = max(min_score, min(max_score, min_val + min_adj))
                # Try different max values
                for max_adj in [-step_size, -step_size//2, 0, step_size//2, step_size]:
                    new_max = max(min_score, min(max_score, max_val + max_adj))
                    
                    if new_min < new_max:
                        candidate = copy.deepcopy(side_thresholds)
                        candidate[cat] = [new_min, new_max]
                        
                        # Ensure constraints: min < max and no overlaps
                        if validate_thresholds(candidate):
                            candidates.append(candidate)
        
        # Always include original thresholds
        if validate_thresholds(side_thresholds):
            candidates.append(side_thresholds)
        
        # Remove duplicates (by converting to string representation)
        unique_candidates = []
        seen = set()
        for cand in candidates:
            cand_str = str(sorted(cand.items()))
            if cand_str not in seen:
                seen.add(cand_str)
                unique_candidates.append(cand)
        
        # Limit to reasonable number for performance
        return unique_candidates[:100] if len(unique_candidates) > 100 else unique_candidates
    
    def validate_thresholds(side_thresholds):
        """Validate that thresholds are valid (min < max, no overlaps)"""
        categories = list(side_thresholds.keys())
        if len(categories) == 0:
            return False
        
        # Check min < max for each category
        for cat, (min_val, max_val) in side_thresholds.items():
            if min_val >= max_val:
                return False
            if min_val < 0 or max_val > 100:
                return False
        
        # Check for overlaps (simplified - just ensure boundaries are reasonable)
        # Categories can have overlapping ranges, so we don't enforce strict non-overlap
        return True
    
    def evaluate_threshold_accuracy(df, thresholds, question_name, model, score_prefix, answer_col, actual_col):
        """
        Evaluate accuracy for given thresholds by recalculating answers.
        Note: answer_col parameter is not used - answers are recalculated from scores and thresholds.
        Returns accuracy percentage.
        """
        from utils.threshold_handler import get_category_from_score, get_severity_order_from_thresholds
        
        question_thresholds = thresholds.get(question_name, {})
        if not question_thresholds:
            return 0.0
        
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        predicted_answers = []
        
        for idx, row in df.iterrows():
            side_categories = []
            
            for side in sides:
                if side not in question_thresholds:
                    continue
                
                score_col = f"{score_prefix}{side}_score"
                if score_col not in df.columns:
                    continue
                
                score = row[score_col]
                if pd.isna(score):
                    continue
                
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(float(score), side_thresholds)
                
                if category:
                    side_categories.append(category)
            
            # Determine final answer based on severity priority
            if not side_categories:
                predicted_answer = None
            else:
                predicted_answer = None
                for cat in severity_order:
                    if cat in side_categories:
                        predicted_answer = cat
                        break
                
                if not predicted_answer:
                    predicted_answer = side_categories[0] if side_categories else None
            
            predicted_answers.append(predicted_answer)
        
        # Calculate accuracy
        correct = 0
        total = 0
        for idx, row in df.iterrows():
            predicted = predicted_answers[idx] if idx < len(predicted_answers) else None
            actual = row[actual_col]
            
            if pd.notna(actual) and str(actual).strip() and predicted:
                total += 1
                # Normalize for comparison
                from utils.threshold_handler import normalize_category_for_confusion_matrix
                pred_norm = normalize_category_for_confusion_matrix(str(predicted), question_name)
                actual_norm = normalize_category_for_confusion_matrix(str(actual), question_name)
                
                if pred_norm == actual_norm:
                    correct += 1
        
        accuracy = (correct / total * 100) if total > 0 else 0.0
        return accuracy
    
    # Populate filter dropdowns for changed records
    @app.callback(
        [Output("tweaker-cscan-answer-filter", "options", allow_duplicate=True),
         Output("tweaker-new-cscan-answer-filter", "options", allow_duplicate=True),
         Output("tweaker-final-answer-filter", "options", allow_duplicate=True)],
        [Input("tweaker-changed-records-store", "data"),
         Input("main-tabs", "active_tab")],
        prevent_initial_call=True
    )
    def populate_tweaker_filter_dropdowns(changed_records_data, active_tab):
        """Populate filter dropdowns with unique values from changed records"""
        if active_tab != "tweaker":
            return no_update, no_update, no_update
        
        if not changed_records_data or not isinstance(changed_records_data, dict):
            return [], [], []
        
        records = changed_records_data.get("data", [])
        if not records:
            return [], [], []
        
        # Get unique values for each filter
        cscan_answers = set()
        new_cscan_answers = set()
        final_answers = set()
        
        for record in records:
            if record.get('cscan_answer'):
                cscan_answers.add(str(record['cscan_answer']).strip())
            if record.get('new_cscan_answer'):
                new_cscan_answers.add(str(record['new_cscan_answer']).strip())
            if record.get('final_answer'):
                final_answers.add(str(record['final_answer']).strip())
        
        cscan_options = [{"label": val, "value": val} for val in sorted(cscan_answers)]
        new_cscan_options = [{"label": val, "value": val} for val in sorted(new_cscan_answers)]
        final_options = [{"label": val, "value": val} for val in sorted(final_answers)]
        
        return cscan_options, new_cscan_options, final_options
    
    # Apply filters to changed records
    @app.callback(
        Output("tweaker-changed-records-store", "data", allow_duplicate=True),
        [Input("tweaker-apply-filters-btn", "n_clicks"),
         Input("tweaker-reset-filters-btn", "n_clicks")],
        [State("tweaker-changed-records-store", "data"),
         State("tweaker-cscan-answer-filter", "value"),
         State("tweaker-new-cscan-answer-filter", "value"),
         State("tweaker-final-answer-filter", "value"),
         State("tweaker-contributing-side-filter", "value"),
         State("tweaker-new-contributing-side-filter", "value"),
         State("tweaker-deployed-side-score-filter", "value"),
         State("tweaker-deployed-score-range-slider", "value"),
         State("tweaker-new-side-score-filter", "value"),
         State("tweaker-new-score-range-slider", "value")],
        prevent_initial_call=True
    )
    def apply_tweaker_filters(apply_clicks, reset_clicks, changed_records_data, cscan_filter, new_cscan_filter, final_filter, side_filter, new_side_filter, deployed_score_side_filter, deployed_score_range, new_score_side_filter, new_score_range):
        """Apply filters to changed records (similar to image viewer)"""
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if not changed_records_data or not isinstance(changed_records_data, dict):
            return no_update
        
        records = changed_records_data.get("data", [])
        if not records:
            return no_update
        
        # Reset filters
        if trigger_id == "tweaker-reset-filters-btn":
            return {"data": records, "filtered": records}
        
        # Apply filters (same logic as image viewer)
        filtered = records
        
        def normalize_for_comparison(value):
            if not value:
                return None
            return str(value).lower().strip()
        
        # CScan Answer filter
        if cscan_filter and len(cscan_filter) > 0:
            normalized_cscan_filter = [normalize_for_comparison(v) for v in cscan_filter]
            filtered = [r for r in filtered if normalize_for_comparison(r.get('cscan_answer', '')) in normalized_cscan_filter]
        
        # New CScan Answer filter
        if new_cscan_filter and len(new_cscan_filter) > 0:
            normalized_new_cscan_filter = [normalize_for_comparison(v) for v in new_cscan_filter]
            filtered = [r for r in filtered if normalize_for_comparison(r.get('new_cscan_answer', '')) in normalized_new_cscan_filter]
        
        # Final Answer filter
        if final_filter and len(final_filter) > 0:
            normalized_final_filter = [normalize_for_comparison(v) for v in final_filter]
            filtered = [r for r in filtered if normalize_for_comparison(r.get('final_answer', '')) in normalized_final_filter]
        
        # Contributing Sides filter
        if side_filter and len(side_filter) > 0:
            def matches_side_filter(record):
                contributing_sides = str(record.get('contributing_sides', '')).lower()
                if '_blank_' in side_filter:
                    if not contributing_sides or contributing_sides.strip() == '':
                        return True
                return any(side in contributing_sides for side in side_filter if side != '_blank_')
            filtered = [r for r in filtered if matches_side_filter(r)]
        
        # New Contributing Sides filter
        if new_side_filter and len(new_side_filter) > 0:
            def matches_new_side_filter(record):
                new_contributing_sides = str(record.get('new_contributing_sides', '')).lower()
                if '_blank_' in new_side_filter:
                    if not new_contributing_sides or new_contributing_sides.strip() == '':
                        return True
                return any(side in new_contributing_sides for side in new_side_filter if side != '_blank_')
            filtered = [r for r in filtered if matches_new_side_filter(r)]
        
        # Deployed Side Score filter
        if deployed_score_range and isinstance(deployed_score_range, list) and len(deployed_score_range) == 2:
            score_min, score_max = deployed_score_range[0], deployed_score_range[1]
            is_default_range = score_min == 0 and score_max == 100
            has_side_filter = deployed_score_side_filter and len(deployed_score_side_filter) > 0
            
            if not is_default_range or has_side_filter:
                def matches_deployed_score_filter(record):
                    sides_to_check = ['top', 'bottom', 'left', 'right', 'back', 'front']
                    if deployed_score_side_filter and len(deployed_score_side_filter) > 0:
                        sides_to_check = deployed_score_side_filter
                    
                    for side in sides_to_check:
                        score_col = f"{side}_score"
                        if score_col in record:
                            score_val = record[score_col]
                            if score_val is not None and score_val != '':
                                try:
                                    score_float = float(score_val)
                                    if score_min <= score_float <= score_max:
                                        return True
                                except (ValueError, TypeError):
                                    continue
                    return False
                filtered = [r for r in filtered if matches_deployed_score_filter(r)]
        
        # New Side Score filter
        if new_score_range and isinstance(new_score_range, list) and len(new_score_range) == 2:
            score_min, score_max = new_score_range[0], new_score_range[1]
            is_default_range = score_min == 0 and score_max == 100
            has_side_filter = new_score_side_filter and len(new_score_side_filter) > 0
            
            if (not is_default_range or has_side_filter):
                def matches_new_score_filter(record):
                    sides_to_check = ['top', 'bottom', 'left', 'right', 'back', 'front']
                    if new_score_side_filter and len(new_score_side_filter) > 0:
                        sides_to_check = new_score_side_filter
                    
                    for side in sides_to_check:
                        score_col = f"new_{side}_score"
                        if score_col in record:
                            score_val = record[score_col]
                            if score_val is not None and score_val != '':
                                try:
                                    score_float = float(score_val)
                                    if score_min <= score_float <= score_max:
                                        return True
                                except (ValueError, TypeError):
                                    continue
                    return False
                filtered = [r for r in filtered if matches_new_score_filter(r)]
        
        return {"data": records, "filtered": filtered}
    
    # Reset filter dropdowns
    @app.callback(
        [Output("tweaker-cscan-answer-filter", "value", allow_duplicate=True),
         Output("tweaker-new-cscan-answer-filter", "value", allow_duplicate=True),
         Output("tweaker-final-answer-filter", "value", allow_duplicate=True),
         Output("tweaker-contributing-side-filter", "value", allow_duplicate=True),
         Output("tweaker-new-contributing-side-filter", "value", allow_duplicate=True),
         Output("tweaker-deployed-side-score-filter", "value", allow_duplicate=True),
         Output("tweaker-deployed-score-range-slider", "value", allow_duplicate=True),
         Output("tweaker-new-side-score-filter", "value", allow_duplicate=True),
         Output("tweaker-new-score-range-slider", "value", allow_duplicate=True)],
        Input("tweaker-reset-filters-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_tweaker_filters(reset_clicks):
        """Reset all filter dropdowns"""
        return [], [], [], [], [], [], [0, 100], [], [0, 100]
    
    # View changed records (auto-triggered on threshold changes)
    @app.callback(
        [Output("tweaker-changed-records-display", "children"),
         Output("tweaker-changed-records-store", "data")],
        [Input("adjusted-thresholds-store", "data"),
         Input("tweaker-model-store", "data"),
         Input("main-tabs", "active_tab"),
         Input("tweaker-changed-records-store", "data"),  # Also trigger on filter changes
         Input("tweaker-current-page-store", "data"),  # Trigger on page changes
         Input("tweaker-image-toggle-state-store", "data")],  # Trigger on image toggle changes
        [State("data-store", "data"),
         State("threshold-config-store", "data"),
         State("tweaker-current-page-store", "data"),
         State("tweaker-image-toggle-state-store", "data")],
        prevent_initial_call=True
    )
    def view_changed_records(adjusted_thresholds, model, active_tab, filtered_data, current_page_input, image_toggle_states_input, data, threshold_config, current_page_state, image_toggle_states_state):
        """Show changed records similar to Image Viewer - auto-updates when thresholds change"""
        
        # Only update if we're on the tweaker tab
        if active_tab != "tweaker":
            return no_update, no_update
        
        if not data or not adjusted_thresholds or not threshold_config:
            return no_update, no_update
        
        # Extract records from main data store
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return html.Div("No data available", className="text-center text-muted py-5"), {}
        
        # Determine question name - prioritize question_name from data-store (set during report generation)
        question_name = None
        if data and isinstance(data, dict) and 'question_name' in data:
            question_name = data['question_name']
        
        # Fallback: detect from threshold_config if not in data-store
        if not question_name:
            for key in threshold_config.keys():
                if 'physicalcondition' in key.lower():
                    question_name = key
                    break
        
        if not question_name:
            return html.Div("No question configuration found", className="text-center text-muted py-5"), {}
        
        # Normalize model value - handle None and ensure it's either "old" or "new"
        if not model:
            model = "old"  # Default to deployed model if not set
        elif model not in ["old", "new"]:
            model = "old"  # Default to deployed model if invalid value
        
        # Determine which answer column to use
        if model == "new":
            original_answer_col = "new_cscan_answer"
            adjusted_answer_col = "adjusted_new_cscan_answer"
            score_prefix = "new_"
        else:
            original_answer_col = "cscan_answer"
            adjusted_answer_col = "adjusted_cscan_answer"
            score_prefix = ""
        
        # Recalculate to get adjusted answers
        df = pd.DataFrame(records)
        question_thresholds = adjusted_thresholds.get(question_name, {})
        severity_order = get_severity_order_from_thresholds(question_thresholds)
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        
        # Recalculate (same logic as above)
        adjusted_answers = []
        for idx, row in df.iterrows():
            side_categories = []
            for side in sides:
                if side not in question_thresholds:
                    continue
                score_col = f"{score_prefix}{side}_score"
                if score_col not in df.columns:
                    continue
                score = row[score_col]
                if pd.isna(score):
                    continue
                side_thresholds = question_thresholds[side]
                category = get_category_from_score(float(score), side_thresholds)
                if category:
                    side_categories.append(category)
            
            if not side_categories:
                adjusted_answer = None
            else:
                adjusted_answer = None
                for cat in severity_order:
                    if cat in side_categories:
                        adjusted_answer = cat
                        break
                if not adjusted_answer:
                    adjusted_answer = side_categories[0] if side_categories else None
            
            adjusted_answers.append(adjusted_answer)
        
        df[adjusted_answer_col] = adjusted_answers
        
        # Find changed records and add score information
        changed_records = []
        for idx, row in df.iterrows():
            original = row[original_answer_col]
            adjusted = row[adjusted_answer_col]
            if original and str(original).strip() and original != adjusted:
                record_dict = row.to_dict()
                record_dict['original_answer'] = original
                record_dict['adjusted_answer'] = adjusted
                
                # Add contributing sides scores (only for sides that contributed to the changed answer)
                contributing_scores = []
                contributing_sides_list = []
                
                # Get contributing sides from the record
                contrib_sides_str = row.get('new_contributing_sides', '') or row.get('contributing_sides', '')
                if contrib_sides_str:
                    contrib_sides_list = [s.strip().lower() for s in str(contrib_sides_str).split(',') if s.strip()]
                    
                    # Only add scores for contributing sides
                    for side in contrib_sides_list:
                        score_col = f"{score_prefix}{side}_score"
                        if score_col in df.columns:
                            score = row[score_col]
                            if pd.notna(score):
                                contributing_scores.append(f"{side}: {score:.2f}")
                
                record_dict['contributing_scores'] = ", ".join(contributing_scores) if contributing_scores else "N/A"
                record_dict['contributing_sides'] = contrib_sides_str if contrib_sides_str else "N/A"
                
                changed_records.append(record_dict)
        
        # Check if we have filtered data from filter callback
        ctx = callback_context
        trigger_id = None
        if ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # If triggered by filter store change, use filtered data
        if trigger_id == "tweaker-changed-records-store" and filtered_data and isinstance(filtered_data, dict):
            records_to_display = filtered_data.get("filtered", changed_records)
        else:
            records_to_display = changed_records
        
        if not records_to_display:
            return html.Div([
                dbc.Alert([
                    html.H4("✅ No records changed", className="alert-heading"),
                    html.P("Adjust thresholds to see impacted records", className="mb-0")
                ], color="info", className="text-center")
            ], className="py-5"), {"data": changed_records, "filtered": changed_records}
        
        # Create filtered data store format
        store_data = {
            "data": changed_records,
            "filtered": records_to_display,
            "columns": list(changed_records[0].keys()) if changed_records else [],
            "source": "threshold_tweaker",
            "folder_name": data.get("folder_name", "") if isinstance(data, dict) else ""
        }
        
        # Use current page from state (default to 0 if not set)
        current_page = current_page_state if current_page_state is not None else 0
        
        # Use image toggle states from state (default to empty dict if not set)
        image_toggle_states = image_toggle_states_state if (image_toggle_states_state and isinstance(image_toggle_states_state, dict)) else {}
        
        # Use create_accordion_view for consistent UI with image viewer
        accordion_view = create_accordion_view(
            records_to_display,  # Use filtered records for display
            current_page,
            image_toggle_states,  # Use image toggle states from store
            {},  # Audit tags
            []   # Audit options
        )
        
        # Create stats bar matching image viewer style
        stats_bar = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.Span("Total Records:", className="label fw-bold me-2"),
                        html.Span(str(len(changed_records)), id="tweaker-total-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Filtered:", className="label fw-bold me-2"),
                        html.Span(str(len(records_to_display)), id="tweaker-filtered-records", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=2),
                    dbc.Col([
                        html.Span("Model:", className="label fw-bold me-2"),
                        html.Span("New Model" if model == "new" else "Deployed Model", className="value", style={"color": "#3b82f6", "fontSize": "1.2em"}),
                    ], md=3),
                ])
            ])
        ], className="mb-4")
        
        # Create pagination controls matching image viewer
        records_per_page = 10
        total_pages = (len(records_to_display) + records_per_page - 1) // records_per_page
        # Ensure current_page is within valid range
        if current_page >= total_pages:
            current_page = max(0, total_pages - 1)
        start_idx = current_page * records_per_page
        end_idx = min(start_idx + records_per_page, len(records_to_display))
        
        pagination = dbc.Card([
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("⏮️ First Page", id="tweaker-first-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("◀️ Prev", id="tweaker-prev-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-start"),
                    dbc.Col([
                        html.Div([
                            html.Span("Records ", style={"fontSize": "0.9em"}),
                            html.Span(id="tweaker-page-start", children=str(start_idx + 1), style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span("-", style={"margin": "0 4px"}),
                            html.Span(id="tweaker-page-end", children=str(end_idx), style={"fontSize": "1.2em", "fontWeight": "600", "color": "#3b82f6"}),
                            html.Span(" of ", style={"margin": "0 8px"}),
                            html.Span(id="tweaker-total-filtered", children=str(len(records_to_display)), style={"fontSize": "1.2em", "fontWeight": "600"}),
                        ], className="text-center", style={"lineHeight": "38px"})
                    ], md=4),
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Next ▶️", id="tweaker-next-btn", color="primary", outline=True, size="sm"),
                            dbc.Button("Last Page ⏭️", id="tweaker-last-btn", color="primary", outline=True, size="sm"),
                        ])
                    ], md=4, className="d-flex justify-content-end"),
                ])
            ])
        ], className="mt-4")
        
        display = html.Div([
            stats_bar,
            accordion_view,
            pagination
        ])
        
        return display, store_data
    
    # Clientside callback for expand/collapse rows in threshold tweaker
    app.clientside_callback(
        """
        function(n_clicks_list) {
            if (!n_clicks_list || n_clicks_list.length === 0) {
                return window.dash_clientside.no_update;
            }
            
            const ctx = window.dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return window.dash_clientside.no_update;
            }
            
            const trigger = ctx.triggered[0];
            const triggerId = trigger.prop_id;
            
            // Extract index from trigger ID
            const match = triggerId.match(/\\{"type":"tweaker-expand-row","index":(\\d+)\\}/);
            if (!match) {
                return window.dash_clientside.no_update;
            }
            
            const index = parseInt(match[1]);
            const arrowId = `tweaker-arrow-${index}`;
            const rowExpandedId = `tweaker-row-expanded-${index}`;
            
            const arrow = document.getElementById(arrowId);
            const rowExpanded = document.getElementById(rowExpandedId);
            
            if (!arrow || !rowExpanded) {
                return window.dash_clientside.no_update;
            }
            
            // Toggle visibility
            const isVisible = rowExpanded.style.display !== 'none';
            
            if (isVisible) {
                rowExpanded.style.display = 'none';
                arrow.style.transform = 'rotate(0deg)';
            } else {
                rowExpanded.style.display = 'table-row';
                arrow.style.transform = 'rotate(90deg)';
            }
            
            return window.dash_clientside.no_update;
        }
        """,
        Output("tweaker-changed-records-display", "children", allow_duplicate=True),
        Input({"type": "tweaker-expand-row", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    
    # Navigation buttons for tweaker pagination
    @app.callback(
        Output("tweaker-current-page-store", "data", allow_duplicate=True),
        [Input("tweaker-first-btn", "n_clicks"),
         Input("tweaker-prev-btn", "n_clicks"),
         Input("tweaker-next-btn", "n_clicks"),
         Input("tweaker-last-btn", "n_clicks")],
        [State("tweaker-changed-records-store", "data"),
         State("tweaker-current-page-store", "data")],
        prevent_initial_call=True
    )
    def navigate_tweaker_records(first_clicks, prev_clicks, next_clicks, last_clicks, changed_records_data, current_page):
        """Navigate pages in tweaker changed records"""
        ctx = callback_context
        if not ctx.triggered:
            return current_page or 0
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        # Get filtered count from store
        if not changed_records_data or not isinstance(changed_records_data, dict):
            return 0
        
        records_to_display = changed_records_data.get("filtered", [])
        if not records_to_display:
            records_to_display = changed_records_data.get("data", [])
        
        filtered_count = len(records_to_display)
        if filtered_count == 0:
            return 0
        
        # Calculate total pages
        total_pages = (filtered_count + 9) // 10  # Ceiling division
        
        # Navigate pages
        if trigger_id == "tweaker-first-btn":
            return 0
        elif trigger_id == "tweaker-prev-btn":
            return max(0, (current_page or 0) - 1)
        elif trigger_id == "tweaker-next-btn":
            return min(total_pages - 1, (current_page or 0) + 1)
        elif trigger_id == "tweaker-last-btn":
            return total_pages - 1
        
        return current_page or 0
    
    # Update image toggle state store for tweaker
    @app.callback(
        Output("tweaker-image-toggle-state-store", "data", allow_duplicate=True),
        Input({"type": "image-toggle-btn", "side": ALL, "record_id": ALL}, "n_clicks"),
        State("tweaker-image-toggle-state-store", "data"),
        prevent_initial_call=True
    )
    def update_tweaker_image_toggle_state(n_clicks_list, current_states):
        """Update image toggle state for tweaker records"""
        from dash import callback_context, no_update
        
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        
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
            
            # Initialize states if needed
            if not current_states or not isinstance(current_states, dict):
                current_states = {}
            
            # Get current state for this record and side
            record_states = current_states.get(record_id, {})
            if not isinstance(record_states, dict):
                record_states = {}
            
            # Toggle state
            current_mode = record_states.get(side, 'result')
            new_mode = 'input' if current_mode == 'result' else 'result'
            
            # Update nested structure
            record_states[side] = new_mode
            current_states[record_id] = record_states
            
            return current_states
        except (json.JSONDecodeError, KeyError, AttributeError):
            return no_update
