"""
Confusion Matrix Tab Component for Analysis Dashboard
Displays interactive confusion matrices with clickable cells
"""

from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from pathlib import Path
import sys
import pandas as pd

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import data loader utilities (same logic as used in report generation)
from utils.data_loader import prepare_matrix_data, create_confusion_matrix_plot
from utils.threshold_handler import load_threshold_config, normalize_category_for_confusion_matrix


def detect_question_name_from_config(threshold_config, data=None):
    """
    Detect question name from data (stored during report generation) or threshold config.
    Priority: data['question_name'] > first non-default question from config
    
    Args:
        threshold_config: Threshold configuration dictionary
        data: Optional data dict that contains question_name from report generation
        
    Returns:
        Question name string, or first available question from config, or None
    """
    # First priority: Use question_name from data (provided in report generation tab)
    if data and isinstance(data, dict) and 'question_name' in data:
        question_name = data['question_name']
        if question_name:
            return question_name
    
    # Fallback: Get first non-default question from threshold config
    if threshold_config and isinstance(threshold_config, dict):
        for key in threshold_config.keys():
            if isinstance(key, str) and key != 'default':
                return key
    
    # If no question found, return None (caller should handle)
    return None


def validate_required_columns(df, required_cols):
    """
    Validate that DataFrame has required columns.
    
    Args:
        df: DataFrame to validate
        required_cols: List of required column names
        
    Returns:
        Tuple of (is_valid, missing_cols)
    """
    if df is None or df.empty:
        return False, required_cols
    
    missing_cols = [col for col in required_cols if col not in df.columns]
    return len(missing_cols) == 0, missing_cols


def create_confusion_matrix_tab():
    """Create the Confusion Matrix tab layout"""
    
    return dbc.Container([
        # Matrix Display Area (header removed)
        html.Div(id="matrix-display", children=[
            html.Div([
                html.Div(className="spinner"),
                html.P("Load data to view confusion matrices...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        ], style={"marginTop": "1.5rem"}),
        
    ], fluid=True, className="tab-content-container", style={"padding": "2rem 1rem"})


# Using prepare_matrix_data and create_confusion_matrix_plot from utils.data_loader
# These functions match the exact logic used when generating confusion matrices in report generation


def create_metrics_panel(matrix_data, color_scheme="primary"):
    """Create metrics panel for confusion matrix"""
    
    if not matrix_data:
        return html.Div()
    
    # Color schemes
    colors = {
        "primary": ["#1e40af", "#3b82f6"],
        "success": ["#10b981", "#059669"],
        "danger": ["#ef4444", "#dc2626"]
    }
    
    color = colors.get(color_scheme, colors["primary"])
    
    return dbc.Card([
        dbc.CardHeader(
            html.H4([
                html.I(className="fas fa-chart-line me-2"),
                "Metrics"
            ], className="mb-0", style={"fontSize": "1.3em", "fontWeight": "600", "color": color[0]}),
            style={
                "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                "borderBottom": "2px solid #e2e8f0"
            }
        ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-bullseye me-2"),
                                "Accuracy"
                            ], style={"fontSize": "0.85em", "fontWeight": "600", "marginBottom": "8px", "opacity": "0.95"}),
                            html.H3(f"{matrix_data['accuracy']:.2f}%", className="mb-0", style={
                                "fontWeight": "700",
                                "fontSize": "1.6em",
                                "textShadow": "0 2px 4px rgba(0,0,0,0.1)",
                                "whiteSpace": "nowrap"
                            })
                        ], style={"padding": "1.5rem", "overflow": "hidden"})
                    ], style={
                        "background": f"linear-gradient(135deg, {color[0]} 0%, {color[1]} 100%)", 
                        "color": "white",
                        "border": "none",
                        "borderRadius": "10px",
                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                        "transition": "transform 0.2s ease",
                        "overflow": "hidden"
                    }, className="hover-lift")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-check-circle me-2"),
                                "Correct"
                            ], style={"fontSize": "0.85em", "fontWeight": "600", "marginBottom": "8px", "opacity": "0.95"}),
                            html.H3(str(matrix_data['correct']), className="mb-0", style={
                                "fontWeight": "700",
                                "fontSize": "2em",
                                "textShadow": "0 2px 4px rgba(0,0,0,0.1)"
                            })
                        ], style={"padding": "1.5rem", "overflow": "hidden"})
                    ], style={
                        "background": "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)", 
                        "color": "white",
                        "border": "none",
                        "borderRadius": "10px",
                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                        "transition": "transform 0.2s ease",
                        "overflow": "hidden"
                    }, className="hover-lift")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.Div([
                                html.I(className="fas fa-database me-2"),
                                "Total Samples"
                            ], style={"fontSize": "0.85em", "fontWeight": "600", "marginBottom": "8px", "opacity": "0.95"}),
                            html.H3(str(matrix_data['total']), className="mb-0", style={
                                "fontWeight": "700",
                                "fontSize": "2em",
                                "textShadow": "0 2px 4px rgba(0,0,0,0.1)",
                                "wordBreak": "break-word",
                                "overflowWrap": "break-word"
                            })
                        ], style={"padding": "1.5rem", "overflow": "hidden"})
                    ], style={
                        "background": "linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)", 
                        "color": "white",
                        "border": "none",
                        "borderRadius": "10px",
                        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.15)",
                        "transition": "transform 0.2s ease",
                        "overflow": "hidden"
                    }, className="hover-lift")
                ], md=4),
            ], className="g-3")
        ], style={"padding": "1.5rem"})
    ], className="mt-4", style={
        "border": "1px solid #e2e8f0",
        "borderRadius": "12px",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    })


