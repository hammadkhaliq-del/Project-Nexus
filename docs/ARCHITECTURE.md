# NEXUS Architecture Documentation

## System Overview

NEXUS is a production-grade, real-time smart city simulation system powered by 6 AI engines working in coordination. 

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  REACT FRONTEND                             │
│  (Login, Signup, Dashboard with 3D Visualization)          │
└─────────────────────────────────────────────────────────────┘
                          ↕ WebSocket + REST
┌─────────────────────────────────────────────────────────────┐
│                 FASTAPI BACKEND                             │
│  (Auth, Simulation Control, State Queries, WebSocket)      │
└─────────────────────────────────────────────────────────────┘
                          ↕ Event Bus
┌─────────────────────────────────────────────────────────────┐
│             CORE SIMULATION ENGINE (Python)                 │
│  - City Environment (20×20 Grid)                           │
│  - Vehicle Agents (8 Cars + 2 Emergency)                   │
│  - Graph-Based Pathfinding                                 │
│  - Tick-Based Loop (10-15 FPS)                             │
└─────────────────────────────────────────────────────────────┘
                          ↕ Coordinated via Orchestrator
┌─────────────────────────────────────────────────────────────┐
│                  6 AI ENGINES                               │
│  🔍 Search   ⚡ CSP   📜 Logic   🗺️ HTN   🎲 Bayesian   🧠 XAI  │
└─────────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Directory Structure

```
fastapi-backend/
├── main.py                 # FastAPI entry point
├── api/                    # REST API routes
│   ├── auth. py            # Authentication endpoints
│   ├── simulation. py      # Simulation control
│   ├── state.py           # State query endpoints
│   └── websocket.py       # WebSocket handler
├── core/                   # Core simulation
│   ├── city. py            # City environment
│   ├── graph.py           # Grid graph for pathfinding
│   ├── agent.py           # Vehicle agents
│   ├── simulation.py      # Main simulation loop
│   └── events.py          # Event bus system
├── ai/                     # AI Engines
│   ├── search.py          # A*, Dijkstra, BFS
│   ├── csp_engine.py      # Constraint satisfaction
│   ├── logic_engine.py    # Rule-based reasoning
│   ├── planner.py         # HTN planner
│   ├── bayesian. py        # Bayesian network
│   └── explainability.py  # XAI engine
├── models/                 # Pydantic models
├── services/               # Business logic
└── utils/                  # Utilities
```

### Core Components

#### 1. City Environment (`core/city.py`)
- 20×20 grid world
- Buildings (Residential, Commercial, Industrial, Hospital, Fire Station)
- Dynamic weather system
- Road blocking/unblocking
- Emergency spawning

#### 2. Vehicle Agents (`core/agent.py`)
- Normal vehicles (8)
- Emergency vehicles (Ambulance, Fire Truck)
- Energy management
- Health degradation
- Path following

#### 3. Grid Graph (`core/graph.py`)
- 4-directional movement
- Dynamic neighbor calculation
- Weather-affected movement costs
- Heuristic functions for A*

#### 4. Simulation Engine (`core/simulation.py`)
- Main tick loop
- AI engine coordination
- Event generation
- State management

### Data Flow

```
User Action → REST API → Simulation Service → Core Engine
                                    ↓
              WebSocket ← Event Bus ← AI Engines
                 ↓
            Frontend Update
```

## Frontend Architecture

### Directory Structure

```
client/src/
├── main.jsx               # Entry point
├── App.jsx                # Main app with routing
├── pages/                 # Page components
│   ├── Login.jsx
│   ├── Signup. jsx
│   └── Dashboard.jsx
├── components/            # Reusable components
│   ├── Header.jsx
│   ├── CityVisualization.jsx
│   ├── MetricsPanel.jsx
│   ├── IntelligencePanel.jsx
│   └── ... 
├── hooks/                 # Custom React hooks
│   ├── useAuth.js
│   ├── useSimulation.js
│   └── useWebSocket.js
├── services/              # API services
│   ├── api.js
│   ├── auth.js
│   ├── simulation.js
│   └── websocket.js
├── store/                 # State management
│   └── authStore.js
└── utils/                 # Utilities
    ├── constants.js
    └── helpers.js
```

## Communication Protocols

### REST API
- Authentication (JWT)
- Simulation control
- State queries

### WebSocket
- Real-time events
- AI reasoning logs
- State updates

## Security

### Authentication Flow
1. User submits credentials
2. Backend validates and generates JWT
3. Token stored in localStorage
4. Token sent with each request
5. Backend validates token on protected routes

### Password Security
- Bcrypt hashing
- Minimum length enforcement
- Secure token generation

## Scalability Considerations

### Current Design
- In-memory data storage
- Single-process simulation
- WebSocket broadcast to all clients

### Future Improvements
- Database persistence (PostgreSQL)
- Redis for caching
- Horizontal scaling with load balancer
- Message queue for events