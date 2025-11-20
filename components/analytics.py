"""
Analytics Tab Component for Analysis Dashboard
Displays comprehensive performance analysis and insights for deployed and new models
"""

from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import base64
import io

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from utils.threshold_handler import normalize_category_for_confusion_matrix


def create_analytics_tab():
    """Create the Analytics tab layout with comprehensive performance analysis"""
    
    return dbc.Container([
        # Header
        dbc.Card([
            dbc.CardBody([
                html.H2("📈 Performance Analytics & Insights", className="mb-2", style={
                    "fontWeight": "700",
                    "fontSize": "2em",
                    "letterSpacing": "-0.5px"
                }),
                html.P("Comprehensive performance analysis for deployed and new models with day-wise trends", 
                       className="text-muted", style={"fontSize": "1.1em"})
            ])
        ], className="mb-4", style={
            "background": "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)", 
            "color": "white"
        }),
        
        # Section 1: Performance Overview Cards
        html.Div([
            html.H3("📊 Performance Overview", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            html.Div(id="performance-overview-cards", className="mb-4")
        ]),
        
        # Section 2: Day-wise Performance Chart
        html.Div([
            html.H3("📅 Day-wise Performance Trend", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="day-wise-performance-chart")
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
        # Section 3: Model Comparison Metrics
        html.Div([
            html.H3("⚖️ Model Comparison", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="model-comparison-table"),
                    html.Div([
                        dbc.Button("📥 Export Metrics CSV", id="export-metrics-csv-btn", color="primary", size="sm", className="mt-3"),
                        dcc.Download(id="download-metrics-csv")
                    ])
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
        # Section 4: Category Performance
        html.Div([
            html.H3("🏷️ Category Performance", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="category-performance-chart")
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
        # Section 5: Error Analysis
        html.Div([
            html.H3("❌ Error Analysis", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="error-analysis-chart")
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
        # Section 6: Performance by Side
        html.Div([
            html.H3("📐 Performance by Side", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="side-performance-chart")
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
        # Section 7: Score Distribution Comparison
        html.Div([
            html.H3("📊 Score Distribution Comparison", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            html.Div(id="score-distribution-charts", className="mb-5")
        ]),
        
        # Section 8: Agreement Analysis
        html.Div([
            html.H3("🤝 Agreement Analysis", className="mb-3", style={"color": "#3b82f6", "fontWeight": "600"}),
            dbc.Card([
                dbc.CardBody([
                    html.Div(id="agreement-analysis-chart")
                ])
            ], className="shadow-sm")
        ], className="mb-5"),
        
    ], fluid=True, className="tab-content-container")


def create_performance_card(icon, value, label, color="#3b82f6", subtitle=None):
    """Create a performance overview card"""
    return dbc.Col([
        dbc.Card([
            dbc.CardBody([
                html.Div(icon, style={"fontSize": "2.5em", "marginBottom": "10px"}),
                html.Div(value, className="fs-2 fw-bold", style={"color": color}),
                html.Div(label, className="text-muted small mb-1"),
                html.Div(subtitle, className="text-muted small") if subtitle else None
            ], className="text-center")
        ], className="shadow-sm h-100", style={"borderTop": f"4px solid {color}"})
    ], md=2, className="mb-3")


def register_analytics_callbacks(app):
    """Register callbacks for analytics tab"""
    
    @app.callback(
        [Output("performance-overview-cards", "children"),
         Output("day-wise-performance-chart", "children"),
         Output("model-comparison-table", "children"),
         Output("category-performance-chart", "children"),
         Output("error-analysis-chart", "children"),
         Output("side-performance-chart", "children"),
         Output("score-distribution-charts", "children"),
         Output("agreement-analysis-chart", "children")],
        Input("data-store", "data")
    )
    def update_analytics(data):
        """Generate all analytics visualizations"""
        
        if not data or not isinstance(data, dict):
            empty_msg = html.Div([
                html.H5("No data loaded", className="text-muted text-center py-5"),
                html.P("Please load data to view analytics", className="text-center text-muted")
            ])
            return [empty_msg] * 8
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            empty_msg = html.Div([
                html.H5("No data available", className="text-muted text-center py-5")
            ])
            return [empty_msg] * 8
        
        df = pd.DataFrame(records)
        
        # Check if new model data is available
        has_new_model = 'new_cscan_answer' in df.columns and df['new_cscan_answer'].notna().any()
        
        # Section 1: Performance Overview Cards
        overview_cards = create_performance_overview_cards(df, has_new_model)
        
        # Section 2: Day-wise Performance Chart
        day_chart = create_day_wise_performance_chart(df, has_new_model)
        
        # Section 3: Model Comparison Table
        comparison_table = create_model_comparison_table(df, has_new_model)
        
        # Section 4: Category Performance Chart
        category_chart = create_category_performance_chart(df, has_new_model)
        
        # Section 5: Error Analysis Chart
        error_chart = create_error_analysis_chart(df, has_new_model)
        
        # Section 6: Side Performance Chart
        side_chart = create_side_performance_chart(df, has_new_model)
        
        # Section 7: Score Distribution Charts
        score_dist_charts = create_score_distribution_charts(df, has_new_model)
        
        # Section 8: Agreement Analysis Chart
        agreement_chart = create_agreement_analysis_chart(df, has_new_model)
        
        return [
            overview_cards,
            day_chart,
            comparison_table,
            category_chart,
            error_chart,
            side_chart,
            score_dist_charts,
            agreement_chart
        ]
    
    # Export callbacks
    register_export_callbacks(app)


def create_performance_overview_cards(df, has_new_model):
    """Create performance overview cards"""
    
    cards = []
    
    # Overall Accuracy - Deployed Model
    deployed_acc = calculate_overall_accuracy(df, 'cscan_answer', 'final_answer')
    cards.append(create_performance_card(
        "🎯", f"{deployed_acc:.2f}%", "Deployed Model Accuracy", "#3b82f6"
    ))
    
    # Overall Accuracy - New Model (if available)
    if has_new_model:
        new_acc = calculate_overall_accuracy(df, 'new_cscan_answer', 'final_answer')
        cards.append(create_performance_card(
            "⚡", f"{new_acc:.2f}%", "New Model Accuracy", "#10b981"
        ))
        
        # Accuracy Improvement
        improvement = new_acc - deployed_acc
        improvement_color = "#10b981" if improvement > 0 else "#ef4444"
        improvement_sign = "+" if improvement > 0 else ""
        cards.append(create_performance_card(
            "📈", f"{improvement_sign}{improvement:.2f}%", "Accuracy Improvement", improvement_color
        ))
    else:
        # Placeholder for consistency
        cards.append(create_performance_card(
            "⚡", "N/A", "New Model Accuracy", "#9ca3af", "Not available"
        ))
        cards.append(create_performance_card(
            "📈", "N/A", "Accuracy Improvement", "#9ca3af", "Not available"
        ))
    
    # Total Records
    total_records = len(df)
    cards.append(create_performance_card(
        "📊", f"{total_records:,}", "Total Records", "#8b5cf6"
    ))
    
    # Agreement Rate - Deployed
    deployed_agreement = calculate_agreement_rate(df, 'cscan_answer', 'final_answer')
    cards.append(create_performance_card(
        "🤝", f"{deployed_agreement:.2f}%", "Deployed Agreement", "#f59e0b"
    ))
    
    # Agreement Rate - New (if available)
    if has_new_model:
        new_agreement = calculate_agreement_rate(df, 'new_cscan_answer', 'final_answer')
        cards.append(create_performance_card(
            "🤝", f"{new_agreement:.2f}%", "New Model Agreement", "#10b981"
        ))
    else:
        cards.append(create_performance_card(
            "🤝", "N/A", "New Model Agreement", "#9ca3af", "Not available"
        ))
    
    return dbc.Row(cards)


def create_day_wise_performance_chart(df, has_new_model):
    """Create day-wise performance trend chart"""
    
    if 'quote_date' not in df.columns:
        return html.Div("Date information not available", className="text-muted text-center py-5")
    
    # Convert quote_date to datetime - explicitly handle dd/mm/yyyy format
    # Try parsing with dayfirst=True first (for dd/mm/yyyy), then fallback to default
    try:
        df['quote_date_parsed'] = pd.to_datetime(df['quote_date'], format='%d/%m/%Y', errors='coerce')
        # If parsing failed for some dates, try with dayfirst=True
        if df['quote_date_parsed'].isna().any():
            df.loc[df['quote_date_parsed'].isna(), 'quote_date_parsed'] = pd.to_datetime(
                df.loc[df['quote_date_parsed'].isna(), 'quote_date'], 
                dayfirst=True, 
                errors='coerce'
            )
    except:
        # Fallback to dayfirst=True if format doesn't work
        df['quote_date_parsed'] = pd.to_datetime(df['quote_date'], dayfirst=True, errors='coerce')
    
    df = df[df['quote_date_parsed'].notna()]
    
    if len(df) == 0:
        return html.Div("No valid date data available", className="text-muted text-center py-5")
    
    # Group by date and calculate accuracy
    daily_stats = []
    
    for date, group in df.groupby(df['quote_date_parsed'].dt.date):
        # Deployed model accuracy
        deployed_acc = calculate_overall_accuracy(group, 'cscan_answer', 'final_answer')
        daily_stats.append({
            'date': date,
            'Deployed Model': deployed_acc,
            'count': len(group)
        })
        
        # New model accuracy (if available)
        if has_new_model:
            new_acc = calculate_overall_accuracy(group, 'new_cscan_answer', 'final_answer')
            daily_stats[-1]['New Model'] = new_acc
    
    daily_df = pd.DataFrame(daily_stats)
    daily_df = daily_df.sort_values('date')
    
    # Create line chart
    fig = go.Figure()
    
    # Deployed model line
    fig.add_trace(go.Scatter(
        x=daily_df['date'],
        y=daily_df['Deployed Model'],
        mode='lines+markers',
        name='Deployed Model',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8, color='#3b82f6'),
        hovertemplate='<b>Date:</b> %{x}<br><b>Accuracy:</b> %{y:.2f}%<br><b>Records:</b> %{customdata}<extra></extra>',
        customdata=daily_df['count']
    ))
    
    # New model line (if available)
    if has_new_model and 'New Model' in daily_df.columns:
        fig.add_trace(go.Scatter(
            x=daily_df['date'],
            y=daily_df['New Model'],
            mode='lines+markers',
            name='New Model',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8, color='#10b981'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Accuracy:</b> %{y:.2f}%<br><b>Records:</b> %{customdata}<extra></extra>',
            customdata=daily_df['count']
        ))
    
    fig.update_layout(
        title="Day-wise Accuracy Trend",
        xaxis_title="Date",
        yaxis_title="Accuracy (%)",
        height=450,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'toImageButtonOptions': {'filename': 'day_wise_performance'}})


def create_model_comparison_table(df, has_new_model):
    """Create model comparison metrics table"""
    
    comparison_data = []
    
    # Overall Accuracy
    deployed_overall = calculate_overall_accuracy(df, 'cscan_answer', 'final_answer')
    comparison_data.append({
        'Metric': 'Overall Accuracy',
        'Deployed Model': f"{deployed_overall:.2f}%",
        'New Model': f"{calculate_overall_accuracy(df, 'new_cscan_answer', 'final_answer'):.2f}%" if has_new_model else "N/A",
        'Improvement': f"+{calculate_overall_accuracy(df, 'new_cscan_answer', 'final_answer') - deployed_overall:.2f}%" if has_new_model else "N/A"
    })
    
    # Per-category accuracy
    categories = get_all_categories(df)
    for category in categories:
        deployed_cat_acc = calculate_category_accuracy(df, 'cscan_answer', 'final_answer', category)
        if has_new_model:
            new_cat_acc = calculate_category_accuracy(df, 'new_cscan_answer', 'final_answer', category)
            improvement = new_cat_acc - deployed_cat_acc
            comparison_data.append({
                'Metric': f'Category: {category}',
                'Deployed Model': f"{deployed_cat_acc:.2f}%",
                'New Model': f"{new_cat_acc:.2f}%",
                'Improvement': f"+{improvement:.2f}%" if improvement > 0 else f"{improvement:.2f}%"
            })
        else:
            comparison_data.append({
                'Metric': f'Category: {category}',
                'Deployed Model': f"{deployed_cat_acc:.2f}%",
                'New Model': "N/A",
                'Improvement': "N/A"
            })
    
    # Per-side accuracy
    sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
    for side in sides:
        deployed_side_acc = calculate_side_accuracy(df, 'cscan_answer', 'final_answer', side)
        if has_new_model:
            new_side_acc = calculate_side_accuracy(df, 'new_cscan_answer', 'final_answer', side)
            improvement = new_side_acc - deployed_side_acc
            comparison_data.append({
                'Metric': f'Side: {side.capitalize()}',
                'Deployed Model': f"{deployed_side_acc:.2f}%",
                'New Model': f"{new_side_acc:.2f}%",
                'Improvement': f"+{improvement:.2f}%" if improvement > 0 else f"{improvement:.2f}%"
            })
        else:
            comparison_data.append({
                'Metric': f'Side: {side.capitalize()}',
                'Deployed Model': f"{deployed_side_acc:.2f}%",
                'New Model': "N/A",
                'Improvement': "N/A"
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    return dbc.Table.from_dataframe(
        comparison_df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mt-3"
    )


def create_category_performance_chart(df, has_new_model):
    """Create category performance bar chart"""
    
    categories = get_all_categories(df)
    if not categories:
        return html.Div("No category data available", className="text-muted text-center py-5")
    
    deployed_accs = []
    new_accs = []
    
    for category in categories:
        deployed_accs.append(calculate_category_accuracy(df, 'cscan_answer', 'final_answer', category))
        if has_new_model:
            new_accs.append(calculate_category_accuracy(df, 'new_cscan_answer', 'final_answer', category))
    
    fig = go.Figure()
    
    # Deployed model bars
    fig.add_trace(go.Bar(
        name='Deployed Model',
        x=categories,
        y=deployed_accs,
        marker_color='#3b82f6',
        text=[f"{acc:.1f}%" for acc in deployed_accs],
        textposition='outside'
    ))
    
    # New model bars (if available)
    if has_new_model:
        fig.add_trace(go.Bar(
            name='New Model',
            x=categories,
            y=new_accs,
            marker_color='#10b981',
            text=[f"{acc:.1f}%" for acc in new_accs],
            textposition='outside'
    ))
    
    fig.update_layout(
        title="Accuracy by Category",
        xaxis_title="Category",
        yaxis_title="Accuracy (%)",
        barmode='group',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=30, t=60, b=100),
        xaxis_tickangle=-45
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'toImageButtonOptions': {'filename': 'category_performance'}})


def create_error_analysis_chart(df, has_new_model):
    """Create error analysis chart showing top misclassifications"""
    
    # Get top misclassifications for deployed model
    deployed_errors = get_top_misclassifications(df, 'cscan_answer', 'final_answer', top_n=10)
    
    if not deployed_errors:
        return html.Div("No error data available", className="text-muted text-center py-5")
    
    # Create bar chart
    error_labels = [f"{err['predicted']} → {err['actual']}" for err in deployed_errors]
    error_counts = [err['count'] for err in deployed_errors]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=error_labels,
        y=error_counts,
        marker_color='#ef4444',
        text=error_counts,
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Top Misclassifications (Deployed Model)",
        xaxis_title="Predicted → Actual",
        yaxis_title="Count",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=60, r=30, t=60, b=150),
        xaxis_tickangle=-45
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'toImageButtonOptions': {'filename': 'error_analysis'}})


def create_side_performance_chart(df, has_new_model):
    """Create side performance chart (radar or bar)"""
    
    sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
    deployed_accs = []
    new_accs = []
    
    for side in sides:
        deployed_accs.append(calculate_side_accuracy(df, 'cscan_answer', 'final_answer', side))
        if has_new_model:
            new_accs.append(calculate_side_accuracy(df, 'new_cscan_answer', 'final_answer', side))
    
    # Use bar chart for better readability
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Deployed Model',
        x=[s.capitalize() for s in sides],
        y=deployed_accs,
        marker_color='#3b82f6',
        text=[f"{acc:.1f}%" for acc in deployed_accs],
        textposition='outside'
    ))
    
    if has_new_model:
        fig.add_trace(go.Bar(
            name='New Model',
            x=[s.capitalize() for s in sides],
            y=new_accs,
            marker_color='#10b981',
            text=[f"{acc:.1f}%" for acc in new_accs],
            textposition='outside'
        ))
    
    fig.update_layout(
        title="Accuracy by Side",
        xaxis_title="Side",
        yaxis_title="Accuracy (%)",
        barmode='group',
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'toImageButtonOptions': {'filename': 'side_performance'}})


def create_score_distribution_charts(df, has_new_model):
    """Create score distribution comparison charts for each side"""
    
    sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
    charts = []
    
    for side in sides[:4]:  # Show first 4 sides to avoid clutter
        deployed_col = f"{side}_score"
        new_col = f"new_{side}_score" if has_new_model else None
        
        if deployed_col not in df.columns:
            continue
        
        fig = go.Figure()
        
        # Deployed model distribution
        deployed_scores = pd.to_numeric(df[deployed_col], errors='coerce').dropna()
        if len(deployed_scores) > 0:
            fig.add_trace(go.Histogram(
                x=deployed_scores,
                name='Deployed Model',
                marker_color='#3b82f6',
                opacity=0.7,
                nbinsx=20
            ))
        
        # New model distribution (if available)
        if has_new_model and new_col and new_col in df.columns:
            new_scores = pd.to_numeric(df[new_col], errors='coerce').dropna()
            if len(new_scores) > 0:
                fig.add_trace(go.Histogram(
                    x=new_scores,
                    name='New Model',
                    marker_color='#10b981',
                    opacity=0.7,
                    nbinsx=20
                ))
        
        fig.update_layout(
            title=f"{side.capitalize()} Side Score Distribution",
            xaxis_title="Score",
            yaxis_title="Frequency",
            barmode='overlay',
            height=300,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=60, r=30, t=60, b=60)
        )
        
        charts.append(
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(figure=fig, config={'displayModeBar': False})
                    ])
                ], className="shadow-sm")
            ], md=6, className="mb-3")
        )
    
    return dbc.Row(charts) if charts else html.Div("No score data available", className="text-muted text-center py-5")


