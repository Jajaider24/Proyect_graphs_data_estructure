"""
Network interruption service.
"""


class NetworkService:
    """
    Handles dynamic route interruptions.
    Responsibilities:
        - Block routes dynamically
        - Restore blocked routes
        - Manage network disruptions
    """
    def block_route(self, graph, origin, destination):
        """
        Block route dynamically.

        Args:
            graph:
                Graph instance.

            origin (str):
                Origin airport.

            destination (str):
                Destination airport.
        """
        graph.disable_route(origin, destination)

    def restore_route(self, graph, origin, destination):
        """
        Restore blocked route.
        Args:
            graph:
                Graph instance.

            origin (str):
                Origin airport.

            destination (str):
                Destination airport.
        """
        graph.enable_route(origin,destination)