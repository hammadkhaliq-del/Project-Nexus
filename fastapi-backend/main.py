"""
NEXUS Backend - FastAPI Entry Point
Production-grade smart city simulation system with 6 AI engines
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Set

from api import auth, simulation, state, websocket
from services.simulation_service import SimulationService
from utils.config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Global simulation service instance
sim_service: SimulationService = None
active_websockets: Set[WebSocket] = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    global sim_service
    
    logger.info("🚀 NEXUS Backend Starting...")
    
    # Initialize simulation service
    sim_service = SimulationService()
    app.state.sim_service = sim_service
    app.state.active_websockets = active_websockets
    
    # Start simulation in background
    asyncio.create_task(simulation_loop())
    
    logger.info("✅ NEXUS Backend Ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 NEXUS Backend Shutting Down...")
    if sim_service:
        sim_service.stop()


app = FastAPI(
    title="NEXUS AI System",
    description="AI-Powered Smart City Simulation with 6 AI Engines",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(state.router, prefix="/api/state", tags=["State"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "system": "NEXUS AI Smart City Simulation",
        "version": "1.0.0",
        "engines": [
            "Search (A*)",
            "CSP (Resource Allocation)",
            "Logic (Rule-Based)",
            "HTN (Planning)",
            "Bayesian (Prediction)",
            "XAI (Explainability)"
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time simulation updates"""
    await websocket.accept()
    active_websockets.add(websocket)
    
    logger.info(f"WebSocket connected. Total connections: {len(active_websockets)}")
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            logger.debug(f"Received from client: {data}")
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(active_websockets)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)


async def simulation_loop():
    """Main simulation tick loop - broadcasts events to all connected clients"""
    global sim_service, active_websockets
    
    logger.info("🔄 Simulation loop started")
    
    while True:
        try:
            if sim_service and sim_service.is_running:
                # Execute one simulation tick
                events = sim_service.tick()
                
                # Broadcast events to all connected WebSocket clients
                if events and active_websockets:
                    for event in events:
                        disconnected = set()
                        for ws in active_websockets:
                            try:
                                await ws.send_json(event.dict())
                            except Exception as e:
                                logger.error(f"Failed to send to WebSocket: {e}")
                                disconnected.add(ws)
                        
                        # Remove disconnected clients
                        active_websockets.difference_update(disconnected)
            
            # Control simulation speed (10-15 FPS)
            await asyncio.sleep(1.0 / settings.SIMULATION_FPS)
            
        except Exception as e:
            logger.error(f"Simulation loop error: {e}", exc_info=True)
            await asyncio.sleep(1.0)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )