# Informe de revisión del proyecto SkyRoute Planner

## 1. Objetivo

Este documento consolida la revisión del proyecto frente al enunciado original y frente a las anotaciones del profesor. También resume los refactors ya aplicados para reducir redundancia y mejorar la mantenibilidad de la base de código.

## 2. Estado general del proyecto

El proyecto tiene una base funcional sólida para modelar la red aérea, cargar el JSON, ejecutar búsquedas y ofrecer planificación básica y avanzada.

Sin embargo, antes de la revisión había redundancias importantes entre la capa académica del grafo y la capa de dominio. Esas redundancias ya fueron corregidas parcialmente con refactors puntuales.

## 3. Cumplimientos principales del enunciado

### 3.1 Carga y modelado de la red

- El JSON se carga y valida en `src/utils/json_loader.py`.
- Los aeropuertos, rutas y configuración global se convierten en objetos del sistema.
- La red usa un grafo dirigido con listas de adyacencia.

### 3.2 Algoritmos y planificación

- Se implementa Dijkstra con criterios de distancia, costo y tiempo.
- Se implementa planificación básica por DFS y backtracking.
- Se implementa planificación dinámica con sesiones interactivas, trabajos, actividades, alojamiento y comidas.
- Se contempla la interrupción de rutas y el recálculo del itinerario.

### 3.3 Visualización y API

- Existe backend FastAPI en `api/main.py`.
- Existe frontend con visualización gráfica e ինտերacción con el backend.

## 4. Observaciones del profesor y verificación técnica

### 4.1 Redundancia entre `Vertice` y `Airport`

Antes existía redundancia entre la clase académica y la clase de dominio. Esto se revisó y se corrigió:

- `Airport` ya no hereda de `Vertice`.
- `Airport` ahora funciona como modelo de dominio autónomo con la interfaz mínima requerida por los algoritmos.
- Se eliminó la duplicidad de identidad y se conservó compatibilidad con el resto del sistema.

Archivo afectado:

- `src/core/airport.py`

### 4.2 Redundancia entre `Grafo` y `Graph`

Antes `Grafo` y `Graph` guardaban la misma información en diccionarios distintos. Esto también se corrigió:

- `Graph.airports` ahora usa el mismo almacenamiento que `Grafo.vertices`.
- Se redujo la duplicidad estructural.
- `add_route()` quedó apoyado en una sola lista de adyacencia.

Archivos afectados:

- `src/core/base_graph.py`
- `src/core/graph.py`

### 4.3 Redundancia entre `Arista` y `Route`

Se depuró la clase `Route`:

- Se eliminó la reasignación redundante de peso en el constructor.
- Se unificó el manejo de disponibilidad de la ruta.
- Se dejó `blocked` como alias de compatibilidad mientras se estabiliza el resto del sistema.

Archivo afectado:

- `src/core/route.py`

### 4.4 Cálculo de peso en `Route.update_weight()`

Se refactorizó el cálculo del peso para:

- Normalizar el criterio recibido.
- Centralizar la lógica de selección por criterio.
- Lanzar un error claro si no hay aeronaves para optimizar costo o tiempo.

Archivo afectado:

- `src/core/route.py`

## 5. Mejoras de arquitectura ya aplicadas

- Se simplificó la relación entre modelo académico y dominio.
- Se redujeron puntos duplicados de estado.
- Se fortaleció la compatibilidad de la capa de algoritmos sin reescribir el sistema completo.
- Se mantuvo la API existente para no romper el flujo de ejecución.

## 6. Riesgos y pendientes técnicos

- La planificación por DFS puede crecer de forma exponencial en redes grandes.
- Aún sería recomendable agregar pruebas automáticas más amplias para algoritmos y sesiones dinámicas.
- Falta consolidar documentación de entrega final en PDF y, si aplica, generar el manual técnico y el manual de usuario.
- Sería útil unificar aún más el contrato de datos y reforzarlo con validación formal de esquema.

## 7. Conclusión

El proyecto ya supera la parte más crítica de la revisión estructural del profesor. Las principales redundancias del modelo se corrigieron y la arquitectura quedó más clara y mantenible.

El siguiente paso recomendado es cerrar la documentación final de entrega y, si se desea, añadir pruebas unitarias para asegurar que los refactors no introdujeron regresiones.
