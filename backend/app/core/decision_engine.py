# backend/app/core/decision_engine.py
# ==============================================
# AI DECISION BRIDGE - "The Brain"
# Multi-Model Intelligence + Technical Synthesis
# ==============================================

import os
import json
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Rate limiting
from typing import Dict, Deque
from collections import deque
import threading

# Modern Google GenAI SDK
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-genai SDK not available. Using fallback mode.")

# Perplexity API
try:
    import httpx
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PERPLEXITY_AVAILABLE = False
    print("[WARN] httpx not available for Perplexity integration.")

# Import BigQuery sink from trading-cloud-brain
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../trading-cloud-brain/src'))
    from data.bq_sink import get_data_sink
    BIGQUERY_AVAILABLE = True
except ImportError:
    BIGQUERY_AVAILABLE = False
    print("[WARN] BigQuery sink not available. Using local logging.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradingSignal(Enum):
    """Trading signal enumeration."""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    NO_TRADE = "NO_TRADE"


@dataclass
class MarketAnalysis:
    """Market analysis data structure."""
    symbol: str
    timestamp: str
    technical_score: float  # AEXI score (0-100)
    ai_sentiment: str  # POSITIVE/NEGATIVE/NEUTRAL
    ai_confidence: float  # 0.0-1.0
    macro_context: str
    news_sentiment: str
    grounding_sources: List[str]
    final_signal: TradingSignal
    reasoning: str
    execution_metadata: Dict[str, Any]


class TokenBucketRateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, rate_per_minute: int = 10, burst_limit: int = 5):
        self.rate_per_minute = rate_per_minute
        self.burst_limit = burst_limit
        self.tokens = burst_limit
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token for API call."""
        with self.lock:
            now = time.time()
            # Refill tokens based on rate
            time_passed = now - self.last_refill
            tokens_to_add = int(time_passed * (self.rate_per_minute / 60))
            self.tokens = min(self.burst_limit, self.tokens + tokens_to_add)
            self.last_refill = now
            
            if self.tokens > 0:
                self.tokens -= 1
                return True
            return False
    
    async def wait_for_token(self) -> None:
        """Wait for a token to become available."""
        while not await self.acquire():
            await asyncio.sleep(6)  # Wait 6 seconds between attempts


class CircuitBreaker:
    """Circuit breaker for API fault tolerance."""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution."""
        with self.lock:
            if self.state == "CLOSED":
                return True
            elif self.state == "OPEN":
                if time.time() - self.last_failure_time > self.timeout:
                    self.state = "HALF_OPEN"
                    return True
                return False
            elif self.state == "HALF_OPEN":
                return True
        return False
    
    def record_success(self) -> None:
        """Record successful execution."""
        with self.lock:
            self.failure_count = 0
            self.state = "CLOSED"
    
    def record_failure(self) -> None:
        """Record failed execution."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"


class MarketIntelligence:
    """
    Multi-Model Intelligence System:
    - Gemini 1.5 Pro: Strategic macro analysis with Google Search grounding
    - Perplexity: Tactical news sentiment verification
    """
    
    def __init__(self):
        self.gemini_client = None
        self.perplexity_client = None
        
        # Rate limiters
        self.gemini_rate_limiter = TokenBucketRateLimiter(rate_per_minute=15, burst_limit=3)
        self.perplexity_rate_limiter = TokenBucketRateLimiter(rate_per_minute=20, burst_limit=5)
        
        # Circuit breakers
        self.gemini_circuit = CircuitBreaker(failure_threshold=3, timeout=120)
        self.perplexity_circuit = CircuitBreaker(failure_threshold=3, timeout=120)
        
        # Initialize clients
        self._init_clients()
    
    def _init_clients(self) -> None:
        """Initialize API clients."""
        # Initialize Gemini client
        if GEMINI_AVAILABLE:
            gemini_key = os.getenv("GEMINI_API_KEY")
            if gemini_key:
                self.gemini_client = genai.Client(api_key=gemini_key)
                logger.info("✅ Gemini 1.5 Pro: ONLINE")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not found")
        
        # Initialize Perplexity client
        if PERPLEXITY_AVAILABLE:
            perplexity_key = os.getenv("PERPLEXITY_API_KEY")
            if perplexity_key:
                self.perplexity_client = httpx.AsyncClient(
                    base_url="https://api.perplexity.ai",
                    headers={"Authorization": f"Bearer {perplexity_key}"},
                    timeout=30.0
                )
                logger.info("✅ Perplexity: ONLINE")
            else:
                logger.warning("⚠️ PERPLEXITY_API_KEY not found")
    
    async def analyze_macro_context(self, symbol: str) -> Dict[str, Any]:
        """
        Analyze macro context using Gemini 1.5 Pro with Google Search grounding.
        
        Returns:
            Dict containing sentiment, confidence, and grounding sources
        """
        if not self.gemini_client or not self.gemini_circuit.can_execute():
            return self._fallback_macro_analysis(symbol)
        
        try:
            await self.gemini_rate_limiter.wait_for_token()
            
            prompt = f"""
            As a senior quantitative analyst, analyze the macro context for {symbol}.
            
            Use Google Search to find recent news, earnings, market sentiment, and economic indicators.
            Focus on the next 24-48 hours trading outlook.
            
            Provide analysis in JSON format:
            {{
                "sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL",
                "confidence": 0.0-1.0,
                "key_factors": ["list", "of", "factors"],
                "risk_factors": ["list", "of", "risks"],
                "macro_outlook": "Brief outlook description"
            }}
            
            Ensure all analysis is grounded in real, current information.
            """
            
            response = self.gemini_client.models.generate_content(
                model="gemini-1.5-pro",
                contents=prompt,
                config={
                    "tools": [{"google_search": {}}]
                }
            )
            
            # Extract grounding metadata
            grounding_metadata = getattr(response.candidates[0], 'grounding_metadata', {})
            search_queries = getattr(grounding_metadata, 'web_search_queries', [])
            grounding_chunks = getattr(grounding_metadata, 'grounding_chunks', [])
            
            # Parse JSON response
            try:
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                analysis = {
                    "sentiment": "NEUTRAL",
                    "confidence": 0.5,
                    "key_factors": ["Parsing error - using fallback"],
                    "risk_factors": [],
                    "macro_outlook": "Unable to parse response"
                }
            
            analysis['grounding_sources'] = [
                chunk.web.title if hasattr(chunk, 'web') and hasattr(chunk.web, 'title') else str(chunk)
                for chunk in grounding_chunks
            ]
            analysis['search_queries'] = search_queries
            
            self.gemini_circuit.record_success()
            logger.info(f"✅ Gemini analysis complete for {symbol}: {analysis['sentiment']} ({analysis['confidence']:.2f})")
            
            return analysis
            
        except Exception as e:
            self.gemini_circuit.record_failure()
            logger.error(f"❌ Gemini API error for {symbol}: {e}")
            return self._fallback_macro_analysis(symbol)
    
    async def verify_news_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Verify news sentiment using Perplexity sonar-medium-online model.
        
        Returns:
            Dict containing sentiment verification and confidence
        """
        if not self.perplexity_client or not self.perplexity_circuit.can_execute():
            return self._fallback_sentiment_verification(symbol)
        
        try:
            await self.perplexity_rate_limiter.wait_for_token()
            
            prompt = f"""
            Analyze recent news and sentiment for {symbol}.
            Focus on factual news reporting and avoid speculation.
            
            Provide response in JSON format:
            {{
                "sentiment": "POSITIVE" or "NEGATIVE" or "NEUTRAL",
                "confidence": 0.0-1.0,
                "news_summary": "Brief factual summary",
                "credibility_score": 0.0-1.0,
                "verification_notes": "Notes on source credibility"
            }}
            """
            
            response = await self.perplexity_client.post(
                "/chat/completions",
                json={
                    "model": "sonar-medium-online",
                    "messages": [{"role": "user", "content": prompt}],
                    "return_citations": True,
                    "return_images": False,
                    "return_related_questions": False
                }
            )
            
            result = response.json()
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            try:
                verification = json.loads(content)
            except json.JSONDecodeError:
                verification = {
                    "sentiment": "NEUTRAL",
                    "confidence": 0.5,
                    "news_summary": "Parsing error - using fallback",
                    "credibility_score": 0.5,
                    "verification_notes": "Unable to parse verification response"
                }
            
            self.perplexity_circuit.record_success()
            logger.info(f"✅ Perplexity verification complete for {symbol}: {verification['sentiment']} ({verification['confidence']:.2f})")
            
            return verification
            
        except Exception as e:
            self.perplexity_circuit.record_failure()
            logger.error(f"❌ Perplexity API error for {symbol}: {e}")
            return self._fallback_sentiment_verification(symbol)
    
    def _fallback_macro_analysis(self, symbol: str) -> Dict[str, Any]:
        """Fallback macro analysis when API is unavailable."""
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.5,
            "key_factors": ["API unavailable - using conservative approach"],
            "risk_factors": ["Increased uncertainty due to API failure"],
            "macro_outlook": "Neutral outlook due to API limitations",
            "grounding_sources": [],
            "search_queries": [],
            "fallback": True
        }
    
    def _fallback_sentiment_verification(self, symbol: str) -> Dict[str, Any]:
        """Fallback sentiment verification when API is unavailable."""
        return {
            "sentiment": "NEUTRAL",
            "confidence": 0.5,
            "news_summary": "API unavailable - no recent news analysis",
            "credibility_score": 0.5,
            "verification_notes": "Unable to verify due to API unavailability",
            "fallback": True
        }


