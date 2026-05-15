"""
Settings page - Application configuration.
"""

import flet as ft
from frontend.config import COLORS, SIZES, API_CONFIG


class SettingsPage:
    """Settings page implementation."""
    
    def __init__(self, main_window):
        """Initialize settings page."""
        self.main_window = main_window
    
    def build(self) -> ft.Column:
        """Build settings page UI."""
        return ft.Column([
            # Title
            ft.Row([
                ft.Text(
                    "Configuración",
                    size=SIZES["FONT_SIZE_TITLE"],
                    weight=ft.FontWeight.BOLD,
                    color=COLORS["PRIMARY"]
                )
            ]),
            
            ft.Divider(),
            
            # Server settings
            ft.Text(
                "Configuración del Servidor",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("URL Base de API:", width=200),
                            ft.TextField(
                                value=API_CONFIG["BASE_URL"],
                                read_only=False,
                                expand=True
                            )
                        ], spacing=SIZES["PADDING"]),
                        
                        ft.Row([
                            ft.Text("Timeout (segundos):", width=200),
                            ft.TextField(
                                value=str(API_CONFIG["TIMEOUT"]),
                                input_filter=ft.NumbersOnlyInputFilter(),
                                width=100
                            )
                        ], spacing=SIZES["PADDING"]),
                        
                        ft.Row([
                            ft.Button(
                                content="Probar Conexión",
                                icon="check",
                                on_click=self._on_test_connection
                            ),
                            ft.TextButton(
                                content="Restablecer",
                                icon="refresh",
                                on_click=self._on_reset_settings
                            )
                        ], spacing=SIZES["PADDING"])
                    ], spacing=SIZES["PADDING"]),
                    padding=SIZES["PADDING"]
                )
            ),
            
            ft.Divider(),
            
            # App settings
            ft.Text(
                "Configuración de la Aplicación",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Checkbox(
                                label="Modo Oscuro",
                                value=False,
                                on_change=self._on_toggle_dark_mode
                            )
                        ]),
                        
                        ft.Row([
                            ft.Checkbox(
                                label="Modo Depuración",
                                value=False,
                                on_change=self._on_toggle_debug_mode
                            )
                        ]),
                        
                        ft.Row([
                            ft.Checkbox(
                                label="Carga Automática de Red",
                                value=True,
                                on_change=self._on_toggle_auto_load
                            )
                        ])
                    ], spacing=SIZES["PADDING"]),
                    padding=SIZES["PADDING"]
                )
            ),
            
            ft.Divider(),
            
            # About section
            ft.Text(
                "Acerca de",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("SkyRoute Planner v1.0.0", weight=ft.FontWeight.BOLD),
                        ft.Text("Sistema de Planificación de Rutas Aéreas", size=SIZES["FONT_SIZE_SMALL"]),
                        ft.Text("© 2024 - Proyecto de Estructuras de Datos", size=SIZES["FONT_SIZE_SMALL"]),
                        ft.Text(""),
                        ft.Row([
                            ft.TextButton("GitHub", on_click=self._on_github),
                            ft.TextButton("Documentación", on_click=self._on_documentation),
                            ft.TextButton("Contacto", on_click=self._on_contact)
                        ])
                    ], spacing=SIZES["PADDING"]),
                    padding=SIZES["PADDING"]
                )
            ),

        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _on_test_connection(self, e):
        """Handle test connection button click."""
        self.main_window.show_success("Conexión exitosa con el servidor")
    
    def _on_reset_settings(self, e):
        """Handle reset settings button click."""
        self.main_window.show_success("Configuración restablecida")
    
    def _on_toggle_dark_mode(self, e):
        """Handle dark mode toggle."""
        pass
    
    def _on_toggle_debug_mode(self, e):
        """Handle debug mode toggle."""
        pass
    
    def _on_toggle_auto_load(self, e):
        """Handle auto-load toggle."""
        pass
    
    def _on_github(self, e):
        """Handle GitHub button click."""
        pass
    
    def _on_documentation(self, e):
        """Handle documentation button click."""
        pass
    
    def _on_contact(self, e):
        """Handle contact button click."""
        pass
