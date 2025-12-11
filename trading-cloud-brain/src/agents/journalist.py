# ========================================
# 📰 AXIOM JOURNALIST AGENT - News Intelligence
# ========================================
# Real-time news filter using Perplexity AI.
# Protects trading decisions from market-moving events.
#
# Capabilities:
#   - Crash Protection (Kill Switch on bad news)
#   - Catalyst Detection (Boost confidence on good news)
#   - Sentiment Analysis (Fear & Greed index)
# ========================================

import json
from typing import Dict, Optional, Any
from js import fetch, Headers
from gemini_adapter import GeminiAdapter


class JournalistAgent:
    """
    The Journalist Agent - AXIOM's real-time news filter.
    
    Uses Perplexity Sonar API for web-scale news intelligence.
    Acts as a "veto gate" before MathAgent executes trades.
    """
    
    def __init__(self, api_key: str, env=None):
        """
        Initialize the Journalist.
        
        Args:
            api_key: Perplexity API key (sonar access)
            env: Worker environment (for Gemini Adapter integration)
        """
        self.name = "JournalistAgent"
        self.api_key = api_key
        self.env = env
        self.api_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar"  # Fast for real-time, use "sonar-pro" for deep research

        # New Gemini Summarizer Integration
        if env:
            self.gemini = GeminiAdapter(env)
            self.kv_key_news = "news_cache"
            self.kv_key_summary = "daily_market_summary"
    
    async def run_cycle(self):
        """
        Executes the daily market summary cycle (Journalist V2):
        1. Fetch raw news from KV (populated by Azure Function).
        2. Summarize using Gemini 1.5 Pro.
        3. Save summary to KV.
        """
        if not self.env:
             return {"status": "error", "message": "Environment not provided to JournalistAgent"}

        try:
            # 1. Fetch News
            kv = getattr(self.env, 'BRAIN_MEMORY', None)
            if not kv:
                return {"status": "error", "message": "KV Binding 'BRAIN_MEMORY' not found"}

            raw_news_json = await kv.get(self.kv_key_news)
            if not raw_news_json:
                return {"status": "skipped", "message": "No news found in cache"}

            raw_news = json.loads(raw_news_json)

            # Extract relevant text from the complex structure
            # Structure from Azure Func: {timestamp, general: [...], specific_summary: {SYM: ...}}
            news_text_buffer = []

            if "general" in raw_news:
                for item in raw_news["general"]:
                    if isinstance(item, dict):
                        headline = item.get("headline", "")
                        summary = item.get("summary", "")
                        news_text_buffer.append(f"- {headline}: {summary}")

            if "specific_summary" in raw_news:
                for sym, content in raw_news["specific_summary"].items():
                    news_text_buffer.append(f"News for {sym}: {str(content)[:200]}...") # Truncate

            full_text = "\n".join(news_text_buffer)

            if not full_text:
                return {"status": "skipped", "message": "News content empty"}

            # 2. Summarize with Gemini
            prompt = f"""
            You are an expert Financial Journalist for the 'Axiom Antigravity' hedge fund.

            Synthesize the following raw market news into a concise, professional daily briefing.
            Focus on actionable insights and market sentiment.

            RAW NEWS:
            {full_text[:5000]}

            FORMAT:
            ## 🌍 Global Market Pulse
            [2-3 sentences]

            ## 🔑 Key Drivers
            - [Bullet point]
            - [Bullet point]

            ## 🎯 Sentiment Score (0-100)
            [Score] - [BULLISH/BEARISH/NEUTRAL]

            ## ⚠️ Risk Radar
            [Identify any major risks]
            """

            result = await self.gemini.generate_content(prompt, model="gemini-1.5-pro")

            if not result["success"]:
                # Fallback to standard gemini-pro if 1.5 fails
                result = await self.gemini.generate_content(prompt, model="gemini-pro")
                if not result["success"]:
                    return {"status": "error", "message": f"AI Generation failed: {result['error']}"}

            summary = result["content"]

            # 3. Save Summary
            payload = {
                "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
                "summary": summary,
                "model_used": "gemini-1.5-pro"
            }
            await kv.put(self.kv_key_summary, json.dumps(payload))

            return {"status": "success", "message": "Daily summary generated"}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def check_breaking_news(self, symbol: str) -> Dict[str, Any]:
        """
        Check for breaking news that could affect a trade.
        
        This is the "Crash Protection" function.
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "SOL", "XAUUSD")
            
        Returns:
            News check result with veto decision
        """
        query = f"""Search for any breaking news about {symbol} in the last 2 hours.
Focus on:
- Regulatory news (SEC, CFTC, lawsuits)
- Exchange issues (hacks, insolvency)
- Major partnership announcements
- Price manipulation allegations

Return a JSON object with:
- has_breaking_news: boolean
- sentiment: "positive" | "negative" | "neutral"
- headline: string (main story if any)
- veto_trade: boolean (true if news is very negative)
- reason: string
"""
        
        result = await self._search(query)
        
        # Parse the response into structured format
        return self._parse_news_response(result, symbol)
    
    async def analyze_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get current market sentiment from social media.
        
        This creates a custom "Fear & Greed" index.
        
        Args:
            symbol: Asset symbol
            
        Returns:
            Sentiment score (0-100) with summary
        """
        query = f"""Analyze current market sentiment for {symbol} based on:
