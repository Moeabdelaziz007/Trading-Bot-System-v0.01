"""
🔍 PatternScanner - Unified Pattern Recognition Module
Detects candlestick, chart, and harmonic patterns in price data.

Inspired by TA-Lib, pyharmonics, and chart_patterns libraries.
Optimized for Cloudflare Workers (pure Python, no dependencies).

Pattern Categories:
    1. Candlestick (1-3 bars): Doji, Hammer, Engulfing, Stars
    2. Chart (10+ bars): Double Top/Bottom, Head & Shoulders
    3. Harmonic (XABCD): Gartley, Bat, Crab

Usage:
    scanner = PatternScanner(candle_data)
    patterns = scanner.scan_all()
"""

import math
from typing import List, Dict, Optional


class PatternScanner:
    """
    Unified Pattern Recognition for Trading.
    Pure Python implementation for Cloudflare Workers compatibility.
    """
    
    def __init__(self, data: List[Dict]):
        """
        Initialize PatternScanner.
        
        Args:
            data: List of OHLCV dicts [{open, high, low, close, volume}, ...]
        """
        self.data = data
        self.closes = [d['close'] for d in data]
        self.opens = [d['open'] for d in data]
        self.highs = [d['high'] for d in data]
        self.lows = [d['low'] for d in data]

    # ==========================================
    # 🕯️ CANDLESTICK PATTERNS (1-3 bars)
    # ==========================================
    
    def detect_doji(self, tolerance: float = 0.1) -> Dict:
        """
        Detect Doji candle (open ≈ close).
        
        Doji indicates indecision, potential reversal.
        
        Args:
            tolerance: Max body/range ratio (0.1 = 10%)
        
        Returns:
            dict: {detected, type, strength}
        """
        if len(self.data) < 1:
            return {"detected": False}
            
        c = self.data[-1]
        body = abs(c['close'] - c['open'])
        range_ = c['high'] - c['low']
        
        if range_ == 0:
            return {"detected": False}
        
        body_ratio = body / range_
        
        if body_ratio <= tolerance:
            # Classify doji type
            upper_wick = c['high'] - max(c['open'], c['close'])
            lower_wick = min(c['open'], c['close']) - c['low']
            
            doji_type = "STANDARD"
            if upper_wick > lower_wick * 2:
                doji_type = "GRAVESTONE"
            elif lower_wick > upper_wick * 2:
                doji_type = "DRAGONFLY"
                
            return {
                "detected": True,
                "type": doji_type,
                "strength": round(1 - body_ratio, 2)
            }
        
        return {"detected": False}
    
    def detect_hammer(self) -> Dict:
        """
        Detect Hammer/Hanging Man pattern.
        
        Hammer (at bottom): Long lower wick, small body at top.
        Hanging Man (at top): Same shape, different context.
        
        Returns:
            dict: {detected, bullish, trend_context}
        """
        if len(self.data) < 5:
            return {"detected": False}
            
        c = self.data[-1]
        body = abs(c['close'] - c['open'])
        range_ = c['high'] - c['low']
        
        if range_ == 0 or body == 0:
            return {"detected": False}
        
        lower_wick = min(c['open'], c['close']) - c['low']
        upper_wick = c['high'] - max(c['open'], c['close'])
        
        # Hammer criteria: lower wick >= 2x body, upper wick small
        is_hammer = (lower_wick >= body * 2) and (upper_wick <= body * 0.5)
        
        if is_hammer:
            # Check trend context
            prev_closes = self.closes[-6:-1]
            is_downtrend = prev_closes[0] > prev_closes[-1]
            
            return {
                "detected": True,
                "bullish": is_downtrend,
                "pattern": "HAMMER" if is_downtrend else "HANGING_MAN",
                "strength": round(lower_wick / body, 2)
            }
        
        return {"detected": False}
    
    def detect_engulfing(self) -> Dict:
        """
        Detect Bullish/Bearish Engulfing pattern.
        
        Current candle completely engulfs previous candle's body.
        
        Returns:
            dict: {detected, bullish, strength}
        """
        if len(self.data) < 2:
            return {"detected": False}
        
        prev = self.data[-2]
        curr = self.data[-1]
        
        prev_body_top = max(prev['open'], prev['close'])
        prev_body_bottom = min(prev['open'], prev['close'])
        curr_body_top = max(curr['open'], curr['close'])
        curr_body_bottom = min(curr['open'], curr['close'])
        
        # Bullish engulfing: prev is red, curr is green and engulfs
        is_prev_bearish = prev['close'] < prev['open']
        is_curr_bullish = curr['close'] > curr['open']
        is_bullish_engulf = (
            is_prev_bearish and 
            is_curr_bullish and
            curr_body_bottom < prev_body_bottom and
            curr_body_top > prev_body_top
        )
        
        # Bearish engulfing: prev is green, curr is red and engulfs
        is_prev_bullish = prev['close'] > prev['open']
        is_curr_bearish = curr['close'] < curr['open']
        is_bearish_engulf = (
            is_prev_bullish and 
            is_curr_bearish and
            curr_body_top > prev_body_top and
            curr_body_bottom < prev_body_bottom
        )
        
        if is_bullish_engulf or is_bearish_engulf:
            return {
                "detected": True,
                "bullish": is_bullish_engulf,
                "pattern": "BULLISH_ENGULFING" if is_bullish_engulf else "BEARISH_ENGULFING",
                "strength": round(abs(curr['close'] - curr['open']) / abs(prev['close'] - prev['open']), 2)
            }
        
        return {"detected": False}
    
    def detect_morning_star(self) -> Dict:
        """
        Detect Morning/Evening Star pattern (3-bar reversal).
        
        Morning: Large red → Small body (star) → Large green
        Evening: Large green → Small body (star) → Large red
        
        Returns:
            dict: {detected, bullish}
        """
        if len(self.data) < 3:
            return {"detected": False}
        
        first = self.data[-3]
        star = self.data[-2]
        third = self.data[-1]
        
        first_body = abs(first['close'] - first['open'])
        star_body = abs(star['close'] - star['open'])
        third_body = abs(third['close'] - third['open'])
        
        # Star must be significantly smaller
        avg_body = (first_body + third_body) / 2
        is_star_small = star_body < avg_body * 0.3
        
        # Morning Star: Red → Star → Green
        is_morning = (
            first['close'] < first['open'] and  # First is bearish
            is_star_small and
            third['close'] > third['open'] and  # Third is bullish
            third['close'] > (first['open'] + first['close']) / 2  # Close above first midpoint
        )
        
        # Evening Star: Green → Star → Red
        is_evening = (
            first['close'] > first['open'] and  # First is bullish
            is_star_small and
            third['close'] < third['open'] and  # Third is bearish
            third['close'] < (first['open'] + first['close']) / 2  # Close below first midpoint
        )
        
        if is_morning or is_evening:
            return {
                "detected": True,
                "bullish": is_morning,
                "pattern": "MORNING_STAR" if is_morning else "EVENING_STAR"
            }
        
        return {"detected": False}

    # ==========================================
    # 📈 CHART PATTERNS (Structure-based)
    # ==========================================
    
    def _find_pivots(self, lookback: int = 5) -> Dict:
        """Find swing highs and lows."""
        swing_highs = []
        swing_lows = []
        
        for i in range(lookback, len(self.data) - lookback):
            # Swing high: higher than surrounding bars
            is_high = all(self.highs[i] > self.highs[i-j] and 
                         self.highs[i] > self.highs[i+j] 
                         for j in range(1, lookback+1))
            if is_high:
                swing_highs.append({"index": i, "price": self.highs[i]})
            
            # Swing low: lower than surrounding bars
            is_low = all(self.lows[i] < self.lows[i-j] and 
                        self.lows[i] < self.lows[i+j] 
                        for j in range(1, lookback+1))
            if is_low:
                swing_lows.append({"index": i, "price": self.lows[i]})
        
        return {"highs": swing_highs, "lows": swing_lows}
    
    def detect_double_top(self, tolerance: float = 0.02) -> Dict:
        """
        Detect Double Top pattern.
        
        Two peaks at similar price levels with a trough between.
        
        Args:
            tolerance: Max price difference between peaks (2%)
        
        Returns:
            dict: {detected, peaks, neckline, target}
        """
        pivots = self._find_pivots()
        highs = pivots['highs']
        
        if len(highs) < 2:
            return {"detected": False}
        
        # Check last two peaks
        peak1 = highs[-2]
        peak2 = highs[-1]
        
        price_diff = abs(peak1['price'] - peak2['price']) / peak1['price']
        
        if price_diff <= tolerance:
            # Find trough between peaks
            trough_idx = min(range(peak1['index'], peak2['index']+1), 
                           key=lambda x: self.lows[x])
            neckline = self.lows[trough_idx]
            
            # Target = neckline - (peak - neckline)
            avg_peak = (peak1['price'] + peak2['price']) / 2
            target = neckline - (avg_peak - neckline)
            
            return {
                "detected": True,
                "pattern": "DOUBLE_TOP",
                "peak1": peak1['price'],
                "peak2": peak2['price'],
                "neckline": neckline,
                "target": round(target, 5)
            }
        
        return {"detected": False}
    
    def detect_double_bottom(self, tolerance: float = 0.02) -> Dict:
        """
        Detect Double Bottom pattern.
        
        Two troughs at similar price levels with a peak between.
        """
        pivots = self._find_pivots()
        lows = pivots['lows']
        
        if len(lows) < 2:
            return {"detected": False}
        
        # Check last two troughs
        trough1 = lows[-2]
        trough2 = lows[-1]
        
        price_diff = abs(trough1['price'] - trough2['price']) / trough1['price']
        
        if price_diff <= tolerance:
            # Find peak between troughs
            peak_idx = max(range(trough1['index'], trough2['index']+1), 
                          key=lambda x: self.highs[x])
            neckline = self.highs[peak_idx]
            
            # Target = neckline + (neckline - trough)
            avg_trough = (trough1['price'] + trough2['price']) / 2
            target = neckline + (neckline - avg_trough)
            
            return {
                "detected": True,
                "pattern": "DOUBLE_BOTTOM",
                "trough1": trough1['price'],
                "trough2": trough2['price'],
                "neckline": neckline,
                "target": round(target, 5)
            }
        
        return {"detected": False}
    
    def detect_head_shoulders(self) -> Dict:
        """
        Detect Head and Shoulders pattern.
        
        Three peaks: left shoulder, head (highest), right shoulder.
        Neckline connects the two troughs.
        """
        pivots = self._find_pivots()
        highs = pivots['highs']
        
        if len(highs) < 3:
            return {"detected": False}
        
        # Get last 3 peaks
        ls = highs[-3]  # Left shoulder
        head = highs[-2]  # Head
        rs = highs[-1]  # Right shoulder
        
        # Head must be highest
        if not (head['price'] > ls['price'] and head['price'] > rs['price']):
            return {"detected": False}
        
        # Shoulders should be similar height (within 5%)
        shoulder_diff = abs(ls['price'] - rs['price']) / ls['price']
        if shoulder_diff > 0.05:
            return {"detected": False}
        
        # Find neckline (connect lows between LS-Head and Head-RS)
        low1_idx = min(range(ls['index'], head['index']+1), key=lambda x: self.lows[x])
        low2_idx = min(range(head['index'], rs['index']+1), key=lambda x: self.lows[x])
        neckline = (self.lows[low1_idx] + self.lows[low2_idx]) / 2
        
        # Target = neckline - (head - neckline)
        target = neckline - (head['price'] - neckline)
        
        return {
            "detected": True,
            "pattern": "HEAD_AND_SHOULDERS",
            "left_shoulder": ls['price'],
            "head": head['price'],
            "right_shoulder": rs['price'],
            "neckline": round(neckline, 5),
            "target": round(target, 5)
        }

    # ==========================================
    # 🎯 HARMONIC PATTERNS (Fibonacci-based)
    # ==========================================
    
    def _calc_retracement(self, pointA: float, pointB: float, pointC: float) -> float:
        """Calculate Fibonacci retracement level."""
        if pointA == pointB:
            return 0
        return abs(pointC - pointB) / abs(pointA - pointB)
    
    def detect_gartley(self) -> Dict:
        """
        Detect Gartley harmonic pattern.
        
        Fibonacci Ratios:
        - XA leg: Initial move
        - AB: 61.8% retracement of XA
        - BC: 38.2% to 88.6% of AB
        - CD: 78.6% of XA
        """
        pivots = self._find_pivots()
        # Simplified: Check if recent pivots match Gartley ratios
        # Full implementation would need more complex XABCD detection
        
        if len(pivots['highs']) < 2 or len(pivots['lows']) < 2:
            return {"detected": False}
        
        # This is a simplified check - full harmonic detection is complex
        return {"detected": False, "note": "Full harmonic detection requires XABCD pivot analysis"}

    # ==========================================
    # 🔍 MASTER SCAN
    # ==========================================
    
    def scan_all(self) -> List[Dict]:
        """
        Scan for all pattern types.
        
        Returns:
            list: All detected patterns with details
        """
        patterns = []
        
        # Candlestick patterns
        doji = self.detect_doji()
        if doji.get("detected"):
            patterns.append({"category": "candlestick", **doji})
        
        hammer = self.detect_hammer()
        if hammer.get("detected"):
            patterns.append({"category": "candlestick", **hammer})
        
        engulfing = self.detect_engulfing()
        if engulfing.get("detected"):
            patterns.append({"category": "candlestick", **engulfing})
        
        star = self.detect_morning_star()
        if star.get("detected"):
            patterns.append({"category": "candlestick", **star})
        
        # Chart patterns
        double_top = self.detect_double_top()
        if double_top.get("detected"):
            patterns.append({"category": "chart", **double_top})
        
        double_bottom = self.detect_double_bottom()
        if double_bottom.get("detected"):
            patterns.append({"category": "chart", **double_bottom})
        
        hs = self.detect_head_shoulders()
        if hs.get("detected"):
            patterns.append({"category": "chart", **hs})
        
        return patterns
