"""
API Router: The Brain of Smart MCP
Orchestrates data fetching with "Antigravity" rules.
"""

from .credit_manager import CreditManager
from .smart_cache import SmartCache
import re

class APIRouter:
    """
    Intelligent request router that:
    1. Checks cache first (L1/L2)
    2. Routes to appropriate API based on symbol type
    3. Manages rate limits via CreditManager
    4. Returns stale data as fallback
    """

    CRYPTO_PATTERNS = [
        r'BTC', r'ETH', r'USDT', r'SOL', r'XRP', r'DOGE',
        r'.*USDT$', r'.*USD$', r'.*PERP$'
    ]
    
    SYMBOL_MAP = {
        'gold': 'XAUUSD',
        'bitcoin': 'BTCUSDT',
        'ethereum': 'ETHUSDT',
        'oil': 'USOIL',
        'euro': 'EURUSD',
    }

    def __init__(self):
        self.credit_manager = CreditManager()
        self.cache = SmartCache()

    def _resolve_symbol(self, symbol: str) -> str:
        """Map friendly names to standard symbols."""
        return self.SYMBOL_MAP.get(symbol.lower(), symbol.upper())

    def _is_crypto(self, symbol: str) -> bool:
        """Check if symbol is cryptocurrency."""
        for pattern in self.CRYPTO_PATTERNS:
            if re.match(pattern, symbol, re.IGNORECASE):
                return True
        return False

    async def route_price_request(self, symbol: str) -> dict:
        """
        Smart routing for price requests.
        Returns: {"price": ..., "source": ..., "is_stale": bool}
        """
        symbol = self._resolve_symbol(symbol)
        
        # Step 1: Check Cache (Hot)
        cached = await self.cache.get_price(symbol)
        if cached:
            return {**cached, "is_stale": False, "source": "cache"}
        
        # Step 2: Crypto -> Bybit (Unlimited)
        if self._is_crypto(symbol):
            return {"action": "fetch_bybit", "symbol": symbol}
        
        # Step 3: Stock/Forex -> Check Finnhub Budget
        if await self.credit_manager.check_credits("finnhub", 1):
            return {"action": "fetch_finnhub", "symbol": symbol}
        
        # Step 4: No Budget -> Return Stale (5min old OK)
        # Caller should handle this gracefully
        return {"action": "return_stale", "symbol": symbol, "is_stale": True}

    async def route_technicals_request(self, symbol: str) -> dict:
        """
        Route technical indicator requests.
        Alpha Vantage is precious (25/day), so cache aggressively.
        """
        symbol = self._resolve_symbol(symbol)
        
        # Check Cache (4h TTL)
        cached = await self.cache.get_technicals(symbol)
        if cached:
            return {**cached, "is_stale": False, "source": "cache"}
        
        # Check Alpha Vantage Budget (cost=3 for technicals)
        if await self.credit_manager.check_credits("alpha_vantage", 3):
            return {"action": "fetch_alpha_vantage", "symbol": symbol}
        
        # Fallback: Try to compute from D1 history
        return {"action": "compute_from_d1", "symbol": symbol, "is_stale": True}

    async def route_news_request(self, symbol: str) -> dict:
        """
        Route news/sentiment requests.
        NewsData.io (200/day) or fallback to Workers AI sentiment.
        """
        symbol = self._resolve_symbol(symbol)
        
        # Check Cache (15min TTL)
        cached = await self.cache.get_news_sentiment(symbol)
        if cached:
            return {**cached, "is_stale": False, "source": "cache"}
        
        # Check NewsData Budget (cost=2)
        if await self.credit_manager.check_credits("news_data", 2):
            return {"action": "fetch_newsdata", "symbol": symbol}
        
        # Fallback: Return neutral or use Workers AI
        return {"action": "neutral_fallback", "symbol": symbol, "is_stale": True}
