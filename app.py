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
    
    create_header(),
    create_tab_navigation(),
    
    html.Div(id="tab-content", className="tab-content-container", children=create_report_generation_tab()),
    
    # Modal for full image view
    dbc.Modal([
        dbc.ModalHeader("Image Viewer"),
        dbc.ModalBody(html.Img(id="modal-image", style={"width": "100%", "height": "auto"})),
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


# =============== RUN APP ===============

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
