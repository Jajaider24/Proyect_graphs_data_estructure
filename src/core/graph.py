"""
Graph module - Airline graph implementation.

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

import heapq
import math


class Graph:
    """
    Directed weighted airline graph.

    Airports are stored:
        - In a fast-access dictionary
    """

    def __init__(self):
        """
        Initialize graph.
        """

        self.vertices = {}
        self.airports = self.vertices

    def agregar_vertice(self, vertice):
        """Add vertex to graph."""

        self.vertices[vertice.id] = vertice

    def obtener_vertice(self, identificador):
        """Retrieve vertex by ID."""

        return self.vertices.get(identificador)

    def reset_visits(self):
        """Reset traversal state for all vertices."""

        for vertice in self.vertices.values():
            if hasattr(vertice, "visitado"):
                vertice.visitado = False

    def add_airport(self, airport):
        """
        Add airport to graph.

        Args:
            airport:
                Airport object.
        """

        self.agregar_vertice(airport)

    def add_route(self, route):
        """
        Add directed route to graph.

        Args:
            route:
                Route object.
        """

        route.origin.agregar_adyacencia(route)

    def get_airport(self, airport_id):
        """Retrieve airport by ID."""

        return self.airports.get(airport_id)

    def airport_exists(self, airport_id):
        """Check whether airport exists."""

        return airport_id in self.airports

    def get_all_airports(self):
        """Retrieve all airports."""

        return list(self.airports.values())

    def agregar_arista(self, origen_id, destino_id, peso=0):
        """Compatibility helper to add a weighted connection."""

        origen = self.obtener_vertice(origen_id)
        destino = self.obtener_vertice(destino_id)

        if origen and destino and hasattr(origen, "agregar_adyacencia"):
            from src.core.route import Route

            arista = Route(origen, destino, peso)
            origen.agregar_adyacencia(arista)

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

    def dijkstra_simple(self, graph, start_id, end_id):
        """Dijkstra shortest path algorithm."""

        distances = {
            vertex_id: math.inf
            for vertex_id in graph.vertices
        }

        predecessors = {}

        if start_id not in distances or end_id not in distances:
            return distances, predecessors, []

        distances[start_id] = 0
        priority_queue = [(0, start_id)]

        while priority_queue:
            current_distance, current_id = heapq.heappop(priority_queue)

            if current_distance > distances[current_id]:
                continue

            current_vertex = graph.obtener_vertice(current_id)
            if current_vertex is None or not hasattr(current_vertex, "obtener_adyacencias"):
                continue

            for arista in current_vertex.obtener_adyacencias():
                if hasattr(arista, "is_available") and not arista.is_available:
                    continue

                neighbor = arista.getDestino()
                weight = arista.getPeso()
                new_distance = current_distance + weight

                if new_distance < distances[neighbor.id]:
                    distances[neighbor.id] = new_distance
                    predecessors[neighbor.id] = current_id
                    heapq.heappush(priority_queue, (new_distance, neighbor.id))

        if distances[end_id] == math.inf:
            return distances, predecessors, []

        path = []
        current = end_id

        while current != start_id:
            path.insert(0, current)
            current = predecessors[current]

        path.insert(0, start_id)

        return distances, predecessors, path

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