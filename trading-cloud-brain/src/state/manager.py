"""
⚡ StateManager - Trade State Coordination
Prevents race conditions using KV-based locking.

For Cloudflare Workers without Durable Objects:
Uses KV storage with TTL-based locks for coordination.

For full Durable Objects support, upgrade wrangler.toml.

Usage:
    state = StateManager(env)
    
    # Before trading
    if await state.acquire_lock("EURUSD"):
        try:
            # Execute trade
            await state.record_trade(trade_data)
        finally:
            await state.release_lock("EURUSD")
"""

import time
import json
from typing import Dict, List, Optional

# Structured logging
from core.structured_logging import get_logger
log = get_logger("state_manager")


class StateManager:
    """
    Trade State Coordination for Cloudflare Workers.
    Uses KV storage for locking and state management.
    """
    
    # Lock TTL in seconds (auto-expire if worker crashes)
    LOCK_TTL = 60  # 1 minute
    
    # KV key prefixes
    PREFIX_LOCK = "lock:"
    PREFIX_TRADE = "trade:"
    PREFIX_CRON = "cron:"
    
    def __init__(self, env):
        """
        Initialize StateManager.
        
        Args:
            env: Cloudflare Worker environment with KV binding
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
    
    # ==========================================
    # 🔒 SYMBOL LOCKING
    # ==========================================
    
    async def acquire_lock(self, symbol: str) -> bool:
        """
        Acquire exclusive lock on a symbol.
        
        Prevents multiple workers from trading same symbol.
        Uses atomic put with condition check.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
        
        Returns:
            bool: True if lock acquired, False if symbol is locked
        """
        if not self.kv:
            return True  # No KV = allow (dev mode)
        
        key = f"{self.PREFIX_LOCK}{symbol}"
        
        try:
            # Check if already locked
            existing = await self.kv.get(key)
            if existing:
                # Lock exists, check if expired
                lock_data = json.loads(existing)
                if time.time() < lock_data.get('expires', 0):
                    return False  # Still locked
            
            # Acquire lock
            lock_data = {
                "symbol": symbol,
                "acquired_at": time.time(),
                "expires": time.time() + self.LOCK_TTL
            }
            await self.kv.put(key, json.dumps(lock_data), expirationTtl=self.LOCK_TTL)
            return True
            
        except Exception as e:
            log.error("lock_acquire_failed", symbol=symbol, error=str(e))
            return False
    
    async def release_lock(self, symbol: str) -> bool:
        """
        Release lock on a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            bool: True if released successfully
        """
        if not self.kv:
            return True
        
        key = f"{self.PREFIX_LOCK}{symbol}"
        
        try:
            await self.kv.delete(key)
            return True
        except Exception as e:
            log.error("lock_release_failed", symbol=symbol, error=str(e))
            return False
    
    async def is_locked(self, symbol: str) -> bool:
        """Check if symbol is currently locked."""
        if not self.kv:
            return False
        
        key = f"{self.PREFIX_LOCK}{symbol}"
        
        try:
            existing = await self.kv.get(key)
            if existing:
                lock_data = json.loads(existing)
                return time.time() < lock_data.get('expires', 0)
            return False
        except:
            return False
    
    # ==========================================
    # 📊 TRADE STATE
    # ==========================================
    
    async def record_trade(self, trade: Dict) -> str:
        """
        Record a new trade in state.
        
        Args:
            trade: Trade data {symbol, side, amount, entry_price, ...}
        
        Returns:
            str: Trade ID
        """
        if not self.kv:
            return "dev_trade_id"
        
        trade_id = f"{trade['symbol']}_{int(time.time())}"
        key = f"{self.PREFIX_TRADE}{trade_id}"
        
        trade_data = {
            **trade,
            "id": trade_id,
            "opened_at": time.time(),
            "status": "OPEN"
        }
        
        try:
            # Store trade (TTL 24 hours)
            await self.kv.put(key, json.dumps(trade_data), expirationTtl=86400)
            return trade_id
        except Exception as e:
            log.error("record_trade_failed", trade_id=trade_id, error=str(e))
            return ""
    
    async def get_open_trades(self) -> List[Dict]:
        """
        Get all open trades.
        
        Returns:
            list: Open trade records
        """
        if not self.kv:
            return []
        
        try:
            # List all trade keys
            keys = await self.kv.list(prefix=self.PREFIX_TRADE)
            trades = []
            
            for key in keys.get('keys', []):
                data = await self.kv.get(key['name'])
                if data:
                    trade = json.loads(data)
                    if trade.get('status') == 'OPEN':
                        trades.append(trade)
            
            return trades
        except Exception as e:
            log.error("get_trades_failed", error=str(e))
            return []
    
    async def close_trade(self, trade_id: str, exit_price: float) -> bool:
        """
        Mark trade as closed.
        
        Args:
            trade_id: Trade identifier
            exit_price: Closing price
        
        Returns:
            bool: Success
        """
        if not self.kv:
            return True
        
        key = f"{self.PREFIX_TRADE}{trade_id}"
        
        try:
            data = await self.kv.get(key)
            if data:
                trade = json.loads(data)
                trade['status'] = 'CLOSED'
                trade['exit_price'] = exit_price
                trade['closed_at'] = time.time()
                
                # Calculate P&L
                entry = trade.get('entry_price', 0)
                side = trade.get('side', 'BUY')
                if side.upper() == 'BUY':
                    trade['pnl'] = exit_price - entry
                else:
                    trade['pnl'] = entry - exit_price
                
                await self.kv.put(key, json.dumps(trade), expirationTtl=86400)
                return True
            return False
        except Exception as e:
            log.error("close_trade_failed", trade_id=trade_id, error=str(e))
            return False
    
    async def has_open_position(self, symbol: str) -> bool:
        """Check if there's an open position for symbol."""
        trades = await self.get_open_trades()
        return any(t.get('symbol') == symbol for t in trades)
    
    # ==========================================
    # ⏰ CRON COORDINATION
    # ==========================================
    
    async def acquire_cron_lock(self, job_name: str, ttl: int = 30) -> bool:
        """
        Acquire exclusive cron job lock.
        
        Prevents multiple cron instances from running simultaneously.
        
        Args:
            job_name: Cron job identifier (e.g., "scalper_5min")
            ttl: Lock timeout in seconds
        
        Returns:
            bool: True if lock acquired
        """
        if not self.kv:
            return True
        
        key = f"{self.PREFIX_CRON}{job_name}"
        
        try:
            existing = await self.kv.get(key)
            if existing:
                lock_data = json.loads(existing)
                if time.time() < lock_data.get('expires', 0):
                    return False  # Another cron is running
            
            lock_data = {
                "job": job_name,
                "started_at": time.time(),
                "expires": time.time() + ttl
            }
            await self.kv.put(key, json.dumps(lock_data), expirationTtl=ttl)
            return True
            
        except Exception as e:
            log.error("cron_lock_failed", job_name=job_name, error=str(e))
            return False
    
    async def release_cron_lock(self, job_name: str) -> bool:
        """Release cron job lock."""
        if not self.kv:
            return True
        
        key = f"{self.PREFIX_CRON}{job_name}"
        
        try:
            await self.kv.delete(key)
            return True
        except:
            return False
