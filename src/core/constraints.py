"""
Constraints module - Trip restriction management.

This module contains the structures used to define
travel restrictions and optimization limits.
"""


class TripConstraints:
    """
    Represents all trip restrictions used during
    route planning and simulation.

    Constraints are used by DFS and backtracking
    algorithms to prune invalid exploration branches.
    """

    def __init__(
        self,
        max_budget,
        max_time,
        allowed_aircraft=None,
        avoid_hubs=False
    ):
        """
        Initialize trip constraints.

        Args:
            max_budget (float):
                Maximum available budget.

            max_time (int):
                Maximum available travel time.

            allowed_aircraft (list):
                Allowed aircraft types.

            avoid_hubs (bool):
                Whether hub airports should be avoided.
        """

        # Maximum travel budget
        self.max_budget = max_budget

        # Maximum travel time
        self.max_time = max_time

        # Aircraft restrictions
        self.allowed_aircraft = (
            allowed_aircraft or []
        )

        # Hub avoidance flag
        self.avoid_hubs = avoid_hubs