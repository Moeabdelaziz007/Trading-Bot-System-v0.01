"""
📡 MarketFeed - Unified Market Data Module
Consolidates DataCollector + EconomicCalendar + SentimentAnalyzer.

SENSOR Layer - The "Eyes" of the Trading Brain.

Components:
    - Collector: OHLCV candles, real-time quotes
    - Calendar: Economic events, news impact
    - Sentiment: News sentiment analysis

Usage:
    feed = MarketFeed(env)
    
    # Get comprehensive market data
    data = await feed.get_market_context("EURUSD")
    
    # Check if safe to trade
    impact = await feed.check_news_impact("EURUSD")
"""

import json
import time
from typing import Dict, List, Optional
from js import fetch, Headers
from brokers.gateway import BrokerGateway


# High-impact event types to avoid
HIGH_IMPACT_EVENTS = [
    "Non-Farm Payrolls", "NFP", "FOMC", "Interest Rate Decision",
    "CPI", "Core CPI", "GDP", "Retail Sales", "Unemployment Rate",
    "PMI", "ECB", "BOE", "BOJ", "Fed Chair", "Powell", "Lagarde"
]

# Currency pair mapping
CURRENCY_MAP = {
    "USD": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"],
    "EUR": ["EURUSD", "EURGBP", "EURJPY"],
    "GBP": ["GBPUSD", "EURGBP", "GBPJPY"],
    "JPY": ["USDJPY", "EURJPY", "GBPJPY"],
    "XAU": ["XAUUSD"],
    "BTC": ["BTCUSD"]
}

# News buffer windows (minutes)
NEWS_BUFFER_BEFORE = 15
NEWS_BUFFER_AFTER = 15


