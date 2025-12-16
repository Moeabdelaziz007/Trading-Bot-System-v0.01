"""
============================================
🧠 BRAIN RUNNER v2.0 - Institutional Trading AI
============================================

MERGED VERSION combining:
- Our: MT5 direct integration, demo mode, embedded cipher
- DeepSeek: async pattern, logging to file, parallel analysis, VWAP stops

Features:
1. Async/await for concurrent analysis (DeepSeek)
2. MT5 direct integration (Our - faster on same server)
3. Professional logging with file handler (DeepSeek)
4. Demo mode fallback (Our - safe testing)
5. VWAP-based stop loss calculation (DeepSeek)
6. Parallel symbol analysis (DeepSeek)

Author: AlphaAxiom Team + DeepSeek Research
Version: 2.0.0 (Production Grade)
"""

import asyncio
import time
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Setup professional logging (DeepSeek)
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "brain_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 library not available. Running in DEMO mode.")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    import requests  # Fallback to sync requests

# Load environment variables for API keys
import os
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Try to import AI Council
try:
    from ai_council import AICouncil, AIConfig
    # Configure API keys
    AIConfig.GROQ_API_KEY = GROQ_API_KEY
    AIConfig.PERPLEXITY_API_KEY = PERPLEXITY_API_KEY
    AIConfig.GEMINI_API_KEY = GEMINI_API_KEY
    AIConfig.OPENROUTER_API_KEY = OPENROUTER_API_KEY
    AI_COUNCIL_AVAILABLE = True
    logger.info("🤖 AI Council loaded successfully")
except ImportError:
    AI_COUNCIL_AVAILABLE = False
    logger.warning("AI Council not available - using cipher-only mode")


# ============================================
# CONFIGURATION
# ============================================

class BrainConfig:
    """Brain Runner Configuration - Production optimized"""
    
    # MT5 Settings
    MT5_LOGIN = 5043654138  # Demo account
    MT5_PASSWORD = ""
    MT5_SERVER = "MetaQuotes-Demo"
    
    # Trading Symbols (Multi-asset)
    SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"]
    
    # Timeframe
    TIMEFRAME_MINUTES = 5
    CANDLE_COUNT = 500
    
    # Signal Thresholds
    CONFIDENCE_THRESHOLD = 70  # 70% minimum (lowered from 80 for more trades)
    
    # ============================================
    # TRADING MODES - AI Strategy Selection
    # ============================================
    # SNIPER = Long-term trades, higher TP, let profits run
    # SCALPER = Quick wins, tight SL/TP, hit-and-run style
    TRADING_MODE = "SCALPER"  # "SNIPER" or "SCALPER"
    
    # SNIPER Mode Settings (Long-term)
    SNIPER_SL_PIPS = 50    # 50 pips stop loss
    SNIPER_TP_PIPS = 150   # 150 pips take profit (1:3 R:R)
    SNIPER_HOLD_TIME = 24  # Hold for up to 24 hours
    
    # SCALPER Mode Settings (Quick wins)
    SCALPER_SL_PIPS = 15   # 15 pips stop loss
    SCALPER_TP_PIPS = 30   # 30 pips take profit (1:2 R:R)
    SCALPER_HOLD_TIME = 2  # Close within 2 hours max
    
    # API Settings
    SIGNAL_API_URL = "https://oracle.axiomid.app/api/v1/signals/push"
    API_KEY = "aw-windows-local-key"
    
    # Risk Management
    MAX_RISK_PERCENT = 2.0  # 2% per trade
    MAX_POSITION_SIZE = 0.1  # Max 0.1 lot
    
    # Loop Settings
    ANALYSIS_INTERVAL_SECONDS = 300  # 5 minutes


# ============================================
# VECTORIZED INDICATORS (Optimized)
# ============================================

def vectorized_ema(prices: np.ndarray, period: int) -> np.ndarray:
    """High-performance EMA calculation."""
    alpha = 2.0 / (period + 1)
    ema = np.zeros_like(prices, dtype=np.float64)
    ema[0] = prices[0]
    for i in range(1, len(prices)):
        ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
    return ema


