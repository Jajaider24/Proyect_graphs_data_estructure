"""
Planning service layer.

This service centralizes:
    - DFS planning
    - Constraint creation
    - Planning orchestration
"""

from src.algorithms.planning import (
    maximize_destinations
)

from src.core.constraints import (
    TripConstraints
)


class PlanningService:
    """
    Planning orchestration service.
    """

    def execute_planning(
        self,
        graph,
        origin,
        budget,
        available_time
    ):
        """
        Execute DFS itinerary planning.

        Args:
            graph:
                Graph instance.

            origin (str):
                Starting airport.

            budget (float):
                Maximum budget.

            available_time (float):
                Available time in minutes.

        Returns:
            dict:
                Planning solution.
        """

        # -----------------------------------------
        # CREATE CONSTRAINTS
        # -----------------------------------------

        constraints = TripConstraints(

            max_budget=
                budget,

            max_time=
                available_time
        )

        # -----------------------------------------
        # EXECUTE DFS PLANNING
        # -----------------------------------------

        solution = (
            maximize_destinations(

                graph,

                origin,

                constraints
            )
        )

        return solution