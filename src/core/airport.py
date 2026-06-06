"""
Airport module - Airport domain model.

Represents airports as graph nodes in the airline network.
"""

class Airport:
    """
    Represents an airport node in the graph.

    The class keeps only the interface that the graph algorithms need:
        - id
        - visitado
        - adjacency list helpers

    Domain-specific data such as metadata, costs, activities and jobs
    live here instead of in the academic graph vertex base class.
    """

    def __init__(self, iata_code):
        """
        Initialize airport.

        Args:
            iata_code (str):
                Airport IATA code.
        """

        # Graph-compatible identity and traversal state.
        self.id = iata_code
        self.adyacencias = []
        self.visitado = False

        # Airport metadata
        self.nombre = ""
        self.ciudad = ""
        self.pais = ""
        self.zona_horaria = ""

        # Airport classification
        self.es_hub = False

        # Mandatory traveler costs
        self.costo_alojamiento = 0
        self.costo_alimentacion = 0

        # Dynamic simulation data
        self.actividades = []
        self.trabajos = []

    def agregar_adyacencia(self, arista):
        """Add a route to the airport adjacency list."""
        self.adyacencias.append(arista)

    def obtener_adyacencias(self):
        """Return the airport adjacency list."""
        return self.adyacencias

    @property #The decorator is used to define a class method as if it were an attribute
    def routes(self):
        """Compatibility alias for the adjacency list."""
        return self.adyacencias

    @routes.setter #This decorator is used to assign a new value to adjacencies as an OOP setter.
    def routes(self, value):
        self.adyacencias = list(value)

    def __str__(self):
        """
        String representation of airport.
        """
        return (
            f"{self.id} - "
            f"{self.ciudad}, "
            f"{self.pais}"
        )