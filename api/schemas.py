"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class AirportInfo(BaseModel):
    """Airport information model."""
    id: str
    nombre: str
    ciudad: str
    pais: str
    zona_horaria: str
    es_hub: bool = False
    costo_alojamiento: float
    costo_alimentacion: float


class RouteInfo(BaseModel):
    """Route information model."""
    origin_id: str
    destination_id: str
    distance: float
    time: float
    cost: float
    aircraft_type: str


class GraphDataResponse(BaseModel):
    """Response model for graph data."""
    airports: List[AirportInfo]
    routes: List[RouteInfo]
    total_airports: int
    total_routes: int


class PlanningRequest(BaseModel):
    """Planning request model."""
    origin: str = Field(..., description="Starting airport IATA code")
    budget: float = Field(..., gt=0, description="Maximum budget in USD")
    available_time: float = Field(..., gt=0, description="Available time in minutes")
    aircraft_type: Optional[str] = Field("Commercial", description="Aircraft type")


class PathRequest(BaseModel):
    """Shortest path request model."""
    start: str = Field(..., description="Starting airport")
    end: str = Field(..., description="Destination airport")
    criterion: str = Field("distance", description="Optimization criterion: distance, cost, time")


class FlightSegmentResponse(BaseModel):
    """Flight segment response model."""
    origin: str
    destination: str
    distance: float
    time: float
    cost: float
    aircraft_type: str


class ItineraryResponse(BaseModel):
    """Itinerary response model."""
    origin: str
    flights: List[FlightSegmentResponse]
    total_distance: float
    total_time: float
    total_cost: float
    number_of_stops: int
    feasible: bool
    constraints_met: Dict[str, bool]


class SimulationRequest(BaseModel):
    """Simulation request model."""
    network_file: str = Field("../data/sample_network.json", description="Network JSON file path")


class PathResponse(BaseModel):
    """Path response model."""
    path: List[str]
    distances: Dict[str, float]
    predecessors: Dict[str, str]
    total_distance: float


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    code: int = 400
