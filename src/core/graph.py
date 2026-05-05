"""
Graph module - Directed weighted graph with adjacency list implementation.
This module implements the main graph data structure for representing the airline network.

Classes:
    - Vertice: Represents a vertex (airport) in the graph
    - Arista: Represents an edge (route) between two vertices
    - Grafo: Main graph class containing vertices and algorithms
"""

import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


class Vertice:
    """
    Represents a vertex (airport) in the graph.
    Contains the airport identifier and adjacency list of edges.
    """
    def __init__(self, identificador):
        """
        Initialize a vertex.
        
        Args:
            identificador: Unique identifier for the vertex (airport IATA code)
        """
        self.identificador = identificador
        self.adyacencias = []

    def agregar_adyacencia(self, arista):
        """
        Add an edge to this vertex's adjacency list.
        
        Args:
            arista: Arista object representing the outgoing edge
        """
        self.adyacencias.append(arista)


class Arista:
    """
    Represents an edge between two vertices in the graph.
    Contains the destination vertex and weight of the edge.
    """
    def __init__(self, vertice_destino, peso=0):
        """
        Initialize an edge.
        
        Args:
            vertice_destino: Vertice object representing destination
            peso: Weight of the edge (cost, distance, or time)
        """
        self.vertice_destino = vertice_destino
        self.peso = peso

    def getPeso(self):
        """Get the weight of this edge."""
        return self.peso