def synthesize_signal(technical_score: float, ai_sentiment: str, ai_confidence: float = 0.0) -> Dict[str, Any]:
    """
    Synthesis logic combining technical analysis (AEXI) with AI sentiment.
    
    Logic:
    - If Technical Score (AEXI) > 80 AND AI Sentiment is "POSITIVE" -> STRONG BUY
    - If Technical > 80 BUT AI is "NEGATIVE" -> HOLD (Divergence Detected)
    - If AI Confidence < 0.7 -> NO TRADE
    
    Args:
        technical_score: AEXI score (0-100)
        ai_sentiment: POSITIVE/NEGATIVE/NEUTRAL
        ai_confidence: AI confidence level (0.0-1.0)
    
    Returns:
        Dict with final signal and reasoning
    """
    
    # Decision tree logic
    if ai_confidence < 0.7:
        final_signal = TradingSignal.NO_TRADE
        reasoning = f"Low AI confidence ({ai_confidence:.2f}) - insufficient conviction"
    
    elif technical_score > 80 and ai_sentiment == "POSITIVE":
        final_signal = TradingSignal.STRONG_BUY
        reasoning = f"Strong technical setup (AEXI: {technical_score:.1f}) + Positive AI sentiment"
    
    elif technical_score > 80 and ai_sentiment == "NEGATIVE":
        final_signal = TradingSignal.HOLD
        reasoning = f"Strong technical (AEXI: {technical_score:.1f}) but negative AI sentiment - divergence detected"
    
    elif technical_score < 20 and ai_sentiment == "NEGATIVE":
        final_signal = TradingSignal.STRONG_SELL
        reasoning = f"Weak technical setup (AEXI: {technical_score:.1f}) + Negative AI sentiment"
    
    elif technical_score < 20 and ai_sentiment == "POSITIVE":
        final_signal = TradingSignal.HOLD
        reasoning = f"Weak technical (AEXI: {technical_score:.1f}) but positive AI sentiment - divergence detected"
    
    elif ai_sentiment == "POSITIVE":
        final_signal = TradingSignal.BUY
        reasoning = f"Positive AI sentiment with moderate technicals (AEXI: {technical_score:.1f})"
    
    elif ai_sentiment == "NEGATIVE":
        final_signal = TradingSignal.SELL
        reasoning = f"Negative AI sentiment with moderate technicals (AEXI: {technical_score:.1f})"
    
    else:
        final_signal = TradingSignal.HOLD
        reasoning = f"Neutral signals across technical (AEXI: {technical_score:.1f}) and AI analysis"
    
    return {
        "signal": final_signal.value,
        "reasoning": reasoning,
        "technical_score": technical_score,
        "ai_sentiment": ai_sentiment,
        "ai_confidence": ai_confidence
    }


