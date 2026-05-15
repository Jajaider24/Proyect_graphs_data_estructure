"""
Main entry point for SkyRoute Planner Frontend.

Flet-based desktop application for airline route planning.
Connects to FastAPI backend at http://localhost:8000
"""

import flet as ft
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.ui.main_window import MainWindow
from frontend.config import APP_CONFIG


def main(page: ft.Page):
    """
    Flet entry point.
    
    Args:
        page: Flet page object
    """
    # Configure page
    page.title = APP_CONFIG["APP_TITLE"]
    page.window_width = APP_CONFIG["WINDOW_WIDTH"]
    page.window_height = APP_CONFIG["WINDOW_HEIGHT"]
    page.window_resizable = True
    page.window_min_width = 1000
    page.window_min_height = 600
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # Create and start main window
    window = MainWindow(page)
    window.build()


if __name__ == "__main__":
    ft.app(target=main, assets_dir="frontend/assets")
