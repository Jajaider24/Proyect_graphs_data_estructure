"""
Airport module - Airport domain model.

Represents airports as graph nodes in the airline network.
"""

from src.core.base_graph import Vertice


class Airport(Vertice):
    """
    Represents an airport node in the graph.

    This class extends the academic Vertice structure
    provided in class and adds domain-specific data
    required by the airline simulation project.

    Each airport stores:
        - Metadata
        - Costs
        - Activities
        - Jobs
        - Route adjacency list
    """

    def __init__(self, iata_code):
        """
        Initialize airport.

        Args:
            iata_code (str):
                Airport IATA code.
        """

        # Initialize academic graph vertex structure
        super().__init__(iata_code)

        # Unique airport identifier
        self.id = iata_code

        # Project adjacency list.
        # Stores Route objects.
        self.routes = []

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

    def __str__(self):
        """
        String representation of airport.
        """

        return (
            f"{self.id} - "
            f"{self.ciudad}, "
            f"{self.pais}"
        )