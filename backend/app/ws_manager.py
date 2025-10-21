"""
WebSocket Manager for Real-Time Telemetry Broadcasting
"""
import asyncio
import json
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect
from .utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        async with self.lock:
            self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        async with self.lock:
            self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = set()
        
        async with self.lock:
            connections = self.active_connections.copy()
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.add(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        if disconnected:
            async with self.lock:
                self.active_connections -= disconnected
            logger.info(f"Removed {len(disconnected)} disconnected clients")
    
    async def broadcast_telemetry(self, telemetry_data: dict):
        """Broadcast telemetry data to all connected clients"""
        message = {
            "type": "telemetry",
            "data": telemetry_data
        }
        await self.broadcast(message)
    
    async def broadcast_alert(self, alert_data: dict):
        """Broadcast alert to all connected clients"""
        message = {
            "type": "alert",
            "data": alert_data
        }
        await self.broadcast(message)
    
    async def broadcast_valve_event(self, event_data: dict):
        """Broadcast valve state change event"""
        message = {
            "type": "valve_event",
            "data": event_data
        }
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)


# Global connection manager instance
ws_manager = ConnectionManager()
