"""
Simulation service layer.

This service orchestrates:
    - BFS
    - DFS
    - Dijkstra simulations
"""

from src.algorithms.traversal import (breadth_first_search, depth_first_search)
from src.algorithms.shortestpath import (dijkstra_shortest_path)

class SimulationService:
    """
    Simulation orchestration service.
    """
    def run_bfs(self, graph, origin):
        """
        Execute BFS traversal.
        """
        return breadth_first_search(graph, origin)

    def run_dfs(self, graph, origin):
        """
        Execute DFS traversal.
        """
        return depth_first_search(graph, origin)

    def run_dijkstra(self, graph, origin, destination, optimization):
        """
        Execute multicriteria Dijkstra.
        """
        return dijkstra_shortest_path(
            graph= graph,
            start_id= origin,
            end_id= destination,
            criterion= optimization
        )