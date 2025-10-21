"""
Alert Management Service
"""
import time
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from ..db.models import SystemAlert
from ..db.schemas import AlertPriority
from ..utils.logger import logger


class AlertService:
    """Manages system alerts"""
    
    @staticmethod
    def create_alert(
        db: Session,
        alert_type: str,
        message: str,
        priority: AlertPriority = AlertPriority.MEDIUM,
        alert_metadata: Optional[Dict[str, Any]] = None
    ) -> SystemAlert:
        """Create a new alert"""
        alert = SystemAlert(
            ts_utc=int(time.time()),
            alert_type=alert_type,
            message=message,
            priority=priority.value,
            acknowledged=False,
            alert_metadata=alert_metadata
        )
        
        db.add(alert)
        db.commit()
        db.refresh(alert)
        
        logger.warning(f"Alert created: [{priority.value}] {alert_type} - {message}")
        return alert
    
    @staticmethod
    def acknowledge_alert(db: Session, alert_id: int) -> bool:
        """Acknowledge an alert"""
        alert = db.query(SystemAlert).filter(SystemAlert.id == alert_id).first()
        
        if not alert:
            logger.error(f"Alert {alert_id} not found")
            return False
        
        alert.acknowledged = True
        db.commit()
        
        logger.info(f"Alert {alert_id} acknowledged")
        return True
    
    @staticmethod
    def get_unacknowledged_alerts(db: Session, limit: int = 50):
        """Get all unacknowledged alerts"""
        return (
            db.query(SystemAlert)
            .filter(SystemAlert.acknowledged == False)
            .order_by(SystemAlert.ts_utc.desc())
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def get_recent_alerts(db: Session, hours: int = 24, limit: int = 100):
        """Get recent alerts within specified hours"""
        cutoff_time = int(time.time()) - (hours * 3600)
        
        return (
            db.query(SystemAlert)
            .filter(SystemAlert.ts_utc >= cutoff_time)
            .order_by(SystemAlert.ts_utc.desc())
            .limit(limit)
            .all()
        )
    
    @staticmethod
    def create_emergency_alert(
        db: Session,
        violation_type: str,
        violation_details: str,
        telemetry_data: Optional[Dict[str, Any]] = None
    ) -> SystemAlert:
        """Create a critical emergency alert"""
        message = f"EMERGENCY: {violation_type} - {violation_details}"
        
        metadata = {
            "violation_type": violation_type,
            "details": violation_details
        }
        
        if telemetry_data:
            metadata["telemetry"] = telemetry_data
        
        return AlertService.create_alert(
            db=db,
            alert_type="EMERGENCY",
            message=message,
            priority=AlertPriority.CRITICAL,
            alert_metadata=metadata
        )


# Global alert service instance
alert_service = AlertService()
