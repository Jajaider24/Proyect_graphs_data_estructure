"""Planning service layer for itinerary alternatives and constraints."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import uuid


class PlanningService:
    """Planning orchestration service."""

    def __init__(self):
        # In-memory session store: session_id -> PlanningSession
        self.sessions: Dict[str, "PlanningSession"] = {}

    def execute_planning(
        self,
        graph,
        origin: str,
        budget: float,
        available_time_minutes: float,
        preferred_transports: Optional[List[str]] = None,
        include_secondary_airports: bool = True,
    ) -> Dict:
        """Generate two itinerary alternatives for basic planning requirement 2.2.

        Alternatives:
        - maximize destinations under budget
        - maximize destinations under time
        """

        if not graph or origin not in graph.airports:
            raise ValueError(f"Origin airport '{origin}' not found")

        # collect available transport types from graph
        available_transport_types = set()
        for airport in graph.airports.values():
            for route in getattr(airport, "routes", []) or []:
                for aircraft in getattr(route, "aircraft_options", []) or []:
                    available_transport_types.add(aircraft.name)
        if preferred_transports:
            allowed_transports = [t for t in preferred_transports if t in available_transport_types]
        else:
            allowed_transports = sorted(available_transport_types)

        if not allowed_transports:
            raise ValueError("No valid transport types selected for current network")

        required_transports = set(allowed_transports)

        budget_alternative = self._find_best_itinerary(
            graph=graph,
            origin=origin,
            max_budget=budget,
            max_time=available_time_minutes,
            allowed_transports=set(allowed_transports),
            required_transports=required_transports,
            include_secondary_airports=include_secondary_airports,
            objective="budget",
        )

        time_alternative = self._find_best_itinerary(
            graph=graph,
            origin=origin,
            max_budget=budget,
            max_time=available_time_minutes,
            allowed_transports=set(allowed_transports),
            required_transports=required_transports,
            include_secondary_airports=include_secondary_airports,
            objective="time",
        )

        return {
            "origin": origin,
            "required_transport_types": sorted(required_transports),
            "alternatives": {
                "max_destinations_budget": budget_alternative,
                "max_destinations_time": time_alternative,
            },
        }

    def _collect_transport_types(self, graph) -> Set[str]:
        transport_types: Set[str] = set()
        for airport in graph.airports.values():
            for route in getattr(airport, "routes", []) or []:
                for aircraft in getattr(route, "aircraft_options", []) or []:
                    transport_types.add(aircraft.name)
        return transport_types

    def _find_best_itinerary(
        self,
        graph,
        origin: str,
        max_budget: float,
        max_time: float,
        allowed_transports: Set[str],
        required_transports: Set[str],
        include_secondary_airports: bool,
        objective: str,
    ) -> Dict:
        best_payload: Optional[Dict] = None
        best_score: Optional[Tuple] = None

        def evaluate_candidate(payload: Dict) -> Tuple:
            transport_ok = payload["transport_requirement_met"]
            total_destinations = payload["total_destinations"]
            used_count = len(payload["used_transport_types"])
            total_cost = payload["total_cost"]
            total_time = payload["total_time"]

            if objective == "budget":
                return (
                    1 if transport_ok else 0,
                    total_destinations,
                    used_count,
                    -total_cost,
                    -total_time,
                )

            return (
                1 if transport_ok else 0,
                total_destinations,
                used_count,
                -total_time,
                -total_cost,
            )

        def select_aircraft_options(route):
            options = [a for a in route.aircraft_options if a.name in allowed_transports]
            if objective == "budget":
                options.sort(key=lambda a: (route.calculate_cost(a), route.calculate_time(a)))
            else:
                options.sort(key=lambda a: (route.calculate_time(a), route.calculate_cost(a)))
            return options

        def dfs(
            current_airport_id: str,
            visited: Set[str],
            flights: List[Dict],
            total_cost: float,
            total_time: float,
            total_distance: float,
            used_transports: Set[str],
        ):
            nonlocal best_payload, best_score

            # Keep the route in travel order; `visited` is only for cycle detection.
            route_sequence = [origin]
            route_sequence.extend(
                flight["destination"] for flight in flights if flight.get("destination")
            )

            payload = {
                "criterion": objective,
                "visited_airports": route_sequence,
                "total_destinations": max(0, len(visited) - 1),
                "flights": flights.copy(),
                "total_distance": round(total_distance, 2),
                "total_cost": round(total_cost, 2),
                "total_time": round(total_time, 2),
                "constraints_met": {
                    "budget": total_cost <= max_budget,
                    "time": total_time <= max_time,
                },
                "used_transport_types": sorted(used_transports),
                "transport_requirement_met": required_transports.issubset(used_transports),
            }

            score = evaluate_candidate(payload)
            if best_score is None or score > best_score:
                best_score = score
                best_payload = payload

            current_airport = graph.airports.get(current_airport_id)
            if current_airport is None:
                return

            for route in getattr(current_airport, "routes", []) or []:
                if not route.is_available:
                    continue

                destination = route.destination
                destination_id = destination.id

                if destination_id in visited:
                    continue

                if (
                    not include_secondary_airports
                    and not destination.es_hub
                    and destination_id != origin
                ):
                    continue

                aircraft_options = select_aircraft_options(route)
                if not aircraft_options:
                    continue

                for aircraft in aircraft_options:
                    segment_cost = route.calculate_cost(aircraft)
                    segment_time = route.calculate_time(aircraft)
                    segment_distance = route.distance_km

                    new_total_cost = total_cost + segment_cost
                    new_total_time = total_time + segment_time

                    if new_total_cost > max_budget or new_total_time > max_time:
                        continue

                    new_total_distance = total_distance + segment_distance
                    new_used_transports = set(used_transports)
                    new_used_transports.add(aircraft.name)

                    new_flights = flights.copy()
                    new_flights.append(
                        {
                            "origin": current_airport_id,
                            "destination": destination_id,
                            "distance": round(segment_distance, 2),
                            "time": round(segment_time, 2),
                            "cost": round(segment_cost, 2),
                            "aircraft_type": aircraft.name,
                            "cumulative_cost": round(new_total_cost, 2),
                            "cumulative_time": round(new_total_time, 2),
                        }
                    )

                    new_visited = set(visited)
                    new_visited.add(destination_id)

                    dfs(
                        current_airport_id=destination_id,
                        visited=new_visited,
                        flights=new_flights,
                        total_cost=new_total_cost,
                        total_time=new_total_time,
                        total_distance=new_total_distance,
                        used_transports=new_used_transports,
                    )

        dfs(
            current_airport_id=origin,
            visited={origin},
            flights=[],
            total_cost=0.0,
            total_time=0.0,
            total_distance=0.0,
            used_transports=set(),
        )

        if best_payload is None:
            return {
                "criterion": objective,
                "visited_airports": [origin],
                "total_destinations": 0,
                "flights": [],
                "total_distance": 0.0,
                "total_cost": 0.0,
                "total_time": 0.0,
                "constraints_met": {"budget": True, "time": True},
                "used_transport_types": [],
                "transport_requirement_met": False,
            }

        return best_payload

    # -----------------------------
    # Interactive planning sessions
    # -----------------------------

    def create_session(
        self,
        graph,
        origin: str,
        initial_budget: float,
        available_time_minutes: float,
        preferred_transports: Optional[List[str]] = None,
        include_secondary_airports: bool = True,
    ) -> Dict:
        """Create a step-by-step planning session for dynamic budgeting (requirement 2.3).

        Returns a session descriptor with `session_id` and initial state.
        """

        if not graph or origin not in graph.airports:
            raise ValueError(f"Origin airport '{origin}' not found")

        session_id = str(uuid.uuid4())

        # Determine allowed transports
        available_transport_types = set()
        for airport in graph.airports.values():
            for route in getattr(airport, "routes", []) or []:
                for aircraft in getattr(route, "aircraft_options", []) or []:
                    available_transport_types.add(aircraft.name)
        if preferred_transports:
            allowed_transports = [t for t in preferred_transports if t in available_transport_types]
        else:
            allowed_transports = sorted(available_transport_types)

        traveler = None
        from src.core.traveler import Traveler

        traveler = Traveler(
            current_airport=graph.get_airport(origin),
            initial_budget=initial_budget,
            available_time=available_time_minutes,
        )

        # Create session object
        session = PlanningSession(
            session_id=session_id,
            graph=graph,
            traveler=traveler,
            allowed_transports=set(allowed_transports),
            include_secondary_airports=include_secondary_airports,
        )

        self.sessions[session_id] = session

        return {"session_id": session_id, "state": session.get_state()}

    def get_session_options(self, session_id: str) -> Dict:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.get_options()

    def apply_session_decision(self, session_id: str, decision: Dict) -> Dict:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.apply_decision(decision)

    def get_session_state(self, session_id: str) -> Dict:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.get_state()

    def interrupt_route(
        self,
        origin_id: Optional[str] = None,
        destination_id: Optional[str] = None,
        session_id: Optional[str] = None,
        reason: str = "Interrupcion operativa",
    ) -> Dict[str, Any]:
        graph = None
        target_session = None
        if session_id:
            session = self.sessions.get(session_id)
            if not session:
                raise ValueError("Session not found")
            graph = session.graph
            target_session = session
        else:
            if self.sessions:
                graph = next(iter(self.sessions.values())).graph

        if graph is None:
            raise ValueError("No graph available for route interruption")

        # If route was not provided, infer it from the current session transit.
        if (not origin_id or not destination_id) and target_session and target_session.transit:
            origin_id = target_session.transit.get("origin")
            destination_id = target_session.transit.get("destination")

        if not origin_id or not destination_id:
            raise ValueError("Origin and destination are required when no flight is currently in transit")

        origin = graph.airports.get(origin_id)
        if not origin:
            raise ValueError("Origin airport not found")

        route = next((r for r in getattr(origin, "routes", []) or [] if r.destination.id == destination_id), None)
        if route is None:
            raise ValueError("Route not found")

        route.blocked = True
        route.is_available = False

        impacted_sessions: List[str] = []
        for sid, sess in self.sessions.items():
            if sess.handle_route_interruption(origin_id, destination_id, reason):
                impacted_sessions.append(sid)

        return {
            "status": "blocked",
            "origin_id": origin_id,
            "destination_id": destination_id,
            "reason": reason,
            "impacted_sessions": impacted_sessions,
        }

    def get_session_report(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.build_final_report()


class PlanningSession:
    """Represents an interactive planning session for a single traveler."""

    def __init__(
        self,
        session_id: str,
        graph,
        traveler,
        allowed_transports: Set[str],
        include_secondary_airports: bool = True,
    ):
        self.session_id = session_id
        self.graph = graph
        self.traveler = traveler
        self.allowed_transports = allowed_transports
        self.include_secondary_airports = include_secondary_airports
        self.history: List[Dict[str, Any]] = []
        self.total_distance = 0.0
        self.subsidized_distance = 0.0
        self.pending_min_stay_minutes = 0.0
        self.transit: Optional[Dict[str, Any]] = None
        self.blocked_routes: List[Dict[str, str]] = []
        self.recommended_itinerary: Dict[str, Any] = {}

        self.net_config = getattr(graph, "config", {}) or {}
        if self.traveler.current_airport:
            self.traveler.visit_airport(self.traveler.current_airport)
        self._recompute_recommended_itinerary()

    def get_state(self) -> Dict:
        return {
            "session_id": self.session_id,
            "current_airport": self.traveler.current_airport.id if self.traveler.current_airport else None,
            "remaining_budget": round(self.traveler.current_budget, 2),
            "remaining_time": round(self.traveler.remaining_time, 2),
            "visited_airports": list(self.traveler.visited_airports),
            "total_distance": round(self.total_distance, 2),
            "subsidized_distance": round(self.subsidized_distance, 2),
            "pending_min_stay_minutes": round(self.pending_min_stay_minutes, 2),
            "jobs_done": list(self.traveler.jobs_done),
            "activities_done": list(self.traveler.activities_done),
            "in_transit": self.transit is not None,
            "transit": self.transit or {},
            "recommended_itinerary": self.recommended_itinerary,
            "blocked_routes": list(self.blocked_routes),
        }

    def _lodging_required(self) -> bool:
        lodging_interval = self.net_config.get("intervaloAlojamiento", 20)
        return self.traveler.hours_since_last_lodging >= lodging_interval

    def _meal_required(self) -> bool:
        meal_interval = self.net_config.get("intervaloAlimentacion", 8)
        return self.traveler.hours_since_last_meal >= meal_interval

    def _consume_minutes(self, minutes: float):
        self.traveler.consume_time(minutes)
        delta_hours = minutes / 60.0
        self.traveler.hours_since_last_meal += delta_hours
        self.traveler.hours_since_last_lodging += delta_hours
        return delta_hours

    def _decrease_pending_stay(self, consumed_minutes: float):
        self.pending_min_stay_minutes = max(0.0, self.pending_min_stay_minutes - consumed_minutes)

    def _recompute_recommended_itinerary(self):
        origin = self.traveler.current_airport.id if self.traveler.current_airport else None
        if not origin:
            self.recommended_itinerary = {}
            return

        self.recommended_itinerary = self._find_best_itinerary(
            graph=self.graph,
            origin=origin,
            max_budget=max(0.0, float(self.traveler.current_budget)),
            max_time=max(0.0, float(self.traveler.remaining_time)),
            allowed_transports=set(self.allowed_transports),
            required_transports=set(),
            include_secondary_airports=self.include_secondary_airports,
            objective="budget",
        )

    def _itinerary_uses_segment(self, origin_id: str, destination_id: str) -> bool:
        flights = self.recommended_itinerary.get("flights", []) or []
        for flight in flights:
            if flight.get("origin") == origin_id and flight.get("destination") == destination_id:
                return True
        return False

    def get_options(self) -> Dict:
        """Return available flights, activities and jobs with computed costs/times."""
        if self.transit is not None:
            return {
                "flights": [],
                "activities": [],
                "jobs": [],
                "lodging_required": False,
                "meal_required": False,
                "pending_min_stay_minutes": round(self.pending_min_stay_minutes, 2),
                "can_take_flight": False,
                "traveler_state": self.get_state(),
            }

        airport = self.traveler.current_airport
        if airport is None:
            raise ValueError("Traveler has no current airport")

        flights = []
        for route in getattr(airport, "routes", []) or []:
            if not bool(getattr(route, "is_available", True)):
                continue

            if route.destination.id in self.traveler.visited_airports:
                continue

            if (
                not self.include_secondary_airports
                and not route.destination.es_hub
                and route.destination.id != self.traveler.current_airport.id
            ):
                continue

            for aircraft in getattr(route, "aircraft_options", []) or []:
                if aircraft.name not in self.allowed_transports:
                    continue

                flights.append(
                    {
                        "origin": airport.id,
                        "destination": route.destination.id,
                        "distance": route.distance_km,
                        "aircraft_type": aircraft.name,
                        "cost": round(route.calculate_cost(aircraft), 2),
                        "time": round(route.calculate_time(aircraft), 2),
                        "subsidized": bool(route.subsidized),
                        "blocked": bool(getattr(route, "blocked", False)),
                    }
                )

        activities = getattr(airport, "actividades", []) or []
        jobs = getattr(airport, "trabajos", []) or []
        lodging_required = self._lodging_required()
        meal_required = self._meal_required()

        return {
            "flights": flights,
            "activities": activities,
            "jobs": jobs,
            "lodging_required": lodging_required,
            "meal_required": meal_required,
            "pending_min_stay_minutes": round(self.pending_min_stay_minutes, 2),
            "can_take_flight": (not lodging_required) and self.pending_min_stay_minutes <= 0,
            "traveler_state": self.get_state(),
        }

    def apply_decision(self, decision: Dict) -> Dict:
        dtype = decision.get("type")
        if dtype == "job":
            result = self._apply_job_decision(decision)
        elif dtype == "activities":
            result = self._apply_activities_decision(decision)
        elif dtype == "flight":
            result = self._apply_flight_decision(decision)
        elif dtype == "stay":
            result = self._apply_stay_decision(decision)
        elif dtype == "advance":
            result = self._apply_advance_decision(decision)
        else:
            raise ValueError("Unknown decision type")

        if dtype != "advance" or self.transit is None:
            self._recompute_recommended_itinerary()
        return result

    def _apply_job_decision(self, decision: Dict) -> Dict:
        if self.transit is not None:
            raise ValueError("No puedes tomar trabajos durante un vuelo en transito")

        job_name = decision.get("job_name")
        hours = int(decision.get("hours", 0))
        airport = self.traveler.current_airport
        if not airport or not airport.trabajos:
            raise ValueError("No jobs available")

        job = next((j for j in airport.trabajos if j.get("nombre") == job_name), None)
        if not job:
            raise ValueError("Job not found")

        hours = min(hours, int(job.get("maxHoras", hours)))
        min_pct = self.net_config.get("presupuestoMinimoPorc", 35)
        if not (self.traveler.current_budget <= (self.traveler.initial_budget * (min_pct / 100.0))):
            raise ValueError("Budget threshold not reached; jobs unavailable")

        earnings = hours * job.get("tarifaHora", 0)
        worked_minutes = hours * 60
        self.traveler.earn_money(earnings)
        self._consume_minutes(worked_minutes)
        self._decrease_pending_stay(worked_minutes)
        entry = {
            "airport": airport.id,
            "job_name": job.get("nombre"),
            "hours": hours,
            "earnings": round(earnings, 2),
        }
        self.traveler.jobs_done.append(entry)
        self.history.append({"action": "job", "detail": entry, "airport": airport.id, "time": worked_minutes})

        return {"result": "job_applied", "state": self.get_state()}

    def _apply_activities_decision(self, decision: Dict) -> Dict:
        if self.transit is not None:
            raise ValueError("No puedes tomar actividades durante un vuelo en transito")

        selected = decision.get("activities", []) or []
        airport = self.traveler.current_airport
        if not airport:
            raise ValueError("No current airport")

        for act_name in selected:
            activity = next((a for a in airport.actividades if a.get("nombre") == act_name), None)
            if not activity:
                continue
            cost = float(activity.get("costoUSD", 0))
            time = float(activity.get("duracionMin", 0))
            if self.traveler.current_budget < cost or self.traveler.remaining_time < time:
                continue

            self.traveler.spend_money(cost)
            self._consume_minutes(time)
            self._decrease_pending_stay(time)
            detail = {
                "airport": airport.id,
                "activity": activity.get("nombre"),
                "type": activity.get("tipo", "opcional"),
                "time": round(time, 2),
                "cost": round(cost, 2),
            }
            self.traveler.activities_done.append(detail)
            self.history.append({"action": "activity", "detail": detail, "airport": airport.id, "time": time})

        return {"result": "activities_applied", "state": self.get_state()}

    def _apply_stay_decision(self, decision: Dict) -> Dict:
        if self.transit is not None:
            raise ValueError("No puedes aplicar stay durante un vuelo en transito")

        airport = self.traveler.current_airport
        if not airport:
            raise ValueError("No current airport")

        free_time_min = max(0, int(decision.get("free_time_min", 0) or 0))
        total_stay_minutes = 0.0
        lodging_applied = False
        meal_applied = False

        if self._lodging_required():
            lodging_cost = airport.costo_alojamiento
            if self.traveler.current_budget < lodging_cost:
                raise ValueError("Insufficient budget for mandatory lodging")
            self.traveler.spend_money(lodging_cost)
            self._consume_minutes(480)
            self.traveler.hours_since_last_lodging = 0
            total_stay_minutes += 480
            lodging_applied = True
            self.history.append({"action": "lodging", "airport": airport.id, "cost": lodging_cost, "time": 480})

        if self._meal_required():
            food_cost = airport.costo_alimentacion
            if self.traveler.current_budget < food_cost:
                raise ValueError("Insufficient budget for mandatory meal")
            self.traveler.spend_money(food_cost)
            self._consume_minutes(60)
            self.traveler.hours_since_last_meal = 0
            total_stay_minutes += 60
            meal_applied = True
            self.history.append({"action": "meal", "airport": airport.id, "cost": food_cost, "time": 60})

        if free_time_min > 0:
            self._consume_minutes(free_time_min)
            total_stay_minutes += free_time_min
            self.history.append({"action": "free_time", "airport": airport.id, "time": free_time_min})

        remaining_required = max(0.0, self.pending_min_stay_minutes - total_stay_minutes)
        if remaining_required > 0:
            self._consume_minutes(remaining_required)
            total_stay_minutes += remaining_required
            self.history.append({"action": "auto_free_time", "airport": airport.id, "time": remaining_required})

        self._decrease_pending_stay(total_stay_minutes)
        return {
            "result": "stay_applied",
            "lodging_applied": lodging_applied,
            "meal_applied": meal_applied,
            "total_stay_minutes": round(total_stay_minutes, 2),
            "state": self.get_state(),
        }

    def _apply_flight_decision(self, decision: Dict) -> Dict:
        if self.transit is not None:
            raise ValueError("Ya existe un vuelo en transito")

        dest = decision.get("destination")
        aircraft_type = decision.get("aircraft_type")
        airport = self.traveler.current_airport
        if not airport:
            raise ValueError("No current airport")

        if self._lodging_required():
            raise ValueError("Mandatory lodging required before next flight. Apply a stay decision first")
        if self.pending_min_stay_minutes > 0:
            raise ValueError("Minimum stay at current airport not completed. Apply a stay decision first")

        route = next((r for r in airport.routes if r.destination.id == dest and r.is_available), None)
        if not route:
            raise ValueError("Route not found or unavailable")

        aircraft = next((a for a in route.aircraft_options if a.name == aircraft_type), None)
        if not aircraft:
            raise ValueError("Aircraft type not available on route")

        cost = float(route.calculate_cost(aircraft))
        time_min = float(route.calculate_time(aircraft))
        distance = float(route.distance_km)

        subsidized_after = self.subsidized_distance + (distance if route.subsidized else 0.0)
        total_after = self.total_distance + distance
        if total_after > 0 and (subsidized_after / total_after) > 0.2:
            current_pct = 0.0 if self.total_distance <= 0 else (self.subsidized_distance / self.total_distance) * 100.0
            projected_pct = (subsidized_after / total_after) * 100.0
            raise ValueError(
                "Ruta subsidiada no permitida: "
                f"{origin.id} -> {route.destination.id} ({aircraft.name}) excede el 20% de distancia subsidiada "
                f"permitido. Actual: {current_pct:.2f}%, proyectado: {projected_pct:.2f}%"
            )
        if self.traveler.current_budget < cost:
            raise ValueError("Insufficient budget to take selected flight")

        self.traveler.spend_money(cost)
        self.transit = {
            "origin": airport.id,
            "destination": route.destination.id,
            "aircraft_type": aircraft.name,
            "distance": round(distance, 2),
            "cost": round(cost, 2),
            "total_minutes": round(time_min, 2),
            "elapsed_minutes": 0.0,
            "remaining_minutes": round(time_min, 2),
            "progress": 0.0,
            "subsidized": bool(route.subsidized),
            "min_stay": float(getattr(route, "min_stay", 0) or 0),
        }
        self.history.append({"action": "flight_started", "detail": dict(self.transit)})
        return {"result": "flight_started", "state": self.get_state()}

    def _apply_advance_decision(self, decision: Dict) -> Dict:
        if self.transit is None:
            raise ValueError("No hay vuelo en transito")

        advance_minutes = max(0.0, float(decision.get("advance_minutes", 0) or 0))
        if advance_minutes <= 0:
            raise ValueError("advance_minutes debe ser mayor que 0")

        remaining = max(0.0, float(self.transit["total_minutes"]) - float(self.transit["elapsed_minutes"]))
        consumed = min(remaining, advance_minutes)
        # record previous meal/lodging counters to detect thresholds crossed during flight
        prev_meal_hours = getattr(self.traveler, "hours_since_last_meal", 0.0)
        prev_lodging_hours = getattr(self.traveler, "hours_since_last_lodging", 0.0)

        self._consume_minutes(consumed)

        # detect if meal interval crossed during consumed minutes and charge to origin airport
        meal_interval = self.net_config.get("intervaloAlimentacion", 8)
        new_meal_hours = getattr(self.traveler, "hours_since_last_meal", 0.0)
        if prev_meal_hours < meal_interval and new_meal_hours >= meal_interval:
            # apply meal cost to the last visited airport (origin of transit)
            origin_id = self.transit.get("origin")
            origin_airport = self.graph.get_airport(origin_id) if origin_id else None
            if origin_airport:
                food_cost = getattr(origin_airport, "costo_alimentacion", 0)
                # charge meal (allow budget to go negative if needed)
                try:
                    self.traveler.spend_money(food_cost)
                except Exception:
                    # ensure spending doesn't crash session
                    self.traveler.current_budget -= food_cost
                    self.traveler.total_spent += food_cost
                # reset meal counter after applying meal
                self.traveler.hours_since_last_meal = 0
                # record history
                self.history.append({
                    "action": "meal_in_flight",
                    "airport": origin_id,
                    "cost": food_cost,
                    "time": 60,
                })

        self.transit["elapsed_minutes"] = round(float(self.transit["elapsed_minutes"]) + consumed, 2)
        rem = max(0.0, float(self.transit["total_minutes"]) - float(self.transit["elapsed_minutes"]))
        # Snap very small remainders to zero so the flight always reaches the destination.
        if rem <= 0.05:
            rem = 0.0
            self.transit["elapsed_minutes"] = round(float(self.transit["total_minutes"]), 2)
        self.transit["remaining_minutes"] = round(rem, 2)
        if float(self.transit["total_minutes"]) > 0:
            progress = (float(self.transit["elapsed_minutes"]) / float(self.transit["total_minutes"])) * 100.0
            if rem == 0.0:
                progress = 100.0
            self.transit["progress"] = round(progress, 2)

        if rem > 0:
            self.history.append({"action": "flight_progress", "detail": dict(self.transit), "consumed": consumed})
            return {"result": "transit_advanced", "state": self.get_state()}

        destination_id = self.transit["destination"]
        destination = self.graph.get_airport(destination_id)
        if destination is None:
            raise ValueError("Destination airport not found")

        segment = {
            "origin": self.transit["origin"],
            "destination": destination_id,
            "distance": self.transit["distance"],
            "time": self.transit["total_minutes"],
            "cost": self.transit["cost"],
            "aircraft_type": self.transit["aircraft_type"],
            "subsidized": bool(self.transit.get("subsidized", False)),
        }
        self.traveler.visit_airport(destination)
        self.traveler.flight_history.append(segment)
        self.total_distance += float(segment["distance"])
        if segment["subsidized"]:
            self.subsidized_distance += float(segment["distance"])
        self.pending_min_stay_minutes = max(0.0, float(self.transit.get("min_stay", 0) or 0))
        self.history.append({"action": "flight_arrived", "detail": segment})
        self.transit = None
        self._recompute_recommended_itinerary()
        return {"result": "flight_arrived", "state": self.get_state()}

    def handle_route_interruption(self, origin_id: str, destination_id: str, reason: str) -> bool:
        interruption = {
            "origin_id": origin_id,
            "destination_id": destination_id,
            "reason": reason,
        }
        if interruption not in self.blocked_routes:
            self.blocked_routes.append(interruption)

        impacted = False
        if self.transit and self.transit.get("origin") == origin_id and self.transit.get("destination") == destination_id:
            impacted = True
            elapsed = float(self.transit.get("elapsed_minutes", 0.0))
            # Explicitly place traveler back at route origin when interruption happens in transit.
            origin_airport = self.graph.get_airport(origin_id)
            if origin_airport is not None:
                self.traveler.current_airport = origin_airport
            self.history.append(
                {
                    "action": "flight_interrupted",
                    "detail": {
                        "origin": origin_id,
                        "destination": destination_id,
                        "elapsed_minutes": round(elapsed, 2),
                        "reason": reason,
                    },
                }
            )
            self.transit = None

        if impacted or self._itinerary_uses_segment(origin_id, destination_id):
            self._recompute_recommended_itinerary()
            return True
        return False

    def build_final_report(self) -> Dict[str, Any]:
        airports_by_id = self.graph.airports
        destination_stats: Dict[str, Dict[str, Any]] = {}

        for aid in self.traveler.visited_airports:
            airport = airports_by_id.get(aid)
            if not airport:
                continue
            destination_stats[aid] = {
                "airport_id": aid,
                "nombre": airport.nombre,
                "ciudad": airport.ciudad,
                "pais": airport.pais,
                "tiempo_estadia_min": 0.0,
                "costo_total_destino": 0.0,
            }

        for event in self.history:
            airport_id = event.get("airport") or (event.get("detail") or {}).get("airport")
            if not airport_id or airport_id not in destination_stats:
                continue

            action = event.get("action")
            if action in {"lodging", "meal", "free_time", "auto_free_time", "activity", "job"}:
                destination_stats[airport_id]["tiempo_estadia_min"] += float(event.get("time", 0) or 0)
                destination_stats[airport_id]["costo_total_destino"] += float(event.get("cost", 0) or 0)

        destinations_visited = []
        for value in destination_stats.values():
            value["tiempo_estadia_min"] = round(value["tiempo_estadia_min"], 2)
            value["costo_total_destino"] = round(value["costo_total_destino"], 2)
            destinations_visited.append(value)

        flight_segments = []
        for segment in self.traveler.flight_history:
            flight_segments.append(
                {
                    "origen": segment.get("origin"),
                    "destino": segment.get("destination"),
                    "aeronave": segment.get("aircraft_type"),
                    "distancia_km": round(float(segment.get("distance", 0) or 0), 2),
                    "tiempo_vuelo_min": round(float(segment.get("time", 0) or 0), 2),
                    "costo_tramo": round(float(segment.get("cost", 0) or 0), 2),
                }
            )

        activities = []
        for entry in self.traveler.activities_done:
            activities.append(
                {
                    "nombre": entry.get("activity"),
                    "tipo": entry.get("type", "opcional"),
                    "tiempo_min": round(float(entry.get("time", 0) or 0), 2),
                    "costo": round(float(entry.get("cost", 0) or 0), 2),
                    "airport": entry.get("airport"),
                }
            )

        jobs = []
        for entry in self.traveler.jobs_done:
            jobs.append(
                {
                    "nombre_trabajo": entry.get("job_name"),
                    "horas_trabajadas": entry.get("hours", 0),
                    "ingreso_obtenido": round(float(entry.get("earnings", 0) or 0), 2),
                    "airport": entry.get("airport"),
                }
            )

        total_time_trip = round(float(self.traveler.available_time - self.traveler.remaining_time), 2)
        totals = {
            "presupuesto_inicial": round(float(self.traveler.initial_budget), 2),
            "total_gastado": round(float(self.traveler.total_spent), 2),
            "total_ganado": round(float(self.traveler.total_earned), 2),
            "saldo_final": round(float(self.traveler.current_budget), 2),
            "tiempo_total_viaje_min": total_time_trip,
        }

        return {
            "session_id": self.session_id,
            "destinos_visitados": destinations_visited,
            "tramos_volados": flight_segments,
            "actividades_realizadas": activities,
            "trabajos_realizados": jobs,
            "totales": totals,
            "bloqueos_ruta": list(self.blocked_routes),
            "itinerario_recomendado_actual": self.recommended_itinerary,
        }

    def _find_best_itinerary(
        self,
        graph,
        origin: str,
        max_budget: float,
        max_time: float,
        allowed_transports: Set[str],
        required_transports: Set[str],
        include_secondary_airports: bool,
        objective: str,
    ) -> Dict:
        best_payload: Optional[Dict] = None
        best_score: Optional[Tuple] = None

        def evaluate_candidate(payload: Dict) -> Tuple:
            transport_ok = payload["transport_requirement_met"]
            total_destinations = payload["total_destinations"]
            used_count = len(payload["used_transport_types"])
            total_cost = payload["total_cost"]
            total_time = payload["total_time"]

            if objective == "budget":
                return (1 if transport_ok else 0, total_destinations, used_count, -total_cost, -total_time)
            return (1 if transport_ok else 0, total_destinations, used_count, -total_time, -total_cost)

        def select_aircraft_options(route):
            options = [a for a in route.aircraft_options if a.name in allowed_transports]
            if objective == "budget":
                options.sort(key=lambda a: (route.calculate_cost(a), route.calculate_time(a)))
            else:
                options.sort(key=lambda a: (route.calculate_time(a), route.calculate_cost(a)))
            return options

        def dfs(
            current_airport_id: str,
            visited: Set[str],
            flights: List[Dict],
            total_cost: float,
            total_time: float,
            total_distance: float,
            used_transports: Set[str],
        ):
            nonlocal best_payload, best_score

            # Keep the route in travel order; `visited` is only for cycle detection.
            route_sequence = [origin]
            route_sequence.extend(
                flight["destination"] for flight in flights if flight.get("destination")
            )

            payload = {
                "criterion": objective,
                "visited_airports": route_sequence,
                "total_destinations": max(0, len(visited) - 1),
                "flights": flights.copy(),
                "total_distance": round(total_distance, 2),
                "total_cost": round(total_cost, 2),
                "total_time": round(total_time, 2),
                "constraints_met": {
                    "budget": total_cost <= max_budget,
                    "time": total_time <= max_time,
                },
                "used_transport_types": sorted(used_transports),
                "transport_requirement_met": required_transports.issubset(used_transports),
            }

            score = evaluate_candidate(payload)
            if best_score is None or score > best_score:
                best_score = score
                best_payload = payload

            current_airport = graph.airports.get(current_airport_id)
            if current_airport is None:
                return

            for route in getattr(current_airport, "routes", []) or []:
                if not route.is_available:
                    continue

                destination = route.destination
                destination_id = destination.id
                if destination_id in visited:
                    continue

                if (
                    not include_secondary_airports
                    and not destination.es_hub
                    and destination_id != origin
                ):
                    continue

                aircraft_options = select_aircraft_options(route)
                if not aircraft_options:
                    continue

                for aircraft in aircraft_options:
                    segment_cost = route.calculate_cost(aircraft)
                    segment_time = route.calculate_time(aircraft)
                    segment_distance = route.distance_km

                    new_total_cost = total_cost + segment_cost
                    new_total_time = total_time + segment_time
                    if new_total_cost > max_budget or new_total_time > max_time:
                        continue

                    new_flights = flights.copy()
                    new_flights.append(
                        {
                            "origin": current_airport_id,
                            "destination": destination_id,
                            "distance": round(segment_distance, 2),
                            "time": round(segment_time, 2),
                            "cost": round(segment_cost, 2),
                            "aircraft_type": aircraft.name,
                            "cumulative_cost": round(new_total_cost, 2),
                            "cumulative_time": round(new_total_time, 2),
                        }
                    )

                    new_visited = set(visited)
                    new_visited.add(destination_id)
                    new_used_transports = set(used_transports)
                    new_used_transports.add(aircraft.name)

                    dfs(
                        current_airport_id=destination_id,
                        visited=new_visited,
                        flights=new_flights,
                        total_cost=new_total_cost,
                        total_time=new_total_time,
                        total_distance=total_distance + segment_distance,
                        used_transports=new_used_transports,
                    )

        dfs(
            current_airport_id=origin,
            visited={origin},
            flights=[],
            total_cost=0.0,
            total_time=0.0,
            total_distance=0.0,
            used_transports=set(),
        )

        if best_payload is None:
            return {
                "criterion": objective,
                "visited_airports": [origin],
                "total_destinations": 0,
                "flights": [],
                "total_distance": 0.0,
                "total_cost": 0.0,
                "total_time": 0.0,
                "constraints_met": {"budget": True, "time": True},
                "used_transport_types": [],
                "transport_requirement_met": False,
            }

        return best_payload