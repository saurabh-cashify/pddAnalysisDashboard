"""
Threshold configuration handler
Loads and processes threshold.json for classification
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_threshold_config(threshold_path: Optional[Path] = None) -> Dict:
    """
    Load threshold configuration from threshold.json
    
    Args:
        threshold_path: Path to threshold.json. If None, looks in analysisDashboard directory first
        
    Returns:
        Dictionary containing threshold configuration
    """
    if threshold_path is None:
        # First, try in analysisDashboard directory (current project directory)
        alt_path = Path(__file__).parent.parent / "threshold.json"
        if alt_path.exists():
            threshold_path = alt_path
        else:
            # Fallback to parent directory
            base_dir = Path(__file__).parent.parent.parent
            threshold_path = base_dir / "threshold.json"
    
    if isinstance(threshold_path, str):
        threshold_path = Path(threshold_path)
    
    if not threshold_path.exists():
        return {}
    
    try:
        print(f"📄 Loading threshold.json from: {threshold_path.absolute()}")
        with open(threshold_path, 'r') as f:
            config = json.load(f)
            print(f"✓ Successfully loaded threshold.json")
            return config
    except Exception as e:
        print(f"Error loading threshold config: {e}")
        return {}


def get_category_order_from_threshold(question_name: str, threshold_config: Optional[Dict] = None) -> List[str]:
    """
    Get category order from threshold.json for a given question.
    Returns list of categories in order they appear in threshold.json (using first side's order).
    
    Args:
        question_name: Name of the question (e.g., 'physicalConditionScratch')
        threshold_config: Threshold config dict. If None, loads from file.
        
    Returns:
        List of categories in order as they appear in threshold.json
    """
    if threshold_config is None:
        threshold_config = load_threshold_config()
    
    if question_name not in threshold_config:
        question_name = "default"
    
    question_thresholds = threshold_config.get(question_name, {})
    
    if not question_thresholds:
        return []
    
    # Use the order from the first side to ensure consistent ordering
    # All sides should have the same category order, so we use the first one
    first_side = next(iter(question_thresholds.values()))
    
    # Get categories in the exact order they appear in threshold.json
    category_order = [cat.lower().strip() for cat in first_side.keys()]
    print("order of categories", category_order)
    
    return category_order


def get_severity_order_from_thresholds(question_thresholds: Dict) -> List[str]:
    """
    Determine severity order of categories based on their maximum threshold values.
    Higher max threshold = higher severity.
    
    Args:
        question_thresholds: Dict with side -> category -> [min, max] thresholds
        
    Returns:
        List of categories sorted by severity (highest first)
    """
    category_max_scores = {}
    
    # Collect max scores for each category across all sides
    for side, side_thresholds in question_thresholds.items():
        for category, (min_val, max_val) in side_thresholds.items():
            # Track the highest max value for each category
            if category not in category_max_scores:
                category_max_scores[category] = max_val
            else:
                category_max_scores[category] = max(category_max_scores[category], max_val)
    
    # Sort categories by max score (descending) - higher max = higher severity
    sorted_categories = sorted(category_max_scores.items(), key=lambda x: x[1], reverse=True)
    severity_order = [cat for cat, _ in sorted_categories]
    
    return severity_order


def get_category_from_score(score: float, thresholds: Dict[str, List[float]]) -> Optional[str]:
    """
    Get category for a given score based on thresholds.
    
    Args:
        score: Score value
        thresholds: Dict mapping category -> [min, max] threshold range
        
    Returns:
        Category name if score falls within a range, None otherwise
    """
    if score is None or (isinstance(score, float) and (score != score)):  # Check for NaN
        return None
    
    for category, (min_val, max_val) in thresholds.items():
        if min_val <= score < max_val:
            return category
    
    return None


def get_severity_order(question_name: str = None, threshold_config: Optional[Dict] = None) -> List[str]:
    """
    Get severity order for classification labels.
    Falls back to hardcoded order if threshold config not available.
    
    Args:
        question_name: Question name to get order for
        threshold_config: Threshold config dict
        
    Returns:
        List of categories in severity order
    """
    if threshold_config is None:
        threshold_config = load_threshold_config()
    
    if question_name and question_name in threshold_config:
        question_thresholds = threshold_config[question_name]
        return get_severity_order_from_thresholds(question_thresholds)
    
    # Fallback to hardcoded order (for physicalConditionScratch)
    return [
        'major paint peel-off/bubble',
        'minor paint peel-off/bubble',
        'major scratch',
        'minor scratch',
        'normal sign of usage',
        'no scratches'
    ]


def normalize_category_for_confusion_matrix(value: str, question_name: str) -> str:
    """
    Normalize category values for confusion matrix.
    For physicalConditionPanel, combines 'glass panel damaged' with 'cracked or broken panel'.
    
    Args:
        value: Category value to normalize
        question_name: Question name for context
        
    Returns:
        Normalized category string
    """
    normalized = str(value).strip().lower()
    
    # For physicalConditionPanel, combine Glass Panel Damaged with Cracked or Broken Panel
    if question_name.lower() == "physicalconditionpanel":
        if normalized == "glass panel damaged":
            normalized = "cracked or broken panel"
    
    return normalized


def get_least_severe_category(question_name: str, threshold_config: Optional[Dict] = None) -> Optional[str]:
    """
    Get the least severe category for a given question.
    The least severe category is the one with the lowest maximum threshold value.
    
    Args:
        question_name: Name of the question (e.g., 'physicalConditionScratch')
        threshold_config: Threshold config dict. If None, loads from file.
        
    Returns:
        Least severe category name, or None if not found
    """
    if threshold_config is None:
        threshold_config = load_threshold_config()
    
    if question_name not in threshold_config:
        question_name = "default"
    
    question_thresholds = threshold_config.get(question_name, {})
    if not question_thresholds:
        return None
    
    severity_order = get_severity_order_from_thresholds(question_thresholds)
    
    # The least severe category is the last one in the severity order (lowest severity)
    if severity_order:
        return severity_order[-1]
    
    return None


def is_least_severe_category(category: str, question_name: str, threshold_config: Optional[Dict] = None) -> bool:
    """
    Check if a category is the least severe category for a given question.
    Performs case-insensitive comparison.
    
    Args:
        category: Category name to check
        question_name: Name of the question
        threshold_config: Threshold config dict. If None, loads from file.
        
    Returns:
        True if the category is the least severe, False otherwise
    """
    if not category:
        return False
    
    least_severe = get_least_severe_category(question_name, threshold_config)
    if not least_severe:
        return False
    
    # Case-insensitive comparison
    return str(category).strip().lower() == str(least_severe).strip().lower()

