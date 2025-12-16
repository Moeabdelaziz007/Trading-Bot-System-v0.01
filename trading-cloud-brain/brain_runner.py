"""
============================================
🧠 BRAIN RUNNER - The Heartbeat of AlphaAxiom
============================================

24/7 Trading Brain that:
1. Connects to MT5 on the same Windows Server
2. Fetches real-time OHLCV data
3. Runs InstitutionalCipher analysis (DeepSeek + Gemini)
4. Sends signals to Oracle API when confidence >= 80%

Run with: python brain_runner.py

Author: AlphaAxiom Team
Version: 1.0.0
"""

import time
import json
import requests
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional

# Try to import MT5 - will work on Windows with MT5 installed
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("⚠️ MetaTrader5 library not available. Running in DEMO mode.")

# ============================================
# CONFIGURATION
# ============================================

class BrainConfig:
    """Brain Runner Configuration"""
    
    # MT5 Settings
    MT5_LOGIN = 5043654138  # Demo account
    MT5_PASSWORD = ""  # Will prompt or use env
    MT5_SERVER = "MetaQuotes-Demo"
    
    # Trading Symbols
    SYMBOLS = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF"]
    
    # Timeframe (M5 = 5 minutes)
    TIMEFRAME = 5  # mt5.TIMEFRAME_M5 when available
    CANDLE_COUNT = 500  # Number of candles to fetch
    
    # Signal Settings
    MIN_CONFIDENCE = 80  # Minimum confidence to send signal
    
    # API Endpoint
    SIGNAL_API_URL = "https://oracle.axiomid.app/api/v1/signals/push"
    
    # Loop Settings
    SLEEP_SECONDS = 300  # 5 minutes (matches M5 timeframe)
    
    # Logging
    VERBOSE = True


# ============================================
# INSTITUTIONAL CIPHER (Embedded for Portability)
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


class InstitutionalCipherLite:
    """
    Lightweight version of InstitutionalCipher for deployment.
    
    Combines:
    - WaveTrend Oscillator (Momentum)
    - Smart Money Flow (Volume-weighted)
    - VWAP Context
    - Divergence Detection
    """
    
    # Configuration
    WT_CHANNEL_LEN = 10
    WT_AVERAGE_LEN = 21
    WT_OVERSOLD = -60
    WT_OVERBOUGHT = 60
    MF_PERIOD = 60
    MF_MULTIPLIER = 150
    MIN_CONFIDENCE = 80
    
    def analyze(
        self,
        symbol: str,
        open_: np.ndarray,
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        volume: np.ndarray
    ) -> Dict:
        """Main analysis function."""
        
        # ============================================
        # 1. WAVETREND CALCULATION
        # ============================================
        hlc3 = (high + low + close) / 3.0
        esa = vectorized_ema(hlc3, self.WT_CHANNEL_LEN)
        diff = np.abs(hlc3 - esa)
        d = vectorized_ema(diff, self.WT_CHANNEL_LEN)
        epsilon = 1e-10
        ci = (hlc3 - esa) / (0.015 * d + epsilon)
        wt1 = vectorized_ema(ci, self.WT_AVERAGE_LEN)
        wt2 = vectorized_sma(wt1, 4)
        
        wt1_current = wt1[-1]
        wt2_current = wt2[-1]
        wt1_prev = wt1[-2] if len(wt1) > 1 else wt1_current
        wt2_prev = wt2[-2] if len(wt2) > 1 else wt2_current
        
        # Crossovers
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
        # 3. VWAP CONTEXT
        # ============================================
        tp = (high + low + close) / 3.0
        cum_tp_vol = np.cumsum(tp * volume)
        cum_vol = np.cumsum(volume)
        vwap = cum_tp_vol / (cum_vol + epsilon)
        vwap_current = vwap[-1]
        price_current = close[-1]
        below_vwap = price_current < vwap_current
        
        # ============================================
        # 4. SCORING (AND-Gate Logic)
        # ============================================
        score = 0
        reasons = []
        
        # Momentum Gate (30 points)
        if cross_up and is_oversold:
            score += 30
            reasons.append(f"WT Oversold Cross ({wt1_current:.1f})")
        elif cross_down and is_overbought:
            score += 30
            reasons.append(f"WT Overbought Cross ({wt1_current:.1f})")
        elif cross_up:
            score += 15
            reasons.append("WT Bullish Cross")
        elif cross_down:
            score += 15
            reasons.append("WT Bearish Cross")
        
        # Money Flow Gate (25 points)
        if is_accumulation and is_increasing:
            score += 25
            reasons.append("Smart Money Accumulating")
        elif not is_accumulation and not is_increasing:
            score += 25
            reasons.append("Smart Money Distributing")
        elif is_increasing:
            score += 12
            reasons.append("Money Flow Rising")
        
        # Context Gate (25 points)
        if below_vwap and (cross_up or is_oversold):
            score += 25
            reasons.append("Below VWAP (Discount Zone)")
        elif not below_vwap and (cross_down or is_overbought):
            score += 25
            reasons.append("Above VWAP (Premium Zone)")
        elif below_vwap:
            score += 12
            reasons.append("Below VWAP")
        
        # Trend Bonus (20 points)
        # Simple trend: price above/below SMA200
        if len(close) >= 200:
            sma200 = np.mean(close[-200:])
            if price_current > sma200 and (cross_up or is_accumulation):
                score += 20
                reasons.append("Above SMA200 (Bullish)")
            elif price_current < sma200 and (cross_down or not is_accumulation):
                score += 20
                reasons.append("Below SMA200 (Bearish)")
        
        # ============================================
        # 5. FINAL DECISION
        # ============================================
        action = "NONE"
        if score >= self.MIN_CONFIDENCE:
            if cross_up or (is_accumulation and is_oversold):
                action = "BUY"
            elif cross_down or (not is_accumulation and is_overbought):
                action = "SELL"
        
        return {
            "symbol": symbol,
            "action": action,
            "confidence": min(score, 100),
            "reasons": reasons,
            "indicators": {
                "wt1": round(float(wt1_current), 2),
                "wt2": round(float(wt2_current), 2),
                "mf": round(float(mf_current), 2),
                "vwap": round(float(vwap_current), 5),
                "price": round(float(price_current), 5)
            }
        }


