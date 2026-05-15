"""
Network page - Airport network visualization and analysis.
"""

import flet as ft
from frontend.config import COLORS, SIZES
from frontend.services.api_client import api_client


class NetworkPage:
    """Network page implementation."""
    
    def __init__(self, main_window):
        """Initialize network page."""
        self.main_window = main_window
        self.airports_data = []
        self.routes_data = []
    
    def build(self) -> ft.Column:
        """Build network page UI."""
        return ft.Column([
            # Title
            ft.Row([
                ft.Text(
                    "Red de Aeropuertos",
                    size=SIZES["FONT_SIZE_TITLE"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["PRIMARY"]
                )
            ]),
            
            ft.Divider(),
            
            # Statistics section
            ft.Text(
                "Estadísticas de la Red",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Row([
                self._create_stat_card("Total Aeropuertos", "0"),
                self._create_stat_card("Total Rutas", "0"),
                self._create_stat_card("Aeropuertos Hub", "0"),
                self._create_stat_card("Densidad de Red", "0%")
            ], spacing=SIZES["PADDING"], wrap=True),
            
            ft.Divider(),
            
            # Airports list
            ft.Text(
                "Aeropuertos",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Row([
                ft.TextField(
                    label="Buscar aeropuerto...",
                    expand=True,
                    on_change=self._on_search_airport
                ),
                ft.IconButton(
                    icon="refresh",
                    on_click=self._on_refresh_data
                )
            ], spacing=SIZES["PADDING"]),
            
            # Airports table
            self._create_airports_table(),
            
            ft.Spacer()
        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _create_stat_card(self, title: str, value: str) -> ft.Card:
        """Create statistics card."""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=SIZES["FONT_SIZE_SMALL"], color=COLORS["TEXT"]),
                    ft.Text(value, size=SIZES["FONT_SIZE_SUBTITLE"], weight=ft.FontWeight.BOLD, color=COLORS["PRIMARY"])
                ], spacing=8),
                padding=SIZES["PADDING"],
                width=150
            )
        )
    
    def _create_airports_table(self) -> ft.Container:
        """Create airports table."""
        self.airports_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("IATA")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Ciudad")),
                ft.DataColumn(ft.Text("País")),
                ft.DataColumn(ft.Text("Conexiones")),
                ft.DataColumn(ft.Text("Hub"))
            ],
            rows=[],
            expand=True
        )
        
        return ft.Container(
            content=self.airports_table,
            expand=True,
            border=ft.border.all(1, COLORS["BORDER"]),
            border_radius=SIZES["BORDER_RADIUS"],
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
        )
    
    def _on_search_airport(self, e):
        """Handle airport search."""
        pass
    
    def _on_refresh_data(self, e):
        """Handle refresh data button click."""
        pass
