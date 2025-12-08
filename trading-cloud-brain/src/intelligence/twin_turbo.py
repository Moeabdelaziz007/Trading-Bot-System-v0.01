"""
🚀 TwinTurbo - Unified Market Intelligence Engine
Combines AEXI (Exhaustion Detection) + Dream (Chaos Analysis)

The "Twin-Turbo" system provides a comprehensive market intelligence layer:
- AEXI: Identifies when price has moved too far, too fast (reversal signals)
- Dream: Detects market structure breakdown and chaos regimes

Usage:
    turbo = TwinTurbo(candle_data)
    result = turbo.analyze()
    # result = {aexi: {...}, dream: {...}, combined_signal: "..."}
"""

import math
from typing import List, Dict


class TwinTurbo:
    """
    Unified Market Intelligence combining AEXI + Dream engines.
    """
    
    # AEXI Configuration
    AEXI_SMA_PERIOD = 20
    AEXI_ATR_PERIOD = 14
    AEXI_VOLUME_PERIOD = 20
    AEXI_THRESHOLD = 80
    
    # Dream Configuration
    DREAM_LOOKBACK = 30
    DREAM_NUM_BINS = 10
    DREAM_THRESHOLD = 70
    
    def __init__(self, data: List[Dict]):
        """
        :param data: List of OHLCV dicts [{'open', 'high', 'low', 'close', 'volume'}, ...]
        """
        self.data = data
        self.closes = [d['close'] for d in data]
        self.highs = [d.get('high', d['close']) for d in data]
        self.lows = [d.get('low', d['close']) for d in data]
        self.volumes = [d.get('volume', 0) for d in data]
        
        # Pre-calculate returns
        self.returns = []
        for i in range(1, len(self.closes)):
            if self.closes[i-1] > 0:
                self.returns.append((self.closes[i] - self.closes[i-1]) / self.closes[i-1])

    # ==========================================
    # ⚡ AEXI CALCULATIONS
    # ==========================================
    
    def _calc_exh(self) -> Dict:
        """Z-Score Exhaustion."""
        if len(self.closes) < self.AEXI_SMA_PERIOD:
            return {"normalized": 0, "signal": "NEUTRAL"}
        
        recent = self.closes[-self.AEXI_SMA_PERIOD:]
        sma = sum(recent) / len(recent)
        variance = sum((x - sma) ** 2 for x in recent) / len(recent)
        std_dev = math.sqrt(variance) if variance > 0 else 0.0001
        
        z_score = (self.closes[-1] - sma) / std_dev
        normalized = min(100, max(0, (z_score + 3) / 6 * 100))
        
        signal = "NEUTRAL"
        if z_score > 2.0: signal = "OVERBOUGHT"
        elif z_score < -2.0: signal = "OVERSOLD"
        
        return {"z_score": round(z_score, 3), "normalized": round(normalized, 2), "signal": signal}
    
    def _calc_vaf(self) -> Dict:
        """Velocity/ATR Factor."""
        if len(self.closes) < max(self.AEXI_ATR_PERIOD + 1, 6):
            return {"normalized": 0}
        
        roc = (self.closes[-1] - self.closes[-6]) / self.closes[-6] * 100
        
        tr_sum = 0
        for i in range(-self.AEXI_ATR_PERIOD, 0):
            tr = max(self.highs[i] - self.lows[i], 
                    abs(self.highs[i] - self.closes[i-1]),
                    abs(self.lows[i] - self.closes[i-1]))
            tr_sum += tr
        atr = tr_sum / self.AEXI_ATR_PERIOD
        atr_pct = (atr / self.closes[-1]) * 100 if self.closes[-1] > 0 else 0.0001
        vaf_ratio = abs(roc) / atr_pct if atr_pct > 0 else 0
        normalized = min(100, max(0, vaf_ratio / 3 * 100))
        
        return {"roc": round(roc, 3), "atr": round(atr, 4), "normalized": round(normalized, 2)}
    
    def _calc_svp(self) -> Dict:
        """Surveillance Volume Proxy."""
        if len(self.volumes) < self.AEXI_VOLUME_PERIOD:
            return {"normalized": 50}
        
        vol_sma = sum(self.volumes[-self.AEXI_VOLUME_PERIOD:]) / self.AEXI_VOLUME_PERIOD
        vol_ratio = self.volumes[-1] / vol_sma if vol_sma > 0 else 1
        normalized = min(100, max(0, vol_ratio / 2 * 100))
        
        return {"ratio": round(vol_ratio, 3), "normalized": round(normalized, 2), "is_spike": vol_ratio > 1.5}
    
    def get_aexi(self) -> Dict:
        """Calculate AEXI score."""
        exh = self._calc_exh()
        vaf = self._calc_vaf()
        svp = self._calc_svp()
        
        score = 0.4 * exh['normalized'] + 0.3 * vaf['normalized'] + 0.3 * svp['normalized']
        
        signal = "NEUTRAL"
        direction = "NONE"
        if score >= self.AEXI_THRESHOLD:
            if exh['signal'] == "OVERBOUGHT":
                signal, direction = "REVERSAL_DOWN", "SHORT"
            elif exh['signal'] == "OVERSOLD":
                signal, direction = "REVERSAL_UP", "LONG"
            else:
                signal = "HIGH_EXHAUSTION"
        
        return {
            "score": round(score, 2),
            "signal": signal,
            "direction": direction,
            "triggered": score >= self.AEXI_THRESHOLD,
            "components": {"exh": exh, "vaf": vaf, "svp": svp}
        }

    # ==========================================
    # 🌀 DREAM CALCULATIONS
    # ==========================================
    
    def _calc_entropy(self) -> Dict:
        """Shannon Entropy."""
        if len(self.returns) < self.DREAM_LOOKBACK:
            return {"normalized": 50}
        
        recent = self.returns[-self.DREAM_LOOKBACK:]
        min_ret, max_ret = min(recent), max(recent)
        range_ret = max_ret - min_ret if max_ret != min_ret else 0.0001
        
        bins = [0] * self.DREAM_NUM_BINS
        for r in recent:
            idx = min(int((r - min_ret) / range_ret * self.DREAM_NUM_BINS), self.DREAM_NUM_BINS - 1)
            bins[idx] += 1
        
        n = len(recent)
        entropy = 0.0
        for count in bins:
            if count > 0:
                p = count / n
                entropy -= p * math.log2(p)
        
        max_entropy = math.log2(self.DREAM_NUM_BINS)
        normalized = (entropy / max_entropy) * 100 if max_entropy > 0 else 50
        
        return {"raw": round(entropy, 4), "normalized": round(normalized, 2)}
    
    def _calc_fractal(self) -> Dict:
        """Fractal Dimension approximation."""
        if len(self.closes) < self.DREAM_LOOKBACK:
            return {"normalized": 50}
        
        series = self.closes[-self.DREAM_LOOKBACK:]
        sign_changes = 0
        for i in range(1, len(series) - 1):
            if (series[i] - series[i-1]) * (series[i+1] - series[i]) < 0:
                sign_changes += 1
        
        max_changes = len(series) - 2
        fd = 1.0 + (sign_changes / max_changes) if max_changes > 0 else 1.5
        normalized = min(100, max(0, (fd - 1.0) * 100))
        
        return {"fd": round(fd, 4), "normalized": round(normalized, 2)}
    
    def _calc_hurst(self) -> Dict:
        """Hurst Exponent (R/S Analysis)."""
        if len(self.returns) < self.DREAM_LOOKBACK:
            return {"normalized": 50, "behavior": "RANDOM"}
        
        series = self.returns[-self.DREAM_LOOKBACK:]
        n = len(series)
        mean = sum(series) / n
        
        cumsum = []
        running = 0
        for s in series:
            running += s - mean
            cumsum.append(running)
        
        R = max(cumsum) - min(cumsum)
        variance = sum((x - mean) ** 2 for x in series) / n
        S = math.sqrt(variance) if variance > 0 else 0.0001
        RS = R / S if S > 0 else 0
        
        H = math.log(RS) / math.log(n) if RS > 0 and n > 1 else 0.5
        H = min(1.0, max(0.0, H))
        
        behavior = "TRENDING" if H > 0.6 else ("MEAN_REVERTING" if H < 0.4 else "RANDOM")
        normalized = (1 - abs(H - 0.5) * 2) * 100
        
        return {"H": round(H, 4), "behavior": behavior, "normalized": round(normalized, 2)}
    
    def _calc_vol_dispersion(self) -> Dict:
        """Volume Coefficient of Variation."""
        if len(self.volumes) < self.DREAM_LOOKBACK:
            return {"normalized": 50}
        
        recent = self.volumes[-self.DREAM_LOOKBACK:]
        mean = sum(recent) / len(recent)
        if mean <= 0:
            return {"normalized": 50}
        
        variance = sum((v - mean) ** 2 for v in recent) / len(recent)
        cv = math.sqrt(variance) / mean
        normalized = min(100, cv * 100)
        
        return {"cv": round(cv, 4), "normalized": round(normalized, 2)}
    
    def get_dream(self) -> Dict:
        """Calculate Dream score."""
        entropy = self._calc_entropy()
        fractal = self._calc_fractal()
        hurst = self._calc_hurst()
        vol_disp = self._calc_vol_dispersion()
        
        score = (0.30 * entropy['normalized'] + 0.25 * fractal['normalized'] + 
                0.25 * hurst['normalized'] + 0.20 * vol_disp['normalized'])
        
        if score >= 80:
            regime, signal = "CHAOS", "AVOID_TRADING"
        elif score >= self.DREAM_THRESHOLD:
            regime, signal = "UNSTABLE", "CAUTION"
        elif score <= 30:
            regime, signal = "ORDERED", "TREND_FOLLOW"
        else:
            regime, signal = "NORMAL", "NEUTRAL"
        
        return {
            "score": round(score, 2),
            "regime": regime,
            "signal": signal,
            "chaotic": score >= self.DREAM_THRESHOLD,
            "components": {"entropy": entropy, "fractal": fractal, "hurst": hurst, "vol_dispersion": vol_disp}
        }

    # ==========================================
    # 🎯 COMBINED ANALYSIS
    # ==========================================
    
    def analyze(self) -> Dict:
        """
        Full Twin-Turbo analysis.
        Returns AEXI, Dream, and a combined trading signal.
        """
        aexi = self.get_aexi()
        dream = self.get_dream()
        
        # Combined signal logic
        combined_signal = "NEUTRAL"
        confidence = 0.5
        
        if dream['chaotic']:
            combined_signal = "WAIT"
            confidence = 0.3
        elif aexi['triggered']:
            combined_signal = aexi['direction'] if aexi['direction'] != "NONE" else aexi['signal']
            confidence = 0.75 if not dream['chaotic'] else 0.5
        elif dream['regime'] == "ORDERED":
            combined_signal = "TREND_FOLLOW"
            confidence = 0.6
        
        return {
            "aexi": aexi,
            "dream": dream,
            "combined_signal": combined_signal,
            "confidence": round(confidence, 2)
        }
