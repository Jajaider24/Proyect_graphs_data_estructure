"""
Routes page - Route search and comparison.
"""

import flet as ft
from frontend.config import COLORS, SIZES
from frontend.services.api_client import api_client


class RoutesPage:
    """Routes page implementation."""
    
    def __init__(self, main_window):
        """Initialize routes page."""
        self.main_window = main_window
        self.routes_result = None
    
    def build(self) -> ft.Column:
        """Build routes page UI."""
        return ft.Column([
            # Title
            ft.Row([
                ft.Text(
                    "Búsqueda y Comparación de Rutas",
                    size=SIZES["FONT_SIZE_TITLE"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["PRIMARY"]
                )
            ]),
            
            ft.Divider(),
            
            # Search section
            ft.Text(
                "Parámetros de Búsqueda",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Row([
                # Start airport
                ft.TextField(
                    label="Aeropuerto de Salida",
                    hint_text="Ej: MDE",
                    width=150,
                    ref=ft.Ref()
                ),
                
                # End airport
                ft.TextField(
                    label="Aeropuerto de Destino",
                    hint_text="Ej: BOG",
                    width=150,
                    ref=ft.Ref()
                ),
                
                # Criterion
                ft.Dropdown(
                    label="Optimizar por",
                    options=[
                        ft.dropdown.Option("distance", "Distancia"),
                        ft.dropdown.Option("cost", "Costo"),
                        ft.dropdown.Option("time", "Tiempo")
                    ],
                    width=150,
                    value="distance",
                    ref=ft.Ref()
                )
            ], spacing=SIZES["PADDING"], wrap=True),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    text="Buscar Ruta",
                    icon="search",
                    on_click=self._on_search_route
                ),
                ft.ElevatedButton(
                    text="Comparar Rutas",
                    icon="compare_arrows",
                    on_click=self._on_compare_routes
                ),
                ft.TextButton(
                    text="Limpiar",
                    icon="clear",
                    on_click=self._on_clear_search
                )
            ], spacing=SIZES["PADDING"]),
            
            ft.Divider(),
            
            # Results section
            ft.Text(
                "Resultados",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            # Results container
            ft.Container(
                content=ft.Column([
                    ft.Text("Sin búsqueda realizada", size=SIZES["FONT_SIZE_BODY"]),
                ], expand=True),
                expand=True,
                border=ft.border.all(1, COLORS["BORDER"]),
                border_radius=SIZES["BORDER_RADIUS"],
                padding=SIZES["PADDING"],
                ref=ft.Ref()
            ),
            
            ft.Spacer()
        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _on_search_route(self, e):
        """Handle search route button click."""
        self.main_window.show_success("Ruta encontrada exitosamente")
    
    def _on_compare_routes(self, e):
        """Handle compare routes button click."""
        self.main_window.show_success("Rutas comparadas exitosamente")
    
    def _on_clear_search(self, e):
        """Handle clear search button click."""
        pass
