"""
Graph service layer.

Responsible for:
    - Loading JSON datasets
    - Building graph structures
    - Providing graph access
"""

from src.utils.json_loader import (load_network_from_json, build_graph_from_json)

class GraphService:
    """
    Graph orchestration service.
    """
    def __init__(self):
        """
        Initialize graph service.
        """
        self.graph = None

    def load_graph(self, json_path):
        """
        Load graph from JSON dataset.

        Args:
            json_path (str):
                JSON dataset path.

        Returns:
            Graph:
                Constructed graph object.
        """
        # -----------------------------------------
        # LOAD RAW JSON DATA
        # -----------------------------------------
        data = (load_network_from_json(json_path))
        # -----------------------------------------
        # BUILD GRAPH OBJECT
        # -----------------------------------------
        self.graph = (build_graph_from_json(data))
        return self.graph

    def get_graph(self):
        """
        Return current graph.
        """
        return self.graph
    
# Module-level shared GraphService instance for API usage
graph_service = GraphService()