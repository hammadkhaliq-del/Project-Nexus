# NEXUS API Reference

## Base URL

```
http://localhost:8000
```

## Authentication

### POST /api/auth/signup

Create a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "full_name": "string (optional)"
}
```

**Response:**
```json
{
  "access_token":  "string",
  "token_type": "bearer"
}
```

### POST /api/auth/login

Authenticate user and get JWT token.

**Request Body (form-data):**
```
username:  string
password: string
```

**Response:**
```json
{
  "access_token": "string",
  "token_type":  "bearer"
}
```

### GET /api/auth/me

Get current authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "created_at": "datetime"
}
```

### POST /api/auth/logout

Logout current user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

## Simulation Control

### POST /api/simulation/start

Start the simulation.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status":  "running",
  "tick":  0,
  "message":  "Simulation started"
}
```

### POST /api/simulation/pause

Pause the simulation. 

**Response:**
```json
{
  "status": "paused",
  "tick": 150,
  "message": "Simulation paused"
}
```

### POST /api/simulation/restart

Restart simulation with fresh state.

**Response:**
```json
{
  "status":  "running",
  "tick":  0,
  "message":  "Simulation restarted"
}
```

### POST /api/simulation/weather

Change weather conditions.

**Request Body:**
```json
{
  "weather":  "clear" | "rain" | "snow"
}
```

**Response:**
```json
{
  "weather": "rain",
  "message": "Weather changed to rain"
}
```

### GET /api/simulation/status

Get current simulation status.

**Response:**
```json
{
  "is_running": true,
  "is_paused":  false,
  "tick": 250,
  "weather": "clear"
}
```

---

## State Queries

### GET /api/state/city

Get complete city state.

**Response:**
```json
{
  "tick": 250,
  "weather": "clear",
  "grid_size": 20,
  "vehicles": [... ],
  "buildings": [...],
  "emergencies": [...],
  "blocked_roads": [...]
}
```

### GET /api/state/vehicles

Get all vehicle states.

**Response:**
```json
[
  {
    "id":  "car_0",
    "type": "normal",
    "position": {"x": 5, "y": 10},
    "destination": {"x": 15, "y": 8},
    "path": [... ],
    "speed": 50. 0,
    "health": 95.5,
    "energy": 78.3,
    "is_emergency": false,
    "active_mission": null,
    "status": "moving"
  }
]
```

### GET /api/state/buildings

Get all building states.

**Response:**
```json
[
  {
    "id": "hospital_1",
    "type": "hospital",
    "position": {"x": 5, "y": 10},
    "power_requirement": 150,
    "allocated_power": 150,
    "color": "#d73a4a"
  }
]
```

### GET /api/state/events

Get recent simulation events.

**Query Parameters:**
- `limit` (int, optional): Maximum number of events (default: 50)

**Response:**
```json
[
  {
    "id":  "evt_123",
    "tick": 245,
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "emergency_spawn",
    "title": "Accident Reported",
    "description": "Accident at position (12, 8)",
    "severity": "critical",
    "data": {
      "emergency_id": "accident_245",
      "position": {"x": 12, "y": 8}
    }
  }
]
```

### GET /api/state/reasoning

Get AI reasoning logs.

**Query Parameters:**
- `limit` (int, optional): Maximum number of logs (default: 50)
- `engine` (string, optional): Filter by engine (search, csp, logic, htn, bayesian, xai)

**Response:**
```json
[
  {
    "id": "XAI_42",
    "tick": 240,
    "timestamp": "2024-01-15T10:29:55Z",
    "engine": "bayesian",
    "decision": "event_prediction",
    "reasoning": "Bayesian Network predicted accident (P=0.18).. .",
    "input_data": {
      "weather":  "rain",
      "is_rush_hour": true,
      "traffic_density": "high"
    },
    "output_data": {
      "probability": 0.18,
      "spawned":  true
    },
    "confidence": 0.18
  }
]
```

### GET /api/state/metrics

Get simulation metrics.

**Response:**
```json
{
  "tick": 250,
  "fps": 12,
  "efficiency_score": 87.5,
  "total_vehicles": 10,
  "active_vehicles": 7,
  "total_emergencies": 15,
  "resolved_emergencies": 12,
  "active_emergencies": 3,
  "power_utilization": 78.5,
  "weather":  "clear"
}
```

---

## WebSocket

### WS /ws

Real-time event stream.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Incoming Message Types:**

1. **connected** - Connection established
```json
{
  "type":  "connected",
  "data":  {
    "message": "Connected to NEXUS WebSocket",
    "connections": 3
  }
}
```

2. **event** - Simulation event
```json
{
  "type": "event",
  "tick": 250,
  "event_type": "emergency_spawn",
  "title": "Fire Reported",
  "description": "Fire at (8, 15)",
  "severity": "critical",
  "data": {... }
}
```

3. **reasoning** - AI decision
```json
{
  "type": "reasoning",
  "tick": 250,
  "engine": "search",
  "decision": "pathfinding",
  "reasoning":  "A* found path in 12 steps",
  "data": {...}
}
```

4. **state_update** - State change
```json
{
  "type": "state_update",
  "tick": 250,
  "vehicles": [... ],
  "emergencies": [...]
}
```

**Outgoing Message Types:**

1. **ping** - Keep-alive
```json
{"type": "ping"}
```

**Response:**
```json
{"type": "pong"}
```

---

## Error Responses

All endpoints may return error responses: 

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**400 Bad Request:**
```json
{
  "detail": "Username already registered"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider adding: 
- 100 requests/minute for authenticated users
- 20 requests/minute for unauthenticated users

---

## CORS

Allowed origins (configurable in `.env`):
- http://localhost:5173
- http://localhost:3000