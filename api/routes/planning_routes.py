"""
Planning API routes.

Endpoints for trip planning:
    - Generate itinerary
    - Calculate shortest path
    - Find optimal routes
"""

from fastapi import APIRouter, HTTPException
from api.schemas import PlanningRequest, PathRequest, ItineraryResponse, PathResponse
from src.services.graph_service import GraphService
from src.services.planning_service import PlanningService
from src.algorithms.shortestpath import dijkstra_shortest_path

router = APIRouter()

# Service instances
graph_service = GraphService()
planning_service = PlanningService()


@router.post("/itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: PlanningRequest):
    """
    Generate an optimized itinerary based on constraints.
    
    Args:
        request: Planning request with origin, budget, and time
    
    Returns:
        Itinerary with flights and constraints validation
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        # Execute planning
        result = planning_service.execute_planning(
            graph=graph,
            origin=request.origin,
            budget=request.budget,
            available_time=request.available_time
        )
        
        # Convert to response model
        flights = []
        total_distance = 0
        total_time = 0
        total_cost = 0
        
        if result and 'flights' in result:
            for flight in result['flights']:
                flights.append(
                    {
                        "origin": flight.origin.id,
                        "destination": flight.destination.id,
                        "distance": flight.distance,
                        "time": flight.time,
                        "cost": flight.cost,
                        "aircraft_type": flight.aircraft_type
                    }
                )
                total_distance += flight.distance
                total_time += flight.time
                total_cost += flight.cost
        
        return ItineraryResponse(
            origin=request.origin,
            flights=flights,
            total_distance=total_distance,
            total_time=total_time,
            total_cost=total_cost,
            number_of_stops=len(flights),
            feasible=result.get('feasible', True),
            constraints_met={
                "budget": total_cost <= request.budget,
                "time": total_time <= request.available_time
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shortest-path", response_model=PathResponse)
async def calculate_shortest_path(request: PathRequest):
    """
    Calculate shortest path between two airports.
    
    Args:
        request: Path request with start, end, and criterion
    
    Returns:
        Path with distances and total cost
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        # Validate airports exist
        if request.start not in graph.airports:
            raise HTTPException(
                status_code=404,
                detail=f"Airport {request.start} not found"
            )
        
        if request.end not in graph.airports:
            raise HTTPException(
                status_code=404,
                detail=f"Airport {request.end} not found"
            )
        
        # Calculate shortest path
        distances, predecessors, path = dijkstra_shortest_path(
            graph=graph,
            start_id=request.start,
            end_id=request.end,
            criterion=request.criterion
        )
        
        # Calculate total distance
        total_distance = distances.get(request.end, float('inf'))
        
        return PathResponse(
            path=path,
            distances=distances,
            predecessors=predecessors,
            total_distance=total_distance
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-routes")
async def compare_routes(start: str, end: str):
    """
    Compare routes by different criteria (distance, cost, time).
    
    Args:
        start: Starting airport
        end: Destination airport
    
    Returns:
        Dictionary with paths for each criterion
    """
    try:
        graph = graph_service.get_graph()
        
        if not graph:
            raise HTTPException(
                status_code=400,
                detail="Graph not loaded. Call /graph/load first."
            )
        
        results = {}
        criteria = ["distance", "cost", "time"]
        
        for criterion in criteria:
            try:
                distances, predecessors, path = dijkstra_shortest_path(
                    graph=graph,
                    start_id=start,
                    end_id=end,
                    criterion=criterion
                )
                results[criterion] = {
                    "path": path,
                    "total_value": distances.get(end, None)
                }
            except Exception as e:
                results[criterion] = {"error": str(e)}
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
