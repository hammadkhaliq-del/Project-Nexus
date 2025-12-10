"""
NEXUS Models Package
Pydantic models for API and internal use
"""
from .city_state import (
    WeatherType,
    VehicleType,
    BuildingType,
    EventType,
    AIEngine,
    Position,
    Path,
    VehicleState,
    BuildingState,
    EmergencyState,
    CityState,
    EventLog,
    ReasoningLog,
    WSMessage,
    SimulationMetrics
)
from .user import User, UserCreate, UserInDB, UserResponse
from .events import SimulationEvent, EventSeverity

__all__ = [
    # City State
    "WeatherType",
    "VehicleType", 
    "BuildingType",
    "EventType",
    "AIEngine",
    "Position",
    "Path",
    "VehicleState",
    "BuildingState",
    "EmergencyState",
    "CityState",
    "EventLog",
    "ReasoningLog",
    "WSMessage",
    "SimulationMetrics",
    # User
    "User",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    # Events
    "SimulationEvent",
    "EventSeverity"
]