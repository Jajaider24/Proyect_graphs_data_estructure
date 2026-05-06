"""
Traveler module - Traveler state management.

This module contains the Traveler class used to track
the current state of the user during itinerary simulation.

The traveler object is the core component for:
    - Budget management
    - Time tracking
    - Airport traversal
    - Activities and jobs
    - Dynamic route planning
"""


class Traveler:
    """
    Represents the traveler during the simulation.

    This class stores the complete dynamic state
    of the traveler while exploring the airline network.

    The traveler state changes constantly during:
        - Flights
        - Activities
        - Jobs
        - Lodging
        - Food consumption

    This structure is essential for implementing:
        - DFS with constraints
        - Dynamic planning
        - Budget optimization
        - Final reporting
    """

    def __init__(
        self,
        current_airport=None,
        initial_budget=0,
        available_time=0
    ):
        """
        Initialize traveler state.

        Args:
            current_airport:
                Starting airport object.

            initial_budget (float):
                Initial available budget in USD.

            available_time (int):
                Total available travel time in minutes.
        """

        # Current airport where the traveler is located
        self.current_airport = current_airport

        # Initial budget never changes.
        # Used to calculate thresholds such as:
        # "35% remaining budget" for job activation.
        self.initial_budget = initial_budget

        # Current remaining budget.
        # This value changes during the simulation.
        self.current_budget = initial_budget

        # Total available time for the entire trip.
        self.available_time = available_time

        # Remaining travel time.
        # Reduced after flights, activities, jobs, etc.
        self.remaining_time = available_time

        # Airports already visited.
        # Used to avoid revisiting airports and cycles.
        self.visited_airports = []

        # Flight history.
        # Stores all route segments taken by the traveler.
        self.flight_history = []

        # Activities completed during the trip.
        # Includes optional and mandatory activities.
        self.activities_done = []

        # Jobs completed during the trip.
        # Used for dynamic budget management.
        self.jobs_done = []

        # Total accumulated expenses.
        self.total_spent = 0

        # Total accumulated earnings from jobs.
        self.total_earned = 0

        # Food tracking.
        # Used to determine when food consumption is required.
        self.hours_since_last_meal = 0

        # Lodging tracking.
        # Used to determine when accommodation is mandatory.
        self.hours_since_last_lodging = 0

    def visit_airport(self, airport):
        """
        Register an airport visit.

        Args:
            airport:
                Airport object being visited.
        """

        # Update current traveler location
        self.current_airport = airport

        # Prevent duplicate visits in history
        if airport.id not in self.visited_airports:
            self.visited_airports.append(airport.id)

    def spend_money(self, amount):
        """
        Reduce traveler budget.

        Args:
            amount (float):
                Expense amount in USD.
        """

        self.current_budget -= amount

        self.total_spent += amount

    def earn_money(self, amount):
        """
        Increase traveler budget from jobs.

        Args:
            amount (float):
                Earned amount in USD.
        """

        self.current_budget += amount

        self.total_earned += amount

    def consume_time(self, minutes):
        """
        Reduce remaining available time.

        Args:
            minutes (int):
                Time consumed in minutes.
        """

        self.remaining_time -= minutes

    def can_continue(self):
        """
        Check whether the traveler can continue the trip.

        Returns:
            bool:
                True if traveler still has budget and time.
        """

        return (
            self.current_budget > 0
            and self.remaining_time > 0
        )

    def budget_threshold_reached(self):
        """
        Check if traveler reached the minimum budget threshold.

        According to project requirements, jobs become
        available when the budget falls below 35%
        of the initial budget.

        Returns:
            bool:
                True if budget threshold is reached.
        """

        threshold = self.initial_budget * 0.35

        return self.current_budget <= threshold

    def __str__(self):
        """
        String representation of traveler state.
        Useful for debugging and reports.
        """

        return (
            f"Traveler("
            f"airport={self.current_airport.id if self.current_airport else 'None'}, "
            f"budget={self.current_budget}, "
            f"time={self.remaining_time}"
            f")"
        )
    def clone(self):
        """
        Create a deep copy of the traveler state.

        This method is essential for DFS (Depth-First Search (Búsqueda en Profundidad))  and backtracking
        algorithms where each exploration branch must
        maintain an independent traveler state.

        Returns:
            Traveler:
                Independent traveler copy.
        """

        cloned = self.__class__(
            current_airport=self.current_airport,
            initial_budget=self.initial_budget,
            available_time=self.available_time
        )

        cloned.current_budget = self.current_budget
        cloned.remaining_time = self.remaining_time

        cloned.visited_airports = self.visited_airports.copy()
        cloned.flight_history = self.flight_history.copy()
        cloned.activities_done = self.activities_done.copy()
        cloned.jobs_done = self.jobs_done.copy()

        cloned.total_spent = self.total_spent
        cloned.total_earned = self.total_earned

        cloned.hours_since_last_meal = self.hours_since_last_meal
        cloned.hours_since_last_lodging = self.hours_since_last_lodging

        return cloned
    