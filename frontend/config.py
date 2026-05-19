"""
Frontend configuration and constants.
"""

APP_CONFIG = {
    "APP_TITLE": "SkyRoute Planner",
    "VERSION": "1.0.0",
    "WINDOW_WIDTH": 1200,
    "WINDOW_HEIGHT": 800,
    "DEBUG": True
}

API_CONFIG = {
    "BASE_URL": "http://localhost:8000",
    "API_PREFIX": "/api",
    "TIMEOUT": 30
}

# UI Theme colors
COLORS = {
    "PRIMARY": "#0066CC",
    "SECONDARY": "#00A4EF",
    "SUCCESS": "#28A745",
    "WARNING": "#FFC107",
    "DANGER": "#DC3545",
    "LIGHT": "#F8F9FA",
    "DARK": "#343A40",
    "TEXT": "#212529",
    "BORDER": "#DDD",
    "BACKGROUND": "#FFFFFF"
}

# UI Sizes
SIZES = {
    "PADDING": 16,
    "BORDER_RADIUS": 8,
    "ICON_SIZE": 24,
    "FONT_SIZE_TITLE": 24,
    "FONT_SIZE_SUBTITLE": 18,
    "FONT_SIZE_BODY": 14,
    "FONT_SIZE_SMALL": 12
}

# Navigation
NAV_ITEMS = [
    {"label": "Dashboard", "icon": "dashboard", "value": "dashboard"},
    {"label": "Red de Aeropuertos", "icon": "language", "value": "network"},
    {"label": "Mapa de Red", "icon": "account_tree", "value": "network_graph"},
    {"label": "Planificación", "icon": "route", "value": "planning"},
    {"label": "Rutas", "icon": "directions_run", "value": "routes"},
    {"label": "Configuración", "icon": "settings", "value": "settings"}
]
