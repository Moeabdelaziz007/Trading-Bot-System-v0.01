"""
Real-time Price Streaming via SSE (Server-Sent Events)
Zero-cost alternative to WebSockets for Cloudflare Workers.
"""

import asyncio
import json
import random
from typing import Dict, Any, AsyncGenerator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PriceStreamSimulator:
    """
    Simulates real-time price data for development/demo.
    In production, replace with actual MT5 bridge connection.
    """
    
    def __init__(self):
        self.base_prices = {
            "XAUUSD": 2650.00,
            "EURUSD": 1.0850,
            "GBPUSD": 1.2750,
            "USDJPY": 149.50,
            "BTCUSD": 95000.00,
            "ETHUSD": 3500.00
        }
        self.volatility = {
            "XAUUSD": 0.50,
            "EURUSD": 0.0005,
            "GBPUSD": 0.0008,
            "USDJPY": 0.10,
            "BTCUSD": 100.00,
            "ETHUSD": 20.00
        }
    
    def get_tick(self, symbol: str) -> Dict[str, Any]:
        """Generate a simulated price tick"""
        base = self.base_prices.get(symbol, 100.0)
        vol = self.volatility.get(symbol, 0.01)
        
        # Random walk
        change = random.uniform(-vol, vol)
        new_price = base + change
        self.base_prices[symbol] = new_price
        
        spread = vol * 0.1
        
        return {
            "symbol": symbol,
            "bid": round(new_price, 5),
            "ask": round(new_price + spread, 5),
            "timestamp": datetime.now().isoformat(),
            "volume": random.randint(100, 10000)
        }


async def stream_prices_sse(
    symbols: list = None,
    interval_ms: int = 500
) -> AsyncGenerator[str, None]:
    """
    Stream price updates via SSE format.
    
    Args:
        symbols: List of symbols to stream (default: all)
        interval_ms: Update interval in milliseconds
    
    Yields:
        SSE formatted price events
    """
    if symbols is None:
        symbols = ["XAUUSD", "EURUSD", "GBPUSD", "BTCUSD"]
    
    simulator = PriceStreamSimulator()
    
    # Send initial connection event
    yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'symbols': symbols})}\n\n"
    
    tick_count = 0
    max_ticks = 100  # Limit for demo
    
    while tick_count < max_ticks:
        for symbol in symbols:
            tick = simulator.get_tick(symbol)
            yield f"event: price\ndata: {json.dumps(tick)}\n\n"
        
        tick_count += 1
        await asyncio.sleep(interval_ms / 1000)
    
    yield f"event: complete\ndata: {json.dumps({'status': 'complete', 'ticks': tick_count})}\n\n"


# For testing
async def demo_stream():
    async for event in stream_prices_sse(["XAUUSD", "BTCUSD"], 1000):
        print(event, end="")


if __name__ == "__main__":
    asyncio.run(demo_stream())
