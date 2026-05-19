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
        self.status_text = None
        self.metric_values = {}
    
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
            ft.Text(
                "Acciones rápidas",
                size=SIZES["FONT_SIZE_SUBTITLE"],
                weight=ft.FontWeight.BOLD
            ),

            ft.Row([
                self._create_action_tile(
                    "Cargar Red de Aeropuertos",
                    "Importa el archivo JSON y habilita el resto de vistas.",
                    ft.Icons.UPLOAD,
                    self._on_load_network
                ),
                self._create_action_tile(
                    "Generar Itinerario",
                    "Abre el formulario para calcular un plan de viaje.",
                    ft.Icons.ROUTE,
                    self._on_generate_itinerary
                ),
                self._create_action_tile(
                    "Estadísticas de Red",
                    "Muestra el panel con aeropuertos, rutas y hubs.",
                    ft.Icons.ANALYTICS,
                    self._on_show_statistics
                )
            ], spacing=SIZES["PADDING"], wrap=True),
            
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
        self.status_text = ft.Text("Estado: No cargado | Aeropuertos: 0 | Rutas: 0", size=SIZES["FONT_SIZE_BODY"])
        
        return ft.Card(
            content=ft.Container(
                content=self.status_text,
                padding=SIZES["PADDING"]
            )
        )
    
    def _create_info_card(self, title: str, value: str, icon: str) -> ft.Card:
        """Create info card."""
        value_text = ft.Text(value, size=SIZES["FONT_SIZE_SUBTITLE"], weight=ft.FontWeight.BOLD)
        self.metric_values[title] = value_text

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, size=SIZES["ICON_SIZE"], color=COLORS["PRIMARY"])
                    ]),
                    ft.Text(title, size=SIZES["FONT_SIZE_SMALL"], color=COLORS["TEXT"]),
                    value_text
                ], spacing=8),
                padding=SIZES["PADDING"],
                width=200
            )
        )

    def _create_action_tile(self, title: str, description: str, icon, on_click) -> ft.Container:
        """Create a self-explanatory action tile for the dashboard."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Button(
                        content=ft.Row(
                            [
                                ft.Icon(icon, size=18),
                                ft.Text(title)
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        on_click=on_click,
                        tooltip=description,
                    ),
                    ft.Text(
                        description,
                        size=SIZES["FONT_SIZE_SMALL"],
                        color=COLORS["TEXT"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
            width=240,
            margin=8,
        )
    
    async def load_data(self):
        """Load dashboard data from the backend."""
        if not self.status_text:
            return

        try:
            status = await api_client.get_graph_status()
            if not status.get("loaded"):
                self.status_text.value = "Estado: No cargado | Aeropuertos: 0 | Rutas: 0"
                self._set_metric("Total de Aeropuertos", 0)
                self._set_metric("Total de Rutas", 0)
                self._set_metric("Aeropuertos Hub", 0)
                self._set_metric("Conectividad Promedio", 0)
                self.main_window.page.update()
                return

            stats = await api_client.get_network_statistics()
            graph_data = await api_client.get_graph_data()

            self.status_text.value = (
                f"Estado: {'Cargado' if status.get('loaded') else 'No cargado'}"
                f" | Aeropuertos: {status.get('airports_count', 0)}"
                f" | Rutas: {status.get('routes_count', 0)}"
            )

            self._set_metric("Total de Aeropuertos", graph_data.get("total_airports", 0) if graph_data else 0)
            self._set_metric("Total de Rutas", graph_data.get("total_routes", 0) if graph_data else 0)
            self._set_metric("Aeropuertos Hub", stats.get("hub_airports", 0))
            self._set_metric("Conectividad Promedio", stats.get("average_connections", 0))
        except Exception as exc:
            self.status_text.value = f"No fue posible cargar el estado: {exc}"
            self._set_metric("Total de Aeropuertos", 0)
            self._set_metric("Total de Rutas", 0)
            self._set_metric("Aeropuertos Hub", 0)
            self._set_metric("Conectividad Promedio", 0)

        self.main_window.page.update()

    def _set_metric(self, title: str, value):
        """Update a dashboard metric value."""
        metric = self.metric_values.get(title)
        if metric:
            metric.value = str(value)
    
    def _on_load_network(self, e):
        """Handle load network button click (synchronous wrapper for Flet event)."""
        self.main_window.page.run_task(self._on_load_network_async, e)
    
    async def _on_load_network_async(self, e):
        """Async implementation of load network."""
        try:
            result = await api_client.load_graph()
            await self.load_data()
            network_page = self.main_window.pages.get("network")
            if network_page and hasattr(network_page, "load_data"):
                await network_page.load_data()
            # Also refresh graph visualization page if present
            graph_page = self.main_window.pages.get("network_graph")
            if graph_page and hasattr(graph_page, "load_data"):
                try:
                    await graph_page.load_data()
                except Exception:
                    # don't block success message if graph page fails
                    pass
            self.main_window.show_success(result.get("message", "Red de aeropuertos cargada exitosamente"))
        except Exception as exc:
            self.main_window.show_error(f"No se pudo cargar la red: {exc}")
    
    def _on_generate_itinerary(self, e):
        """Handle generate itinerary button click."""
        self.main_window.switch_page("planning")
    
    def _on_show_statistics(self, e):
        """Handle show statistics button click."""
        self.main_window.switch_page("network")