# ============================================
# MT5 CONNECTION
# ============================================

class MT5Connector:
    """MetaTrader 5 Connection Manager"""
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.connected = False
    
    def connect(self) -> bool:
        """Initialize connection to MT5."""
        if not MT5_AVAILABLE:
            print("⚠️ MT5 library not available. Using DEMO mode.")
            return False
        
        if not mt5.initialize():
            print(f"❌ MT5 initialize() failed: {mt5.last_error()}")
            return False
        
        print(f"✅ MT5 initialized: {mt5.terminal_info().name}")
        self.connected = True
        return True
    
    def get_candles(self, symbol: str, count: int = 500) -> Optional[Dict]:
        """Fetch OHLCV candles from MT5."""
        if not self.connected or not MT5_AVAILABLE:
            return self._get_demo_candles(symbol, count)
        
        # Get timeframe constant
        timeframe = mt5.TIMEFRAME_M5  # 5-minute candles
        
        # Fetch rates
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        
        if rates is None or len(rates) == 0:
            print(f"⚠️ No data for {symbol}")
            return None
        
        # Convert to arrays
        return {
            "open": np.array([r[1] for r in rates], dtype=np.float64),
            "high": np.array([r[2] for r in rates], dtype=np.float64),
            "low": np.array([r[3] for r in rates], dtype=np.float64),
            "close": np.array([r[4] for r in rates], dtype=np.float64),
            "volume": np.array([r[5] for r in rates], dtype=np.float64)
        }
    
    def _get_demo_candles(self, symbol: str, count: int) -> Dict:
        """Generate demo candles for testing without MT5."""
        np.random.seed(int(time.time()) % 1000)
        
        # Simulate realistic price data
        if "JPY" in symbol:
            base_price = 150.0
            volatility = 0.5
        elif "CHF" in symbol:
            base_price = 0.88
            volatility = 0.002
        else:
            base_price = 1.05
            volatility = 0.002
        
        # Random walk
        returns = np.random.randn(count) * volatility
        close = base_price * np.exp(np.cumsum(returns))
        
        high = close + np.abs(np.random.randn(count)) * volatility
        low = close - np.abs(np.random.randn(count)) * volatility
        open_ = close + np.random.randn(count) * volatility * 0.5
        volume = np.random.exponential(1000, count)
        
        return {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume
        }
    
    def disconnect(self):
        """Clean shutdown."""
        if MT5_AVAILABLE and self.connected:
            mt5.shutdown()
            print("🔌 MT5 disconnected")


# ============================================
# SIGNAL BROADCASTER
# ============================================

