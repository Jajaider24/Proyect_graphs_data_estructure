"""
Dashboard page - Main overview page with modern design.
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
        self.status_icon = None
        self.status_title = None
        self.status_info = None
        self.metric_values = {}
    
    def build(self) -> ft.Container:
        """Build dashboard UI with modern design."""
        return ft.Container(
            content=ft.Column([
                # Premium Header
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.FLIGHT, size=40, color=COLORS["PRIMARY"]),
                        ft.Column([
                            ft.Text(
                                "SkyRoute Planner",
                                size=32,
                                weight=ft.FontWeight.BOLD,
                                color=COLORS["PRIMARY"]
                            ),
                            ft.Text(
                                "Sistema de Planificación de Rutas Aéreas",
                                size=13,
                                color=COLORS["DARK"],
                                opacity=0.7
                            )
                        ], spacing=0),
                    ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=16,
                    bgcolor=COLORS["LIGHT"],
                    border_radius=8,
                    border=ft.border.Border(bottom=ft.border.BorderSide(3, COLORS["PRIMARY"]))
                ),
                
                ft.Divider(height=1, color=COLORS["BORDER"]),
                
                # Graph Status Card
                ft.Text("Estado de la Red", size=18, weight=ft.FontWeight.BOLD, color=COLORS["DARK"]),
                ft.Card(
                    content=ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    self._create_status_icon(),
                                    self._create_status_text()
                                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                                padding=16,
                                bgcolor=COLORS["LIGHT"],
                                border_radius=8
                            ),
                            ft.Column([
                                self._create_status_title(),
                                self._create_status_info()
                            ], spacing=4),
                            ft.Container(expand=True),
                            ft.ElevatedButton("Cargar Red", icon=ft.Icons.UPLOAD, on_click=self._on_load_network)
                        ], spacing=16, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=16
                    )
                ),
                
                # Metrics Section
                ft.Text("Métricas Principales", size=18, weight=ft.FontWeight.BOLD, color=COLORS["DARK"]),
                ft.Container(
                    content=ft.Row([
                        self._metric_card("Aeropuertos", "0", ft.Icons.LANGUAGE, COLORS["PRIMARY"]),
                        self._metric_card("Rutas", "0", ft.Icons.ROUTE, COLORS["SECONDARY"]),
                        self._metric_card("Hubs", "0", ft.Icons.HUB, COLORS["SUCCESS"]),
                        self._metric_card("Conectividad", "0%", ft.Icons.SHOW_CHART, COLORS["WARNING"]),
                    ], spacing=12, wrap=True, run_spacing=12),
                    margin=8
                ),
                
                # Quick Actions
                ft.Text("Acciones Rápidas", size=18, weight=ft.FontWeight.BOLD, color=COLORS["DARK"]),
                ft.Row([
                    self._action_button("Generar Itinerario", "Crea un plan personalizado", ft.Icons.ROUTE, self._on_generate_itinerary, COLORS["PRIMARY"]),
                    self._action_button("Ver Red", "Explora la red aérea", ft.Icons.LANGUAGE, self._on_show_statistics, COLORS["SECONDARY"]),
                    self._action_button("Ver Gráfico", "Visualiza las rutas", ft.Icons.ACCOUNT_TREE, self._on_show_graph, COLORS["SUCCESS"]),
                ], spacing=12, wrap=True, run_spacing=12)
                
            ], expand=True, spacing=12, scroll=ft.ScrollMode.AUTO),
            padding=16,
            expand=True
        )
    
    def _create_status_icon(self) -> ft.Icon:
        """Create status icon."""
        self.status_icon = ft.Icon(
            ft.Icons.CLOUD_OFF,
            size=36,
            color=COLORS["DANGER"]
        )
        return self.status_icon
    
    def _create_status_text(self) -> ft.Text:
        """Create status text."""
        self.status_text = ft.Text(
            "No cargada",
            size=14,
            weight=ft.FontWeight.W_500,
            color=COLORS["DANGER"]
        )
        return self.status_text
    
    def _create_status_title(self) -> ft.Text:
        """Create status title text."""
        self.status_title = ft.Text(
            "Red no cargada",
            size=14,
            weight=ft.FontWeight.BOLD,
            color=COLORS["DARK"]
        )
        return self.status_title
    
    def _create_status_info(self) -> ft.Text:
        """Create status info text."""
        self.status_info = ft.Text(
            "Haz clic en 'Cargar Red' para comenzar",
            size=12,
            color=COLORS["TEXT"],
            opacity=0.7
        )
        return self.status_info
    
    def _metric_card(self, title: str, value: str, icon, color: str) -> ft.Card:
        """Create a metric card."""
        value_text = ft.Text(value, size=28, weight=ft.FontWeight.BOLD, color=color)
        self.metric_values[title] = value_text
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(icon, size=32, color="#FFFFFF"),
                        bgcolor=color,
                        padding=12,
                        border_radius=8,
                        width=56,
                        height=56
                    ),
                    ft.Text(title, size=12, color=COLORS["DARK"], weight=ft.FontWeight.W_500),
                    value_text
                ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=16,
                width=200
            )
        )
    
    def _action_button(self, title: str, description: str, icon, on_click, color: str) -> ft.Container:
        """Create an action button card."""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, size=32, color="#FFFFFF"),
                    bgcolor=color,
                    padding=12,
                    border_radius=8,
                    width=56,
                    height=56
                ),
                ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=COLORS["DARK"], text_align=ft.TextAlign.CENTER),
                ft.Text(description, size=11, color=COLORS["TEXT"], text_align=ft.TextAlign.CENTER, max_lines=2)
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=on_click,
            padding=16,
            bgcolor=COLORS["LIGHT"],
            border_radius=8,
            width=200,
            ink=True
        )
    
    async def load_data(self):
        """Load dashboard data from the backend."""
        if not self.status_text:
            return

        try:
            status = await api_client.get_graph_status()
            
            if not status.get("loaded"):
                self.status_text.value = "No cargada"
                self.status_title.value = "Red no cargada"
                self.status_info.value = "Haz clic en 'Cargar Red' para comenzar"
                self.status_info.color = COLORS["TEXT"]
                self.status_icon.name = ft.Icons.CLOUD_OFF
                self.status_icon.color = COLORS["DANGER"]
                self.status_text.color = COLORS["DANGER"]
                self.status_title.color = COLORS["DARK"]
                
                self._set_metric("Aeropuertos", 0)
                self._set_metric("Rutas", 0)
                self._set_metric("Hubs", 0)
                self._set_metric("Conectividad", "0%")
                self.main_window.page.update()
                return

            stats = await api_client.get_network_statistics()
            graph_data = await api_client.get_graph_data()

            airports = graph_data.get("total_airports", 0) if graph_data else 0
            routes = graph_data.get("total_routes", 0) if graph_data else 0

            self.status_text.value = "✓ Cargada"
            self.status_title.value = "✓ Red cargada exitosamente"
            self.status_info.value = f"✈ Aeropuertos: {airports} | 🛫 Rutas: {routes}"
            self.status_info.color = COLORS["SUCCESS"]
            self.status_icon.name = ft.Icons.CLOUD_DONE
            self.status_icon.color = COLORS["SUCCESS"]
            self.status_text.color = COLORS["SUCCESS"]
            self.status_title.color = COLORS["SUCCESS"]

            hubs = stats.get("hub_airports", 0)
            connectivity = stats.get("average_connections", 0)
            
            self._set_metric("Aeropuertos", airports)
            self._set_metric("Rutas", routes)
            self._set_metric("Hubs", hubs)
            self._set_metric("Conectividad", f"{connectivity:.1f}%")
            
        except Exception as exc:
            self.status_text.value = "Error"
            self.status_title.value = "⚠ Error al cargar"
            self.status_info.value = "Verifica la conexión e intenta de nuevo"
            self.status_info.color = COLORS["DANGER"]
            self.status_icon.name = ft.Icons.ERROR
            self.status_icon.color = COLORS["DANGER"]
            self.status_text.color = COLORS["DANGER"]
            self.status_title.color = COLORS["DANGER"]
            
            self._set_metric("Aeropuertos", "—")
            self._set_metric("Rutas", "—")
            self._set_metric("Hubs", "—")
            self._set_metric("Conectividad", "—")

        self.main_window.page.update()

    def _set_metric(self, title: str, value):
        """Update metric value."""
        metric = self.metric_values.get(title)
        if metric:
            metric.value = str(value)
    
    def _on_load_network(self, e):
        """Handle load network button click."""
        self.main_window.page.run_task(self._on_load_network_async, e)
    
    async def _on_load_network_async(self, e):
        """Async implementation of load network."""
        try:
            result = await api_client.load_graph()
            await self.load_data()
            
            network_page = self.main_window.pages.get("network")
            if network_page and hasattr(network_page, "load_data"):
                await network_page.load_data()
            
            graph_page = self.main_window.pages.get("network_graph")
            if graph_page and hasattr(graph_page, "load_data"):
                try:
                    await graph_page.load_data()
                except Exception:
                    pass
            
            self.main_window.show_success(result.get("message", "Red cargada exitosamente"))
        except Exception as exc:
            self.main_window.show_error(f"Error: {exc}")
    
    def _on_generate_itinerary(self, e):
        """Handle generate itinerary button click."""
        self.main_window.switch_page("planning")
    
    def _on_show_statistics(self, e):
        """Handle show statistics button click."""
        self.main_window.switch_page("network")
    
    def _on_show_graph(self, e):
        """Handle show graph button click."""
        self.main_window.switch_page("network_graph")
    
    async def load_data(self):
        """Load dashboard data from the backend."""
        if not self.status_text:
            return

        try:
            status = await api_client.get_graph_status()
            
            if not status.get("loaded"):
                # Network not loaded
                self.status_text.value = "Red no cargada"
                self.status_icon.name = ft.Icons.CLOUD_OFF
                self.status_icon.color = COLORS["DANGER"]
                self.status_text.color = COLORS["DANGER"]
                
                self._set_metric("Total de Aeropuertos", 0)
                self._set_metric("Total de Rutas", 0)
                self._set_metric("Aeropuertos Hub", 0)
                self._set_metric("Conectividad Promedio", "0%")
                self.main_window.page.update()
                return

            # Network loaded - fetch additional data
            stats = await api_client.get_network_statistics()
            graph_data = await api_client.get_graph_data()

            # Update status to loaded
            self.status_text.value = "✓ Red cargada correctamente"
            self.status_icon.name = ft.Icons.CLOUD_DONE
            self.status_icon.color = COLORS["SUCCESS"]
            self.status_text.color = COLORS["SUCCESS"]

            # Extract metrics
            airports = graph_data.get("total_airports", 0) if graph_data else 0
            routes = graph_data.get("total_routes", 0) if graph_data else 0
            hubs = stats.get("hub_airports", 0)
            connectivity = stats.get("average_connections", 0)
            
            # Update metric cards
            self._set_metric("Total de Aeropuertos", airports)
            self._set_metric("Total de Rutas", routes)
            self._set_metric("Aeropuertos Hub", hubs)
            self._set_metric("Conectividad Promedio", f"{connectivity:.1f}%")
            
        except Exception as exc:
            # Error loading data
            self.status_text.value = "⚠ Error al cargar la red"
            self.status_icon.name = ft.Icons.ERROR
            self.status_icon.color = COLORS["DANGER"]
            self.status_text.color = COLORS["DANGER"]
            
            self._set_metric("Total de Aeropuertos", "—")
            self._set_metric("Total de Rutas", "—")
            self._set_metric("Aeropuertos Hub", "—")
            self._set_metric("Conectividad Promedio", "—")

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
            
            # Refresh other pages if they exist
            network_page = self.main_window.pages.get("network")
            if network_page and hasattr(network_page, "load_data"):
                await network_page.load_data()
            
            graph_page = self.main_window.pages.get("network_graph")
            if graph_page and hasattr(graph_page, "load_data"):
                try:
                    await graph_page.load_data()
                except Exception:
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
    
    def _on_show_graph(self, e):
        """Handle show graph button click."""
        self.main_window.switch_page("network_graph")
    
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