def create_per_class_metrics_table(matrix_data, model_name="Model", color_scheme="primary"):
    """Create per-class precision and recall metrics table"""
    
    if not matrix_data or not matrix_data.get('precisions') or not matrix_data.get('recalls'):
        return html.Div()
    
    precisions = matrix_data.get('precisions', {})
    recalls = matrix_data.get('recalls', {})
    labels = matrix_data.get('labels', [])
    
    if not labels:
        return html.Div()
    
    # Color schemes
    colors = {
        "primary": "#3b82f6",
        "success": "#10b981",
        "danger": "#ef4444"
    }
    
    header_color = colors.get(color_scheme, colors["primary"])
    
    # Create table rows
    table_rows = []
    for label in labels:
        precision_val = precisions.get(label, 0)
        recall_val = recalls.get(label, 0)
        
        table_rows.append(
            html.Tr([
                html.Td(label.capitalize(), style={"fontWeight": "600", "padding": "0.75rem"}),
                html.Td(f"{precision_val:.2f}%", style={"padding": "0.75rem", "textAlign": "center"}),
                html.Td(f"{recall_val:.2f}%", style={"padding": "0.75rem", "textAlign": "center"})
            ], style={"borderBottom": "1px solid #e2e8f0"})
        )
    
    return dbc.Card([
        dbc.CardHeader(
            html.H4([
                html.I(className="fas fa-table me-2"),
                f"{model_name} - Per-Class Metrics"
            ], className="mb-0", style={"fontSize": "1.3em", "fontWeight": "600", "color": header_color}),
            style={
                "background": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
                "borderBottom": "2px solid #e2e8f0"
            }
        ),
        dbc.CardBody([
            dbc.Table([
                html.Thead([
                    html.Tr([
                        html.Th("Class", style={"fontWeight": "700", "padding": "0.75rem", "backgroundColor": "#f8fafc"}),
                        html.Th("Precision", style={"fontWeight": "700", "padding": "0.75rem", "textAlign": "center", "backgroundColor": "#f8fafc"}),
                        html.Th("Recall", style={"fontWeight": "700", "padding": "0.75rem", "textAlign": "center", "backgroundColor": "#f8fafc"})
                    ])
                ]),
                html.Tbody(table_rows)
            ], bordered=True, hover=True, responsive=True, striped=True, style={
                "marginBottom": "0",
                "fontSize": "0.95em"
            })
        ], style={"padding": "1.5rem"})
    ], className="mt-4", style={
        "border": "1px solid #e2e8f0",
        "borderRadius": "12px",
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)"
    })


