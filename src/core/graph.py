"""
Graph module - Airline graph implementation.

This module extends the academic graph structure
provided in class and adapts it for the airline
simulation project.

The graph uses:
    - Directed edges
    - Weighted routes
    - Adjacency lists

Why adjacency lists?
    Airline networks are sparse graphs where
    each airport connects to only a subset
    of all available airports.

    Adjacency lists are more memory-efficient
    and traversal-efficient for sparse graphs.
"""

from src.core.base_graph import Grafo


class Graph(Grafo):
    """
    Directed weighted airline graph.

    This class extends the academic Grafo structure
    while adding domain-specific airline behavior.

    Airports are stored:
        - In the academic vertex structure
        - In a fast-access dictionary
    """

    def __init__(self):
        """
        Initialize graph.
        """

        # Initialize academic graph structure
        super().__init__()

        # Fast airport lookup
        self.airports = {}

    def add_airport(self, airport):
        """
        Add airport to graph.

        Args:
            airport:
                Airport object.
        """

        # Add to project registry
        self.airports[airport.id] = airport

        # Add to academic graph structure
        self.agregar_vertice(airport)

    def add_route(self, route):
        """
        Add directed route to graph.

        Routes are stored:
            - In project adjacency lists
            - In academic adjacency lists

        Args:
            route:
                Route object.
        """

        # Project adjacency list
        route.origin.routes.append(route)

        # Academic adjacency list
        route.origin.agregar_adyacencia(route)

    def get_airport(self, airport_id):
        """
        Retrieve airport by ID.

        Args:
            airport_id (str):
                Airport IATA code.

        Returns:
            Airport:
                Matching airport object.
        """

        return self.airports.get(airport_id)

    def airport_exists(self, airport_id):
        """
        Check whether airport exists.

        Args:
            airport_id (str):
                Airport IATA code.

        Returns:
            bool:
                True if airport exists.
        """

        return airport_id in self.airports

    def get_all_airports(self):
        """
        Retrieve all airports.

        Returns:
            list:
                List of Airport objects.
        """

        return list(
            self.airports.values()
        )
    

    def update_all_weights(self, criterion):
        """
        Update all route weights dynamically.

        This method prepares the graph for:
            - Distance optimization
            - Cost optimization
            - Time optimization

        Args:
            criterion (str):
                Optimization criterion.
        """

        for airport in self.airports.values():

            for route in airport.routes:

                route.update_weight(
                    criterion
                )

    def print_graph(self):
        """
        Print graph structure.

        Useful for debugging and validation.
        """

        print(
            "\n===== AIRLINE NETWORK =====\n"
        )

        for airport in self.airports.values():

            print(f"{airport.id} ->")

            for route in airport.routes:

                print(
                    f"   {route.destination.id} | "
                    f"{route.distance_km} km"
                )

            print()

    def total_airports(self):
        """
        Retrieve total airport count.

        Returns:
            int:
                Number of airports.
        """

        return len(self.airports)

    def total_routes(self):
        """
        Retrieve total route count.

        Returns:
            int:
                Number of routes.
        """

        total = 0

        for airport in self.airports.values():

            total += len(
                airport.routes
            )

        return total

    def disable_route(
        self,
        origin_id,
        destination_id
    ):
        """
        Disable a route dynamically.
        """

        for route in self.airports[origin_id].routes:

            if (
                route.destination.id
                == destination_id
            ):

                route.is_available = False

    def enable_route(
        self,
        origin_id,
        destination_id
    ):
        """
        Enable a route dynamically.
        """

        for route in self.airports[origin_id].routes:

            if (
                route.destination.id
                == destination_id
            ):

                route.is_available = True