"""
📰 Finnhub Data Connector for AXIOM Trading System
Market Data, News, and Company Fundamentals

FREE TIER: 60 API calls/minute
FEATURES: Real-time quotes, company news, earnings, forex rates

Note: Sentiment Analysis is PREMIUM only.
For free tier, we use news headlines for basic sentiment scoring.

API Documentation: https://finnhub.io/docs/api
"""

import json
from typing import Optional, Dict, List


class FinnhubConnector:
    """
    Finnhub Market Data Integration.
    
    Free Tier Features:
    - Real-time quotes (US stocks, Forex)
    - Company news
    - Earnings calendar
    - Basic fundamentals
    
    Premium Only (not included):
    - Sentiment Analysis
    - SEC filings sentiment
    - Social media sentiment
    """
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize with Finnhub API key.
        Get free key at: https://finnhub.io/register
        """
        self.api_key = api_key
    
    async def _fetch(self, endpoint: str, params: dict = None) -> dict:
        """Make API request to Finnhub."""
        from js import fetch
        
        params = params or {}
        params["token"] = self.api_key
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}{endpoint}?{query_string}"
        
        response = await fetch(url)
        
        if response.status == 429:
            return {"error": "Rate limit exceeded (60 calls/min)"}
        
        data = await response.json()
        return data
    
    # ==========================================
    # 📈 MARKET DATA
    # ==========================================
    
    async def get_quote(self, symbol: str) -> dict:
        """
        Get real-time quote for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "TSLA")
        
        Returns:
            dict: {current, high, low, open, prev_close, change, change_pct}
        """
        data = await self._fetch("/quote", {"symbol": symbol})
        
        if "error" in data or "c" not in data:
            return {"error": "Failed to fetch quote"}
        
        current = data.get("c", 0)
        prev = data.get("pc", current)
        change = current - prev
        change_pct = (change / prev * 100) if prev else 0
        
        return {
            "symbol": symbol,
            "current": current,
            "high": data.get("h", 0),
            "low": data.get("l", 0),
            "open": data.get("o", 0),
            "prev_close": prev,
            "change": round(change, 4),
            "change_pct": round(change_pct, 2),
            "timestamp": data.get("t", 0)
        }
    
    async def get_forex_rate(self, symbol: str = "EUR/USD") -> dict:
        """
        Get forex exchange rate.
        
        Args:
            symbol: Forex pair (e.g., "EUR/USD", "GBP/USD")
        
        Returns:
            dict: {rate, timestamp}
        """
        # Finnhub uses different symbols for forex
        forex_symbol = f"OANDA:{symbol.replace('/', '_')}"
        
        data = await self._fetch("/quote", {"symbol": forex_symbol})
        
        if "error" in data or "c" not in data:
            return {"error": "Failed to fetch forex rate"}
        
        return {
            "symbol": symbol,
            "rate": data.get("c", 0),
            "high": data.get("h", 0),
            "low": data.get("l", 0),
            "prev_close": data.get("pc", 0),
            "timestamp": data.get("t", 0)
        }
    
    async def get_crypto_candles(
        self,
        symbol: str,
        resolution: str = "5",
        from_ts: int = None,
        to_ts: int = None
    ) -> list:
        """
        Get crypto candlestick data.
        
        Args:
            symbol: Crypto symbol (e.g., "BINANCE:BTCUSDT")
            resolution: 1, 5, 15, 30, 60, D, W, M
            from_ts: Unix timestamp start
            to_ts: Unix timestamp end
        """
        import time
        
        to_ts = to_ts or int(time.time())
        from_ts = from_ts or (to_ts - 86400)  # Last 24 hours
        
        data = await self._fetch("/crypto/candle", {
            "symbol": symbol,
            "resolution": resolution,
            "from": str(from_ts),
            "to": str(to_ts)
        })
        
        if data.get("s") != "ok":
            return {"error": "No data available"}
        
        candles = []
        times = data.get("t", [])
        opens = data.get("o", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        closes = data.get("c", [])
        volumes = data.get("v", [])
        
        for i in range(len(times)):
            candles.append({
                "time": times[i],
                "open": opens[i],
                "high": highs[i],
                "low": lows[i],
                "close": closes[i],
                "volume": volumes[i]
            })
        
        return candles
    
    # ==========================================
    # 📰 NEWS & FUNDAMENTALS
    # ==========================================
    
    async def get_company_news(
        self,
        symbol: str,
        from_date: str = None,
        to_date: str = None
    ) -> list:
        """
        Get company news headlines.
        
        Args:
            symbol: Stock symbol
            from_date: YYYY-MM-DD
            to_date: YYYY-MM-DD
        
        Returns:
            list: News articles with headline, summary, source
        """
        from datetime import datetime, timedelta
        
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        data = await self._fetch("/company-news", {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        })
        
        if isinstance(data, dict) and "error" in data:
            return []
        
        news = []
        for article in data[:20]:  # Limit to 20 articles
            news.append({
                "headline": article.get("headline", ""),
                "summary": article.get("summary", "")[:200],
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "datetime": article.get("datetime", 0),
                "related": article.get("related", "")
            })
        
        return news
    
    async def get_market_news(self, category: str = "general") -> list:
        """
        Get general market news.
        
        Args:
            category: general, forex, crypto, merger
        """
        data = await self._fetch("/news", {"category": category})
        
        if isinstance(data, dict) and "error" in data:
            return []
        
        news = []
        for article in data[:15]:
            news.append({
                "headline": article.get("headline", ""),
                "summary": article.get("summary", "")[:200],
                "source": article.get("source", ""),
                "url": article.get("url", ""),
                "datetime": article.get("datetime", 0),
                "category": category
            })
        
        return news
    
    # ==========================================
    # 🎯 BASIC SENTIMENT (FREE ALTERNATIVE)
    # ==========================================
    
    async def get_news_sentiment_basic(self, symbol: str) -> dict:
        """
        Basic sentiment analysis using news headlines.
        FREE alternative to premium sentiment API.
        
        Uses keyword matching for basic sentiment scoring.
        """
        news = await self.get_company_news(symbol)
        
        if not news:
            return {"sentiment": "NEUTRAL", "score": 0, "articles": 0}
        
        # Keyword-based sentiment (basic)
        positive_words = [
            "surge", "rally", "gain", "profit", "growth", "beat", "upgrade",
            "bullish", "record", "high", "strong", "optimistic", "buy",
            "outperform", "soar", "jump", "boost", "successful"
        ]
        negative_words = [
            "drop", "fall", "loss", "decline", "crash", "miss", "downgrade",
            "bearish", "low", "weak", "concern", "sell", "underperform",
            "plunge", "slump", "cut", "warning", "fear", "risk"
        ]
        
        total_score = 0
        
        for article in news:
            text = (article["headline"] + " " + article["summary"]).lower()
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            total_score += (pos_count - neg_count)
        
        # Normalize score
        avg_score = total_score / len(news) if news else 0
        
        if avg_score > 0.5:
            sentiment = "BULLISH"
        elif avg_score < -0.5:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        return {
            "symbol": symbol,
            "sentiment": sentiment,
            "score": round(avg_score, 2),
            "articles_analyzed": len(news),
            "method": "keyword_matching",
            "note": "Basic analysis. For AI sentiment, use Groq/DeepSeek."
        }
    
    # ==========================================
    # 📊 EARNINGS & FUNDAMENTALS
    # ==========================================
    
    async def get_earnings_calendar(
        self,
        from_date: str = None,
        to_date: str = None
    ) -> list:
        """Get upcoming earnings announcements."""
        from datetime import datetime, timedelta
        
        if not to_date:
            to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        if not from_date:
            from_date = datetime.now().strftime("%Y-%m-%d")
        
        data = await self._fetch("/calendar/earnings", {
            "from": from_date,
            "to": to_date
        })
        
        earnings = data.get("earningsCalendar", [])
        
        return [{
            "symbol": e.get("symbol"),
            "date": e.get("date"),
            "eps_estimate": e.get("epsEstimate"),
            "eps_actual": e.get("epsActual"),
            "revenue_estimate": e.get("revenueEstimate"),
            "hour": e.get("hour", "unknown")
        } for e in earnings[:50]]
    
    async def get_company_profile(self, symbol: str) -> dict:
        """Get company profile/fundamentals."""
        data = await self._fetch("/stock/profile2", {"symbol": symbol})
        
        if not data or "error" in data:
            return {"error": "Company not found"}
        
        return {
            "symbol": symbol,
            "name": data.get("name", ""),
            "industry": data.get("finnhubIndustry", ""),
            "market_cap": data.get("marketCapitalization", 0),
            "country": data.get("country", ""),
            "exchange": data.get("exchange", ""),
            "ipo": data.get("ipo", ""),
            "logo": data.get("logo", ""),
            "weburl": data.get("weburl", "")
        }
