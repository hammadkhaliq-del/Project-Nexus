"""
Main Simulation Engine
Orchestrates the city simulation tick loop
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import random

from core.city import City, Weather, Emergency
from core.agent import Vehicle, VehicleType, VehicleStatus, create_vehicle
from core.graph import GridGraph
from core.events import EventBus, Event, EventType
from ai.search import SearchEngine
from ai.csp_engine import CSPEngine
from ai. logic_engine import LogicEngine
from ai.planner import HTNPlanner
from ai.bayesian import BayesianNetwork
from ai.explainability import XAIEngine, AIEngine as XAIEngineType
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SimulationEngine:
    """
    Main simulation engine that coordinates all components
    """
    
    def __init__(self):
        # Core components
        self.city: City = None
        self.graph: GridGraph = None
        self.vehicles: List[Vehicle] = []
        self.event_bus: EventBus = None
        
        # AI Engines
        self.search_engine: SearchEngine = None
        self.csp_engine: CSPEngine = None
        self.logic_engine: LogicEngine = None
        self.htn_planner: HTNPlanner = None
        self.bayesian_network: BayesianNetwork = None
        self.xai_engine: XAIEngine = None
        
        # State
        self.tick: int = 0
        self.is_running: bool = False
        self.is_paused: bool = False
        
        # Statistics
        self.stats = {
            "total_emergencies": 0,
            "resolved_emergencies": 0,
            "total_distance_traveled": 0
        }
        
        # Initialize everything
        self._initialize()
    
    def _initialize(self):
        """Initialize all simulation components"""
        logger.info("Initializing Simulation Engine...")
        
        # Create city
        self.city = City(settings.GRID_SIZE)
        
        # Create graph for pathfinding
        self.graph = GridGraph(self.city)
        
        # Create event bus
        self.event_bus = EventBus()
        
        # Initialize AI engines
        self.search_engine = SearchEngine(self.graph)
        self.csp_engine = CSPEngine(self. city)
        self.logic_engine = LogicEngine(self.city)
        self.htn_planner = HTNPlanner()
        self.bayesian_network = BayesianNetwork(self.city)
        self.xai_engine = XAIEngine()
        
        # Create vehicles
        self._spawn_vehicles()
        
        # Initial CSP run
        self. csp_engine.solve()
        
        logger.info("Simulation Engine initialized successfully")
    
    def _spawn_vehicles(self):
        """Spawn all vehicles"""
        self.vehicles = []
        
        # Spawn normal vehicles
        for i in range(settings.NUM_VEHICLES):
            pos = self._get_random_road_position()
            vehicle = create_vehicle(
                f"car_{i}",
                VehicleType. NORMAL,
                pos
            )
            self.vehicles. append(vehicle)
        
        # Spawn ambulance near hospital
        hospital = next((b for b in self.city.buildings if b.type. value == "hospital"), None)
        if hospital:
            ambulance = create_vehicle(
                "ambulance_1",
                VehicleType.AMBULANCE,
                hospital.position
            )
            self.vehicles.append(ambulance)
        
        # Spawn fire truck near fire station
        fire_station = next((b for b in self.city.buildings if b.type.value == "fire_station"), None)
        if fire_station:
            fire_truck = create_vehicle(
                "fire_truck_1",
                VehicleType. FIRE_TRUCK,
                fire_station.position
            )
            self.vehicles.append(fire_truck)
        
        logger.info(f"Spawned {len(self.vehicles)} vehicles")
    
    def _get_random_road_position(self) -> tuple:
        """Get a random walkable position"""
        attempts = 0
        while attempts < 100:
            x = random.randint(0, self.city.size - 1)
            y = random.randint(0, self. city.size - 1)
            if self.city.is_walkable(x, y):
                return (x, y)
            attempts += 1
        return (0, 0)
    
    def start(self):
        """Start the simulation"""
        self.is_running = True
        self.is_paused = False
        
        self. event_bus.create_and_publish(
            EventType.SIMULATION_START,
            self.tick,
            "Simulation Started",
            "NEXUS simulation is now running"
        )
        
        logger.info("Simulation started")
    
    def pause(self):
        """Pause the simulation"""
        self.is_paused = True
        
        self.event_bus.create_and_publish(
            EventType.SIMULATION_PAUSE,
            self.tick,
            "Simulation Paused",
            "NEXUS simulation has been paused"
        )
        
        logger.info("Simulation paused")
    
    def resume(self):
        """Resume the simulation"""
        self.is_paused = False
        logger.info("Simulation resumed")
    
    def stop(self):
        """Stop the simulation"""
        self.is_running = False
        self.is_paused = False
        logger.info("Simulation stopped")
    
    def restart(self):
        """Restart simulation with fresh state"""
        self.stop()
        self.tick = 0
        self._initialize()
        self.start()
        logger.info("Simulation restarted")
    
    def update(self) -> List[Event]:
        """
        Execute one simulation tick
        
        Returns:
            List of events that occurred this tick
        """
        if not self.is_running or self.is_paused:
            return []
        
        self.tick += 1
        events = []
        
        # 1. Update all vehicles
        for vehicle in self. vehicles:
            vehicle.update(self.tick)
            
            # Move vehicles along their paths
            if vehicle.path:
                reached = vehicle.move_along_path()
                if reached and vehicle.active_mission:
                    # Vehicle reached emergency destination
                    self._handle_mission_arrival(vehicle)
            
            # Assign random destinations to idle normal vehicles
            elif vehicle.status == VehicleStatus.IDLE and not vehicle.is_emergency:
                if random.random() < 0.1:  # 10% chance per tick
                    self._assign_random_destination(vehicle)
        
        # 2. Run CSP power allocation periodically
        if self.tick % settings.CSP_TICK_INTERVAL == 0:
            allocation = self.csp_engine. solve()
            summary = self. csp_engine.get_allocation_summary()
            
            # Log CSP decision
            self.xai_engine.explain_csp_decision(
                self.tick,
                allocation,
                settings. TOTAL_POWER,
                summary['critical_satisfied'],
                []
            )
        
        # 3. Bayesian prediction for emergencies
        num_active_vehicles = sum(1 for v in self. vehicles if v.status == VehicleStatus.MOVING)
        
        # Predict accidents
        should_spawn_accident, prob, factors = self.bayesian_network. predict_accident(
            self.tick,
            num_active_vehicles
        )
        
        if should_spawn_accident: 
            emergency = self.city.spawn_emergency("accident", self.tick)
            if emergency:
                self.stats["total_emergencies"] += 1
                self._dispatch_emergency_vehicle(emergency)
                
                self.xai_engine.explain_bayesian_decision(
                    self.tick, "accident", prob, factors, True
                )
                
                events.append(Event(
                    type=EventType. EMERGENCY_SPAWN,
                    tick=self.tick,
                    title="Accident Reported",
                    description=f"Accident at {emergency.position}",
                    severity="critical",
                    data={"emergency_id": emergency.id, "position": emergency.position}
                ))
        
        # Predict fires
        should_spawn_fire, prob, factors = self.bayesian_network.predict_fire(self.tick)
        
        if should_spawn_fire:
            emergency = self.city.spawn_emergency("fire", self.tick)
            if emergency:
                self.stats["total_emergencies"] += 1
                self._dispatch_emergency_vehicle(emergency)
                
                self.xai_engine.explain_bayesian_decision(
                    self.tick, "fire", prob, factors, True
                )
                
                events.append(Event(
                    type=EventType.EMERGENCY_SPAWN,
                    tick=self.tick,
                    title="Fire Reported",
                    description=f"Fire at {emergency.position}",
                    severity="critical",
                    data={"emergency_id": emergency.id, "position": emergency.position}
                ))
        
        # 4. Run logic engine for anomaly detection
        alerts = self.logic_engine.evaluate(self.tick, self.vehicles)
        for alert in alerts:
            self. xai_engine.explain_logic_decision(
                self.tick,
                alert.rule_id,
                alert.rule_name,
                alert.message,
                alert.alert_level. value,
                alert.context
            )
            
            events.append(Event(
                type=EventType.AI_ALERT,
                tick=self.tick,
                title=alert.rule_name,
                description=alert.message,
                severity=alert.alert_level.value,
                data={"rule_id": alert.rule_id}
            ))
        
        return events
    
    def _assign_random_destination(self, vehicle: Vehicle):
        """Assign a random destination to a vehicle"""
        destination = self._get_random_road_position()
        
        # Use A* to find path
        path = self.search_engine.find_path(
            vehicle.position,
            destination,
            algorithm="astar"
        )
        
        if path:
            vehicle. set_path(path[1: ])  # Exclude starting position
            
            self.xai_engine.explain_search_decision(
                self.tick,
                "astar",
                vehicle.position,
                destination,
                len(path),
                len(path) * 2  # Approximate nodes explored
            )
    
    def _dispatch_emergency_vehicle(self, emergency: Emergency):
        """Dispatch appropriate emergency vehicle"""
        # Find available emergency vehicle
        if emergency.type == "accident": 
            vehicle = next(
                (v for v in self.vehicles 
                 if v.type == VehicleType.AMBULANCE and v.active_mission is None),
                None
            )
        else:  # fire
            vehicle = next(
                (v for v in self.vehicles 
                 if v.type == VehicleType. FIRE_TRUCK and v. active_mission is None),
                None
            )
        
        if not vehicle:
            logger.warning(f"No available emergency vehicle for {emergency.id}")
            return
        
        # Calculate path to emergency
        path = self. search_engine.find_path(
            vehicle.position,
            emergency.position,
            algorithm="astar"
        )
        
        if path:
            vehicle.assign_mission(emergency.id, emergency.position)
            vehicle.set_path(path[1:])
            emergency.assigned_vehicle_id = vehicle.id
            
            # Create HTN plan
            plan = self.htn_planner.create_plan(emergency, vehicle, self.tick)
            
            if plan:
                self.xai_engine.explain_htn_decision(
                    self.tick,
                    plan.id,
                    emergency.id,
                    vehicle.id,
                    len(plan.get_all_tasks()),
                    plan.get_task_tree_string()
                )
            
            logger.info(f"Dispatched {vehicle.id} to {emergency. id}")
    
    def _handle_mission_arrival(self, vehicle: Vehicle):
        """Handle emergency vehicle arriving at destination"""
        emergency_id = vehicle.active_mission
        
        # Find and resolve emergency
        for emergency in self.city.emergencies:
            if emergency.id == emergency_id:
                self.city.resolve_emergency(emergency_id)
                self.stats["resolved_emergencies"] += 1
                
                # Send vehicle back to base
                base_pos = self._get_vehicle_base(vehicle)
                path = self.search_engine.find_path(
                    vehicle.position,
                    base_pos,
                    algorithm="astar"
                )
                
                vehicle.complete_mission()
                
                if path:
                    vehicle.set_path(path[1:])
                
                logger.info(f"Emergency {emergency_id} resolved by {vehicle.id}")
                break
    
    def _get_vehicle_base(self, vehicle: Vehicle) -> tuple:
        """Get base position for emergency vehicle"""
        if vehicle.type == VehicleType.AMBULANCE:
            hospital = next(
                (b for b in self.city.buildings if b.type.value == "hospital"),
                None
            )
            return hospital.position if hospital else (5, 10)
        else: 
            fire_station = next(
                (b for b in self.city. buildings if b.type.value == "fire_station"),
                None
            )
            return fire_station.position if fire_station else (15, 10)
    
    def set_weather(self, weather:  str):
        """Change weather conditions"""
        self.city.set_weather(weather)
        
        self.event_bus.create_and_publish(
            EventType.WEATHER_CHANGE,
            self. tick,
            "Weather Changed",
            f"Weather is now {weather}",
            data={"weather": weather}
        )
    
    def get_state(self) -> dict:
        """Get complete simulation state"""
        return {
            "tick": self.tick,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "weather": self.city.weather. value,
            "grid_size": self.city.size,
            "vehicles": [v.get_state_dict() for v in self.vehicles],
            "buildings": [
                {
                    "id": b.id,
                    "type": b.type.value,
                    "position": {"x": b.position[0], "y": b.position[1]},
                    "power_requirement": b.power_requirement,
                    "allocated_power": b.allocated_power,
                    "color": b.color
                }
                for b in self.city.buildings
            ],
            "emergencies": [
                {
                    "id": e.id,
                    "type": e.type,
                    "position": {"x": e.position[0], "y": e.position[1]},
                    "severity": e.severity,
                    "resolved": e.resolved,
                    "assigned_vehicle": e.assigned_vehicle_id
                }
                for e in self.city. emergencies if not e.resolved
            ],
            "blocked_roads": [{"x": p[0], "y": p[1]} for p in self.city.blocked_roads],
            "stats": self.stats
        }
    
    def get_metrics(self) -> dict:
        """Get simulation metrics"""
        active_emergencies = sum(1 for e in self.city.emergencies if not e.resolved)
        active_vehicles = sum(1 for v in self.vehicles if v. status == VehicleStatus. MOVING)
        
        power_summary = self.csp_engine. get_allocation_summary()
        
        return {
            "tick": self. tick,
            "fps": settings. SIMULATION_FPS,
            "efficiency_score": self._calculate_efficiency(),
            "total_vehicles": len(self.vehicles),
            "active_vehicles": active_vehicles,
            "total_emergencies": self.stats["total_emergencies"],
            "resolved_emergencies": self.stats["resolved_emergencies"],
            "active_emergencies": active_emergencies,
            "power_utilization": power_summary["utilization_percent"],
            "weather": self.city.weather.value
        }
    
    def _calculate_efficiency(self) -> float:
        """Calculate overall system efficiency score"""
        total = self.stats["total_emergencies"]
        resolved = self.stats["resolved_emergencies"]
        
        if total == 0:
            return 100.0
        
        resolution_rate = (resolved / total) * 100
        
        # Factor in response time, power efficiency, etc.
        power_summary = self.csp_engine. get_allocation_summary()
        power_score = min(power_summary["utilization_percent"], 100)
        
        return (resolution_rate * 0.7) + (power_score * 0.3)