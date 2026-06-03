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
    distance_km: float
    aircraft_count: int = 0
    aircraft_types: Optional[List[str]] = None
    blocked: bool = False
    is_available: bool = True


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
    available_time: float = Field(..., gt=0, description="Available travel time in hours")
    preferred_transports: List[str] = Field(default_factory=list, description="Allowed transport types")
    include_secondary_airports: bool = Field(True, description="Whether secondary airports can be used")


class PathRequest(BaseModel):
    """Shortest path request model."""
    start: str = Field(..., description="Starting airport")
    end: str = Field(..., description="Destination airport")
    criterion: str = Field("distance", description="Optimization criterion: distance, cost, time")
    criteria: List[str] = Field(default_factory=list, description="Multiple criteria to evaluate")
    include_secondary_airports: bool = Field(True, description="Whether to include secondary airports")
    transport_types: List[str] = Field(default_factory=list, description="Allowed transport types")


class FlightSegmentResponse(BaseModel):
    """Flight segment response model."""
    origin: str
    destination: str
    distance: float
    time: float
    cost: float
    aircraft_type: str
    cumulative_cost: Optional[float] = None
    cumulative_time: Optional[float] = None


class ItineraryAlternativeResponse(BaseModel):
    """Alternative itinerary response model."""
    criterion: str
    visited_airports: List[str]
    total_destinations: int
    flights: List[FlightSegmentResponse]
    total_distance: float
    total_time: float
    total_cost: float
    constraints_met: Dict[str, bool]
    used_transport_types: List[str]
    transport_requirement_met: bool


class ItineraryResponse(BaseModel):
    """Itinerary response model."""
    origin: str
    required_transport_types: List[str] = Field(default_factory=list)
    alternatives: Dict[str, ItineraryAlternativeResponse] = Field(default_factory=dict)
    flights: List[FlightSegmentResponse] = Field(default_factory=list)
    total_distance: float = 0
    total_time: float = 0
    total_cost: float = 0
    number_of_stops: int = 0
    feasible: bool = True
    constraints_met: Dict[str, bool] = Field(default_factory=dict)


class SimulationRequest(BaseModel):
    """Simulation request model."""
    network_file: str = Field("../data/sample_network.json", description="Network JSON file path")


class SessionCreateRequest(BaseModel):
    origin: str
    initial_budget: float
    available_time_hours: float
    preferred_transports: List[str] = Field(default_factory=list)
    include_secondary_airports: bool = True


class SessionStateResponse(BaseModel):
    session_id: str
    current_airport: Optional[str]
    remaining_budget: float
    remaining_time: float
    visited_airports: List[str]
    total_distance: float
    subsidized_distance: float
    pending_min_stay_minutes: float = 0
    jobs_done: List[Dict[str, Any]] = Field(default_factory=list)
    activities_done: List[Dict[str, Any]] = Field(default_factory=list)
    in_transit: bool = False
    transit: Dict[str, Any] = Field(default_factory=dict)
    recommended_itinerary: Dict[str, Any] = Field(default_factory=dict)
    blocked_routes: List[Dict[str, str]] = Field(default_factory=list)


class SessionOptionsResponse(BaseModel):
    flights: List[Dict[str, Any]] = Field(default_factory=list)
    activities: List[Dict[str, Any]] = Field(default_factory=list)
    jobs: List[Dict[str, Any]] = Field(default_factory=list)
    can_take_job: bool = False
    budget_percent: float = 100.0
    lodging_required: bool = False
    meal_required: bool = False
    pending_min_stay_minutes: float = 0
    can_take_flight: bool = True
    traveler_state: SessionStateResponse


class DecisionRequest(BaseModel):
    type: str
    # job
    job_name: Optional[str] = None
    hours: Optional[int] = None
    # activities
    activities: Optional[List[str]] = None
    # flight
    destination: Optional[str] = None
    aircraft_type: Optional[str] = None
    # stay
    free_time_min: Optional[int] = None
    # advance transit
    advance_minutes: Optional[float] = None


class RouteInterruptionRequest(BaseModel):
    origin_id: Optional[str] = None
    destination_id: Optional[str] = None
    # Backward-compatible aliases sometimes used by clients/manual requests.
    origin: Optional[str] = None
    destination: Optional[str] = None
    session_id: Optional[str] = None
    reason: Optional[str] = "Interrupcion operativa"


class PathResponse(BaseModel):
    """Path response model."""
    criterion: Optional[str] = None
    path: List[str]
    distances: Dict[str, float]
    predecessors: Dict[str, str]
    total_distance: float
    total_cost: Optional[float] = None
    total_time: Optional[float] = None
    segments: List[Dict[str, Any]] = Field(default_factory=list)
    results_by_criterion: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: str
    code: int = 400
