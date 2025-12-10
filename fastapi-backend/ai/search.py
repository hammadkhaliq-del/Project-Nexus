"""
Search Engine - Pathfinding Algorithms
Implements A*, Dijkstra, and BFS for vehicle navigation
"""
import heapq
from typing import List, Tuple, Optional, Dict, Set
from collections import deque
from dataclasses import dataclass, field

from core.graph import GridGraph
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass(order=True)
class PriorityNode:
    """Node for priority queue"""
    priority: float
    position: Tuple[int, int] = field(compare=False)
    path: List[Tuple[int, int]] = field(default_factory=list, compare=False)


class SearchEngine:
    """
    AI Engine #1: Search-based pathfinding
    Provides optimal routing for all vehicles using classic search algorithms
    """
    
    def __init__(self, graph: GridGraph):
        self.graph = graph
        self.algorithm_stats = {
            "astar": {"calls": 0, "successes": 0, "avg_path_length": 0},
            "dijkstra": {"calls": 0, "successes": 0, "avg_path_length": 0},
            "bfs": {"calls": 0, "successes": 0, "avg_path_length": 0}
        }
    
    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        algorithm: str = "astar"
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find path using specified algorithm
        
        Args:
            start: Starting position
            goal: Goal position
            algorithm: "astar", "dijkstra", or "bfs"
        
        Returns:
            List of positions forming the path, or None if no path exists
        """
        # Validate positions
        if not self.graph.is_valid_position(start):
            logger.error(f"Invalid start position: {start}")
            return None
        
        if not self.graph.is_valid_position(goal):
            logger.error(f"Invalid goal position: {goal}")
            return None
        
        # Select algorithm
        if algorithm.lower() == "astar":
            path = self._astar(start, goal)
        elif algorithm.lower() == "dijkstra":
            path = self._dijkstra(start, goal)
        elif algorithm.lower() == "bfs":
            path = self._bfs(start, goal)
        else:
            logger.error(f"Unknown algorithm: {algorithm}")
            return None
        
        # Update statistics
        self.algorithm_stats[algorithm.lower()]["calls"] += 1
        if path:
            self.algorithm_stats[algorithm.lower()]["successes"] += 1
            self._update_avg_path_length(algorithm.lower(), len(path))
        
        return path
    
    def _astar(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        A* Algorithm - Optimal pathfinding with heuristic
        Uses f(n) = g(n) + h(n) where:
        - g(n) = actual cost from start
        - h(n) = heuristic estimate to goal
        """
        frontier = []
        heapq.heappush(frontier, PriorityNode(0, start, [start]))
        
        visited: Set[Tuple[int, int]] = set()
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0}
        
        nodes_explored = 0
        
        while frontier:
            current_node = heapq.heappop(frontier)
            current_pos = current_node.position
            current_path = current_node.path
            
            # Goal check
            if current_pos == goal:
                logger.debug(f"A* found path: {len(current_path)} steps, {nodes_explored} nodes explored")
                return current_path
            
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            nodes_explored += 1
            
            # Expand neighbors
            for neighbor in self.graph.get_neighbors(current_pos):
                new_cost = cost_so_far[current_pos] + self.graph.get_cost(current_pos, neighbor)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.graph.heuristic(neighbor, goal)
                    new_path = current_path + [neighbor]
                    heapq.heappush(frontier, PriorityNode(priority, neighbor, new_path))
        
        logger.warning(f"A* failed to find path from {start} to {goal}")
        return None
    
    def _dijkstra(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Dijkstra's Algorithm - Guaranteed optimal path (no heuristic)
        Uses f(n) = g(n) only
        """
        frontier = []
        heapq.heappush(frontier, PriorityNode(0, start, [start]))
        
        visited: Set[Tuple[int, int]] = set()
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0}
        
        nodes_explored = 0
        
        while frontier:
            current_node = heapq.heappop(frontier)
            current_pos = current_node.position
            current_path = current_node.path
            
            # Goal check
            if current_pos == goal:
                logger.debug(f"Dijkstra found path: {len(current_path)} steps, {nodes_explored} nodes explored")
                return current_path
            
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            nodes_explored += 1
            
            # Expand neighbors
            for neighbor in self.graph.get_neighbors(current_pos):
                new_cost = cost_so_far[current_pos] + self.graph.get_cost(current_pos, neighbor)
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    new_path = current_path + [neighbor]
                    heapq.heappush(frontier, PriorityNode(new_cost, neighbor, new_path))
        
        logger.warning(f"Dijkstra failed to find path from {start} to {goal}")
        return None
    
    def _bfs(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """
        Breadth-First Search - Finds shortest path in unweighted graph
        Explores nodes level by level
        """
        queue = deque([(start, [start])])
        visited: Set[Tuple[int, int]] = {start}
        
        nodes_explored = 0
        
        while queue:
            current_pos, current_path = queue.popleft()
            nodes_explored += 1
            
            # Goal check
            if current_pos == goal:
                logger.debug(f"BFS found path: {len(current_path)} steps, {nodes_explored} nodes explored")
                return current_path
            
            # Expand neighbors
            for neighbor in self.graph.get_neighbors(current_pos):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = current_path + [neighbor]
                    queue.append((neighbor, new_path))
        
        logger.warning(f"BFS failed to find path from {start} to {goal}")
        return None
    
    def _update_avg_path_length(self, algorithm: str, path_length: int):
        """Update average path length statistic"""
        stats = self.algorithm_stats[algorithm]
        current_avg = stats["avg_path_length"]
        successes = stats["successes"]
        
        # Running average
        new_avg = ((current_avg * (successes - 1)) + path_length) / successes
        stats["avg_path_length"] = new_avg
    
    def get_stats(self) -> dict:
        """Get search engine statistics"""
        return self.algorithm_stats
    
    def generate_explanation(
        self,
        algorithm: str,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        path_length: Optional[int]
    ) -> str:
        """Generate natural language explanation for XAI"""
        if path_length is None:
            return (
                f"Pathfinding failed using {algorithm.upper()}. "
                f"No valid path exists from {start} to {goal}. "
                f"This could be due to blocked roads or unreachable destination."
            )
        
        algorithm_descriptions = {
            "astar": "A* (optimal with heuristic guidance)",
            "dijkstra": "Dijkstra's algorithm (guaranteed optimal)",
            "bfs": "Breadth-First Search (shortest in unweighted graph)"
        }
        
        algo_desc = algorithm_descriptions.get(algorithm.lower(), algorithm)
        
        return (
            f"Navigation planned using {algo_desc}. "
            f"Route from {start} to {goal} calculated as {path_length} steps. "
            f"Path considers current road blocks and weather conditions. "
            f"Vehicle will follow optimal route to minimize travel time and energy consumption."
        )