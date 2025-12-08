"""
🧠 TradingBrain - Unified Strategy Engine
Combines Scalping + Swing trading strategies with shared analytics.

The brain provides two operating modes:
- SCALP: Short-term (M5/M15), high frequency, tight stops
- SWING: Long-term (H4/D1), trend following, wide stops

Usage:
    brain = TradingBrain(candle_data, mode="SCALP")
    signal = brain.analyze()
"""

import math
from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class Strategy(ABC):
    """Abstract base for trading strategies."""
    
    @abstractmethod
    def analyze(self, data: List[Dict]) -> Dict:
        pass


class TradingBrain:
    """
    Unified Trading Strategy Engine.
    Supports multiple modes with shared indicator toolkit.
    """
    
    # Common Configuration
    ATR_PERIOD = 14
    
    # Scalping Mode Config
    SCALP_ATR_SL_MULT = 1.0
    SCALP_ATR_TP_MULT = 7.0  # 1:7 R:R
    SCALP_MIN_SCORE = 10
    
    # Swing Mode Config  
    SWING_RSI_PERIOD = 14
    SWING_ADX_PERIOD = 14
    SWING_ADX_THRESHOLD = 25
    SWING_VOLUME_SURGE = 1.2
    
    def __init__(self, data: List[Dict], mode: str = "SCALP"):
        """
        :param data: OHLCV data
        :param mode: "SCALP" or "SWING"
        """
        self.data = data
        self.mode = mode.upper()
        
    # ==========================================
    # 🛠️ SHARED INDICATORS
    # ==========================================
    
    def _calc_atr(self, period: int = None) -> Optional[float]:
        period = period or self.ATR_PERIOD
        if len(self.data) < period + 1:
            return None
        tr_sum = 0
        for i in range(-period, 0):
            h, l = self.data[i]['high'], self.data[i]['low']
            pc = self.data[i-1]['close']
            tr_sum += max(h - l, abs(h - pc), abs(l - pc))
        return tr_sum / period

    def _calc_sma(self, period: int) -> Optional[float]:
        if len(self.data) < period:
            return None
        return sum(d['close'] for d in self.data[-period:]) / period

    def _calc_ema(self, period: int) -> Optional[float]:
        if len(self.data) < period:
            return None
        closes = [d['close'] for d in self.data]
        mult = 2 / (period + 1)
        ema = closes[0]
        for c in closes[1:]:
            ema = (c - ema) * mult + ema
        return ema

    def _calc_rsi(self, period: int = None) -> float:
        period = period or self.SWING_RSI_PERIOD
        if len(self.data) < period + 1:
            return 50.0
        gains, losses = 0, 0
        for i in range(-period, 0):
            change = self.data[i]['close'] - self.data[i-1]['close']
            if change > 0: gains += change
            else: losses += abs(change)
        avg_gain, avg_loss = gains / period, losses / period
        if avg_loss == 0: return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def _calc_adx(self, period: int = None) -> tuple:
        period = period or self.SWING_ADX_PERIOD
        if len(self.data) < period * 2:
            return 0, 0, 0
        tr_list, plus_dm, minus_dm = [], [], []
        for i in range(-period * 2 + 1, 0):
            h, l = self.data[i]['high'], self.data[i]['low']
            ph, pl, pc = self.data[i-1]['high'], self.data[i-1]['low'], self.data[i-1]['close']
            tr_list.append(max(h - l, abs(h - pc), abs(l - pc)))
            plus_dm.append(max(h - ph, 0) if (h - ph) > (pl - l) else 0)
            minus_dm.append(max(pl - l, 0) if (pl - l) > (h - ph) else 0)
        atr = sum(tr_list[-period:]) / period
        plus_di = (sum(plus_dm[-period:]) / atr) * 100 if atr > 0 else 0
        minus_di = (sum(minus_dm[-period:]) / atr) * 100 if atr > 0 else 0
        di_sum = plus_di + minus_di
        dx = (abs(plus_di - minus_di) / di_sum) * 100 if di_sum > 0 else 0
        return dx, plus_di, minus_di

    # ==========================================
    # 🔥 SCALPING ANALYSIS
    # ==========================================
    
    def _scalp_analyze(self) -> Dict:
        """Scalping mode analysis with 14 tools."""
        atr = self._calc_atr()
        if not atr:
            return {"signal": "NO_DATA", "score": 0}
        
        current = self.data[-1]['close']
        sr = self._calc_sr()
        rejection = self._detect_rejection()
        supertrend = self._calc_supertrend()
        footprint = self._calc_footprint()
        macd = self._calc_macd()
        stoch = self._calc_stochastic()
        
        buy_score, sell_score = 0, 0
        
        # Score accumulation
        if supertrend['trend'] == 1: buy_score += 2
        elif supertrend['trend'] == -1: sell_score += 2
        
        if current < sr['support'] * 1.01: buy_score += 2
        if current > sr['resistance'] * 0.99: sell_score += 2
        
        if rejection['bullish']: buy_score += 1
        if rejection['bearish']: sell_score += 1
        
        if macd['histogram'] > 0: buy_score += 1
        if macd['histogram'] < 0: sell_score += 1
        
        if stoch['signal'] == 'OVERSOLD': buy_score += 1
        if stoch['signal'] == 'OVERBOUGHT': sell_score += 1
        
        if footprint > 0.1: buy_score += 1
        if footprint < -0.1: sell_score += 1
        
        # Determine signal
        signal = "NEUTRAL"
        direction = "NONE"
        if buy_score >= self.SCALP_MIN_SCORE:
            signal = "BUY"
            direction = "LONG"
        elif sell_score >= self.SCALP_MIN_SCORE:
            signal = "SELL"
            direction = "SHORT"
        
        # Calculate stops
        stops = None
        if signal != "NEUTRAL":
            sl_dist = atr * self.SCALP_ATR_SL_MULT
            tp_dist = atr * self.SCALP_ATR_TP_MULT
            if direction == "LONG":
                stops = {"entry": current, "sl": current - sl_dist, "tp": current + tp_dist}
            else:
                stops = {"entry": current, "sl": current + sl_dist, "tp": current - tp_dist}
        
        return {
            "signal": signal,
            "direction": direction,
            "buy_score": buy_score,
            "sell_score": sell_score,
            "stops": stops,
            "atr": round(atr, 5),
            "rr_ratio": self.SCALP_ATR_TP_MULT / self.SCALP_ATR_SL_MULT
        }

    def _calc_sr(self) -> Dict:
        lookback = min(20, len(self.data))
        recent = self.data[-lookback:]
        return {
            "support": min(d['low'] for d in recent),
            "resistance": max(d['high'] for d in recent)
        }

    def _detect_rejection(self) -> Dict:
        if len(self.data) < 2:
            return {"bullish": False, "bearish": False}
        c = self.data[-1]
        body = abs(c['close'] - c['open'])
        total = c['high'] - c['low']
        if total == 0:
            return {"bullish": False, "bearish": False}
        upper = c['high'] - max(c['close'], c['open'])
        lower = min(c['close'], c['open']) - c['low']
        return {
            "bullish": lower > body * 1.5 and lower > upper,
            "bearish": upper > body * 1.5 and upper > lower
        }

    def _calc_supertrend(self, mult: float = 3.0) -> Dict:
        atr = self._calc_atr(10)
        if not atr:
            return {"trend": 0, "value": 0}
        c = self.data[-1]
        hl2 = (c['high'] + c['low']) / 2
        upper = hl2 + (mult * atr)
        lower = hl2 - (mult * atr)
        trend = 1 if c['close'] > lower else (-1 if c['close'] < upper else 0)
        return {"trend": trend, "value": lower if trend == 1 else upper}

    def _calc_footprint(self) -> float:
        if len(self.data) < 5:
            return 0
        buy_v = sum(d['volume'] for d in self.data[-5:] if d['close'] > d['open'])
        sell_v = sum(d['volume'] for d in self.data[-5:] if d['close'] <= d['open'])
        total = buy_v + sell_v
        return (buy_v - sell_v) / total if total > 0 else 0

    def _calc_macd(self) -> Dict:
        ema12 = self._calc_ema(12)
        ema26 = self._calc_ema(26)
        if not ema12 or not ema26:
            return {"line": 0, "signal": 0, "histogram": 0}
        macd_line = ema12 - ema26
        return {"line": macd_line, "signal": 0, "histogram": macd_line}

    def _calc_stochastic(self, period: int = 14) -> Dict:
        if len(self.data) < period:
            return {"k": 50, "signal": "NEUTRAL"}
        recent = self.data[-period:]
        low_min = min(d['low'] for d in recent)
        high_max = max(d['high'] for d in recent)
        current = self.data[-1]['close']
        if high_max == low_min:
            k = 50
        else:
            k = ((current - low_min) / (high_max - low_min)) * 100
        signal = "OVERBOUGHT" if k > 80 else ("OVERSOLD" if k < 20 else "NEUTRAL")
        return {"k": round(k, 2), "signal": signal}

    # ==========================================
    # 🏦 SWING ANALYSIS
    # ==========================================
    
    def _swing_analyze(self) -> Dict:
        """Swing mode with golden/death cross."""
        if len(self.data) < 200:
            return {"signal": "NO_DATA", "recommendation": "WAIT"}
        
        ema50 = self._calc_ema(50)
        sma200 = self._calc_sma(200)
        rsi = self._calc_rsi()
        adx, plus_di, minus_di = self._calc_adx()
        
        is_golden = ema50 > sma200
        is_death = ema50 < sma200
        
        last_vol = self.data[-1]['volume']
        avg_vol = sum(d['volume'] for d in self.data[-20:]) / 20
        vol_surge = last_vol > (avg_vol * self.SWING_VOLUME_SURGE)
        
        strong_trend = adx > self.SWING_ADX_THRESHOLD
        
        buy_score, sell_score = 0, 0
        if is_golden:
            buy_score += 1
            if vol_surge: buy_score += 1
            if rsi > 50: buy_score += 1
            if strong_trend and plus_di > minus_di: buy_score += 1
        if is_death:
            sell_score += 1
            if vol_surge: sell_score += 1
            if rsi < 50: sell_score += 1
            if strong_trend and minus_di > plus_di: sell_score += 1
        
        signal = "NEUTRAL"
        recommendation = "HOLD"
        if buy_score >= 3:
            signal = "STRONG_GOLDEN_CROSS"
            recommendation = "BUY_LONG_TERM"
        elif buy_score >= 2:
            signal = "WEAK_GOLDEN_CROSS"
            recommendation = "ACCUMULATE"
        elif sell_score >= 3:
            signal = "STRONG_DEATH_CROSS"
            recommendation = "SELL_LONG_TERM"
        elif sell_score >= 2:
            signal = "WEAK_DEATH_CROSS"
            recommendation = "REDUCE"
        
        return {
            "signal": signal,
            "recommendation": recommendation,
            "ema50": round(ema50, 5) if ema50 else 0,
            "sma200": round(sma200, 5) if sma200 else 0,
            "rsi": round(rsi, 2),
            "adx": round(adx, 2),
            "vol_surge": vol_surge
        }

    # ==========================================
    # 🎯 MAIN ENTRY POINT
    # ==========================================
    
    def analyze(self) -> Dict:
        """Main analysis entry point."""
        if self.mode == "SCALP":
            return self._scalp_analyze()
        elif self.mode == "SWING":
            return self._swing_analyze()
        else:
            return {"error": f"Unknown mode: {self.mode}"}