- Twitter/X crypto community
- Reddit (r/cryptocurrency, r/wallstreetbets)
- Discord trading channels

Return a JSON object with:
- sentiment_score: number (0-100, where 100 is extreme greed)
- sentiment_label: "Extreme Fear" | "Fear" | "Neutral" | "Greed" | "Extreme Greed"
- key_topics: list of trending topics
- recommendation: "cautious" | "normal" | "aggressive"
"""
        
        result = await self._search(query)
        return self._parse_sentiment_response(result, symbol)
    
    async def explain_price_move(self, symbol: str, change_percent: float) -> str:
        """
        Explain why a price moved significantly.
        
        Useful for the News Ticker on dashboard.
        
        Args:
            symbol: Asset symbol
            change_percent: Price change (e.g., 5.0 for +5%)
            
        Returns:
            Human-readable explanation
        """
        direction = "pumping" if change_percent > 0 else "dumping"
        query = f"Why is {symbol} {direction} by {abs(change_percent):.1f}% today? Give a brief 1-2 sentence answer."
        
        result = await self._search(query)
        return result.get("content", f"{symbol} moved {change_percent:.1f}% - no specific catalyst found.")
    
    async def _search(self, query: str) -> Dict[str, Any]:
        """
        Execute search using available provider.
        
        Priority:
        1. DuckDuckGo Instant API (FREE, no key needed)
        2. Perplexity API (if key available)
        
        Args:
            query: Search query
            
        Returns:
            Search result content
        """
        # Try DuckDuckGo first (FREE)
        try:
            ddg_result = await self._search_duckduckgo(query)
            if ddg_result.get("content"):
                return ddg_result
        except:
            pass
        
        # Fallback to Perplexity if key available
        if self.api_key:
            return await self._search_perplexity(query)
        
        return {"error": "No search provider available", "content": ""}
    
    async def _search_duckduckgo(self, query: str) -> Dict[str, Any]:
        """
        FREE search using DuckDuckGo Instant Answer API.
        No API key required!
        """
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1"
            
            headers = Headers.new({
                "User-Agent": "AXIOM-Trading-Bot/1.0"
            }.items())
            
            response = await fetch(url, method="GET", headers=headers)
            
            if response.status != 200:
                return {"error": f"DDG error: {response.status}", "content": ""}
            
            data = json.loads(await response.text())
            
            # Extract useful content
            content = ""
            citations = []
            
            # Abstract (main answer)
            if data.get("Abstract"):
                content = data["Abstract"]
                citations.append(data.get("AbstractURL", ""))
            
            # Related topics for more context
            for topic in data.get("RelatedTopics", [])[:3]:
                if isinstance(topic, dict) and topic.get("Text"):
                    content += f"\n- {topic['Text']}"
                    if topic.get("FirstURL"):
                        citations.append(topic["FirstURL"])
            
            # Infobox data
            if data.get("Infobox"):
                for item in data["Infobox"].get("content", [])[:5]:
                    if item.get("label") and item.get("value"):
                        content += f"\n{item['label']}: {item['value']}"
            
            return {
                "content": content or "No instant answer available. Try a more specific query.",
                "citations": citations,
                "source": "duckduckgo"
            }
            
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    async def _search_perplexity(self, query: str) -> Dict[str, Any]:
        """
        Premium search using Perplexity Sonar API.
        Requires API key.
        """
        try:
            payload = json.dumps({
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial news analyst. Always return structured JSON when asked. Be concise."
                    },
                    {
                        "role": "user", 
                        "content": query
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.1  # Low for factual accuracy
            })
            
            headers = Headers.new({
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }.items())
            
            response = await fetch(
                self.api_url,
                method="POST",
                headers=headers,
                body=payload
            )
            
            if response.status != 200:
                return {"error": f"API error: {response.status}", "content": ""}
            
            data = json.loads(await response.text())
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {"content": content, "citations": data.get("citations", [])}
            
        except Exception as e:
            return {"error": str(e), "content": ""}
    
    def _parse_news_response(self, result: Dict, symbol: str) -> Dict[str, Any]:
        """Parse news check response into structured format."""
        content = result.get("content", "")
        
        # Try to extract JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed = json.loads(content)
            return {
                "symbol": symbol,
                "has_breaking_news": parsed.get("has_breaking_news", False),
                "sentiment": parsed.get("sentiment", "neutral"),
                "headline": parsed.get("headline", ""),
                "veto_trade": parsed.get("veto_trade", False),
                "reason": parsed.get("reason", "No significant news"),
                "citations": result.get("citations", [])
            }
        except:
            # Fallback if JSON parsing fails
            return {
                "symbol": symbol,
                "has_breaking_news": False,
                "sentiment": "neutral",
                "headline": content[:100] if content else "",
                "veto_trade": False,
                "reason": "Unable to parse news response",
                "citations": []
            }
    
    def _parse_sentiment_response(self, result: Dict, symbol: str) -> Dict[str, Any]:
        """Parse sentiment response into structured format."""
        content = result.get("content", "")
        
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            parsed = json.loads(content)
            return {
                "symbol": symbol,
                "score": parsed.get("sentiment_score", 50),
                "label": parsed.get("sentiment_label", "Neutral"),
                "topics": parsed.get("key_topics", []),
                "recommendation": parsed.get("recommendation", "normal")
            }
        except:
            return {
                "symbol": symbol,
                "score": 50,
                "label": "Neutral",
                "topics": [],
                "recommendation": "normal"
            }

    async def run_mission(self, env):
        """
        Execute the Journalist's 15-minute mission.
        
        1. Scan news for major watchlist assets (BTC, ETH, SOL)
        2. Analyze sentiment
        3. Broadcast alerts via Ably if significant
        """
        watchlist = ["BTC", "ETH", "SOL", "XAU"]
        alerts = []
        
        print(f"📰 Journalist Mission Started: Scanning {watchlist}")
        
        for symbol in watchlist:
            # 1. Check breaking news
            news = await self.check_breaking_news(symbol)
            
            if news.get("has_breaking_news") or news.get("veto_trade"):
                alert = {
                    "type": "NEWS_ALERT",
                    "symbol": symbol,
                    "headline": news.get("headline"),
                    "sentiment": news.get("sentiment"),
                    "action": "VETO_TRADES" if news.get("veto_trade") else "INFO"
                }
                alerts.append(alert)
                
            # 2. Check sentiment (Fear & Greed)
            sentiment = await self.analyze_sentiment(symbol)
            if sentiment.get("label") in ["Extreme Fear", "Extreme Greed"]:
                alert = {
                    "type": "SENTIMENT_ALERT",
                    "symbol": symbol,
                    "score": sentiment.get("score"),
                    "label": sentiment.get("label"),
                    "recommendation": sentiment.get("recommendation")
                }
                alerts.append(alert)
        
        # 3. Broadcast to Ably (if alerts exist)
        if alerts:
            # We need to import publish_to_ably here or pass it in
            # Assuming worker.py handles the actual broadcast if we return alerts
            # Or we can do it here if we had the Ably key.
            # Best practice: Return findings, let worker.py orchestrate.
            print(f"📰 Found {len(alerts)} alerts.")
            return alerts
            
        print("📰 Mission Complete: No significant alerts.")
        return []


# ========================================
# 🏭 Factory Function
# ========================================

def get_journalist_agent(api_key: str) -> JournalistAgent:
    """Get JournalistAgent instance."""
    return JournalistAgent(api_key)


# ========================================
# 🔌 Integration with Signal Synthesis
# ========================================

async def news_filter_gate(env, symbol: str, signal_direction: str) -> Dict[str, Any]:
    """
    News filter gate - call before executing any trade.
    
    This is the integration point with worker.py signal synthesis.
    
    Args:
        env: Worker environment with PERPLEXITY_API_KEY
        symbol: Trading symbol
        signal_direction: "BUY", "SELL", "STRONG_BUY", etc.
        
    Returns:
        Gate decision with news context
    """
    api_key = str(getattr(env, 'PERPLEXITY_API_KEY', ''))
    
    if not api_key:
        # No API key = skip news filter (allow trade)
        return {
            "allowed": True,
            "reason": "News filter disabled (no API key)",
            "news": None
        }
    
    journalist = get_journalist_agent(api_key)
    
    # Check for breaking news
    news = await journalist.check_breaking_news(symbol)
    
    # Decision logic
    if news.get("veto_trade"):
        return {
            "allowed": False,
            "reason": f"🛑 VETOED: {news.get('headline', 'Negative news detected')}",
            "news": news
        }
    
    # Boost confidence for positive catalyst
    if news.get("sentiment") == "positive" and news.get("has_breaking_news"):
        return {
            "allowed": True,
            "boost_confidence": 0.1,  # +10% confidence
            "reason": f"🚀 CATALYST: {news.get('headline', 'Positive news')}",
            "news": news
        }
    
    # Normal flow
    return {
        "allowed": True,
        "reason": "✅ No significant news detected",
        "news": news
    }
