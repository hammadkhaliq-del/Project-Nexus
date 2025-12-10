"""
Event Bus System for Simulation
Handles event dispatching and subscription
"""
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

from utils.logger import setup_logger

logger = setup_logger(__name__)


class EventType(Enum):
    """Types of simulation events"""
    # Simulation lifecycle
    SIMULATION_START = "simulation_start"
    SIMULATION_PAUSE = "simulation_pause"
    SIMULATION_TICK = "simulation_tick"
    
    # Vehicle events
    VEHICLE_SPAWN = "vehicle_spawn"
    VEHICLE_MOVE = "vehicle_move"
    VEHICLE_STUCK = "vehicle_stuck"
    VEHICLE_ARRIVED = "vehicle_arrived"
    VEHICLE_LOW_ENERGY = "vehicle_low_energy"
    
    # Emergency events
    EMERGENCY_SPAWN = "emergency_spawn"
    EMERGENCY_DISPATCH = "emergency_dispatch"
    EMERGENCY_RESOLVED = "emergency_resolved"
    
    # Infrastructure events
    ROAD_BLOCKED = "road_blocked"
    ROAD_UNBLOCKED = "road_unblocked"
    POWER_ALLOCATED = "power_allocated"
    POWER_SHORTAGE = "power_shortage"
    
    # Weather events
    WEATHER_CHANGE = "weather_change"
    
    # AI events
    AI_DECISION = "ai_decision"
    AI_ALERT = "ai_alert"


@dataclass
class Event: 
    """Represents a simulation event"""
    id:  str = field(default_factory=lambda:  str(uuid.uuid4())[:8])
    type: EventType = EventType.SIMULATION_TICK
    tick: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    title: str = ""
    description:  str = ""
    severity: str = "info"  # info, warning, critical
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert event to dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "tick": self. tick,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "description": self.description,
            "severity": self. severity,
            "data": self.data
        }


class EventBus:
    """
    Central event bus for simulation
    Allows components to publish and subscribe to events
    """
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history = 500
        
        logger.info("EventBus initialized")
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event occurs
        """
        if event_type not in self.subscribers:
            self. subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        logger.debug(f"Subscriber added for {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback:  Callable):
        """Remove a subscriber"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                cb for cb in self.subscribers[event_type] if cb != callback
            ]
    
    def publish(self, event: Event):
        """
        Publish an event to all subscribers
        
        Args:
            event: Event to publish
        """
        # Store in history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self. max_history:]
        
        # Notify subscribers
        if event.type in self.subscribers:
            for callback in self.subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e: 
                    logger.error(f"Error in event subscriber: {e}")
        
        # Also notify wildcard subscribers (if any)
        if EventType.SIMULATION_TICK in self.subscribers and event.type != EventType.SIMULATION_TICK:
            pass  # Tick events handled separately
    
    def create_and_publish(
        self,
        event_type: EventType,
        tick: int,
        title: str,
        description: str,
        severity: str = "info",
        data: Dict[str, Any] = None
    ) -> Event:
        """
        Create and publish an event in one call
        
        Returns:
            The created event
        """
        event = Event(
            type=event_type,
            tick=tick,
            title=title,
            description=description,
            severity=severity,
            data=data or {}
        )
        
        self.publish(event)
        return event
    
    def get_recent_events(self, limit: int = 50, event_type: Optional[EventType] = None) -> List[Event]:
        """Get recent events, optionally filtered by type"""
        if event_type:
            filtered = [e for e in self. event_history if e.type == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]
    
    def clear_history(self):
        """Clear event history"""
        self.event_history = []
        logger.info("Event history cleared")