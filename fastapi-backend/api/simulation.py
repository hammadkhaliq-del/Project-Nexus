"""
Simulation Control API Endpoints
Start, pause, restart, and configure simulation
"""
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional

from api.auth import get_current_user, User
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class WeatherRequest(BaseModel):
    """Weather change request"""
    weather: str  # "clear", "rain", "snow"


class SimulationResponse(BaseModel):
    """Standard simulation response"""
    status: str
    tick: int
    message: str


@router.post("/start", response_model=SimulationResponse)
async def start_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Start the simulation"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.start()
    
    logger.info(f"Simulation started by user:  {current_user.username}")
    
    return SimulationResponse(
        status="running",
        tick=sim_service.tick,
        message="Simulation started"
    )


@router.post("/pause", response_model=SimulationResponse)
async def pause_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Pause the simulation"""
    sim_service = request.app.state. sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.pause()
    
    logger.info(f"Simulation paused by user: {current_user.username}")
    
    return SimulationResponse(
        status="paused",
        tick=sim_service.tick,
        message="Simulation paused"
    )


@router.post("/restart", response_model=SimulationResponse)
async def restart_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Restart simulation with fresh state"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.restart()
    
    logger.info(f"Simulation restarted by user: {current_user.username}")
    
    return SimulationResponse(
        status="running",
        tick=0,
        message="Simulation restarted"
    )


@router.post("/weather")
async def set_weather(
    weather_request: WeatherRequest,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Change weather conditions"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    valid_weather = ["clear", "rain", "snow"]
    if weather_request.weather. lower() not in valid_weather: 
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid weather.  Must be one of: {valid_weather}"
        )
    
    sim_service.set_weather(weather_request.weather. lower())
    
    logger.info(f"Weather changed to {weather_request.weather} by user: {current_user. username}")
    
    return {
        "weather": weather_request.weather. lower(),
        "message": f"Weather changed to {weather_request.weather}"
    }


@router.get("/status")
async def get_simulation_status(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current simulation status"""
    sim_service = request. app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return {
        "is_running": sim_service.is_running,
        "is_paused": sim_service. is_paused,
        "tick": sim_service.tick,
        "weather": sim_service.city. weather. value if sim_service.city else "unknown"
    }