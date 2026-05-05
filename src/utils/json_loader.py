"""
JSON loader module - Load and validate airline network data from JSON.

Functions:
    - load_network_from_json(): Load graph data from JSON file
    - validate_json_structure(): Validate JSON against required schema
    - build_graph_from_json(): Construct Graph object from JSON data
"""

import json
from src.core.graph import Grafo, Vertice, Arista
from src.core.airport import Airport


def load_network_from_json(filepath):
    """
    Load airline network data from JSON file.
    
    Args:
        filepath: Path to JSON file containing network data
        
    Returns:
        Parsed JSON data as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✓ JSON loaded successfully from {filepath}")
        return data
    except FileNotFoundError:
        print(f"✗ File not found: {filepath}")
        raise
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON format: {e}")
        raise


def validate_json_structure(data):
    """
    Validate that JSON data contains all required fields.
    
    Args:
        data: Dictionary containing JSON data
        
    Returns:
        Tuple of (is_valid: bool, errors: list)
    """
    errors = []
    
    # Check top-level keys
    if 'airports' not in data:
        errors.append("Missing 'airports' key")
    if 'rutas' not in data:
        errors.append("Missing 'rutas' key")
    
    # Validate airports structure
    if 'airports' in data:
        if not isinstance(data['airports'], list):
            errors.append("'airports' must be a list")
        else:
            for i, airport in enumerate(data['airports']):
                required_fields = ['id', 'nombre']
                for field in required_fields:
                    if field not in airport:
                        errors.append(f"Airport {i}: missing '{field}'")
    
    # Validate routes structure
    if 'rutas' in data:
        if not isinstance(data['rutas'], list):
            errors.append("'rutas' must be a list")
        else:
            airport_ids = {a['id'] for a in data.get('airports', [])}
            for i, route in enumerate(data['rutas']):
                required_fields = ['origen', 'destino', 'distanciaKm']
                for field in required_fields:
                    if field not in route:
                        errors.append(f"Route {i}: missing '{field}'")
                
                # Check if endpoints exist
                if 'origen' in route and route['origen'] not in airport_ids:
                    errors.append(f"Route {i}: origen '{route['origen']}' not found in airports")
                if 'destino' in route and route['destino'] not in airport_ids:
                    errors.append(f"Route {i}: destino '{route['destino']}' not found in airports")
                
                # Check for self-loops
                if route.get('origen') == route.get('destino'):
                    errors.append(f"Route {i}: self-loop detected ({route['origen']})")
    
    is_valid = len(errors) == 0
    if is_valid:
        print("✓ JSON structure is valid")
    else:
        print(f"✗ Validation errors found ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    return is_valid, errors


def build_graph_from_json(data):
    """
    Construct Grafo object from JSON data.
    
    Args:
        data: Parsed JSON data dictionary
        
    Returns:
        Grafo object with all airports and routes loaded
        
    Raises:
        ValueError: If JSON structure is invalid
    """
    # Validate first
    is_valid, errors = validate_json_structure(data)
    if not is_valid:
        raise ValueError(f"Invalid JSON structure: {errors}")
    
    # Create Grafo
    grafo = Grafo()
    
    # Create vertices (airports)
    vertices_map = {}  # Map airport_id → Vertice object
    
    for airport_data in data.get('airports', []):
        airport_id = airport_data['id']
        
        # Create Airport object with details
        airport = Airport(
            iata_code=airport_id,
            nombre=airport_data.get('nombre', ''),
            ciudad=airport_data.get('ciudad', ''),
            pais=airport_data.get('pais', ''),
            zona_horaria=airport_data.get('zonaHoraria', '')
        )
        
        # Set additional properties
        airport.es_hub = airport_data.get('esHub', False)
        airport.costo_alojamiento = airport_data.get('costoAlojamiento', 0)
        airport.costo_alimentacion = airport_data.get('costoAlimentacion', 0)
        airport.actividades = airport_data.get('actividades', [])
        airport.trabajos = airport_data.get('trabajos', [])
        
        # Create Vertice using the airport object as identifier
        vertice = Vertice(airport_id)
        vertice.airport = airport  # Store airport details in vertice
        
        vertices_map[airport_id] = vertice
        grafo.agregar_vertice(vertice)
    
    # Add routes (edges)
    for route_data in data.get('rutas', []):
        origen_id = route_data['origen']
        destino_id = route_data['destino']
        distancia_km = route_data['distanciaKm']
        
        origen_vertice = vertices_map[origen_id]
        destino_vertice = vertices_map[destino_id]
        
        # Use distance as weight for Dijkstra
        peso = distancia_km
        
        # Create and add edge
        arista = Arista(destino_vertice, peso)
        arista.route_data = route_data  # Store original route data
        origen_vertice.agregar_adyacencia(arista)
    
    print(f"✓ Graph built successfully: {len(vertices_map)} airports, "
          f"{sum(len(v.adyacencias) for v in grafo.vertices)} routes")
    
    return grafo
