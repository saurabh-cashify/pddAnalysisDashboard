"""
Data loading and processing utilities
"""

import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Optional
from pathlib import Path
import os

from .threshold_handler import (
    get_severity_order,
    normalize_category_for_confusion_matrix,
    get_category_order_from_threshold
)


def load_csv_data(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Load CSV data from file
    
    Args:
        csv_path: Path to CSV file. If None, looks for default path.
        
    Returns:
        DataFrame with data, filtered to rows with pdd_txn_id
    """
    if csv_path is None:
        # Look for default path in parent directory
        base_dir = Path(__file__).parent.parent.parent
        default_path = base_dir / "analysis_2025_11_13_physicalConditionPanel_10NOV" / "analysis_2025_11_13.csv"
        csv_path = default_path
    
    if isinstance(csv_path, str):
        csv_path = Path(csv_path)
    
    if not csv_path.exists():
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(csv_path)
        # Filter out rows without pdd_txn_id
        df = df[df['pdd_txn_id'].notna()]
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()


def prepare_matrix_data(
    df: pd.DataFrame,
    predicted_col: str,
    actual_col: str = 'final_answer',
    question_name: Optional[str] = None,
    threshold_config: Optional[Dict] = None
) -> Dict:
    """
    Prepare confusion matrix data from DataFrame
    
    Args:
        df: DataFrame with prediction and actual columns
        predicted_col: Column name for predictions
        actual_col: Column name for actual values
        question_name: Question name for category ordering
        threshold_config: Threshold config for category ordering
        
    Returns:
        Dictionary with matrix data, labels, accuracy, etc.
    """
    valid_df = df[
        df[predicted_col].notna() & 
        df[actual_col].notna() &
        (df[predicted_col].astype(str).str.strip() != '') &
        (df[actual_col].astype(str).str.strip() != '')
    ].copy()
    
    if len(valid_df) == 0:
        return {
            'labels': [],
            'matrix': [],
            'accuracy': 0,
            'correct': 0,
            'total': 0,
            'cell_records': {}
        }
    
    # Normalize values
    if question_name:
        valid_df['predicted_normalized'] = valid_df[predicted_col].apply(
            lambda x: normalize_category_for_confusion_matrix(x, question_name)
        )
        valid_df['actual_normalized'] = valid_df[actual_col].apply(
            lambda x: normalize_category_for_confusion_matrix(x, question_name)
        )
    else:
        valid_df['predicted_normalized'] = valid_df[predicted_col].astype(str).str.lower().str.strip()
        valid_df['actual_normalized'] = valid_df[actual_col].astype(str).str.lower().str.strip()
    
    # Get category order
    if question_name and threshold_config:
        category_order = get_category_order_from_threshold(question_name, threshold_config)
        # Get all unique labels from data
        data_labels = set(valid_df['predicted_normalized'].unique()) | set(valid_df['actual_normalized'].unique())
        # Use threshold order but only include categories that exist in data
        labels = [cat for cat in category_order if cat in data_labels]
        # Add any missing categories
        missing = sorted(data_labels - set(labels))
        labels.extend(missing)
    else:
        # Fallback to severity order or alphabetical
        severity_order = get_severity_order(question_name, threshold_config)
        data_labels = set(valid_df['predicted_normalized'].unique()) | set(valid_df['actual_normalized'].unique())
        labels = [cat for cat in severity_order if cat in data_labels]
        missing = sorted(data_labels - set(labels))
        labels.extend(missing)
    
    if len(labels) == 0:
        return {
            'labels': [],
            'matrix': [],
            'accuracy': 0,
            'correct': 0,
            'total': 0,
            'cell_records': {}
        }
    
    # Initialize matrix
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    cell_records = {actual: {pred: [] for pred in labels} for actual in labels}
    
    correct = 0
    for _, row in valid_df.iterrows():
        predicted = row['predicted_normalized']
        actual = row['actual_normalized']
        
        if predicted in labels and actual in labels:
            matrix[actual][predicted] += 1
            cell_records[actual][predicted].append(row.to_dict())
            if predicted == actual:
                correct += 1
    
    # Convert to 2D array
    z_data = [[matrix[actual][pred] for pred in labels] for actual in labels]
    
    accuracy = (correct / len(valid_df) * 100) if len(valid_df) > 0 else 0
    
    return {
        'labels': labels,
        'matrix': z_data,
        'accuracy': accuracy,
        'correct': correct,
        'total': len(valid_df),
        'cell_records': cell_records
    }


def create_confusion_matrix_plot(
    matrix_data: Dict,
    plot_id: str = None,
    title: str = "",
    colorscale: Optional[List] = None
) -> go.Figure:
    """
    Create Plotly confusion matrix heatmap
    
    Args:
        matrix_data: Dictionary with matrix data from prepare_matrix_data
        plot_id: ID for the plot (not used in Plotly, kept for compatibility)
        title: Title for the plot
        colorscale: Custom colorscale. If None, uses default blue scale.
        
    Returns:
        Plotly Figure object
    """
    if not matrix_data['labels']:
        return go.Figure()
    
    labels_display = [l.capitalize() for l in matrix_data['labels']]
    
    if colorscale is None:
        colorscale = [
            [0, '#f0f9ff'],
            [0.2, '#e0f2fe'],
            [0.4, '#bae6fd'],
            [0.6, '#7dd3fc'],
            [0.8, '#38bdf8'],
            [1, '#0ea5e9']
        ]
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data['matrix'],
        x=labels_display,
        y=labels_display,
        colorscale=colorscale,
        showscale=True,
        hovertemplate='<b>Predicted:</b> %{x}<br><b>Actual:</b> %{y}<br><b>Count:</b> %{z}<br><br>🖱️ <i>Click to view these records</i><extra></extra>',
        text=matrix_data['matrix'],
        texttemplate='%{text}',
        textfont={'size': 14, 'color': '#1e293b'}
    ))
    
    fig.update_layout(
        title=title,
        xaxis={'title': 'Predicted', 'side': 'bottom', 'tickangle': -45},
        yaxis={'title': 'Actual (Ground Truth)', 'autorange': 'reversed'},
        margin={'l': 150, 'r': 50, 't': 50, 'b': 150},
        height=600
    )
    
    return fig