class Grafo:
    """
    Directed weighted graph implementation using adjacency list.
    Used to represent the airline route network.
    Contains methods for graph operations including Dijkstra's algorithm
    and visualization.
    """
    def __init__(self):
        """Initialize an empty graph."""
        self.vertices = []

    def agregar_vertice(self, vertice):
        """
        Add a vertex to the graph.
        
        Args:
            vertice: Vertice object to add
        """
        self.vertices.append(vertice)

    def imprimir_grafo(self):
        """Print the graph structure showing all vertices and edges."""
        for v in self.vertices:
            print("***************************")
            print(v.identificador)
            for a in v.adyacencias:
                print(a.vertice_destino.identificador, a.getPeso())
        print("-------------------------------------")
        print("-------------------------------------")

    def visualizar(self, titulo="Visualización del Grafo con NetworkX"):
        """
        Visualize the graph using NetworkX and Matplotlib.
        
        Args:
            titulo: Title for the visualization
        """
        G_nx = nx.DiGraph()

        # Construir el grafo de networkx desde la estructura propia
        for v in self.vertices:
            for arista in v.adyacencias:
                G_nx.add_edge(
                    v.identificador,
                    arista.vertice_destino.identificador,
                    weight=arista.getPeso()
                )

        # Dibujar
        pos = nx.spring_layout(G_nx, seed=42)
        edge_labels = nx.get_edge_attributes(G_nx, 'weight')

        plt.figure(figsize=(10, 7))
        nx.draw(G_nx, pos,
                with_labels=True,
                node_color='skyblue',
                node_size=1500,
                font_size=12,
                font_weight='bold',
                arrows=True)
        nx.draw_networkx_edge_labels(G_nx, pos,
                                      edge_labels=edge_labels,
                                      font_color='red')
        plt.title(titulo, fontsize=14)
        plt.show()

    def dijkstra_simple(self, grafo, inicio_id, destino_id):
        """
        Dijkstra's algorithm implementation for finding shortest path.
        
        Args:
            grafo: Grafo object (typically self)
            inicio_id: Starting vertex identifier
            destino_id: Destination vertex identifier
            
        Returns:
            Tuple of (distances dict, predecessors dict, path list)
        """
        # Obtener todos los identificadores
        todos = [v.identificador for v in grafo.vertices]

        dist = {v: math.inf for v in todos}
        pred = {v: None for v in todos}
        dist[inicio_id] = 0

        no_visitados = set(todos)

        # Mapa de id → objeto Vertice para acceso rápido
        mapa_vertices = {v.identificador: v for v in grafo.vertices}

        print("=== Iteración inicial ===")
        for v in todos:
            print(f"{v}: ({'∞' if dist[v] == math.inf else dist[v]}, {pred[v]})")
        print()

        while no_visitados:
            # Elegir el vértice no visitado con menor distancia
            u = min(no_visitados, key=lambda v: dist[v])
            if dist[u] == math.inf:
                break

            print(f"Procesando vértice {u} con distancia {dist[u]}")
            no_visitados.remove(u)

            if u == destino_id:
                print(f"\nDestino {destino_id} alcanzado. Fin de la búsqueda.\n")
                break

            # Relajar aristas usando la estructura Arista
            vertice_actual = mapa_vertices[u]
            for arista in vertice_actual.adyacencias:
                v = arista.vertice_destino.identificador
                if v in no_visitados:
                    nueva_dist = dist[u] + arista.getPeso()
                    if nueva_dist < dist[v]:
                        dist[v] = nueva_dist
                        pred[v] = u
                        print(f"  Actualizado {v}: viene de {u}, nuevo costo = {nueva_dist}")

            print("\nEtiquetas actuales:")
            for v in todos:
                costo = "∞" if dist[v] == math.inf else dist[v]
                print(f"{v}: ({costo}, {pred[v]})")
            print()

        # Reconstruir camino más corto
        path = []
        actual = destino_id
        while actual is not None:
            path.insert(0, actual)
            actual = pred[actual]

        print(f"Camino más corto de {inicio_id} a {destino_id}: {' → '.join(str(n) for n in path)}")
        print(f"Distancia total: {dist[destino_id]}")
        return dist, pred, path

    def visualizar_con_ruta(self, path, titulo="Ruta más corta - Dijkstra"):
        """
        Visualize the graph highlighting a specific path.
        
        Args:
            path: List of vertex identifiers representing the path
            titulo: Title for the visualization
        """
        G_nx = nx.DiGraph()

        for v in self.vertices:
            for arista in v.adyacencias:
                G_nx.add_edge(
                    v.identificador,
                    arista.vertice_destino.identificador,
                    weight=arista.getPeso()
                )

        aristas_ruta = set(zip(path[:-1], path[1:]))

        edge_colors = [
            'red' if (u, v) in aristas_ruta else '#cccccc'
            for u, v in G_nx.edges()
        ]
        edge_widths = [
            3.5 if (u, v) in aristas_ruta else 1.0
            for u, v in G_nx.edges()
        ]
        node_colors = [
            'orange'     if n == path[0]  else
            'lightgreen' if n == path[-1] else
            '#ff6b6b'    if n in path     else
            'skyblue'
            for n in G_nx.nodes()
        ]

        pos = nx.spring_layout(G_nx, seed=42)
        edge_labels = nx.get_edge_attributes(G_nx, 'weight')

        plt.figure(figsize=(12, 8))

        # Dibujar nodos y aristas SIN etiquetas de nodo aún
        nx.draw(G_nx, pos,
                with_labels=False,
                node_color=node_colors,
                node_size=2000,
                arrows=True,
                arrowsize=20,
                edge_color=edge_colors,
                width=edge_widths,
                connectionstyle="arc3,rad=0.1")

        # Etiquetas de nodos por separado con fondo blanco
        nx.draw_networkx_labels(G_nx, pos,
                                font_size=12,
                                font_weight='bold',
                                bbox=dict(boxstyle="round,pad=0.3",
                                          fc="white",
                                          ec="none",
                                          alpha=0.8))

        # Etiquetas de aristas por separado con fondo blanco
        nx.draw_networkx_edge_labels(G_nx, pos,
                                     edge_labels=edge_labels,
                                     font_size=9,
                                     font_color='black',
                                     bbox=dict(boxstyle="round,pad=0.2",
                                               fc="white",
                                               ec="none",
                                               alpha=0.9),
                                     label_pos=0.35)

        leyenda = [
            Patch(color='orange',     label=f'Inicio ({path[0]})'),
            Patch(color='lightgreen', label=f'Destino ({path[-1]})'),
            Patch(color='#ff6b6b',    label='Nodos en ruta'),
            Patch(color='skyblue',    label='Otros nodos'),
        ]
        plt.legend(handles=leyenda, loc='upper left')
        plt.title(titulo, fontsize=14)
        plt.tight_layout()
        plt.show()


# Aliases for backward compatibility
Graph = Grafo
Node = Vertice
Edge = Arista