def vectorized_sma(prices: np.ndarray, period: int) -> np.ndarray:
    """Vectorized SMA using convolution."""
    if len(prices) < period:
        return np.zeros_like(prices)
    kernel = np.ones(period) / period
    return np.convolve(prices, kernel, mode='same')


# ============================================
# INSTITUTIONAL CIPHER (Embedded + Enhanced)
# ============================================

class InstitutionalCipherEngine:
    """
    Institutional Cipher Engine - Enhanced with VWAP stops
    
    Combines:
    - WaveTrend Oscillator
    - Smart Money Flow
    - VWAP with Standard Deviation Bands
    - Divergence Detection
    """
    
    # Configuration
    WT_CHANNEL_LEN = 10
    WT_AVERAGE_LEN = 21
    WT_OVERSOLD = -60
    WT_OVERBOUGHT = 60
    MF_PERIOD = 60
    MF_MULTIPLIER = 150
    CONFIDENCE_THRESHOLD = 80
    
    def __init__(self):
        self.last_analysis = {}
    
    async def analyze(
        self,
        symbol: str,
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> Dict:
        """Async analysis for concurrent processing."""
        # Run sync analysis in executor to not block
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._sync_analyze,
            symbol, open_, high, low, close, volume
        )
    
    def _sync_analyze(
        self,
        symbol: str,
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> Dict:
        """Synchronous analysis logic."""
        
        epsilon = 1e-10
        
        # ============================================
        # 1. WAVETREND CALCULATION
        # ============================================
        hlc3 = (high + low + close) / 3.0
        esa = vectorized_ema(hlc3, self.WT_CHANNEL_LEN)
        diff = np.abs(hlc3 - esa)
        d = vectorized_ema(diff, self.WT_CHANNEL_LEN)
        ci = (hlc3 - esa) / (0.015 * d + epsilon)
        wt1 = vectorized_ema(ci, self.WT_AVERAGE_LEN)
        wt2 = vectorized_sma(wt1, 4)
        
        wt1_current = wt1[-1]
        wt2_current = wt2[-1]
        wt1_prev = wt1[-2] if len(wt1) > 1 else wt1_current
        wt2_prev = wt2[-2] if len(wt2) > 1 else wt2_current
        
        cross_up = (wt1_prev <= wt2_prev) and (wt1_current > wt2_current)
        cross_down = (wt1_prev >= wt2_prev) and (wt1_current < wt2_current)
        is_oversold = wt1_current < self.WT_OVERSOLD
        is_overbought = wt1_current > self.WT_OVERBOUGHT
        
        # ============================================
        # 2. SMART MONEY FLOW
        # ============================================
        clv = (close - open_) / (high - low + epsilon)
        money_flow_raw = clv * volume * self.MF_MULTIPLIER
        money_flow = vectorized_sma(money_flow_raw, self.MF_PERIOD)
        mf_current = money_flow[-1]
        mf_prev = money_flow[-2] if len(money_flow) > 1 else mf_current
        is_accumulation = mf_current > 0
        is_increasing = mf_current > mf_prev
        
        # ============================================
        # 3. VWAP WITH BANDS (DeepSeek Enhancement)
        # ============================================
        tp = (high + low + close) / 3.0
        cum_tp_vol = np.cumsum(tp * volume)
        cum_vol = np.cumsum(volume)
        vwap = cum_tp_vol / (cum_vol + epsilon)
        
        # Standard deviation for bands
        squared_diff = (tp - vwap) ** 2
        cum_squared_diff = np.cumsum(squared_diff * volume)
        variance = cum_squared_diff / (cum_vol + epsilon)
        std_dev = np.sqrt(variance)
        
        vwap_current = vwap[-1]
        std_current = std_dev[-1]
        price_current = close[-1]
        
        # VWAP Bands
        vwap_upper1 = vwap_current + std_current
        vwap_lower1 = vwap_current - std_current
        vwap_upper2 = vwap_current + 2 * std_current
        vwap_lower2 = vwap_current - 2 * std_current
        
        below_vwap = price_current < vwap_current
        above_vwap = price_current > vwap_current
        
        # ============================================
        # 4. CONFIDENCE SCORING (AND-Gate Logic)
        # ============================================
        score = 0
        reasons = []
        metadata = {}
        
        # Gate 1: WaveTrend Momentum (30 points)
        if cross_up and is_oversold:
            score += 30
            reasons.append(f"WT Oversold Cross ({wt1_current:.1f})")
            metadata['cross_up'] = True
            metadata['oversold'] = True
        elif cross_down and is_overbought:
            score += 30
            reasons.append(f"WT Overbought Cross ({wt1_current:.1f})")
            metadata['cross_down'] = True
        elif cross_up:
            score += 15
            reasons.append("WT Bullish Cross")
            metadata['cross_up'] = True
        elif cross_down:
            score += 15
            reasons.append("WT Bearish Cross")
        
        # Gate 2: Money Flow (25 points)
        if is_accumulation and is_increasing:
            score += 25
            reasons.append("Smart Money Accumulating")
            metadata['mf_confirmation'] = True
        elif not is_accumulation and not is_increasing:
            score += 25
            reasons.append("Smart Money Distributing")
            metadata['mf_confirmation'] = True
        elif is_increasing:
            score += 12
            reasons.append("Money Flow Rising")
        
        # Gate 3: VWAP Context (25 points)
        if below_vwap and (cross_up or is_oversold):
            score += 25
            reasons.append("Below VWAP (Discount Zone)")
        elif above_vwap and (cross_down or is_overbought):
            score += 25
            reasons.append("Above VWAP (Premium Zone)")
            metadata['price_above_vwap'] = True
        elif below_vwap:
            score += 12
            reasons.append("Below VWAP")
        
        # Gate 4: Trend Alignment (20 points)
        if len(close) >= 200:
            sma200 = np.mean(close[-200:])
            if price_current > sma200 and (cross_up or is_accumulation):
                score += 20
                reasons.append("Above SMA200")
            elif price_current < sma200 and (cross_down or not is_accumulation):
                score += 20
                reasons.append("Below SMA200")
        
        # Volatility adjustment (DeepSeek)
        recent_volatility = np.std(close[-20:]) / np.mean(close[-20:])
        if recent_volatility > 0.005:  # High volatility
            score = int(score * 0.8)
            reasons.append("⚠️ High Volatility Adjustment")
        
        # ============================================
        # 5. FINAL DECISION
        # ============================================
        action = "NONE"
        if score >= self.CONFIDENCE_THRESHOLD:
            if cross_up or (is_accumulation and is_oversold):
                action = "BUY"
            elif cross_down or (not is_accumulation and is_overbought):
                action = "SELL"
        
        # ============================================
        # 6. STOP LOSS / TAKE PROFIT (DeepSeek VWAP-based)
        # ============================================
        stop_loss = 0  # 0 means EA will calculate
        take_profit = 0
        
        if action == "BUY":
            # Stop below recent low or VWAP-1SD
            recent_low = np.min(low[-10:])
            stop_loss = min(recent_low, vwap_lower1)
            take_profit = vwap_upper1
        elif action == "SELL":
            recent_high = np.max(high[-10:])
            stop_loss = max(recent_high, vwap_upper1)
            take_profit = vwap_lower1
        
        # Position size based on confidence (DeepSeek)
        lot_size = round(0.01 * (score / 100), 2)
        
        return {
            "symbol": symbol,
            "action": action,
            "confidence": min(score, 100),
            "reasons": reasons,
            "entry_price": float(price_current),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "lot_size": lot_size,
            "metadata": metadata,
            "indicators": {
                "wt1": round(float(wt1_current), 2),
                "wt2": round(float(wt2_current), 2),
                "money_flow": round(float(mf_current), 2),
                "vwap": round(float(vwap_current), 5),
                "price": round(float(price_current), 5)
            },
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================
# MT5 CONNECTOR (Our Implementation)
# ============================================

class MT5Connector:
    """MetaTrader 5 Direct Connection (faster on same server)"""
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.connected = False
    
    async def connect(self) -> bool:
        """Initialize connection to MT5."""
        if not MT5_AVAILABLE:
            logger.warning("MT5 library not available. Using DEMO mode.")
            return False
        
        # Run in executor to not block
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, mt5.initialize)
        
        if not result:
            logger.error(f"MT5 initialize() failed: {mt5.last_error()}")
            return False
        
        logger.info(f"✅ MT5 initialized: {mt5.terminal_info().name}")
        self.connected = True
        return True
    
    async def get_candles(self, symbol: str, count: int = 500) -> Optional[Dict]:
        """Fetch OHLCV candles from MT5."""
        if not self.connected or not MT5_AVAILABLE:
            return self._get_demo_candles(symbol, count)
        
        loop = asyncio.get_event_loop()
        rates = await loop.run_in_executor(
            None,
            lambda: mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, count)
        )
        
        if rates is None or len(rates) == 0:
            logger.warning(f"No data for {symbol}, using demo data")
            return self._get_demo_candles(symbol, count)
        
        return {
            "open": np.array([r[1] for r in rates], dtype=np.float64),
            "high": np.array([r[2] for r in rates], dtype=np.float64),
            "low": np.array([r[3] for r in rates], dtype=np.float64),
            "close": np.array([r[4] for r in rates], dtype=np.float64),
            "volume": np.array([r[5] for r in rates], dtype=np.float64)
        }
    
    def _get_demo_candles(self, symbol: str, count: int) -> Dict:
        """Generate demo candles for testing."""
        np.random.seed(int(time.time()) % 1000)
        
        if "JPY" in symbol:
            base_price, volatility = 150.0, 0.5
        elif "CHF" in symbol:
            base_price, volatility = 0.88, 0.002
        else:
            base_price, volatility = 1.05, 0.002
        
        returns = np.random.randn(count) * volatility
        close = base_price * np.exp(np.cumsum(returns))
        
        return {
            "open": close + np.random.randn(count) * volatility * 0.5,
            "high": close + np.abs(np.random.randn(count)) * volatility,
            "low": close - np.abs(np.random.randn(count)) * volatility,
            "close": close,
            "volume": np.random.exponential(1000, count)
        }
    
    async def disconnect(self):
        """Clean shutdown."""
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            logger.info("🔌 MT5 disconnected")


