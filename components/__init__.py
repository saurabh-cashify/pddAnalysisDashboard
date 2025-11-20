"""
Dashboard component modules
"""

from .report_generation import create_report_generation_tab, register_report_generation_callbacks
from .image_viewer import create_image_viewer_tab, register_image_viewer_callbacks
from .confusion_matrix import create_confusion_matrix_tab, register_confusion_matrix_callbacks
from .analytics import create_analytics_tab, register_analytics_callbacks
from .threshold_tweaker import create_threshold_tweaker_tab, register_threshold_tweaker_callbacks
from .cell_details import create_cell_details_tab, register_cell_details_callbacks

__all__ = [
    'create_report_generation_tab',
    'register_report_generation_callbacks',
    'create_image_viewer_tab',
    'register_image_viewer_callbacks',
    'create_confusion_matrix_tab',
    'register_confusion_matrix_callbacks',
    'create_analytics_tab',
    'register_analytics_callbacks',
    'create_threshold_tweaker_tab',
    'register_threshold_tweaker_callbacks',
    'create_cell_details_tab',
    'register_cell_details_callbacks'
]

