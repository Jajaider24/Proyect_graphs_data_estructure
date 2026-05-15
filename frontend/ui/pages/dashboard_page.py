"""
Dashboard page - Main overview page.
"""

import flet as ft
from frontend.config import COLORS, SIZES
from frontend.services.api_client import api_client


class DashboardPage:
    """Dashboard page implementation."""
    
    def __init__(self, main_window):
        """Initialize dashboard page."""
        self.main_window = main_window
        self.loading = False
    
    def build(self) -> ft.Column:
        """Build dashboard UI."""
        return ft.Column([
            # Title
            ft.Row([
                ft.Text(
                    "SkyRoute Planner - Dashboard",
                    size=SIZES["FONT_SIZE_TITLE"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["PRIMARY"]
                )
            ], spacing=SIZES["PADDING"]),
            
            ft.Divider(),
            
            # Quick actions
            ft.Row([
                ft.Button(
                    content="Cargar Red de Aeropuertos",
                    icon="upload",
                    on_click=self._on_load_network
                ),
                ft.Button(
                    content="Generar Itinerario",
                    icon="route",
                    on_click=self._on_generate_itinerary
                ),
                ft.Button(
                    content="Estadísticas de Red",
                    icon="analytics",
                    on_click=self._on_show_statistics
                )
            ], spacing=SIZES["PADDING"]),
            
            ft.Divider(),
            
            # Status section
            ft.Text(
                "Estado de la Aplicación",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            self._create_status_card(),
            
            # Quick info
            ft.Text(
                "Información Rápida",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Row([
                self._create_info_card("Total de Aeropuertos", "0", "language"),
                self._create_info_card("Total de Rutas", "0", "route"),
                self._create_info_card("Aeropuertos Hub", "0", "hub"),
                self._create_info_card("Conectividad Promedio", "0", "signal_cellular_alt")
            ], spacing=SIZES["PADDING"], wrap=True)
        ], expand=True, spacing=SIZES["PADDING"])
    
    def _create_status_card(self) -> ft.Card:
        """Create status card."""
        self.status_text = ft.Text("Cargando estado...", size=SIZES["FONT_SIZE_BODY"])
        
        self._update_status()
        
        return ft.Card(
            content=ft.Container(
                content=self.status_text,
                padding=SIZES["PADDING"]
            )
        )
    
    def _create_info_card(self, title: str, value: str, icon: str) -> ft.Card:
        """Create info card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=SIZES["ICON_SIZE"], color=COLORS["PRIMARY"])
                    ]),
                    ft.Text(title, size=SIZES["FONT_SIZE_SMALL"], color=COLORS["TEXT"]),
                    ft.Text(value, size=SIZES["FONT_SIZE_SUBTITLE"], weight=ft.FontWeight.BOLD)
                ], spacing=8),
                padding=SIZES["PADDING"],
                width=200
            )
        )
    
    def _update_status(self):
        """Update status information."""
        # This will be called when the page is displayed
        pass
    
    def _on_load_network(self, e):
        """Handle load network button click."""
        self.main_window.show_success("Red de aeropuertos cargada exitosamente")
    
    def _on_generate_itinerary(self, e):
        """Handle generate itinerary button click."""
        self.main_window.switch_page("planning")
    
    def _on_show_statistics(self, e):
        """Handle show statistics button click."""
        self.main_window.switch_page("network")
