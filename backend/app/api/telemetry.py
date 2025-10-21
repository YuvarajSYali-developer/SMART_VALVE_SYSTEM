"""
Telemetry and System Status API endpoints
"""
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..db.session import get_db
from ..db.models import User, Telemetry, SystemAlert, ValveOperation
from ..db.schemas import (
    TelemetryResponse, SystemStatus, SystemMetrics,
    AlertResponse, ValveOperationResponse
)
from ..utils.security import get_current_user
from ..services.alerts import alert_service
from ..utils.logger import logger

router = APIRouter(prefix="/api", tags=["Telemetry & Status"])


@router.get("/status", response_model=SystemStatus)
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get current system status including latest telemetry and alerts
    """
    # Get latest telemetry
    latest_telemetry = (
        db.query(Telemetry)
        .order_by(desc(Telemetry.ts_utc))
        .first()
    )
    
    # Count unacknowledged alerts
    unack_alerts_count = (
        db.query(SystemAlert)
        .filter(SystemAlert.acknowledged == False)
        .count()
    )
    
    # Determine valve state and emergency mode
    valve_state = "CLOSED"
    emergency_mode = False
    
    if latest_telemetry:
        valve_state = latest_telemetry.valve_state
        emergency_mode = latest_telemetry.em == 1
    
    return SystemStatus(
        valve_state=valve_state,
        emergency_mode=emergency_mode,
        last_telemetry=TelemetryResponse.from_orm(latest_telemetry) if latest_telemetry else None,
        active_alerts_count=unack_alerts_count
    )


@router.get("/telemetry/history", response_model=List[TelemetryResponse])
async def get_telemetry_history(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get historical telemetry data
    """
    telemetry = (
        db.query(Telemetry)
        .order_by(desc(Telemetry.ts_utc))
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return [TelemetryResponse.from_orm(t) for t in telemetry]


@router.get("/telemetry/latest", response_model=Optional[TelemetryResponse])
async def get_latest_telemetry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the most recent telemetry entry
    """
    latest = (
        db.query(Telemetry)
        .order_by(desc(Telemetry.ts_utc))
        .first()
    )
    
    return TelemetryResponse.from_orm(latest) if latest else None


@router.get("/telemetry/range")
async def get_telemetry_range(
    start_ts: int = Query(..., description="Start timestamp (Unix)"),
    end_ts: int = Query(..., description="End timestamp (Unix)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get telemetry data within a time range
    """
    telemetry = (
        db.query(Telemetry)
        .filter(Telemetry.ts_utc >= start_ts)
        .filter(Telemetry.ts_utc <= end_ts)
        .order_by(Telemetry.ts_utc)
        .all()
    )
    
    return [TelemetryResponse.from_orm(t) for t in telemetry]


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system metrics and aggregates
    """
    cutoff_time = int(time.time()) - (hours * 3600)
    
    # Calculate averages
    metrics = (
        db.query(
            func.avg(Telemetry.p1).label("avg_p1"),
            func.avg(Telemetry.p2).label("avg_p2"),
            func.avg(Telemetry.c_src).label("avg_c_src"),
            func.avg(Telemetry.c_dst).label("avg_c_dst")
        )
        .filter(Telemetry.ts_utc >= cutoff_time)
        .first()
    )
    
    # Count operations
    total_ops = (
        db.query(ValveOperation)
        .filter(ValveOperation.ts_utc >= cutoff_time)
        .count()
    )
    
    # Calculate runtime (sum of time when valve was open)
    # Simplified: count records where valve was open
    open_records = (
        db.query(Telemetry)
        .filter(Telemetry.ts_utc >= cutoff_time)
        .filter(Telemetry.valve_state == "OPEN")
        .count()
    )
    # Assume 1 record per second = runtime in seconds
    total_runtime = open_records
    
    # System uptime (time since first telemetry record)
    first_record = db.query(Telemetry).order_by(Telemetry.ts_utc).first()
    uptime = 0
    if first_record:
        uptime = int(time.time()) - first_record.ts_utc
    
    return SystemMetrics(
        avg_pressure_p1=round(metrics.avg_p1 or 0, 2),
        avg_pressure_p2=round(metrics.avg_p2 or 0, 2),
        avg_concentration_src=round(metrics.avg_c_src or 0, 2),
        avg_concentration_dst=round(metrics.avg_c_dst or 0, 2),
        total_operations=total_ops,
        total_runtime_seconds=total_runtime,
        uptime_seconds=uptime
    )


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    acknowledged: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get system alerts, optionally filtered by acknowledgment status
    """
    query = db.query(SystemAlert)
    
    if acknowledged is not None:
        query = query.filter(SystemAlert.acknowledged == acknowledged)
    
    alerts = (
        query
        .order_by(desc(SystemAlert.ts_utc))
        .limit(limit)
        .all()
    )
    
    return [AlertResponse.from_orm(alert) for alert in alerts]


@router.post("/alerts/ack")
async def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Acknowledge an alert
    """
    success = alert_service.acknowledge_alert(db, alert_id)
    
    if not success:
        return {"success": False, "message": f"Alert {alert_id} not found"}
    
    return {"success": True, "message": f"Alert {alert_id} acknowledged"}


@router.get("/operations/history", response_model=List[ValveOperationResponse])
async def get_operations_history(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get valve operations history
    """
    operations = (
        db.query(ValveOperation)
        .order_by(desc(ValveOperation.ts_utc))
        .limit(limit)
        .all()
    )
    
    return [ValveOperationResponse.from_orm(op) for op in operations]


@router.get("/healthz")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    from ..serial_manager import serial_manager
    
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "arduino_connected": serial_manager.is_connected()
    }
