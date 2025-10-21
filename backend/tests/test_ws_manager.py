"""
Tests for WebSocket Manager
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.ws_manager import ConnectionManager


@pytest.fixture
def ws_manager():
    """Create WebSocket manager instance"""
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_websocket(ws_manager):
    """Test connecting a WebSocket"""
    mock_ws = AsyncMock()
    
    await ws_manager.connect(mock_ws)
    
    assert mock_ws in ws_manager.active_connections
    assert ws_manager.get_connection_count() == 1
    mock_ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_websocket(ws_manager):
    """Test disconnecting a WebSocket"""
    mock_ws = AsyncMock()
    
    await ws_manager.connect(mock_ws)
    await ws_manager.disconnect(mock_ws)
    
    assert mock_ws not in ws_manager.active_connections
    assert ws_manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_send_personal_message(ws_manager):
    """Test sending personal message"""
    mock_ws = AsyncMock()
    await ws_manager.connect(mock_ws)
    
    message = {"type": "test", "data": "hello"}
    await ws_manager.send_personal_message(message, mock_ws)
    
    mock_ws.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_telemetry(ws_manager):
    """Test broadcasting telemetry"""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    
    await ws_manager.connect(mock_ws1)
    await ws_manager.connect(mock_ws2)
    
    telemetry_data = {"valve": "OPEN", "p1": 3.5}
    await ws_manager.broadcast_telemetry(telemetry_data)
    
    assert mock_ws1.send_json.called
    assert mock_ws2.send_json.called


@pytest.mark.asyncio
async def test_broadcast_alert(ws_manager):
    """Test broadcasting alert"""
    mock_ws = AsyncMock()
    await ws_manager.connect(mock_ws)
    
    alert_data = {"type": "SAFETY_VIOLATION", "message": "High pressure"}
    await ws_manager.broadcast_alert(alert_data)
    
    mock_ws.send_json.assert_called()
    call_args = mock_ws.send_json.call_args[0][0]
    assert call_args["type"] == "alert"
    assert "data" in call_args


def test_get_connection_count(ws_manager):
    """Test getting connection count"""
    assert ws_manager.get_connection_count() == 0