def register_confusion_matrix_callbacks(app):
    """Register callbacks for confusion matrix tab"""
    
    @app.callback(
        Output("matrix-display", "children"),
        [Input("data-store", "data"),
         Input("threshold-config-store", "data")],
        prevent_initial_call=True  # Same as Image Viewer
    )
    def update_confusion_matrices(data, threshold_config):
        """Generate and display confusion matrices - same pattern as Image Viewer"""
        
        print(f"\n{'='*60}")
        print(f"📊 Confusion Matrix callback triggered")
        print(f"   Data Type: {type(data)}")
        print(f"{'='*60}")
        
        if not data or not isinstance(data, dict):
            print("   ⚠️ No data or not a dict")
            return html.Div([
                html.Div([
                    html.H4("No data loaded", className="text-muted text-center"),
                    html.P("Please load data from the Report Generation tab or upload a CSV", className="text-center text-muted")
                ], className="py-5")
            ])
        
        # Extract records
        if "data" in data:
            records = data["data"]
            print(f"   ✓ Found {len(records)} records in data dict")
        else:
            records = data if isinstance(data, list) else []
            print(f"   ⚠️ Data is not a dict with 'data' key")
        
        if not records:
            print("   ⚠️ No records to display")
            return html.Div([
                html.Div([
                    html.H4("No data available", className="text-muted text-center"),
                    html.P("The loaded dataset is empty", className="text-center text-muted")
                ], className="py-5")
            ])
        
        # Convert to DataFrame for proper processing (matching report generation logic)
        try:
            df = pd.DataFrame(records)
        except Exception as e:
            print(f"   ❌ Error creating DataFrame: {e}")
            return html.Div([
                html.Div([
                    html.H4("Error processing data", className="text-muted text-center"),
                    html.P(f"Failed to create DataFrame: {str(e)}", className="text-center text-muted")
                ], className="py-5")
            ])
        
        # Validate required columns
        required_cols = ['cscan_answer', 'final_answer']
        is_valid, missing_cols = validate_required_columns(df, required_cols)
        if not is_valid:
            print(f"   ❌ Missing required columns: {missing_cols}")
            return html.Div([
                html.Div([
                    html.H4("Missing required columns", className="text-muted text-center"),
                    html.P(f"Required columns not found: {', '.join(missing_cols)}", className="text-center text-muted")
                ], className="py-5")
            ])
        
        # Detect question name from threshold config or data (dynamic, not hardcoded)
        question_name = detect_question_name_from_config(threshold_config, data)
        if not question_name:
            # Fallback: use first available question from config
            if threshold_config and isinstance(threshold_config, dict):
                for key in threshold_config.keys():
                    if key != 'default':
                        question_name = key
                        break
        
        if not question_name:
            print(f"   ⚠️ Could not detect question name, using default")
            question_name = 'default'
        
        print(f"   ✓ Detected question name: {question_name}")
        
        # Check if we have new model data
        has_new_data = 'new_cscan_answer' in df.columns and df['new_cscan_answer'].notna().any()
        print(f"   ✓ Has new model data: {has_new_data}")
        
        # Prepare matrix data using the same function as report generation
        try:
            old_matrix_data = prepare_matrix_data(
                df, 
                'cscan_answer', 
                'final_answer',
                question_name,
                threshold_config
            )
        except Exception as e:
            print(f"   ❌ Error preparing matrix data: {e}")
            import traceback
            traceback.print_exc()
            return html.Div([
                html.Div([
                    html.H4("Error generating confusion matrix", className="text-muted text-center"),
                    html.P(f"Failed to prepare matrix data: {str(e)}", className="text-center text-muted")
                ], className="py-5")
            ])
        
        if not old_matrix_data or not old_matrix_data.get('labels'):
            print("   ❌ Cannot generate confusion matrix - missing labels or empty data")
            return html.Div([
                html.Div([
                    html.H4("Cannot generate confusion matrix", className="text-muted text-center"),
                    html.P("No valid data found in 'cscan_answer' and 'final_answer' columns. Please check your data.", className="text-center text-muted")
                ], className="py-5")
            ])
        
        print(f"   ✅ Generated confusion matrix with {len(old_matrix_data['labels'])} categories, accuracy: {old_matrix_data['accuracy']:.2f}%")
        
        # Create matrices display
        if has_new_data:
            try:
                new_matrix_data = prepare_matrix_data(
                    df, 
                    'new_cscan_answer', 
                    'final_answer',
                    question_name,
                    threshold_config
                )
            except Exception as e:
                print(f"   ⚠️ Error preparing new matrix data: {e}")
                # Fall back to single matrix if new matrix fails
                new_matrix_data = None
            
            if new_matrix_data and new_matrix_data.get('labels'):
                print(f"   ✅ New matrix generated, creating two-column layout")
                # Two column layout
                return dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H3(
                                    "Deployed Model",
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
                                html.P("CScan Answer vs Final Answer", className="text-muted mb-3", style={
                                    "fontSize": "0.95em",
                                    "fontWeight": "500"
                                }),
                                dcc.Graph(
                                    id='old-matrix-plot',
                                    figure=create_confusion_matrix_plot(old_matrix_data, 'old-matrix-plot', "Deployed Model"),
                                    config={'displayModeBar': True, 'displaylogo': False}
                                ),
                                create_metrics_panel(old_matrix_data, "primary"),
                                create_per_class_metrics_table(old_matrix_data, "Deployed Model", "primary")
                            ], style={"padding": "1.5rem"})
                        ], style={
                            "border": "1px solid #e2e8f0",
                            "borderRadius": "12px",
                            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                            "overflow": "hidden"
                        })
                    ], md=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H3([
                                    html.I(className="fas fa-sparkles me-2", style={"color": "#10b981"}),
                                    "New Model"
                                ], className="mb-0", style={"fontSize": "1.5em", "fontWeight": "600", "color": "#1e293b"}),
                                style={
                                    "background": "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                                    "borderBottom": "3px solid #10b981",
                                    "padding": "1.2rem"
                                }
                            ),
                            dbc.CardBody([
                                html.P("New CScan Answer vs Final Answer", className="text-muted mb-3", style={
                                    "fontSize": "0.95em",
                                    "fontWeight": "500"
                                }),
                                dcc.Graph(
                                    id='new-matrix-plot',
                                    figure=create_confusion_matrix_plot(new_matrix_data, 'new-matrix-plot', "New Model"),
                                    config={'displayModeBar': True, 'displaylogo': False}
                                ),
                                create_metrics_panel(new_matrix_data, "success"),
                                create_per_class_metrics_table(new_matrix_data, "New Model", "success")
                            ], style={"padding": "1.5rem"})
                        ], style={
                            "border": "1px solid #e2e8f0",
                            "borderRadius": "12px",
                            "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                            "overflow": "hidden"
                        })
                    ], md=6, className="mb-4"),
                ], className="g-4")
        
        # Single matrix layout
        print(f"   ✅ Creating single matrix layout")
        return dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H3(
                            "Deployed Model",
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
                        html.P("CScan Answer vs Final Answer", className="text-muted mb-3", style={
                            "fontSize": "0.95em",
                            "fontWeight": "500"
                        }),
                        dcc.Graph(
                            id='old-matrix-plot',
                            figure=create_confusion_matrix_plot(old_matrix_data, 'old-matrix-plot', "Deployed Model"),
                            config={'displayModeBar': True, 'displaylogo': False}
                        ),
                        create_metrics_panel(old_matrix_data, "primary"),
                        create_per_class_metrics_table(old_matrix_data, "Deployed Model", "primary")
                    ], style={"padding": "1.5rem"})
                ], style={
                    "border": "1px solid #e2e8f0",
                    "borderRadius": "12px",
                    "boxShadow": "0 4px 16px rgba(0, 0, 0, 0.1)",
                    "overflow": "hidden"
                })
            ], md=12, className="mb-4"),
            # Hidden placeholder for new-matrix-plot to ensure callback always has both inputs
            html.Div([
                dcc.Graph(
                    id='new-matrix-plot',
                    figure={},
                    config={'displayModeBar': False, 'displaylogo': False}
                )
            ], style={"display": "none"})
        ])
    
    # Handle cell clicks to filter records in Image Viewer
    @app.callback(
        [Output("matrix-filter-cscan", "data"),
         Output("matrix-filter-new-cscan", "data"),
         Output("matrix-filter-final", "data"),
         Output("matrix-click-trigger", "data"),
         Output("main-tabs", "active_tab")],
        [Input("old-matrix-plot", "clickData"),
         Input("new-matrix-plot", "clickData")],
        [State("matrix-click-trigger", "data"),
         State("threshold-config-store", "data"),
         State("data-store", "data")],
        prevent_initial_call=True
    )
    def handle_matrix_cell_click(old_click_data, new_click_data, current_trigger, threshold_config, data):
        """Handle clicks on confusion matrix cells to filter and show records in Image Viewer"""
        
        from dash import no_update
        
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, no_update, no_update
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        print(f"   🔍 Trigger ID: {trigger_id}")
        print(f"   📊 Old click data: {old_click_data is not None}")
        print(f"   📊 New click data: {new_click_data is not None}")
        
        # Determine which matrix was clicked and get click data
        click_data = None
        is_new_model = False
        
        if trigger_id == "old-matrix-plot":
            if not old_click_data:
                print(f"   ⚠️ Old matrix plot triggered but no click data available")
                return no_update, no_update, no_update, no_update, no_update
            click_data = old_click_data
            is_new_model = False
            print(f"🖱️ Old matrix cell clicked")
        elif trigger_id == "new-matrix-plot":
            if not new_click_data:
                print(f"   ⚠️ New matrix plot triggered but no click data available")
                return no_update, no_update, no_update, no_update, no_update
            click_data = new_click_data
            is_new_model = True
            print(f"🖱️ New matrix cell clicked")
        else:
            print(f"   ⚠️ Unknown trigger: {trigger_id}")
            return no_update, no_update, no_update, no_update, no_update
        
        # Validate click data structure
        if not click_data or not isinstance(click_data, dict):
            print(f"   ❌ Invalid click data structure: {type(click_data)}")
            return no_update, no_update, no_update, no_update, no_update
        
        if 'points' not in click_data or not click_data['points']:
            print(f"   ❌ No points in click data")
            return no_update, no_update, no_update, no_update, no_update
        
        # Extract clicked cell coordinates
        try:
            point = click_data['points'][0]
            
            # Get labels from the point data
            # Labels in plot are capitalized (e.g., "Major scratch"), but data uses normalized lowercase
            # We need to normalize them the same way as the confusion matrix data
            
            # Detect question name from threshold config and data (consistent with main callback)
            question_name = detect_question_name_from_config(threshold_config, data)
            if not question_name:
                # Fallback: use first available question from config
                if threshold_config and isinstance(threshold_config, dict):
                    for key in threshold_config.keys():
                        if key != 'default':
                            question_name = key
                            break
            
            if not question_name:
                question_name = 'default'
            
            print(f"   ✓ Using question name for normalization: {question_name}")
            
            # Extract raw labels from click data (these are capitalized display labels)
            predicted_label_raw = str(point.get('x', '')).strip()
            actual_label_raw = str(point.get('y', '')).strip()
            
            if not predicted_label_raw or not actual_label_raw:
                print(f"   ❌ Invalid click data: missing x or y label")
                return no_update, no_update, no_update, no_update, no_update
            
            # Normalize labels using the same function as confusion matrix generation
            # normalize_category_for_confusion_matrix handles lowercase conversion internally
            # NOTE: Glass panel normalization ONLY applies when question_name is 'physicalConditionPanel'
            predicted_label = normalize_category_for_confusion_matrix(predicted_label_raw, question_name)
            actual_label = normalize_category_for_confusion_matrix(actual_label_raw, question_name)
            
            print(f"   📋 Cell clicked: Predicted='{predicted_label}' (from '{predicted_label_raw}'), Actual='{actual_label}' (from '{actual_label_raw}')")
            print(f"   🔍 Model: {'New' if is_new_model else 'Deployed'}")
            
            # Increment trigger to signal filter application
            new_trigger = (current_trigger or 0) + 1
            
            # Set the appropriate filters based on which matrix was clicked
            # Use single-item lists for exact matching (compatible with multi-select filter logic)
            # IMPORTANT: Clear the unused filter to avoid interference between models
            if is_new_model:
                # New model clicked: filter by new_cscan_answer and final_answer
                # Clear deployed model filter (cscan) to avoid conflicts
                print(f"   ✅ Setting filters: new_cscan_answer='{predicted_label}', final_answer='{actual_label}'")
                print(f"   🧹 Clearing deployed model filter (cscan) to avoid conflicts")
                return [], [predicted_label], [actual_label], new_trigger, "celldetail"
            else:
                # Old/deployed model clicked: filter by cscan_answer and final_answer
                # Clear new model filter (new_cscan) to avoid conflicts
                print(f"   ✅ Setting filters: cscan_answer='{predicted_label}', final_answer='{actual_label}'")
                print(f"   🧹 Clearing new model filter (new_cscan) to avoid conflicts")
                return [predicted_label], [], [actual_label], new_trigger, "celldetail"
            
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            print(f"   ❌ Error handling matrix click: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update, no_update, no_update, no_update
        except Exception as e:
            print(f"   ❌ Unexpected error handling matrix click: {e}")
            import traceback
            traceback.print_exc()
            return no_update, no_update, no_update, no_update, no_update
