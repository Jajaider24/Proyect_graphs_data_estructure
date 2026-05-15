"""
Network API routes.

Endpoints for network analysis:
    - Network statistics
    - Airport connectivity
    - Route analysis
"""

from fastapi import APIRouter, HTTPException
from src.services.graph_service import GraphService

router = APIRouter()

graph_service = GraphService()


@router.get("/statistics")
async def get_network_statistics():
    """Get network statistics."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        # Calculate statistics
        total_airports = len(graph.airports)
        total_routes = sum(len(airport.routes) for airport in graph.airports.values())
        
        # Calculate connectivity
        hub_airports = sum(1 for airport in graph.airports.values() if airport.es_hub)
        
        # Calculate average connections per airport
        avg_connections = total_routes / total_airports if total_airports > 0 else 0
        
        return {
            "total_airports": total_airports,
            "total_routes": total_routes,
            "hub_airports": hub_airports,
            "average_connections": round(avg_connections, 2),
            "network_density": round(total_routes / (total_airports * (total_airports - 1)), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/airport/{airport_id}")
async def get_airport_details(airport_id: str):
    """Get details about a specific airport."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        if airport_id not in graph.airports:
            raise HTTPException(
                status_code=404,
                detail=f"Airport {airport_id} not found"
            )
        
        airport = graph.airports[airport_id]
        
        # Get connected airports
        connected = []
        for route in airport.routes:
            connected.append({
                "destination": route.destination.id,
                "distance": route.distance,
                "cost": route.cost,
                "time": route.time,
                "aircraft_type": route.aircraft_type
            })
        
        return {
            "id": airport.id,
            "nombre": airport.nombre,
            "ciudad": airport.ciudad,
            "pais": airport.pais,
            "zona_horaria": airport.zona_horaria,
            "es_hub": airport.es_hub,
            "costo_alojamiento": airport.costo_alojamiento,
            "costo_alimentacion": airport.costo_alimentacion,
            "total_connections": len(airport.routes),
            "connected_airports": connected
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hubs")
async def get_hub_airports():
    """Get all hub airports in the network."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        hubs = []
        for airport in graph.airports.values():
            if airport.es_hub:
                hubs.append({
                    "id": airport.id,
                    "nombre": airport.nombre,
                    "ciudad": airport.ciudad,
                    "pais": airport.pais,
                    "connections": len(airport.routes)
                })
        
        return {
            "total_hubs": len(hubs),
            "hubs": hubs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connectivity/{airport_id}")
async def analyze_connectivity(airport_id: str):
    """Analyze connectivity metrics for an airport."""
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        if airport_id not in graph.airports:
            raise HTTPException(
                status_code=404,
                detail=f"Airport {airport_id} not found"
            )
        
        airport = graph.airports[airport_id]
        
        # Calculate metrics
        outgoing_routes = len(airport.routes)
        
        # Calculate average distance and cost
        if outgoing_routes > 0:
            avg_distance = sum(r.distance for r in airport.routes) / outgoing_routes
            avg_cost = sum(r.cost for r in airport.routes) / outgoing_routes
            avg_time = sum(r.time for r in airport.routes) / outgoing_routes
        else:
            avg_distance = avg_cost = avg_time = 0
        
        return {
            "airport_id": airport_id,
            "outgoing_routes": outgoing_routes,
            "average_distance": round(avg_distance, 2),
            "average_cost": round(avg_cost, 2),
            "average_time": round(avg_time, 2),
            "is_hub": airport.es_hub,
            "accommodation_cost": airport.costo_alojamiento,
            "food_cost": airport.costo_alimentacion
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
