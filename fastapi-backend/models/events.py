"""
Event Models for Simulation
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class EventSeverity(str, Enum):
    """Event severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class EventCategory(str, Enum):
    """Event categories"""
    SIMULATION = "simulation"
    VEHICLE = "vehicle"
    EMERGENCY = "emergency"
    POWER = "power"
    AI = "ai"
    SYSTEM = "system"


class SimulationEvent(BaseModel):
    """
    Simulation event for WebSocket broadcast
    """
    id: str
    tick: int
    timestamp: datetime = Field(default_factory=datetime. utcnow)
    event_type: str
    category: EventCategory = EventCategory.SIMULATION
    severity: EventSeverity = EventSeverity.INFO
    title: str
    description: str
    data: Dict[str, Any] = {}
    
    def dict(self, **kwargs):
        """Override dict to serialize datetime and enums"""
        d = super().dict(**kwargs)
        d['timestamp'] = self. timestamp.isoformat()
        d['category'] = self.category.value
        d['severity'] = self. severity.value
        return d


class VehicleEvent(SimulationEvent):
    """Vehicle-specific event"""
    vehicle_id:  str
    position: Dict[str, int]
    category: EventCategory = EventCategory. VEHICLE


class EmergencyEvent(SimulationEvent):
    """Emergency-specific event"""
    emergency_id: str
    emergency_type: str
    position: Dict[str, int]
    category: EventCategory = EventCategory. EMERGENCY


class AIReasoningEvent(SimulationEvent):
    """AI reasoning event for XAI"""
    engine: str
    decision: str
    reasoning_steps: List[str] = []
    confidence: Optional[float] = None
    category: EventCategory = EventCategory.AI


class PowerEvent(SimulationEvent):
    """Power allocation event"""
    total_power: int
    allocated_power: int
    utilization_percent: float
    category: EventCategory = EventCategory.POWER