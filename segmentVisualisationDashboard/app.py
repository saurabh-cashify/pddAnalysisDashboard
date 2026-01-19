"""
Segmentation Data Visualization Dashboard
A utility dashboard for visualizing annotated segmentation data with masks and overlays
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from pathlib import Path
import os

# Import components
from components import (
    create_image_viewer_tab,
    create_statistics_tab,
    create_settings_tab
)

# Import component callbacks
from components.image_viewer import register_image_viewer_callbacks
from components.statistics import register_statistics_callbacks
from components.settings import register_settings_callbacks

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

app.title = "Segmentation Data Visualization Dashboard"

# =============== CONFIGURATION ===============
BASE_DIR = Path(__file__).parent

# =============== LAYOUT COMPONENTS ===============

def create_header():
    """Create dashboard header"""
    return dbc.Container([
        html.Div([
            html.H1(
                "Segmentation Data Visualization Dashboard",
                className="dashboard-title"
            ),
            html.P(
                "Visualize and analyze your annotated segmentation data",
                className="dashboard-subtitle"
            ),
        ], className="dashboard-header")
    ], fluid=True, className="header-container")


def create_tab_navigation():
    """Create tab navigation"""
    return dbc.Tabs([
        dbc.Tab(
            label="⚙️ Settings",
            tab_id="settings",
            className="tab-content"
        ),
        dbc.Tab(
            label="📊 Statistics",
            tab_id="statistics",
            className="tab-content"
        ),
        dbc.Tab(
            label="🖼️ Image Viewer",
            tab_id="viewer",
            className="tab-content"
        ),
    ], id="main-tabs", active_tab="settings", className="tab-navigation")


# =============== MAIN LAYOUT ===============

app.layout = dbc.Container([
    # Data stores
    dcc.Store(id='data-store', data={}),  # Stores loaded image and label data
    dcc.Store(id='current-index-store', data=0),  # Current image index
    dcc.Store(id='label-format-store', data=None),  # Selected label format
    dcc.Store(id='images-path-store', data=None),  # Images folder path
    dcc.Store(id='labels-path-store', data=None),  # Labels folder path
    dcc.Store(id='class-colors-store', data={}),  # Color mapping for classes
    dcc.Store(id='overlay-opacity-store', data={}),  # Overlay opacity per record {index: opacity}
    dcc.Store(id='modal-state-store', data={'view': None, 'index': None}),  # Current modal view state
    
    create_header(),
    create_tab_navigation(),
    
    html.Div(id="tab-content", className="tab-content-container", children=create_settings_tab()),
    
    # Modal for full image view
    dbc.Modal([
        dbc.ModalHeader([
            dbc.ModalTitle("Image View", style={"margin": "0", "marginRight": "auto"}),
            # Overlay opacity slider (only shown for overlay view) - in header
            html.Div(id="modal-overlay-controls", style={"display": "none", "marginLeft": "20px", "minWidth": "350px"}, children=[
                html.Div([
                    html.Span("Opacity: ", className="fw-bold", style={"fontSize": "0.85em", "marginRight": "8px", "whiteSpace": "nowrap"}),
                    html.Div([
                        dcc.Slider(
                            id="modal-overlay-opacity-slider",
                            min=0,
                            max=100,
                            step=5,
                            value=100,
                            marks={i: f"{i}%" for i in range(0, 101, 25)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ], style={"width": "300px", "display": "inline-block"}),
                ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
            ]),
        ], style={"display": "flex", "alignItems": "center", "justifyContent": "space-between"}),
        dbc.ModalBody([
            html.Img(id="modal-image", src="", style={"width": "100%", "height": "auto"}),
        ]),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
        ])
    ], id="image-modal", is_open=False, size="xl", centered=True),
    
], fluid=True, className="main-container")


# =============== CALLBACKS ===============

@app.callback(
    Output('tab-content', 'children'),
    Input('main-tabs', 'active_tab')
)
def render_tab_content(active_tab):
    """Render content based on active tab"""
    if active_tab == "settings":
        return create_settings_tab()
    elif active_tab == "statistics":
        return create_statistics_tab()
    elif active_tab == "viewer":
        return create_image_viewer_tab()
    
    return html.Div("Select a tab to begin")


# Register component callbacks
register_settings_callbacks(app)
register_statistics_callbacks(app)
register_image_viewer_callbacks(app)


# =============== RUN APP ===============

# Expose server for gunicorn (production)
server = app.server

if __name__ == '__main__':
    import os
    # Get port from environment variable (Render sets this), default to 8051 for local
    port = int(os.getenv("PORT", 8051))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("=" * 60)
    print("🚀 Starting Segmentation Visualization Dashboard")
    print("=" * 60)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"🌐 Dashboard will be available at: http://{host}:{port}")
    print("=" * 60)
    app.run_server(debug=True, host=host, port=port)

