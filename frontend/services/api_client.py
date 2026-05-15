"""
HTTP client for communicating with FastAPI backend.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from frontend.config import API_CONFIG


class APIClient:
    """Client for API communication."""
    
    def __init__(self):
        """Initialize API client."""
        self.base_url = API_CONFIG["BASE_URL"]
        self.timeout = API_CONFIG["TIMEOUT"]
        self.client = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self.client
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        try:
            client = await self._get_client()
            response = await client.get(f"/api{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"GET {endpoint} failed: {str(e)}")
    
    async def post(self, endpoint: str, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Make POST request."""
        try:
            client = await self._get_client()
            response = await client.post(
                f"/api{endpoint}",
                json=data,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"POST {endpoint} failed: {str(e)}")
    
    # Graph endpoints
    async def load_graph(self, network_file: str = "../data/sample_network.json") -> Dict[str, Any]:
        """Load graph from network file."""
        return await self.post("/graph/load", {"network_file": network_file})
    
    async def get_graph_data(self) -> Dict[str, Any]:
        """Get current graph data."""
        return await self.get("/graph/data")
    
    async def get_airports(self) -> List[Dict[str, Any]]:
        """Get all airports."""
        return await self.get("/graph/airports")
    
    async def get_routes(self) -> List[Dict[str, Any]]:
        """Get all routes."""
        return await self.get("/graph/routes")
    
    async def get_graph_status(self) -> Dict[str, Any]:
        """Get graph loading status."""
        return await self.get("/graph/status")
    
    # Planning endpoints
    async def generate_itinerary(
        self,
        origin: str,
        budget: float,
        available_time: float,
        aircraft_type: str = "Commercial"
    ) -> Dict[str, Any]:
        """Generate travel itinerary."""
        return await self.post(
            "/planning/itinerary",
            {
                "origin": origin,
                "budget": budget,
                "available_time": available_time,
                "aircraft_type": aircraft_type
            }
        )
    
    async def calculate_shortest_path(
        self,
        start: str,
        end: str,
        criterion: str = "distance"
    ) -> Dict[str, Any]:
        """Calculate shortest path between airports."""
        return await self.post(
            "/planning/shortest-path",
            {
                "start": start,
                "end": end,
                "criterion": criterion
            }
        )
    
    async def compare_routes(self, start: str, end: str) -> Dict[str, Any]:
        """Compare routes by different criteria."""
        return await self.post("/planning/compare-routes", {"start": start, "end": end})
    
    # Network endpoints
    async def get_network_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        return await self.get("/network/statistics")
    
    async def get_airport_details(self, airport_id: str) -> Dict[str, Any]:
        """Get details about an airport."""
        return await self.get(f"/network/airport/{airport_id}")
    
    async def get_hub_airports(self) -> Dict[str, Any]:
        """Get all hub airports."""
        return await self.get("/network/hubs")
    
    async def analyze_connectivity(self, airport_id: str) -> Dict[str, Any]:
        """Analyze airport connectivity."""
        return await self.post(f"/network/connectivity/{airport_id}")
    
    # Simulation endpoints
    async def run_simulation(self, network_file: str = "../data/sample_network.json") -> Dict[str, Any]:
        """Run simulation."""
        return await self.post("/simulation/run", {"network_file": network_file})
    
    async def get_scenarios(self) -> Dict[str, Any]:
        """Get available scenarios."""
        return await self.get("/simulation/scenarios")


# Global API client instance
api_client = APIClient()
