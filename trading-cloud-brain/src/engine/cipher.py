"""
🟢 Cipher Engine - Institutional Money Flow Logic
=================================================
Implements the core logic of "Market Cipher B" (MFI + VWAP).
Used to detect institutional buying/selling pressure.

Logic:
    - MFI (Money Flow Index): Volume-weighted RSI. 
      - Green (>60) = Inflow
      - Red (<40) = Outflow
    - VWAP (Volume Weighted Avg Price): Institutional fair value.
      - Price > VWAP = Bullish
      - Price < VWAP = Bearish

Signal Generation:
    - BUY: MFI < 20 (Oversold) AND turning up (Green Dot equivalent)
    - SELL: MFI > 80 (Overbought) AND turning down (Red Dot equivalent)
    - TREND_BUY: Price > VWAP AND MFI > 50 (Momentum)
"""

import numpy as np
import logging
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SignalType(Enum):
    BUY = "buy"
    SELL = "sell"
    NEUTRAL = "neutral"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


@dataclass
class CipherAnalysis:
    """Result of Cipher analysis."""
    symbol: str
    timeframe: str
    price: float
    mfi: float
    vwap: float
    rsi: float
    signal: SignalType
    strength: float  # 0.0 to 1.0
    reason: str


class CipherEngine:
    """
    The 'Money Flow' Engine.
    Analyzes candle data to detect institutional footprints.
    """
    
    def __init__(self, mfi_period: int = 14, vwap_period: int = 14):
        self.mfi_period = mfi_period
        self.vwap_period = vwap_period
    
    def analyze(
        self, 
        symbol: str, 
        candles: List[Dict[str, Any]], 
        timeframe: str = "1h"
    ) -> CipherAnalysis:
        """
        Analyze a series of candles and generate a signal.
        
        Args:
            symbol: Trading pair
            candles: List of dicts {'close': float, 'high': ..., 'volume': ...}
            timeframe: e.g. '1h'
            
        Returns:
            CipherAnalysis object
        """
        if not candles or len(candles) < max(self.mfi_period, self.vwap_period) + 5:
            return self._empty_analysis(symbol, timeframe)
            
        # Extract numpy arrays for speed
        closes = np.array([c['close'] for c in candles])
        highs = np.array([c['high'] for c in candles])
        lows = np.array([c['low'] for c in candles])
        volumes = np.array([c['volume'] for c in candles])
        
        # 1. Calculate MFI
        mfi = self._calculate_mfi(highs, lows, closes, volumes)
        current_mfi = mfi[-1]
        prev_mfi = mfi[-2]
        
        # 2. Calculate VWAP (Rolling)
        vwap = self._calculate_vwap(highs, lows, closes, volumes)
        current_vwap = vwap[-1]
        current_price = closes[-1]
        
        # 3. Calculate RSI (Supplementary)
        rsi = self._calculate_rsi(closes)
        current_rsi = rsi[-1]
        
        # 4. Generate Signal
        signal, strength, reason = self._detect_signal(
            current_price, current_vwap, current_mfi, prev_mfi, current_rsi
        )
        
        return CipherAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            price=current_price,
            mfi=current_mfi,
            vwap=current_vwap,
            rsi=current_rsi,
            signal=signal,
            strength=strength,
            reason=reason
        )

    def _calculate_mfi(self, highs, lows, closes, volumes, period=14):
        """Calculate Money Flow Index."""
        tp = (highs + lows + closes) / 3
        raw_money_flow = tp * volumes
        
        positive_flow = []
        negative_flow = []
        
        # First diff
        diff = np.diff(tp)
        # Pad first element to match length
        diff = np.insert(diff, 0, 0.0)
        
        for i in range(len(diff)):
            if diff[i] > 0:
                positive_flow.append(raw_money_flow[i])
                negative_flow.append(0)
            else:
                positive_flow.append(0)
                negative_flow.append(raw_money_flow[i])
                
        # Calculate ratios over rolling window
        # We'll use a simple loop for clarity, though rolling_window methods are faster for huge datasets
        mfi_series = []
        for i in range(len(tp)):
            if i < period:
                mfi_series.append(50.0)
                continue
                
            pos_sum = sum(positive_flow[i-period:i])
            neg_sum = sum(negative_flow[i-period:i])
            
            if neg_sum == 0:
                mfi = 100.0
            else:
                mfr = pos_sum / neg_sum
                mfi = 100 - (100 / (1 + mfr))
            mfi_series.append(mfi)
            
        return np.array(mfi_series)

    def _calculate_vwap(self, highs, lows, closes, volumes, period=14):
        """Calculate Rolling VWAP."""
        tp = (highs + lows + closes) / 3
        matches = tp * volumes
        
        vwap_series = []
        for i in range(len(tp)):
            if i < period:
                # Not enough data for full period, use expanding
                cum_vol = np.sum(volumes[:i+1])
                cum_tp_vol = np.sum(matches[:i+1])
            else:
                # Rolling window
                cum_vol = np.sum(volumes[i-period:i+1])
                cum_tp_vol = np.sum(matches[i-period:i+1])
            
            if cum_vol == 0:
                vwap_series.append(tp[i])
            else:
                vwap_series.append(cum_tp_vol / cum_vol)
                
        return np.array(vwap_series)

    def _calculate_rsi(self, prices, period=14):
        """Calculate standard RSI."""
        deltas = np.diff(prices)
        seed = deltas[:period+1]
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:period] = 100. - 100./(1. + rs)

        for i in range(period, len(prices)):
            delta = deltas[i - 1] 
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            rs = up / down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
        
        return rsi

    def _detect_signal(
        self, price, vwap, mfi, prev_mfi, rsi
    ) -> Tuple[SignalType, float, str]:
        """Core Strategy Logic."""
        
        # 1. Money Flow Crossover (The "Green Dot")
        # Oversold (<20) and crossing up
        if prev_mfi < 20 and mfi > 20:
            strength = 0.9
            if price > vwap: strength += 0.1 # Stronger if above value
            return SignalType.STRONG_BUY, strength, "MFI Green Dot (Oversold Bounce)"

        # 2. Money Flow Dump (The "Red Dot")
        # Overbought (>80) and crossing down
        if prev_mfi > 80 and mfi < 80:
            strength = 0.9
            if price < vwap: strength += 0.1
            return SignalType.STRONG_SELL, strength, "MFI Red Dot (Overbought Dump)"
            
        # 3. Simple Trend Following
        if price > vwap and mfi > 50 and mfi > prev_mfi:
            # Bullish flow
            if rsi < 70:
                return SignalType.BUY, 0.6, "Trend Follow (Price > VWAP + MFI Rising)"
        
        if price < vwap and mfi < 50 and mfi < prev_mfi:
            # Bearish flow
            if rsi > 30:
                return SignalType.SELL, 0.6, "Trend Follow (Price < VWAP + MFI Falling)"
                
        return SignalType.NEUTRAL, 0.0, "No clear signal"

    def _empty_analysis(self, symbol, timeframe) -> CipherAnalysis:
        return CipherAnalysis(
            symbol=symbol,
            timeframe=timeframe,
            price=0, mfi=0, vwap=0, rsi=0,
            signal=SignalType.NEUTRAL,
            strength=0,
            reason="Insufficient Data"
        )
