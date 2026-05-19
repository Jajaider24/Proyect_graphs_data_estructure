"""
Network page - Airport network visualization and analysis.
"""

import asyncio
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
        self.search_field = None
        self.airports_table = None
        self.stat_total_airports = None
        self.stat_total_routes = None
        self.stat_hubs = None
        self.stat_density = None
    
    def build(self) -> ft.Column:
        """Build network page UI."""
        self.search_field = ft.TextField(
            label="Buscar aeropuerto...",
            expand=True,
            on_change=self._on_search_airport
        )

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
                self.search_field,
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    on_click=self._on_refresh_data
                )
            ], spacing=SIZES["PADDING"]),
            
            # Airports table
            self._create_airports_table()
        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)
    
    def _create_stat_card(self, title: str, value: str) -> ft.Card:
        """Create statistics card."""
        value_text = ft.Text(value, size=SIZES["FONT_SIZE_SUBTITLE"], weight=ft.FontWeight.BOLD, color=COLORS["PRIMARY"])
        if title == "Total Aeropuertos":
            self.stat_total_airports = value_text
        elif title == "Total Rutas":
            self.stat_total_routes = value_text
        elif title == "Aeropuertos Hub":
            self.stat_hubs = value_text
        elif title == "Densidad de Red":
            self.stat_density = value_text

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text(title, size=SIZES["FONT_SIZE_SMALL"], color=COLORS["TEXT"]),
                    value_text
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
            border=ft.border.Border(
                top=ft.border.BorderSide(1, COLORS["BORDER"]),
                right=ft.border.BorderSide(1, COLORS["BORDER"]),
                bottom=ft.border.BorderSide(1, COLORS["BORDER"]),
                left=ft.border.BorderSide(1, COLORS["BORDER"]),
            ),
            border_radius=SIZES["BORDER_RADIUS"],
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS
        )

    async def load_data(self):
        """Load network statistics and airport rows from the backend."""
        try:
            status = await api_client.get_graph_status()
            if not status.get("loaded"):
                self.airports_data = []
                self.routes_data = []
                self._set_stat(self.stat_total_airports, 0)
                self._set_stat(self.stat_total_routes, 0)
                self._set_stat(self.stat_hubs, 0)
                self._set_stat(self.stat_density, "0%")
                self._populate_airports_table([])
                self.main_window.page.update()
                return

            graph_data, stats = await asyncio.gather(
                api_client.get_graph_data(),
                api_client.get_network_statistics(),
            )
            self.airports_data = graph_data.get("airports", [])
            self.routes_data = graph_data.get("routes", [])

            self._set_stat(self.stat_total_airports, graph_data.get("total_airports", 0))
            self._set_stat(self.stat_total_routes, graph_data.get("total_routes", 0))
            self._set_stat(self.stat_hubs, stats.get("hub_airports", 0))
            self._set_stat(self.stat_density, f"{stats.get('network_density', 0)}")
            self._populate_airports_table(self.airports_data)
        except Exception as exc:
            self._set_stat(self.stat_total_airports, 0)
            self._set_stat(self.stat_total_routes, 0)
            self._set_stat(self.stat_hubs, 0)
            self._set_stat(self.stat_density, "0%")
            self._populate_airports_table([])
            self.main_window.show_error(f"No se pudo cargar la red: {exc}")

        self.main_window.page.update()

    def _set_stat(self, control, value):
        """Update a stat card value."""
        if control:
            control.value = str(value)

    def _populate_airports_table(self, airports):
        """Populate table rows using the provided airports list."""
        if not self.airports_table:
            return

        self.airports_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(airport.get("id", ""))),
                    ft.DataCell(ft.Text(airport.get("nombre", ""))),
                    ft.DataCell(ft.Text(airport.get("ciudad", ""))),
                    ft.DataCell(ft.Text(airport.get("pais", ""))),
                    ft.DataCell(
                        ft.Text(
                            str(
                                sum(
                                    1 for route in self.routes_data
                                    if route.get("origin_id") == airport.get("id")
                                )
                            )
                        )
                    ),
                    ft.DataCell(ft.Text("Sí" if airport.get("es_hub") else "No")),
                ]
            )
            for airport in airports
        ]

    def _filter_airports(self, query: str):
        """Filter airports by query and refresh the table."""
        if not query:
            filtered = self.airports_data
        else:
            lowered = query.lower()
            filtered = [
                airport for airport in self.airports_data
                if lowered in airport.get("id", "").lower()
                or lowered in airport.get("nombre", "").lower()
                or lowered in airport.get("ciudad", "").lower()
                or lowered in airport.get("pais", "").lower()
            ]

        self._populate_airports_table(filtered)
        self.main_window.page.update()
    
    def _on_search_airport(self, e):
        """Handle airport search."""
        self._filter_airports(e.control.value if e and e.control else "")
    
    def _on_refresh_data(self, e):
        """Handle refresh data button click (synchronous wrapper for Flet event)."""
        self.main_window.page.run_task(self._on_refresh_data_async, e)
    
    async def _on_refresh_data_async(self, e):
        """Async implementation of refresh data."""
        await self.load_data()
