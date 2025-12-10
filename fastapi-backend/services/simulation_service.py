"""
Simulation Service - Main orchestrator for the simulation
Wraps the core simulation engine and provides service-level functionality
"""
from typing import List, Optional
from datetime import datetime

from core.simulation import SimulationEngine
from models.events import SimulationEvent, EventSeverity, EventCategory
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SimulationService:
    """
    High-level simulation service that wraps the core engine
    Provides business logic and API-friendly interfaces
    """
    
    def __init__(self):
        logger.info("Initializing SimulationService...")
        
        # Core simulation engine
        self.engine = SimulationEngine()
        
        # Service state
        self.created_at = datetime.utcnow()
        self.last_tick_time = None
        
        logger.info("SimulationService initialized")
    
    @property
    def is_running(self) -> bool:
        """Check if simulation is running"""
        return self.engine.is_running and not self.engine.is_paused
    
    @property
    def is_paused(self) -> bool:
        """Check if simulation is paused"""
        return self.engine.is_paused
    
    @property
    def tick(self) -> int:
        """Get current tick"""
        return self.engine.tick
    
    @property
    def city(self):
        """Get city reference"""
        return self.engine. city
    
    @property
    def vehicles(self):
        """Get vehicles reference"""
        return self.engine. vehicles
    
    @property
    def event_bus(self):
        """Get event bus reference"""
        return self.engine.event_bus
    
    @property
    def search_engine(self):
        """Get search engine reference"""
        return self.engine.search_engine
    
    @property
    def csp_engine(self):
        """Get CSP engine reference"""
        return self.engine. csp_engine
    
    @property
    def logic_engine(self):
        """Get logic engine reference"""
        return self. engine.logic_engine
    
    @property
    def htn_planner(self):
        """Get HTN planner reference"""
        return self.engine.htn_planner
    
    @property
    def bayesian_network(self):
        """Get Bayesian network reference"""
        return self. engine.bayesian_network
    
    @property
    def xai_engine(self):
        """Get XAI engine reference"""
        return self.engine.xai_engine
    
    def start(self):
        """Start the simulation"""
        self.engine.start()
        logger.info("Simulation started via service")
    
    def pause(self):
        """Pause the simulation"""
        self.engine. pause()
        logger.info("Simulation paused via service")
    
    def resume(self):
        """Resume the simulation"""
        self.engine. resume()
        logger.info("Simulation resumed via service")
    
    def stop(self):
        """Stop the simulation"""
        self.engine. stop()
        logger.info("Simulation stopped via service")
    
    def restart(self):
        """Restart the simulation"""
        self.engine.restart()
        logger.info("Simulation restarted via service")
    
    def set_weather(self, weather: str):
        """Change weather conditions"""
        self.engine.set_weather(weather)
        logger.info(f"Weather changed to {weather} via service")
    
    def tick(self) -> List[SimulationEvent]:
        """
        Execute one simulation tick
        
        Returns:
            List of events that occurred this tick
        """
        self.last_tick_time = datetime.utcnow()
        
        # Execute engine tick
        core_events = self.engine.update()
        
        # Convert to SimulationEvent objects
        events = []
        for event in core_events:
            sim_event = SimulationEvent(
                id=event.id,
                tick=event.tick,
                timestamp=event.timestamp,
                event_type=event.type. value,
                category=EventCategory. SIMULATION,
                severity=EventSeverity(event.severity) if event.severity in ['info', 'warning', 'critical'] else EventSeverity.INFO,
                title=event.title,
                description=event.description,
                data=event.data
            )
            events.append(sim_event)
        
        return events
    
    def get_state(self) -> dict:
        """Get complete simulation state"""
        return self.engine.get_state()
    
    def get_metrics(self) -> dict:
        """Get simulation metrics"""
        metrics = self.engine.get_metrics()
        
        # Add service-level metrics
        metrics["service_uptime"] = (datetime.utcnow() - self.created_at).total_seconds()
        
        if self.last_tick_time:
            metrics["last_tick"] = self.last_tick_time.isoformat()
        
        return metrics
    
    def get_status(self) -> dict:
        """Get simulation status"""
        return {
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "tick": self.tick,
            "weather":  self.city.weather.value if self.city else "unknown",
            "created_at": self.created_at.isoformat(),
            "last_tick": self.last_tick_time.isoformat() if self.last_tick_time else None
        }