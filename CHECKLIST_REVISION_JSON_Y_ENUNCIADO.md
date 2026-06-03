# Checklist de revisión del JSON y del enunciado

## Validación del JSON de datos

- [x] El archivo JSON parsea correctamente.
- [x] El dataset contiene al menos 30 aeropuertos.
- [x] El dataset contiene rutas dirigidas.
- [x] El JSON incluye configuración global de aeronaves.
- [x] El JSON incluye intervalos de alojamiento y alimentación.
- [x] El JSON incluye aeropuertos marcados como hub.
- [x] El JSON incluye costos de alojamiento por aeropuerto.
- [x] El JSON incluye costos de alimentación por aeropuerto.
- [x] El JSON incluye actividades por aeropuerto.
- [x] El JSON incluye trabajos por aeropuerto.
- [x] El JSON incluye rutas con distancia en kilómetros.
- [x] El JSON incluye tipos de aeronave por ruta.
- [x] El JSON incluye rutas subsidiadas con `costoBase = 0`.

## Hallazgos del dataset

- [x] Cantidad de aeropuertos verificada: 30.
- [x] Cantidad de rutas verificada: 45.
- [x] Existe configuración de aeronaves para `Helice`, `Regional` y `Commercial`.
- [ ] Falta el campo explícito de aerolíneas que operan desde cada aeropuerto.
- [ ] Falta enriquecer algunos aeropuertos secundarios con actividades o trabajos si se quiere una simulación más variada.
- [ ] Conviene revisar si todas las rutas subsidiadas respetan el límite del 20% de distancia permitida durante la ejecución.

## Checklist frente al enunciado

### 1. Carga y visualización de la red aérea

- [x] El sistema carga un archivo JSON con la red.
- [x] El sistema modela aeropuertos como nodos.
- [x] El sistema modela rutas como aristas dirigidas.
- [x] El sistema conserva la distancia en km para cada ruta.
- [x] El sistema distingue hubs mediante el atributo `esHub`.
- [ ] La interfaz debe mostrar la información completa del aeropuerto al seleccionar un nodo.
- [ ] La interfaz debe mostrar la red completa con resaltado visual consistente.
- [ ] La interfaz debe mostrar claramente el tipo de aeronave disponible por ruta.
- [ ] La interfaz debe resaltar rutas bloqueadas con un color diferente.

### 2. Planificación básica de itinerario

- [x] Existe cálculo de mejor ruta por criterio de distancia.
- [x] Existe cálculo de mejor ruta por criterio de costo.
- [x] Existe cálculo de mejor ruta por criterio de tiempo.
- [x] El sistema permite excluir aeropuertos secundarios.
- [x] El sistema permite seleccionar tipos de transporte.
- [ ] La solución debe entregar dos alternativas automáticas: mayor cantidad de destinos por presupuesto y por tiempo.
- [ ] La solución debe mostrar secuencia completa de vuelos y escalas intermedias de forma clara.
- [ ] La solución debe calcular una ruta por cada criterio seleccionado cuando el usuario elija varios.
- [ ] La solución debe garantizar que se use al menos una vez cada tipo de transporte requerido por la consigna.

### 3. Planificación avanzada con gestión dinámica de presupuesto

- [x] Existe estructura para sesiones dinámicas de planificación.
- [x] Existen trabajos temporales por aeropuerto.
- [x] Existen actividades obligatorias y opcionales.
- [x] Existe lógica de alojamiento periódico.
- [x] Existe lógica de alimentación periódica.
- [x] Existe actualización del presupuesto durante el viaje.
- [x] Existe registro de trabajos, actividades y vuelos para el reporte.
- [ ] La interfaz debe permitir decisiones paso a paso durante el viaje.
- [ ] La interfaz debe mostrar las alternativas disponibles en cada momento.
- [ ] El sistema debe dejar visible el tiempo de permanencia restante por aeropuerto.
- [ ] El sistema debe dejar visible el impacto de cada decisión en presupuesto y tiempo.

### 4. Interrupciones en la red

- [x] Existe bloqueo de rutas en backend.
- [x] Existe recálculo del itinerario tras interrupción.
- [x] Existe soporte para interrupción de ruta mientras hay una sesión activa.
- [ ] La interfaz debe mostrar el vuelo en tránsito antes de permitir interrupciones.
- [ ] La interfaz debe reflejar el retorno al aeropuerto de origen cuando la ruta se interrumpe en vuelo.
- [ ] La ruta bloqueada debe resaltarse visualmente en el mapa.

### 5. Visualización de resultados y reporte final

- [x] Existe estructura de reporte final por sesión.
- [x] El reporte incluye destinos visitados.
- [x] El reporte incluye tramos volados.
- [x] El reporte incluye actividades realizadas.
- [x] El reporte incluye trabajos realizados.
- [x] El reporte incluye totales del viaje.
- [ ] El reporte final debe presentarse con formato más legible para entrega.
- [ ] El reporte debe integrarse mejor con la interfaz de usuario.

## Mejoras recomendadas después de la revisión

- [ ] Añadir pruebas automáticas para JSON, Dijkstra, planificación y sesiones dinámicas.
- [ ] Unificar completamente frontend y backend en un flujo de ejecución simple.
- [ ] Mejorar la validación del JSON con un esquema formal.
- [ ] Refinar la visualización de la red para que sea más clara y demostrable.
- [ ] Agregar documentación final: manual técnico, manual de usuario y guía de ejecución.
- [ ] Confirmar que el proyecto cumple el requisito de documentación en inglés.
- [ ] Verificar que el dataset final use correctamente rutas dirigidas y subsidiadas.

## Resumen rápido

- [x] El JSON está bien estructurado y se puede cargar.
- [x] El dataset cumple el mínimo de 30 aeropuertos.
- [x] Hay base funcional para casi todo el motor del proyecto.
- [ ] La parte más pendiente sigue siendo la experiencia visual y la entrega formal.
