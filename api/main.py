"""
FastAPI main entry point for SkyRoute Planner backend.

Provides REST API endpoints for:
    - Graph/Network management
    - Path planning algorithms
    - Route optimization
    - Simulation services
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import (
    graph_routes,
    planning_routes,
    simulation_routes,
    network_routes
)
from api.config import API_CONFIG

# Initialize FastAPI app
app = FastAPI(
    title="SkyRoute Planner API",
    description="REST API for airline route planning and optimization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_CONFIG["CORS_ORIGINS"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(graph_routes.router, prefix="/api/graph", tags=["Graph"])
app.include_router(planning_routes.router, prefix="/api/planning", tags=["Planning"])
app.include_router(simulation_routes.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(network_routes.router, prefix="/api/network", tags=["Network"])


@app.get("/")
async def root():
    """API health check endpoint."""
    return {
        "status": "active",
        "service": "SkyRoute Planner API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "detail": "Internal server error"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=API_CONFIG["HOST"],
        port=API_CONFIG["PORT"],
        reload=API_CONFIG["DEBUG"]
    )
