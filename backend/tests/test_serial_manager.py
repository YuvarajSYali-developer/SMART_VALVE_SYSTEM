"""
Tests for Serial Manager
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.serial_manager import SerialManager


@pytest.fixture
def serial_manager():
    """Create serial manager instance"""
    return SerialManager(port="COM_TEST", baudrate=115200)


def test_parse_telemetry_valid(serial_manager):
    """Test parsing valid telemetry"""
    line = 'TELEMETRY:{"t":1234567890,"valve":"OPEN","p1":3.5,"p2":3.2,"c_src":150.0,"c_dst":250.0,"em":0}'
    
    data = serial_manager.parse_telemetry(line)
    assert data is not None
    assert data["valve"] == "OPEN"
    assert data["p1"] == 3.5
    assert data["p2"] == 3.2
    assert data["c_src"] == 150.0
    assert data["c_dst"] == 250.0
    assert data["em"] == 0


def test_parse_telemetry_invalid_json(serial_manager):
    """Test parsing invalid JSON"""
    line = 'TELEMETRY:{invalid json}'
    
    data = serial_manager.parse_telemetry(line)
    assert data is None


def test_parse_telemetry_not_telemetry(serial_manager):
    """Test parsing non-telemetry line"""
    line = 'STATUS: VALVE_CLOSED'
    
    data = serial_manager.parse_telemetry(line)
    assert data is None


def test_parse_telemetry_adds_timestamp(serial_manager):
    """Test that timestamp is added if not present"""
    line = 'TELEMETRY:{"valve":"OPEN","p1":3.5,"p2":3.2,"c_src":150.0,"c_dst":250.0,"em":0}'
    
    data = serial_manager.parse_telemetry(line)
    assert data is not None
    assert "t" in data
    assert isinstance(data["t"], int)


@patch('serial.Serial')
def test_connect_success(mock_serial, serial_manager):
    """Test successful connection to Arduino"""
    mock_instance = MagicMock()
    mock_instance.is_open = True
    mock_instance.in_waiting = 4
    mock_instance.readline.return_value = b'PONG\n'
    mock_serial.return_value = mock_instance
    
    with patch.object(serial_manager, 'detect_arduino', return_value="COM3"):
        result = serial_manager.connect()
        assert result is True


def test_is_connected_true(serial_manager):
    """Test is_connected returns True when connected"""
    mock_serial = MagicMock()
    mock_serial.is_open = True
    serial_manager.serial_conn = mock_serial
    
    assert serial_manager.is_connected() is True


def test_is_connected_false(serial_manager):
    """Test is_connected returns False when not connected"""
    serial_manager.serial_conn = None
    assert serial_manager.is_connected() is False
