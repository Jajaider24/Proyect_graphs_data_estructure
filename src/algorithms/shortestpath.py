"""
Shortest path algorithms module.

This module contains path optimization algorithms
used in the airline network simulation project.

Implemented algorithms:
    - Dijkstra shortest path
    - Dynamic route recalculation
    - Multi-criteria optimization

The implementation reuses the academic graph
algorithms provided during class lectures while
extending them for real-world airline simulation.
"""


def dijkstra_shortest_path(
    graph,
    start_id,
    end_id,
    criterion="distance"
):
    """
    Find shortest path using Dijkstra's algorithm.

    This function dynamically updates all route
    weights depending on the selected optimization
    criterion before executing the professor's
    Dijkstra implementation.

    Supported criteria:
        - distance
        - cost
        - time

    Time Complexity:
        O((V + E) log V)

    Args:
        graph:
            Graph object.

        start_id (str):
            Starting airport ID.

        end_id (str):
            Destination airport ID.

        criterion (str):
            Optimization criterion.

    Returns:
        tuple:
            (
                distances,
                predecessors,
                path
            )
    """

    # -----------------------------------------
    # UPDATE GRAPH WEIGHTS
    # -----------------------------------------

    # Update all route weights dynamically.
    #
    # Example:
    #   distance -> kilometers
    #   cost     -> USD
    #   time     -> minutes
    #
    # This allows compatibility with the
    # professor's Dijkstra implementation,
    # which expects static edge weights.
    graph.update_all_weights(
        criterion
    )

    # -----------------------------------------
    # EXECUTE DIJKSTRA
    # -----------------------------------------

    # Reuse academic implementation
    distances, predecessors, path = (
        graph.dijkstra_simple(
            graph,
            start_id,
            end_id
        )
    )

    return (
        distances,
        predecessors,
        path
    )


def reconstruct_route_details(
    graph,
    path,
    criterion="distance"
):
    """
    Reconstruct detailed route information.

    Generates human-readable route information
    including:
        - Selected aircraft
        - Route cost
        - Route duration
        - Route distance

    Args:
        graph:
            Graph object.

        path (list):
            List of airport IDs.

        criterion (str):
            Optimization criterion.

    Returns:
        dict:
            Detailed route information.
    """

    route_details = []

    total_distance = 0
    total_cost = 0
    total_time = 0

    # -----------------------------------------
    # PROCESS EACH ROUTE SEGMENT
    # -----------------------------------------

    for i in range(len(path) - 1):

        current_airport = graph.get_airport(
            path[i]
        )

        next_airport_id = path[i + 1]

        selected_route = None

        # Find matching route
        for route in current_airport.routes:
            if not route.is_available:
                continue

            if (
                route.destination.id
                == next_airport_id
            ):

                selected_route = route

                break

        if selected_route is None:
            continue

        # -----------------------------------------
        # SELECT BEST AIRCRAFT
        # -----------------------------------------

        best_aircraft = None

        best_value = float("inf")

        for aircraft in (
            selected_route.aircraft_options
        ):

            # DISTANCE
            if criterion == "distance":

                value = (
                    selected_route.distance_km
                )

            # COST
            elif criterion == "cost":

                value = (
                    selected_route.calculate_cost(
                        aircraft
                    )
                )

            # TIME
            elif criterion == "time":

                value = (
                    selected_route.calculate_time(
                        aircraft
                    )
                )

            else:

                raise ValueError(
                    f"Invalid criterion: {criterion}"
                )

            # Keep best aircraft
            if value < best_value:

                best_value = value

                best_aircraft = aircraft

        # -----------------------------------------
        # CALCULATE ROUTE METRICS
        # -----------------------------------------

        route_distance = (
            selected_route.distance_km
        )

        route_cost = (
            selected_route.calculate_cost(
                best_aircraft
            )
        )

        route_time = (
            selected_route.calculate_time(
                best_aircraft
            )
        )

        # Accumulate totals
        total_distance += route_distance

        total_cost += route_cost

        total_time += route_time

        # Store segment details
        route_details.append({

            "from": selected_route.origin.id,

            "to": selected_route.destination.id,

            "distance_km": route_distance,

            "cost_usd": route_cost,

            "time_min": route_time,

            "aircraft": best_aircraft.name
        })

    # -----------------------------------------
    # RETURN COMPLETE SUMMARY
    # -----------------------------------------

    return {

        "path": path,

        "criterion": criterion,

        "segments": route_details,

        "total_distance": total_distance,

        "total_cost": total_cost,

        "total_time": total_time
    }


def print_route_summary(route_summary):
    """
    Print formatted route summary.

    Args:
        route_summary (dict):
            Route summary dictionary.
    """

    print(
        "\n===== ROUTE SUMMARY =====\n"
    )

    print(
        f"Optimization: "
        f"{route_summary['criterion']}"
    )

    print(
        f"Path: "
        f"{' -> '.join(route_summary['path'])}"
    )

    print()

    # Print segments
    for segment in route_summary["segments"]:

        print(
            f"{segment['from']} -> "
            f"{segment['to']}"
        )

        print(
            f"   Aircraft: "
            f"{segment['aircraft']}"
        )

        print(
            f"   Distance: "
            f"{segment['distance_km']} km"
        )

        print(
            f"   Cost: "
            f"${segment['cost_usd']:.2f}"
        )

        print(
            f"   Time: "
            f"{segment['time_min']:.2f} min"
        )

        print()

    # Print totals
    print(
        "===== TOTALS ====="
    )

    print(
        f"Total Distance: "
        f"{route_summary['total_distance']} km"
    )

    print(
        f"Total Cost: "
        f"${route_summary['total_cost']:.2f}"
    )

    print(
        f"Total Time: "
        f"{route_summary['total_time']:.2f} min"
    )


def recalculate_route_on_disruption(
    graph,
    start_id,
    end_id,
    blocked_route,
    criterion="distance"
):
    """
    Recalculate route after disruption.

    Simulates route interruption events such as:
        - Weather conditions
        - Airport closure
        - Aircraft malfunction
        - Air traffic restrictions

    Args:
        graph:
            Graph object.

        start_id (str):
            Current airport ID.

        end_id (str):
            Destination airport ID.

        blocked_route:
            Route object to block.

        criterion (str):
            Optimization criterion.

    Returns:
        tuple:
            New recalculated path.
    """

    # -----------------------------------------
    # BLOCK ROUTE
    # -----------------------------------------

    blocked_route.blocked = True

    print(
        f"\n⚠ Route blocked: "
        f"{blocked_route.origin.id} -> "
        f"{blocked_route.destination.id}"
    )

    # -----------------------------------------
    # RECALCULATE NEW ROUTE
    # -----------------------------------------

    return dijkstra_shortest_path(
        graph,
        start_id,
        end_id,
        criterion
    )