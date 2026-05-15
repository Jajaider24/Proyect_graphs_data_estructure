"""
Planning page - Travel itinerary generation.
"""

import flet as ft
from frontend.config import COLORS, SIZES
from frontend.services.api_client import api_client


class PlanningPage:
    """Planning page implementation."""
    
    def __init__(self, main_window):
        """Initialize planning page."""
        self.main_window = main_window
        self.itinerary_result = None
    
    def build(self) -> ft.Column:
        """Build planning page UI."""
        return ft.Column([
            # Title
            ft.Row([
                ft.Text(
                    "Generador de Itinerarios",
                    size=SIZES["FONT_SIZE_TITLE"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["PRIMARY"]
                )
            ]),
            
            ft.Divider(),
            
            # Input section
            ft.Text(
                "Parámetros de Viaje",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Row([
                # Origin airport
                ft.TextField(
                    label="Aeropuerto de Origen",
                    hint_text="Ej: MDE",
                    width=150,
                    ref=ft.Ref()
                ),
                
                # Budget
                ft.TextField(
                    label="Presupuesto (USD)",
                    hint_text="Ej: 5000",
                    input_filter=ft.NumbersOnlyInputFilter(),
                    width=150,
                    ref=ft.Ref()
                ),
                
                # Available time
                ft.TextField(
                    label="Tiempo Disponible (horas)",
                    hint_text="Ej: 48",
                    input_filter=ft.NumbersOnlyInputFilter(),
                    width=150,
                    ref=ft.Ref()
                ),
                
                # Aircraft type
                ft.Dropdown(
                    label="Tipo de Aeronave",
                    options=[
                        ft.dropdown.Option("Commercial"),
                        ft.dropdown.Option("Regional"),
                        ft.dropdown.Option("Helicopter")
                    ],
                    width=150,
                    value="Commercial",
                    ref=ft.Ref()
                )
            ], spacing=SIZES["PADDING"], wrap=True),
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                    text="Generar Itinerario",
                    icon="route",
                    on_click=self._on_generate_itinerary
                ),
                ft.TextButton(
                    text="Limpiar",
                    icon="clear",
                    on_click=self._on_clear_form
                )
            ], spacing=SIZES["PADDING"]),
            
            ft.Divider(),
            
            # Results section
            ft.Text(
                "Resultado del Itinerario",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            # Results container
            ft.Container(
                content=ft.Column([
                    ft.Text("Sin itinerario generado aún", size=SIZES["FONT_SIZE_BODY"]),
                ], expand=True),
                expand=True,
                border=ft.border.all(1, COLORS["BORDER"]),
                border_radius=SIZES["BORDER_RADIUS"],
                padding=SIZES["PADDING"],
                ref=ft.Ref()
            ),
            
            ft.Spacer()
        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _on_generate_itinerary(self, e):
        """Handle generate itinerary button click."""
        self.main_window.show_success("Itinerario generado exitosamente")
    
    def _on_clear_form(self, e):
        """Handle clear form button click."""
        pass
