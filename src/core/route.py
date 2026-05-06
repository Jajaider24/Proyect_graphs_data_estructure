"""
Route module - Route and aircraft domain models.

This module contains the structures used to represent:
    - Directed airline routes
    - Aircraft options
    - Dynamic route behavior

The classes extend the academic graph structures
provided during class lectures.
"""

from src.core.base_graph import Arista


class AircraftOption:
    """
    Represents an aircraft option available for a route.

    Each route can support multiple aircraft types
    with different operational costs and durations.

    Example:
        - Commercial aircraft
        - Regional aircraft
        - Helicopter aircraft
    """

    def __init__(
        self,
        name,
        cost_per_km,
        time_per_km
    ):
        """
        Initialize aircraft option.

        Args:
            name (str):
                Aircraft type name.

            cost_per_km (float):
                Operational cost per kilometer.

            time_per_km (float):
                Flight duration in minutes per kilometer.
        """

        self.name = name

        self.cost_per_km = cost_per_km

        self.time_per_km = time_per_km

    def __str__(self):
        """
        String representation of aircraft option.
        """

        return (
            f"{self.name} | "
            f"Cost/km={self.cost_per_km} | "
            f"Time/km={self.time_per_km}"
        )


class Route(Arista):
    """
    Represents a directed route between two airports.

    This class extends the academic Arista structure
    while adding domain-specific airline functionality.

    The route stores:
        - Distance
        - Aircraft options
        - Dynamic restrictions
        - Route state
    """

    def __init__(
        self,
        origin,
        destination,
        distance_km
    ):
        """
        Initialize route.

        Args:
            origin:
                Origin airport object.

            destination:
                Destination airport object.

            distance_km (float):
                Distance between airports in kilometers.
        """

        # Initialize academic edge structure
        super().__init__(
            destination,
            distance_km
        )

        # Airport references
        self.origin = origin
        self.destination = destination

        # Distance metric
        self.distance_km = distance_km

        # Academic weight compatibility
        self.peso = distance_km

        # Current optimization criterion
        self.criterion = "distance"

        # Aircraft available for this route
        self.aircraft_options = []

        # Dynamic route state
        self.blocked = False

        # Subsidized route support
        self.subsidized = False

        # Minimum destination stay time
        self.min_stay = 0

    def add_aircraft_option(self, aircraft_option):
        """
        Add aircraft option to route.

        Args:
            aircraft_option:
                AircraftOption object.
        """

        self.aircraft_options.append(
            aircraft_option
        )

    def is_available(self):
        """
        Check whether route is available.

        Returns:
            bool:
                True if route is operational.
        """

        return not self.blocked

    def calculate_cost(self, aircraft_option):
        """
        Calculate route cost using selected aircraft.

        Args:
            aircraft_option:
                AircraftOption object.

        Returns:
            float:
                Total route cost.
        """

        return (
            self.distance_km
            * aircraft_option.cost_per_km
        )

    def calculate_time(self, aircraft_option):
        """
        Calculate route duration using selected aircraft.

        Args:
            aircraft_option:
                AircraftOption object.

        Returns:
            float:
                Flight duration in minutes.
        """

        return (
            self.distance_km
            * aircraft_option.time_per_km
        )

    def update_weight(self, criterion):
        """
        Update academic edge weight dynamically.

        This method allows compatibility with the
        professor's Dijkstra implementation.

        Args:
            criterion (str):
                Optimization criterion:
                    - distance
                    - cost
                    - time
        """

        self.criterion = criterion

        # DISTANCE OPTIMIZATION
        if criterion == "distance":

            self.peso = self.distance_km

        # COST OPTIMIZATION
        elif criterion == "cost":

            best_cost = min(

                self.calculate_cost(aircraft)

                for aircraft in self.aircraft_options
            )

            self.peso = best_cost

        # TIME OPTIMIZATION
        elif criterion == "time":

            best_time = min(

                self.calculate_time(aircraft)

                for aircraft in self.aircraft_options
            )

            self.peso = best_time

        else:

            raise ValueError(
                f"Invalid criterion: {criterion}"
            )

    def getPeso(self):
        """
        Retrieve current route weight.

        Used by the professor's Dijkstra implementation.

        Returns:
            float:
                Current route weight.
        """

        return self.peso

    def __str__(self):
        """
        String representation of route.
        """

        return (
            f"{self.origin.id} -> "
            f"{self.destination.id} "
            f"({self.distance_km} km)"
        )