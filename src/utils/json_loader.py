"""
JSON loader module - Airline network loading utilities.

This module is responsible for:
    - Loading JSON files
    - Validating JSON structure
    - Building graph objects
    - Creating airports and routes

The JSON structure follows the project requirements
defined in the official specification document.
"""

import json

from src.core.graph import Graph
from src.core.airport import Airport
from src.core.route import Route
from src.core.route import AircraftOption


def load_network_from_json(filepath):
    """
    Load JSON file from disk.

    Args:
        filepath (str):
            JSON file path.

    Returns:
        dict:
            Parsed JSON data.
    """

    try:

        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        print(f"✓ JSON loaded successfully: {filepath}")

        return data

    except FileNotFoundError:

        print(f"✗ File not found: {filepath}")

        raise

    except json.JSONDecodeError as error:

        print(f"✗ Invalid JSON format: {error}")

        raise


def validate_json_structure(data):
    """
    Validate JSON structure.

    Args:
        data (dict):
            Parsed JSON data.

    Returns:
        tuple:
            (is_valid, errors)
    """

    errors = []

    # Validate top-level keys
    if "airports" not in data:
        errors.append("Missing 'airports' key")

    if "rutas" not in data:
        errors.append("Missing 'rutas' key")

    # Validate airports
    for airport in data.get("airports", []):

        if "id" not in airport:
            errors.append("Airport missing 'id'")

        if "nombre" not in airport:
            errors.append("Airport missing 'nombre'")

    # Validate routes
    for route in data.get("rutas", []):

        if "origen" not in route:
            errors.append("Route missing 'origen'")

        if "destino" not in route:
            errors.append("Route missing 'destino'")

        if "distanciaKm" not in route:
            errors.append("Route missing 'distanciaKm'")

    return len(errors) == 0, errors


def build_graph_from_json(data):
    """
    Build Graph object from JSON data.

    Args:
        data (dict):
            Parsed JSON data.

    Returns:
        Graph:
            Fully constructed graph object.
    """

    # Validate JSON before graph construction
    is_valid, errors = validate_json_structure(data)

    if not is_valid:
        raise ValueError(errors)

    # Create graph
    graph = Graph()

    # -----------------------------------------
    # CREATE AIRPORTS
    # -----------------------------------------

    for airport_data in data.get("airports", []):

        airport = Airport(
            airport_data["id"]
        )

        # Basic metadata
        airport.nombre = airport_data.get("nombre", "")
        airport.ciudad = airport_data.get("ciudad", "")
        airport.pais = airport_data.get("pais", "")
        airport.zona_horaria = airport_data.get(
            "zonaHoraria",
            ""
        )

        # Airport properties
        airport.es_hub = airport_data.get(
            "esHub",
            False
        )

        airport.costo_alojamiento = airport_data.get(
            "costoAlojamiento",
            0
        )

        airport.costo_alimentacion = airport_data.get(
            "costoAlimentacion",
            0
        )

        # Dynamic data
        airport.actividades = airport_data.get(
            "actividades",
            []
        )

        airport.trabajos = airport_data.get(
            "trabajos",
            []
        )

        # Add airport to graph
        graph.add_airport(airport)

    # -----------------------------------------
    # CREATE ROUTES
    # -----------------------------------------

    aircraft_config = (
        data.get("configuracion", {})
        .get("aeronaves", {})
    )

    for route_data in data.get("rutas", []):

        origin = graph.get_airport(
            route_data["origen"]
        )

        destination = graph.get_airport(
            route_data["destino"]
        )

        route = Route(
            origin=origin,
            destination=destination,
            distance_km=route_data["distanciaKm"]
        )

        # Route configuration
        route.min_stay = route_data.get(
            "estanciaMinima",
            0
        )

        # Subsidized route detection
        if route_data.get("costoBase", 1) == 0:
            route.subsidized = True

        # -----------------------------------------
        # ADD AIRCRAFT OPTIONS
        # -----------------------------------------

        for aircraft_name in route_data.get(
            "aeronaves",
            []
        ):

            aircraft_data = aircraft_config.get(
                aircraft_name,
                {}
            )

            aircraft_option = AircraftOption(
                name=aircraft_name,
                cost_per_km=aircraft_data.get(
                    "costoKm",
                    0
                ),
                time_per_km=aircraft_data.get(
                    "tiempoKm",
                    0
                )
            )

            route.add_aircraft_option(
                aircraft_option
            )

        # Add route to graph
        graph.add_route(route)

    print(
        f"\n✓ Graph loaded successfully:"
        f"\n   Airports: {graph.total_airports()}"
        f"\n   Routes: {graph.total_routes()}"
    )

    return graph