# ============================================
# ORACLE API CLIENT (Async - DeepSeek Pattern)
# ============================================

class OracleAPIClient:
    """Async API client for sending signals to Oracle."""
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.signals_sent = 0
        self.session = None
    
    async def __aenter__(self):
        if AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_signal(self, signal: Dict) -> Dict[str, Any]:
        """Send signal to Oracle API."""
        payload = {
            "action": signal["action"],
            "symbol": signal["symbol"],
            "confidence": signal["confidence"],
            "sl": signal.get("stop_loss", 0),
            "tp": signal.get("take_profit", 0),
            "quantity": signal.get("lot_size", 0.01),
            "reason": " | ".join(signal["reasons"][:3])
        }
        
        try:
            if AIOHTTP_AVAILABLE and self.session:
                async with self.session.post(
                    self.config.SIGNAL_API_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    if response.status == 200:
                        self.signals_sent += 1
                        logger.info(f"   ✅ Signal sent! ID: {result.get('signal_id', 'N/A')}")
                        return {"success": True, "response": result}
                    else:
                        logger.error(f"   ❌ API Error: {response.status}")
                        return {"success": False, "error": str(response.status)}
            else:
                # Fallback to sync requests
                response = requests.post(
                    self.config.SIGNAL_API_URL,
                    json=payload,
                    timeout=10
                )
                if response.status_code == 200:
                    self.signals_sent += 1
                    result = response.json()
                    logger.info(f"   ✅ Signal sent! ID: {result.get('signal_id', 'N/A')}")
                    return {"success": True, "response": result}
                else:
                    logger.error(f"   ❌ API Error: {response.status_code}")
                    return {"success": False, "error": str(response.status_code)}
                    
        except Exception as e:
            logger.error(f"   ❌ Broadcast failed: {e}")
            return {"success": False, "error": str(e)}


# ============================================
# BRAIN RUNNER (Async - DeepSeek Pattern)
# ============================================

class InstitutionalBrain:
    """
    🧠 Institutional Trading Brain - AI-Enhanced
    
    Runs 24/7, analyzing markets with:
    1. Technical Analysis (Cipher Engine)
    2. AI Council (Groq, Perplexity, Gemini, DeepSeek)
    
    AI makes the brain smarter with:
    - News filtering (avoid high-impact events)
    - Sentiment analysis (market mood)
    - Pattern recognition (chart patterns)
    - Self-improvement (learning from trades)
    """
    
    def __init__(self):
        self.config = BrainConfig()
        self.mt5 = MT5Connector(self.config)
        self.cipher = InstitutionalCipherEngine()
        self.api_client = OracleAPIClient(self.config)
        
        # AI Council for enhanced decisions
        if AI_COUNCIL_AVAILABLE:
            self.ai_council = AICouncil()
            logger.info("🤖 AI Council integrated - Brain is now smarter!")
        else:
            self.ai_council = None
            logger.warning("⚠️ AI Council not available - using cipher-only mode")
        
        # Trade history for self-improvement
        self.trade_history = []
        self.win_count = 0
        self.loss_count = 0
        
        self.last_analysis_time = {}
        self.cycles = 0
        self.running = False
    
    async def start(self):
        """Start the brain loop."""
        logger.info("=" * 60)
        logger.info("🧠 INSTITUTIONAL BRAIN v2.0 - Starting")
        logger.info("=" * 60)
        logger.info(f"   Symbols: {', '.join(self.config.SYMBOLS)}")
        logger.info(f"   Timeframe: M{self.config.TIMEFRAME_MINUTES}")
        logger.info(f"   Confidence Threshold: {self.config.CONFIDENCE_THRESHOLD}%")
        logger.info(f"   API: {self.config.SIGNAL_API_URL}")
        logger.info("=" * 60)
        
        # Connect to MT5
        await self.mt5.connect()
        
        # Start async loop
        self.running = True
        async with self.api_client:
            await self._run_continuous_analysis()
    
    async def _run_continuous_analysis(self):
        """Main analysis loop - runs every 5 minutes."""
        while self.running:
            try:
                self.cycles += 1
                current_time = datetime.utcnow()
                timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
                
                logger.info(f"\n🔄 Cycle #{self.cycles} | {timestamp}")
                logger.info("-" * 40)
                
                # Parallel analysis of all symbols (DeepSeek pattern)
                tasks = [
                    self._analyze_symbol(symbol)
                    for symbol in self.config.SYMBOLS
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                signals_this_cycle = 0
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"   ❌ {self.config.SYMBOLS[i]}: {result}")
                    elif result and result.get("action") != "NONE":
                        signals_this_cycle += 1
                
                # Summary
                logger.info("-" * 40)
                logger.info(f"💤 Sleeping {self.config.ANALYSIS_INTERVAL_SECONDS}s until next cycle...")
                logger.info(f"   This cycle signals: {signals_this_cycle}")
                logger.info(f"   Total signals sent: {self.api_client.signals_sent}")
                
                # Wait until next candle close
                await asyncio.sleep(self.config.ANALYSIS_INTERVAL_SECONDS)
                
            except asyncio.CancelledError:
                logger.info("🛑 Brain Runner cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _analyze_symbol(self, symbol: str) -> Optional[Dict]:
        """Analyze a single symbol with AI enhancement."""
        try:
            # Fetch data
            candles = await self.mt5.get_candles(symbol, self.config.CANDLE_COUNT)
            
            if candles is None:
                logger.warning(f"   ⚠️ {symbol}: No data")
                return None
            
            # Run cipher analysis first
            result = await self.cipher.analyze(
                symbol,
                candles["open"],
                candles["high"],
                candles["low"],
                candles["close"],
                candles["volume"]
            )
            
            cipher_score = result["confidence"]
            action = result["action"]
            reasons = result["reasons"]
            
            # ============================================
            # AI COUNCIL CONSULTATION
            # ============================================
            if self.ai_council and action != "NONE":
                logger.info(f"   🤖 Consulting AI Council for {symbol}...")
                
                # Consult AI models
                ai_result = await self.ai_council.consult(
                    symbol=symbol,
                    price=result["indicators"]["price"],
                    indicators=result["indicators"],
                    cipher_score=cipher_score,
                    recent_prices=list(candles["close"][-50:])
                )
                
                # Update score with AI adjustment
                ai_adjusted_score = ai_result.get("ai_adjusted_score", cipher_score)
                news_risk = ai_result.get("news_risk", "LOW")
                consensus = ai_result.get("consensus", "HOLD")
                
                # Add AI insights to reasons
                if ai_result.get("models_consulted"):
                    reasons.append(f"🤖 AI: {consensus} ({len(ai_result['models_consulted'])} models)")
                
                # Override action if AI strongly disagrees
                if news_risk == "HIGH":
                    logger.warning(f"   📰 {symbol}: High news risk - SKIPPING trade")
                    result["action"] = "NONE"
                    result["reasons"].append("⚠️ High news risk - trade avoided")
                    return None
                
                # Use AI-adjusted score
                result["confidence"] = ai_adjusted_score
                result["ai_analysis"] = ai_result
                
                logger.info(f"   📊 Score: {cipher_score}→{ai_adjusted_score} | News: {news_risk} | AI: {consensus}")
            
            # ============================================
            # FINAL DECISION
            # ============================================
            action = result["action"]
            final_confidence = result["confidence"]
            
            if action != "NONE" and final_confidence >= self.config.CONFIDENCE_THRESHOLD:
                logger.info(f"   🌊 {symbol}: {action} | Conf: {final_confidence}/100")
                logger.info(f"      Reasons: {', '.join(reasons[:3])}")
                logger.info(f"      SL: {result['stop_loss']:.5f} | TP: {result['take_profit']:.5f}")
                
                # Track trade for self-improvement
                self.trade_history.append({
                    "symbol": symbol,
                    "action": action,
                    "confidence": final_confidence,
                    "timestamp": result["timestamp"]
                })
                
                # Send to API
                await self.api_client.send_signal(result)
                return result
            else:
                logger.info(f"   💤 {symbol}: {action} | Conf: {final_confidence}/100 (below threshold)")
                return None
                
        except Exception as e:
            logger.error(f"   ❌ {symbol}: Analysis failed - {e}")
            return None
    
    async def stop(self):
        """Stop the brain runner."""
        self.running = False
        await self.mt5.disconnect()
        
        logger.info("\n" + "=" * 60)
        logger.info("🧠 INSTITUTIONAL BRAIN STOPPED")
        logger.info("=" * 60)
        logger.info(f"   Total Cycles: {self.cycles}")
        logger.info(f"   Signals Sent: {self.api_client.signals_sent}")
        logger.info("=" * 60)


# ============================================
# ENTRY POINT
# ============================================

async def main():
    """Main entry point."""
    brain = InstitutionalBrain()
    
    try:
        await brain.start()
    except KeyboardInterrupt:
        logger.info("\n🛑 Keyboard interrupt received")
        await brain.stop()
    except Exception as e:
        logger.error(f"❌ Fatal Error: {e}")
        await brain.stop()


if __name__ == "__main__":
    asyncio.run(main())
