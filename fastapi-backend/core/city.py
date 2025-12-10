"""
City Environment - Smart City Grid World
Manages buildings, roads, restricted zones, weather, and spatial layout
"""
import random
from typing import List, Tuple, Set, Dict
from dataclasses import dataclass, field
from enum import Enum

from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class CellType(Enum):
    """Grid cell types"""
    ROAD = "road"
    BUILDING = "building"
    PARK = "park"
    RESTRICTED = "restricted"


class BuildingType(Enum):
    """Building categories"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    HOSPITAL = "hospital"
    FIRE_STATION = "fire_station"


@dataclass
class Building:
    """Represents a building in the city"""
    id: str
    type: BuildingType
    position: Tuple[int, int]
    power_requirement: int
    allocated_power: int = 0
    color: str = "#3a4556"
    
    def __post_init__(self):
        # Assign colors based on type
        color_map = {
            BuildingType.RESIDENTIAL: "#3a4556",
            BuildingType.COMMERCIAL: "#445566",
            BuildingType.INDUSTRIAL: "#556677",
            BuildingType.HOSPITAL: "#d73a4a",
            BuildingType.FIRE_STATION: "#f85149"
        }
        self.color = color_map.get(self.type, "#3a4556")


@dataclass
class Emergency:
    """Emergency event in the city"""
    id: str
    type: str  # "accident", "fire"
    position: Tuple[int, int]
    severity: int
    created_tick: int
    assigned_vehicle_id: str = None
    resolved: bool = False


class Weather(Enum):
    """Weather conditions affecting simulation"""
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"


class City:
    """
    Smart City Grid Environment
    20x20 grid with buildings, roads, parks, and dynamic events
    """
    
    def __init__(self, size: int = None):
        self.size = size or settings.GRID_SIZE
        self.grid: List[List[CellType]] = []
        self.buildings: List[Building] = []
        self.emergencies: List[Emergency] = []
        self.blocked_roads: Set[Tuple[int, int]] = set()
        self.weather: Weather = Weather.CLEAR
        
        # Power management
        self.total_power = settings.TOTAL_POWER
        self.power_allocated = 0
        
        # Initialize city
        self._generate_city()
        
        logger.info(f"City initialized: {self.size}x{self.size} grid, {len(self.buildings)} buildings")
    
    def _generate_city(self):
        """Generate procedural city layout"""
        # Initialize grid with roads
        self.grid = [[CellType.ROAD for _ in range(self.size)] for _ in range(self.size)]
        
        # Place buildings in zones
        self._place_critical_buildings()
        self._place_residential_zone(0, 0, 8, 8)
        self._place_commercial_zone(12, 0, 20, 8)
        self._place_industrial_zone(0, 12, 8, 20)
        
        # Add parks (green spaces)
        self._place_parks()
        
        # Add some restricted zones
        self._place_restricted_zones()
    
    def _place_critical_buildings(self):
        """Place hospital and fire station"""
        # Hospital at strategic location
        hospital_pos = (5, 10)
        self.buildings.append(Building(
            id="hospital_1",
            type=BuildingType.HOSPITAL,
            position=hospital_pos,
            power_requirement=150
        ))
        self.grid[hospital_pos[1]][hospital_pos[0]] = CellType.BUILDING
        
        # Fire station
        fire_pos = (15, 10)
        self.buildings.append(Building(
            id="fire_station_1",
            type=BuildingType.FIRE_STATION,
            position=fire_pos,
            power_requirement=100
        ))
        self.grid[fire_pos[1]][fire_pos[0]] = CellType.BUILDING
    
    def _place_residential_zone(self, x1, y1, x2, y2):
        """Place residential buildings in zone"""
        for i in range(5):
            x = random.randint(x1, x2 - 1)
            y = random.randint(y1, y2 - 1)
            if self.grid[y][x] == CellType.ROAD:
                self.buildings.append(Building(
                    id=f"residential_{i}",
                    type=BuildingType.RESIDENTIAL,
                    position=(x, y),
                    power_requirement=random.randint(30, 60)
                ))
                self.grid[y][x] = CellType.BUILDING
    
    def _place_commercial_zone(self, x1, y1, x2, y2):
        """Place commercial buildings in zone"""
        for i in range(6):
            x = random.randint(x1, x2 - 1)
            y = random.randint(y1, y2 - 1)
            if self.grid[y][x] == CellType.ROAD:
                self.buildings.append(Building(
                    id=f"commercial_{i}",
                    type=BuildingType.COMMERCIAL,
                    position=(x, y),
                    power_requirement=random.randint(50, 100)
                ))
                self.grid[y][x] = CellType.BUILDING
    
    def _place_industrial_zone(self, x1, y1, x2, y2):
        """Place industrial buildings in zone"""
        for i in range(4):
            x = random.randint(x1, x2 - 1)
            y = random.randint(y1, y2 - 1)
            if self.grid[y][x] == CellType.ROAD:
                self.buildings.append(Building(
                    id=f"industrial_{i}",
                    type=BuildingType.INDUSTRIAL,
                    position=(x, y),
                    power_requirement=random.randint(100, 200)
                ))
                self.grid[y][x] = CellType.BUILDING
    
    def _place_parks(self):
        """Place parks (green spaces)"""
        park_positions = [(10, 5), (15, 15), (5, 18)]
        for idx, pos in enumerate(park_positions):
            if self.grid[pos[1]][pos[0]] == CellType.ROAD:
                self.grid[pos[1]][pos[0]] = CellType.PARK
    
    def _place_restricted_zones(self):
        """Place restricted zones (no traffic)"""
        restricted = [(2, 2), (18, 18)]
        for pos in restricted:
            if self.grid[pos[1]][pos[0]] == CellType.ROAD:
                self.grid[pos[1]][pos[0]] = CellType.RESTRICTED
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if position is accessible for vehicles"""
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False
        
        if (x, y) in self.blocked_roads:
            return False
        
        cell = self.grid[y][x]
        return cell in [CellType.ROAD, CellType.PARK]
    
    def spawn_emergency(self, emergency_type: str, tick: int) -> Emergency:
        """Spawn random emergency event"""
        # Find valid spawn position
        attempts = 0
        while attempts < 50:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.is_walkable(x, y):
                emergency = Emergency(
                    id=f"{emergency_type}_{tick}",
                    type=emergency_type,
                    position=(x, y),
                    severity=random.randint(3, 10),
                    created_tick=tick
                )
                self.emergencies.append(emergency)
                logger.warning(f"Emergency spawned: {emergency_type} at {(x, y)}")
                return emergency
            attempts += 1
        
        return None
    
    def block_road(self, position: Tuple[int, int]):
        """Block a road (e.g., due to accident)"""
        self.blocked_roads.add(position)
        logger.info(f"Road blocked at {position}")
    
    def unblock_road(self, position: Tuple[int, int]):
        """Unblock a road"""
        if position in self.blocked_roads:
            self.blocked_roads.remove(position)
            logger.info(f"Road unblocked at {position}")
    
    def set_weather(self, weather: str):
        """Change weather conditions"""
        weather_map = {
            "clear": Weather.CLEAR,
            "rain": Weather.RAIN,
            "snow": Weather.SNOW
        }
        self.weather = weather_map.get(weather.lower(), Weather.CLEAR)
        logger.info(f"Weather changed to {self.weather.value}")
    
    def get_weather_modifier(self) -> float:
        """Get accident probability modifier based on weather"""
        modifiers = {
            Weather.CLEAR: 1.0,
            Weather.RAIN: 2.5,
            Weather.SNOW: 3.0
        }
        return modifiers.get(self.weather, 1.0)
    
    def resolve_emergency(self, emergency_id: str):
        """Mark emergency as resolved"""
        for emergency in self.emergencies:
            if emergency.id == emergency_id:
                emergency.resolved = True
                # Unblock road if it was an accident
                if emergency.type == "accident":
                    self.unblock_road(emergency.position)
                logger.info(f"Emergency resolved: {emergency_id}")
                break
    
    def get_total_power_demand(self) -> int:
        """Calculate total power demand from all buildings"""
        return sum(b.power_requirement for b in self.buildings)
    
    def reset_power_allocation(self):
        """Reset power allocation for CSP solver"""
        self.power_allocated = 0
        for building in self.buildings:
            building.allocated_power = 0