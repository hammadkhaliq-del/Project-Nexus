"""
HTN Planner - Hierarchical Task Network for Emergency Response
Plans complex multi-step missions for emergency vehicles
"""
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from core.agent import Vehicle, VehicleType
from core.city import Emergency
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a single task in a plan"""
    id: str
    name: str
    type: str  # "primitive" or "compound"
    subtasks: List['Task'] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def is_primitive(self) -> bool:
        """Check if task is primitive (executable)"""
        return self.type == "primitive"
    
    def is_compound(self) -> bool:
        """Check if task is compound (needs decomposition)"""
        return self.type == "compound"


@dataclass
class Plan:
    """Complete emergency response plan"""
    id: str
    emergency_id: str
    vehicle_id: str
    root_task: Task
    created_tick: int
    status: TaskStatus = TaskStatus.PENDING
    
    def get_all_tasks(self) -> List[Task]:
        """Get flat list of all tasks"""
        tasks = []
        
        def collect_tasks(task: Task):
            tasks.append(task)
            for subtask in task.subtasks:
                collect_tasks(subtask)
        
        collect_tasks(self.root_task)
        return tasks
    
    def get_task_tree_string(self, task: Optional[Task] = None, indent: int = 0) -> str:
        """Get human-readable task tree"""
        if task is None:
            task = self.root_task
        
        status_symbol = {
            TaskStatus.PENDING: "○",
            TaskStatus.IN_PROGRESS: "◐",
            TaskStatus.COMPLETED: "●",
            TaskStatus.FAILED: "✗"
        }
        
        symbol = status_symbol.get(task.status, "?")
        result = "  " * indent + f"{symbol} {task.name}
"
        
        for subtask in task.subtasks:
            result += self.get_task_tree_string(subtask, indent + 1)
        
        return result


class HTNPlanner:
    """
    AI Engine #4: Hierarchical Task Network Planner
    Plans emergency response missions by decomposing high-level goals into executable actions
    
    Example Decomposition:
    Respond to Accident
    ├── Dispatch Ambulance
    │   ├── Assign Vehicle
    │   ├── Calculate Route
    │   └── Transmit Orders
    ├── Navigate to Scene
    │   ├── Follow Path
    │   └── Avoid Obstacles
    ├── Resolve Emergency
    │   ├── Assess Situation
    │   ├── Provide Aid
    │   └── Clear Road
    └── Return to Base
        ├── Calculate Return Route
        └── Travel to Station
    """
    
    def __init__(self):
        self.plans: Dict[str, Plan] = {}
        self.plan_counter = 0
        self.decomposition_methods = self._initialize_methods()
        
        logger.info("HTN Planner initialized")
    
    def _initialize_methods(self) -> Dict[str, Any]:
        """Initialize task decomposition methods"""
        return {
            "respond_to_accident": self._decompose_accident_response,
            "respond_to_fire": self._decompose_fire_response,
            "dispatch_vehicle": self._decompose_dispatch,
            "navigate_to_scene": self._decompose_navigation,
            "resolve_emergency": self._decompose_resolution,
            "return_to_base": self._decompose_return
        }
    
    def create_plan(
        self,
        emergency: Emergency,
        vehicle: Vehicle,
        tick: int
    ) -> Plan:
        """
        Create emergency response plan using HTN decomposition
        
        Args:
            emergency: Emergency to respond to
            vehicle: Assigned emergency vehicle
            tick: Current simulation tick
        
        Returns:
            Complete hierarchical plan
        """
        self.plan_counter += 1
        plan_id = f"PLAN_{self.plan_counter}"
        
        # Create root task based on emergency type
        if emergency.type == "accident":
            root_task = Task(
                id=f"{plan_id}_ROOT",
                name=f"Respond to Accident at {emergency.position}",
                type="compound",
                parameters={
                    "emergency_id": emergency.id,
                    "emergency_position": emergency.position,
                    "vehicle_id": vehicle.id,
                    "severity": emergency.severity
                }
            )
            self._decompose_accident_response(root_task, vehicle, emergency)
        
        elif emergency.type == "fire":
            root_task = Task(
                id=f"{plan_id}_ROOT",
                name=f"Respond to Fire at {emergency.position}",
                type="compound",
                parameters={
                    "emergency_id": emergency.id,
                    "emergency_position": emergency.position,
                    "vehicle_id": vehicle.id,
                    "severity": emergency.severity
                }
            )
            self._decompose_fire_response(root_task, vehicle, emergency)
        
        else:
            logger.error(f"Unknown emergency type: {emergency.type}")
            return None
        
        # Create plan
        plan = Plan(
            id=plan_id,
            emergency_id=emergency.id,
            vehicle_id=vehicle.id,
            root_task=root_task,
            created_tick=tick
        )
        
        self.plans[plan_id] = plan
        
        logger.info(f"HTN Plan created: {plan_id} for {emergency.type} emergency")
        logger.debug(f"Plan tree:
{plan.get_task_tree_string()}")
        
        return plan
    
    def _decompose_accident_response(self, task: Task, vehicle: Vehicle, emergency: Emergency):
        """Decompose accident response into subtasks"""
        # Dispatch
        dispatch_task = Task(
            id=f"{task.id}_DISPATCH",
            name="Dispatch Ambulance",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_dispatch(dispatch_task, vehicle, emergency)
        task.subtasks.append(dispatch_task)
        
        # Navigate
        navigate_task = Task(
            id=f"{task.id}_NAVIGATE",
            name="Navigate to Accident Scene",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_navigation(navigate_task, vehicle, emergency)
        task.subtasks.append(navigate_task)
        
        # Resolve
        resolve_task = Task(
            id=f"{task.id}_RESOLVE",
            name="Provide Medical Assistance",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_resolution(resolve_task, vehicle, emergency)
        task.subtasks.append(resolve_task)
        
        # Return
        return_task = Task(
            id=f"{task.id}_RETURN",
            name="Return to Hospital",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_return(return_task, vehicle)
        task.subtasks.append(return_task)
    
    def _decompose_fire_response(self, task: Task, vehicle: Vehicle, emergency: Emergency):
        """Decompose fire response into subtasks"""
        # Dispatch
        dispatch_task = Task(
            id=f"{task.id}_DISPATCH",
            name="Dispatch Fire Truck",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_dispatch(dispatch_task, vehicle, emergency)
        task.subtasks.append(dispatch_task)
        
        # Navigate
        navigate_task = Task(
            id=f"{task.id}_NAVIGATE",
            name="Navigate to Fire Location",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_navigation(navigate_task, vehicle, emergency)
        task.subtasks.append(navigate_task)
        
        # Resolve
        resolve_task = Task(
            id=f"{task.id}_RESOLVE",
            name="Extinguish Fire",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_resolution(resolve_task, vehicle, emergency)
        task.subtasks.append(resolve_task)
        
        # Return
        return_task = Task(
            id=f"{task.id}_RETURN",
            name="Return to Fire Station",
            type="compound",
            parameters=task.parameters
        )
        self._decompose_return(return_task, vehicle)
        task.subtasks.append(return_task)
    
    def _decompose_dispatch(self, task: Task, vehicle: Vehicle, emergency: Emergency):
        """Decompose dispatch task"""
        task.subtasks = [
            Task(
                id=f"{task.id}_1",
                name=f"Assign {vehicle.id} to emergency",
                type="primitive",
                parameters={"action": "assign_vehicle"}
            ),
            Task(
                id=f"{task.id}_2",
                name="Calculate optimal route using A*",
                type="primitive",
                parameters={"action": "calculate_route"}
            ),
            Task(
                id=f"{task.id}_3",
                name="Activate emergency lights and sirens",
                type="primitive",
                parameters={"action": "activate_emergency_mode"}
            )
        ]
    
    def _decompose_navigation(self, task: Task, vehicle: Vehicle, emergency: Emergency):
        """Decompose navigation task"""
        task.subtasks = [
            Task(
                id=f"{task.id}_1",
                name="Follow planned route",
                type="primitive",
                parameters={"action": "follow_path"}
            ),
            Task(
                id=f"{task.id}_2",
                name="Monitor for road blocks",
                type="primitive",
                parameters={"action": "monitor_obstacles"}
            ),
            Task(
                id=f"{task.id}_3",
                name="Re-route if necessary",
                type="primitive",
                parameters={"action": "replan_if_needed"}
            )
        ]
    
    def _decompose_resolution(self, task: Task, vehicle: Vehicle, emergency: Emergency):
        """Decompose emergency resolution task"""
        if emergency.type == "accident":
            task.subtasks = [
                Task(
                    id=f"{task.id}_1",
                    name="Assess casualties and injuries",
                    type="primitive",
                    parameters={"action": "assess"}
                ),
                Task(
                    id=f"{task.id}_2",
                    name="Provide first aid treatment",
                    type="primitive",
                    parameters={"action": "treat", "duration": emergency.severity * 2}
                ),
                Task(
                    id=f"{task.id}_3",
                    name="Clear accident site",
                    type="primitive",
                    parameters={"action": "clear_site"}
                )
            ]
        else:  # fire
            task.subtasks = [
                Task(
                    id=f"{task.id}_1",
                    name="Deploy firefighting equipment",
                    type="primitive",
                    parameters={"action": "deploy_equipment"}
                ),
                Task(
                    id=f"{task.id}_2",
                    name="Combat fire",
                    type="primitive",
                    parameters={"action": "fight_fire", "duration": emergency.severity * 3}
                ),
                Task(
                    id=f"{task.id}_3",
                    name="Verify fire is extinguished",
                    type="primitive",
                    parameters={"action": "verify_safe"}
                )
            ]
    
    def _decompose_return(self, task: Task, vehicle: Vehicle):
        """Decompose return to base task"""
        base_name = "Hospital" if vehicle.type == VehicleType.AMBULANCE else "Fire Station"
        
        task.subtasks = [
            Task(
                id=f"{task.id}_1",
                name=f"Calculate route to {base_name}",
                type="primitive",
                parameters={"action": "calculate_return_route"}
            ),
            Task(
                id=f"{task.id}_2",
                name=f"Travel to {base_name}",
                type="primitive",
                parameters={"action": "return_travel"}
            ),
            Task(
                id=f"{task.id}_3",
                name="Report mission complete",
                type="primitive",
                parameters={"action": "report_complete"}
            )
        ]
    
    def update_plan_status(self, plan_id: str, task_id: str, new_status: TaskStatus):
        """Update status of a specific task in a plan"""
        if plan_id not in self.plans:
            logger.error(f"Plan {plan_id} not found")
            return
        
        plan = self.plans[plan_id]
        
        # Find and update task
        for task in plan.get_all_tasks():
            if task.id == task_id:
                task.status = new_status
                logger.info(f"Task {task.name} status updated to {new_status.value}")
                break
    
    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan by ID"""
        return self.plans.get(plan_id)
    
    def generate_explanation(self, plan: Plan) -> str:
        """Generate natural language explanation of plan"""
        total_tasks = len(plan.get_all_tasks())
        completed_tasks = sum(1 for t in plan.get_all_tasks() if t.status == TaskStatus.COMPLETED)
        
        explanation = (
            f"HTN Plan {plan.id} created for emergency {plan.emergency_id}. "
            f"Vehicle {plan.vehicle_id} assigned. "
            f"Plan decomposed into {total_tasks} hierarchical tasks. "
            f"Progress: {completed_tasks}/{total_tasks} tasks completed. "
            f"
Plan Structure:
{plan.get_task_tree_string()}"
        )
        
        return explanation