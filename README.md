Proyecto #2 Grafos Estructura de datos

Jaider León
Michael Ramirez
Jhoan Sebastian Velez

# SkyRoute Planner - Guía de Inicio

## 📋 Descripción

SkyRoute Planner es un sistema completo de planificación de rutas aéreas que utiliza:
- **Backend**: FastAPI para API REST
- **Frontend**: Flet para interfaz de escritorio
- **Algoritmos**: Grafos, Dijkstra, DFS para optimización de rutas
- **Datos**: Red de aeropuertos con restricciones de viajeros

## 🏗️ Estructura del Proyecto

```
proyecto/
├── api/
│   ├── main.py                 # Entrada FastAPI
│   ├── config.py              # Configuración API
│   ├── schemas.py             # Modelos Pydantic
│   └── routes/
│       ├── graph_routes.py    # Endpoints de grafos
│       ├── planning_routes.py # Endpoints de planificación
│       ├── network_routes.py  # Endpoints de red
│       └── simulation_routes.py
│
├── frontend/
│   ├── main.py               # Entrada Flet
│   ├── config.py            # Configuración UI
│   ├── services/
│   │   └── api_client.py    # Cliente HTTP
│   └── ui/
│       ├── main_window.py   # Ventana principal
│       └── pages/
│           ├── dashboard_page.py
│           ├── network_page.py
│           ├── planning_page.py
│           ├── routes_page.py
│           └── settings_page.py
│
├── src/                      # Backend existente
│   ├── core/               # Modelos de dominio
│   ├── algorithms/         # Algoritmos
│   ├── services/          # Servicios
│   ├── models/            # Modelos
│   └── utils/             # Utilidades
│
├── data/
│   └── sample_network.json # Datos de red
│
└── requirements.txt        # Dependencias
```