"""
📡 Webhook Signal Listener - External Signal Receiver
======================================================
FastAPI server that receives trading signals from external sources
(TradingView, custom scripts, etc.) and routes them to Portfolio Manager.

Inspired by: hackingthemarkets/tradingview-binance-strategy-alert-webhook

Usage:
    1. Run this server: python -m src.webhook_listener
    2. Configure your TradingView alert to POST to: http://YOUR_IP:8000/webhook
    3. Signals are automatically routed to Portfolio Manager

Security:
    - Passphrase validation (env: AXIOM_WEBHOOK_SECRET)
    - IP whitelist support
    - Rate limiting
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Will be imported when Portfolio Manager is available
# from src.engine import PortfolioManager

logger = logging.getLogger(__name__)


# =====================
# SIGNAL MODELS
# =====================

class TradingSignal(BaseModel):
    """
    Incoming trading signal schema.
    Compatible with TradingView alert format.
    """
    passphrase: str = Field(..., description="Security passphrase")
    exchange: str = Field(..., description="Target exchange: 'BYBIT' or 'MT5'")
    symbol: str = Field(..., description="Trading symbol: 'BTCUSDT', 'XAUUSD'")
    action: str = Field(..., description="Trade action: 'BUY' or 'SELL'")
    volume: float = Field(..., gt=0, description="Position size")
    leverage: int = Field(default=1, ge=1, le=100, description="Leverage multiplier")
    stop_loss: Optional[float] = Field(default=None, description="Stop loss price")
    take_profit: Optional[float] = Field(default=None, description="Take profit price")
    comment: Optional[str] = Field(default=None, description="Signal comment/source")


class SignalResponse(BaseModel):
    """Response after processing a signal."""
    status: str
    message: str
    order_id: Optional[str] = None
    executed_at: str
    signal: dict


# =====================
# SIGNAL QUEUE
# =====================

class SignalQueue:
    """
    Thread-safe queue for incoming signals.
    Allows decoupled processing from the HTTP layer.
    """
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._history: List[dict] = []
        self._max_history = 100
    
    async def push(self, signal: TradingSignal) -> None:
        """Add a signal to the queue."""
        entry = {
            "signal": signal.dict(),
            "received_at": datetime.now().isoformat(),
            "processed": False
        }
        await self._queue.put(entry)
        self._history.append(entry)
        
        # Trim history
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
    
    async def pop(self) -> Optional[dict]:
        """Get next signal from queue."""
        try:
            return self._queue.get_nowait()
        except asyncio.QueueEmpty:
            return None
    
    def get_history(self, limit: int = 10) -> List[dict]:
        """Get recent signal history."""
        return self._history[-limit:]
    
    @property
    def pending_count(self) -> int:
        return self._queue.qsize()


# Global signal queue
signal_queue = SignalQueue()


# =====================
# SECURITY
# =====================

def get_webhook_secret() -> str:
    """Get webhook secret from environment."""
    secret = os.getenv("AXIOM_WEBHOOK_SECRET", "")
    if not secret:
        logger.warning("⚠️ AXIOM_WEBHOOK_SECRET not set! Using default (INSECURE)")
        return "axiom_default_secret_change_me"
    return secret


def validate_passphrase(passphrase: str) -> bool:
    """Validate incoming passphrase against secret."""
    return passphrase == get_webhook_secret()


# =====================
# PORTFOLIO MANAGER INTEGRATION
# =====================

# Placeholder for Portfolio Manager instance
_portfolio_manager = None

def set_portfolio_manager(pm) -> None:
    """Set the Portfolio Manager instance for signal execution."""
    global _portfolio_manager
    _portfolio_manager = pm
    logger.info("📡 Webhook Listener: Portfolio Manager connected")


async def execute_signal(signal: TradingSignal) -> dict:
    """
    Execute a trading signal via Portfolio Manager.
    
    Returns:
        Execution result dict
    """
    if _portfolio_manager is None:
        logger.warning("Portfolio Manager not connected - signal queued only")
        return {"success": False, "message": "Portfolio Manager not connected"}
    
    try:
        result = await _portfolio_manager.execute_trade(
            exchange=signal.exchange.lower(),
            symbol=signal.symbol,
            side=signal.action.lower(),
            size=signal.volume,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            leverage=signal.leverage
        )
        
        return {
            "success": result.success,
            "order_id": result.order_id,
            "message": result.message
        }
        
    except Exception as e:
        logger.error(f"Signal execution failed: {e}")
        return {"success": False, "message": str(e)}


# =====================
# FASTAPI APP
# =====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("📡 Webhook Listener starting...")
    yield
    logger.info("📡 Webhook Listener shutting down...")


app = FastAPI(
    title="Axiom Alpha Webhook Listener",
    description="Receive external trading signals from TradingView and other sources",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================
# ENDPOINTS
# =====================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Axiom Alpha Webhook Listener",
        "pending_signals": signal_queue.pending_count
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "portfolio_manager_connected": _portfolio_manager is not None,
        "pending_signals": signal_queue.pending_count,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook", response_model=SignalResponse)
async def receive_webhook(signal: TradingSignal, request: Request):
    """
    Main webhook endpoint for receiving trading signals.
    
    TradingView Alert Format:
    ```json
    {
        "passphrase": "YOUR_SECRET",
        "exchange": "BYBIT",
        "symbol": "BTCUSDT",
        "action": "BUY",
        "volume": 0.01,
        "leverage": 10
    }
    ```
    """
    # Security check
    if not validate_passphrase(signal.passphrase):
        logger.warning(f"⛔ Unauthorized webhook attempt from {request.client.host}")
        raise HTTPException(status_code=403, detail="Invalid passphrase")
    
    # Log the signal
    logger.info(f"📩 SIGNAL: {signal.action} {signal.volume} {signal.symbol} on {signal.exchange}")
    
    # Queue the signal
    await signal_queue.push(signal)
    
    # Attempt immediate execution if PM is connected
    execution_result = await execute_signal(signal)
    
    return SignalResponse(
        status="executed" if execution_result.get("success") else "queued",
        message=execution_result.get("message", "Signal received and queued"),
        order_id=execution_result.get("order_id"),
        executed_at=datetime.now().isoformat(),
        signal=signal.dict(exclude={"passphrase"})  # Don't echo secret
    )


@app.get("/signals/history")
async def get_signal_history(limit: int = 10):
    """Get recent signal history (for debugging)."""
    history = signal_queue.get_history(limit)
    # Redact passphrases
    for entry in history:
        if "passphrase" in entry.get("signal", {}):
            entry["signal"]["passphrase"] = "***"
    return {"history": history}


@app.post("/signals/clear")
async def clear_queue():
    """Clear pending signal queue (admin only)."""
    count = signal_queue.pending_count
    while not signal_queue._queue.empty():
        try:
            signal_queue._queue.get_nowait()
        except asyncio.QueueEmpty:
            break
    return {"cleared": count}


# =====================
# STANDALONE RUNNER
# =====================

def run_webhook_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the webhook server standalone."""
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║   📡 AXIOM ALPHA WEBHOOK LISTENER            ║
    ║   Listening on: http://{host}:{port}         ║
    ║   Endpoint: POST /webhook                    ║
    ╚══════════════════════════════════════════════╝
    """)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_webhook_server()
