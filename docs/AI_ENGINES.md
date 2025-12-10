# NEXUS AI Engines Documentation

## Overview

NEXUS employs 6 AI engines that work together to manage the smart city simulation: 

1. **Search Engine** - Pathfinding
2. **CSP Engine** - Resource allocation
3. **Logic Engine** - Rule-based reasoning
4. **HTN Planner** - Hierarchical planning
5. **Bayesian Network** - Probabilistic prediction
6. **XAI Engine** - Explainability

## 1. Search Engine (A*)

**File:** `ai/search.py`

### Purpose
Optimal vehicle pathfinding through the city grid. 

### Algorithms
- **A*** - Optimal with heuristic (primary)
- **Dijkstra** - Guaranteed optimal, no heuristic
- **BFS** - Shortest path in unweighted graph

### A* Implementation

```python
def _astar(self, start, goal):
    frontier = []  # Priority queue
    heapq.heappush(frontier, PriorityNode(0, start, [start]))
    
    visited = set()
    cost_so_far = {start: 0}
    
    while frontier: 
        current = heapq. heappop(frontier)
        
        if current.position == goal:
            return current.path
        
        for neighbor in self.graph.get_neighbors(current.position):
            new_cost = cost_so_far[current.position] + self. graph.get_cost(current. position, neighbor)
            
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + self.graph.heuristic(neighbor, goal)
                heapq.heappush(frontier, PriorityNode(priority, neighbor, current.path + [neighbor]))
    
    return None
```

### Heuristic
Manhattan distance for 4-directional movement: 
```python
h(n) = |x1 - x2| + |y1 - y2|
```

## 2. CSP Engine

**File:** `ai/csp_engine.py`

### Purpose
Allocate limited power resources to buildings while satisfying constraints.

### Constraints
1. Total power ≤ available capacity
2. Critical buildings get minimum 80% requirement
3. High-priority buildings get minimum 50%
4. No building exceeds its max requirement

### Priority Levels
- **CRITICAL (3):** Hospitals, Fire Stations
- **HIGH (2):** Industrial, Commercial
- **NORMAL (1):** Residential

### Algorithm
Backtracking with constraint propagation: 

```python
def solve(self):
    # Phase 1: Allocate minimum to critical
    for constraint in sorted_constraints:
        if constraint.priority == Priority.CRITICAL:
            allocate(constraint. min_power)
    
    # Phase 2: Allocate to high-priority
    for constraint in sorted_constraints: 
        if constraint.priority == Priority.HIGH:
            allocate(constraint.min_power)
    
    # Phase 3: Distribute remaining proportionally
    distribute_remaining_power()
```

## 3. Logic Engine

**File:** `ai/logic_engine.py`

### Purpose
Monitor city state and generate alerts using IF-THEN rules.

### Rules (10 total)

| ID | Name | Condition | Alert Level |
|----|------|-----------|-------------|
| R01 | Low Energy Alert | energy < 25% | WARNING |
| R02 | Engine Failure | speed < 20 AND health < 50 | CRITICAL |
| R03 | Severe Weather | weather IN (rain, snow) | WARNING |
| R04 | Traffic Jam | stuck_counter > 5 | WARNING |
| R05 | Power Shortage | utilization > 95% | CRITICAL |
| R06 | Emergency Delay | age > 50 AND ! assigned | CRITICAL |
| R07 | Multiple Emergencies | active >= 3 | CRITICAL |
| R08 | Vehicle Health | health < 30% | WARNING |
| R09 | Fire Risk | fire AND nearby_buildings > 3 | CRITICAL |
| R10 | Road Block Impact | blocked > 0 AND affected > 2 | INFO |

### Example Rule Structure

```python
Rule(
    id="R01",
    name="Low Energy Alert",
    condition=lambda ctx: ctx.get("energy", 100) < 25,
    action=lambda ctx: f"Vehicle {ctx['vehicle_id']} has low energy ({ctx['energy']:. 1f}%)",
    alert_level=AlertLevel.WARNING
)
```

## 4. HTN Planner

**File:** `ai/planner.py`

### Purpose
Create hierarchical emergency response plans. 

### Plan Structure

```
Respond to Accident
├── Dispatch Ambulance
│   ├── Assign Vehicle (primitive)
│   ├── Calculate Route (primitive)
│   └── Activate Emergency Mode (primitive)
├── Navigate to Scene
│   ├── Follow Path (primitive)
│   ├── Monitor Obstacles (primitive)
│   └── Re-route if Needed (primitive)
├── Resolve Emergency
│   ├── Assess Situation (primitive)
│   ├── Provide Aid (primitive)
│   └── Clear Site (primitive)
└── Return to Base
    ├── Calculate Return Route (primitive)
    ├── Travel to Station (primitive)
    └── Report Complete (primitive)
```

### Task Types
- **Compound:** Can be decomposed into subtasks
- **Primitive:** Directly executable actions

## 5. Bayesian Network

**File:** `ai/bayesian.py`

### Purpose
Predict accidents and fires using conditional probabilities.

### Network Structure

```
Weather ──────┐
              ├──→ P(Accident)
Rush Hour ────┤
              │
Traffic ──────┘

Weather ──────┐
              ├──→ P(Fire)
Building ─────┘
Density
```

### Conditional Probability Tables (CPTs)

**Accident | Weather:**
| Weather | Multiplier |
|---------|------------|
| Clear | 1.0 |
| Rain | 2.5 |
| Snow | 3.0 |

**Accident | Rush Hour:**
| Rush Hour | Multiplier |
|-----------|------------|
| True | 2.0 |
| False | 1.0 |

### Probability Calculation

```python
P(Accident|Evidence) = base_rate × P(Weather) × P(RushHour) × P(Traffic)
```

Example: 
```
P(Accident | Rain, Rush Hour, High Traffic) = 0.02 × 2.5 × 2.0 × 1.8 = 0.18
```

## 6. XAI Engine

**File:** `ai/explainability.py`

### Purpose
Generate human-readable explanations for all AI decisions.

### Explanation Types

1. **Search Decisions**
   ```
   "Pathfinding using A* algorithm found optimal route from (5,5) to (15,10) 
   in 15 steps. Algorithm explored 45 nodes."
   ```

2. **CSP Decisions**
   ```
   "CSP Solver allocated 850/1000 power units (85% utilization) across 17 
   buildings. All constraints satisfied."
   ```

3. **Logic Decisions**
   ```
   "Logic Rule 'Low Energy Alert' (ID:  R01) triggered. Alert Level: WARNING. 
   Vehicle car_3 has critically low energy (18. 5%)."
   ```

4. **HTN Decisions**
   ```
   "HTN Plan PLAN_5 created for emergency accident_150. Vehicle ambulance_1 
   assigned with 12 hierarchical tasks."
   ```

5. **Bayesian Decisions**
   ```
   "Bayesian Network predicted accident (P=0.18). Factors: Weather=rain, 
   RushHour=True, Traffic=high."
   ```

### Reasoning Trace

Each decision is logged with:
- Tick number
- Engine ID
- Input data
- Output data
- Reasoning steps
- Confidence score (where applicable)