def create_agreement_analysis_chart(df, has_new_model):
    """Create agreement analysis pie chart"""
    
    if not has_new_model:
        return html.Div("New model data not available for agreement analysis", className="text-muted text-center py-5")
    
    # Calculate agreement scenarios
    both_agree = 0
    only_deployed_agrees = 0
    only_new_agrees = 0
    both_disagree = 0
    
    for _, row in df.iterrows():
        final = str(row.get('final_answer', '')).strip().lower() if pd.notna(row.get('final_answer')) else ''
        deployed = str(row.get('cscan_answer', '')).strip().lower() if pd.notna(row.get('cscan_answer')) else ''
        new = str(row.get('new_cscan_answer', '')).strip().lower() if pd.notna(row.get('new_cscan_answer')) else ''
        
        deployed_match = deployed == final
        new_match = new == final
        
        if deployed_match and new_match:
            both_agree += 1
        elif deployed_match:
            only_deployed_agrees += 1
        elif new_match:
            only_new_agrees += 1
        else:
            both_disagree += 1
    
    labels = ['Both Agree', 'Only Deployed Agrees', 'Only New Agrees', 'Both Disagree']
    values = [both_agree, only_deployed_agrees, only_new_agrees, both_disagree]
    colors = ['#10b981', '#3b82f6', '#10b981', '#ef4444']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="Model Agreement Analysis",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02)
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': True, 'toImageButtonOptions': {'filename': 'agreement_analysis'}})


