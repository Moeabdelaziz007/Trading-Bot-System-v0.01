"""
============================================
🤖 AI COUNCIL - Multi-Model Intelligence Hub
============================================

Integrates 4 AI models for institutional-grade trading analysis:
1. Groq (Llama 3.1) - Fast market sentiment analysis
2. Perplexity - Real-time news and events
3. Gemini - Pattern recognition and trends
4. DeepSeek (via OpenRouter) - Deep quantitative analysis

Author: AlphaAxiom Team
Version: 1.0.0
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================
# AI CONFIGURATION
# ============================================

class AIConfig:
    """AI Model Configuration"""
    
    # Groq (Free tier - 6000 tokens/min)
    GROQ_API_KEY = ""  # Set via environment
    GROQ_MODEL = "llama-3.1-70b-versatile"
    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # Perplexity (Free tier available)
    PERPLEXITY_API_KEY = ""  # Set via environment
    PERPLEXITY_URL = "https://api.perplexity.ai/chat/completions"
    PERPLEXITY_MODEL = "llama-3.1-sonar-small-128k-online"
    
    # Gemini (Free tier - 15 RPM)
    GEMINI_API_KEY = ""  # Set via environment
    GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    # DeepSeek via OpenRouter (Free tier)
    OPENROUTER_API_KEY = ""  # Set via environment
    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEEPSEEK_MODEL = "deepseek/deepseek-chat"


# ============================================
# GROQ ANALYST - Fast Market Sentiment
# ============================================

class GroqAnalyst:
    """
    Groq-powered fast market sentiment analysis.
    Uses Llama 3.1 70B for quick responses.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or AIConfig.GROQ_API_KEY
        self.enabled = bool(self.api_key)
    
    async def analyze_sentiment(
        self,
        symbol: str,
        price: float,
        indicators: Dict
    ) -> Dict:
        """Analyze market sentiment using Groq."""
        if not self.enabled:
            logger.warning("Groq API key not set")
            return {"sentiment": "NEUTRAL", "confidence": 50, "reasoning": "API not configured"}
        
        prompt = f"""You are an institutional trading analyst. Analyze this market data and provide a trading recommendation.

Symbol: {symbol}
Current Price: {price}
Indicators:
- WaveTrend WT1: {indicators.get('wt1', 'N/A')}
- WaveTrend WT2: {indicators.get('wt2', 'N/A')}
- Money Flow: {indicators.get('money_flow', 'N/A')}
- VWAP: {indicators.get('vwap', 'N/A')}

Respond in JSON format only:
{{"sentiment": "BULLISH/BEARISH/NEUTRAL", "confidence": 0-100, "reasoning": "brief explanation", "action": "BUY/SELL/HOLD"}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    AIConfig.GROQ_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": AIConfig.GROQ_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 200
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        # Parse JSON from response
                        result = json.loads(content)
                        logger.info(f"🤖 Groq: {symbol} = {result.get('sentiment')} ({result.get('confidence')}%)")
                        return result
                    else:
                        logger.error(f"Groq API error: {response.status}")
                        return {"sentiment": "NEUTRAL", "confidence": 50, "reasoning": "API error"}
                        
        except Exception as e:
            logger.error(f"Groq analysis failed: {e}")
            return {"sentiment": "NEUTRAL", "confidence": 50, "reasoning": str(e)}


# ============================================
# PERPLEXITY NEWS - Real-time News Filter
# ============================================

class PerplexityNews:
    """
    Perplexity-powered real-time news analysis.
    Checks for market-moving events.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or AIConfig.PERPLEXITY_API_KEY
        self.enabled = bool(self.api_key)
    
    async def check_news_risk(self, symbol: str) -> Dict:
        """Check for high-impact news that could affect the symbol."""
        if not self.enabled:
            logger.warning("Perplexity API key not set")
            return {"risk_level": "LOW", "has_news": False, "events": []}
        
        # Convert symbol for news search
        currency_map = {
            "EURUSD": "EUR/USD Euro Dollar",
            "GBPUSD": "GBP/USD British Pound",
            "USDJPY": "USD/JPY Japanese Yen",
            "XAUUSD": "Gold XAU/USD"
        }
        search_term = currency_map.get(symbol, symbol)
        
        prompt = f"""Search for any major financial news or economic events TODAY that could impact {search_term} forex trading.

Focus on:
- Central bank announcements (Fed, ECB, BOE, BOJ)
- Economic data releases (NFP, CPI, GDP)
- Geopolitical events
- Major market moves

Respond in JSON format only:
{{"risk_level": "HIGH/MEDIUM/LOW", "has_news": true/false, "events": ["event1", "event2"], "recommendation": "TRADE/AVOID/CAUTION"}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    AIConfig.PERPLEXITY_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": AIConfig.PERPLEXITY_MODEL,
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        result = json.loads(content)
                        logger.info(f"📰 Perplexity: {symbol} News Risk = {result.get('risk_level')}")
                        return result
                    else:
                        logger.error(f"Perplexity API error: {response.status}")
                        return {"risk_level": "LOW", "has_news": False, "events": []}
                        
        except Exception as e:
            logger.error(f"Perplexity news check failed: {e}")
            return {"risk_level": "LOW", "has_news": False, "events": []}


# ============================================
# GEMINI PATTERNS - Pattern Recognition
# ============================================

class GeminiPatterns:
    """
    Gemini-powered pattern recognition and trend analysis.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or AIConfig.GEMINI_API_KEY
        self.enabled = bool(self.api_key)
    
    async def analyze_patterns(
        self,
        symbol: str,
        recent_prices: List[float]
    ) -> Dict:
        """Analyze price patterns using Gemini."""
        if not self.enabled:
            logger.warning("Gemini API key not set")
            return {"pattern": "NONE", "trend": "NEUTRAL", "strength": 50}
        
        # Calculate basic metrics
        if len(recent_prices) < 10:
            return {"pattern": "INSUFFICIENT_DATA", "trend": "NEUTRAL", "strength": 0}
        
        price_changes = [
            round((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] * 100, 4)
            for i in range(1, min(20, len(recent_prices)))
        ]
        
        prompt = f"""You are a technical analysis expert. Analyze this price data for {symbol}:

Last 20 price changes (%): {price_changes}
Current price: {recent_prices[-1]}
Highest (20 bars): {max(recent_prices[-20:])}
Lowest (20 bars): {min(recent_prices[-20:])}

Identify any chart patterns and trend direction.

Respond in JSON format only:
{{"pattern": "DOUBLE_BOTTOM/HEAD_SHOULDERS/TRIANGLE/CHANNEL/NONE", "trend": "BULLISH/BEARISH/NEUTRAL", "strength": 0-100, "description": "brief explanation"}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{AIConfig.GEMINI_URL}?key={self.api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 200}
                    },
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["candidates"][0]["content"]["parts"][0]["text"]
                        # Extract JSON from response
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end > start:
                            result = json.loads(content[start:end])
                            logger.info(f"🔮 Gemini: {symbol} Pattern = {result.get('pattern')}")
                            return result
                    logger.error(f"Gemini API error: {response.status}")
                    return {"pattern": "NONE", "trend": "NEUTRAL", "strength": 50}
                        
        except Exception as e:
            logger.error(f"Gemini pattern analysis failed: {e}")
            return {"pattern": "NONE", "trend": "NEUTRAL", "strength": 50}


# ============================================
# DEEPSEEK QUANT - Deep Quantitative Analysis
# ============================================

class DeepSeekQuant:
    """
    DeepSeek-powered deep quantitative analysis via OpenRouter.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or AIConfig.OPENROUTER_API_KEY
        self.enabled = bool(self.api_key)
    
    async def deep_analysis(
        self,
        symbol: str,
        indicators: Dict,
        cipher_score: int
    ) -> Dict:
        """Perform deep quantitative analysis."""
        if not self.enabled:
            logger.warning("OpenRouter API key not set")
            return {"recommendation": "HOLD", "confidence": 50, "risk_score": 50}
        
        prompt = f"""You are a quantitative trading analyst at a hedge fund. Analyze this trade setup:

Symbol: {symbol}
Current Cipher Score: {cipher_score}/100

Technical Indicators:
- WaveTrend: WT1={indicators.get('wt1')}, WT2={indicators.get('wt2')}
- Money Flow: {indicators.get('money_flow')}
- VWAP Distance: {indicators.get('price', 0) - indicators.get('vwap', 0):.5f}

Based on institutional trading principles (VuManChu Cipher B strategy), provide your analysis.

Respond in JSON format only:
{{"recommendation": "STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL", "confidence": 0-100, "risk_score": 0-100, "edge": "description of trading edge", "position_size_modifier": 0.5-1.5}}"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    AIConfig.OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://axiomid.app",
                        "X-Title": "AlphaAxiom Trading Brain"
                    },
                    json={
                        "model": AIConfig.DEEPSEEK_MODEL,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 300
                    },
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        # Extract JSON
                        start = content.find('{')
                        end = content.rfind('}') + 1
                        if start != -1 and end > start:
                            result = json.loads(content[start:end])
                            logger.info(f"🧠 DeepSeek: {symbol} = {result.get('recommendation')} ({result.get('confidence')}%)")
                            return result
                    logger.error(f"OpenRouter API error: {response.status}")
                    return {"recommendation": "HOLD", "confidence": 50, "risk_score": 50}
                        
        except Exception as e:
            logger.error(f"DeepSeek analysis failed: {e}")
            return {"recommendation": "HOLD", "confidence": 50, "risk_score": 50}


# ============================================
# AI COUNCIL - Unified Decision Making
# ============================================

class AICouncil:
    """
    AI Council - Combines all AI models for consensus trading decisions.
    
    Decision process:
    1. Groq analyzes sentiment
    2. Perplexity checks news risk
    3. Gemini identifies patterns
    4. DeepSeek provides deep analysis
    5. Council votes on final decision
    """
    
    def __init__(self):
        self.groq = GroqAnalyst()
        self.perplexity = PerplexityNews()
        self.gemini = GeminiPatterns()
        self.deepseek = DeepSeekQuant()
        
        # Track which models are enabled
        self.enabled_models = []
        if self.groq.enabled:
            self.enabled_models.append("Groq")
        if self.perplexity.enabled:
            self.enabled_models.append("Perplexity")
        if self.gemini.enabled:
            self.enabled_models.append("Gemini")
        if self.deepseek.enabled:
            self.enabled_models.append("DeepSeek")
        
        logger.info(f"🤖 AI Council initialized: {self.enabled_models or 'No API keys configured'}")
    
    async def consult(
        self,
        symbol: str,
        price: float,
        indicators: Dict,
        cipher_score: int,
        recent_prices: List[float]
    ) -> Dict:
        """
        Consult all AI models and reach consensus.
        
        Returns adjusted confidence and final recommendation.
        """
        if not self.enabled_models:
            logger.warning("No AI models enabled - using cipher score only")
            return {
                "ai_adjusted_score": cipher_score,
                "consensus": "NONE",
                "ai_confidence": 0,
                "news_risk": "UNKNOWN",
                "models_consulted": []
            }
        
        # Run all analyses in parallel
        tasks = [
            self.groq.analyze_sentiment(symbol, price, indicators),
            self.perplexity.check_news_risk(symbol),
            self.gemini.analyze_patterns(symbol, recent_prices),
            self.deepseek.deep_analysis(symbol, indicators, cipher_score)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        groq_result = results[0] if not isinstance(results[0], Exception) else {}
        perplexity_result = results[1] if not isinstance(results[1], Exception) else {}
        gemini_result = results[2] if not isinstance(results[2], Exception) else {}
        deepseek_result = results[3] if not isinstance(results[3], Exception) else {}
        
        # Calculate consensus
        votes = {"BUY": 0, "SELL": 0, "HOLD": 0}
        confidence_sum = 0
        confidence_count = 0
        
        # Groq vote
        if groq_result.get("action") in votes:
            votes[groq_result["action"]] += 1
            confidence_sum += groq_result.get("confidence", 50)
            confidence_count += 1
        
        # DeepSeek vote
        rec = deepseek_result.get("recommendation", "HOLD")
        if "BUY" in rec:
            votes["BUY"] += 1
        elif "SELL" in rec:
            votes["SELL"] += 1
        else:
            votes["HOLD"] += 1
        confidence_sum += deepseek_result.get("confidence", 50)
        confidence_count += 1
        
        # Gemini trend vote
        trend = gemini_result.get("trend", "NEUTRAL")
        if trend == "BULLISH":
            votes["BUY"] += 0.5
        elif trend == "BEARISH":
            votes["SELL"] += 0.5
        
        # Determine consensus
        max_votes = max(votes.values())
        consensus = max(votes, key=votes.get) if max_votes > 1 else "HOLD"
        
        # News risk adjustment
        news_risk = perplexity_result.get("risk_level", "LOW")
        news_modifier = 1.0
        if news_risk == "HIGH":
            news_modifier = 0.5  # Halve confidence if high-risk news
            consensus = "HOLD"  # Don't trade during high-risk news
        elif news_risk == "MEDIUM":
            news_modifier = 0.8
        
        # Calculate adjusted score
        ai_confidence = (confidence_sum / confidence_count) if confidence_count > 0 else 50
        ai_adjusted_score = int(cipher_score * 0.6 + ai_confidence * 0.4 * news_modifier)
        
        result = {
            "ai_adjusted_score": ai_adjusted_score,
            "original_cipher_score": cipher_score,
            "consensus": consensus,
            "ai_confidence": round(ai_confidence, 1),
            "news_risk": news_risk,
            "votes": votes,
            "models_consulted": self.enabled_models,
            "details": {
                "groq": groq_result,
                "perplexity": perplexity_result,
                "gemini": gemini_result,
                "deepseek": deepseek_result
            }
        }
        
        logger.info(f"🏛️ AI Council for {symbol}: {consensus} (Score: {cipher_score}→{ai_adjusted_score})")
        
        return result


# ============================================
# TEST
# ============================================

async def test_council():
    """Test the AI Council."""
    import os
    
    # Set API keys from environment
    AIConfig.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    AIConfig.PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
    AIConfig.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    AIConfig.OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    
    council = AICouncil()
    
    # Test data
    result = await council.consult(
        symbol="EURUSD",
        price=1.0520,
        indicators={"wt1": -65, "wt2": -60, "money_flow": 120, "vwap": 1.0515},
        cipher_score=75,
        recent_prices=[1.0500, 1.0505, 1.0510, 1.0515, 1.0520] * 10
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(test_council())
