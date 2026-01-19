"""
Dashboard component modules
"""

from .settings import create_settings_tab, register_settings_callbacks
from .statistics import create_statistics_tab, register_statistics_callbacks
from .image_viewer import create_image_viewer_tab, register_image_viewer_callbacks

__all__ = [
    'create_settings_tab',
    'register_settings_callbacks',
    'create_statistics_tab',
    'register_statistics_callbacks',
    'create_image_viewer_tab',
    'register_image_viewer_callbacks'
]

