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