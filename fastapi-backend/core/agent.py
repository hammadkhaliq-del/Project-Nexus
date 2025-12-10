"""
Vehicle Agent Base Class
Represents smart cars and emergency vehicles in the simulation
"""
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import random

from utils.logger import setup_logger

logger = setup_logger(__name__)


class VehicleType(Enum):
    """Vehicle categories"""
    NORMAL = "normal"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"


class VehicleStatus(Enum):
    """Vehicle operational status"""
    IDLE = "idle"
    MOVING = "moving"
    RESPONDING = "responding"
    STUCK = "stuck"
    CHARGING = "charging"


@dataclass
class Vehicle:
    """
    Base Vehicle Agent
    All vehicles navigate using A* search and respond to city conditions
    """
    id: str
    type: VehicleType
    position: Tuple[int, int]
    destination: Optional[Tuple[int, int]] = None
    path: List[Tuple[int, int]] = field(default_factory=list)
    
    # Vehicle stats
    speed: float = 50.0  # 0-100
    health: float = 100.0  # 0-100
    energy: float = 100.0  # 0-100
    
    # State
    status: VehicleStatus = VehicleStatus.IDLE
    stuck_counter: int = 0
    
    # Emergency vehicle properties
    is_emergency: bool = False
    active_mission: Optional[str] = None  # Emergency ID
    
    def __post_init__(self):
        self.is_emergency = self.type in [VehicleType.AMBULANCE, VehicleType.FIRE_TRUCK]
    
    def update(self, tick: int):
        """Update vehicle state each tick"""
        # Drain energy while moving
        if self.status == VehicleStatus.MOVING:
            self.energy = max(0, self.energy - 0.1)
        
        # Slow energy recovery while idle
        if self.status == VehicleStatus.IDLE:
            self.energy = min(100, self.energy + 0.2)
        
        # Check for low energy
        if self.energy < 25 and self.status != VehicleStatus.CHARGING:
            logger.warning(f"Vehicle {self.id} low on energy: {self.energy:.1f}%")
        
        # Random health degradation (wear and tear)
        if random.random() < 0.001:  # 0.1% chance per tick
            self.health = max(0, self.health - random.uniform(1, 5))
    
    def move_along_path(self) -> bool:
        """
        Move one step along the path
        Returns True if reached destination, False otherwise
        """
        if not self.path:
            self.status = VehicleStatus.IDLE
            return True
        
        # Get next position
        next_pos = self.path[0]
        
        # Move to next position
        self.position = next_pos
        self.path.pop(0)
        
        self.status = VehicleStatus.MOVING
        self.stuck_counter = 0
        
        # Check if reached destination
        if not self.path:
            self.status = VehicleStatus.IDLE
            self.destination = None
            return True
        
        return False
    
    def set_path(self, path: List[Tuple[int, int]]):
        """Set new navigation path"""
        self.path = path
        if path:
            self.destination = path[-1]
            self.status = VehicleStatus.MOVING
            logger.debug(f"Vehicle {self.id} path set: {len(path)} steps")
        else:
            logger.warning(f"Vehicle {self.id} received empty path")
    
    def assign_mission(self, emergency_id: str, destination: Tuple[int, int]):
        """Assign emergency mission (for emergency vehicles)"""
        if not self.is_emergency:
            logger.error(f"Cannot assign mission to non-emergency vehicle {self.id}")
            return
        
        self.active_mission = emergency_id
        self.destination = destination
        self.status = VehicleStatus.RESPONDING
        logger.info(f"Emergency vehicle {self.id} assigned to {emergency_id}")
    
    def complete_mission(self):
        """Complete current mission"""
        if self.active_mission:
            logger.info(f"Emergency vehicle {self.id} completed mission {self.active_mission}")
            self.active_mission = None
            self.status = VehicleStatus.IDLE
    
    def is_stuck(self) -> bool:
        """Check if vehicle is stuck (blocked path)"""
        return self.stuck_counter > 5
    
    def increment_stuck(self):
        """Increment stuck counter when unable to move"""
        self.stuck_counter += 1
        if self.stuck_counter > 5:
            self.status = VehicleStatus.STUCK
            logger.warning(f"Vehicle {self.id} is stuck at {self.position}")
    
    def get_state_dict(self) -> dict:
        """Get vehicle state as dictionary for API/WebSocket"""
        return {
            "id": self.id,
            "type": self.type.value,
            "position": {"x": self.position[0], "y": self.position[1]},
            "destination": {"x": self.destination[0], "y": self.destination[1]} if self.destination else None,
            "path": [{"x": p[0], "y": p[1]} for p in self.path] if self.path else [],
            "speed": self.speed,
            "health": self.health,
            "energy": self.energy,
            "is_emergency": self.is_emergency,
            "active_mission": self.active_mission,
            "status": self.status.value
        }


def create_vehicle(vehicle_id: str, vehicle_type: VehicleType, start_pos: Tuple[int, int]) -> Vehicle:
    """Factory function to create vehicles with appropriate stats"""
    if vehicle_type == VehicleType.AMBULANCE:
        return Vehicle(
            id=vehicle_id,
            type=vehicle_type,
            position=start_pos,
            speed=70.0,
            health=100.0,
            energy=100.0
        )
    elif vehicle_type == VehicleType.FIRE_TRUCK:
        return Vehicle(
            id=vehicle_id,
            type=vehicle_type,
            position=start_pos,
            speed=65.0,
            health=100.0,
            energy=100.0
        )
    else:  # Normal vehicle
        return Vehicle(
            id=vehicle_id,
            type=vehicle_type,
            position=start_pos,
            speed=random.uniform(40, 60),
            health=100.0,
            energy=random.uniform(70, 100)
        )