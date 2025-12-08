"""
📰 NewsData.io Connector for AXIOM Trading System
Global News with Crypto & Finance Focus

FREE TIER: 200 requests/day
FEATURES: News from 150+ countries, Crypto news, Finance news

API Documentation: https://newsdata.io/documentation
"""

import json
from typing import Optional, List


class NewsDataConnector:
    """
    NewsData.io Integration for Trading News.
    
    Free Tier Features:
    - 200 API requests/day
    - News from 150+ countries
    - Category filtering (business, technology, crypto)
    - Language filtering
    - Full-text article content
    """
    
    BASE_URL = "https://newsdata.io/api/1"
    
    def __init__(self, api_key: str):
        """
        Initialize with NewsData.io API key.
        Get free key at: https://newsdata.io/register
        """
        self.api_key = api_key
        self.requests_today = 0
        self.max_daily_requests = 200
    
    def _can_request(self) -> bool:
        """Check if we have remaining daily quota."""
        return self.requests_today < self.max_daily_requests
    
    async def _fetch(self, endpoint: str, params: dict = None) -> dict:
        """Make API request to NewsData.io."""
        from js import fetch
        
        if not self._can_request():
            return {"error": "Daily limit reached (200 requests)"}
        
        params = params or {}
        params["apikey"] = self.api_key
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}{endpoint}?{query_string}"
        
        response = await fetch(url)
        self.requests_today += 1
        
        data = await response.json()
        
        if data.get("status") != "success":
            return {"error": data.get("results", {}).get("message", "Unknown error")}
        
        return data
    
    # ==========================================
    # 📰 NEWS ENDPOINTS
    # ==========================================
    
    async def get_crypto_news(self, language: str = "en") -> list:
        """
        Get latest cryptocurrency news.
        
        Args:
            language: Language code (en, ar, etc.)
        
        Returns:
            list: News articles about crypto
        """
        data = await self._fetch("/news", {
            "category": "technology",
            "q": "crypto OR bitcoin OR ethereum OR solana",
            "language": language
        })
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    async def get_forex_news(self, language: str = "en") -> list:
        """Get forex and currency market news."""
        data = await self._fetch("/news", {
            "category": "business",
            "q": "forex OR currency OR dollar OR EUR/USD",
            "language": language
        })
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    async def get_market_news(
        self,
        query: str = None,
        category: str = "business",
        country: str = None,
        language: str = "en"
    ) -> list:
        """
        Get general market news.
        
        Args:
            query: Search keywords (e.g., "gold", "oil", "stocks")
            category: business, technology, world, etc.
            country: Country code (us, gb, ae, eg, etc.)
            language: Language code
        """
        params = {
            "category": category,
            "language": language
        }
        
        if query:
            params["q"] = query
        if country:
            params["country"] = country
        
        data = await self._fetch("/news", params)
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    async def get_breaking_news(self, country: str = "us") -> list:
        """Get breaking news from a specific country."""
        data = await self._fetch("/news", {
            "country": country,
            "category": "top"
        })
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    async def search_news(
        self,
        keywords: str,
        from_date: str = None,
        to_date: str = None,
        language: str = "en"
    ) -> list:
        """
        Search news by keywords.
        
        Args:
            keywords: Search terms
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            language: Language code
        """
        params = {
            "q": keywords,
            "language": language
        }
        
        # Note: Date filtering may require premium
        
        data = await self._fetch("/news", params)
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    # ==========================================
    # 🎯 TRADING-FOCUSED NEWS
    # ==========================================
    
    async def get_trading_news(self, symbols: list = None) -> list:
        """
        Get news relevant to trading.
        Combines crypto, forex, and market news.
        
        Uses 1 API call.
        """
        symbols = symbols or ["BTC", "ETH", "SOL", "GOLD", "OIL"]
        query = " OR ".join(symbols)
        
        data = await self._fetch("/news", {
            "q": query,
            "language": "en",
            "category": "business,technology"
        })
        
        if "error" in data:
            return []
        
        return self._parse_articles(data.get("results", []))
    
    async def get_news_with_sentiment(self, symbol: str) -> dict:
        """
        Get news for a symbol with basic sentiment analysis.
        Uses keyword matching for sentiment (free alternative).
        """
        news = await self.search_news(symbol)
        
        if not news:
            return {"symbol": symbol, "sentiment": "NEUTRAL", "score": 0, "articles": []}
        
        # Keyword-based sentiment
        positive_words = [
            "surge", "rally", "gain", "profit", "growth", "beat", "upgrade",
            "bullish", "record", "high", "strong", "optimistic", "buy"
        ]
        negative_words = [
            "drop", "fall", "loss", "decline", "crash", "miss", "downgrade",
            "bearish", "low", "weak", "concern", "sell", "fear", "risk"
        ]
        
        total_score = 0
        
        for article in news:
            text = (article["title"] + " " + article.get("description", "")).lower()
            
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            total_score += (pos_count - neg_count)
        
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
            "articles": news[:5],  # Top 5 articles
            "articles_analyzed": len(news)
        }
    
    # ==========================================
    # 🔧 HELPER METHODS
    # ==========================================
    
    def _parse_articles(self, articles: list) -> list:
        """Parse raw API response into clean article format."""
        parsed = []
        
        for article in articles[:20]:  # Limit to 20
            parsed.append({
                "title": article.get("title", ""),
                "description": article.get("description", "")[:300] if article.get("description") else "",
                "content": article.get("content", "")[:500] if article.get("content") else "",
                "source": article.get("source_id", ""),
                "url": article.get("link", ""),
                "image": article.get("image_url", ""),
                "published": article.get("pubDate", ""),
                "country": article.get("country", []),
                "category": article.get("category", []),
                "keywords": article.get("keywords", [])
            })
        
        return parsed
    
    def reset_daily_counter(self):
        """Reset daily request counter (call at midnight)."""
        self.requests_today = 0
    
    def get_status(self) -> dict:
        """Get current API usage status."""
        return {
            "requests_today": self.requests_today,
            "requests_remaining": self.max_daily_requests - self.requests_today,
            "max_daily": self.max_daily_requests
        }
