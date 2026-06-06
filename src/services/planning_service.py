"""Planning service layer for itinerary alternatives and constraints."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Set
import uuid
from src.core.traveler import Traveler
from src.algorithms.itinerary_finder import find_best_itinerary
from src.services.planning_session import PlanningSession


class PlanningService:
    """Planning orchestration service."""
    def __init__(self):
        # In-memory session store: session_id -> PlanningSession
        self.sessions: Dict[str, PlanningSession] = {}
    def execute_planning(self, graph: Any, origin: str, budget: float, available_time_minutes: float,
        preferred_transports: Optional[List[str]] = None, include_secondary_airports: bool = True,) -> Dict[str, Any]:
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

        budget_alternative = find_best_itinerary(
            graph=graph,
            origin=origin,
            max_budget=budget,
            max_time=available_time_minutes,
            allowed_transports=set(allowed_transports),
            required_transports=required_transports,
            include_secondary_airports=include_secondary_airports,
            objective="budget",
        )

        time_alternative = find_best_itinerary(
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

    def _collect_transport_types(self, graph: Any) -> Set[str]:
        transport_types: Set[str] = set()
        for airport in graph.airports.values():
            for route in getattr(airport, "routes", []) or []:
                for aircraft in getattr(route, "aircraft_options", []) or []:
                    transport_types.add(aircraft.name)
        return transport_types

    def create_session(self, graph: Any, origin: str, initial_budget: float, available_time_minutes: float,
        preferred_transports: Optional[List[str]] = None, include_secondary_airports: bool = True,) -> Dict[str, Any]:
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

    def get_session_options(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.get_options()

    def apply_session_decision(self, session_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.apply_decision(decision)

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.get_state()

    def interrupt_route(self, origin_id: Optional[str] = None, destination_id: Optional[str] = None,
        session_id: Optional[str] = None, reason: str = "Interrupcion operativa",) -> Dict[str, Any]:
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

# Re-export PlanningSession for backward compatibility
__all__ = ["PlanningService", "PlanningSession"]