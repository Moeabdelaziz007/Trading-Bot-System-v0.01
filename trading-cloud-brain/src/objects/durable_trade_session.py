"""
🧠 DurableTradeSession - SQLite-backed Durable Object
The "Active Context" persistence layer for crash recovery.

Stores:
    - Circuit Breaker State (prevents cascading failures)
    - Active Positions (open trades with entry prices)
    - Wallet Balances (real-time equity tracking)

Architecture:
    - Single-threaded: No race conditions
    - SQLite: Complex queries with zero-latency
    - Atomic: Write operations are transactional
    - Recoverable: State survives Worker restarts
    - Observability: Structured JSON logging with trace correlation

Usage:
    From Worker: const session = env.TRADE_SESSION.get(id)
                 await session.fetch(request)
"""

import json
from js import Response, JSON
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union

# 11/10 Standard: Structured Logging
from src.core.logger import Logger, LogLevel

class DurableTradeSession:
    """
    SQLite-backed Durable Object for active trading context.
    
    Features:
    - 🛡️ Circuit Breaker (Open/Closed/Half-Open)
    - 💾 SQLite Persistence
    - 🔍 Structured Logging
    - 🚦 Input Validation
    """
    
    def __init__(self, state, env):
        self.state = state
        self.env = env
        self.sql = state.storage.sql
        
        # Initialize Logger with module context
        self.log = Logger(module="durable_session", level=LogLevel.INFO)
        
        # Initialize SQLite schema on first run
        self._init_schema()
        self.log.info("SESSION_INIT", message="Durable Object initialized", id=str(state.id))
    
    def _init_schema(self):
        """Create SQLite tables if they don't exist."""
        try:
            # Circuit Breaker State
            self.sql.exec("""
                CREATE TABLE IF NOT EXISTS circuit_breakers (
                    name TEXT PRIMARY KEY,
                    state TEXT DEFAULT 'CLOSED',
                    failure_count INTEGER DEFAULT 0,
                    last_failure_at TEXT,
                    last_success_at TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Active Positions (open trades)
            self.sql.exec("""
                CREATE TABLE IF NOT EXISTS active_positions (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    strategy TEXT,
                    opened_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    meta TEXT
                )
            """)
            
            # Wallet Balances
            self.sql.exec("""
                CREATE TABLE IF NOT EXISTS wallet_balances (
                    account_id TEXT PRIMARY KEY,
                    balance REAL DEFAULT 0,
                    equity REAL DEFAULT 0,
                    margin_used REAL DEFAULT 0,
                    free_margin REAL DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Symbol Locks (prevent duplicate trades)
            self.sql.exec("""
                CREATE TABLE IF NOT EXISTS symbol_locks (
                    symbol TEXT PRIMARY KEY,
                    locked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
            """)
        except Exception as e:
            self.log.critical("SCHEMA_INIT_FAILED", error=str(e))
            raise e
    
    async def fetch(self, request):
        """
        RPC Handler - Route requests to internal methods.
        
        Expects `X-Correlation-ID` header for distributed tracing.
        """
        try:
            # 1. Tracing
            correlation_id = request.headers.get("X-Correlation-ID") or self.log.new_correlation_id()
            self.log.set_correlation_id(correlation_id)
            
            url = str(request.url)
            path = url.split("?")[0].split("/")[-1]
            method = request.method
            
            self.log.debug("RPC_REQUEST", path=path, method=method)
            
            # 2. Routing
            # === CIRCUIT BREAKER ===
            if path == "circuit-get":
                return await self._handle_circuit_get(request)
            
            if path == "circuit-update":
                return await self._handle_circuit_update(request)
            
            # === POSITIONS ===
            if path == "positions-list":
                return await self._handle_positions_list()
            
            if path == "positions-open":
                return await self._handle_positions_open(request)
            
            if path == "positions-close":
                return await self._handle_positions_close(request)
            
            # === WALLET ===
            if path == "wallet-get":
                return await self._handle_wallet_get(request)
            
            if path == "wallet-update":
                return await self._handle_wallet_update(request)
            
            # === LOCKS ===
            if path == "locks-acquire":
                return await self._handle_locks_acquire(request)
            
            if path == "locks-release":
                return await self._handle_locks_release(request)
            
            # === METRICS & HEALTH ===
            if path == "metrics-get":
                return await self._handle_metrics_get()
                
            if path == "health":
                return await self._handle_health()
            
            self.log.warn("UNKNOWN_ENDPOINT", path=path)
            return self._error_response("Unknown endpoint", 404)
            
        except Exception as e:
            self.log.error("RPC_ERROR", error=str(e), path=path)
            return self._error_response(str(e), 500)
    
    # ==========================================
    # 🔌 CIRCUIT BREAKER HANDLERS
    # ==========================================
    
    async def _handle_circuit_get(self, request):
        """Get circuit breaker state by name."""
        try:
            data = await self._parse_json(request)
            name = data.get("name", "default")
            
            cursor = self.sql.exec(
                "SELECT * FROM circuit_breakers WHERE name = ?", name
            )
            
            row = cursor.one()
            
            # NEW: Half-Open Logic Check
            # If state is OPEN but timeout passed -> Transition to HALF-OPEN temporarily
            state = "CLOSED"
            if row:
                state = row.state
                if state == "OPEN":
                    last_failure = datetime.fromisoformat(row.last_failure_at) if row.last_failure_at else datetime.min
                    # Default recovery timeout 30s
                    # Ideally this should be stored in DB or config, using hardcoded default for now
                    recovery_timeout = 30 
                    if datetime.utcnow() > last_failure + timedelta(seconds=recovery_timeout):
                        state = "HALF_OPEN"
                        # We don't write to DB yet, just report it as ready to try
            
            if row:
                return self._json_response({
                    "name": row.name,
                    "state": state, # Computed state
                    "failure_count": row.failure_count,
                    "last_failure_at": row.last_failure_at,
                    "last_success_at": row.last_success_at
                })
            
            # Create default if not exists
            self.sql.exec(
                "INSERT OR IGNORE INTO circuit_breakers (name) VALUES (?)", name
            )
            return self._json_response({"name": name, "state": "CLOSED", "failure_count": 0})
            
        except Exception as e:
            self.log.error("CIRCUIT_GET_ERROR", error=str(e))
            return self._error_response("Failed to get circuit state")

    async def _handle_circuit_update(self, request):
        """
        Record success or failure for circuit breaker.
        Handles transitions: CLOSED <-> OPEN <-> HALF_OPEN
        """
        data = await self._parse_json(request)
        if not self._validate_payload(data, ["name", "event"]):
            return self._error_response("Missing required fields: name, event", 400)
            
        name = data.get("name", "default")
        event = data.get("event")  # "success" or "failure"
        threshold = data.get("threshold", 3)
        
        now = datetime.utcnow().isoformat()
        
        try:
            if event == "success":
                # Success resets everything to CLOSED
                self.sql.exec("""
                    UPDATE circuit_breakers 
                    SET failure_count = 0, 
                        state = 'CLOSED',
                        last_success_at = ?,
                        updated_at = ?
                    WHERE name = ?
                """, now, now, name)
                self.log.info("CIRCUIT_RESET", name=name, reason="success_event")
                
            elif event == "failure":
                # Get current state
                cursor = self.sql.exec(
                    "SELECT failure_count, state FROM circuit_breakers WHERE name = ?", name
                )
                row = cursor.one()
                current_count = row.failure_count if row else 0
                current_state = row.state if row else "CLOSED"
                
                new_count = current_count + 1
                
                # State Transition Logic
                new_state = current_state
                if new_state == "CLOSED" and new_count >= threshold:
                    new_state = "OPEN"
                    self.log.warn("CIRCUIT_TRIPPED", name=name, failure_count=new_count)
                elif new_state == "HALF_OPEN":
                    new_state = "OPEN" # Failed probe in half-open -> immediate trip
                    self.log.warn("CIRCUIT_RETRIPPED", name=name, reason="half_open_failure")
                
                self.sql.exec("""
                    INSERT INTO circuit_breakers (name, failure_count, state, last_failure_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        failure_count = ?,
                        state = ?,
                        last_failure_at = ?,
                        updated_at = ?
                """, 
                name, new_count, new_state, now, now, 
                new_count, new_state, now, now)
            
            return self._json_response({"updated": True, "name": name, "event": event})
            
        except Exception as e:
            self.log.error("CIRCUIT_UPDATE_ERROR", error=str(e), name=name)
            return self._error_response("Failed to update circuit")
    
    # ==========================================
    # 📈 POSITIONS HANDLERS
    # ==========================================
    
    async def _handle_positions_list(self):
        """List all active (open) positions."""
        cursor = self.sql.exec("SELECT * FROM active_positions ORDER BY opened_at DESC")
        positions = []
        for row in cursor:
            positions.append({
                "id": row.id,
                "symbol": row.symbol,
                "direction": row.direction,
                "entry_price": row.entry_price,
                "quantity": row.quantity,
                "stop_loss": row.stop_loss,
                "take_profit": row.take_profit,
                "strategy": row.strategy,
                "opened_at": row.opened_at,
                "meta": json.loads(row.meta) if row.meta else {}
            })
        return self._json_response({"positions": positions, "count": len(positions)})
    
    async def _handle_positions_open(self, request):
        """Open a new position (persist to SQLite)."""
        data = await self._parse_json(request)
        required = ["id", "symbol", "direction", "entry_price", "quantity"]
        if not self._validate_payload(data, required):
            return self._error_response(f"Missing fields. Required: {required}", 400)
            
        now = datetime.utcnow().isoformat()
        
        try:
            # Transaction-like execution
            self.sql.exec("""
                INSERT INTO active_positions 
                (id, symbol, direction, entry_price, quantity, stop_loss, take_profit, strategy, opened_at, meta)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                data.get("id"),
                data.get("symbol"),
                data.get("direction"),
                data.get("entry_price"),
                data.get("quantity"),
                data.get("stop_loss"),
                data.get("take_profit"),
                data.get("strategy"),
                now,
                json.dumps(data.get("meta", {}))
            )
            
            self.log.trade_executed(
                symbol=data.get("symbol"),
                side=data.get("direction"),
                qty=data.get("quantity"),
                price=data.get("entry_price"),
                message="Position opened in durable storage"
            )
            
            return self._json_response({"opened": True, "id": data.get("id")})
            
        except Exception as e:
            # SQLite constraint violation (e.g. duplicate ID)
            self.log.error("POSITION_OPEN_FAILED", error=str(e), id=data.get("id"))
            return self._error_response("Failed to open position. ID likely exists.", 409)
    
    async def _handle_positions_close(self, request):
        """Close a position (remove from active, return data for archiving)."""
        data = await self._parse_json(request)
        if not self._validate_payload(data, ["id"]):
            return self._error_response("Missing position ID", 400)
            
        position_id = data.get("id")
        
        try:
            # Get position before deleting to return it
            cursor = self.sql.exec(
                "SELECT * FROM active_positions WHERE id = ?", position_id
            )
            row = cursor.one()
            
            if row:
                # Delete from active
                self.sql.exec("DELETE FROM active_positions WHERE id = ?", position_id)
                
                self.log.info("POSITION_CLOSED", id=position_id, symbol=row.symbol)
                
                # Return data so Worker can archive to D1
                return self._json_response({
                    "closed": True, 
                    "id": position_id,
                    "symbol": row.symbol,
                    "entry_price": row.entry_price,
                    "quantity": row.quantity,
                    "opened_at": row.opened_at
                })
            
            self.log.warn("POSITION_CLOSE_NOT_FOUND", id=position_id)
            return self._error_response("Position not found", 404)
            
        except Exception as e:
            self.log.error("POSITION_CLOSE_ERROR", error=str(e), id=position_id)
            return self._error_response("Failed to close position", 500)
    
    # ==========================================
    # 💰 WALLET HANDLERS
    # ==========================================
    
    async def _handle_wallet_get(self, request):
        """Get wallet balance for account."""
        data = await self._parse_json(request)
        account_id = data.get("account_id", "default")
        
        cursor = self.sql.exec(
            "SELECT * FROM wallet_balances WHERE account_id = ?", account_id
        )
        row = cursor.one()
        
        if row:
            return self._json_response({
                "account_id": row.account_id,
                "balance": row.balance,
                "equity": row.equity,
                "margin_used": row.margin_used,
                "free_margin": row.free_margin
            })
        
        return self._json_response({"account_id": account_id, "balance": 0, "equity": 0})
    
    async def _handle_wallet_update(self, request):
        """Update wallet balance."""
        data = await self._parse_json(request)
        account_id = data.get("account_id", "default")
        now = datetime.utcnow().isoformat()
        
        try:
            self.sql.exec("""
                INSERT INTO wallet_balances (account_id, balance, equity, margin_used, free_margin, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id) DO UPDATE SET
                    balance = ?,
                    equity = ?,
                    margin_used = ?,
                    free_margin = ?,
                    updated_at = ?
            """,
                account_id,
                data.get("balance", 0),
                data.get("equity", 0),
                data.get("margin_used", 0),
                data.get("free_margin", 0),
                now,
                data.get("balance", 0),
                data.get("equity", 0),
                data.get("margin_used", 0),
                data.get("free_margin", 0),
                now
            )
            
            return self._json_response({"updated": True, "account_id": account_id})
        except Exception as e:
            self.log.error("WALLET_UPDATE_ERROR", error=str(e))
            return self._error_response("Failed to update wallet")
    
    # ==========================================
    # 🔒 LOCKS HANDLERS
    # ==========================================
    
    async def _handle_locks_acquire(self, request):
        """Acquire lock for symbol (prevents duplicate trades)."""
        data = await self._parse_json(request)
        if not self._validate_payload(data, ["symbol"]):
            return self._error_response("Missing symbol", 400)
            
        symbol = data.get("symbol")
        reason = data.get("reason", "trading")
        
        cursor = self.sql.exec(
            "SELECT symbol FROM symbol_locks WHERE symbol = ?", symbol
        )
        if cursor.one():
            self.log.debug("LOCK_CONTESTED", symbol=symbol)
            return self._json_response({"acquired": False, "reason": "Already locked"})
        
        # Acquire lock
        now = datetime.utcnow().isoformat()
        self.sql.exec(
            "INSERT INTO symbol_locks (symbol, locked_at, reason) VALUES (?, ?, ?)",
            symbol, now, reason
        )
        self.log.debug("LOCK_ACQUIRED", symbol=symbol)
        
        return self._json_response({"acquired": True, "symbol": symbol})
    
    async def _handle_locks_release(self, request):
        """Release lock for symbol."""
        data = await self._parse_json(request)
        symbol = data.get("symbol")
        
        self.sql.exec("DELETE FROM symbol_locks WHERE symbol = ?", symbol)
        return self._json_response({"released": True, "symbol": symbol})
    
    # ==========================================
    # 🏥 HEALTH & METRICS
    # ==========================================
    
    async def _handle_metrics_get(self):
        """Get operational metrics for dashboard."""
        pos_count = self.sql.exec("SELECT COUNT(*) as c FROM active_positions").one().c
        lock_count = self.sql.exec("SELECT COUNT(*) as c FROM symbol_locks").one().c
        circuit_open = self.sql.exec("SELECT COUNT(*) as c FROM circuit_breakers WHERE state != 'CLOSED'").one().c
        
        return self._json_response({
            "positions": pos_count,
            "locks": lock_count,
            "circuits_tripped": circuit_open,
            "memory_usage": "N/A" # Would need internal bindings to measure
        })

    async def _handle_health(self):
        """Full state dump for recovery verification and debugging."""
        positions_cursor = self.sql.exec("SELECT COUNT(*) as count FROM active_positions")
        positions_count = positions_cursor.one().count
        
        circuits_cursor = self.sql.exec("SELECT * FROM circuit_breakers")
        circuits = [{
            "name": r.name,
            "state": r.state,
            "failure_count": r.failure_count
        } for r in circuits_cursor]
        
        locks_cursor = self.sql.exec("SELECT symbol FROM symbol_locks")
        locks = [r.symbol for r in locks_cursor]
        
        return self._json_response({
            "healthy": True,
            "timestamp": datetime.utcnow().isoformat(),
            "active_positions_count": positions_count,
            "circuit_breakers": circuits,
            "locked_symbols": locks
        })
    
    # ==========================================
    # 🔧 UTILITIES
    # ==========================================
    
    async def _parse_json(self, request) -> Dict[str, Any]:
        """Safe JSON parsing from request."""
        try:
            body = await request.json()
            # Pyodide JS conversion if needed
            if hasattr(body, "to_py"):
                return body.to_py()
            # If it's a JS Proxy object (common in Workers)
            return json.loads(JSON.stringify(body))
        except Exception:
            return {}
            
    def _validate_payload(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate presence of required fields."""
        return all(field in data for field in required_fields)
    
    def _json_response(self, data: Any, status: int = 200) -> Response:
        """Create structured JSON response."""
        return Response.new(
            json.dumps(data),
            status=status,
            headers={"Content-Type": "application/json"}
        )

    def _error_response(self, message: str, status: int = 500) -> Response:
        """Standardized error response."""
        return self._json_response({"error": message, "success": False}, status=status)
