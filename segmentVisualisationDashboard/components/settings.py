"""
Settings Tab Component
Configure image and label folder paths, and label format
"""

from dash import html, dcc, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.label_loader import LabelLoader


def create_settings_tab():
    """Create the Settings tab layout"""
    
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("📁 Data Configuration", className="mb-4", style={"color": "#3b82f6"}),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Images Folder Path", html_for="images-path-input", className="fw-bold"),
                        dbc.Input(
                            id="images-path-input",
                            type="text",
                            placeholder="Enter path to images folder...",
                            className="mb-3"
                        ),
                        html.Small("Path to folder containing all images", className="text-muted"),
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Label("Labels Folder Path", html_for="labels-path-input", className="fw-bold"),
                        dbc.Input(
                            id="labels-path-input",
                            type="text",
                            placeholder="Enter path to labels folder...",
                            className="mb-3"
                        ),
                        html.Small("Path to folder containing label files", className="text-muted"),
                    ], md=6),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Label Format", html_for="label-format-dropdown", className="fw-bold"),
                        dcc.Dropdown(
                            id="label-format-dropdown",
                            options=[
                                {"label": "YOLO Format (.txt)", "value": "yolo"},
                                {"label": "Pascal VOC XML (.xml)", "value": "voc"},
                                {"label": "Mask PNG Files (.png)", "value": "mask"},
                                {"label": "Custom JSON (.json)", "value": "json"},
                            ],
                            value="mask",
                            className="mb-3"
                        ),
                        html.Small("Select the format of your label files", className="text-muted"),
                    ], md=6),
                ], className="mb-4"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Button(
                            "🔄 Load Data",
                            id="load-data-button",
                            color="primary",
                            size="lg",
                            className="w-100"
                        ),
                    ], md=6),
                    dbc.Col([
                        dbc.Button(
                            "🔄 Reset",
                            id="reset-data-button",
                            color="secondary",
                            size="lg",
                            className="w-100"
                        ),
                    ], md=6),
                ], className="mb-4"),
                
                dcc.Loading(
                    id="loading-indicator",
                    type="default",
                    children=html.Div(id="load-status", className="mt-3"),
                    style={"minHeight": "60px"}
                ),
                
            ])
        ], className="mb-4"),
        
    ], fluid=True)


def register_settings_callbacks(app):
    """Register callbacks for settings tab"""
    
    @app.callback(
        [
            Output('data-store', 'data'),
            Output('images-path-store', 'data'),
            Output('labels-path-store', 'data'),
            Output('label-format-store', 'data'),
            Output('load-status', 'children'),
            Output('class-colors-store', 'data'),
        ],
        [
            Input('load-data-button', 'n_clicks'),
            Input('reset-data-button', 'n_clicks'),
        ],
        [
            State('images-path-input', 'value'),
            State('labels-path-input', 'value'),
            State('label-format-dropdown', 'value'),
            State('data-store', 'data'),
        ]
    )
    def load_or_reset_data(load_clicks, reset_clicks, images_path, labels_path, label_format, current_data):
        """Load data or reset based on button clicked"""
        ctx = callback_context
        
        if not ctx.triggered:
            return current_data or {}, None, None, None, "", {}
        
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if button_id == 'reset-data-button':
            return {}, None, None, None, dbc.Alert("Data reset successfully", color="info"), {}
        
        if button_id == 'load-data-button':
            # Show loading message immediately
            loading_message = dbc.Alert([
                html.Div([
                    html.Div(className="spinner", style={"display": "inline-block", "marginRight": "10px"}),
                    html.Span("Loading data... Please wait", style={"verticalAlign": "middle"})
                ], style={"display": "flex", "alignItems": "center"})
            ], color="info")
            
            if not images_path or not labels_path or not label_format:
                return (
                    current_data or {},
                    images_path,
                    labels_path,
                    label_format,
                    dbc.Alert("Please fill in all fields", color="warning"),
                    {}
                )
            
            # Validate paths
            images_path_obj = Path(images_path)
            labels_path_obj = Path(labels_path)
            
            if not images_path_obj.exists():
                return (
                    current_data or {},
                    images_path,
                    labels_path,
                    label_format,
                    dbc.Alert(f"Images folder not found: {images_path}", color="danger"),
                    {}
                )
            
            if not labels_path_obj.exists():
                return (
                    current_data or {},
                    images_path,
                    labels_path,
                    label_format,
                    dbc.Alert(f"Labels folder not found: {labels_path}", color="danger"),
                    {}
                )
            
            # Load data
            try:
                loader = LabelLoader(images_path, labels_path, label_format)
                data = loader.load_all()
                
                if not data:
                    return (
                        {},
                        images_path,
                        labels_path,
                        label_format,
                        dbc.Alert([
                            html.Strong("⚠️ No Data Found"),
                            html.Br(),
                            "No matching images and labels were found. Please check:",
                            html.Ul([
                                html.Li("Image folder contains valid image files (.jpg, .png, etc.)"),
                                html.Li("Label folder contains matching label files"),
                                html.Li("Label format matches your annotation files"),
                                html.Li("File names match between images and labels")
                            ])
                        ], color="warning", dismissable=True),
                        {}
                    )
                
                # Create class colors mapping
                all_classes = set()
                for item in data:
                    label_data = item['label_data']
                    if label_data:
                        classes = label_data.get('classes', [])
                        all_classes.update(classes)
                
                # Assign colors to classes
                colors = [
                    [255, 0, 0],    # Red
                    [0, 255, 0],    # Green
                    [0, 0, 255],    # Blue
                    [255, 255, 0],  # Yellow
                    [255, 0, 255],  # Magenta
                    [0, 255, 255],  # Cyan
                    [255, 128, 0],  # Orange
                    [128, 0, 255],  # Purple
                    [0, 128, 255],  # Light Blue
                    [255, 192, 203], # Pink
                ]
                
                class_colors = {}
                for idx, class_id in enumerate(sorted(all_classes)):
                    class_colors[class_id] = colors[idx % len(colors)]
                
                # Create success message with details
                success_message = dbc.Alert([
                    html.H5("✅ Data Loaded Successfully!", className="mb-2"),
                    html.P([
                        html.Strong(f"Total Images: "), f"{len(data)}",
                        html.Br(),
                        html.Strong(f"Unique Classes: "), f"{len(class_colors)}",
                        html.Br(),
                        html.Small("You can now navigate to Statistics or Image Viewer tabs", className="text-muted")
                    ])
                ], color="success", dismissable=True)
                
                return (
                    {'data': data, 'total': len(data)},
                    images_path,
                    labels_path,
                    label_format,
                    success_message,
                    class_colors
                )
            
            except Exception as e:
                import traceback
                traceback.print_exc()
                return (
                    current_data or {},
                    images_path,
                    labels_path,
                    label_format,
                    dbc.Alert(f"Error loading data: {str(e)}", color="danger"),
                    {}
                )
        
        return current_data or {}, images_path, labels_path, label_format, "", {}

