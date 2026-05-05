"""
Airport module - Airport data model representation.

Classes:
    - Airport: Represents a single airport node with all its properties
"""


class Airport:
    """
    Represents an airport node with complete information about location,
    costs, activities, and available jobs.
    
    Extends Vertice concept from professor's class with domain-specific information.
    """
    def __init__(self, iata_code, nombre="", ciudad="", pais="", zona_horaria=""):
        """
        Initialize an airport.
        
        Args:
            iata_code: IATA airport code (identifier)
            nombre: Full airport name
            ciudad: City name
            pais: Country name
            zona_horaria: Timezone
        """
        self.id = iata_code  # Identifier for graph
        self.iata_code = iata_code
        self.nombre = nombre
        self.ciudad = ciudad
        self.pais = pais
        self.zona_horaria = zona_horaria
        self.es_hub = False
        self.costo_alojamiento = 0
        self.costo_alimentacion = 0
        self.actividades = []
        self.trabajos = []
    
    def __str__(self):
        """String representation of airport."""
        return f"{self.iata_code}: {self.nombre}"
    
    def __repr__(self):
        """Developer representation of airport."""
        return f"Airport(id={self.iata_code}, nombre={self.nombre})"