class MarketFeed:
    """
    📡 Unified Market Data Feed.
    
    Combines:
    - DataCollector: Candles, quotes, news
    - EconomicCalendar: High-impact events
    - SentimentAnalyzer: News sentiment scoring
    """
    
    def __init__(self, env):
        """
        Initialize MarketFeed.
        
        Args:
            env: Cloudflare Worker environment with KV and API keys
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.finnhub_key = str(getattr(env, 'FINNHUB_API_KEY', ''))
        self.gateway = BrokerGateway(env)
    
    # ==========================================
    # 📊 DATA COLLECTOR
    # ==========================================
    
    async def fetch_candles(self, symbol: str, timeframe: str = "1m", limit: int = 100) -> List[Dict]:
        """
        Fetch OHLCV candle data.
        
        Args:
            symbol: Trading pair (e.g., "EURUSD")
            timeframe: Candle timeframe (1m, 5m, 1h, 1d)
            limit: Number of candles
        
        Returns:
            list: [{open, high, low, close, volume, time}, ...]
        """
        cache_key = f"candles:{symbol}:{timeframe}"
        
        # Check cache
        if self.kv:
            cached = await self.kv.get(cache_key)
            if cached:
                return json.loads(cached)
        
        # Map timeframe to standard broker format
        tf_map = {
            "1m": "M1", "5m": "M5", "15m": "M15", "30m": "M30",
            "1h": "H1", "4h": "H4", "1d": "D"
        }
        broker_tf = tf_map.get(timeframe, "M5")

        try:
            candles = await self.gateway.get_market_data(symbol, timeframe=broker_tf, limit=limit)

            if candles:
                # Cache for 1 minute (short lived for market data)
                if self.kv:
                    await self.kv.put(cache_key, json.dumps(candles), expirationTtl=60)
                return candles
        except Exception as e:
            print(f"Broker fetch error: {e}")

        return []
    
    async def fetch_snapshot(self, symbol: str) -> Dict:
        """
        Get real-time price snapshot.
        
        Returns:
            dict: {bid, ask, mid, spread, time}
        """
        cache_key = f"snapshot:{symbol}"
        
        if self.kv:
            cached = await self.kv.get(cache_key)
            if cached:
                return json.loads(cached)
        
        return {"symbol": symbol, "bid": 0, "ask": 0, "mid": 0}
    
    async def fetch_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        Fetch news headlines from Finnhub.
        
        Args:
            symbol: Trading symbol
            limit: Max headlines to return
        
        Returns:
            list: [{headline, summary, sentiment}, ...]
        """
        cache_key = f"news:{symbol}"
        
        if self.kv:
            cached = await self.kv.get(cache_key)
            if cached:
                return json.loads(cached)
        
        try:
            category = "forex" if any(c in symbol for c in ["USD", "EUR", "GBP"]) else "general"
            url = f"https://finnhub.io/api/v1/news?category={category}&token={self.finnhub_key}"
            
            resp = await fetch(url)
            if resp.ok:
                data = json.loads(await resp.text())
                headlines = []
                
                for item in data[:limit]:
                    headline = item.get("headline", "")
                    headlines.append({
                        "headline": headline,
                        "summary": item.get("summary", ""),
                        "sentiment": self._analyze_sentiment(headline)
                    })
                
                # Cache for 15 minutes
                if self.kv:
                    await self.kv.put(cache_key, json.dumps(headlines), expirationTtl=900)
                
                return headlines
        except Exception as e:
            print(f"News fetch error: {e}")
        
        return []
    
    # ==========================================
    # 📅 ECONOMIC CALENDAR
    # ==========================================
    
    async def get_calendar_events(self, days: int = 7) -> List[Dict]:
        """
        Get upcoming economic events.
        
        Args:
            days: Number of days to look ahead
        
        Returns:
            list: [{name, time, currency, impact}, ...]
        """
        cache_key = "economic_calendar"
        
        if self.kv:
            cached = await self.kv.get(cache_key)
            if cached:
                cache_data = json.loads(cached)
                cache_age = time.time() - cache_data.get("timestamp", 0)
                
                if cache_age < 6 * 60 * 60:  # 6 hours
                    return cache_data.get("events", [])
        
        try:
            from_date = time.strftime("%Y-%m-%d")
            to_date = time.strftime("%Y-%m-%d", time.localtime(time.time() + days * 86400))
            
            url = f"https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={self.finnhub_key}"
            
            resp = await fetch(url)
            if resp.ok:
                data = json.loads(await resp.text())
                events = data.get("economicCalendar", [])
                
                high_impact = []
                for event in events:
                    name = event.get("event", "")
                    impact = event.get("impact", "").lower()
                    
                    is_high = impact == "high" or any(
                        hi.lower() in name.lower() for hi in HIGH_IMPACT_EVENTS
                    )
                    
                    if is_high:
                        high_impact.append({
                            "name": name,
                            "time": event.get("time", ""),
                            "currency": event.get("currency", "USD"),
                            "impact": "high"
                        })
                
                # Cache for 6 hours
                if self.kv:
                    await self.kv.put(cache_key, json.dumps({
                        "timestamp": time.time(),
                        "events": high_impact
                    }))
                
                return high_impact
        except Exception as e:
            print(f"Calendar fetch error: {e}")
        
        return []
    
    async def check_news_impact(self, symbol: str) -> Dict:
        """
        Check if trading should be avoided due to news.
        
        Args:
            symbol: Trading pair
        
        Returns:
            dict: {avoid, reason, events}
        """
        events = await self.get_calendar_events()
        affecting = []
        
        for event in events:
            currency = event.get("currency", "USD")
            affected_pairs = CURRENCY_MAP.get(currency, [])
            symbol_clean = symbol.upper().replace("/", "").replace("_", "")
            
            if any(symbol_clean in pair for pair in affected_pairs):
                if self._is_within_news_window(event.get("time", "")):
                    affecting.append(event)
        
        if affecting:
            names = [e.get("name", "")[:30] for e in affecting[:3]]
            return {
                "avoid": True,
                "reason": f"News: {', '.join(names)}",
                "events": affecting
            }
        
        return {"avoid": False, "reason": "", "events": []}
    
    def _is_within_news_window(self, event_time_str: str) -> bool:
        """Check if current time is within news buffer window."""
        try:
            if not event_time_str or ":" not in event_time_str:
                return False
            
            hour, minute = map(int, event_time_str.split(":")[:2])
            now = time.gmtime()
            current_minutes = now.tm_hour * 60 + now.tm_min
            event_minutes = hour * 60 + minute
            
            return abs(current_minutes - event_minutes) <= (NEWS_BUFFER_BEFORE + NEWS_BUFFER_AFTER)
        except:
            return False
    
    # ==========================================
    # 💬 SENTIMENT ANALYZER
    # ==========================================
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """
        Simple sentiment analysis using keyword matching.
        
        For production, use Cloudflare Workers AI or external NLP.
        
        Args:
            text: Text to analyze
        
        Returns:
            dict: {score, label}
        """
        text_lower = text.lower()
        
        bullish_words = [
            "rally", "surge", "gain", "rise", "bull", "up", "higher",
            "strong", "growth", "positive", "record", "jump", "soar"
        ]
        bearish_words = [
            "fall", "drop", "decline", "bear", "down", "lower", "weak",
            "negative", "crash", "plunge", "slump", "loss", "fear"
        ]
        
        bullish_count = sum(1 for word in bullish_words if word in text_lower)
        bearish_count = sum(1 for word in bearish_words if word in text_lower)
        
        total = bullish_count + bearish_count
        if total == 0:
            return {"score": 0.0, "label": "NEUTRAL"}
        
        score = (bullish_count - bearish_count) / total
        
        if score > 0.3:
            label = "BULLISH"
        elif score < -0.3:
            label = "BEARISH"
        else:
            label = "NEUTRAL"
        
        return {"score": round(score, 2), "label": label}
    
    async def get_sentiment_score(self, symbol: str) -> Dict:
        """
        Get aggregated sentiment for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            dict: {score, label, sources}
        """
        news = await self.fetch_news(symbol)
        
        if not news:
            return {"score": 0.0, "label": "NEUTRAL", "sources": 0}
        
        total_score = 0
        for item in news:
            sentiment = item.get("sentiment", {})
            total_score += sentiment.get("score", 0)
        
        avg_score = total_score / len(news)
        
        if avg_score > 0.2:
            label = "BULLISH"
        elif avg_score < -0.2:
            label = "BEARISH"
        else:
            label = "NEUTRAL"
        
        return {
            "score": round(avg_score, 2),
            "label": label,
            "sources": len(news)
        }
    
    # ==========================================
    # 🎯 UNIFIED CONTEXT
    # ==========================================
    
    async def get_market_context(self, symbol: str) -> Dict:
        """
        Get comprehensive market context for AI chatbot.
        
        Combines all data sources into single context object.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            dict: {symbol, news, events, sentiment, impact}
        """
        # Gather all data
        news = await self.fetch_news(symbol)
        events = await self.get_calendar_events()
        sentiment = await self.get_sentiment_score(symbol)
        impact = await self.check_news_impact(symbol)
        
        return {
            "symbol": symbol,
            "timestamp": time.time(),
            "news": news[:3],  # Top 3 headlines
            "upcoming_events": events[:5],  # Next 5 events
            "sentiment": sentiment,
            "news_impact": impact,
            "trading_safe": not impact.get("avoid", False)
        }
