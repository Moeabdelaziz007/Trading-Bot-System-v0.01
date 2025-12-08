"""
Smart MCP Main Endpoint: get_market_intelligence
The unified interface that orchestrates all components.
"""

from .core import APIRouter, SignalSynthesizer, SmartCache, CreditManager
from .tools import get_finnhub_price, get_bybit_price, get_alpha_vantage_technicals, get_newsdata_sentiment

class MarketIntelligenceMCP:
    """
    The main MCP server that exposes the get_market_intelligence tool.
    This is the single entry point for AI agents to get market data.
    """
    
    def __init__(self, secrets: dict):
        """
        Initialize with API secrets.
        
        Args:
            secrets: {"FINNHUB_API_KEY": ..., "ALPHA_VANTAGE_KEY": ..., "NEWSDATA_KEY": ...}
        """
        self.router = APIRouter()
        self.synthesizer = SignalSynthesizer()
        self.cache = SmartCache()
        self.credits = CreditManager()
        self.secrets = secrets

    async def get_market_intelligence(self, symbol: str) -> dict:
        """
        The unified MCP tool that returns complete market intelligence.
        
        Args:
            symbol: Ticker symbol (e.g., "AAPL", "BTCUSDT", "Gold")
            
        Returns:
            MarketState object with price, technicals, sentiment, and composite signal.
        """
        result = {
            "symbol": symbol,
            "is_stale": False,
            "price": None,
            "technicals": None,
            "sentiment": None,
            "composite_signal": None,
            "errors": []
        }
        
        # 1. Fetch Price
        price_route = await self.router.route_price_request(symbol)
        
        if price_route.get("action") == "fetch_bybit":
            price_data = await get_bybit_price(price_route["symbol"])
        elif price_route.get("action") == "fetch_finnhub":
            await self.credits.deduct_credit("finnhub", 1)
            price_data = await get_finnhub_price(
                price_route["symbol"], 
                self.secrets.get("FINNHUB_API_KEY", "")
            )
            if "error" not in price_data:
                await self.cache.put_price(symbol, price_data)
        elif price_route.get("source") == "cache":
            price_data = price_route
        else:
            price_data = {"current": 0, "change_pct": 0, "source": "stale"}
            result["is_stale"] = True
        
        result["price"] = price_data
        
        # 2. Fetch Technicals
        tech_route = await self.router.route_technicals_request(symbol)
        
        if tech_route.get("action") == "fetch_alpha_vantage":
            await self.credits.deduct_credit("alpha_vantage", 3)
            tech_data = await get_alpha_vantage_technicals(
                symbol,
                self.secrets.get("ALPHA_VANTAGE_KEY", "")
            )
            if "error" not in tech_data:
                await self.cache.put_technicals(symbol, tech_data)
        elif tech_route.get("source") == "cache":
            tech_data = tech_route
        else:
            # Return default values if no data
            tech_data = {"rsi_14": 50, "macd": {"value": 0, "signal": 0}, "source": "default"}
            result["is_stale"] = True
        
        result["technicals"] = tech_data
        
        # 3. Fetch News/Sentiment
        news_route = await self.router.route_news_request(symbol)
        
        if news_route.get("action") == "fetch_newsdata":
            await self.credits.deduct_credit("news_data", 2)
            sentiment_data = await get_newsdata_sentiment(
                symbol,
                self.secrets.get("NEWSDATA_KEY", "")
            )
            if "error" not in sentiment_data:
                await self.cache.put_news_sentiment(symbol, sentiment_data)
        elif news_route.get("source") == "cache":
            sentiment_data = news_route
        else:
            sentiment_data = {"score": 0, "headline_count": 0, "source": "neutral"}
        
        result["sentiment"] = sentiment_data
        
        # 4. Synthesize Signal
        try:
            composite = self.synthesizer.synthesize(
                price_change_pct=price_data.get("change_pct", 0),
                rsi_14=tech_data.get("rsi_14", 50),
                macd_value=tech_data.get("macd", {}).get("value", 0),
                macd_signal=tech_data.get("macd", {}).get("signal", 0),
                sentiment_score=sentiment_data.get("score", 0),
                volume_change_pct=price_data.get("volume_change_pct", 0) if "volume_change_pct" in price_data else 0
            )
            result["composite_signal"] = composite
        except Exception as e:
            result["errors"].append(f"Synthesis error: {str(e)}")
            result["composite_signal"] = {"direction": "NEUTRAL", "confidence": 0}
        
        return result

    async def get_api_health(self) -> dict:
        """
        Check remaining API credits for monitoring.
        """
        return {
            "finnhub": await self.credits.get_remaining_credits("finnhub"),
            "alpha_vantage": await self.credits.get_remaining_credits("alpha_vantage"),
            "news_data": await self.credits.get_remaining_credits("news_data"),
        }
