"""
Statistics Tab Component
Display statistics about the loaded segmentation data
"""

from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from collections import Counter
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def create_statistics_tab():
    """Create the Statistics tab layout"""
    
    return dbc.Container([
        dbc.Card([
            dbc.CardBody([
                html.H3("📊 Dataset Statistics", className="mb-4", style={"color": "#3b82f6"}),
                
                html.Div(id="statistics-content", children=[
                    html.Div([
                        html.Div(className="spinner"),
                        html.P("Load data in Settings tab to view statistics...", className="text-center mt-3", style={"color": "#3b82f6"})
                    ], className="text-center py-5")
                ]),
            ])
        ]),
    ], fluid=True)


def register_statistics_callbacks(app):
    """Register callbacks for statistics tab"""
    
    @app.callback(
        Output('statistics-content', 'children'),
        Input('data-store', 'data')
    )
    def update_statistics(data_store):
        """Update statistics based on loaded data"""
        
        if not data_store or 'data' not in data_store:
            return html.Div([
                html.Div(className="spinner"),
                html.P("Load data in Settings tab to view statistics...", className="text-center mt-3", style={"color": "#3b82f6"})
            ], className="text-center py-5")
        
        data = data_store['data']
        total = len(data)
        
        if total == 0:
            return dbc.Alert("No data available", color="warning")
        
        # Calculate statistics
        total_images = total
        total_annotations = 0
        class_counts = Counter()
        images_with_labels = 0
        images_without_labels = 0
        
        for item in data:
            label_data = item.get('label_data')
            if label_data:
                images_with_labels += 1
                classes = label_data.get('classes', [])
                total_annotations += len(classes)
                for class_id in classes:
                    class_counts[class_id] += 1
            else:
                images_without_labels += 1
        
        # Create statistics cards
        stats_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(str(total_images), className="text-primary"),
                        html.P("Total Images", className="mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(str(total_annotations), className="text-success"),
                        html.P("Total Annotations", className="mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(str(len(class_counts)), className="text-info"),
                        html.P("Unique Classes", className="mb-0")
                    ])
                ], className="text-center")
            ], md=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H2(str(images_with_labels), className="text-warning"),
                        html.P("Images with Labels", className="mb-0")
                    ])
                ], className="text-center")
            ], md=3),
        ], className="mb-4")
        
        # Class distribution chart
        if class_counts:
            class_ids = list(class_counts.keys())
            counts = list(class_counts.values())
            
            fig_class_dist = go.Figure(data=[
                go.Bar(
                    x=[f"Class {cid}" for cid in class_ids],
                    y=counts,
                    marker_color='rgb(59, 130, 246)'
                )
            ])
            fig_class_dist.update_layout(
                title="Class Distribution",
                xaxis_title="Class ID",
                yaxis_title="Count",
                height=400
            )
            
            class_chart = dcc.Graph(figure=fig_class_dist)
        else:
            class_chart = dbc.Alert("No class data available", color="info")
        
        # Create layout
        return html.Div([
            stats_cards,
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Class Distribution", className="mb-3"),
                            class_chart
                        ])
                    ])
                ], md=12)
            ], className="mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Summary", className="mb-3"),
                            html.Ul([
                                html.Li(f"Total Images: {total_images}"),
                                html.Li(f"Images with Labels: {images_with_labels}"),
                                html.Li(f"Images without Labels: {images_without_labels}"),
                                html.Li(f"Total Annotations: {total_annotations}"),
                                html.Li(f"Unique Classes: {len(class_counts)}"),
                                html.Li(f"Average Annotations per Image: {total_annotations / images_with_labels if images_with_labels > 0 else 0:.2f}"),
                            ])
                        ])
                    ])
                ], md=12)
            ])
        ])

