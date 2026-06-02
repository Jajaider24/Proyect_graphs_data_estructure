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
        self.start_field = None
        self.end_field = None
        self.criterion_field = None
        self.criteria_checks = {}
        self.transport_checks = {}
        self.include_secondary_switch = None
        self.results_column = None
    
    def build(self) -> ft.Column:
        """Build routes page UI."""
        self.start_field = ft.TextField(
            label="Aeropuerto de Salida",
            hint_text="Ej: MDE",
            width=150,
        )
        self.end_field = ft.TextField(
            label="Aeropuerto de Destino",
            hint_text="Ej: BOG",
            width=150,
        )
        self.criteria_checks = {
            "distance": ft.Checkbox(label="Distancia", value=True),
            "cost": ft.Checkbox(label="Costo", value=False),
            "time": ft.Checkbox(label="Tiempo", value=False),
        }
        self.transport_checks = {
            "Commercial": ft.Checkbox(label="Commercial", value=True),
            "Regional": ft.Checkbox(label="Regional", value=True),
            "Helice": ft.Checkbox(label="Helice", value=True),
        }
        self.include_secondary_switch = ft.Switch(
            label="Incluir aeropuertos secundarios",
            value=True,
        )

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
                self.start_field,
                
                # End airport
                self.end_field,
            ], spacing=SIZES["PADDING"], wrap=True),

            ft.Text("Criterios de optimización (elige uno o varios)", weight=ft.FontWeight.BOLD),
            ft.Row(list(self.criteria_checks.values()), spacing=SIZES["PADDING"], wrap=True),
            ft.Text("Tipos de transporte permitidos", weight=ft.FontWeight.BOLD),
            ft.Row(list(self.transport_checks.values()), spacing=SIZES["PADDING"], wrap=True),
            self.include_secondary_switch,
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                        content=ft.Text("Buscar Ruta"),
                    icon="search",
                    on_click=self._on_search_route
                ),
                ft.ElevatedButton(
                        content=ft.Text("Comparar Rutas"),
                    icon="compare_arrows",
                    on_click=self._on_compare_routes
                ),
                ft.TextButton(
                        content=ft.Text("Limpiar"),
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
                content=self._create_results_column(),
                expand=True,
                border=ft.border.Border(
                    top=ft.border.BorderSide(1, COLORS["BORDER"]),
                    right=ft.border.BorderSide(1, COLORS["BORDER"]),
                    bottom=ft.border.BorderSide(1, COLORS["BORDER"]),
                    left=ft.border.BorderSide(1, COLORS["BORDER"]),
                ),
                border_radius=SIZES["BORDER_RADIUS"],
                padding=SIZES["PADDING"],
            ),

        ], expand=True, spacing=SIZES["PADDING"], scroll=ft.ScrollMode.AUTO)

    def _create_results_column(self) -> ft.Column:
        """Create the results column and keep a reference for updates."""
        self.results_column = ft.Column([
            ft.Text("Sin búsqueda realizada", size=SIZES["FONT_SIZE_BODY"]),
        ], expand=True, spacing=12)
        return self.results_column

    def _set_results(self, controls):
        """Replace the routes results content."""
        if self.results_column is None:
            return

        self.results_column.controls = controls
        self.main_window.page.update()

    def _build_shortest_path_view(self, result: dict):
        """Build the shortest path result cards."""
        results_by_criterion = result.get("results_by_criterion", {}) or {}
        if not results_by_criterion and result.get("criterion"):
            results_by_criterion = {result.get("criterion"): result}

        controls = [
            ft.Text("Ruta más corta", weight=ft.FontWeight.BOLD),
        ]

        if not results_by_criterion:
            controls.append(ft.Text("Sin ruta disponible"))
            return controls

        for criterion, payload in results_by_criterion.items():
            path = payload.get("path", []) or []
            controls.append(ft.Text(f"Criterio: {criterion}", weight=ft.FontWeight.BOLD, color=COLORS["PRIMARY"]))
            controls.append(ft.Text(f"Ruta: {' → '.join(path) if path else 'Sin ruta disponible'}"))
            controls.append(ft.Text(f"Distancia total: {payload.get('total_distance', 0)} km"))
            controls.append(ft.Text(f"Tiempo total: {payload.get('total_time', 0)} min"))
            controls.append(ft.Text(f"Costo total: {payload.get('total_cost', 0)} USD"))

            segments = payload.get("segments", []) or []
            if segments:
                controls.append(ft.Text("Segmentos", weight=ft.FontWeight.BOLD))
                for segment in segments:
                    controls.append(
                        ft.Text(
                            f"{segment.get('origin')} → {segment.get('destination')} | "
                            f"{segment.get('distance', 0)} km | {segment.get('time', 0)} min | "
                            f"{segment.get('cost', 0)} USD | {segment.get('aircraft_type', '')}"
                        )
                    )

            controls.append(ft.Divider())

        return controls

    def _build_compare_view(self, result: dict):
        """Build comparison results for all criteria."""
        controls = [ft.Text("Comparación de rutas", weight=ft.FontWeight.BOLD)]

        for criterion, payload in result.items():
            if isinstance(payload, dict) and payload.get("error"):
                controls.append(ft.Text(f"{criterion.title()}: {payload['error']}"))
                continue

            path = payload.get("path", []) if isinstance(payload, dict) else []

            # ----------------------------------------
            # Visualizar primera ruta encontrada
            # ----------------------------------------

            if path:
                    try:
                        graph_page = self.main_window.pages["network_graph"]

                        graph_page.visualize_path(path)

                        self.main_window.current_page = "network_graph"
                        self.main_window.refresh_content()
                        
                    except Exception as exc:
                        print(f"Graph visualization error: {exc}")

            controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(criterion.title(), weight=ft.FontWeight.BOLD),
                            ft.Text(f"Ruta: {' → '.join(path) if path else 'Sin ruta disponible'}"),
                            ft.Text(f"Valor total: {payload.get('total_value') if isinstance(payload, dict) else ''}"),
                            ft.Text(f"Distancia total: {payload.get('total_distance') if isinstance(payload, dict) else ''}"),
                            ft.Text(f"Tiempo total: {payload.get('total_time') if isinstance(payload, dict) else ''}"),
                            ft.Text(f"Costo total: {payload.get('total_cost') if isinstance(payload, dict) else ''}"),
                        ], spacing=4),
                        padding=SIZES["PADDING"]
                    )
                )
            )

        return controls
    
    def _on_search_route(self, e):
        """Handle search route button click (synchronous wrapper for Flet event)."""
        self.main_window.page.run_task(self._on_search_route_async, e)

    def _selected_criteria(self):
        values = [key for key, checkbox in self.criteria_checks.items() if checkbox.value]
        return values

    def _selected_transports(self):
        values = [key for key, checkbox in self.transport_checks.items() if checkbox.value]
        return values
    
    async def _on_search_route_async(self, e):
        """Async implementation of search route."""
        try:
            start = (self.start_field.value or "").strip().upper()
            end = (self.end_field.value or "").strip().upper()
            criteria = self._selected_criteria()
            transports = self._selected_transports()
            include_secondary_airports = bool(self.include_secondary_switch.value)

            if not start or not end:
                raise ValueError("Ingresa aeropuertos de salida y destino.")
            if not criteria:
                raise ValueError("Selecciona al menos un criterio de optimización.")
            if not transports:
                raise ValueError("Selecciona al menos un tipo de transporte.")

            result = await api_client.calculate_shortest_path(
                start=start,
                end=end,
                criterion=criteria[0],
                criteria=criteria,
                include_secondary_airports=include_secondary_airports,
                transport_types=transports,
            )
            self.routes_result = result
            self._set_results(self._build_shortest_path_view(result))
            self.main_window.show_success("Ruta encontrada exitosamente")
        except ValueError as exc:
            self.main_window.show_error(str(exc))
        except Exception as exc:
            self.main_window.show_error(f"No se pudo buscar la ruta: {exc}")
    
    def _on_compare_routes(self, e):
        """Handle compare routes button click (synchronous wrapper for Flet event)."""
        self.main_window.page.run_task(self._on_compare_routes_async, e)
    
    async def _on_compare_routes_async(self, e):
        """Async implementation of compare routes."""
        try:
            start = (self.start_field.value or "").strip().upper()
            end = (self.end_field.value or "").strip().upper()
            criteria = self._selected_criteria()
            transports = self._selected_transports()
            include_secondary_airports = bool(self.include_secondary_switch.value)

            if not start or not end:
                raise ValueError("Ingresa aeropuertos de salida y destino.")
            if not criteria:
                raise ValueError("Selecciona al menos un criterio de optimización.")
            if not transports:
                raise ValueError("Selecciona al menos un tipo de transporte.")

            result = await api_client.compare_routes(
                start=start,
                end=end,
                criteria=criteria,
                include_secondary_airports=include_secondary_airports,
                transport_types=transports,
            )
            self.routes_result = result
            self._set_results(self._build_compare_view(result))
            self.main_window.show_success("Rutas comparadas exitosamente")
        except ValueError as exc:
            self.main_window.show_error(str(exc))
        except Exception as exc:
            self.main_window.show_error(f"No se pudieron comparar las rutas: {exc}")
    
    def _on_clear_search(self, e):
        """Handle clear search button click."""
        if self.start_field:
            self.start_field.value = ""
        if self.end_field:
            self.end_field.value = ""
        for key, checkbox in self.criteria_checks.items():
            checkbox.value = key == "distance"
        for checkbox in self.transport_checks.values():
            checkbox.value = True
        if self.include_secondary_switch:
            self.include_secondary_switch.value = True

        self.routes_result = None
        self._set_results([ft.Text("Sin búsqueda realizada", size=SIZES["FONT_SIZE_BODY"])])
