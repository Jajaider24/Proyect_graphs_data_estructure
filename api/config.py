"""
API configuration and constants.
"""

API_CONFIG = {
    "HOST": "127.0.0.1",
    "PORT": 8000,
    "DEBUG": True,
    "CORS_ORIGINS": [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Allow all origins for development
    ],
    "API_PREFIX": "/api"
}

# Paths
NETWORK_DATA_PATH = "../data/sample_network.json"
