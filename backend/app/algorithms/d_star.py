"""
D* Algorithm Implementation for Dynamic Maritime Routing

Provides real-time rerouting capabilities when obstacles (weather, traffic, hazards) 
are detected along the planned route. Optimized for ship routing with incremental 
replanning to minimize computational overhead.

Key Features:
- Dynamic obstacle detection and avoidance
- Incremental replanning (only affected route segments)
- Real-time weather and hazard integration
- Optimized for maritime environments

References:
- Stentz (1994): Optimal and efficient path planning for partially-known environments
- Koenig & Likhachev (2002): D* Lite for faster replanning
- Lazarowska (2015): Ship path planning using D* algorithm
"""

import math
import heapq
from typing import List, Tuple, Dict, Set, Optional
from dataclasses import dataclass, field

from app.services.land_detection import LandDetectionService


@dataclass
class DStarNode:
    lat: float
    lon: float
    g: float = float('inf')  # Cost from start
    rhs: float = float('inf')  # One-step lookahead cost
    key: Tuple[float, float] = field(default_factory=lambda: (float('inf'), float('inf')))
    parent: Optional['DStarNode'] = None
    
    def __lt__(self, other):
        return self.key < other.key
    
    def __hash__(self):
        return hash((round(self.lat, 6), round(self.lon, 6)))
    
    def __eq__(self, other):
        return (round(self.lat, 6), round(self.lon, 6)) == (round(other.lat, 6), round(other.lon, 6))


