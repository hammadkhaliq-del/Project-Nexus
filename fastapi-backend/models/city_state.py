"""
Pydantic models for city state representation
Used for API responses and WebSocket messages
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
from datetime import datetime
from enum import Enum


class WeatherType(str, Enum):
    CLEAR = "clear"
    RAIN = "rain"
    SNOW = "snow"


class VehicleType(str, Enum):
    NORMAL = "normal"
    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"


class BuildingType(str, Enum):
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    HOSPITAL = "hospital"
    FIRE_STATION = "fire_station"
    PARK = "park"


class EventType(str, Enum):
    ACCIDENT = "accident"
    FIRE = "fire"
    POWER_SHORTAGE = "power_shortage"
    ROAD_BLOCK = "road_block"
    VEHICLE_MOVEMENT = "vehicle_movement"
    EMERGENCY_DISPATCH = "emergency_dispatch"
    EMERGENCY_RESOLVED = "emergency_resolved"
    CSP_ALLOCATION = "csp_allocation"
    LOGIC_ALERT = "logic_alert"


class AIEngine(str, Enum):
    SEARCH = "search"
    CSP = "csp"
    LOGIC = "logic"
    HTN = "htn"
    BAYESIAN = "bayesian"
    XAI = "xai"


# Position model
class Position(BaseModel):
    x: int
    y: int


class Path(BaseModel):
    positions: List[Position]
    length: int


# Vehicle State
class VehicleState(BaseModel):
    id: str
    type: VehicleType
    position: Position
    destination: Optional[Position] = None
    path: Optional[List[Position]] = None
    speed: float = Field(..., ge=0, le=100)
    health: float = Field(..., ge=0, le=100)
    energy: float = Field(..., ge=0, le=100)
    is_emergency: bool = False
    active_mission: Optional[str] = None
    status: str = "idle"  # idle, moving, responding, stuck


# Building State
class BuildingState(BaseModel):
    id: str
    type: BuildingType
    position: Position
    power_usage: int
    allocated_power: int
    occupancy: int = 0
    color: str  # Hex color for visualization


# Emergency State
class EmergencyState(BaseModel):
    id: str
    type: str  # accident, fire
    position: Position
    severity: int = Field(..., ge=1, le=10)
    created_tick: int
    assigned_vehicle: Optional[str] = None
    resolved: bool = False


# Complete City State
class CityState(BaseModel):
    tick: int
    weather: WeatherType
    vehicles: List[VehicleState]
    buildings: List[BuildingState]
    emergencies: List[EmergencyState]
    grid_size: int
    blocked_roads: List[Position]


# Event Log
class EventLog(BaseModel):
    id: str
    tick: int
    timestamp: datetime
    event_type: EventType
    description: str
    data: dict = {}
    severity: str = "info"  # info, warning, critical


# AI Reasoning Log
class ReasoningLog(BaseModel):
    id: str
    tick: int
    timestamp: datetime
    engine: AIEngine
    decision: str
    reasoning: str
    input_data: dict = {}
    output_data: dict = {}
    confidence: Optional[float] = None


# WebSocket Message
class WSMessage(BaseModel):
    type: str  # "event", "reasoning", "state_update", "metrics"
    timestamp: datetime
    data: dict


# Simulation Metrics
class SimulationMetrics(BaseModel):
    tick: int
    fps: float
    efficiency_score: float = Field(..., ge=0, le=100)
    total_vehicles: int
    active_vehicles: int
    total_emergencies: int
    resolved_emergencies: int
    average_response_time: float
    power_usage_percent: float
    ai_engine_status: dict