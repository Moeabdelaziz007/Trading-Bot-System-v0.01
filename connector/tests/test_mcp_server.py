import pytest
import sys
import os
from unittest.mock import MagicMock
import inspect
import asyncio

# Ensure the connector directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock MetaTrader5 before importing mcp_server
sys.modules['MetaTrader5'] = MagicMock()

# Import the module
import mcp_server

# ============= TEST SETUP =============

@pytest.fixture
def mcp_tools():
    """Fixture to access the tools directly."""
    return {
        "get_account_info": mcp_server.get_account_info,
        "get_open_positions": mcp_server.get_open_positions,
        "execute_trade": mcp_server.execute_trade,
        "get_system_status": mcp_server.get_system_status
    }

# ============= UNIT TESTS =============

@pytest.mark.asyncio
async def test_get_account_info_simulation(mcp_tools):
    """Test get_account_info."""
    result = await mcp_tools["get_account_info"]()
    assert "login" in result
    assert "balance" in result
    assert "equity" in result

@pytest.mark.asyncio
async def test_get_open_positions(mcp_tools):
    """Test get_open_positions returns a list."""
    positions = await mcp_tools["get_open_positions"]()
    assert isinstance(positions, list)

@pytest.mark.asyncio
async def test_execute_trade_simulation(mcp_tools):
    """Test execute_trade returns result."""
    result = await mcp_tools["execute_trade"](symbol="EURUSD", action="BUY", volume=0.1)

    if mcp_server.MT5_AVAILABLE:
        assert result["status"] == "PENDING_IMPLEMENTATION"
        assert result["symbol"] == "EURUSD"
    else:
        assert result["status"] == "SIMULATED"
        assert result["symbol"] == "EURUSD"

@pytest.mark.asyncio
async def test_get_system_status(mcp_tools):
    """Test system status."""
    status = await mcp_tools["get_system_status"]()
    assert "mt5_connected" in status
    assert "version" in status

# ============= EDGE CASES =============

@pytest.mark.asyncio
async def test_execute_trade_invalid_inputs(mcp_tools):
    """Test execute_trade with invalid inputs."""
    # Invalid Action
    result = await mcp_tools["execute_trade"](symbol="EURUSD", action="INVALID_ACTION", volume=0.1)
    assert "error" in result
    assert "Invalid action" in result["error"]

    # Negative Volume
    result = await mcp_tools["execute_trade"](symbol="EURUSD", action="BUY", volume=-1.0)
    assert "error" in result
    assert "Volume" in result["error"]

@pytest.mark.asyncio
async def test_execute_trade_injection_attempt(mcp_tools):
    """Test execute_trade with injection strings."""
    injection_payload = "EURUSD; DROP TABLE users;"
    result = await mcp_tools["execute_trade"](symbol=injection_payload, action="BUY")

    # Validation passes, so it should proceed to simulation/pending
    if result.get("status") == "SIMULATED":
        assert result["symbol"] == injection_payload

# ============= ASYNC/BLOCKING CHECK =============

def test_tools_are_asynchronous(mcp_tools):
    """Verify that tools are now asynchronous."""
    assert inspect.iscoroutinefunction(mcp_tools["execute_trade"])
    assert inspect.iscoroutinefunction(mcp_tools["get_account_info"])