# Helper functions

def calculate_overall_accuracy(df, predicted_col, actual_col):
    """Calculate overall accuracy"""
    if predicted_col not in df.columns or actual_col not in df.columns:
        return 0.0
    
    matches = (df[predicted_col].astype(str).str.lower().str.strip() == 
              df[actual_col].astype(str).str.lower().str.strip())
    total = df[predicted_col].notna().sum()
    
    return (matches.sum() / total * 100) if total > 0 else 0.0


def calculate_agreement_rate(df, predicted_col, actual_col):
    """Calculate agreement rate (same as accuracy)"""
    return calculate_overall_accuracy(df, predicted_col, actual_col)


def calculate_category_accuracy(df, predicted_col, actual_col, category):
    """Calculate accuracy for a specific category"""
    if predicted_col not in df.columns or actual_col not in df.columns:
        return 0.0
    
    # Filter to category
    category_df = df[df[actual_col].astype(str).str.lower().str.strip() == category.lower().strip()]
    
    if len(category_df) == 0:
        return 0.0
    
    matches = (category_df[predicted_col].astype(str).str.lower().str.strip() == 
              category_df[actual_col].astype(str).str.lower().str.strip())
    
    return (matches.sum() / len(category_df) * 100) if len(category_df) > 0 else 0.0


