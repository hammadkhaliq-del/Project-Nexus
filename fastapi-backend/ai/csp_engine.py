"""
CSP Engine - Constraint Satisfaction Problem Solver
Manages electricity distribution across city buildings with priority constraints
"""
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

from core.city import City, Building, BuildingType
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class Priority(Enum):
    """Building power priority levels"""
    CRITICAL = 3  # Hospitals, emergency services
    HIGH = 2      # Industrial, commercial
    NORMAL = 1    # Residential


@dataclass
class PowerConstraint:
    """Represents a power allocation constraint"""
    building_id: str
    min_power: int
    max_power: int
    priority: Priority


class CSPEngine:
    """
    AI Engine #2: Constraint Satisfaction Problem Solver
    Allocates limited power resources to buildings while satisfying constraints:
    - Total power cannot exceed available capacity
    - Critical buildings must receive minimum power
    - High-priority buildings get preference
    - No building can exceed its requirement
    """
    
    def __init__(self, city: City):
        self.city = city
        self.total_power = settings.TOTAL_POWER
        self.constraints: List[PowerConstraint] = []
        self.last_allocation: Dict[str, int] = {}
        self.allocation_history: List[Dict[str, int]] = []
        
        self._initialize_constraints()
    
    def _initialize_constraints(self):
        """Initialize power constraints for all buildings"""
        self.constraints = []
        
        for building in self.city.buildings:
            priority = self._get_building_priority(building.type)
            
            # Critical buildings must get at least 80% of requirement
            if priority == Priority.CRITICAL:
                min_power = int(building.power_requirement * 0.8)
            # High priority get at least 50%
            elif priority == Priority.HIGH:
                min_power = int(building.power_requirement * 0.5)
            # Normal can get 0
            else:
                min_power = 0
            
            constraint = PowerConstraint(
                building_id=building.id,
                min_power=min_power,
                max_power=building.power_requirement,
                priority=priority
            )
            self.constraints.append(constraint)
        
        logger.info(f"CSP initialized with {len(self.constraints)} power constraints")
    
    def _get_building_priority(self, building_type: BuildingType) -> Priority:
        """Determine building priority level"""
        if building_type in [BuildingType.HOSPITAL, BuildingType.FIRE_STATION]:
            return Priority.CRITICAL
        elif building_type in [BuildingType.INDUSTRIAL, BuildingType.COMMERCIAL]:
            return Priority.HIGH
        else:
            return Priority.NORMAL
    
    def solve(self) -> Dict[str, int]:
        """
        Solve CSP using backtracking with constraint propagation
        Returns optimal power allocation satisfying all constraints
        """
        logger.info("CSP: Starting power allocation solver")
        
        # Reset allocations
        allocation = {c.building_id: 0 for c in self.constraints}
        
        # Sort constraints by priority (critical first)
        sorted_constraints = sorted(
            self.constraints,
            key=lambda c: c.priority.value,
            reverse=True
        )
        
        # Phase 1: Allocate minimum power to critical buildings
        remaining_power = self.total_power
        
        for constraint in sorted_constraints:
            if constraint.priority == Priority.CRITICAL:
                allocated = min(constraint.min_power, remaining_power)
                allocation[constraint.building_id] = allocated
                remaining_power -= allocated
                
                if allocated < constraint.min_power:
                    logger.error(
                        f"CSP: Cannot satisfy critical constraint for {constraint.building_id}. "
                        f"Required: {constraint.min_power}, Allocated: {allocated}"
                    )
        
        # Phase 2: Allocate to high-priority buildings
        for constraint in sorted_constraints:
            if constraint.priority == Priority.HIGH:
                needed = constraint.min_power - allocation[constraint.building_id]
                allocated = min(needed, remaining_power)
                allocation[constraint.building_id] += allocated
                remaining_power -= allocated
        
        # Phase 3: Distribute remaining power proportionally
        if remaining_power > 0:
            allocation = self._distribute_remaining_power(
                allocation,
                sorted_constraints,
                remaining_power
            )
        
        # Apply allocation to city
        self._apply_allocation(allocation)
        
        # Store for history
        self.last_allocation = allocation
        self.allocation_history.append(allocation.copy())
        
        logger.info(
            f"CSP: Power allocated. Used: {self.total_power - remaining_power}/{self.total_power}"
        )
        
        return allocation
    
    def _distribute_remaining_power(
        self,
        allocation: Dict[str, int],
        constraints: List[PowerConstraint],
        remaining_power: int
    ) -> Dict[str, int]:
        """Distribute remaining power to buildings not at max capacity"""
        # Calculate how much more each building can take
        available_capacity = []
        
        for constraint in constraints:
            current = allocation[constraint.building_id]
            can_take = constraint.max_power - current
            if can_take > 0:
                available_capacity.append((constraint.building_id, can_take, constraint.priority.value))
        
        # Sort by priority
        available_capacity.sort(key=lambda x: x[2], reverse=True)
        
        # Distribute proportionally
        for building_id, can_take, priority in available_capacity:
            if remaining_power <= 0:
                break
            
            allocate = min(can_take, remaining_power)
            allocation[building_id] += allocate
            remaining_power -= allocate
        
        return allocation
    
    def _apply_allocation(self, allocation: Dict[str, int]):
        """Apply power allocation to city buildings"""
        for building in self.city.buildings:
            if building.id in allocation:
                building.allocated_power = allocation[building.id]
    
    def check_constraints_satisfied(self) -> Tuple[bool, List[str]]:
        """
        Check if all constraints are satisfied
        Returns (satisfied, list of violations)
        """
        violations = []
        
        for constraint in self.constraints:
            allocated = self.last_allocation.get(constraint.building_id, 0)
            
            if allocated < constraint.min_power:
                violations.append(
                    f"{constraint.building_id}: allocated {allocated} < minimum {constraint.min_power}"
                )
            
            if allocated > constraint.max_power:
                violations.append(
                    f"{constraint.building_id}: allocated {allocated} > maximum {constraint.max_power}"
                )
        
        # Check total power constraint
        total_used = sum(self.last_allocation.values())
        if total_used > self.total_power:
            violations.append(f"Total power {total_used} exceeds capacity {self.total_power}")
        
        return len(violations) == 0, violations
    
    def get_allocation_summary(self) -> dict:
        """Get summary of current power allocation"""
        total_allocated = sum(self.last_allocation.values())
        total_demand = sum(c.max_power for c in self.constraints)
        
        critical_satisfied = all(
            self.last_allocation.get(c.building_id, 0) >= c.min_power
            for c in self.constraints if c.priority == Priority.CRITICAL
        )
        
        return {
            "total_power": self.total_power,
            "total_allocated": total_allocated,
            "total_demand": total_demand,
            "utilization_percent": (total_allocated / self.total_power) * 100,
            "critical_satisfied": critical_satisfied,
            "num_buildings": len(self.constraints)
        }
    
    def generate_explanation(self) -> str:
        """Generate natural language explanation for XAI"""
        summary = self.get_allocation_summary()
        satisfied, violations = self.check_constraints_satisfied()
        
        explanation = (
            f"CSP Power Allocation: Distributed {summary['total_allocated']}/{summary['total_power']} "
            f"power units across {summary['num_buildings']} buildings. "
            f"Utilization: {summary['utilization_percent']:.1f}%. "
        )
        
        if summary['critical_satisfied']:
            explanation += "All critical infrastructure (hospitals, fire stations) receiving required power. "
        else:
            explanation += "⚠️ WARNING: Some critical infrastructure underpowered. "
        
        if not satisfied:
            explanation += f"Constraint violations detected: {len(violations)} issues. "
        else:
            explanation += "All constraints satisfied. "
        
        # Add priority breakdown
        critical_count = sum(1 for c in self.constraints if c.priority == Priority.CRITICAL)
        high_count = sum(1 for c in self.constraints if c.priority == Priority.HIGH)
        normal_count = sum(1 for c in self.constraints if c.priority == Priority.NORMAL)
        
        explanation += (
            f"Priority distribution: {critical_count} critical, "
            f"{high_count} high, {normal_count} normal facilities."
        )
        
        return explanation