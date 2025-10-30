"""
Main FastAPI Application
Smart Water Valve IoT System Backend
"""
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .db.session import init_db, SessionLocal
from .db.models import Telemetry
from .serial_manager import serial_manager
from .ws_manager import ws_manager
from .services.rules_engine import rules_engine
from .services.alerts import alert_service
from .api import auth_router, valve_router, telemetry_router
from .utils.logger import logger
from .utils.security import decode_token

# Load environment variables
load_dotenv()

# Global variable to store the telemetry task
telemetry_task = None


async def handle_telemetry(telemetry_data: dict, raw_line: str):
    """
    Callback function to handle incoming telemetry from Arduino
    Stores to database and broadcasts via WebSocket
    """
    try:
        # Store in database
        db = SessionLocal()
        try:
            telemetry_record = Telemetry(
                ts_utc=telemetry_data.get("t", int(time.time())),
                valve_state=telemetry_data.get("valve", "CLOSED"),
                p1=telemetry_data.get("p1", 0.0),
                p2=telemetry_data.get("p2", 0.0),
                c_src=telemetry_data.get("c_src", 0.0),
                c_dst=telemetry_data.get("c_dst", 0.0),
                em=telemetry_data.get("em", 0),
                raw_line=raw_line
            )
            
            db.add(telemetry_record)
            db.commit()
            
            # Check for safety violations
            is_safe, violations = rules_engine.validate_telemetry(telemetry_data)
            
            if not is_safe:
                # Create emergency alert
                for violation in violations:
                    alert_service.create_emergency_alert(
                        db=db,
                        violation_type="SAFETY_VIOLATION",
                        violation_details=violation,
                        telemetry_data=telemetry_data
                    )
                
                # Broadcast alert to WebSocket clients
                await ws_manager.broadcast_alert({
                    "type": "SAFETY_VIOLATION",
                    "violations": violations,
                    "telemetry": telemetry_data,
                    "timestamp": int(time.time())
                })
            
        finally:
            db.close()
        
        # Broadcast telemetry to WebSocket clients
        await ws_manager.broadcast_telemetry(telemetry_data)
        
    except Exception as e:
        logger.error(f"Error handling telemetry: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info(">> Starting Smart Water Valve Backend...")
    
    # Initialize database
    init_db()
    logger.info("[OK] Database initialized")
    
    # Set telemetry callback
    serial_manager.set_telemetry_callback(handle_telemetry)
    
    # Connect to Arduino
    if serial_manager.connect():
        logger.info("[OK] Connected to Arduino")
    else:
        logger.warning("[WARN] Arduino not connected (will retry in background)")
    
    # Start serial read loop
    global telemetry_task
    telemetry_task = asyncio.create_task(serial_manager.read_loop())
    logger.info("[OK] Serial read loop started")
    
    logger.info("[READY] Backend ready!")
    
    yield
    
    # Shutdown
    logger.info("[SHUTDOWN] Shutting down...")
    
    # Stop serial manager
    serial_manager.stop()
    
    # Wait for telemetry task to complete
    if telemetry_task:
        try:
            await asyncio.wait_for(telemetry_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("Telemetry task didn't stop gracefully")
    
    logger.info("[OK] Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Smart Water Valve IoT System",
    description="Backend API for monitoring and controlling water valve with safety automation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(valve_router)
app.include_router(telemetry_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Smart Water Valve IoT System",
        "version": "1.0.0",
        "status": "running",
        "arduino_connected": serial_manager.is_connected(),
        "websocket_clients": ws_manager.get_connection_count()
    }


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """
    WebSocket endpoint for real-time telemetry streaming
    Clients should send JWT token in the first message for authentication
    """
    await ws_manager.connect(websocket)
    
    authenticated = False
    
    try:
        # Wait for authentication message
        auth_message = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        
        token = auth_message.get("token")
        if token:
            try:
                # Verify token
                payload = decode_token(token)
                authenticated = True
                logger.info(f"WebSocket client authenticated: {payload.get('sub')}")
                
                # Send confirmation
                await ws_manager.send_personal_message(
                    {"type": "auth_success", "message": "Authenticated successfully"},
                    websocket
                )
            except Exception as e:
                await ws_manager.send_personal_message(
                    {"type": "auth_error", "message": "Invalid token"},
                    websocket
                )
                await ws_manager.disconnect(websocket)
                return
        
        if not authenticated:
            await ws_manager.send_personal_message(
                {"type": "auth_error", "message": "Authentication required"},
                websocket
            )
            await ws_manager.disconnect(websocket)
            return
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for any message (heartbeat, etc.)
                message = await asyncio.wait_for(websocket.receive_json(), timeout=60.0)
                
                # Handle ping/pong for keepalive
                if message.get("type") == "ping":
                    await ws_manager.send_personal_message(
                        {"type": "pong", "timestamp": int(time.time())},
                        websocket
                    )
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await ws_manager.send_personal_message(
                    {"type": "heartbeat", "timestamp": int(time.time())},
                    websocket
                )
                
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