def calculate_side_accuracy(df, predicted_col, actual_col, side):
    """Calculate accuracy for records where a specific side contributed"""
    if predicted_col not in df.columns or actual_col not in df.columns:
        return 0.0
    
    # Filter to records where this side contributed
    contributing_col = 'contributing_sides' if 'new_' not in predicted_col else 'new_contributing_sides'
    
    if contributing_col not in df.columns:
        # If contributing_sides column doesn't exist, calculate overall accuracy
        return calculate_overall_accuracy(df, predicted_col, actual_col)
    
    # Filter records where this side contributed
    side_df = df[df[contributing_col].astype(str).str.lower().str.contains(side.lower(), na=False)]
    
    if len(side_df) == 0:
        return 0.0
    
    matches = (side_df[predicted_col].astype(str).str.lower().str.strip() == 
              side_df[actual_col].astype(str).str.lower().str.strip())
    
    return (matches.sum() / len(side_df) * 100) if len(side_df) > 0 else 0.0


def get_all_categories(df):
    """Get all unique categories from final_answer"""
    if 'final_answer' not in df.columns:
        return []
    
    categories = df['final_answer'].dropna().astype(str).str.strip().unique().tolist()
    return sorted([c for c in categories if c])


def get_top_misclassifications(df, predicted_col, actual_col, top_n=10):
    """Get top misclassifications"""
    if predicted_col not in df.columns or actual_col not in df.columns:
        return []
    
    errors = []
    
    for _, row in df.iterrows():
        predicted = str(row.get(predicted_col, '')).strip().lower() if pd.notna(row.get(predicted_col)) else ''
        actual = str(row.get(actual_col, '')).strip().lower() if pd.notna(row.get(actual_col)) else ''
        
        if predicted and actual and predicted != actual:
            errors.append(f"{predicted} → {actual}")
    
    # Count errors
    error_counts = {}
    for error in errors:
        error_counts[error] = error_counts.get(error, 0) + 1
    
    # Convert to list of dicts
    top_errors = []
    for error, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        parts = error.split(' → ')
        top_errors.append({
            'predicted': parts[0] if len(parts) > 0 else '',
            'actual': parts[1] if len(parts) > 1 else '',
            'count': count
        })
    
    return top_errors


