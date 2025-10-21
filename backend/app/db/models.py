"""
Database models for Smart Water Valve IoT System
"""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, JSON, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Telemetry(Base):
    """Real-time telemetry data from Arduino"""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_utc = Column(Integer, nullable=False, index=True)  # Unix timestamp
    valve_state = Column(String(10), nullable=False, index=True)  # OPEN or CLOSED
    p1 = Column(Float, nullable=False)  # Pressure sensor 1 (bar)
    p2 = Column(Float, nullable=False)  # Pressure sensor 2 (bar)
    c_src = Column(Float, nullable=False)  # Source concentration
    c_dst = Column(Float, nullable=False)  # Destination concentration
    em = Column(Integer, nullable=False, default=0)  # Emergency mode (0 or 1)
    raw_line = Column(Text, nullable=True)  # Original telemetry line
    
    __table_args__ = (
        Index('idx_telemetry_ts_valve', 'ts_utc', 'valve_state'),
    )


class ValveOperation(Base):
    """Log of all valve operations"""
    __tablename__ = "valve_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_utc = Column(Integer, nullable=False, index=True)
    command = Column(String(20), nullable=False)  # OPEN, CLOSE, FORCE_OPEN, etc.
    issuer_user = Column(String(50), nullable=True)  # Username who issued command
    result = Column(String(20), nullable=False)  # SUCCESS, FAILED, REJECTED
    message = Column(Text, nullable=True)  # Additional info or error message
    
    __table_args__ = (
        Index('idx_valve_ops_user', 'issuer_user'),
    )


class SystemAlert(Base):
    """System alerts and notifications"""
    __tablename__ = "system_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    ts_utc = Column(Integer, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # OVER_PRESSURE, CRITICAL_CONCENTRATION, etc.
    message = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    acknowledged = Column(Boolean, nullable=False, default=False)
    alert_metadata = Column(JSON, nullable=True)  # Additional data as JSON
    
    __table_args__ = (
        Index('idx_alerts_ack', 'acknowledged'),
    )


class User(Base):
    """User accounts for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, operator, viewer
    created_at = Column(Integer, nullable=False)  # Unix timestamp
    is_active = Column(Boolean, nullable=False, default=True)


class Rule(Base):
    """Safety rules and thresholds configuration"""
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    json_config = Column(JSON, nullable=False)  # Rule configuration as JSON
    last_updated = Column(Integer, nullable=False)  # Unix timestamp
    enabled = Column(Boolean, nullable=False, default=True)


class Setting(Base):
    """System settings key-value store"""
    __tablename__ = "settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
