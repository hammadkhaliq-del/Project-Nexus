"""
Simulation Control API
Endpoints for starting, pausing, restarting simulation and changing parameters
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from api.auth import get_current_user, User
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


# Request Models
class WeatherChange(BaseModel):
    weather: str  # "clear", "rain", "snow"


class SimulationStatus(BaseModel):
    is_running: bool
    tick_count: int
    fps: int
    weather: str
    active_vehicles: int
    active_emergencies: int


# Endpoints
@router.post("/start")
async def start_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Start the simulation"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.start()
    logger.info(f"Simulation started by {current_user.username}")
    
    return {
        "status": "success",
        "message": "Simulation started",
        "is_running": sim_service.is_running
    }


@router.post("/pause")
async def pause_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Pause the simulation"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.pause()
    logger.info(f"Simulation paused by {current_user.username}")
    
    return {
        "status": "success",
        "message": "Simulation paused",
        "is_running": sim_service.is_running
    }


@router.post("/restart")
async def restart_simulation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Restart the simulation with a new city"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    sim_service.restart()
    logger.info(f"Simulation restarted by {current_user.username}")
    
    return {
        "status": "success",
        "message": "Simulation restarted with new city",
        "is_running": sim_service.is_running,
        "tick_count": 0
    }


@router.get("/status", response_model=SimulationStatus)
async def get_simulation_status(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current simulation status"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    status = sim_service.get_status()
    return status


@router.post("/weather")
async def change_weather(
    weather_data: WeatherChange,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Change the weather conditions"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    valid_weather = ["clear", "rain", "snow"]
    if weather_data.weather.lower() not in valid_weather:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid weather. Must be one of: {valid_weather}"
        )
    
    sim_service.set_weather(weather_data.weather.lower())
    logger.info(f"Weather changed to {weather_data.weather} by {current_user.username}")
    
    return {
        "status": "success",
        "message": f"Weather changed to {weather_data.weather}",
        "weather": weather_data.weather.lower()
    }