"""
Route module - Route and aircraft data models.

Classes:
    - Route: Represents a flight route between two airports
    - Aircraft: Represents an aircraft type with cost and time parameters
"""


class Aircraft:
    """
    Represents an aircraft type with its operational parameters.
    Includes cost per km and time per km values.
    """
    def __init__(self, name, cost_per_km=0, time_per_km=0):
        """
        Initialize an aircraft type.
        
        Args:
            name: Name of aircraft type (Commercial, Regional, Helicopter)
            cost_per_km: Cost in USD per kilometer
            time_per_km: Time in minutes per kilometer
        """
        self.name = name
        self.cost_per_km = cost_per_km
        self.time_per_km = time_per_km


class Route:
    """
    Represents a directed flight route between two airports.
    Stores distance, available aircraft, and cost information.
    """
    def __init__(self, origin, destination, distance_km, aircraft_types=None, cost_base=None, min_stay=0):
        """
        Initialize a route.
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            distance_km: Distance in kilometers
            aircraft_types: List of available aircraft types
            cost_base: Base cost (0 if subsidized)
            min_stay: Minimum stay time in minutes
        """
        self.origin = origin
        self.destination = destination
        self.distance_km = distance_km
        self.aircraft_types = aircraft_types if aircraft_types else []
        self.cost_base = cost_base
        self.min_stay = min_stay
