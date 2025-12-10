"""
WebSocket API for Real-time Updates
Handles WebSocket connections and message broadcasting
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Set, List, Dict, Any
import asyncio
import json

from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections
    """
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_count += 1
        logger.info(f"WebSocket connected.  Total:  {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending to WebSocket: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection. send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast an event with type"""
        message = {
            "type": event_type,
            "data":  data
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global connection manager
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager: 
    """Dependency to get connection manager"""
    return manager


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time simulation updates
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal({
            "type": "connected",
            "data": {
                "message": "Connected to NEXUS WebSocket",
                "connections": manager.get_connection_count()
            }
        }, websocket)
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            
            try: 
                message = json.loads(data)
                message_type = message.get("type", "unknown")
                
                # Handle different message types
                if message_type == "ping":
                    await manager.send_personal({"type": "pong"}, websocket)
                
                elif message_type == "subscribe":
                    # Handle subscription requests
                    logger.debug(f"Subscription request: {message. get('data')}")
                
                else:
                    logger.debug(f"Received message: {message_type}")
            
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received: {data[: 100]}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    
    except Exception as e: 
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)