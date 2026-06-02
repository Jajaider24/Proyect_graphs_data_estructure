"""Planning API routes for itinerary generation and route optimization."""

from __future__ import annotations

import heapq
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import APIRouter, HTTPException
from api.schemas import PlanningRequest, PathRequest, ItineraryResponse, PathResponse
from api.schemas import SessionCreateRequest, SessionOptionsResponse, DecisionRequest, SessionStateResponse, RouteInterruptionRequest
from src.services.graph_service import graph_service
from src.services.planning_service import PlanningService

router = APIRouter()

# Service instances
planning_service = PlanningService()

SUPPORTED_CRITERIA = {"distance", "cost", "time"}


def _all_transport_types(graph) -> Set[str]:
    values: Set[str] = set()
    for airport in graph.airports.values():
        for route in getattr(airport, "routes", []) or []:
            for aircraft in getattr(route, "aircraft_options", []) or []:
                values.add(aircraft.name)
    return values


def _segment_metrics(route, criterion: str, allowed_transports: Optional[Set[str]]) -> Optional[Tuple[float, Dict[str, Any]]]:
    candidates = []
    for aircraft in getattr(route, "aircraft_options", []) or []:
        if allowed_transports and aircraft.name not in allowed_transports:
            continue

        cost = route.calculate_cost(aircraft)
        time = route.calculate_time(aircraft)
        distance = route.distance_km

        if criterion == "distance":
            weight = distance
        elif criterion == "cost":
            weight = cost
        elif criterion == "time":
            weight = time
        else:
            raise ValueError(f"Invalid criterion: {criterion}")

        candidates.append(
            (
                weight,
                {
                    "distance": round(distance, 2),
                    "cost": round(cost, 2),
                    "time": round(time, 2),
                    "aircraft_type": aircraft.name,
                },
            )
        )

    if not candidates:
        return None

    candidates.sort(key=lambda value: value[0])
    return candidates[0]


def _dijkstra_with_filters(
    graph,
    start: str,
    end: str,
    criterion: str,
    include_secondary_airports: bool,
    transport_types: Optional[List[str]],
) -> Dict[str, Any]:
    if criterion not in SUPPORTED_CRITERIA:
        raise ValueError(f"Criterion '{criterion}' is not supported")

    if start not in graph.airports:
        raise ValueError(f"Airport {start} not found")
    if end not in graph.airports:
        raise ValueError(f"Airport {end} not found")

    allowed_transports = None
    if transport_types:
        all_types = _all_transport_types(graph)
        selected = {value for value in transport_types if value in all_types}
        if not selected:
            raise ValueError("None of the selected transport types exist in the graph")
        allowed_transports = selected

    distances: Dict[str, float] = {start: 0.0}
    predecessors: Dict[str, str] = {}
    queue: List[Tuple[float, str]] = [(0.0, start)]
    visited: Set[str] = set()

    while queue:
        current_distance, airport_id = heapq.heappop(queue)
        if airport_id in visited:
            continue
        visited.add(airport_id)

        if airport_id == end:
            break

        current_airport = graph.airports.get(airport_id)
        if current_airport is None:
            continue

        for route in getattr(current_airport, "routes", []) or []:
            if not route.is_available:
                continue

            destination = route.destination
            destination_id = destination.id

            if (
                not include_secondary_airports
                and not destination.es_hub
                and destination_id not in {start, end}
            ):
                continue

            segment = _segment_metrics(route, criterion, allowed_transports)
            if segment is None:
                continue

            weight, _metrics = segment
            new_distance = current_distance + weight

            if new_distance < distances.get(destination_id, float("inf")):
                distances[destination_id] = new_distance
                predecessors[destination_id] = airport_id
                heapq.heappush(queue, (new_distance, destination_id))

    if end not in distances:
        return {
            "criterion": criterion,
            "path": [],
            "distances": distances,
            "predecessors": predecessors,
            "total_distance": float("inf"),
            "total_cost": float("inf"),
            "total_time": float("inf"),
            "segments": [],
        }

    # Reconstruct path
    path = [end]
    while path[-1] != start:
        path.append(predecessors[path[-1]])
    path.reverse()

    segments: List[Dict[str, Any]] = []
    total_distance = 0.0
    total_cost = 0.0
    total_time = 0.0

    for index in range(len(path) - 1):
        origin_id = path[index]
        destination_id = path[index + 1]
        airport = graph.airports[origin_id]

        selected_route = None
        for route in getattr(airport, "routes", []) or []:
            if route.destination.id == destination_id and route.is_available:
                selected_route = route
                break

        if selected_route is None:
            continue

        segment = _segment_metrics(selected_route, criterion, allowed_transports)
        if segment is None:
            continue
        _, metrics = segment

        total_distance += metrics["distance"]
        total_cost += metrics["cost"]
        total_time += metrics["time"]

        segments.append(
            {
                "origin": origin_id,
                "destination": destination_id,
                "distance": metrics["distance"],
                "cost": metrics["cost"],
                "time": metrics["time"],
                "aircraft_type": metrics["aircraft_type"],
            }
        )

    return {
        "criterion": criterion,
        "path": path,
        "distances": distances,
        "predecessors": predecessors,
        "total_distance": round(total_distance, 2),
        "total_cost": round(total_cost, 2),
        "total_time": round(total_time, 2),
        "segments": segments,
    }


