"""
Graph API routes.

Endpoints for graph/network management:
    - Load graph from JSON
    - Get graph data
    - Get airports list
    - Get routes list
"""

from fastapi import APIRouter, HTTPException
from typing import List
import os

from api.schemas import AirportInfo, RouteInfo, GraphDataResponse, RouteInterruptionRequest
from src.services.graph_service import graph_service
from api.config import API_CONFIG

router = APIRouter()

# Use shared graph_service instance from src.services.graph_service
_graph_loaded = False


def _find_route(graph, origin_id: str, destination_id: str):
    origin = graph.airports.get(origin_id)
    if not origin:
        return None
    for route in getattr(origin, "routes", []) or []:
        if route.destination.id == destination_id:
            return route
    return None


@router.post("/load")
async def load_graph(network_file: str = "../data/sample_network.json"):
    """
    Load graph from JSON dataset.
    
    Args:
        network_file: Path to network JSON file
    
    Returns:
        Graph data with airports and routes
    """
    global _graph_loaded
    
    try:
        # Resolve file path
        # __file__ is: api/routes/graph_routes.py
        # dirname twice goes to project root
        api_routes_dir = os.path.dirname(os.path.abspath(__file__))  # api/routes
        api_dir = os.path.dirname(api_routes_dir)                    # api
        project_root = os.path.dirname(api_dir)                      # project root
        
        # Handle relative paths
        if network_file.startswith("../"):
            # Remove "../" and join with project root
            file_relative = network_file.lstrip("../").lstrip("/")
            json_path = os.path.join(project_root, file_relative)
        else:
            # Relative to project root
            json_path = os.path.join(project_root, network_file)
        
        # Normalize path
        json_path = os.path.normpath(json_path)
        
        print(f"[DEBUG] Project root: {project_root}")
        print(f"[DEBUG] Loading graph from: {json_path}")
        
        if not os.path.exists(json_path):
            print(f"[ERROR] File does not exist: {json_path}")
            raise HTTPException(
                status_code=404,
                detail=f"Network file not found: {json_path}"
            )
        
        print(f"[DEBUG] File exists, loading...")
        graph = graph_service.load_graph(json_path)
        _graph_loaded = True
        
        print(f"[DEBUG] Graph loaded successfully. Airports: {len(graph.airports)}")
        
        return {
            "status": "success",
            "message": "Graph loaded successfully",
            "airports_count": len(graph.airports),
            "file": network_file
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        print(f"[ERROR] FileNotFoundError: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        print(f"[ERROR] ValueError: {e}")
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Error loading graph: {str(e)}")


@router.get("/data", response_model=GraphDataResponse)
async def get_graph_data():
    """Get current graph data."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /load first."
            )
        
        print(f"[DEBUG] Getting graph data for {len(graph.airports)} airports")
        
        # Convert airports to response model
        airports_list = []
        for airport_id, airport in graph.airports.items():
            if airport:
                airports_list.append(
                    AirportInfo(
                        id=airport.id,
                        nombre=airport.nombre,
                        ciudad=airport.ciudad,
                        pais=airport.pais,
                        zona_horaria=airport.zona_horaria,
                        es_hub=airport.es_hub,
                        costo_alojamiento=airport.costo_alojamiento,
                        costo_alimentacion=airport.costo_alimentacion
                    )
                )
        
        # Convert routes to response model
        routes_list = []
        for airport in graph.airports.values():
            if airport and hasattr(airport, 'routes') and airport.routes:
                for route in airport.routes:
                    if route:
                        aircraft_types = []
                        if hasattr(route, 'aircraft_options') and route.aircraft_options:
                            aircraft_types = [ac.name for ac in route.aircraft_options]
                        
                        routes_list.append(
                            RouteInfo(
                                origin_id=route.origin.id,
                                destination_id=route.destination.id,
                                distance_km=route.distance_km if hasattr(route, 'distance_km') else 0,
                                aircraft_count=len(aircraft_types),
                                aircraft_types=aircraft_types if aircraft_types else None,
                                blocked=bool(getattr(route, 'blocked', False)),
                                is_available=bool(getattr(route, 'is_available', True)),
                            )
                        )
        
        print(f"[DEBUG] Returning {len(airports_list)} airports and {len(routes_list)} routes")
        
        return GraphDataResponse(
            airports=airports_list,
            routes=routes_list,
            total_airports=len(airports_list),
            total_routes=len(routes_list)
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get graph data: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving graph data: {str(e)}")


@router.get("/airports", response_model=List[AirportInfo])
async def get_airports():
    """Get all airports in the graph."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /load first."
            )
        
        print(f"[DEBUG] Retrieving {len(graph.airports)} airports")
        
        airports = []
        for airport_id, airport in graph.airports.items():
            if airport:
                airports.append(
                    AirportInfo(
                        id=airport.id,
                        nombre=airport.nombre,
                        ciudad=airport.ciudad,
                        pais=airport.pais,
                        zona_horaria=airport.zona_horaria,
                        es_hub=airport.es_hub,
                        costo_alojamiento=airport.costo_alojamiento,
                        costo_alimentacion=airport.costo_alimentacion
                    )
                )
        
        return airports
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get airports: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving airports: {str(e)}")


@router.get("/routes", response_model=List[RouteInfo])
async def get_routes():
    """Get all routes in the graph."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /load first."
            )
        
        routes = []
        for airport in graph.airports.values():
            if airport and hasattr(airport, 'routes') and airport.routes:
                for route in airport.routes:
                    if route:
                        aircraft_types = []
                        if hasattr(route, 'aircraft_options') and route.aircraft_options:
                            aircraft_types = [ac.name for ac in route.aircraft_options]
                        
                        routes.append(
                            RouteInfo(
                                origin_id=route.origin.id,
                                destination_id=route.destination.id,
                                distance_km=route.distance_km if hasattr(route, 'distance_km') else 0,
                                aircraft_count=len(aircraft_types),
                                aircraft_types=aircraft_types if aircraft_types else None,
                                blocked=bool(getattr(route, 'blocked', False)),
                                is_available=bool(getattr(route, 'is_available', True)),
                            )
                        )
        
        return routes
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get routes: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving routes: {str(e)}")


@router.get("/status")
async def graph_status():
    """Get graph loading status."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            return {
                "loaded": False,
                "message": "Graph not loaded",
                "airports_count": 0,
                "routes_count": 0
            }
        
        # Count routes safely
        routes_count = 0
        for airport in graph.airports.values():
            if airport and hasattr(airport, 'routes') and airport.routes:
                routes_count += len(airport.routes)
        
        return {
            "loaded": True,
            "airports_count": len(graph.airports),
            "routes_count": routes_count
        }
    except Exception as e:
        print(f"[ERROR] Failed to get graph status: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "loaded": False,
            "message": f"Error checking status: {str(e)}",
            "airports_count": 0,
            "routes_count": 0
        }


@router.post("/route/block")
async def block_route(request: RouteInterruptionRequest):
    """Block a route in the loaded graph."""
    graph = graph_service.get_graph()
    if not graph:
        raise HTTPException(status_code=400, detail="Graph not loaded. Call /load first.")

    route = _find_route(graph, request.origin_id, request.destination_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    route.blocked = True
    route.is_available = False

    return {
        "status": "blocked",
        "origin_id": request.origin_id,
        "destination_id": request.destination_id,
        "reason": request.reason,
    }


@router.post("/route/unblock")
async def unblock_route(request: RouteInterruptionRequest):
    """Unblock a route in the loaded graph."""
    graph = graph_service.get_graph()
    if not graph:
        raise HTTPException(status_code=400, detail="Graph not loaded. Call /load first.")

    route = _find_route(graph, request.origin_id, request.destination_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    route.blocked = False
    route.is_available = True

    return {
        "status": "unblocked",
        "origin_id": request.origin_id,
        "destination_id": request.destination_id,
    }