class SignalBroadcaster:
    """Sends signals to the Oracle API."""
    
    def __init__(self, config: BrainConfig):
        self.config = config
        self.signals_sent = 0
    
    def send_signal(self, signal: Dict) -> bool:
        """Send signal to Oracle API."""
        try:
            payload = {
                "action": signal["action"],
                "symbol": signal["symbol"],
                "confidence": signal["confidence"],
                "sl": 0,  # EA calculates safe SL
                "tp": 0,  # EA calculates safe TP
                "reason": " | ".join(signal["reasons"][:3])
            }
            
            response = requests.post(
                self.config.SIGNAL_API_URL,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Signal sent! ID: {result.get('signal_id', 'N/A')}")
                self.signals_sent += 1
                return True
            else:
                print(f"   ❌ API Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"   ❌ Broadcast failed: {e}")
            return False


# ============================================
# BRAIN RUNNER - MAIN CLASS
# ============================================

class BrainRunner:
    """
    🧠 The Heartbeat of AlphaAxiom
    
    Runs continuously, analyzing markets and sending signals.
    """
    
    def __init__(self):
        self.config = BrainConfig()
        self.mt5 = MT5Connector(self.config)
        self.cipher = InstitutionalCipherLite()
        self.broadcaster = SignalBroadcaster(self.config)
        self.running = False
        self.cycles = 0
    
    def start(self):
        """Start the brain loop."""
        print("=" * 60)
        print("🧠 ALPHAXIOM BRAIN RUNNER")
        print("=" * 60)
        print(f"   Symbols: {', '.join(self.config.SYMBOLS)}")
        print(f"   Timeframe: M{self.config.TIMEFRAME}")
        print(f"   Min Confidence: {self.config.MIN_CONFIDENCE}%")
        print(f"   API: {self.config.SIGNAL_API_URL}")
        print("=" * 60)
        
        # Connect to MT5
        self.mt5.connect()
        
        # Start loop
        self.running = True
        self._run_loop()
    
    def _run_loop(self):
        """Main analysis loop."""
        while self.running:
            self.cycles += 1
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"\n🔄 Cycle #{self.cycles} | {timestamp}")
            print("-" * 40)
            
            for symbol in self.config.SYMBOLS:
                self._analyze_symbol(symbol)
            
            # Summary
            print("-" * 40)
            print(f"💤 Sleeping {self.config.SLEEP_SECONDS}s until next cycle...")
            print(f"   Total signals sent: {self.broadcaster.signals_sent}")
            
            # Sleep until next candle
            try:
                time.sleep(self.config.SLEEP_SECONDS)
            except KeyboardInterrupt:
                print("\n🛑 Stopping Brain Runner...")
                self.stop()
                break
    
    def _analyze_symbol(self, symbol: str):
        """Analyze a single symbol."""
        # Fetch data
        candles = self.mt5.get_candles(symbol, self.config.CANDLE_COUNT)
        
        if candles is None:
            print(f"   ⚠️ {symbol}: No data")
            return
        
        # Run analysis
        result = self.cipher.analyze(
            symbol,
            candles["open"],
            candles["high"],
            candles["low"],
            candles["close"],
            candles["volume"]
        )
        
        action = result["action"]
        confidence = result["confidence"]
        reasons = result["reasons"]
        
        # Log result
        if action != "NONE" and confidence >= self.config.MIN_CONFIDENCE:
            # High-quality signal!
            print(f"   🌊 {symbol}: {action} | Conf: {confidence}/100")
            print(f"      Reasons: {', '.join(reasons)}")
            
            # Broadcast to API
            self.broadcaster.send_signal(result)
        else:
            # No signal or low confidence
            if self.config.VERBOSE:
                print(f"   💤 {symbol}: {action} | Conf: {confidence}/100 (below threshold)")
    
    def stop(self):
        """Stop the brain runner."""
        self.running = False
        self.mt5.disconnect()
        
        print("\n" + "=" * 60)
        print("🧠 BRAIN RUNNER STOPPED")
        print("=" * 60)
        print(f"   Total Cycles: {self.cycles}")
        print(f"   Signals Sent: {self.broadcaster.signals_sent}")
        print("=" * 60)


# ============================================
# ENTRY POINT
# ============================================

if __name__ == "__main__":
    brain = BrainRunner()
    
    try:
        brain.start()
    except KeyboardInterrupt:
        brain.stop()
    except Exception as e:
        print(f"❌ Fatal Error: {e}")
        brain.stop()
