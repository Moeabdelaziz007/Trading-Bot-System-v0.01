"""
📡 Data Collector Module for Axiom Antigravity
The "Eyes" - Gathers raw data from global markets.

ROLE:
- Fetches real-time price data (Capital.com/Alpha Vantage).
- Feaches news headlines (Finnhub/RSS).
- Prepares context for the Brains (Analyst/Reflex).

ZERO-COST INFRASTRUCTURE:
- Uses Free Tier APIs.
- Caches data in Workers KV to minimize requests.
"""

import json
from js import fetch

class DataCollector:
    def __init__(self, env):
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.finnhub_key = getattr(env, 'FINNHUB_API_KEY', '')

    async def get_market_context(self, symbol: str) -> dict:
        """
        Gather comprehensive market context for a symbol.
        1. Recent News (Finnhub)
        2. Technical Snapshot (Alpha Vantage - mocked/cached for zero cost)
        """
        news = await self._fetch_finnhub_news(symbol)
        # technicals = await self._fetch_technicals(symbol) # Placeholder
        
        return {
            "symbol": symbol,
            "news": news,
            # "technicals": technicals
        }

    async def _fetch_finnhub_news(self, symbol: str) -> list:
        """Fetch general market news or symbol specific if available"""
        # Check cache
        cache_key = f"news_cache:{symbol}"
        if self.kv:
            cached = await self.kv.get(cache_key)
            if cached:
                return json.loads(cached)
        
        try:
            # General news category for Forex
            category = "forex" if "USD" in symbol or "EUR" in symbol else "general"
            url = f"https://finnhub.io/api/v1/news?category={category}&token={self.finnhub_key}"
            
            resp = await fetch(url)
            if resp.ok:
                data = json.loads(await resp.text())
                # Normalize data (first 5 headlines)
                headlines = [
                    {"headline": item.get("headline"), "summary": item.get("summary")}
                    for item in data[:5]
                ]
                
                # Cache for 15 mins
                if self.kv:
                    await self.kv.put(cache_key, json.dumps(headlines), expiration_ttl=900)
                    
                return headlines
        except Exception as e:
            print(f"News fetch error: {e}")
            
        return []
