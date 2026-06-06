"""
HTTP client for communicating with FastAPI backend.
"""

import httpx
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
            self.client = None
    
    async def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make GET request."""
        try:
            client = await self._get_client()
            response = await client.get(f"/api{endpoint}", **kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"GET {endpoint} failed: {str(e)}")
    
    async def post(
        self,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make POST request."""
        try:
            client = await self._get_client()
            response = await client.post(
                f"/api{endpoint}",
                json=data,
                params=params,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            detail = e.response.text
            try:
                payload = e.response.json()
                if isinstance(payload, dict) and payload.get("detail"):
                    detail = payload["detail"]
            except Exception:
                pass
            raise Exception(f"POST {endpoint} failed: {detail}") from e
        except Exception as e:
            raise Exception(f"POST {endpoint} failed: {str(e)}") from e
    
    # Graph endpoints
    async def load_graph(self, network_file: str = "../data/sample_network.json") -> Dict[str, Any]:
        """Load graph from network file."""
        return await self.post("/graph/load", params={"network_file": network_file})
    
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
        preferred_transports: List[str] = None,
        include_secondary_airports: bool = True,
    ) -> Dict[str, Any]:
        """Generate travel itinerary."""
        payload = {
            "origin": origin,
            "budget": budget,
            "available_time": available_time,
            "preferred_transports": preferred_transports or [],
            "include_secondary_airports": include_secondary_airports,
        }
        return await self.post(
            "/planning/itinerary",
            payload,
        )
    
    async def calculate_shortest_path(
        self,
        start: str,
        end: str,
        criterion: str = "distance",
        criteria: List[str] = None,
        include_secondary_airports: bool = True,
        transport_types: List[str] = None,
    ) -> Dict[str, Any]:
        """Calculate shortest path between airports."""
        payload = {
            "start": start,
            "end": end,
            "criterion": criterion,
            "criteria": criteria or [],
            "include_secondary_airports": include_secondary_airports,
            "transport_types": transport_types or [],
        }
        return await self.post(
            "/planning/shortest-path",
            payload,
        )
    
    async def compare_routes(
        self,
        start: str,
        end: str,
        criteria: List[str] = None,
        include_secondary_airports: bool = True,
        transport_types: List[str] = None,
    ) -> Dict[str, Any]:
        """Compare routes by different criteria."""
        return await self.post(
            "/planning/compare-routes",
            params={
                "start": start,
                "end": end,
                "criteria": ",".join(criteria or ["distance", "cost", "time"]),
                "include_secondary_airports": str(include_secondary_airports).lower(),
                "transport_types": ",".join(transport_types or []),
            },
        )
    
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

    # Interactive planning session endpoints
    async def create_session(
        self,
        origin: str,
        initial_budget: float,
        available_time_hours: float,
        preferred_transports: List[str] = None,
        include_secondary_airports: bool = True,
    ) -> Dict[str, Any]:
        payload = {
            "origin": origin,
            "initial_budget": initial_budget,
            "available_time_hours": available_time_hours,
            "preferred_transports": preferred_transports or [],
            "include_secondary_airports": include_secondary_airports,
        }
        return await self.post("/planning/session", payload)

    async def get_session_options(self, session_id: str) -> Dict[str, Any]:
        return await self.get(f"/planning/session/{session_id}/options")

    async def post_session_decision(self, session_id: str, decision: Dict[str, Any]) -> Dict[str, Any]:
        return await self.post(f"/planning/session/{session_id}/decision", decision)

    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        return await self.get(f"/planning/session/{session_id}/state")

    async def advance_session_transit(self, session_id: str, minutes: int) -> Dict[str, Any]:
        decision = {"type": "advance", "advance_minutes": minutes}
        return await self.post_session_decision(session_id, decision)

    async def interrupt_route(
        self,
        origin_id: str,
        destination_id: str,
        session_id: Optional[str] = None,
        reason: str = "Interrupcion operativa",
    ) -> Dict[str, Any]:
        payload = {
            "origin_id": origin_id,
            "destination_id": destination_id,
            "session_id": session_id,
            "reason": reason,
        }
        return await self.post("/planning/session/interrupt-route", payload)

    async def get_session_report(self, session_id: str) -> Dict[str, Any]:
        return await self.get(f"/planning/session/{session_id}/report")


# Global API client instance
api_client = APIClient()
