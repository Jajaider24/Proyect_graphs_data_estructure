"""
Route module - Route and aircraft domain models.

This module contains the structures used to represent:
    - Directed airline routes
    - Aircraft options
    - Dynamic route behavior
"""


class AircraftOption:
    """
    Represents an aircraft option available for a route.

    Each aircraft has:
        - Operational cost
        - Speed
        - Fixed boarding time

    This allows realistic multicriteria optimization.
    """
    def __init__(self, name, cost_per_km, speed_kmh, fixed_time_min):
        """
        Initialize aircraft option.

        Args:
            name (str):
                Aircraft type name.

            cost_per_km (float):
                Operational cost per kilometer.

            speed_kmh (float):
                Aircraft speed in km/h.

            fixed_time_min (float):
                Boarding + airport fixed time.
        """
        self.name = name
        self.cost_per_km = cost_per_km
        self.speed_kmh = speed_kmh
        self.fixed_time_min = fixed_time_min

    def calculate_time(self, distance_km):
        """
        Calculate flight duration.

        Formula:
            time = flight_time + fixed_time

        Returns:
            float:
                Duration in minutes.
        """
        # Convert hours to minutes
        flight_time = (distance_km / self.speed_kmh) * 60
        return (flight_time + self.fixed_time_min)

    def __str__(self):
        """
        String representation.
        """
        return (
            f"{self.name} | "
            f"Cost/km={self.cost_per_km} | "
            f"Speed={self.speed_kmh} km/h"
        )


class Route:
    """
    Represents a directed route between two airports.
    The route stores:
        - Distance
        - Aircraft options
        - Dynamic restrictions
        - Route state
    """
    def __init__(self, origin, destination, distance_km, is_available=True):
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

        # Airport references
        self.origin = origin
        self.destination = destination

        # Distance metric
        self.distance_km = distance_km
        self.peso = distance_km

        # Current optimization criterion
        self.criterion = "distance"

        # Aircraft available for this route
        self.aircraft_options = []

        # Dynamic route state
        self._is_available = is_available

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
        self.aircraft_options.append(aircraft_option)

    @property
    def is_available(self):
        """Return whether the route is currently operational."""
        return self._is_available

    @is_available.setter
    def is_available(self, value):
        self._is_available = bool(value)

    @property
    def blocked(self):
        """Compatibility alias for code that still uses blocked."""
        return not self._is_available

    @blocked.setter
    def blocked(self, value):
        self._is_available = not bool(value)

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
        return (self.distance_km * aircraft_option.cost_per_km)

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
        return aircraft_option.calculate_time(self.distance_km)

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
        normalized_criterion = str(criterion).strip().lower()
        self.criterion = normalized_criterion
        if normalized_criterion == "distance":
            self.peso = self.distance_km
            return
        
        if not self.aircraft_options:
            raise ValueError(
                f"Route {self.origin.id} -> {self.destination.id} has no aircraft options for '{normalized_criterion}' optimization"
            )

        metric_getters = {
            "cost": self.calculate_cost,
            "time": self.calculate_time,
        }

        metric_getter = metric_getters.get(normalized_criterion)
        if metric_getter is None:
            raise ValueError(
                f"Invalid criterion: {criterion}"
            )

        self.peso = min(
            metric_getter(aircraft)
            for aircraft in self.aircraft_options
        )

    def getDestino(self):
        """Retrieve destination airport."""
        return self.destination

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