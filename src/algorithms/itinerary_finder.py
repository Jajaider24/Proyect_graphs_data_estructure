"""DFS algorithm for finding the best travel itinerary based on budget, time and transportation requirements."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple


def find_best_itinerary(graph: Any, origin: str, max_budget: float, max_time: float, allowed_transports: Set[str],
    required_transports: Set[str], include_secondary_airports: bool, objective: str,) -> Dict[str, Any]:
    """Generate the best itinerary option under given constraints.

    Alternatives:
    - maximize destinations under budget
    - maximize destinations under time
    """
    best_payload: Optional[Dict[str, Any]] = None
    best_score: Optional[Tuple[int, int, int, float, float]] = None

    def evaluate_candidate(payload: Dict[str, Any]) -> Tuple[int, int, int, float, float]:
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

    def select_aircraft_options(route: Any) -> List[Any]:
        options = [a for a in route.aircraft_options if a.name in allowed_transports]
        if objective == "budget":
            options.sort(key=lambda a: (route.calculate_cost(a), route.calculate_time(a)))
        else:
            options.sort(key=lambda a: (route.calculate_time(a), route.calculate_cost(a)))
        return options

    def dfs(current_airport_id: str, visited: Set[str], flights: List[Dict[str, Any]],
        total_cost: float, total_time: float, total_distance: float, used_transports: Set[str],):
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

            if (not include_secondary_airports and not destination.es_hub and destination_id != origin):
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