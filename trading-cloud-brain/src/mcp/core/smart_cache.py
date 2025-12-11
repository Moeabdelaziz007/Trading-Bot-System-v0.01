import json
import asyncio
from datetime import datetime
import time

from core.structured_logging import get_logger
log = get_logger("smart_cache")

class SmartCache:
    """
    Tiered Caching System.
    L1: Cloudflare KV (Hot Memory) - Fast, expensive-ish
    L2: Cloudflare D1 (Cold Storage) - Slower, cheap, persistent
    """

    def __init__(self, kv_binding=None, d1_binding=None):
        self.kv = kv_binding
        self.d1 = d1_binding

    async def get_price(self, symbol: str):
        """
        Get price from cache (L1 only for speed).
        Returns dict or None.
        """
        key = f"price:{symbol}"
        data = await self.kv.get(key)
        if data:
            return json.loads(data)
        return None

    async def put_price(self, symbol: str, price_data: dict, ttl: int = 60):
        """
        Cache price in KV (Hot) and Async Write to D1 (Cold History).
        """
        key = f"price:{symbol}"
        # L1: KV
        await self.kv.put(key, json.dumps(price_data), expirationTtl=ttl)
        
        # L2: D1 (History) - Fire and await (fast enough for now)
        # We store minimal data in SQL for history
        try:
            timestamp = int(time.time())
            stmt = self.d1.prepare(
                "INSERT INTO market_ohlcv (symbol, timestamp, price, source) VALUES (?, ?, ?, ?)"
            ).bind(symbol, timestamp, price_data['current'], price_data.get('source', 'unknown'))
            await stmt.run()
        except Exception as e:
            log.error("d1_write_error", error=str(e))

    async def get_technicals(self, symbol: str):
        """
        Get technicals from L1. If missing, could check L2 but usually we recompute.
        """
        key = f"tech:{symbol}"
        data = await self.kv.get(key)
        if data:
            return json.loads(data)
        return None

    async def put_technicals(self, symbol: str, tech_data: dict, ttl: int = 14400): # 4 hours
        key = f"tech:{symbol}"
        await self.kv.put(key, json.dumps(tech_data), expirationTtl=ttl)

    async def get_news_sentiment(self, symbol: str):
        key = f"news:{symbol}"
        data = await self.kv.get(key)
        if data:
            return json.loads(data)
        return None

    async def put_news_sentiment(self, symbol: str, sentiment_data: dict, ttl: int = 900): # 15 min
        key = f"news:{symbol}"
        await self.kv.put(key, json.dumps(sentiment_data), expirationTtl=ttl)
