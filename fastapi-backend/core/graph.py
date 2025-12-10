"""
Grid Graph for Pathfinding
Provides adjacency structure for A*, Dijkstra, and BFS algorithms
"""
from typing import List, Tuple, Set, Dict
from dataclasses import dataclass

from core.city import City


@dataclass
class Node:
    """Graph node representing a grid position"""
    position: Tuple[int, int]
    neighbors: List[Tuple[int, int]]
    cost: float = 1.0  # Base movement cost


class GridGraph:
    """
    Graph representation of the city grid
    Supports 4-directional movement (N, S, E, W)
    Optionally supports 8-directional with diagonals
    """
    
    def __init__(self, city: City, allow_diagonals: bool = False):
        self.city = city
        self.size = city.size
        self.allow_diagonals = allow_diagonals
        self.nodes: Dict[Tuple[int, int], Node] = {}
        
        # Build graph
        self._build_graph()
    
    def _build_graph(self):
        """Build graph from city grid"""
        for y in range(self.size):
            for x in range(self.size):
                if self.city.is_walkable(x, y):
                    neighbors = self._get_neighbors(x, y)
                    self.nodes[(x, y)] = Node(
                        position=(x, y),
                        neighbors=neighbors
                    )
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get valid neighboring positions"""
        neighbors = []
        
        # 4-directional movement
        directions = [
            (0, -1),  # North
            (1, 0),   # East
            (0, 1),   # South
            (-1, 0),  # West
        ]
        
        # Add diagonals if enabled
        if self.allow_diagonals:
            directions.extend([
                (-1, -1), # NW
                (1, -1),  # NE
                (1, 1),   # SE
                (-1, 1),  # SW
            ])
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.city.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get neighbors for a position (updates dynamically based on blocked roads)"""
        x, y = position
        return [
            (nx, ny) for nx, ny in self._get_neighbors(x, y)
            if self.city.is_walkable(nx, ny)
        ]
    
    def get_cost(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Get movement cost between adjacent positions"""
        # Base cost
        cost = 1.0
        
        # Diagonal movement costs more
        if self.allow_diagonals:
            if abs(from_pos[0] - to_pos[0]) == 1 and abs(from_pos[1] - to_pos[1]) == 1:
                cost = 1.414  # sqrt(2)
        
        # Weather affects cost
        weather_modifier = self.city.get_weather_modifier()
        cost *= (1.0 + (weather_modifier - 1.0) * 0.3)  # Weather increases cost
        
        return cost
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Heuristic function for A* (Manhattan distance)
        For diagonal movement, can use Euclidean distance
        """
        if self.allow_diagonals:
            # Euclidean distance
            return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
        else:
            # Manhattan distance
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if position is valid and walkable"""
        return position in self.nodes and self.city.is_walkable(*position)
    
    def rebuild(self):
        """Rebuild graph (call when roads are blocked/unblocked)"""
        self._build_graph()