class DStar:
    """
    D* Algorithm for Dynamic Maritime Route Planning
    
    Efficiently handles dynamic obstacles (weather, hazards) with incremental replanning.
    Optimized for ship routing scenarios where conditions change during transit.
    """
    
    def __init__(self, start: Tuple[float, float], goal: Tuple[float, float], 
                 step_size_nm: float = 20.0, max_iterations: int = 500):
        """
        Initialize D* planner for maritime routing.
        
        Args:
            start: Starting coordinates (lat, lon)
            goal: Goal coordinates (lat, lon)
            step_size_nm: Step size in nautical miles
            max_iterations: Maximum planning iterations
        """
        self.start = DStarNode(start[0], start[1])
        self.goal = DStarNode(goal[0], goal[1])
        self.step_size_nm = step_size_nm
        self.step_size_deg = step_size_nm / 60.0  # Convert to degrees
        self.max_iterations = max_iterations
        
        # Priority queue for open nodes
        self.open_list: List[DStarNode] = []
        
        # Node storage
        self.nodes: Dict[Tuple[float, float], DStarNode] = {}
        
        # Changed cells (for dynamic replanning)
        self.changed_cells: Set[Tuple[float, float]] = set()
        
        # Initialize start node
        self.start.rhs = 0
        self.start.key = self._calculate_key(self.start)
        heapq.heappush(self.open_list, self.start)
        self.nodes[(self.start.lat, self.start.lon)] = self.start
        self.nodes[(self.goal.lat, self.goal.lon)] = self.goal
    
    def _calculate_key(self, node: DStarNode) -> Tuple[float, float]:
        """Calculate priority key for node"""
        h = self._heuristic(node, self.goal)
        return (min(node.g, node.rhs) + h, min(node.g, node.rhs))
    
    def _heuristic(self, node1: DStarNode, node2: DStarNode) -> float:
        """Calculate heuristic distance between nodes (nautical miles)"""
        lat_diff = node1.lat - node2.lat
        lon_diff = node1.lon - node2.lon
        return math.sqrt(lat_diff**2 + lon_diff**2) * 60.0  # Convert to nautical miles
    
    def _get_neighbors(self, node: DStarNode) -> List[DStarNode]:
        """Get valid neighboring nodes"""
        neighbors = []
        
        # 8-directional movement
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for dlat, dlon in directions:
            new_lat = node.lat + dlat * self.step_size_deg
            new_lon = node.lon + dlon * self.step_size_deg
            
            # Check bounds
            if not (-60 <= new_lat <= 30 and 20 <= new_lon <= 120):
                continue
            
            # Check if water (not land)
            if LandDetectionService.is_point_on_land(new_lat, new_lon):
                continue
            
            neighbor_key = (round(new_lat, 6), round(new_lon, 6))
            if neighbor_key not in self.nodes:
                self.nodes[neighbor_key] = DStarNode(new_lat, new_lon)
            
            neighbors.append(self.nodes[neighbor_key])
        
        return neighbors
    
    def _get_edge_cost(self, node1: DStarNode, node2: DStarNode) -> float:
        """Calculate edge cost between two nodes"""
        return self._heuristic(node1, node2)
    
    def _update_node(self, node: DStarNode):
        """Update node and maintain priority queue consistency"""
        if node.g != node.rhs and node in self.open_list:
            # Update key and reheapify
            node.key = self._calculate_key(node)
            heapq.heapify(self.open_list)
        elif node.g != node.rhs and node not in self.open_list:
            # Add to open list
            node.key = self._calculate_key(node)
            heapq.heappush(self.open_list, node)
        elif node.g == node.rhs and node in self.open_list:
            # Remove from open list
            self.open_list.remove(node)
            heapq.heapify(self.open_list)
    
    def _compute_shortest_path(self) -> bool:
        """Main D* computation loop"""
        iterations = 0
        
        while (self.open_list and 
               (self.open_list[0].key < self._calculate_key(self.goal) or 
                self.goal.rhs != self.goal.g) and
               iterations < self.max_iterations):
            
            iterations += 1
            
            if iterations % 50 == 0:
                print(f"  [D*] Iteration {iterations}, open nodes: {len(self.open_list)}")
            
            current = heapq.heappop(self.open_list)
            
            if current.g > current.rhs:
                # Overconsistent node
                current.g = current.rhs
                for neighbor in self._get_neighbors(current):
                    if neighbor != self.start:
                        cost = self._get_edge_cost(current, neighbor)
                        neighbor.rhs = min(neighbor.rhs, current.g + cost)
                    self._update_node(neighbor)
            else:
                # Underconsistent node
                old_g = current.g
                current.g = float('inf')
                
                # Update current node
                if current != self.start:
                    min_cost = float('inf')
                    for neighbor in self._get_neighbors(current):
                        cost = self._get_edge_cost(current, neighbor)
                        if neighbor.g + cost < min_cost:
                            min_cost = neighbor.g + cost
                    current.rhs = min_cost
                self._update_node(current)
                
                # Update neighbors
                for neighbor in self._get_neighbors(current):
                    cost = self._get_edge_cost(current, neighbor)
                    if neighbor.rhs == old_g + cost and neighbor != self.start:
                        min_cost = float('inf')
                        for next_neighbor in self._get_neighbors(neighbor):
                            next_cost = self._get_edge_cost(neighbor, next_neighbor)
                            if next_neighbor.g + next_cost < min_cost:
                                min_cost = next_neighbor.g + next_cost
                        neighbor.rhs = min_cost
                    self._update_node(neighbor)
        
        return self.goal.g < float('inf')

    def plan(self) -> List[Tuple[float, float]]:
        """
        Execute D* planning algorithm.
        
        Returns:
            List of waypoints as (lat, lon) tuples
        """
        print("[D*] Starting dynamic path planning...")
        
        # Compute initial shortest path
        if not self._compute_shortest_path():
            print("[D*] No path found!")
            return []
        
        # Extract path
        path = []
        current = self.goal
        
        while current != self.start and len(path) < 1000:  # Prevent infinite loops
            path.append((current.lat, current.lon))
            
            # Find best predecessor
            best_predecessor = None
            best_cost = float('inf')
            
            for neighbor in self._get_neighbors(current):
                cost = neighbor.g + self._get_edge_cost(neighbor, current)
                if cost < best_cost:
                    best_cost = cost
                    best_predecessor = neighbor
            
            if best_predecessor is None:
                break
            
            current = best_predecessor
        
        path.append((self.start.lat, self.start.lon))
        path.reverse()
        
        print(f"[D*] Path found with {len(path)} waypoints")
        return path
    
    def replan(self, changed_obstacles: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        Dynamic replanning when obstacles change.
        
        Args:
            changed_obstacles: List of (lat, lon) coordinates where obstacles changed
            
        Returns:
            Updated path as list of (lat, lon) tuples
        """
        print(f"[D*] Replanning due to {len(changed_obstacles)} changed obstacles...")
        
        # Update changed cells
        for lat, lon in changed_obstacles:
            key = (round(lat, 6), round(lon, 6))
            self.changed_cells.add(key)
            
            # Update affected nodes
            if key in self.nodes:
                node = self.nodes[key]
                
                # Recalculate rhs for affected neighbors
                for neighbor in self._get_neighbors(node):
                    if neighbor != self.start:
                        min_cost = float('inf')
                        for next_neighbor in self._get_neighbors(neighbor):
                            cost = self._get_edge_cost(neighbor, next_neighbor)
                            if next_neighbor.g + cost < min_cost:
                                min_cost = next_neighbor.g + cost
                        neighbor.rhs = min_cost
                    self._update_node(neighbor)
        
        # Recompute shortest path
        if not self._compute_shortest_path():
            print("[D*] No alternative path found!")
            return []
        
        # Extract updated path using the same logic as plan()
        path = []
        current = self.goal
        
        while current != self.start and len(path) < 1000:
            path.append((current.lat, current.lon))
            
            # Find best predecessor
            best_predecessor = None
            best_cost = float('inf')
            
            for neighbor in self._get_neighbors(current):
                cost = neighbor.g + self._get_edge_cost(neighbor, current)
                if cost < best_cost:
                    best_cost = cost
                    best_predecessor = neighbor
            
            if best_predecessor is None:
                break
            
            current = best_predecessor
        
        path.append((self.start.lat, self.start.lon))
        path.reverse()
        
        print(f"[D*] Replanned path with {len(path)} waypoints")
        return path
