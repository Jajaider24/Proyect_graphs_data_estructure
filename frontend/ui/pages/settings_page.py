"""
Settings page - Application configuration.
"""

import asyncio
import flet as ft
from frontend.config import COLORS, SIZES, API_CONFIG
from frontend.services.api_client import api_client


class SettingsPage:
    """Settings page implementation."""
    
    def __init__(self, main_window):
        """Initialize settings page."""
        self.main_window = main_window
        self.base_url_field = None
        self.timeout_field = None
        self.dark_mode_checkbox = None
        self.debug_mode_checkbox = None
        self.auto_load_checkbox = None
    
    def build(self) -> ft.Column:
        """Build settings page UI."""
        self.base_url_field = ft.TextField(
            value=API_CONFIG["BASE_URL"],
            read_only=False,
            expand=True
        )
        self.timeout_field = ft.TextField(
            value=str(API_CONFIG["TIMEOUT"]),
            input_filter=ft.NumbersOnlyInputFilter(),
            width=100
        )
        self.dark_mode_checkbox = ft.Checkbox(
            label="Modo Oscuro",
            value=False,
            on_change=self._on_toggle_dark_mode
        )
        self.debug_mode_checkbox = ft.Checkbox(
            label="Modo Depuración",
            value=False,
            on_change=self._on_toggle_debug_mode
        )
        self.auto_load_checkbox = ft.Checkbox(
            label="Carga Automática de Red",
            value=True,
            on_change=self._on_toggle_auto_load
        )

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
                            self.base_url_field
                        ], spacing=SIZES["PADDING"]),
                        
                        ft.Row([
                            ft.Text("Timeout (segundos):", width=200),
                            self.timeout_field
                        ], spacing=SIZES["PADDING"]),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                    content=ft.Text("Probar Conexión"),
                                icon="check",
                                on_click=self._on_test_connection
                            ),
                            ft.TextButton(
                                    content=ft.Text("Restablecer"),
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
                            self.dark_mode_checkbox
                        ]),
                        
                        ft.Row([
                            self.debug_mode_checkbox
                        ]),
                        
                        ft.Row([
                            self.auto_load_checkbox
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
                        ft.Row([
                            ft.Icon(ft.Icons.FLIGHT, size=32, color=COLORS["PRIMARY"])
                        ]),
                        ft.Text("SkyRoute Planner", size=SIZES["FONT_SIZE_TITLE"], weight=ft.FontWeight.BOLD, color=COLORS["PRIMARY"]),
                        ft.Text("v1.0.0", size=SIZES["FONT_SIZE_SMALL"], color=COLORS["SECONDARY"]),
                        ft.Divider(),
                        ft.Text("Sistema de Planificación de Rutas Aéreas con Grafos", size=SIZES["FONT_SIZE_BODY"], weight=ft.FontWeight.BOLD),
                        ft.Text(""),
                        ft.Text("Desarrollado por:", weight=ft.FontWeight.BOLD),
                        ft.Text("• Jaider León", size=SIZES["FONT_SIZE_BODY"]),
                        ft.Text("• Michael Ramirez", size=SIZES["FONT_SIZE_BODY"]),
                        ft.Text("• Jhoan Sebastian Velez", size=SIZES["FONT_SIZE_BODY"]),
                        ft.Text(""),
                        ft.Text("© 2026 - Proyecto de Estructuras de Datos", size=SIZES["FONT_SIZE_SMALL"], color=COLORS["DARK"], weight=ft.FontWeight.BOLD),
                        ft.Text(""),
                        ft.Text("Utiliza tecnologías modernas:", weight=ft.FontWeight.BOLD),
                        ft.Text("• Backend: FastAPI + Python", size=SIZES["FONT_SIZE_SMALL"]),
                        ft.Text("• Frontend: Flet (UI multiplataforma)", size=SIZES["FONT_SIZE_SMALL"]),
                        ft.Text("• Algoritmos: Dijkstra, DFS, Grafos", size=SIZES["FONT_SIZE_SMALL"]),
                        ft.Text(""),
                        ft.Row([
                            ft.TextButton("GitHub", on_click=self._on_github, icon=ft.Icons.CODE),
                            ft.TextButton("Documentación", on_click=self._on_documentation, icon=ft.Icons.HELP),
                            ft.TextButton("Contacto", on_click=self._on_contact, icon=ft.Icons.EMAIL)
                        ], spacing=SIZES["PADDING"])
                    ], spacing=8),
                    padding=SIZES["PADDING"]
                )
            ),

        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _on_test_connection(self, e):
        """Handle test connection button click."""
        try:
            self.main_window.page.run_task(self._test_connection)
        except (AttributeError, RuntimeError):
            asyncio.create_task(self._test_connection())
    
    def _on_reset_settings(self, e):
        """Handle reset settings button click."""
        if self.base_url_field:
            self.base_url_field.value = API_CONFIG["BASE_URL"]
        if self.timeout_field:
            self.timeout_field.value = str(API_CONFIG["TIMEOUT"])
        if self.dark_mode_checkbox:
            self.dark_mode_checkbox.value = False
        if self.debug_mode_checkbox:
            self.debug_mode_checkbox.value = False
        if self.auto_load_checkbox:
            self.auto_load_checkbox.value = True

        self.main_window.page.update()
        self.main_window.show_success("Configuración restablecida")

    async def _test_connection(self):
        """Validate API connectivity using a lightweight endpoint."""
        try:
            status = await api_client.get_graph_status()
            self.main_window.show_success(
                f"Conexión exitosa. Estado de red: {'cargada' if status.get('loaded') else 'no cargada'}"
            )
        except Exception as exc:
            self.main_window.show_error(f"No se pudo conectar con la API: {exc}")
    
    def _on_toggle_dark_mode(self, e):
        """Handle dark mode toggle."""
        self.main_window.page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
        self.main_window.page.update()
    
    def _on_toggle_debug_mode(self, e):
        """Handle debug mode toggle."""
        self.main_window.show_success(f"Modo depuración {'activado' if e.control.value else 'desactivado'}")
    
    def _on_toggle_auto_load(self, e):
        """Handle auto-load toggle."""
        self.main_window.show_success(f"Carga automática {'activada' if e.control.value else 'desactivada'}")
    
    def _on_github(self, e):
        """Handle GitHub button click."""
        self._open_external_url("https://github.com/JaiderLeon/SkyRoute-Planner")
    
    def _on_documentation(self, e):
        """Handle documentation button click."""
        self._open_external_url("https://github.com/JaiderLeon/SkyRoute-Planner/wiki")
    
    def _on_contact(self, e):
        """Handle contact button click."""
        self._open_external_url("mailto:info@skyroute.local")

    def _open_external_url(self, url: str):
        """Open an external URL using the page launcher if available."""
        launcher = getattr(self.main_window.page, "launch_url", None) or getattr(self.main_window.page, "open_url", None)
        if callable(launcher):
            launcher(url)
        else:
            self.main_window.show_error(f"No se pudo abrir el enlace: {url}")
