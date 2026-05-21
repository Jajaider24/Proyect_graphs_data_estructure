"""
Frontend configuration and constants.
"""

APP_CONFIG = {
    "APP_TITLE": "SkyRoute Planner - Sistema de Planificación de Rutas Aéreas",
    "VERSION": "1.0.0",
    "WINDOW_WIDTH": 1200,
    "WINDOW_HEIGHT": 800,
    "DEBUG": False,  # Set to False for production
    "YEAR": 2026
}

API_CONFIG = {
    "BASE_URL": "http://localhost:8000",
    "API_PREFIX": "/api",
    "TIMEOUT": 30
}

# UI Theme colors - Professional Aviation Theme
COLORS = {
    "PRIMARY": "#0066CC",        # Professional Blue
    "SECONDARY": "#00A4EF",      # Sky Blue
    "SUCCESS": "#28A745",        # Green
    "WARNING": "#FFC107",        # Amber/Gold
    "DANGER": "#DC3545",         # Red
    "LIGHT": "#F8F9FA",          # Light Gray
    "DARK": "#343A40",           # Dark Gray
    "TEXT": "#212529",           # Charcoal
    "BORDER": "#DDD",            # Border Gray
    "BACKGROUND": "#FFFFFF",     # White
    "ACCENT": "#FF6B6B"          # Accent Red
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

# Navigation - Ordenado lógicamente
NAV_ITEMS = [
    {"label": "Dashboard", "icon": "dashboard", "value": "dashboard"},
    {"label": "Red de Aeropuertos", "icon": "language", "value": "network"},
    {"label": "Mapa de Red", "icon": "account_tree", "value": "network_graph"},
    {"label": "Planificación", "icon": "route", "value": "planning"},
    {"label": "Rutas", "icon": "directions_run", "value": "routes"},
    {"label": "Configuración", "icon": "settings", "value": "settings"}
]
