"""
Graph traversal algorithms - DFS, BFS and exploration strategies.

Functions:
    - depth_first_search(): DFS traversal
    - breadth_first_search(): BFS traversal
    - find_all_paths(): Find all possible paths between two nodes
    - find_connected_components(): Identify graph connectivity
"""

from collections import deque


def depth_first_search(graph, start_id):
    """
    Depth-First Search traversal.

    DFS explores paths deeply before backtracking.

    This algorithm is extremely important for:
        - Route exploration
        - Backtracking
        - Dynamic planning
        - Constraint satisfaction

    Time Complexity:
        O(V + E)

    Args:
        graph:
            Graph object.

        start_id (str):
            Starting airport ID.

    Returns:
        list:
            Visited airports in DFS order.
    """
    visited = []
    visited_ids = set()
    start_airport = graph.get_airport(start_id)
    
    if start_airport is None:
        return visited

    def dfs_recursive(airport):
        visited.append(airport.id)
        visited_ids.add(airport.id)
        for route in airport.routes:
            # Ignore blocked routes
            if not route.is_available:
                continue
            neighbor = route.destination
            if neighbor.id not in visited_ids:
                dfs_recursive(neighbor)
    dfs_recursive(start_airport)
    return visited


def breadth_first_search(graph, start_id):
    """
    Breadth-First Search traversal.

    BFS explores the graph level by level and is useful for:
        - Connectivity analysis
        - Reachability
        - Shortest path by number of hops

    Time Complexity:
        O(V + E)

    Args:
        graph:
            Graph object.

        start_id (str):
            Starting airport ID.

    Returns:
        list:
            Visited airports in BFS order.
    """
    visited = []
    queue = deque()
    start_airport = graph.get_airport(start_id)
    if start_airport is None:
        return visited
    visited_ids = set()
    queue.append(start_airport)
    visited_ids.add(start_airport.id)
    
    while queue:
        current_airport = queue.popleft()
        visited.append(current_airport.id)
        for route in current_airport.routes:
            # Ignore blocked routes
            if not route.is_available:
                continue
            neighbor = route.destination
            if neighbor.id not in visited_ids:
                visited_ids.add(neighbor.id)
                queue.append(neighbor)
    return visited