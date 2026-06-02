"""
Base graph module.

This module provides the generic graph primitives used by the project.

Core structures:
    - Arista
    - Vertice (compatibility helper)
    - Grafo

The project uses these building blocks with domain objects such as:
    - Airport
    - Route
    - Graph
"""

import heapq
import math


class Arista:
    """
    Represents a directed weighted edge.

    This is the academic edge structure used
    by traversal and shortest-path algorithms.
    """

    def __init__(self, destino, peso=0):
        """
        Initialize edge.

        Args:
            destino:
                Destination vertex.

            peso (float):
                Edge weight.
        """

        self.destino = destino

        self.peso = peso

    def getDestino(self):
        """
        Retrieve destination vertex.
        """

        return self.destino

    def getPeso(self):
        """
        Retrieve edge weight.
        """

        return self.peso

    def __str__(self):
        """
        String representation of edge.
        """

        return (
            f"Destino: {self.destino.id} | "
            f"Peso: {self.peso}"
        )


class Vertice:
    """
    Represents a generic graph vertex.

    Stores:
        - Identifier
        - Adjacency list
        - Traversal state
    """

    def __init__(self, identificador):
        """
        Initialize vertex.

        Args:
            identificador (str):
                Unique vertex identifier.
        """

        # Unique identifier
        self.id = identificador

        # Academic adjacency list
        self.adyacencias = []

        # Traversal support
        self.visitado = False

    def agregar_adyacencia(self, arista):
        """
        Add edge to adjacency list.

        Args:
            arista:
                Edge object.
        """

        self.adyacencias.append(arista)

    def obtener_adyacencias(self):
        """
        Retrieve adjacency list.
        """

        return self.adyacencias

    def __str__(self):
        """
        String representation of vertex.
        """

        return f"Vertice({self.id})"


class Grafo:
    """
    Directed weighted graph implementation.

    The graph stores generic nodes indexed by their ``id`` attribute.
    Nodes are expected to expose an adjacency list API compatible with:
        - agregar_adyacencia(arista)
        - obtener_adyacencias()

    The graph uses adjacency lists because airline networks are sparse,
    so they are memory-efficient and traversal-friendly.
    """

    def __init__(self):
        """
        Initialize graph.
        """

        # Vertex dictionary
        self.vertices = {}

    def agregar_vertice(self, vertice):
        """
        Add vertex to graph.

        Args:
            vertice:
                Node object with an ``id`` attribute.
        """

        self.vertices[vertice.id] = vertice

    def obtener_vertice(self, identificador):
        """
        Retrieve vertex by ID.

        Args:
            identificador (str):
                Vertex identifier.

        Returns:
            Vertice:
                Matching vertex object.
        """

        return self.vertices.get(
            identificador
        )

    def agregar_arista(
        self,
        origen_id,
        destino_id,
        peso=0
    ):
        """
        Add edge between vertices.

        Args:
            origen_id (str):
                Origin vertex ID.

            destino_id (str):
                Destination vertex ID.

            peso (float):
                Edge weight.
        """

        origen = self.obtener_vertice(
            origen_id
        )

        destino = self.obtener_vertice(
            destino_id
        )

        if origen and destino and hasattr(origen, "agregar_adyacencia"):

            arista = Arista(
                destino,
                peso
            )

            origen.agregar_adyacencia(
                arista
            )

    def reset_visits(self):
        """
        Reset traversal state for all vertices.
        """

        for vertice in self.vertices.values():

            if hasattr(vertice, "visitado"):
                vertice.visitado = False

    def dijkstra_simple(
        self,
        graph,
        start_id,
        end_id
    ):
        """
        Dijkstra shortest path algorithm.

        Finds the optimal path between two vertices
        using weighted edges.

        Time Complexity:
            O((V + E) log V)

        Args:
            graph:
                Graph object.

            start_id (str):
                Starting vertex ID.

            end_id (str):
                Destination vertex ID.

        Returns:
            tuple:
                (
                    distances,
                    predecessors,
                    path
                )
        """

        # -----------------------------------------
        # INITIALIZATION
        # -----------------------------------------

        distances = {

            vertex_id: math.inf

            for vertex_id in graph.vertices
        }

        predecessors = {}

        distances[start_id] = 0

        # Priority queue:
        # (
        #   accumulated_distance,
        #   vertex_id
        # )
        priority_queue = []

        heapq.heappush(
            priority_queue,
            (0, start_id)
        )

        # -----------------------------------------
        # MAIN LOOP
        # -----------------------------------------

        while priority_queue:

            current_distance, current_id = (
                heapq.heappop(
                    priority_queue
                )
            )

            # Ignore outdated queue entries
            if (
                current_distance
                > distances[current_id]
            ):
                continue

            current_vertex = (
                graph.obtener_vertice(
                    current_id
                )
            )

            if current_vertex is None or not hasattr(current_vertex, "obtener_adyacencias"):
                continue

            # Explore adjacency list
            for arista in (
                current_vertex.obtener_adyacencias()
            ):

                # Ignore blocked routes
                if hasattr(arista, "is_available"):

                    if not arista.is_available:
                        continue

                neighbor = (
                    arista.getDestino()
                )

                weight = (
                    arista.getPeso()
                )

                new_distance = (
                    current_distance
                    + weight
                )

                # Relaxation step
                if (
                    new_distance
                    < distances[neighbor.id]
                ):

                    distances[
                        neighbor.id
                    ] = new_distance

                    predecessors[
                        neighbor.id
                    ] = current_id

                    heapq.heappush(
                        priority_queue,
                        (
                            new_distance,
                            neighbor.id
                        )
                    )

        # -----------------------------------------
        # REBUILD PATH
        # -----------------------------------------

        path = []

        current = end_id

        # Destination unreachable
        if (
            distances[end_id]
            == math.inf
        ):

            return (
                distances,
                predecessors,
                []
            )

        while current != start_id:

            path.insert(0, current)

            current = predecessors[current]

        path.insert(0, start_id)

        return (
            distances,
            predecessors,
            path
        )

    def __str__(self):
        """
        String representation of graph.
        """

        return (
            f"Grafo("
            f"vertices={len(self.vertices)}"
            f")"
        )