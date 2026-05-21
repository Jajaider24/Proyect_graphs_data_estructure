"""
Main window UI for SkyRoute Planner.
"""

import asyncio
import flet as ft
from frontend.config import COLORS, SIZES, NAV_ITEMS
from frontend.ui.pages.dashboard_page import DashboardPage
from frontend.ui.pages.graph_page import GraphPage
from frontend.ui.pages.network_page import NetworkPage
from frontend.ui.pages.planning_page import PlanningPage
from frontend.ui.pages.routes_page import RoutesPage
from frontend.ui.pages.settings_page import SettingsPage


class MainWindow:
    """Main application window."""
    
    def __init__(self, page: ft.Page):
        """
        Initialize main window.
        
        Args:
            page: Flet page object
        """
        self.page = page
        self.current_page = "dashboard"
        
        # Initialize pages
        self.pages = {
            "dashboard": DashboardPage(self),
            "network": NetworkPage(self),
            "network_graph": GraphPage(self),
            "planning": PlanningPage(self),
            "routes": RoutesPage(self),
            "settings": SettingsPage(self)
        }
    
    def build(self):
        """Build UI structure."""
        # Create navigation rail
        nav_rail = self._create_navigation_rail()
        
        # Create content area
        self.content_area = ft.Container(
            content=self.pages["dashboard"].build(),
            expand=True,
            padding=SIZES["PADDING"]
        )
        
        # Create main layout
        main_layout = ft.Row([
            nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area
        ], expand=True, spacing=0)
        
        # Add to page
        self.page.add(main_layout)
        # No auto-load data - user must click "Cargar Red" button
        # self._schedule_page_load("dashboard")
    
    def _create_navigation_rail(self) -> ft.NavigationRail:
        """Create navigation rail."""
        icon_map = {
            "dashboard": ft.Icons.DASHBOARD,
            "language": ft.Icons.LANGUAGE,
            "account_tree": ft.Icons.ACCOUNT_TREE,
            "route": ft.Icons.ROUTE,
            "directions_run": ft.Icons.DIRECTIONS_RUN,
            "settings": ft.Icons.SETTINGS,
        }

        destinations = [
            ft.NavigationRailDestination(
                icon=icon_map.get(item["value"], ft.Icons.CIRCLE_OUTLINED),
                selected_icon=icon_map.get(item["value"], ft.Icons.CIRCLE),
                label=item["label"]
            )
            for item in NAV_ITEMS
        ]
        
        nav_rail = ft.NavigationRail(
            destinations=destinations,
            on_change=self._on_nav_change,
            width=200,
            bgcolor=COLORS["PRIMARY"],
            label_type=ft.NavigationRailLabelType.ALL,
            extended=True,
            selected_index=0
        )
        
        return nav_rail
    
    def _on_nav_change(self, e):
        """Handle navigation change."""
        selected_index = e.control.selected_index
        page_key = NAV_ITEMS[selected_index]["value"]
        self.switch_page(page_key)
    
    def switch_page(self, page_key: str):
        """Switch to a different page."""
        if page_key == self.current_page:
            return
        
        self.current_page = page_key
        
        # Update content area
        self.content_area.content = self.pages[page_key].build()
        self.page.update()
        self._schedule_page_load(page_key)

    def _schedule_page_load(self, page_key: str):
        """Schedule an async refresh for pages that expose load_data."""
        page_obj = self.pages.get(page_key)
        load_method = getattr(page_obj, "load_data", None)

        if not callable(load_method):
            return

        try:
            self.page.run_task(load_method)
        except AttributeError:
            asyncio.create_task(load_method())
        except RuntimeError:
            asyncio.create_task(load_method())
    
    def show_error(self, message: str):
        """Show error message."""
        dlg = ft.AlertDialog(
            title=ft.Text("Error"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(dlg))
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def show_success(self, message: str):
        """Show success message."""
        dlg = ft.AlertDialog(
            title=ft.Text("Éxito"),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=lambda e: self._close_dialog(dlg))
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()
    
    def _close_dialog(self, dlg: ft.AlertDialog):
        """Close dialog."""
        dlg.open = False
        self.page.update()
