"""
Network API routes.

Endpoints for network analysis:
    - Network statistics
    - Airport connectivity
    - Route analysis
"""

from fastapi import APIRouter, HTTPException
from src.services.graph_service import graph_service

router = APIRouter()


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
        
        print(f"[DEBUG] Calculating statistics for graph with {len(graph.airports)} airports")
        
        # Calculate statistics
        total_airports = len(graph.airports)
        total_routes = 0
        
        # Safely count routes
        for airport_id, airport in graph.airports.items():
            if airport and hasattr(airport, 'routes') and airport.routes:
                total_routes += len(airport.routes)
                print(f"[DEBUG] Airport {airport_id}: {len(airport.routes)} routes")
        
        # Calculate connectivity
        hub_airports = sum(1 for airport in graph.airports.values() if airport and airport.es_hub)
        
        # Calculate average connections per airport
        avg_connections = total_routes / total_airports if total_airports > 0 else 0
        
        # Calculate network density safely
        network_density = 0
        if total_airports > 1:
            network_density = total_routes / (total_airports * (total_airports - 1))
        
        result = {
            "total_airports": total_airports,
            "total_routes": total_routes,
            "hub_airports": hub_airports,
            "average_connections": round(avg_connections, 2),
            "network_density": round(network_density, 4)
        }
        
        print(f"[DEBUG] Statistics: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get statistics: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error calculating statistics: {str(e)}")


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
        if airport and hasattr(airport, 'routes') and airport.routes:
            for route in airport.routes:
                # Build connected airport entry with available data
                route_data = {
                    "destination": route.destination.id if route.destination else "Unknown"
                }
                
                # Add distance if available
                if hasattr(route, 'distance_km'):
                    route_data["distance_km"] = route.distance_km
                
                # Add aircraft options if available
                if hasattr(route, 'aircraft_options') and route.aircraft_options:
                    route_data["aircraft_types"] = [ac.name for ac in route.aircraft_options]
                
                connected.append(route_data)
        
        return {
            "id": airport.id,
            "nombre": airport.nombre,
            "ciudad": airport.ciudad,
            "pais": airport.pais,
            "zona_horaria": airport.zona_horaria,
            "es_hub": airport.es_hub,
            "costo_alojamiento": airport.costo_alojamiento,
            "costo_alimentacion": airport.costo_alimentacion,
            "total_connections": len(airport.routes) if airport.routes else 0,
            "connected_airports": connected
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get airport details for {airport_id}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving airport details: {str(e)}")


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
                    "connections": len(airport.routes) if airport.routes else 0
                })
        
        return {
            "total_hubs": len(hubs),
            "hubs": hubs
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get hub airports: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving hubs: {str(e)}")


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
        if not airport or not hasattr(airport, 'routes'):
            raise ValueError(f"Airport {airport_id} has invalid structure")
        
        outgoing_routes = len(airport.routes) if airport.routes else 0
        
        # Calculate average distance safely
        avg_distance = 0
        if outgoing_routes > 0 and airport.routes:
            distances = [r.distance_km for r in airport.routes if r and hasattr(r, 'distance_km')]
            if distances:
                avg_distance = sum(distances) / len(distances)
        
        return {
            "airport_id": airport_id,
            "outgoing_routes": outgoing_routes,
            "average_distance_km": round(avg_distance, 2),
            "is_hub": airport.es_hub,
            "accommodation_cost": airport.costo_alojamiento,
            "food_cost": airport.costo_alimentacion
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to analyze connectivity for {airport_id}: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error analyzing connectivity: {str(e)}")
