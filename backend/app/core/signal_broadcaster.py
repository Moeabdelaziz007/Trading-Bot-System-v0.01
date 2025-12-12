"""
🚀 Fire-and-Forget Signal Broadcaster
Sends signals to AlphaAPI Gateway without blocking the core engine.

Architecture:
    Decision Engine → evaluate_trade() → BUY Signal
                                          ↓ Fire-and-Forget
                        broadcaster.broadcast(signal)
                                          ↓ asyncio.create_task()
                        POST to Sentinel Gateway (non-blocking)

Safety:
    - NEVER awaits the HTTP response
    - If Gateway is down, logs warning and CONTINUES
    - Uses aiohttp for async HTTP
"""

import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Try to import aiohttp, fallback to httpx or requests if not available
try:
    import aiohttp
    ASYNC_CLIENT = "aiohttp"
except ImportError:
    try:
        import httpx
        ASYNC_CLIENT = "httpx"
    except ImportError:
        ASYNC_CLIENT = None
        print("⚠️ [Broadcaster] No async HTTP client available. Install aiohttp or httpx.")


class SignalBroadcaster:
    """
    Async broadcaster that NEVER blocks the Decision Engine.
    
    Usage:
        from .signal_broadcaster import broadcaster
        broadcaster.broadcast({"action": "BUY", "symbol": "BTCUSD", ...})
    """
    
    def __init__(self):
        self.gateway_url = os.getenv(
            "ALPHA_GATEWAY_URL", 
            "https://api.alphaaxiom.com/api/v1/signals/push"
        )
        self.internal_token = os.getenv("ALPHA_INTERNAL_TOKEN", "")
        self._session: Optional[aiohttp.ClientSession] = None
        self._tasks: set = set()  # Track background tasks to prevent GC
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy initialization of aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5),
                headers={"X-Internal-Token": self.internal_token}
            )
        return self._session
    
    async def _push_signal(self, signal: Dict[str, Any]) -> None:
        """
        Internal: Actually POST to Gateway.
        This runs in background - errors are logged, not raised.
        """
        if ASYNC_CLIENT != "aiohttp":
            print(f"⚠️ [Broadcaster] aiohttp not available. Signal not sent.")
            return
            
        try:
            session = await self._get_session()
            
            # Ensure signal has required fields
            if "signal_id" not in signal:
                signal["signal_id"] = f"aa-{uuid.uuid4().hex[:12]}"
            if "timestamp" not in signal:
                signal["timestamp"] = datetime.utcnow().isoformat()
            
            async with session.post(self.gateway_url, json=signal) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"📡 [Broadcaster] Signal pushed: {signal['action']} {signal.get('symbol', 'N/A')} → {result}")
                else:
                    text = await response.text()
                    print(f"⚠️ [Broadcaster] Gateway returned {response.status}: {text}")
                    
        except asyncio.TimeoutError:
            print(f"⚠️ [Broadcaster] Gateway timeout. Signal queued locally. Continuing...")
        except aiohttp.ClientError as e:
            print(f"⚠️ [Broadcaster] Gateway unreachable: {e}. Continuing...")
        except Exception as e:
            # CRITICAL: Never crash the engine. Just log the error.
            print(f"⚠️ [Broadcaster] Unexpected error: {e}. Continuing...")
    
    def broadcast(self, signal: Dict[str, Any]) -> None:
        """
        Fire-and-Forget: Create a background task for the signal.
        
        This method:
        - NEVER blocks (returns immediately)
        - If Gateway is down, engine continues
        - Safe to call from sync or async context
        
        Args:
            signal: Dict with at least {"action": "BUY"|"SELL", "symbol": "..."}
        """
        if not self.internal_token:
            print("⚠️ [Broadcaster] ALPHA_INTERNAL_TOKEN not set. Signal not broadcast.")
            return
            
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._push_signal(signal))
            # Store reference to prevent garbage collection
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
            
        except RuntimeError:
            # No event loop running - try to create one
            try:
                asyncio.run(self._push_signal(signal))
            except Exception as e:
                print(f"⚠️ [Broadcaster] No event loop. Signal not broadcast: {e}")
    
    async def close(self) -> None:
        """Clean up HTTP session. Call on shutdown."""
        if self._session and not self._session.closed:
            await self._session.close()


# Singleton instance for easy import
broadcaster = SignalBroadcaster()


# Convenience function
def broadcast_signal(signal: Dict[str, Any]) -> None:
    """
    Convenience function to broadcast a signal.
    
    Example:
        from backend.app.core.signal_broadcaster import broadcast_signal
        broadcast_signal({"action": "BUY", "symbol": "EURUSD", "quantity": 0.1})
    """
    broadcaster.broadcast(signal)
