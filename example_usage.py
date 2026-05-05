"""
Example script demonstrating the use of Grafo, Vertice, and Arista classes.

This example shows how to:
1. Create vertices (airports)
2. Create edges (routes) between them
3. Add them to a graph
4. Execute Dijkstra's algorithm
5. Visualize the graph and routes
"""

from src.core.graph import Grafo, Vertice, Arista


def ejemplo_grafo_simple():
    """
    Create a simple graph example with test airports and routes.
    """
    print("=" * 60)
    print("EJEMPLO 1: Grafo Simple con Dijkstra")
    print("=" * 60)
    
    # Create vertices (airports)
    bog = Vertice("BOG")  # Bogotá
    mde = Vertice("MDE")  # Medellín
    cali = Vertice("CALI")  # Cali
    barranquilla = Vertice("BARR")  # Barranquilla
    
    # Create a graph and add vertices
    grafo = Grafo()
    grafo.agregar_vertice(bog)
    grafo.agregar_vertice(mde)
    grafo.agregar_vertice(cali)
    grafo.agregar_vertice(barranquilla)
    
    # Create edges with distances as weights
    # BOG → MDE (250 km)
    bog.agregar_adyacencia(Arista(mde, 250))
    
    # BOG → CALI (450 km)
    bog.agregar_adyacencia(Arista(cali, 450))
    
    # MDE → BARR (350 km)
    mde.agregar_adyacencia(Arista(barranquilla, 350))
    
    # CALI → BARR (500 km)
    cali.agregar_adyacencia(Arista(barranquilla, 500))
    
    # MDE → CALI (180 km)
    mde.agregar_adyacencia(Arista(cali, 180))
    
    # Print the graph structure
    print("\n📊 Estructura del Grafo:")
    grafo.imprimir_grafo()
    
    # Execute Dijkstra's algorithm
    print("\n🔍 Ejecutando algoritmo de Dijkstra...")
    print("Inicio: BOG, Destino: BARR\n")
    dist, pred, path = grafo.dijkstra_simple(grafo, "BOG", "BARR")
    
    # Print results
    print("\n📍 Ruta óptima encontrada:")
    print(f"Camino: {' → '.join(path)}")
    print(f"Distancia total: {dist['BARR']} km")
    
    # Visualize the graph
    print("\n🎨 Visualizando grafo completo...")
    grafo.visualizar(titulo="Red aérea colombiana - Grafo completo")
    
    # Visualize the route
    print("\n🎨 Visualizando ruta óptima...")
    grafo.visualizar_con_ruta(path, titulo=f"Ruta óptima de {path[0]} a {path[-1]} - {dist[path[-1]]} km")


def ejemplo_grafo_json():
    """
    Create a graph from JSON file and execute algorithms.
    """
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Cargar Grafo desde JSON")
    print("=" * 60)
    
    from src.utils.json_loader import load_network_from_json, build_graph_from_json
    
    try:
        # Load JSON
        print("\n📂 Cargando archivo JSON...")
        data = load_network_from_json('data/sample_network.json')
        
        # Build graph
        print("\n🏗️  Construyendo grafo...")
        grafo = build_graph_from_json(data)
        
        # Print graph structure
        print("\n📊 Estructura del grafo cargado:")
        grafo.imprimir_grafo()
        
        # Visualize
        print("\n🎨 Visualizando grafo...")
        grafo.visualizar(titulo="Red aérea - Cargada desde JSON")
        
    except FileNotFoundError:
        print("⚠️  Nota: sample_network.json aún no contiene datos de prueba.")
        print("   Primero complete el archivo JSON con datos de aeropuertos.")


if __name__ == "__main__":
    # Run example 1: Simple graph
    ejemplo_grafo_simple()
    
    # Run example 2: JSON graph (if available)
    # ejemplo_grafo_json()
    
    print("\n" + "=" * 60)
    print("✓ Ejemplos completados")
    print("=" * 60)