@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: PlanningRequest):
    """
    Generate an optimized itinerary based on constraints.
    
    Args:
        request: Planning request with origin, budget, and time
    
    Returns:
        Itinerary with flights and constraints validation
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        available_time_minutes = request.available_time * 60

        # Execute planning alternatives
        result = planning_service.execute_planning(
            graph=graph,
            origin=request.origin,
            budget=request.budget,
            available_time_minutes=available_time_minutes,
            preferred_transports=request.preferred_transports,
            include_secondary_airports=request.include_secondary_airports,
        )

        # Keep backward-compatible top-level summary using budget alternative
        main_alt = result["alternatives"].get("max_destinations_budget", {})
        flights = main_alt.get("flights", [])
        return ItineraryResponse(
            origin=request.origin,
            required_transport_types=result.get("required_transport_types", []),
            alternatives=result.get("alternatives", {}),
            flights=flights,
            total_distance=main_alt.get("total_distance", 0),
            total_time=main_alt.get("total_time", 0),
            total_cost=main_alt.get("total_cost", 0),
            number_of_stops=len(flights),
            feasible=bool(main_alt.get("constraints_met", {}).get("budget", True) and main_alt.get("constraints_met", {}).get("time", True)),
            constraints_met=main_alt.get("constraints_met", {}),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/shortest-path", response_model=PathResponse)
async def calculate_shortest_path(request: PathRequest):
    """
    Calculate shortest path between two airports.
    
    Args:
        request: Path request with start, end, and criterion
    
    Returns:
        Path with distances and total cost
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        selected_criteria = request.criteria or [request.criterion]
        selected_criteria = [value for value in selected_criteria if value]
        if not selected_criteria:
            selected_criteria = ["distance"]

        results_by_criterion: Dict[str, Any] = {}
        for criterion in selected_criteria:
            results_by_criterion[criterion] = _dijkstra_with_filters(
                graph=graph,
                start=request.start,
                end=request.end,
                criterion=criterion,
                include_secondary_airports=request.include_secondary_airports,
                transport_types=request.transport_types,
            )

        primary = results_by_criterion[selected_criteria[0]]

        return PathResponse(
            criterion=primary.get("criterion"),
            path=primary.get("path", []),
            distances=primary.get("distances", {}),
            predecessors=primary.get("predecessors", {}),
            total_distance=primary.get("total_distance", float("inf")),
            total_cost=primary.get("total_cost", float("inf")),
            total_time=primary.get("total_time", float("inf")),
            segments=primary.get("segments", []),
            results_by_criterion=results_by_criterion,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-routes")
async def compare_routes(
    start: str,
    end: str,
    criteria: str = "distance,cost,time",
    include_secondary_airports: bool = True,
    transport_types: str = "",
):
    """
    Compare routes by different criteria (distance, cost, time).
    
    Args:
        start: Starting airport
        end: Destination airport
    
    Returns:
        Dictionary with paths for each criterion
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        criteria_list = [value.strip() for value in criteria.split(",") if value.strip()]
        if not criteria_list:
            criteria_list = ["distance", "cost", "time"]

        transport_list = [value.strip() for value in transport_types.split(",") if value.strip()]

        results = {}
        for criterion in criteria_list:
            try:
                outcome = _dijkstra_with_filters(
                    graph=graph,
                    start=start,
                    end=end,
                    criterion=criterion,
                    include_secondary_airports=include_secondary_airports,
                    transport_types=transport_list,
                )
                results[criterion] = {
                    "path": outcome.get("path", []),
                    "total_value": outcome.get(f"total_{criterion}") if criterion in {"distance", "cost", "time"} else None,
                    "total_distance": outcome.get("total_distance"),
                    "total_cost": outcome.get("total_cost"),
                    "total_time": outcome.get("total_time"),
                    "segments": outcome.get("segments", []),
                }
            except Exception as e:
                results[criterion] = {"error": str(e)}

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session", response_model=SessionStateResponse)
async def create_session(request: SessionCreateRequest):
    try:
        graph = graph_service.get_graph()
        if not graph:
            raise HTTPException(status_code=400, detail="Graph not loaded. Call /graph/load first.")

        session = planning_service.create_session(
            graph=graph,
            origin=request.origin,
            initial_budget=request.initial_budget,
            available_time_minutes=request.available_time_hours * 60,
            preferred_transports=request.preferred_transports,
            include_secondary_airports=request.include_secondary_airports,
        )

        # Return initial state including session_id so frontend can continue interactive flow
        state = session.get("state", {})
        session_id = session.get("session_id")
        # session.get_state() may include its own session_id; avoid duplicate keys
        if isinstance(state, dict) and "session_id" in state:
            state = dict(state)
            state.pop("session_id", None)
        return SessionStateResponse(session_id=session_id, **(state or {}))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/options", response_model=SessionOptionsResponse)
async def get_session_options(session_id: str):
    try:
        options = planning_service.get_session_options(session_id)
        # options includes traveler_state which matches SessionStateResponse
        return SessionOptionsResponse(
            flights=options.get("flights", []),
            activities=options.get("activities", []),
            jobs=options.get("jobs", []),
            lodging_required=options.get("lodging_required", False),
            meal_required=options.get("meal_required", False),
            pending_min_stay_minutes=options.get("pending_min_stay_minutes", 0),
            can_take_flight=options.get("can_take_flight", True),
            traveler_state=options.get("traveler_state", {}),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        result = planning_service.apply_session_decision(session_id, decision.dict())
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
@router.get("/session/{session_id}/state", response_model=SessionStateResponse)
async def get_session_state(session_id: str):
    try:
        state = planning_service.get_session_state(session_id)
        return SessionStateResponse(**state)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/session/interrupt-route")
async def interrupt_route(request: RouteInterruptionRequest):
    """Interrupt a route and propagate impacts to active sessions."""
    try:
        origin_id = request.origin_id or request.origin
        destination_id = request.destination_id or request.destination
        return planning_service.interrupt_route(
            origin_id=origin_id,
            destination_id=destination_id,
            session_id=request.session_id,
            reason=request.reason or "Interrupcion operativa",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/report")
async def get_session_report(session_id: str):
    """Return final/detailed report for the interactive planning session."""
    try:
        return planning_service.get_session_report(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
