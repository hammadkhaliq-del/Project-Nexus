"""
State Query API Endpoints
Retrieve city state, vehicles, buildings, events, and metrics
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import List, Optional

from api.auth import get_current_user, User
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


@router.get("/city")
async def get_city_state(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get complete city state"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return sim_service.get_state()


@router.get("/vehicles")
async def get_vehicles(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all vehicle states"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return [v.get_state_dict() for v in sim_service.vehicles]


@router.get("/buildings")
async def get_buildings(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get all building states"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return [
        {
            "id": b.id,
            "type": b.type. value,
            "position": {"x": b.position[0], "y": b.position[1]},
            "power_requirement": b.power_requirement,
            "allocated_power": b.allocated_power,
            "color": b.color
        }
        for b in sim_service.city.buildings
    ]


@router.get("/emergencies")
async def get_emergencies(
    request: Request,
    include_resolved: bool = Query(False, description="Include resolved emergencies"),
    current_user: User = Depends(get_current_user)
):
    """Get emergency states"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    emergencies = sim_service.city.emergencies
    
    if not include_resolved:
        emergencies = [e for e in emergencies if not e. resolved]
    
    return [
        {
            "id":  e.id,
            "type": e.type,
            "position": {"x":  e.position[0], "y": e.position[1]},
            "severity": e.severity,
            "created_tick": e.created_tick,
            "assigned_vehicle": e.assigned_vehicle_id,
            "resolved":  e.resolved
        }
        for e in emergencies
    ]


@router.get("/events")
async def get_events(
    request: Request,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of events"),
    current_user: User = Depends(get_current_user)
):
    """Get recent simulation events"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    # Get events from event bus
    events = sim_service. event_bus.get_recent_events(limit=limit)
    
    return [event.to_dict() for event in events]


@router.get("/reasoning")
async def get_reasoning(
    request: Request,
    limit: int = Query(50, ge=1, le=200, description="Maximum number of logs"),
    engine:  Optional[str] = Query(None, description="Filter by engine"),
    current_user: User = Depends(get_current_user)
):
    """Get AI reasoning logs"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    # Get reasoning traces from XAI engine
    from ai.explainability import AIEngine
    
    engine_filter = None
    if engine: 
        try:
            engine_filter = AIEngine(engine. lower())
        except ValueError:
            pass
    
    traces = sim_service.xai_engine.get_recent_traces(limit=limit, engine=engine_filter)
    
    return [
        {
            "id": t.id,
            "tick": t.tick,
            "timestamp": t.timestamp. isoformat(),
            "engine": t.engine. value,
            "decision": t.decision_type,
            "reasoning": t.explanation,
            "input_data": t.input_data,
            "output_data": t.output_data,
            "reasoning_steps": t.reasoning_steps,
            "confidence": t.confidence
        }
        for t in traces
    ]


@router.get("/metrics")
async def get_metrics(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get simulation metrics"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return sim_service.get_metrics()


@router.get("/power")
async def get_power_allocation(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get CSP power allocation details"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    summary = sim_service.csp_engine.get_allocation_summary()
    allocation = sim_service.csp_engine.last_allocation
    
    return {
        **summary,
        "allocation": allocation
    }


@router.get("/ai/stats")
async def get_ai_stats(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get AI engine statistics"""
    sim_service = request.app.state.sim_service
    
    if not sim_service:
        raise HTTPException(status_code=500, detail="Simulation service not initialized")
    
    return {
        "search":  sim_service.search_engine.get_stats(),
        "csp":  sim_service.csp_engine.get_allocation_summary(),
        "logic": sim_service.logic_engine.get_rule_statistics(),
        "bayesian": sim_service.bayesian_network.get_network_state(),
        "xai": sim_service.xai_engine.get_statistics()
    }