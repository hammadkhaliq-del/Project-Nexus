"""
XAI Engine - Explainability and Reasoning Transparency
Generates natural language explanations for all AI decisions
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class AIEngine(Enum):
    """AI Engine identifiers"""
    SEARCH = "search"
    CSP = "csp"
    LOGIC = "logic"
    HTN = "htn"
    BAYESIAN = "bayesian"
    XAI = "xai"


@dataclass
class ReasoningTrace:
    """Detailed reasoning trace for a decision"""
    id: str
    tick: int
    timestamp: datetime
    engine: AIEngine
    decision_type: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning_steps: List[str]
    explanation: str
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = None


class XAIEngine:
    """
    AI Engine #6: Explainability Engine
    
    Purpose:
    - Generate human-readable explanations for all AI decisions
    - Maintain reasoning traces for transparency
    - Provide confidence scores where applicable
    - Enable audit trail of decision-making process
    
    Every AI engine logs its decisions through XAI for full transparency
    """
    
    def __init__(self):
        self.reasoning_traces: List[ReasoningTrace] = []
        self.trace_counter = 0
        self.enabled = settings.XAI_ENABLED
        self.verbose = settings.XAI_VERBOSE
        
        # Statistics
        self.traces_by_engine: Dict[str, int] = {
            engine.value: 0 for engine in AIEngine
        }
        
        logger.info(f"XAI Engine initialized (Enabled: {self.enabled}, Verbose: {self.verbose})")
    
    def log_decision(
        self,
        tick: int,
        engine: AIEngine,
        decision_type: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        explanation: str,
        reasoning_steps: Optional[List[str]] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ReasoningTrace:
        """
        Log an AI decision with full reasoning trace
        
        Args:
            tick: Current simulation tick
            engine: Which AI engine made the decision
            decision_type: Type of decision (e.g., "pathfinding", "power_allocation")
            input_data: Input parameters that influenced decision
            output_data: Decision output/result
            explanation: Natural language explanation
            reasoning_steps: Optional step-by-step reasoning
            confidence: Optional confidence score (0-1)
            metadata: Additional context
        
        Returns:
            ReasoningTrace object
        """
        if not self.enabled:
            return None
        
        self.trace_counter += 1
        trace_id = f"XAI_{self.trace_counter}"
        
        trace = ReasoningTrace(
            id=trace_id,
            tick=tick,
            timestamp=datetime.now(),
            engine=engine,
            decision_type=decision_type,
            input_data=input_data or {},
            output_data=output_data or {},
            reasoning_steps=reasoning_steps or [],
            explanation=explanation,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        self.reasoning_traces.append(trace)
        self.traces_by_engine[engine.value] += 1
        
        # Limit trace history
        if len(self.reasoning_traces) > 1000:
            self.reasoning_traces = self.reasoning_traces[-1000:]
        
        if self.verbose:
            logger.info(f"XAI: {engine.value.upper()} - {decision_type}: {explanation[:100]}...")
        
        return trace
    
    def explain_search_decision(
        self,
        tick: int,
        algorithm: str,
        start: tuple,
        goal: tuple,
        path_length: Optional[int],
        nodes_explored: int
    ) -> ReasoningTrace:
        """Generate explanation for search/pathfinding decision"""
        if path_length:
            explanation = (
                f"Pathfinding using {algorithm.upper()} algorithm found optimal route "
                f"from {start} to {goal} in {path_length} steps. "
                f"Algorithm explored {nodes_explored} nodes. "
                f"Path accounts for current road blocks and weather conditions."
            )
            output = {"path_found": True, "path_length": path_length}
        else:
            explanation = (
                f"Pathfinding using {algorithm.upper()} failed to find route "
                f"from {start} to {goal}. Explored {nodes_explored} nodes. "
                f"Destination may be unreachable due to blocked roads."
            )
            output = {"path_found": False, "path_length": None}
        
        return self.log_decision(
            tick=tick,
            engine=AIEngine.SEARCH,
            decision_type="pathfinding",
            input_data={"algorithm": algorithm, "start": start, "goal": goal},
            output_data=output,
            explanation=explanation,
            reasoning_steps=[
                f"1. Initialize {algorithm} algorithm with start={start}, goal={goal}",
                f"2. Explore graph using {'heuristic guidance' if algorithm == 'astar' else 'systematic search'}",
                f"3. Nodes explored: {nodes_explored}",
                f"4. Result: {'Path found' if path_length else 'No path exists'}"
            ]
        )
    
    def explain_csp_decision(
        self,
        tick: int,
        allocation: Dict[str, int],
        total_power: int,
        constraints_satisfied: bool,
        violations: List[str]
    ) -> ReasoningTrace:
        """Generate explanation for CSP power allocation"""
        total_allocated = sum(allocation.values())
        utilization = (total_allocated / total_power) * 100
        
        if constraints_satisfied:
            explanation = (
                f"CSP Solver allocated {total_allocated}/{total_power} power units "
                f"({utilization:.1f}% utilization) across {len(allocation)} buildings. "
                f"All constraints satisfied: critical infrastructure prioritized, "
                f"no overload detected."
            )
        else:
            explanation = (
                f"CSP Solver allocated {total_allocated}/{total_power} power units "
                f"but encountered {len(violations)} constraint violations. "
                f"Critical buildings may be underpowered."
            )
        
        return self.log_decision(
            tick=tick,
            engine=AIEngine.CSP,
            decision_type="power_allocation",
            input_data={"total_power": total_power, "num_buildings": len(allocation)},
            output_data={
                "allocation": allocation,
                "total_allocated": total_allocated,
                "constraints_satisfied": constraints_satisfied
            },
            explanation=explanation,
            reasoning_steps=[
                "1. Identify power constraints for all buildings",
                "2. Sort buildings by priority (Critical > High > Normal)",
                "3. Allocate minimum power to critical buildings first",
                "4. Distribute remaining power proportionally",
                "5. Verify all constraints satisfied"
            ] + ([f"⚠️ Violation: {v}" for v in violations] if violations else []),
            confidence=1.0 if constraints_satisfied else 0.7
        )
    
    def explain_logic_decision(
        self,
        tick: int,
        rule_id: str,
        rule_name: str,
        alert_message: str,
        alert_level: str,
        context: Dict[str, Any]
    ) -> ReasoningTrace:
        """Generate explanation for logic rule firing"""
        explanation = (
            f"Logic Rule '{rule_name}' (ID: {rule_id}) triggered. "
            f"Alert Level: {alert_level.upper()}. "
            f"Reasoning: {alert_message}"
        )
        
        return self.log_decision(
            tick=tick,
            engine=AIEngine.LOGIC,
            decision_type="rule_evaluation",
            input_data={"rule_id": rule_id, "context": context},
            output_data={"alert_level": alert_level, "message": alert_message},
            explanation=explanation,
            reasoning_steps=[
                f"1. Evaluate rule condition with context: {list(context.keys())}",
                "2. Condition evaluated to TRUE",
                f"3. Execute rule action: Generate {alert_level} alert",
                f"4. Alert message: {alert_message}"
            ]
        )
    
    def explain_htn_decision(
        self,
        tick: int,
        plan_id: str,
        emergency_id: str,
        vehicle_id: str,
        num_tasks: int,
        plan_tree: str
    ) -> ReasoningTrace:
        """Generate explanation for HTN planning"""
        explanation = (
            f"HTN Planner created mission plan {plan_id} for emergency {emergency_id}. "
            f"Vehicle {vehicle_id} assigned with {num_tasks} hierarchical tasks. "
            f"Plan decomposed high-level mission into executable primitive actions."
        )
        
        return self.log_decision(
            tick=tick,
            engine=AIEngine.HTN,
            decision_type="emergency_planning",
            input_data={"emergency_id": emergency_id, "vehicle_id": vehicle_id},
            output_data={"plan_id": plan_id, "num_tasks": num_tasks},
            explanation=explanation,
            reasoning_steps=[
                "1. Identify emergency type and severity",
                "2. Select appropriate vehicle (ambulance/fire truck)",
                "3. Decompose mission: Dispatch → Navigate → Resolve → Return",
                "4. Break compound tasks into primitive actions",
                f"5. Generated {num_tasks} total tasks in hierarchy"
            ],
            metadata={"plan_tree": plan_tree}
        )
    
    def explain_bayesian_decision(
        self,
        tick: int,
        event_type: str,
        probability: float,
        factors: Dict[str, Any],
        spawned: bool
    ) -> ReasoningTrace:
        """Generate explanation for Bayesian prediction"""
        factor_str = ", ".join([f"{k}={v}" for k, v in factors.items() if not k.startswith('p_')])
        
        if spawned:
            explanation = (
                f"Bayesian Network predicted {event_type} (P={probability:.3f}) and event spawned. "
                f"Factors: {factor_str}. "
                f"Conditional probabilities combined using Bayes' rule."
            )
        else:
            explanation = (
                f"Bayesian Network evaluated {event_type} risk (P={probability:.3f}). "
                f"Probability below threshold, no event spawned. "
                f"Factors: {factor_str}."
            )
        
        multipliers = {k: v for k, v in factors.items() if k.startswith('p_')}
        
        return self.log_decision(
            tick=tick,
            engine=AIEngine.BAYESIAN,
            decision_type="event_prediction",
            input_data={"event_type": event_type, "factors": factors},
            output_data={"probability": probability, "spawned": spawned},
            explanation=explanation,
            reasoning_steps=[
                f"1. Identify evidence variables: {factor_str}",
                "2. Look up conditional probabilities from CPTs",
                f"3. Apply multipliers: {', '.join([f'{k}={v:.2f}' for k, v in multipliers.items()])}",
                f"4. Calculate P({event_type}|Evidence) = base_rate × multipliers",
                f"5. Final probability: {probability:.3f}",
                f"6. Stochastic decision: {'Spawn event' if spawned else 'No event'}"
            ],
            confidence=probability
        )
    
    def get_recent_traces(
        self,
        limit: int = 50,
        engine: Optional[AIEngine] = None
    ) -> List[ReasoningTrace]:
        """Get recent reasoning traces, optionally filtered by engine"""
        if engine:
            filtered = [t for t in self.reasoning_traces if t.engine == engine]
            return filtered[-limit:]
        return self.reasoning_traces[-limit:]
    
    def get_statistics(self) -> dict:
        """Get XAI engine statistics"""
        return {
            "enabled": self.enabled,
            "verbose": self.verbose,
            "total_traces": len(self.reasoning_traces),
            "traces_by_engine": self.traces_by_engine.copy(),
            "trace_counter": self.trace_counter
        }
    
    def generate_summary(self, tick: int) -> str:
        """Generate summary of AI activity"""
        recent = self.get_recent_traces(limit=10)
        
        if not recent:
            return "No recent AI decisions recorded."
        
        engine_counts = {}
        for trace in recent:
            engine_counts[trace.engine.value] = engine_counts.get(trace.engine.value, 0) + 1
        
        summary = (
            f"XAI Summary (Tick {tick}): "
            f"{len(recent)} recent decisions tracked. "
            f"Active engines: {', '.join([f'{k}({v})' for k, v in engine_counts.items()])}. "
            f"Total transparency traces: {len(self.reasoning_traces)}."
        )
        
        return summary