# Export functionality

def register_export_callbacks(app):
    """Register export callbacks"""
    
    @app.callback(
        Output("download-metrics-csv", "data"),
        Input("export-metrics-csv-btn", "n_clicks"),
        State("data-store", "data"),
        prevent_initial_call=True
    )
    def export_metrics_csv(n_clicks, data):
        """Export model comparison metrics as CSV"""
        if not data or not isinstance(data, dict):
            return None
        
        # Extract records
        if "data" in data:
            records = data["data"]
        else:
            records = data if isinstance(data, list) else []
        
        if not records:
            return None
        
        df = pd.DataFrame(records)
        has_new_model = 'new_cscan_answer' in df.columns and df['new_cscan_answer'].notna().any()
        
        # Recreate comparison table data
        comparison_data = []
        
        # Overall Accuracy
        deployed_overall = calculate_overall_accuracy(df, 'cscan_answer', 'final_answer')
        comparison_data.append({
            'Metric': 'Overall Accuracy',
            'Deployed Model': f"{deployed_overall:.2f}%",
            'New Model': f"{calculate_overall_accuracy(df, 'new_cscan_answer', 'final_answer'):.2f}%" if has_new_model else "N/A",
            'Improvement': f"+{calculate_overall_accuracy(df, 'new_cscan_answer', 'final_answer') - deployed_overall:.2f}%" if has_new_model else "N/A"
        })
        
        # Per-category accuracy
        categories = get_all_categories(df)
        for category in categories:
            deployed_cat_acc = calculate_category_accuracy(df, 'cscan_answer', 'final_answer', category)
            if has_new_model:
                new_cat_acc = calculate_category_accuracy(df, 'new_cscan_answer', 'final_answer', category)
                improvement = new_cat_acc - deployed_cat_acc
                comparison_data.append({
                    'Metric': f'Category: {category}',
                    'Deployed Model': f"{deployed_cat_acc:.2f}%",
                    'New Model': f"{new_cat_acc:.2f}%",
                    'Improvement': f"+{improvement:.2f}%" if improvement > 0 else f"{improvement:.2f}%"
                })
            else:
                comparison_data.append({
                    'Metric': f'Category: {category}',
                    'Deployed Model': f"{deployed_cat_acc:.2f}%",
                    'New Model': "N/A",
                    'Improvement': "N/A"
                })
        
        # Per-side accuracy
        sides = ['top', 'bottom', 'left', 'right', 'back', 'front']
        for side in sides:
            deployed_side_acc = calculate_side_accuracy(df, 'cscan_answer', 'final_answer', side)
            if has_new_model:
                new_side_acc = calculate_side_accuracy(df, 'new_cscan_answer', 'final_answer', side)
                improvement = new_side_acc - deployed_side_acc
                comparison_data.append({
                    'Metric': f'Side: {side.capitalize()}',
                    'Deployed Model': f"{deployed_side_acc:.2f}%",
                    'New Model': f"{new_side_acc:.2f}%",
                    'Improvement': f"+{improvement:.2f}%" if improvement > 0 else f"{improvement:.2f}%"
                })
            else:
                comparison_data.append({
                    'Metric': f'Side: {side.capitalize()}',
                    'Deployed Model': f"{deployed_side_acc:.2f}%",
                    'New Model': "N/A",
                    'Improvement': "N/A"
                })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        return dcc.send_data_frame(comparison_df.to_csv, "model_comparison_metrics.csv", index=False)
    
    # Note: Chart exports are handled by Plotly's built-in export button (toImageButtonOptions)
    # The export buttons for charts are kept for UI consistency but use Plotly's native export
