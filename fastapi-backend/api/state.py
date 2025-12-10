"""
State Query API
Endpoints for querying current city state, vehicles, events, and AI reasoning logs
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import List, Optional

from api.auth import get_current_user, User
from models.city_state import CityState, VehicleState, BuildingState, EventLog, ReasoningLog
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/city", response_model=CityState)
async def get_city_state(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get complete city state snapshot"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    city_state = sim_service.get_city_state()
    return city_state


@router.get("/vehicles", response_model=List[VehicleState])
async def get_vehicles(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all vehicle states"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    vehicles = sim_service.get_vehicles_state()
    return vehicles


@router.get("/buildings", response_model=List[BuildingState])
async def get_buildings(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all building states"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    buildings = sim_service.get_buildings_state()
    return buildings


@router.get("/events", response_model=List[EventLog])
async def get_events(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    event_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get event logs with optional filtering"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    events = sim_service.get_event_logs(limit=limit, event_type=event_type)
    return events


@router.get("/reasoning", response_model=List[ReasoningLog])
async def get_reasoning_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=500),
    engine: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get AI reasoning logs with optional filtering by engine"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    reasoning = sim_service.get_reasoning_logs(limit=limit, engine=engine)
    return reasoning


@router.get("/metrics")
async def get_metrics(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get simulation performance metrics"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    metrics = sim_service.get_metrics()
    return metrics