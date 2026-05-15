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

from api.schemas import AirportInfo, RouteInfo, GraphDataResponse
from src.services.graph_service import GraphService
from api.config import API_CONFIG

router = APIRouter()

# Global graph service instance
graph_service = GraphService()
_graph_loaded = False


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
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, network_file.lstrip("../"))
        
        if not os.path.exists(json_path):
            raise HTTPException(
                status_code=404,
                detail=f"Network file not found: {json_path}"
            )
        
        graph = graph_service.load_graph(json_path)
        _graph_loaded = True
        
        return {
            "status": "success",
            "message": "Graph loaded successfully",
            "airports_count": len(graph.airports),
            "file": network_file
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
        
        # Convert airports to response model
        airports_list = []
        for airport_id, airport in graph.airports.items():
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
            for route in airport.routes:
                routes_list.append(
                    RouteInfo(
                        origin_id=route.origin.id,
                        destination_id=route.destination.id,
                        distance=route.distance,
                        time=route.time,
                        cost=route.cost,
                        aircraft_type=route.aircraft_type
                    )
                )
        
        return GraphDataResponse(
            airports=airports_list,
            routes=routes_list,
            total_airports=len(airports_list),
            total_routes=len(routes_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        
        airports = []
        for airport_id, airport in graph.airports.items():
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
            for route in airport.routes:
                routes.append(
                    RouteInfo(
                        origin_id=route.origin.id,
                        destination_id=route.destination.id,
                        distance=route.distance,
                        time=route.time,
                        cost=route.cost,
                        aircraft_type=route.aircraft_type
                    )
                )
        
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def graph_status():
    """Get graph loading status."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            return {
                "loaded": False,
                "message": "Graph not loaded"
            }
        
        return {
            "loaded": True,
            "airports_count": len(graph.airports),
            "routes_count": sum(len(airport.routes) for airport in graph.airports.values())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
