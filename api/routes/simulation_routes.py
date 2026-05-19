"""
Simulation API routes.

Endpoints for simulation services:
    - Run simulations
    - Get simulation results
    - Analyze scenarios
"""

from fastapi import APIRouter, HTTPException
from api.schemas import SimulationRequest
from src.services.graph_service import graph_service
from src.services.simulation_service import SimulationService

router = APIRouter()

simulation_service = SimulationService()


@router.post("/run")
async def run_simulation(request: SimulationRequest):
    """
    Run a simulation on the network.
    
    Args:
        request: Simulation request with network file
    
    Returns:
        Simulation results
    """
    try:
        import os
        
        # Load graph if not already loaded
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, request.network_file.lstrip("../"))
        
        graph = graph_service.load_graph(json_path)
        
        # Run simulation
        results = simulation_service.run_simulation(graph)
        
        return {
            "status": "completed",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios")
async def get_scenarios():
    """Get available simulation scenarios."""
    return {
        "scenarios": [
            {
                "id": "scenario_1",
                "name": "Commercial Heavy Load",
                "description": "Peak commercial traffic simulation"
            },
            {
                "id": "scenario_2",
                "name": "Regional Network",
                "description": "Regional airport focus"
            },
            {
                "id": "scenario_3",
                "name": "Emergency Routes",
                "description": "Alternative routing simulation"
            }
        ]
    }


@router.post("/scenario/{scenario_id}")
async def run_scenario(scenario_id: str):
    """
    Run a specific scenario simulation.
    
    Args:
        scenario_id: Scenario identifier
    
    Returns:
        Scenario results
    """
    try:
        # TODO: Implement scenario-based simulation
        return {
            "scenario_id": scenario_id,
            "status": "running",
            "message": "Simulation started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
