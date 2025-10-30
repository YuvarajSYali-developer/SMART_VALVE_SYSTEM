"""
Valve Control API endpoints
"""
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..db.models import User, ValveOperation
from ..db.schemas import ValveCommandResponse, UserRole
from ..utils.security import get_current_user, require_role
from ..serial_manager import serial_manager
from ..services.rules_engine import rules_engine
from ..services.alerts import alert_service
from ..ws_manager import ws_manager
from ..utils.logger import logger

router = APIRouter(prefix="/api/valve", tags=["Valve Control"])


async def log_operation(db: Session, command: str, user: User, result: str, message: str = None):
    """Log valve operation to database"""
    operation = ValveOperation(
        ts_utc=int(time.time()),
        command=command,
        issuer_user=user.username,
        result=result,
        message=message
    )
    db.add(operation)
    db.commit()
    
    # Broadcast valve event
    await ws_manager.broadcast_valve_event({
        "command": command,
        "user": user.username,
        "result": result,
        "message": message,
        "timestamp": int(time.time())
    })


@router.post("/open", response_model=ValveCommandResponse)
async def open_valve(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """
    Open the valve (requires operator or admin role)
    Performs safety checks before opening
    """
    if not serial_manager.is_connected():
        await log_operation(db, "OPEN", current_user, "FAILED", "Arduino not connected")
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Get current telemetry for safety check
    # Note: In production, you'd fetch the latest telemetry from DB
    # For now, we'll send the command and let Arduino handle safety
    
    # Send OPEN command
    response = serial_manager.send_command("OPEN")
    logger.info(f"OPEN command response: {repr(response)}")
    
    if not response:
        await log_operation(db, "OPEN", current_user, "FAILED", "No response from Arduino")
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    # Check response
    if "VALVE_OPENED" in response:
        await log_operation(db, "OPEN", current_user, "SUCCESS", "Valve opened successfully")
        logger.info(f"Valve opened by {current_user.username}")
        return ValveCommandResponse(
            success=True,
            message="Valve opened successfully",
            valve_state="OPEN"
        )
    elif "ERROR" in response or "emergency" in response.lower():
        await log_operation(db, "OPEN", current_user, "REJECTED", response)
        return ValveCommandResponse(
            success=False,
            message=response,
            valve_state=None
        )
    else:
        await log_operation(db, "OPEN", current_user, "UNKNOWN", response)
        return ValveCommandResponse(
            success=False,
            message=f"Unexpected response: {response}",
            valve_state=None
        )


@router.post("/close", response_model=ValveCommandResponse)
async def close_valve(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Close the valve (any authenticated user can close)
    """
    if not serial_manager.is_connected():
        await log_operation(db, "CLOSE", current_user, "FAILED", "Arduino not connected")
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Send CLOSE command
    response = serial_manager.send_command("CLOSE")
    logger.info(f"CLOSE command response: {repr(response)}")
    
    if not response:
        await log_operation(db, "CLOSE", current_user, "FAILED", "No response from Arduino")
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    # Check response
    if "VALVE_CLOSED" in response or "ALREADY_CLOSED" in response:
        await log_operation(db, "CLOSE", current_user, "SUCCESS", "Valve closed successfully")
        logger.info(f"Valve closed by {current_user.username}")
        return ValveCommandResponse(
            success=True,
            message="Valve closed successfully",
            valve_state="CLOSED"
        )
    else:
        await log_operation(db, "CLOSE", current_user, "UNKNOWN", response)
        return ValveCommandResponse(
            success=False,
            message=f"Unexpected response: {response}",
            valve_state=None
        )


@router.post("/force_open", response_model=ValveCommandResponse)
async def force_open_valve(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Force open the valve, bypassing emergency mode (admin only)
    Use with extreme caution!
    """
    if not serial_manager.is_connected():
        await log_operation(db, "FORCE_OPEN", current_user, "FAILED", "Arduino not connected")
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Send FORCE_OPEN command
    response = serial_manager.send_command("FORCE_OPEN")
    
    if not response:
        await log_operation(db, "FORCE_OPEN", current_user, "FAILED", "No response from Arduino")
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    # Log critical action
    logger.warning(f"⚠️ FORCE_OPEN command issued by admin: {current_user.username}")
    
    if "VALVE_OPENED" in response:
        await log_operation(db, "FORCE_OPEN", current_user, "SUCCESS", "Valve force-opened")
        
        # Create alert for force open
        alert_service.create_alert(
            db=db,
            alert_type="FORCE_OPEN",
            message=f"Valve force-opened by admin {current_user.username}",
            priority="HIGH"
        )
        
        return ValveCommandResponse(
            success=True,
            message="Valve force-opened (bypassed safety)",
            valve_state="OPEN"
        )
    else:
        await log_operation(db, "FORCE_OPEN", current_user, "FAILED", response)
        return ValveCommandResponse(
            success=False,
            message=response,
            valve_state=None
        )


@router.post("/reset_emergency", response_model=ValveCommandResponse)
async def reset_emergency(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Reset emergency mode (admin only)
    """
    if not serial_manager.is_connected():
        await log_operation(db, "RESET_EMERGENCY", current_user, "FAILED", "Arduino not connected")
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Send RESET_EMERGENCY command
    response = serial_manager.send_command("RESET_EMERGENCY")
    
    if not response:
        await log_operation(db, "RESET_EMERGENCY", current_user, "FAILED", "No response from Arduino")
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    logger.info(f"Emergency mode reset by admin: {current_user.username}")
    
    if "reset successfully" in response.lower() or "EVENT" in response:
        await log_operation(db, "RESET_EMERGENCY", current_user, "SUCCESS", "Emergency mode reset")
        return ValveCommandResponse(
            success=True,
            message="Emergency mode reset successfully",
            valve_state=None
        )
    else:
        await log_operation(db, "RESET_EMERGENCY", current_user, "UNKNOWN", response)
        return ValveCommandResponse(
            success=False,
            message=response,
            valve_state=None
        )


@router.post("/test_mode/enable", response_model=ValveCommandResponse)
async def enable_test_mode(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Enable test mode with mock sensor values (admin only)
    Requires updated Arduino firmware with TEST_MODE_ON support
    """
    if not serial_manager.is_connected():
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Send TEST_MODE_ON command
    response = serial_manager.send_command("TEST_MODE_ON")
    
    if not response:
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    logger.info(f"Test mode enabled by admin: {current_user.username}")
    await log_operation(db, "TEST_MODE_ON", current_user, "SUCCESS", "Test mode enabled")
    
    return ValveCommandResponse(
        success=True,
        message="Test mode enabled - using mock sensor values",
        valve_state=None
    )


@router.post("/test_mode/disable", response_model=ValveCommandResponse)
async def disable_test_mode(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """
    Disable test mode and return to real sensor values (admin only)
    """
    if not serial_manager.is_connected():
        raise HTTPException(status_code=503, detail="Arduino not connected")
    
    # Send TEST_MODE_OFF command
    response = serial_manager.send_command("TEST_MODE_OFF")
    
    if not response:
        raise HTTPException(status_code=503, detail="No response from Arduino")
    
    logger.info(f"Test mode disabled by admin: {current_user.username}")
    await log_operation(db, "TEST_MODE_OFF", current_user, "SUCCESS", "Test mode disabled")
    
    return ValveCommandResponse(
        success=True,
        message="Test mode disabled - using real sensor values",
        valve_state=None
    )
