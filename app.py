"""
Physical Condition Scratch Detection - Analysis Dashboard (Dash Version)
Migrated from dashboard_phase2.html

This dashboard provides comprehensive analysis with:
- Report Generation (NEW) - Generate analysis CSV from raw data
- Image Viewer with filters and navigation
- Interactive Confusion Matrices
- Statistical Analytics
- Threshold Tweaker with real-time updates
- Cell Details viewer
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import jsonify
from pathlib import Path
import os

# Import components
from components import (
    create_report_generation_tab,
    create_image_viewer_tab,
    create_confusion_matrix_tab,
    create_analytics_tab,
    create_threshold_tweaker_tab,
    create_cell_details_tab
)

# Import component callbacks
from components.report_generation import register_report_generation_callbacks
from components.image_viewer import register_image_viewer_callbacks
from components.confusion_matrix import register_confusion_matrix_callbacks
from components.analytics import register_analytics_callbacks
from components.threshold_tweaker import register_threshold_tweaker_callbacks
from components.cell_details import register_cell_details_callbacks

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
    ],
    suppress_callback_exceptions=True,
    assets_folder='assets'
)

app.title = "Defect Detection Analysis Dashboard"


# =============== KUBERNETES HEALTH CHECKS ===============
@app.server.route("/health/live")
def liveness():
    """Liveness: process is running. K8s uses this to decide whether to restart the pod."""
    return jsonify({"status": "alive"}), 200


@app.server.route("/health/ready")
def readiness():
    """Readiness: app is ready to accept traffic. K8s uses this for Service endpoints."""
    return jsonify({"status": "ready"}), 200


# =============== CONFIGURATION ===============
BASE_DIR = Path(__file__).parent.parent

# =============== LAYOUT COMPONENTS ===============

def create_header():
    """Create dashboard header"""
    return dbc.Container([
        html.Div([
            html.H1(
                "Defect Detection Analysis Dashboard",
                className="dashboard-title"
            ),
        ], className="dashboard-header")
    ], fluid=True, className="header-container")


def create_tab_navigation():
    """Create tab navigation"""
    return dbc.Tabs([
        dbc.Tab(
            label="📊 Report Generation",
            tab_id="report-generation",
            className="tab-content"
        ),
        dbc.Tab(
            label="📈 Analytics",
            tab_id="analytics",
            className="tab-content"
        ),
        dbc.Tab(
            label="📊 Confusion Matrices",
            tab_id="matrix",
            className="tab-content"
        ),
        dbc.Tab(
            label="📷 Image Viewer",
            tab_id="viewer",
            className="tab-content"
        ),
        dbc.Tab(
            label="🔍 Cell Details",
            tab_id="celldetail",
            className="tab-content"
        ),
        dbc.Tab(
            label="🎛️ Threshold Tweaker",
            tab_id="tweaker",
            className="tab-content"
        ),
    ], id="main-tabs", active_tab="report-generation", className="tab-navigation", style={"width": "100%", "display": "flex", "justifyContent": "space-between"})


# =============== MAIN LAYOUT ===============

app.layout = dbc.Container([
    # Data stores
    dcc.Store(id='data-store', data={}),
    dcc.Store(id='filtered-data-store', data={}),
    dcc.Store(id='threshold-config-store', data={}),
    dcc.Store(id='current-index-store', data=0),
    dcc.Store(id='current-cell-filter-store', data=None),
    dcc.Store(id='matrix-click-trigger', data=0),  # Triggers filter application from confusion matrix
    dcc.Store(id='matrix-filter-cscan', data=[]),  # Stores cscan filter from matrix click
    dcc.Store(id='matrix-filter-new-cscan', data=[]),  # Stores new cscan filter from matrix click
    dcc.Store(id='matrix-filter-final', data=[]),  # Stores final answer filter from matrix click
    dcc.Store(id='tweaker-model-store', data='old'),
    dcc.Store(id='adjusted-thresholds-store', data={}),
    dcc.Store(id='image-toggle-state-store', data={}),  # Structure: {record_id: {side: 'input'|'result'}}
    dcc.Store(id='expanded-rows-store', data={}),  # Structure: {index: bool} - tracks which rows are expanded
    dcc.Store(id='generated-folder-path', data=None),  # Stores folder name for reference
    dcc.Store(id='cell-details-filtered-data-store', data={}),  # Stores filtered data for cell details
    dcc.Store(id='cell-details-current-page-store', data=0),  # Stores current page for cell details
    dcc.Store(id='cell-details-original-filtered-data-store', data={}),  # Stores original matrix-filtered data (before user filters)
    dcc.Store(id='audit-tags-store', data={}, storage_type='session'),  # Shared audit tags store for Image Viewer and Cell Details
    dcc.Store(id='tweaker-original-answers-store', data={}),  # Stores original answers before threshold adjustment
    dcc.Store(id='tweaker-changed-records-store', data={}),  # Stores changed records from threshold tweaking
    dcc.Store(id='tweaker-current-side-store', data='back'),  # Stores currently selected side for threshold adjustment
    dcc.Store(id='tweaker-current-page-store', data=0),  # Stores current page for tweaker pagination
    dcc.Store(id='tweaker-image-toggle-state-store', data={}),  # Stores image toggle states for tweaker (structure: {record_id: {side: 'input'|'result'}})
    dcc.Store(id='clipboard-copy-dummy-store', data=None),  # Dummy store for clipboard copy callbacks
    dcc.Store(id='modal-gamma-store', data=1.0),  # Stores gamma value for modal image adjustment
    
    create_header(),
    create_tab_navigation(),
    
    html.Div(id="tab-content", className="tab-content-container", children=create_report_generation_tab()),
    
    # Modal for full image view
    dbc.Modal([
        dbc.ModalHeader([
            html.Div([
                dbc.ModalTitle("Image View", className="mb-0 d-inline-block me-3"),
                html.Div([
                    dbc.Label("Gamma: ", html_for="gamma-slider", className="mb-0 me-2", style={"fontSize": "0.9em", "verticalAlign": "middle"}),
                    html.Div([
                        dcc.Slider(
                            id="gamma-slider",
                            min=0.1,
                            max=3.0,
                            step=0.1,
                            value=1.0,
                            marks={0.5: "0.5", 1.0: "1.0", 1.5: "1.5", 2.0: "2.0", 2.5: "2.5"},
                            tooltip={"placement": "bottom", "always_visible": False}
                        )
                    ], style={"width": "200px", "display": "inline-block", "verticalAlign": "middle"})
                ], style={"display": "inline-block", "verticalAlign": "middle", "marginLeft": "auto"})
            ], style={"display": "flex", "alignItems": "center", "width": "100%"})
        ]),
        dbc.ModalBody([
            html.Div([
                html.Img(id="modal-image", src="", style={"width": "100%", "height": "auto"}),
                html.Canvas(id="modal-image-canvas", style={"display": "none"})
            ])
        ]),
        dbc.ModalFooter(dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0))
    ], id="image-modal", is_open=False, size="xl"),
    
], fluid=True, className="main-container")


# =============== CALLBACKS ===============

@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'active_tab')
)
def render_tab_content(active_tab):
    """Render content based on active tab"""
    if active_tab == "report-generation":
        return create_report_generation_tab()
    elif active_tab == "viewer":
        return create_image_viewer_tab()
    elif active_tab == "matrix":
        return create_confusion_matrix_tab()
    elif active_tab == "analytics":
        return create_analytics_tab()
    elif active_tab == "tweaker":
        return create_threshold_tweaker_tab()
    elif active_tab == "celldetail":
        return create_cell_details_tab()
    
    return html.Div("Select a tab to begin")


@app.callback(
    Output('threshold-config-store', 'data'),
    Input('main-tabs', 'active_tab')
)
def load_threshold_config_on_start(active_tab):
    """Load threshold config when app starts"""
    from utils.threshold_handler import load_threshold_config
    return load_threshold_config()


# Register component callbacks
register_report_generation_callbacks(app)
register_image_viewer_callbacks(app)
register_confusion_matrix_callbacks(app)
register_analytics_callbacks(app)
register_threshold_tweaker_callbacks(app)
register_cell_details_callbacks(app)


# Gamma adjustment callback for modal image using canvas for proper gamma correction
app.clientside_callback(
    """
    function(gamma_value, image_src) {
        if (!image_src || image_src === '') {
            return window.dash_clientside.no_update;
        }
        
        const img = document.getElementById('modal-image');
        const canvas = document.getElementById('modal-image-canvas');
        
        if (!img || !canvas) {
            return window.dash_clientside.no_update;
        }
        
        // Store original image source when it changes
        if (!img.dataset.originalSrc || img.dataset.originalSrc !== image_src) {
            img.dataset.originalSrc = image_src;
            // Reset to original source if we were showing a canvas-modified version
            if (img.src && img.src.startsWith('data:image')) {
                img.src = image_src;
            }
        }
        
        // Function to apply gamma correction using canvas
        function applyGammaCorrection() {
            try {
                // Reset to original source first
                if (img.src !== img.dataset.originalSrc) {
                    img.src = img.dataset.originalSrc;
                }
                
                // Wait for image to load
                if (!img.complete || img.naturalWidth === 0) {
                    img.onload = function() {
                        applyGammaCorrection();
                    };
                    return;
                }
                
                const ctx = canvas.getContext('2d');
                canvas.width = img.naturalWidth;
                canvas.height = img.naturalHeight;
                
                // Draw original image to canvas
                ctx.drawImage(img, 0, 0);
                
                // Get image data
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                const data = imageData.data;
                
                // Apply gamma correction: output = (input / 255) ^ (1/gamma) * 255
                const invGamma = 1.0 / (gamma_value || 1.0);
                
                for (let i = 0; i < data.length; i += 4) {
                    // Red channel
                    data[i] = Math.pow(data[i] / 255, invGamma) * 255;
                    // Green channel
                    data[i + 1] = Math.pow(data[i + 1] / 255, invGamma) * 255;
                    // Blue channel
                    data[i + 2] = Math.pow(data[i + 2] / 255, invGamma) * 255;
                    // Alpha channel stays the same
                }
                
                // Put modified image data back
                ctx.putImageData(imageData, 0, 0);
                
                // Replace img src with canvas data URL
                const dataUrl = canvas.toDataURL('image/png');
                img.src = dataUrl;
                img.style.filter = 'none';
            } catch (e) {
                // If CORS error or other issue, fall back to CSS filter approximation
                console.warn('Canvas gamma correction failed, using CSS filter:', e);
                applyCSSGamma(gamma_value);
            }
        }
        
        // Fallback: CSS filter approximation
        function applyCSSGamma(gamma) {
            if (gamma === 1.0 || !gamma) {
                img.style.filter = 'none';
                // Reset to original if we were showing canvas version
                if (img.src && img.src.startsWith('data:image') && img.dataset.originalSrc) {
                    img.src = img.dataset.originalSrc;
                }
            } else {
                // Reset to original source first
                if (img.src && img.src.startsWith('data:image') && img.dataset.originalSrc) {
                    img.src = img.dataset.originalSrc;
                }
                // Approximate gamma using brightness and contrast
                const brightness = Math.pow(gamma, 0.4);
                const contrast = 1 / Math.pow(gamma, 0.2);
                img.style.filter = `brightness(${brightness}) contrast(${contrast})`;
            }
        }
        
        // Apply gamma correction
        if (gamma_value === 1.0 || !gamma_value) {
            // Reset to original
            if (img.dataset.originalSrc) {
                img.src = img.dataset.originalSrc;
            }
            img.style.filter = 'none';
        } else {
            // Apply gamma correction
            if (img.complete && img.naturalWidth > 0) {
                applyGammaCorrection();
            } else {
                // Wait for image to load
                const loadHandler = function() {
                    applyGammaCorrection();
                    img.removeEventListener('load', loadHandler);
                };
                img.addEventListener('load', loadHandler);
            }
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output("modal-image-canvas", "style"),
    [Input("gamma-slider", "value"),
     Input("modal-image", "src")],
    prevent_initial_call=True
)


# =============== RUN APP ===============

# Expose server for gunicorn (production)
server = app.server

if __name__ == '__main__':
    import os
    # Get port from environment variable (Render sets this), default to 8050 for local
    port = int(os.getenv("PORT", 8050))
    host = os.getenv("HOST", "0.0.0.0")  # Render needs 0.0.0.0, local can use 127.0.0.1
    
    print("=" * 60)
    print("🚀 Starting Analysis Dashboard")
    print("=" * 60)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"🌐 Dashboard will be available at: http://{host}:{port}")
    print("=" * 60)
    app.run_server(debug=False, host=host, port=port)
