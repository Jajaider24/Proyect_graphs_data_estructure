"""
Configuration file for SkyRoute Planner.

Stores default aircraft parameters, global constraints, and application settings.
"""

# Default aircraft parameters (can be overridden in JSON)
DEFAULT_AIRCRAFT_COSTS = {
    'Commercial': 0.18,      # USD per km
    'Regional': 0.25,        # USD per km
    'Helicopter': 0.12       # USD per km
}

DEFAULT_AIRCRAFT_TIMES = {
    'Commercial': 0.7,       # minutes per km
    'Regional': 1.1,         # minutes per km
    'Helicopter': 2.5        # minutes per km
}

# Global constraints
DEFAULT_ACCOMMODATION_INTERVAL = 20    # hours between mandatory lodging
DEFAULT_FOOD_INTERVAL = 8              # hours between mandatory meals
DEFAULT_BUDGET_THRESHOLD = 0.35        # 35% of initial budget for job eligibility
DEFAULT_SUBSIDIZED_ROUTE_LIMIT = 0.20  # 20% of distance can use free routes

# UI Settings
DEBUG_MODE = False
LOG_LEVEL = 'INFO'
