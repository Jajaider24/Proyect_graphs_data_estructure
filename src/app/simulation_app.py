"""
Main simulation application.

This class orchestrates the complete system.
"""

from src.services.graph_service import (
    GraphService
)

from src.services.simulation_service import (
    SimulationService
)

from src.services.planning_service import (
    PlanningService
)

from src.services.report_service import (
    ReportService
)

from src.services.network_service import (
    NetworkService
)


class SimulationApp:
    """
    Main application orchestrator.
    """

    def __init__(self):
        """
        Initialize application services.
        """

        self.graph_service = (
            GraphService()
        )

        self.simulation_service = (
            SimulationService()
        )

        self.planning_service = (
            PlanningService()
        )

        self.report_service = (
            ReportService()
        )

        self.network_service = (
            NetworkService()
        )

    def run(self):
        """
        Execute complete simulation flow.
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
        # LOAD GRAPH
        # -----------------------------------------

        graph = (
            self.graph_service.load_graph(
                "data/sample_network.json"
            )
        )

        print(
            "✓ Graph loaded successfully"
        )

        print()

        # -----------------------------------------
        # BFS TEST
        # -----------------------------------------

        bfs_result = (
            self.simulation_service.run_bfs(
                graph,
                "BOG"
            )
        )

        print(
            "BFS:"
        )

        print(
            bfs_result
        )

        print()

        # -----------------------------------------
        # DFS TEST
        # -----------------------------------------

        dfs_result = (
            self.simulation_service.run_dfs(
                graph,
                "BOG"
            )
        )

        print(
            "DFS:"
        )

        print(
            dfs_result
        )

        print()

        self.network_service.block_route(
            graph,
            "BOG",
            "PTY"
        )

        # -----------------------------------------
        # DIJKSTRA TEST
        # -----------------------------------------

        result = (
            self.simulation_service
            .run_dijkstra(

                graph=
                    graph,

                origin=
                    "BOG",

                destination=
                    "MEX",

                optimization=
                    "cost"
            )
        )

        print(
            "Dijkstra Result:"
        )

        print(
            result
        )

        print()

        # -----------------------------------------
        # PLANNING TEST
        # -----------------------------------------

        solution = (
            self.planning_service
            .execute_planning(

                graph=
                    graph,

                origin=
                    "BOG",

                budget=
                    6000,

                available_time=
                    25000,
            )
        )

        print(
            "Planning Solution:"
        )

        print(
            solution
        )

        print()

        # -----------------------------------------
        # REPORTS
        # -----------------------------------------

        self.report_service.generate_graph_report(
            graph
        )

        self.report_service.generate_travel_report(
            solution
        )

        print(
            "\n========================================"
        )

        print(
            " ALL TESTS COMPLETED SUCCESSFULLY"
        )

        print(
            "========================================"
        )