class DecisionEngine:
    """
    AI Decision Bridge - The Brain
    Orchestrates multi-model intelligence and technical synthesis.
    """
    
    def __init__(self):
        self.market_intelligence = MarketIntelligence()
        self.data_sink = None
        
        # Initialize BigQuery sink if available
        if BIGQUERY_AVAILABLE:
            try:
                self.data_sink = get_data_sink()
                logger.info("✅ BigQuery audit trail: ONLINE")
            except Exception as e:
                logger.warning(f"⚠️ BigQuery sink init failed: {e}")
                self.data_sink = None
    
    async def make_decision(
        self,
        symbol: str,
        technical_score: float,
        timeout_seconds: float = 5.0
    ) -> MarketAnalysis:
        """
        Make trading decision by combining technical and AI analysis.
        
        Args:
            symbol: Trading symbol (e.g., "BTC/USD", "TSLA")
            technical_score: AEXI technical score (0-100)
            timeout_seconds: Maximum time to wait for AI analysis
        
        Returns:
            MarketAnalysis object with complete decision data
        """
        
        start_time = time.time()
        timestamp = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"🧠 DECISION ENGINE: Analyzing {symbol} (Technical: {technical_score:.1f})")
        
        # Run AI analysis concurrently with timeout protection
        try:
            gemini_task = asyncio.wait_for(
                self.market_intelligence.analyze_macro_context(symbol),
                timeout=timeout_seconds
            )
            perplexity_task = asyncio.wait_for(
                self.market_intelligence.verify_news_sentiment(symbol),
                timeout=timeout_seconds
            )
            
            # Wait for both analyses with timeout
            done, pending = await asyncio.wait(
                [gemini_task, perplexity_task],
                timeout=timeout_seconds,
                return_when=asyncio.FIRST_EXCEPTION
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
            
            # Collect results
            gemini_result = {}
            perplexity_result = {}
            
            for task in done:
                try:
                    result = await task
                    if "search_queries" in result:  # Gemini result
                        gemini_result = result
                    else:  # Perplexity result
                        perplexity_result = result
                except Exception as e:
                    logger.error(f"Task failed: {e}")
        
        except asyncio.TimeoutError:
            logger.warning(f"⏰ TIMEOUT: AI analysis exceeded {timeout_seconds}s for {symbol}")
            # Use fallback responses
            gemini_result = self.market_intelligence._fallback_macro_analysis(symbol)
            perplexity_result = self.market_intelligence._fallback_sentiment_verification(symbol)
        
        # Synthesize signals
        ai_sentiment = gemini_result.get("sentiment", "NEUTRAL")
        ai_confidence = min(
            gemini_result.get("confidence", 0.5),
            perplexity_result.get("confidence", 0.5)
        )
        
        synthesis_result = synthesize_signal(technical_score, ai_sentiment, ai_confidence)
        
        # Create final analysis object
        analysis = MarketAnalysis(
            symbol=symbol,
            timestamp=timestamp,
            technical_score=technical_score,
            ai_sentiment=ai_sentiment,
            ai_confidence=ai_confidence,
            macro_context=gemini_result.get("macro_outlook", "No context available"),
            news_sentiment=perplexity_result.get("news_summary", "No news analysis"),
            grounding_sources=gemini_result.get("grounding_sources", []),
            final_signal=TradingSignal(synthesis_result["signal"]),
            reasoning=synthesis_result["reasoning"],
            execution_metadata={
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "gemini_available": self.market_intelligence.gemini_client is not None,
                "perplexity_available": self.market_intelligence.perplexity_client is not None,
                "bigquery_available": self.data_sink is not None,
                "timeout_used": timeout_seconds,
                "circuit_breaker_gemini": self.market_intelligence.gemini_circuit.state,
                "circuit_breaker_perplexity": self.market_intelligence.perplexity_circuit.state
            }
        )
        
        # Log to BigQuery audit trail
        await self._log_decision_to_bigquery(analysis)
        
        logger.info(f"✅ DECISION: {symbol} -> {analysis.final_signal.value} ({analysis.execution_metadata['processing_time_ms']}ms)")
        
        return analysis
    
    async def _log_decision_to_bigquery(self, analysis: MarketAnalysis) -> None:
        """Log decision to BigQuery audit trail."""
        if not self.data_sink:
            logger.debug("BigQuery sink not available - skipping audit log")
            return
        
        try:
            # Format for BigQuery app_logs schema
            log_entry = {
                "timestamp": analysis.timestamp,
                "level": "INFO",
                "event": "AI_DECISION",
                "module": "decision_engine",
                "context": {
                    "symbol": analysis.symbol,
                    "technical_score": analysis.technical_score,
                    "ai_sentiment": analysis.ai_sentiment,
                    "ai_confidence": analysis.ai_confidence,
                    "final_signal": analysis.final_signal.value,
                    "reasoning": analysis.reasoning,
                    "macro_context": analysis.macro_context,
                    "news_sentiment": analysis.news_sentiment,
                    "grounding_sources": analysis.grounding_sources,
                    "execution_metadata": analysis.execution_metadata
                }
            }
            
            self.data_sink.log(log_entry)
            await asyncio.get_event_loop().run_in_executor(None, self.data_sink.flush)
            
        except Exception as e:
            logger.error(f"❌ Failed to log to BigQuery: {e}")
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get decision engine status and health metrics."""
        return {
            "engine": "ONLINE",
            "gemini": {
                "available": self.market_intelligence.gemini_client is not None,
                "circuit_breaker": self.market_intelligence.gemini_circuit.state,
                "rate_limiter": "ACTIVE"
            },
            "perplexity": {
                "available": self.market_intelligence.perplexity_client is not None,
                "circuit_breaker": self.market_intelligence.perplexity_circuit.state,
                "rate_limiter": "ACTIVE"
            },
            "bigquery": {
                "available": self.data_sink is not None,
                "sink_type": type(self.data_sink).__name__ if self.data_sink else "None"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global instance
decision_engine = DecisionEngine()


# Convenience functions for easy integration
async def analyze_market(symbol: str, technical_score: float) -> MarketAnalysis:
    """
    Convenience function for market analysis.
    
    Args:
        symbol: Trading symbol
        technical_score: AEXI technical score (0-100)
    
    Returns:
        MarketAnalysis object
    """
    return await decision_engine.make_decision(symbol, technical_score)


async def get_trading_signal(symbol: str, technical_score: float) -> str:
    """
    Convenience function for getting trading signal.
    
    Args:
        symbol: Trading symbol
        technical_score: AEXI technical score (0-100)
    
    Returns:
        Trading signal as string
    """
    analysis = await analyze_market(symbol, technical_score)
    return analysis.final_signal.value


if __name__ == "__main__":
    # Example usage
    async def main():
        print("🚀 AI Decision Bridge - Test Run")
        
        # Get engine status
        status = decision_engine.get_engine_status()
        print(f"Status: {json.dumps(status, indent=2)}")
        
        # Test decision making
        analysis = await analyze_market("BTC/USD", 85.5)
        print(f"\nDecision Analysis:")
        print(f"Symbol: {analysis.symbol}")
        print(f"Technical Score: {analysis.technical_score}")
        print(f"AI Sentiment: {analysis.ai_sentiment}")
        print(f"Final Signal: {analysis.final_signal.value}")
        print(f"Reasoning: {analysis.reasoning}")
        print(f"Processing Time: {analysis.execution_metadata['processing_time_ms']}ms")
        
        # Test with different technical scores
        test_scores = [15.2, 45.7, 92.3]
        for score in test_scores:
            analysis = await analyze_market("TSLA", score)
            print(f"\nAEXI {score:.1f} -> {analysis.final_signal.value}")
    
    asyncio.run(main())