"""
Tests for Rules Engine
"""
import pytest
from app.services.rules_engine import RulesEngine


@pytest.fixture
def rules_engine():
    """Create rules engine instance"""
    return RulesEngine()


def test_validate_telemetry_safe(rules_engine):
    """Test telemetry validation with safe values"""
    telemetry = {
        "p1": 3.5,
        "p2": 3.2,
        "c_src": 150.0,
        "c_dst": 250.0,
        "em": 0
    }
    
    is_safe, violations = rules_engine.validate_telemetry(telemetry)
    assert is_safe is True
    assert len(violations) == 0


def test_validate_telemetry_high_pressure(rules_engine):
    """Test telemetry validation with high pressure"""
    telemetry = {
        "p1": 7.5,
        "p2": 3.2,
        "c_src": 150.0,
        "c_dst": 250.0,
        "em": 0
    }
    
    is_safe, violations = rules_engine.validate_telemetry(telemetry)
    assert is_safe is False
    assert len(violations) > 0
    assert any("Pressure sensor 1" in v for v in violations)


def test_validate_telemetry_critical_concentration(rules_engine):
    """Test telemetry validation with critical concentration"""
    telemetry = {
        "p1": 3.5,
        "p2": 3.2,
        "c_src": 600.0,  # Above critical threshold
        "c_dst": 250.0,
        "em": 0
    }
    
    is_safe, violations = rules_engine.validate_telemetry(telemetry)
    assert is_safe is False
    assert len(violations) > 0
    assert any("concentration" in v.lower() for v in violations)


def test_can_open_valve_safe(rules_engine):
    """Test can open valve with safe conditions"""
    telemetry = {
        "p1": 3.5,
        "p2": 3.2,
        "c_src": 150.0,
        "c_dst": 250.0,
        "em": 0
    }
    
    can_open, reason = rules_engine.can_open_valve(telemetry)
    assert can_open is True
    assert "passed" in reason.lower()


def test_can_open_valve_emergency_mode(rules_engine):
    """Test cannot open valve in emergency mode"""
    telemetry = {
        "p1": 3.5,
        "p2": 3.2,
        "c_src": 150.0,
        "c_dst": 250.0,
        "em": 1  # Emergency mode active
    }
    
    can_open, reason = rules_engine.can_open_valve(telemetry)
    assert can_open is False
    assert "emergency" in reason.lower()


def test_can_open_valve_low_source_concentration(rules_engine):
    """Test cannot open valve with low source concentration"""
    telemetry = {
        "p1": 3.5,
        "p2": 3.2,
        "c_src": 5.0,  # Below minimum
        "c_dst": 250.0,
        "em": 0
    }
    
    can_open, reason = rules_engine.can_open_valve(telemetry)
    assert can_open is False
    assert "source concentration too low" in reason.lower()


def test_get_alert_priority(rules_engine):
    """Test alert priority assignment"""
    assert rules_engine.get_alert_priority("pressure_high") == "CRITICAL"
    assert rules_engine.get_alert_priority("emergency_triggered") == "CRITICAL"
    assert rules_engine.get_alert_priority("valve_timeout") == "HIGH"
