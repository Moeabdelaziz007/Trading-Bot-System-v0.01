"""
============================================
🌊 CIPHER CORE STRATEGY - AlphaAxiom Brain
============================================

Advanced trading strategy inspired by:
- Market Cipher B (WaveTrend, Money Flow, VWAP)
- Chaikin Money Flow (CMF)
- Smart Money Concepts (Liquidity, Order Blocks)

Architecture:
1. WaveTrend Oscillator - Primary momentum signal
2. Money Flow Index - Volume-weighted buying/selling pressure
3. CMF (Chaikin Money Flow) - Accumulation/Distribution
4. Confluence Score - Multi-factor validation (80% threshold)

Author: AlphaAxiom Team
Version: 1.0.0
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math

# ============================================
# CONFIGURATION
# ============================================

@dataclass
class CipherConfig:
    """Cipher Strategy Configuration"""
    # WaveTrend Settings
    WT_CHANNEL_LENGTH: int = 9
    WT_AVERAGE_LENGTH: int = 12
    WT_OVERBOUGHT: float = 60
    WT_OVERSOLD: float = -60
    
    # Money Flow Settings
    MFI_LENGTH: int = 14
    MFI_OVERBOUGHT: float = 80
    MFI_OVERSOLD: float = 20
    
    # CMF Settings
    CMF_LENGTH: int = 20
    CMF_BULLISH_THRESHOLD: float = 0.05
    CMF_BEARISH_THRESHOLD: float = -0.05
    
    # Signal Thresholds
    MIN_CONFLUENCE_SCORE: int = 80  # Minimum 80% for entry
    

# ============================================
# WAVETREND OSCILLATOR
# ============================================

class WaveTrend:
    """
    WaveTrend Oscillator - Core of Market Cipher B
    
    Identifies overbought/oversold conditions and momentum shifts.
    Uses EMA smoothing of typical price vs channel.
    """
    
    def __init__(self, config: CipherConfig = None):
        self.config = config or CipherConfig()
    
    def calculate(self, high: List[float], low: List[float], close: List[float]) -> Dict:
        """
        Calculate WaveTrend values.
        
        Formula:
        1. HLC3 = (High + Low + Close) / 3
        2. ESA = EMA(HLC3, channel_length)
        3. D = EMA(|HLC3 - ESA|, channel_length)
        4. CI = (HLC3 - ESA) / (0.015 * D)
        5. WT1 = EMA(CI, average_length)
        6. WT2 = SMA(WT1, 4)
        """
        if len(close) < self.config.WT_CHANNEL_LENGTH + self.config.WT_AVERAGE_LENGTH:
            return {"wt1": 0, "wt2": 0, "signal": "NEUTRAL", "cross": None}
        
        # Calculate HLC3 (Typical Price)
        hlc3 = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
        
        # Calculate ESA (EMA of HLC3)
        esa = self._ema(hlc3, self.config.WT_CHANNEL_LENGTH)
        
        # Calculate D (EMA of absolute deviation)
        d_values = [abs(hlc3[i] - esa[i]) for i in range(len(hlc3))]
        d = self._ema(d_values, self.config.WT_CHANNEL_LENGTH)
        
        # Calculate CI (Commodity Index)
        ci = []
        for i in range(len(hlc3)):
            if d[i] != 0:
                ci.append((hlc3[i] - esa[i]) / (0.015 * d[i]))
            else:
                ci.append(0)
        
        # Calculate WT1 (EMA of CI)
        wt1 = self._ema(ci, self.config.WT_AVERAGE_LENGTH)
        
        # Calculate WT2 (SMA of WT1, period 4)
        wt2 = self._sma(wt1, 4)
        
        # Get latest values
        wt1_current = wt1[-1] if wt1 else 0
        wt2_current = wt2[-1] if wt2 else 0
        wt1_prev = wt1[-2] if len(wt1) > 1 else 0
        wt2_prev = wt2[-2] if len(wt2) > 1 else 0
        
        # Detect crossovers
        cross = None
        if wt1_prev <= wt2_prev and wt1_current > wt2_current:
            cross = "BULLISH"  # WT1 crossed above WT2
        elif wt1_prev >= wt2_prev and wt1_current < wt2_current:
            cross = "BEARISH"  # WT1 crossed below WT2
        
        # Generate signal
        signal = "NEUTRAL"
        if wt1_current < self.config.WT_OVERSOLD and cross == "BULLISH":
            signal = "BUY"
        elif wt1_current > self.config.WT_OVERBOUGHT and cross == "BEARISH":
            signal = "SELL"
        
        return {
            "wt1": round(wt1_current, 2),
            "wt2": round(wt2_current, 2),
            "signal": signal,
            "cross": cross,
            "is_oversold": wt1_current < self.config.WT_OVERSOLD,
            "is_overbought": wt1_current > self.config.WT_OVERBOUGHT
        }
    
    def _ema(self, data: List[float], period: int) -> List[float]:
        """Exponential Moving Average"""
        if len(data) < period:
            return [0] * len(data)
        
        multiplier = 2 / (period + 1)
        ema_values = [sum(data[:period]) / period]  # SMA for first value
        
        for i in range(period, len(data)):
            ema_values.append((data[i] - ema_values[-1]) * multiplier + ema_values[-1])
        
        # Pad with zeros to match length
        return [0] * (len(data) - len(ema_values)) + ema_values
    
    def _sma(self, data: List[float], period: int) -> List[float]:
        """Simple Moving Average"""
        if len(data) < period:
            return [0] * len(data)
        
        sma_values = []
        for i in range(period - 1, len(data)):
            sma_values.append(sum(data[i-period+1:i+1]) / period)
        
        return [0] * (len(data) - len(sma_values)) + sma_values


# ============================================
# CHAIKIN MONEY FLOW (CMF)
# ============================================

class ChaikinMoneyFlow:
    """
    Chaikin Money Flow - Volume-weighted buying/selling pressure
    
    Formula:
    1. MFM = ((Close - Low) - (High - Close)) / (High - Low)
    2. MFV = MFM * Volume
    3. CMF = Sum(MFV, n) / Sum(Volume, n)
    """
    
    def __init__(self, config: CipherConfig = None):
        self.config = config or CipherConfig()
    
    def calculate(
        self, 
        high: List[float], 
        low: List[float], 
        close: List[float], 
        volume: List[float]
    ) -> Dict:
        """Calculate CMF values"""
        if len(close) < self.config.CMF_LENGTH:
            return {"cmf": 0, "signal": "NEUTRAL", "trend": "NEUTRAL"}
        
        # Calculate Money Flow Multiplier for each bar
        mfm = []
        for i in range(len(close)):
            hl_range = high[i] - low[i]
            if hl_range > 0:
                mfm_val = ((close[i] - low[i]) - (high[i] - close[i])) / hl_range
            else:
                mfm_val = 0
            mfm.append(mfm_val)
        
        # Calculate Money Flow Volume
        mfv = [mfm[i] * volume[i] for i in range(len(mfm))]
        
        # Calculate CMF (20-period sum)
        period = self.config.CMF_LENGTH
        cmf_values = []
        for i in range(period - 1, len(mfv)):
            sum_mfv = sum(mfv[i-period+1:i+1])
            sum_vol = sum(volume[i-period+1:i+1])
            if sum_vol > 0:
                cmf_values.append(sum_mfv / sum_vol)
            else:
                cmf_values.append(0)
        
        cmf_current = cmf_values[-1] if cmf_values else 0
        
        # Generate signals
        signal = "NEUTRAL"
        if cmf_current > self.config.CMF_BULLISH_THRESHOLD:
            signal = "BUY"
            trend = "ACCUMULATION"
        elif cmf_current < self.config.CMF_BEARISH_THRESHOLD:
            signal = "SELL"
            trend = "DISTRIBUTION"
        else:
            trend = "NEUTRAL"
        
        return {
            "cmf": round(cmf_current, 4),
            "signal": signal,
            "trend": trend,
            "is_accumulation": cmf_current > 0,
            "is_distribution": cmf_current < 0
        }


# ============================================
# MONEY FLOW INDEX (MFI)
# ============================================

class MoneyFlowIndex:
    """
    Money Flow Index - Volume-weighted RSI
    
    Formula:
    1. Typical Price = (High + Low + Close) / 3
    2. Raw Money Flow = Typical Price * Volume
    3. Money Ratio = Positive MF / Negative MF
    4. MFI = 100 - (100 / (1 + Money Ratio))
    """
    
    def __init__(self, config: CipherConfig = None):
        self.config = config or CipherConfig()
    
    def calculate(
        self, 
        high: List[float], 
        low: List[float], 
        close: List[float], 
        volume: List[float]
    ) -> Dict:
        """Calculate MFI values"""
        period = self.config.MFI_LENGTH
        
        if len(close) < period + 1:
            return {"mfi": 50, "signal": "NEUTRAL"}
        
        # Calculate Typical Price
        typical_price = [(h + l + c) / 3 for h, l, c in zip(high, low, close)]
        
        # Calculate Raw Money Flow
        raw_mf = [tp * v for tp, v in zip(typical_price, volume)]
        
        # Separate positive and negative money flow
        positive_mf = 0
        negative_mf = 0
        
        for i in range(-period, 0):
            if typical_price[i] > typical_price[i-1]:
                positive_mf += raw_mf[i]
            else:
                negative_mf += raw_mf[i]
        
        # Calculate MFI
        if negative_mf == 0:
            mfi = 100
        else:
            money_ratio = positive_mf / negative_mf
            mfi = 100 - (100 / (1 + money_ratio))
        
        # Generate signals
        signal = "NEUTRAL"
        if mfi < self.config.MFI_OVERSOLD:
            signal = "BUY"
        elif mfi > self.config.MFI_OVERBOUGHT:
            signal = "SELL"
        
        return {
            "mfi": round(mfi, 2),
            "signal": signal,
            "is_oversold": mfi < self.config.MFI_OVERSOLD,
            "is_overbought": mfi > self.config.MFI_OVERBOUGHT
        }


# ============================================
# CIPHER STRATEGY - MAIN CLASS
# ============================================

class CipherStrategy:
    """
    🌊 CIPHER CORE STRATEGY
    
    Combines WaveTrend, CMF, and MFI for high-probability signals.
    Only trades when confluence score >= 80%.
    
    Scoring System:
    - WaveTrend Signal: 30 points
    - Money Flow (CMF): 25 points
    - MFI Confirmation: 25 points
    - Trend Alignment: 20 points
    """
    
    def __init__(self, config: CipherConfig = None):
        self.config = config or CipherConfig()
        self.wave_trend = WaveTrend(config)
        self.cmf = ChaikinMoneyFlow(config)
        self.mfi = MoneyFlowIndex(config)
    
    def analyze(
        self,
        symbol: str,
        high: List[float],
        low: List[float],
        close: List[float],
        volume: List[float],
        sma_200: Optional[float] = None
    ) -> Dict:
        """
        Main analysis function.
        
        Returns signal with confluence score and reasoning.
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Calculate indicators
        wt_result = self.wave_trend.calculate(high, low, close)
        cmf_result = self.cmf.calculate(high, low, close, volume)
        mfi_result = self.mfi.calculate(high, low, close, volume)
        
        # Calculate trend (price vs SMA200)
        current_price = close[-1] if close else 0
        if sma_200:
            trend = "BULLISH" if current_price > sma_200 else "BEARISH"
        else:
            trend = "NEUTRAL"
        
        # Calculate confluence score
        score = 0
        reasons = []
        
        # WaveTrend (30 points)
        if wt_result["signal"] == "BUY":
            score += 30
            reasons.append(f"WT Oversold Cross ({wt_result['wt1']})")
        elif wt_result["signal"] == "SELL":
            score += 30
            reasons.append(f"WT Overbought Cross ({wt_result['wt1']})")
        elif wt_result["cross"]:
            score += 15
            reasons.append(f"WT {wt_result['cross']} Cross")
        
        # CMF (25 points)
        if cmf_result["signal"] == "BUY":
            score += 25
            reasons.append(f"CMF Accumulation ({cmf_result['cmf']})")
        elif cmf_result["signal"] == "SELL":
            score += 25
            reasons.append(f"CMF Distribution ({cmf_result['cmf']})")
        elif abs(cmf_result["cmf"]) > 0.02:
            score += 12
            reasons.append(f"CMF Moderate ({cmf_result['cmf']})")
        
        # MFI (25 points)
        if mfi_result["signal"] == "BUY":
            score += 25
            reasons.append(f"MFI Oversold ({mfi_result['mfi']})")
        elif mfi_result["signal"] == "SELL":
            score += 25
            reasons.append(f"MFI Overbought ({mfi_result['mfi']})")
        elif mfi_result["mfi"] < 40 or mfi_result["mfi"] > 60:
            score += 12
            reasons.append(f"MFI Moderate ({mfi_result['mfi']})")
        
        # Trend Alignment (20 points)
        if trend == "BULLISH" and (wt_result["signal"] == "BUY" or cmf_result["signal"] == "BUY"):
            score += 20
            reasons.append("Trend Aligned (Above SMA200)")
        elif trend == "BEARISH" and (wt_result["signal"] == "SELL" or cmf_result["signal"] == "SELL"):
            score += 20
            reasons.append("Trend Aligned (Below SMA200)")
        
        # Determine final signal
        if score >= self.config.MIN_CONFLUENCE_SCORE:
            # High-confidence signal
            if wt_result["signal"] == "BUY" or cmf_result["signal"] == "BUY":
                action = "BUY"
            elif wt_result["signal"] == "SELL" or cmf_result["signal"] == "SELL":
                action = "SELL"
            else:
                action = "NONE"
        else:
            action = "NONE"
        
        # Build response
        result = {
            "symbol": symbol,
            "action": action,
            "confidence": score,
            "reasons": reasons,
            "timestamp": timestamp,
            "indicators": {
                "wave_trend": wt_result,
                "cmf": cmf_result,
                "mfi": mfi_result,
                "trend": trend
            }
        }
        
        # Log with emoji-rich format
        if action != "NONE":
            print(f"🌊 Cipher Signal: {action} {symbol} | Score: {score}/100 | MoneyFlow: {cmf_result['trend']} | WT: {wt_result['cross'] or 'Neutral'}")
            print(f"   📋 Reasons: {', '.join(reasons)}")
        
        return result
    
    def generate_trade_signal(
        self,
        symbol: str,
        candles: List[Dict]
    ) -> Optional[Dict]:
        """
        Generate trade signal from candle data.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            candles: List of OHLCV candles
            
        Returns:
            Trade signal dict or None if no signal
        """
        if not candles or len(candles) < 50:
            return None
        
        # Extract OHLCV
        high = [c.get("high", c.get("h", 0)) for c in candles]
        low = [c.get("low", c.get("l", 0)) for c in candles]
        close = [c.get("close", c.get("c", 0)) for c in candles]
        volume = [c.get("volume", c.get("v", 1)) for c in candles]
        
        # Calculate SMA200 if enough data
        sma_200 = None
        if len(close) >= 200:
            sma_200 = sum(close[-200:]) / 200
        
        # Run analysis
        result = self.analyze(symbol, high, low, close, volume, sma_200)
        
        if result["action"] != "NONE":
            return {
                "action": result["action"],
                "symbol": symbol,
                "confidence": result["confidence"],
                "reasons": result["reasons"],
                "sl": 0,  # EA will calculate safe SL
                "tp": 0,  # EA will calculate safe TP
                "timestamp": result["timestamp"]
            }
        
        return None


# ============================================
# QUICK TEST
# ============================================

if __name__ == "__main__":
    # Test with sample data
    import random
    
    print("🧪 Testing Cipher Strategy...")
    
    # Generate sample data
    n = 100
    base_price = 1.0500
    high = [base_price + random.uniform(0, 0.005) for _ in range(n)]
    low = [base_price - random.uniform(0, 0.005) for _ in range(n)]
    close = [base_price + random.uniform(-0.003, 0.003) for _ in range(n)]
    volume = [random.randint(1000, 5000) for _ in range(n)]
    
    # Create strategy
    strategy = CipherStrategy()
    
    # Run analysis
    result = strategy.analyze("EURUSD", high, low, close, volume)
    
    print(f"\n📊 Result:")
    print(f"   Action: {result['action']}")
    print(f"   Confidence: {result['confidence']}/100")
    print(f"   Reasons: {result['reasons']}")
    print(f"   WaveTrend: {result['indicators']['wave_trend']}")
    print(f"   CMF: {result['indicators']['cmf']}")
    print(f"   MFI: {result['indicators']['mfi']}")
    
    print("\n✅ Cipher Strategy Test Complete!")
