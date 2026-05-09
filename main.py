"""
Main module - Airline graph simulation tests.

This file is used to validate:
    - JSON loading
    - Graph construction
    - BFS traversal
    - DFS traversal
    - Dijkstra shortest path
    - Multi-criteria optimization

This module acts as the testing environment
before integrating the graphical interface.
"""

from src.utils.json_loader import (
    load_network_from_json,
    build_graph_from_json
)

from src.algorithms.traversal import (
    breadth_first_search,
    depth_first_search
)

from src.algorithms.shortestpath import (
    dijkstra_shortest_path,
    reconstruct_route_details,
    print_route_summary
)

from src.core.constraints import (
    TripConstraints
)

from src.algorithms.planning import (
    maximize_destinations,
    print_planning_summary
)

from src.core.traveler import (
    Traveler
)

from src.algorithms.dynamic_planning import (
    job_recommendation_engine,
    print_job_summary
)

from src.algorithms.dynamic_planning import (
    simulate_airport_stay,
    print_stay_summary
)


def main():
    """
    Main execution function.
    """

    print(
        "\n========================================"
    )

    print(
        " AIRLINE GRAPH SIMULATION PROJECT"
    )

    print(
        "========================================\n"
    )

    # -----------------------------------------
    # LOAD JSON DATA
    # -----------------------------------------

    print("Loading JSON data...\n")

    data = load_network_from_json(
        "data/sample_network.json"
    )

    # -----------------------------------------
    # BUILD GRAPH
    # -----------------------------------------

    print("\nBuilding graph...\n")

    graph = build_graph_from_json(data)

    # -----------------------------------------
    # PRINT GRAPH STRUCTURE
    # -----------------------------------------

    print("\nPrinting graph structure...\n")

    graph.print_graph()

    # -----------------------------------------
    # BFS TEST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " BFS TEST"
    )

    print(
        "========================================"
    )

    bfs_result = breadth_first_search(
        graph,
        "BOG"
    )

    print("\nBFS Traversal Order:")

    print(bfs_result)

    # -----------------------------------------
    # DFS TEST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " DFS TEST"
    )

    print(
        "========================================"
    )

    dfs_result = depth_first_search(
        graph,
        "BOG"
    )

    print("\nDFS Traversal Order:")

    print(dfs_result)

    # -----------------------------------------
    # DIJKSTRA TEST - DISTANCE
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " DIJKSTRA TEST - DISTANCE"
    )

    print(
        "========================================"
    )

    distances, predecessors, path = (
        dijkstra_shortest_path(
            graph,
            "BOG",
            "MEX",
            criterion="distance"
        )
    )

    print("\nOptimal Path:")

    print(path)

    summary = reconstruct_route_details(
        graph,
        path,
        criterion="distance"
    )

    print_route_summary(summary)

    # -----------------------------------------
    # DIJKSTRA TEST - COST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " DIJKSTRA TEST - COST"
    )

    print(
        "========================================"
    )

    distances, predecessors, path = (
        dijkstra_shortest_path(
            graph,
            "BOG",
            "MEX",
            criterion="cost"
        )
    )

    print("\nOptimal Path:")

    print(path)

    summary = reconstruct_route_details(
        graph,
        path,
        criterion="cost"
    )

    print_route_summary(summary)

    # -----------------------------------------
    # DIJKSTRA TEST - TIME
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " DIJKSTRA TEST - TIME"
    )

    print(
        "========================================"
    )

    distances, predecessors, path = (
        dijkstra_shortest_path(
            graph,
            "BOG",
            "MEX",
            criterion="time"
        )
    )

    print("\nOptimal Path:")

    print(path)

    summary = reconstruct_route_details(
        graph,
        path,
        criterion="time"
    )

    print_route_summary(summary)

    # -----------------------------------------
    # DFS PLANNING TEST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " DFS PLANNING TEST"
    )

    print(
        "========================================"
    )

    constraints = TripConstraints(

        max_budget=3000,

        max_time=10000,

        allowed_aircraft=[],

        avoid_hubs=False
    )

    solution = maximize_destinations(

        graph,

        "BOG",

        constraints
    )

    print_planning_summary(
        solution
    )

        # -----------------------------------------
    # JOB SIMULATION TEST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " JOB SIMULATION TEST"
    )

    print(
        "========================================"
    )

    # Create traveler with low budget
    traveler = Traveler(

        current_airport=
            graph.get_airport("BOG"),

        initial_budget=1000,

        available_time=5000
    )

    # Force threshold activation
    traveler.current_budget = 300

    result = job_recommendation_engine(

        airport=
            graph.get_airport("BOG"),

        traveler=traveler,

        available_hours=6
    )

    print_job_summary(result)

        # -----------------------------------------
    # AIRPORT STAY TEST
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " AIRPORT STAY TEST"
    )

    print(
        "========================================"
    )

    traveler = Traveler(

        current_airport=
            graph.get_airport("LIM"),

        initial_budget=2000,

        available_time=8000
    )

    stay_summary = simulate_airport_stay(

        airport=
            graph.get_airport("LIM"),

        traveler=traveler,

        activity_limit=2
    )

    print_stay_summary(
        stay_summary
    )

    print()

    print(
        f"Traveler Remaining Budget: "
        f"${traveler.current_budget:.2f}"
    )

    print(
        f"Traveler Remaining Time: "
        f"{traveler.remaining_time:.2f} min"
    )


    # -----------------------------------------
    # FINAL MESSAGE
    # -----------------------------------------

    print(
        "\n========================================"
    )

    print(
        " ALL TESTS COMPLETED SUCCESSFULLY"
    )

    print(
        "========================================\n"
    )


if __name__ == "__main__":
    
 main()