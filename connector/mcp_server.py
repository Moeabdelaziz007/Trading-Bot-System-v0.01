"""
QTP MCP Server - Quantum Trading Protocol
An MCP Server that exposes trading functions as tools for AI agents (V0, Claude, etc.)
"""

import asyncio
import os
from mcp.server.fastmcp import FastMCP
import json

# Try to import real MT5, fallback to Mock
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
    mt5.initialize()
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 not found. Running in SIMULATION MODE.")
    
    class MockMT5:
        def initialize(self): return True
        def shutdown(self): pass
        def terminal_info(self): 
            return type('Info', (object,), {'trade_allowed': True})()
        def account_info(self): 
            return type('Account', (object,), {
                'login': 123456, 
                'balance': 10000.0, 
                'equity': 10050.0,
                'profit': 50.0,
                'margin': 100.0,
                'margin_free': 9900.0
            })()
        def positions_get(self):
            return [
                type('Position', (object,), {
                    'ticket': 12345,
                    'symbol': 'XAUUSD',
                    'type': 0,  # BUY
                    'volume': 0.01,
                    'profit': 25.50,
                    'price_open': 2650.00
                })()
            ]
    
    mt5 = MockMT5()

# Initialize the MCP Server
mcp = FastMCP("AlphaQuanTopology (AQT)")

# ============= TOOLS =============

@mcp.tool()
async def get_account_info() -> dict:
    """
    Get the current trading account information.
    Returns balance, equity, profit, margin, and free margin.
    """
    # Run blocking MT5 call in a separate thread
    account = await asyncio.to_thread(mt5.account_info)

    if account is None:
        return {"error": "MT5 not connected"}
    
    return {
        "login": account.login,
        "balance": account.balance,
        "equity": account.equity,
        "profit": account.profit,
        "margin": account.margin,
        "margin_free": account.margin_free,
        "simulation_mode": not MT5_AVAILABLE
    }

@mcp.tool()
async def get_open_positions() -> list:
    """
    Get all currently open trading positions.
    Returns a list of positions with symbol, type, volume, and profit.
    """
    positions = await asyncio.to_thread(mt5.positions_get)

    if positions is None:
        return []
    
    return [
        {
            "ticket": pos.ticket,
            "symbol": pos.symbol,
            "type": "BUY" if pos.type == 0 else "SELL",
            "volume": pos.volume,
            "profit": pos.profit,
            "price_open": pos.price_open
        }
        for pos in positions
    ]

@mcp.tool()
async def execute_trade(symbol: str, action: str, volume: float = 0.01) -> dict:
    """
    Execute a trade on MetaTrader 5.
    
    Args:
        symbol: The trading symbol (e.g., 'XAUUSD', 'EURUSD')
        action: 'BUY' or 'SELL'
        volume: Lot size (default 0.01)
    
    Returns:
        Trade execution result with ticket number or error.
    """
    # Input Validation
    action_upper = action.upper()
    if action_upper not in ['BUY', 'SELL']:
        return {"error": f"Invalid action: {action}. Must be BUY or SELL."}

    if volume <= 0:
        return {"error": "Volume must be greater than 0."}

    if not MT5_AVAILABLE:
        return {
            "status": "SIMULATED",
            "ticket": 99999,
            "symbol": symbol,
            "action": action_upper,
            "volume": volume,
            "message": "Trade simulated (MT5 not available)"
        }
    
    # In production, implement real MT5 order_send here
    # request = {
    #     "action": mt5.TRADE_ACTION_DEAL,
    #     "symbol": symbol,
    #     "volume": volume,
    #     "type": mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL,
    #     ...
    # }
    # result = await asyncio.to_thread(mt5.order_send, request)
    
    return {
        "status": "PENDING_IMPLEMENTATION",
        "symbol": symbol,
        "action": action_upper,
        "volume": volume,
        "message": "Real trading not yet implemented"
    }

@mcp.tool()
async def get_system_status() -> dict:
    """
    Get the current status of the QTP system.
    Returns MT5 connection status and system health.
    """
    terminal = await asyncio.to_thread(mt5.terminal_info)
    return {
        "mt5_connected": terminal is not None,
        "algo_trading_enabled": terminal.trade_allowed if terminal else False,
        "simulation_mode": not MT5_AVAILABLE,
        "version": "1.1.0",
        "protocol": "AQT (AlphaQuanTopology)"
    }

# ============= RESOURCES =============

@mcp.resource("qtp://account/summary")
async def account_summary() -> str:
    """Summary of the trading account."""
    info = await get_account_info()
    return f"""
    📊 Account Summary
    -----------------
    Login: {info.get('login')}
    Balance: ${info.get('balance', 0):,.2f}
    Equity: ${info.get('equity', 0):,.2f}
    Profit: ${info.get('profit', 0):,.2f}
    Mode: {'🔴 Simulation' if info.get('simulation_mode') else '🟢 Live'}
    """

# ============= RUN =============

# ============= RUN =============

# Note: The server is intended to be run via the `fastmcp run` CLI command in production.
# Example: fastmcp run mcp_server.py:mcp --transport sse --host 0.0.0.0 --port 8766

if __name__ == "__main__":
    # This block is only for local dev/testing with standard python execution
    # It might fail if the installed fastmcp version enforces CLI usage
    try:
        mcp.run()
    except TypeError:
        print("⚠️ Please run this server using: fastmcp run mcp_server.py:mcp")
