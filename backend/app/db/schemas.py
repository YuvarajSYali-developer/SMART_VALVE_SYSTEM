"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from enum import Enum


class ValveState(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class AlertPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# --- Telemetry Schemas ---
class TelemetryBase(BaseModel):
    ts_utc: int
    valve_state: ValveState
    p1: float
    p2: float
    c_src: float
    c_dst: float
    em: int


class TelemetryCreate(TelemetryBase):
    raw_line: Optional[str] = None


class TelemetryResponse(TelemetryBase):
    id: int
    
    class Config:
        from_attributes = True


# --- User Schemas ---
class UserBase(BaseModel):
    username: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: int
    is_active: bool
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Valve Operation Schemas ---
class ValveOperationCreate(BaseModel):
    command: str
    issuer_user: Optional[str] = None
    result: str
    message: Optional[str] = None


class ValveOperationResponse(BaseModel):
    id: int
    ts_utc: int
    command: str
    issuer_user: Optional[str]
    result: str
    message: Optional[str]
    
    class Config:
        from_attributes = True


class ValveCommandResponse(BaseModel):
    success: bool
    message: str
    valve_state: Optional[ValveState] = None


# --- Alert Schemas ---
class AlertCreate(BaseModel):
    alert_type: str
    message: str
    priority: AlertPriority = AlertPriority.MEDIUM
    alert_metadata: Optional[Dict[str, Any]] = None


class AlertResponse(BaseModel):
    id: int
    ts_utc: int
    alert_type: str
    message: str
    priority: AlertPriority
    acknowledged: bool
    alert_metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class AlertAckRequest(BaseModel):
    alert_id: int


# --- Status Schemas ---
class SystemStatus(BaseModel):
    valve_state: ValveState
    emergency_mode: bool
    last_telemetry: Optional[TelemetryResponse]
    active_alerts_count: int


# --- Metrics Schemas ---
class SystemMetrics(BaseModel):
    avg_pressure_p1: float
    avg_pressure_p2: float
    avg_concentration_src: float
    avg_concentration_dst: float
    total_operations: int
    total_runtime_seconds: int
    uptime_seconds: int


# --- Rule Schemas ---
class RuleBase(BaseModel):
    name: str
    json_config: Dict[str, Any]
    enabled: bool = True


class RuleCreate(RuleBase):
    pass


class RuleResponse(RuleBase):
    id: int
    last_updated: int
    
    class Config:
        from_attributes = True
