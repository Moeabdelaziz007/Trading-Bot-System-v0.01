"""
🔌 Durable Objects Client Helper
Provides easy access to DurableTradeSession from Worker code.

Usage:
    from state.do_client import TradeSessionClient
    
    client = TradeSessionClient(env)
    positions = await client.get_positions()
    await client.record_circuit_failure("oracle")
"""

import json
from js import Headers


class TradeSessionClient:
    """
    High-level client for interacting with DurableTradeSession DO.
    Abstracts away the RPC details for clean Worker code.
    """
    
    def __init__(self, env, session_id: str = "main"):
        """
        Initialize client with environment bindings.
        
        Args:
            env: Cloudflare Worker environment with TRADE_SESSION binding.
            session_id: Unique identifier for this trading session (default: "main").
        """
        self.env = env
        self.session_id = session_id
        self._do_stub = None
    
    def _get_stub(self):
        """Get or create Durable Object stub."""
        if self._do_stub is None:
            # Get DO namespace and create stub for our session ID
            do_id = self.env.TRADE_SESSION.idFromName(self.session_id)
            self._do_stub = self.env.TRADE_SESSION.get(do_id)
        return self._do_stub
    
    async def _request(self, endpoint: str, data: dict = None):
        """Make RPC request to Durable Object."""
        from js import Request, JSON
        
        stub = self._get_stub()
        url = f"https://do-internal/{endpoint}"
        
        if data:
            request = Request.new(url, {
                "method": "POST",
                "headers": Headers.new({"Content-Type": "application/json"}),
                "body": JSON.stringify(data)
            })
        else:
            request = Request.new(url)
        
        response = await stub.fetch(request)
        text = await response.text()
        return json.loads(text)
    
    # ==========================================
    # 🔌 CIRCUIT BREAKER
    # ==========================================
    
    async def get_circuit_state(self, name: str = "default") -> dict:
        """Get current circuit breaker state."""
        return await self._request("circuit-get", {"name": name})
    
    async def record_circuit_success(self, name: str = "default"):
        """Record successful operation for circuit breaker."""
        return await self._request("circuit-update", {
            "name": name,
            "event": "success"
        })
    
    async def record_circuit_failure(self, name: str = "default", threshold: int = 3):
        """Record failed operation for circuit breaker."""
        return await self._request("circuit-update", {
            "name": name,
            "event": "failure",
            "threshold": threshold
        })
    
    async def is_circuit_open(self, name: str = "default") -> bool:
        """Check if circuit is open (blocking requests)."""
        state = await self.get_circuit_state(name)
        return state.get("state") == "OPEN"
    
    # ==========================================
    # 📈 POSITIONS
    # ==========================================
    
    async def get_positions(self) -> list:
        """Get all active (open) positions."""
        result = await self._request("positions-list")
        return result.get("positions", [])
    
    async def open_position(self, position: dict) -> dict:
        """Open a new trading position."""
        return await self._request("positions-open", position)
    
    async def close_position(self, position_id: str) -> dict:
        """Close an existing position."""
        return await self._request("positions-close", {"id": position_id})
    
    async def has_position(self, symbol: str) -> bool:
        """Check if there's an open position for symbol."""
        positions = await self.get_positions()
        return any(p.get("symbol") == symbol for p in positions)
    
    # ==========================================
    # 💰 WALLET
    # ==========================================
    
    async def get_wallet(self, account_id: str = "default") -> dict:
        """Get wallet balance."""
        return await self._request("wallet-get", {"account_id": account_id})
    
    async def update_wallet(self, balance: float, equity: float, 
                           margin_used: float = 0, free_margin: float = 0,
                           account_id: str = "default") -> dict:
        """Update wallet balance."""
        return await self._request("wallet-update", {
            "account_id": account_id,
            "balance": balance,
            "equity": equity,
            "margin_used": margin_used,
            "free_margin": free_margin
        })
    
    # ==========================================
    # 🔒 LOCKS
    # ==========================================
    
    async def acquire_lock(self, symbol: str, reason: str = "trading") -> bool:
        """Acquire symbol lock (prevent duplicate trades)."""
        result = await self._request("locks-acquire", {
            "symbol": symbol,
            "reason": reason
        })
        return result.get("acquired", False)
    
    async def release_lock(self, symbol: str) -> bool:
        """Release symbol lock."""
        result = await self._request("locks-release", {"symbol": symbol})
        return result.get("released", False)
    
    # ==========================================
    # 🏥 HEALTH
    # ==========================================
    
    async def health_check(self) -> dict:
        """Get full DO health status."""
        return await self._request("health")
    
    async def recover_state(self) -> dict:
        """
        Recovery procedure after Worker restart.
        Returns current state for verification.
        """
        health = await self.health_check()
        return {
            "recovered": True,
            "positions_count": health.get("active_positions_count", 0),
            "locked_symbols": health.get("locked_symbols", []),
            "circuit_breakers": health.get("circuit_breakers", [])
        }
