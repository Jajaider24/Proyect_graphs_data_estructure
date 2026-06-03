"""
Planning page - Travel itinerary generation.
"""

import asyncio
import math

import flet as ft
from frontend.config import COLORS, SIZES
from frontend.services.api_client import api_client


class PlanningPage:
    """Planning page implementation."""
    
    def __init__(self, main_window):
        """Initialize planning page."""
        self.main_window = main_window
        self.itinerary_result = None
        self.origin_field = None
        self.budget_field = None
        self.time_field = None
        self.aircraft_field = None
        self.transport_checks = {}
        self.include_secondary_switch = None
        self.results_column = None
        self.advance_timer_text = None
        self.session_id = None
        self.session_options_box = None
        self.stay_minutes_field = None
        self.transit_monitor_running = False
        self.transit_monitor_cancelled = False
        self.transit_monitor_base = None
        # Preview monitor (client-side pre-flight preview)
        self.preview_monitor_running = False
        self.preview_monitor_cancelled = False
        self.interrupt_origin_field = None
        self.interrupt_destination_field = None
    
    def build(self) -> ft.Column:
        """Build planning page UI."""
        self.origin_field = ft.TextField(
            label="Aeropuerto de Origen",
            hint_text="Ej: MDE",
            width=150,
        )
        self.budget_field = ft.TextField(
            label="Presupuesto (USD)",
            hint_text="Ej: 5000",
            input_filter=ft.NumbersOnlyInputFilter(),
            width=150,
        )
        self.time_field = ft.TextField(
            label="Tiempo Disponible (horas)",
            hint_text="Ej: 48",
            input_filter=ft.NumbersOnlyInputFilter(),
            width=150,
        )
        self.transport_checks = {
            "Commercial": ft.Checkbox(label="Commercial", value=True),
            "Regional": ft.Checkbox(label="Regional", value=True),
            "Helice": ft.Checkbox(label="Helice", value=True),
        }
        self.include_secondary_switch = ft.Switch(
            label="Incluir aeropuertos secundarios",
            value=True,
        )
        self.stay_minutes_field = ft.TextField(
            label="Tiempo libre stay (min)",
            hint_text="Ej: 30",
            input_filter=ft.NumbersOnlyInputFilter(),
            width=160,
            value="0",
        )
        self.interrupt_origin_field = ft.TextField(
            label="Interrumpir origen",
            hint_text="Ej: MDE",
            width=150,
        )
        self.interrupt_destination_field = ft.TextField(
            label="Interrumpir destino",
            hint_text="Ej: BOG",
            width=150,
        )

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
                self.origin_field,
                
                # Budget
                self.budget_field,
                
                # Available time
                self.time_field,
            ], spacing=SIZES["PADDING"], wrap=True),

            ft.Text("Transportes preferidos (elige al menos uno)", weight=ft.FontWeight.BOLD),
            ft.Row(list(self.transport_checks.values()), spacing=SIZES["PADDING"], wrap=True),
            self.include_secondary_switch,
            
            # Action buttons
            ft.Row([
                ft.ElevatedButton(
                        content=ft.Text("Generar Itinerario"),
                    icon="play_arrow",
                    on_click=self._on_generate_itinerary
                ),
                ft.ElevatedButton(
                        content=ft.Text("Iniciar sesión interactiva"),
                    icon="play_arrow", on_click=self._on_start_session
                ),
                ft.TextButton(
                        content=ft.Text("Limpiar"),
                    icon="clear",
                    on_click=self._on_clear_form
                )
            ], spacing=SIZES["PADDING"]),
            ft.Row([
                self.stay_minutes_field,
                ft.ElevatedButton(
                    content=ft.Text("Aplicar stay"),
                    icon="hotel",
                    on_click=self._on_apply_stay,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Actualizar opciones"),
                    icon="refresh",
                    on_click=self._on_fetch_options,
                ),
            ], spacing=SIZES["PADDING"], wrap=True),
            ft.Row([
                self.interrupt_origin_field,
                self.interrupt_destination_field,
                ft.ElevatedButton(
                    content=ft.Text("Interrumpir ruta"),
                    icon="warning",
                    on_click=self._on_interrupt_route,
                ),
                ft.ElevatedButton(
                    content=ft.Text("Generar reporte final"),
                    icon="description",
                    on_click=self._on_get_report,
                ),
            ], spacing=SIZES["PADDING"], wrap=True),
            
            ft.Divider(),
            
            # Results section
            ft.Text(
                "Resultado del Itinerario",
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
        self.advance_timer_text = ft.Text(
            "Temporizador listo",
            size=SIZES["FONT_SIZE_SMALL"],
            color=COLORS["PRIMARY"],
        )
        self.results_column = ft.Column([
            self.advance_timer_text,
            ft.Text("Sin itinerario generado aún", size=SIZES["FONT_SIZE_BODY"]),
        ], expand=True, spacing=12)
        self.session_options_box = ft.Column([], spacing=8)
        return self.results_column

    def _set_results(self, controls):
        """Replace the itinerary results content."""
        if self.results_column is None:
            return

        prefix = [self.advance_timer_text] if self.advance_timer_text else []
        self.results_column.controls = prefix + controls
        self.main_window.page.update()

    def _build_itinerary_view(self, itinerary: dict):
        """Build a visual representation of the itinerary response."""
        alternatives = itinerary.get("alternatives", {}) or {}
        required_transports = itinerary.get("required_transport_types", []) or []

        controls = [
            ft.Text(f"Origen: {itinerary.get('origin', '')}", weight=ft.FontWeight.BOLD),
            ft.Text(f"Transportes requeridos: {', '.join(required_transports) if required_transports else 'N/A'}"),
            ft.Divider(),
        ]

        if not alternatives:
            controls.append(ft.Text("No se encontraron alternativas para este itinerario."))
            return controls

        labels = {
            "max_destinations_budget": "Alternativa A · Máximos destinos sin exceder presupuesto",
            "max_destinations_time": "Alternativa B · Máximos destinos en menor tiempo",
        }

        for key, payload in alternatives.items():
            flights = payload.get("flights", []) or []
            controls.append(ft.Text(labels.get(key, key), weight=ft.FontWeight.BOLD, color=COLORS["PRIMARY"]))
            controls.append(ft.Text(f"Destinos visitados: {payload.get('total_destinations', 0)}"))
            controls.append(ft.Text(f"Secuencia: {' → '.join(payload.get('visited_airports', []))}"))
            controls.append(ft.Text(f"Costo total: {payload.get('total_cost', 0)} USD"))
            controls.append(ft.Text(f"Tiempo total: {payload.get('total_time', 0)} min"))
            controls.append(ft.Text(f"Distancia total: {payload.get('total_distance', 0)} km"))
            controls.append(ft.Text(f"Transportes usados: {', '.join(payload.get('used_transport_types', []))}"))
            controls.append(
                ft.Text(
                    f"Cumple uso de todos los transportes: {'Sí' if payload.get('transport_requirement_met') else 'No'}"
                )
            )

            if not flights:
                controls.append(ft.Text("No se encontraron segmentos para esta alternativa."))
                controls.append(ft.Divider())
                continue

            for flight in flights:
                controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text(
                                    f"{flight.get('origin')} → {flight.get('destination')}",
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(f"Distancia: {flight.get('distance', 0)} km"),
                                ft.Text(f"Tiempo tramo: {flight.get('time', 0)} min"),
                                ft.Text(f"Costo tramo: {flight.get('cost', 0)} USD"),
                                ft.Text(f"Costo acumulado: {flight.get('cumulative_cost', 0)} USD"),
                                ft.Text(f"Tiempo acumulado: {flight.get('cumulative_time', 0)} min"),
                                ft.Text(f"Aeronave: {flight.get('aircraft_type', '')}"),
                            ], spacing=4),
                            padding=SIZES["PADDING"]
                        )
                    )
                )

            controls.append(ft.Divider())

        return controls

    def _selected_transports(self):
        values = []
        for transport_name, checkbox in self.transport_checks.items():
            if checkbox and checkbox.value:
                values.append(transport_name)
        return values

    async def _on_generate_itinerary_async(self, e):
        """Async implementation of generate itinerary."""
        try:
            origin = (self.origin_field.value or "").strip().upper()
            budget = float(self.budget_field.value)
            available_time_hours = float(self.time_field.value)
            preferred_transports = self._selected_transports()
            include_secondary_airports = bool(self.include_secondary_switch.value)

            if not origin:
                raise ValueError("Ingresa un aeropuerto de origen.")

            if not preferred_transports:
                raise ValueError("Debes seleccionar al menos un tipo de transporte.")

            itinerary = await api_client.generate_itinerary(
                origin=origin,
                budget=budget,
                available_time=available_time_hours,
                preferred_transports=preferred_transports,
                include_secondary_airports=include_secondary_airports,
            )

            self.itinerary_result = itinerary
            self._set_results(self._build_itinerary_view(itinerary))
            self.main_window.show_success("Itinerario generado exitosamente")
        except ValueError as exc:
            self.main_window.show_error(str(exc))
        except Exception as exc:
            self.main_window.show_error(f"No se pudo generar el itinerario: {exc}")

    def _on_clear_form(self, e):
        """Handle clear form button click."""
        if self.origin_field:
            self.origin_field.value = ""
        if self.budget_field:
            self.budget_field.value = ""
        if self.time_field:
            self.time_field.value = ""
        for checkbox in self.transport_checks.values():
            checkbox.value = True
        if self.include_secondary_switch:
            self.include_secondary_switch.value = True
        if self.stay_minutes_field:
            self.stay_minutes_field.value = "0"
        self._cancel_advance_timer()
        if self.interrupt_origin_field:
            self.interrupt_origin_field.value = ""
        if self.interrupt_destination_field:
            self.interrupt_destination_field.value = ""

        self.itinerary_result = None
        self._set_results([ft.Text("Sin itinerario generado aún", size=SIZES["FONT_SIZE_BODY"])])

    def _set_advance_timer_status(self, message: str):
        """Keep the timer feedback internal while the transit is active."""
        if self.advance_timer_text is not None:
            self.advance_timer_text.value = message
        self.main_window.page.update()

    def _cancel_advance_timer(self):
        """Cancel any active advance timer."""
        self.advance_timer_cancelled = True
        self.advance_timer_running = False
        self.transit_monitor_cancelled = True
        self.transit_monitor_running = False
        self.transit_monitor_base = None
        self._set_advance_timer_status("Temporizador cancelado")

    def _format_transit_preview(self, transit: dict, elapsed_seconds: float) -> dict:
        """Build a local preview of transit progress for the live card."""
        total_minutes = float(transit.get("total_minutes", 0) or 0)
        ratio = min(1.0, max(0.0, elapsed_seconds / 60.0))
        elapsed_minutes = round(total_minutes * ratio, 2)
        remaining_minutes = round(max(0.0, total_minutes - elapsed_minutes), 2)
        progress = round(min(100.0, ratio * 100.0), 2)

        total_distance = float(transit.get("distance", 0) or 0)
        distance_covered = round(total_distance * ratio, 2)
        distance_remaining = round(max(0.0, total_distance - distance_covered), 2)

        preview = dict(transit)
        preview["elapsed_minutes"] = elapsed_minutes
        preview["remaining_minutes"] = remaining_minutes
        preview["progress"] = progress
        preview["distance_covered"] = distance_covered
        preview["distance_remaining"] = distance_remaining
        return preview

    def _build_transit_card(self, transit: dict) -> ft.Card:
        """Create the live transit card used in the results panel."""
        return ft.Card(
            content=ft.Container(
                padding=SIZES["PADDING"],
                content=ft.Column([
                    ft.Text(
                        f"{transit.get('origin')} → {transit.get('destination')} ({transit.get('aircraft_type')})",
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(f"Progreso: {transit.get('progress', 0)}%"),
                    ft.Text(
                        f"Transcurrido: {transit.get('elapsed_minutes', 0)} min | Restante: {transit.get('remaining_minutes', 0)} min"
                    ),
                    ft.Text(f"Distancia recorrida: {transit.get('distance_covered', 0)} km / {transit.get('distance', 0)} km"),
                    ft.Text(f"Costo: ${transit.get('cost', 0)}"),
                ], spacing=4),
            )
        )

    async def _run_transit_monitor_async(self, session_id: str, base_transit: dict):
        """Refresh the transit card every second until the route completes or is cancelled."""
        if self.transit_monitor_running:
            return

        self.transit_monitor_running = True
        self.transit_monitor_cancelled = False
        self.transit_monitor_base = dict(base_transit)

        try:
            for elapsed_seconds in range(61):
                if self.transit_monitor_cancelled:
                    return

                state = await api_client.get_session_state(session_id)
                current_transit = state.get("transit") or {}
                if not state.get("in_transit") or not current_transit:
                    await self._on_fetch_options_async(None)
                    return

                total_minutes = float(current_transit.get("total_minutes", 0) or 0)
                step_minutes = total_minutes / 60.0 if total_minutes > 0 else 0.0

                if elapsed_seconds > 0 and step_minutes > 0:
                    try:
                        # Use the exact remaining minutes on the final tick so the flight reaches 100%.
                        advance_minutes = step_minutes
                        if elapsed_seconds >= 60:
                            advance_minutes = float(current_transit.get("remaining_minutes", step_minutes) or step_minutes)
                        await api_client.advance_session_transit(session_id, advance_minutes)
                    except Exception as exc:
                        # Show the user the issue and stop the loop so we do not hide backend validation errors.
                        self.main_window.show_error(f"No se pudo avanzar el vuelo: {exc}")
                        return

                    state = await api_client.get_session_state(session_id)
                    current_transit = state.get("transit") or current_transit

                options = await api_client.get_session_options(session_id)
                options_state = options.get("traveler_state", {}) or state

                # Use the real backend transit state for the card so progress and distance are synced.
                preview = dict(current_transit)
                preview.setdefault("elapsed_minutes", 0.0)
                preview.setdefault("remaining_minutes", total_minutes)
                preview.setdefault("progress", 0.0)
                if total_minutes > 0:
                    preview["distance_covered"] = round(float(preview.get("distance", 0) or 0) * min(1.0, float(preview.get("progress", 0) or 0) / 100.0), 2)
                    preview["distance_remaining"] = round(max(0.0, float(preview.get("distance", 0) or 0) - float(preview.get("distance_covered", 0) or 0)), 2)

                self._render_session_options(options, options_state, preview_transit=preview)

                if elapsed_seconds >= 60:
                    # If the backend already arrived, refresh options; otherwise force a final exact advance.
                    if state.get("in_transit") and current_transit:
                        remaining_minutes = float(current_transit.get("remaining_minutes", 0) or 0)
                        if remaining_minutes > 0:
                            try:
                                await api_client.advance_session_transit(session_id, remaining_minutes)
                            except Exception:
                                pass
                    await self._on_fetch_options_async(None)
                    self._set_advance_timer_status("Vuelo completado automáticamente")
                    return

                self._set_advance_timer_status(f"Vuelo en progreso: {elapsed_seconds}/60 s")
                await asyncio.sleep(1)
        finally:
            self.transit_monitor_running = False
            self.transit_monitor_cancelled = False
            self.transit_monitor_base = None

    def _ensure_transit_monitor(self, session_id: str, transit: dict):
        """Start the live transit monitor if it is not already running."""
        if self.transit_monitor_running:
            return
        self.main_window.page.run_task(self._run_transit_monitor_async, session_id, transit)

    def _render_session_options(self, options: dict, state: dict, preview_transit: dict | None = None):
        """Render the interactive session state and available actions."""
        transit = preview_transit or state.get("transit", {}) or {}
        controls = [
            ft.Text("Planificación dinámica paso a paso", weight=ft.FontWeight.BOLD, size=SIZES["FONT_SIZE_SUBTITLE"]),
            ft.Card(
                content=ft.Container(
                    padding=SIZES["PADDING"],
                    content=ft.Column([
                        ft.Text(f"Sesión: {self.session_id}"),
                        ft.Text(f"Aeropuerto actual: {state.get('current_airport', 'N/A')}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Presupuesto restante: ${state.get('remaining_budget', 0)}"),
                        ft.Text(f"Tiempo restante: {state.get('remaining_time', 0)} min"),
                        ft.Text(f"Estancia mínima pendiente: {options.get('pending_min_stay_minutes', 0)} min"),
                        ft.Text(f"¿Puede volar?: {'Sí' if options.get('can_take_flight', True) else 'No'}"),
                    ], spacing=4),
                )
            ),
            ft.Text(
                f"Rutas bloqueadas: {len(state.get('blocked_routes', []) or [])}",
                color=COLORS["PRIMARY"],
            ),
            ft.Divider(),
        ]

        # Show transit card either for real in-transit state or for a preview transit
        if (state.get("in_transit") and transit) or preview_transit:
            title_text = "Vuelo en tránsito"
            if preview_transit and not state.get("in_transit"):
                title_text = "Vuelo en tránsito (previsualización)"
            controls.append(ft.Text(title_text, weight=ft.FontWeight.BOLD, color="orange"))
            controls.append(self._build_transit_card(transit))
            controls.append(ft.Divider())

        # If we are showing a preview, refresh the graph panel only when it is already built.
        # This avoids triggering GraphPage.load_data before the graph view exists.
        graph_page = self.main_window.pages.get("network_graph")
        if graph_page and preview_transit and getattr(graph_page, "stack", None) is not None:
            try:
                graph_page.visualize_path([preview_transit.get("origin"), preview_transit.get("destination")])
            except Exception:
                pass

        recommended = state.get("recommended_itinerary", {}) or {}
        rec_flights = recommended.get("flights", []) or []
        controls.append(ft.Text("Mejor alternativa disponible (auto-recalculada)", weight=ft.FontWeight.BOLD))
        if rec_flights:
            controls.append(ft.Text(f"Destinos potenciales: {recommended.get('total_destinations', 0)}"))
            controls.append(ft.Text(f"Secuencia: {' → '.join(recommended.get('visited_airports', []))}"))
            controls.append(ft.Text(f"Costo total proyectado: {recommended.get('total_cost', 0)} USD"))
            controls.append(ft.Text(f"Tiempo total proyectado: {recommended.get('total_time', 0)} min"))
        else:
            controls.append(ft.Text("No hay alternativa disponible con las restricciones actuales."))
        controls.append(ft.Divider())

        controls.append(ft.Text("Vuelos disponibles:", weight=ft.FontWeight.BOLD))
        if not options.get("flights"):
            controls.append(ft.Text("No hay vuelos disponibles desde este aeropuerto."))
        for f in options.get("flights", []):
            take_btn = ft.ElevatedButton(
                "Elegir vuelo",
                icon="flight_takeoff",
                on_click=lambda e, payload=f, st=state: self.main_window.page.run_task(self._on_take_flight_async, payload, st)
            )
            controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=SIZES["PADDING"],
                        content=ft.Column([
                            ft.Text(f"{f['origin']} → {f['destination']} ({f['aircraft_type']})", weight=ft.FontWeight.BOLD),
                            ft.Text(f"Distancia: {f['distance']} km | Costo: ${f['cost']} | Tiempo: {f['time']} min"),
                            ft.Text(f"Subsidio: {'Sí' if f.get('subsidized') else 'No'}"),
                            ft.Row([take_btn], spacing=8),
                        ], spacing=4),
                    )
                )
            )

        controls.append(ft.Text("Trabajos disponibles:", weight=ft.FontWeight.BOLD))
        if not options.get("jobs"):
            controls.append(ft.Text("No hay trabajos disponibles en este aeropuerto."))
        else: 
            controls.append(ft.Text("Solo se pueden aceptar trabajos cuando se llegue al 35% del presupuesto inicial", color = "orange"))
        for job in options.get("jobs", []):
            hours_input = ft.TextField(label="Horas", width=80)
            btn = ft.ElevatedButton(
                f"Aceptar {job.get('nombre')} (tarifa {job.get('tarifaHora')})",
                on_click=lambda e, j=job, h=hours_input: self.main_window.page.run_task(self._on_accept_job_async, (j, h))
            )
            controls.append(ft.Row([ft.Text(f"{job.get('nombre')} | tarifa: {job.get('tarifaHora')} | maxHoras: {job.get('maxHoras')}") , hours_input, btn], wrap=True))

        controls.append(ft.Text("Actividades (opcionales):", weight=ft.FontWeight.BOLD))
        activity_checks = []
        for act in options.get("activities", []):
            chk = ft.Checkbox(label=f"{act.get('nombre')} - ${act.get('costoUSD')} | {act.get('duracionMin')}min")
            activity_checks.append((act, chk))
            controls.append(chk)

        if not activity_checks:
            controls.append(ft.Text("No hay actividades opcionales en este aeropuerto."))

        apply_acts_btn = ft.ElevatedButton("Aplicar actividades seleccionadas", icon="hiking", on_click=lambda e, items=activity_checks: self.main_window.page.run_task(self._on_apply_activities_async, items))
        controls.append(apply_acts_btn)

        if options.get("lodging_required"):
            controls.append(ft.Text("ALOJAMIENTO OBLIGATORIO: Debe hospedarse antes de continuar.", color="red"))
        if options.get("meal_required"):
            controls.append(ft.Text("ALIMENTACIÓN OBLIGATORIA: Consumir antes de continuar.", color="red"))

        controls.append(ft.Divider())
        self._set_results(controls)

        graph_page = self.main_window.pages.get("network_graph")
        if graph_page and getattr(graph_page, "stack", None) is not None:
            try:
                self.main_window.page.run_task(graph_page.load_data)
            except Exception:
                pass
            try:
                if state.get("in_transit") and transit:
                    graph_page.visualize_path([transit.get("origin"), transit.get("destination")])
                else:
                    graph_page.visualize_path([])
            except Exception:
                pass

    def _on_generate_itinerary(self, e):
        """Handle generate itinerary button click (synchronous wrapper for Flet event)."""
        self.main_window.page.run_task(self._on_generate_itinerary_async, e)

    async def _on_start_session_async(self, e):
        try:
            origin = (self.origin_field.value or "").strip().upper()
            if not origin:
                raise ValueError("Ingresa un aeropuerto de origen.")

            try:
                budget = float(self.budget_field.value)
            except Exception:
                raise ValueError("Ingresa un presupuesto válido (USD).")

            try:
                available_time_hours = float(self.time_field.value)
            except Exception:
                raise ValueError("Ingresa un tiempo disponible válido (horas).")

            preferred_transports = self._selected_transports()
            if not preferred_transports:
                raise ValueError("Debes seleccionar al menos un tipo de transporte.")

            include_secondary_airports = bool(self.include_secondary_switch.value)

            result = await api_client.create_session(
                origin=origin,
                initial_budget=budget,
                available_time_hours=available_time_hours,
                preferred_transports=preferred_transports,
                include_secondary_airports=include_secondary_airports,
            )

            # Backend may return different shapes; try to extract session_id robustly
            session_id = None
            if isinstance(result, dict):
                session_id = result.get("session_id") or result.get("sessionId") or result.get("id")
                # sometimes planning_service returns wrapper {session_id:..., state:{...}}
                if not session_id and isinstance(result.get("state"), dict):
                    session_id = result["state"].get("session_id") or result["state"].get("sessionId")

            if not session_id:
                # show full response for debugging
                self.main_window.show_error("Respuesta inesperada del servidor al iniciar sesión. Revisa consola.")
                self._set_results([ft.Text("Respuesta servidor:"), ft.Text(str(result))])
                return

            self.session_id = session_id
            state = result if isinstance(result, dict) else {}
            self._set_results([ft.Text(f"Sesión iniciada: {self.session_id}"), ft.Divider(), ft.Text(str(state))])
            # Fetch options immediately
            await self._on_fetch_options_async(None)
        except ValueError as exc:
            self.main_window.show_error(str(exc))
        except Exception as exc:
            self.main_window.show_error(f"No se pudo iniciar la sesión: {exc}")

    def _on_start_session(self, e):
        self.main_window.page.run_task(self._on_start_session_async, e)

    async def _on_fetch_options_async(self, e):
        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return
        try:
            options = await api_client.get_session_options(self.session_id)
            state = options.get("traveler_state", {})
            transit = state.get("transit", {}) or {}
            if state.get("in_transit") and transit:
                self._ensure_transit_monitor(self.session_id, transit)
            else:
                self.transit_monitor_cancelled = True
                self.transit_monitor_running = False
                self.transit_monitor_base = None
                self._set_advance_timer_status("Temporizador listo")

            self._render_session_options(options, state)
        except Exception as exc:
            self.main_window.show_error(f"No se pudieron obtener opciones: {exc}")

    def _on_fetch_options(self, e):
        self.main_window.page.run_task(self._on_fetch_options_async, e)

    async def _on_take_flight_async(self, flight, state):
        """When a flight is chosen, start the backend transit immediately and let the monitor advance it."""
        if self.preview_monitor_running:
            return

        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return

        self.preview_monitor_running = True
        self.preview_monitor_cancelled = False

        try:
            # Create the transit immediately in the backend.
            decision = {"type": "flight", "destination": flight["destination"], "aircraft_type": flight["aircraft_type"]}
            result = await api_client.post_session_decision(self.session_id, decision)
            self._set_results([ft.Text(str(result))])
            await self._on_fetch_options_async(None)
        except Exception as exc:
            self.main_window.show_error(f"No se pudo tomar el vuelo: {exc}")
        finally:
            self.preview_monitor_running = False
            self.preview_monitor_cancelled = False

    

    async def _on_accept_job_async(self, payload):
        try:
            job, hours_input = payload
            hours = int(hours_input.value or 0)
            decision = {"type": "job", "job_name": job.get("nombre"), "hours": hours}
            result = await api_client.post_session_decision(self.session_id, decision)
            self._set_results([ft.Text(str(result))])
            await self._on_fetch_options_async(None)
        except Exception as exc:
            self.main_window.show_error(f"No se pudo aceptar el trabajo: {exc}")

    async def _on_apply_activities_async(self, items):
        try:
            selected = [act.get("nombre") for act, chk in items if chk.value]
            decision = {"type": "activities", "activities": selected}
            result = await api_client.post_session_decision(self.session_id, decision)
            self._set_results([ft.Text(str(result))])
            await self._on_fetch_options_async(None)
        except Exception as exc:
            self.main_window.show_error(f"No se pudieron aplicar actividades: {exc}")

    async def _on_apply_stay_async(self, e):
        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return
        try:
            free_time_min = int((self.stay_minutes_field.value or "0").strip() or 0)
            decision = {"type": "stay", "free_time_min": free_time_min}
            await api_client.post_session_decision(self.session_id, decision)
            await self._on_fetch_options_async(None)
            self.main_window.show_success("Stay aplicado correctamente")
        except Exception as exc:
            self.main_window.show_error(f"No se pudo aplicar stay: {exc}")

    def _on_apply_stay(self, e):
        self.main_window.page.run_task(self._on_apply_stay_async, e)

    async def _on_advance_transit_async(self, e):
        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return
        try:
            state = await api_client.get_session_state(self.session_id)
            transit = state.get("transit") or {}
            if not state.get("in_transit") or not transit:
                raise ValueError("No hay vuelo en tránsito")

            self._set_advance_timer_status("Temporizador de vuelo iniciado")
            self._ensure_transit_monitor(self.session_id, transit)
            self.main_window.show_success("El vuelo se está actualizando en tiempo real")
        except Exception as exc:
            self.main_window.show_error(f"No se pudo avanzar el vuelo: {exc}")

    def _on_advance_transit(self, e):
        self.main_window.page.run_task(self._on_advance_transit_async, e)

    async def _on_interrupt_route_async(self, e):
        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return
        try:
            origin = (self.interrupt_origin_field.value or "").strip().upper()
            destination = (self.interrupt_destination_field.value or "").strip().upper()

            # If fields are empty, interrupt the current in-transit segment automatically.
            if not origin or not destination:
                state = await api_client.get_session_state(self.session_id)
                transit = state.get("transit") or {}
                if state.get("in_transit") and transit:
                    origin = (transit.get("origin") or "").strip().upper()
                    destination = (transit.get("destination") or "").strip().upper()
                    if self.interrupt_origin_field:
                        self.interrupt_origin_field.value = origin
                    if self.interrupt_destination_field:
                        self.interrupt_destination_field.value = destination
                if not origin or not destination:
                    raise ValueError("Debes indicar origen y destino, o interrumpir mientras haya un vuelo en tránsito")

            await api_client.interrupt_route(
                origin_id=origin,
                destination_id=destination,
                session_id=self.session_id,
                reason="Interrupcion manual desde interfaz",
            )
            if self.advance_timer_running:
                self._cancel_advance_timer()
            await self._on_fetch_options_async(None)
            self.main_window.show_success("Ruta interrumpida y plan recalculado")
        except Exception as exc:
            self.main_window.show_error(f"No se pudo interrumpir la ruta: {exc}")

    def _on_interrupt_route(self, e):
        self.main_window.page.run_task(self._on_interrupt_route_async, e)

    def _build_report_controls(self, report: dict):
        controls = [
            ft.Text("Reporte final del viaje", weight=ft.FontWeight.BOLD, size=SIZES["FONT_SIZE_SUBTITLE"]),
            ft.Divider(),
            ft.Text("Destinos visitados", weight=ft.FontWeight.BOLD),
        ]

        for item in report.get("destinos_visitados", []) or []:
            controls.append(
                ft.Text(
                    f"{item.get('airport_id')} | {item.get('nombre')} ({item.get('ciudad')}, {item.get('pais')}) "
                    f"| estadía: {item.get('tiempo_estadia_min', 0)} min | costo destino: ${item.get('costo_total_destino', 0)}"
                )
            )

        controls.append(ft.Divider())
        controls.append(ft.Text("Tramos volados", weight=ft.FontWeight.BOLD))
        for item in report.get("tramos_volados", []) or []:
            controls.append(
                ft.Text(
                    f"{item.get('origen')} → {item.get('destino')} | {item.get('aeronave')} | "
                    f"{item.get('distancia_km')} km | {item.get('tiempo_vuelo_min')} min | ${item.get('costo_tramo')}"
                )
            )

        controls.append(ft.Divider())
        controls.append(ft.Text("Actividades realizadas", weight=ft.FontWeight.BOLD))
        for item in report.get("actividades_realizadas", []) or []:
            controls.append(
                ft.Text(
                    f"{item.get('nombre')} ({item.get('tipo')}) | {item.get('tiempo_min')} min | ${item.get('costo')} | {item.get('airport')}"
                )
            )

        controls.append(ft.Divider())
        controls.append(ft.Text("Trabajos realizados", weight=ft.FontWeight.BOLD))
        for item in report.get("trabajos_realizados", []) or []:
            controls.append(
                ft.Text(
                    f"{item.get('nombre_trabajo')} | horas: {item.get('horas_trabajadas')} | "
                    f"ingreso: ${item.get('ingreso_obtenido')} | {item.get('airport')}"
                )
            )

        totals = report.get("totales", {}) or {}
        controls.append(ft.Divider())
        controls.append(ft.Text("Totales", weight=ft.FontWeight.BOLD))
        controls.append(ft.Text(f"Presupuesto inicial: ${totals.get('presupuesto_inicial', 0)}"))
        controls.append(ft.Text(f"Total gastado: ${totals.get('total_gastado', 0)}"))
        controls.append(ft.Text(f"Total ganado: ${totals.get('total_ganado', 0)}"))
        controls.append(ft.Text(f"Saldo final: ${totals.get('saldo_final', 0)}"))
        controls.append(ft.Text(f"Tiempo total del viaje: {totals.get('tiempo_total_viaje_min', 0)} min"))

        return controls

    async def _on_get_report_async(self, e):
        if not self.session_id:
            self.main_window.show_error("No hay sesión activa")
            return
        try:
            report = await api_client.get_session_report(self.session_id)
            self._set_results(self._build_report_controls(report))
        except Exception as exc:
            self.main_window.show_error(f"No se pudo generar el reporte: {exc}")

    def _on_get_report(self, e):
        self.main_window.page.run_task(self._on_get_report_async, e)
