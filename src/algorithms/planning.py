"""
Planning module - Intelligent route planning algorithms.

This module contains advanced DFS and backtracking
algorithms used to solve:

    - Maximum destination exploration
    - Budget-constrained planning
    - Time-constrained planning
    - Dynamic route simulation

Main technique:
    DFS + Pruning + Backtracking
"""

from src.core.traveler import Traveler
from src.algorithms.dynamic_planning import (simulate_airport_stay, job_recommendation_engine)


def maximize_destinations(graph, start_airport_id, constraints):
    """
    Find the route that visits the maximum number
    of destinations under budget and time constraints.

    This algorithm uses:
        - DFS
        - Backtracking
        - Constraint pruning

    Worst-case Complexity:
        O(b^d)

    where:
        b = branching factor
        d = maximum search depth

    Args:
        graph:
            Graph object.

        start_airport_id (str):
            Starting airport ID.

        constraints:
            TripConstraints object.

    Returns:
        dict:
            Best route solution.
    """

    # -----------------------------------------
    # INITIALIZE TRAVELER
    # -----------------------------------------

    start_airport = graph.get_airport(start_airport_id)

    traveler = Traveler(current_airport=start_airport, initial_budget=constraints.max_budget, available_time=constraints.max_time)

    traveler.visit_airport(start_airport)

    # -----------------------------------------
    # BEST SOLUTION TRACKING
    # -----------------------------------------

    best_solution = {
        "visited_airports": [],
        "remaining_budget": 0,
        "remaining_time": 0,
        "total_destinations": 0,
        "jobs_completed": [],
        "activities_completed": [],
        "flight_history": []
    }

    # -----------------------------------------
    # DFS + BACKTRACKING
    # -----------------------------------------

    def dfs(current_airport, traveler_state):
        """
        Recursive DFS exploration.
        Args:
            current_airport:
                Current airport object.

            traveler_state:
                Traveler object.
        """
        nonlocal best_solution
        # -----------------------------------------
        # UPDATE BEST SOLUTION
        # -----------------------------------------

        current_total = len(traveler_state.visited_airports)

        if (current_total > best_solution["total_destinations"]):
            best_solution = {
                "visited_airports": traveler_state.visited_airports.copy(),
                "remaining_budget": traveler_state.current_budget,
                "remaining_time": traveler_state.remaining_time,
                "total_destinations": current_total,
                "jobs_completed": traveler_state.jobs_done.copy(),
                "activities_completed": traveler_state.activities_done.copy(),
                "flight_history": traveler_state.flight_history.copy()
            }

        # -----------------------------------------
        # EXPLORE ROUTES
        # -----------------------------------------

        for route in current_airport.routes:
            # Ignore blocked routes
            if not route.is_available:
                continue
            destination = (route.destination)

            # Avoid cycles
            if (destination.id in traveler_state.visited_airports):
                continue

            # Avoid hubs if requested
            if (constraints.avoid_hubs and destination.es_hub):
                continue

            # -----------------------------------------
            # SELECT BEST AIRCRAFT
            # -----------------------------------------
            best_aircraft = None
            best_cost = float("inf")

            for aircraft in (route.aircraft_options):
                # Aircraft restrictions
                if (constraints.allowed_aircraft and aircraft.name not in constraints.allowed_aircraft):
                    continue

                aircraft_cost = (route.calculate_cost(aircraft))

                if aircraft_cost < best_cost:
                    best_cost = aircraft_cost
                    best_aircraft = aircraft

            # No valid aircraft found
            if best_aircraft is None:
                continue

            # -----------------------------------------
            # CALCULATE ROUTE METRICS
            # -----------------------------------------

            route_cost = (route.calculate_cost(best_aircraft))

            route_time = (route.calculate_time(best_aircraft))

            # -----------------------------------------
            # CREATE NEW TRAVELER STATE
            # -----------------------------------------

            new_traveler = (traveler_state.clone())

            # Update traveler state
            new_traveler.visit_airport(destination)

            # -----------------------------------------
            # SIMULATE AIRPORT STAY
            # -----------------------------------------

            stay_summary = (simulate_airport_stay(destination, new_traveler,activity_limit=2))

            # -----------------------------------------
            # JOB RECOVERY SYSTEM
            # -----------------------------------------

            # If budget falls below threshold,
            # attempt to recover money through jobs.
            if (new_traveler.budget_threshold_reached()):
                job_recommendation_engine(airport=destination, traveler=new_traveler, available_hours=6)

            new_traveler.spend_money(route_cost)

            new_traveler.consume_time(route_time)

            # Store route history
            new_traveler.flight_history.append({
                "from": current_airport.id,
                "to": destination.id,
                "aircraft": best_aircraft.name,
                "cost": route_cost,
                "time":route_time
            })

            # -----------------------------------------
            # PRUNING
            # -----------------------------------------
            # Budget pruning
            if (new_traveler.current_budget < 0):
                continue

            # Time pruning
            if (new_traveler.remaining_time < 0):
                continue

            # Continue DFS exploration
            dfs(destination, new_traveler)

    # -----------------------------------------
    # START DFS
    # -----------------------------------------
    dfs(start_airport, traveler)
    return best_solution


def print_planning_summary(solution):
    """
    Print formatted planning solution.

    Args:
        solution (dict):
            Planning result dictionary.
    """
    print("\n===== TRIP PLANNING SUMMARY =====\n")
    print(
        f"Visited Airports: "
        f"{solution['total_destinations']}"
    )
    print()
    print("Route:")
    print(" -> ".join(solution["visited_airports"]))
    print()
    print(
        f"Remaining Budget: "
        f"${solution['remaining_budget']:.2f}"
    )
    print(
        f"Remaining Time: "
        f"{solution['remaining_time']:.2f} min"
    )
    print()
    print("===== FLIGHT HISTORY =====")

    for flight in (solution["flight_history"]):
        print(
            f"{flight['from']} -> "
            f"{flight['to']} | "
            f"{flight['aircraft']} | "
            f"${flight['cost']:.2f}"
        )
    print()
    print("===== ACTIVITIES =====")
    if not solution["activities_completed"]:
        print("No activities completed.")
    else:
        for activity in (solution["activities_completed"]):
            print(
                f"{activity['airport']} | "
                f"{activity['activity']}"
            )
    print()
    print("===== JOBS =====")
    if not solution["jobs_completed"]:
        print("No jobs completed.")
    else:
        for job in (solution["jobs_completed"]):
            print(
                f"{job['airport']} | "
                f"{job['job_name']} | "
                f"${job['earnings']:.2f}"
            )