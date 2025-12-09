"""
⚡ Volatility Spiker - Regime Change Detector
محفز التقلبات - كاشف تغيير نظام السوق

AlphaAxiom Mini-Agent Swarm
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Hypothesis:
    Rapid ATR expansion signals a regime change and 
    high-probability entry/exit points.
    
    الفرضية: التوسع السريع في ATR يشير إلى تغيير نظام السوق
    ونقاط دخول/خروج عالية الاحتمالية.

Indicators:
    - ATR(14) increase > 50% in 3 candles
    - Bollinger Band Width expansion
    - Keltner Channel squeeze/expansion

Entry Trigger:
    ATR increases 50%+ in 3 bars with clear directional bias
"""

from typing import Optional, Dict, Any, List
import math
from .base_mini_agent import (
    BaseMiniAgent,
    AgentSignal,
    SignalType,
)


class VolatilitySpiker(BaseMiniAgent):
    """
    ⚡ Volatility Spiker Agent
    Tests the ATR expansion regime change hypothesis
    
    يختبر فرضية تغيير النظام عند توسع ATR
    """
    
    # Agent configuration
    ATR_PERIOD = 14
    ATR_EXPANSION_THRESHOLD = 0.5  # 50% increase
    ATR_LOOKBACK = 3  # Candles to check for expansion
    BB_PERIOD = 20
    BB_STD = 2
    KELTNER_PERIOD = 20
    KELTNER_MULTIPLIER = 1.5
    
    @property
    def hypothesis(self) -> str:
        return (
            "Regime change: ATR expanding >50% in 3 bars signals "
            "major volatility shift and directional opportunity."
        )
    
    @property
    def timeframes(self) -> List[str]:
        return ["15M", "1H"]
    
    def __init__(self, env=None):
        super().__init__(env)
        self.watchlist = ["BTCUSD", "ETHUSD", "SPY", "XAUUSD"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 INDICATOR CALCULATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_indicators(self, ohlcv: List[Dict]) -> Dict[str, Any]:
        """Calculate volatility-based indicators"""
        if len(ohlcv) < self.ATR_PERIOD + self.ATR_LOOKBACK + 5:
            return {}
        
        closes = [c["close"] for c in ohlcv]
        highs = [c["high"] for c in ohlcv]
        lows = [c["low"] for c in ohlcv]
        
        # Calculate ATR series
        atr_series = self._calculate_atr_series(highs, lows, closes)
        
        # ATR expansion analysis
        if len(atr_series) >= self.ATR_LOOKBACK + 1:
            current_atr = atr_series[-1]
            past_atr = atr_series[-(self.ATR_LOOKBACK + 1)]
            atr_change = (current_atr - past_atr) / past_atr if past_atr > 0 else 0
        else:
            current_atr = atr_series[-1] if atr_series else 0
            atr_change = 0
        
        # Bollinger Band Width
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger(
            closes, self.BB_PERIOD, self.BB_STD
        )
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0
        
        # Keltner Channel
        kc_upper, kc_middle, kc_lower = self._calculate_keltner(
            closes, highs, lows
        )
        
        # Squeeze detection (BB inside KC = squeeze)
        in_squeeze = bb_upper < kc_upper and bb_lower > kc_lower
        squeeze_release = not in_squeeze  # Was in squeeze, now out
        
        # Directional bias from price movement
        current_price = closes[-1]
        price_3_back = closes[-(self.ATR_LOOKBACK + 1)]
        price_direction = "UP" if current_price > price_3_back else "DOWN"
        
        # Detect volatility spike
        volatility_spike = atr_change >= self.ATR_EXPANSION_THRESHOLD
        
        return {
            "current_atr": current_atr,
            "atr_change": atr_change,
            "atr_change_pct": atr_change * 100,
            "volatility_spike": volatility_spike,
            "bb_width": bb_width,
            "bb_upper": bb_upper,
            "bb_lower": bb_lower,
            "kc_upper": kc_upper,
            "kc_lower": kc_lower,
            "in_squeeze": in_squeeze,
            "squeeze_release": squeeze_release,
            "price_direction": price_direction,
            "price_momentum": (current_price - price_3_back) / price_3_back * 100,
        }
    
    def _calculate_atr_series(
        self, 
        highs: List[float], 
        lows: List[float], 
        closes: List[float]
    ) -> List[float]:
        """Calculate Average True Range series"""
        if len(highs) < 2:
            return [0]
        
        tr_list = []
        
        for i in range(1, len(highs)):
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
        
        if len(tr_list) < self.ATR_PERIOD:
            return [sum(tr_list) / len(tr_list)] if tr_list else [0]
        
        # Calculate ATR using Wilder's smoothing
        atr = [sum(tr_list[:self.ATR_PERIOD]) / self.ATR_PERIOD]
        
        for i in range(self.ATR_PERIOD, len(tr_list)):
            atr.append(
                (atr[-1] * (self.ATR_PERIOD - 1) + tr_list[i]) / self.ATR_PERIOD
            )
        
        return atr
    
    def _calculate_bollinger(
        self, 
        prices: List[float], 
        period: int, 
        num_std: float
    ) -> tuple:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return (prices[-1], prices[-1], prices[-1])
        
        middle = sum(prices[-period:]) / period
        std = self._calculate_std(prices[-period:])
        
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
        return (upper, middle, lower)
    
    def _calculate_keltner(
        self, 
        closes: List[float], 
        highs: List[float], 
        lows: List[float]
    ) -> tuple:
        """Calculate Keltner Channels"""
        if len(closes) < self.KELTNER_PERIOD:
            return (closes[-1], closes[-1], closes[-1])
        
        # EMA for middle
        ema = self._calculate_ema(closes, self.KELTNER_PERIOD)
        middle = ema[-1] if ema else closes[-1]
        
        # ATR for bands
        atr_series = self._calculate_atr_series(highs, lows, closes)
        atr = atr_series[-1] if atr_series else 0
        
        upper = middle + (self.KELTNER_MULTIPLIER * atr)
        lower = middle - (self.KELTNER_MULTIPLIER * atr)
        
        return (upper, middle, lower)
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices.copy()
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎯 SIGNAL GENERATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def analyze_market(
        self, 
        symbol: str, 
        market_data: Dict[str, Any]
    ) -> Optional[AgentSignal]:
        """
        Analyze market for volatility regime changes
        
        Entry conditions:
        - ATR increased 50%+ in last 3 candles
        - Clear directional bias from price movement
        - Optional: Squeeze release for confirmation
        """
        indicators = market_data.get("indicators", {})
        current_price = market_data.get("current_price", 0)
        
        if not indicators or current_price == 0:
            return None
        
        # Check for volatility spike
        volatility_spike = indicators.get("volatility_spike", False)
        
        if not volatility_spike:
            return None
        
        # Get direction and generate signal
        direction = indicators.get("price_direction", "UP")
        atr_change_pct = indicators.get("atr_change_pct", 0)
        squeeze_release = indicators.get("squeeze_release", False)
        
        signal_type = None
        
        if direction == "UP":
            signal_type = SignalType.BUY
            reasoning = (
                f"Volatility expansion: ATR +{atr_change_pct:.1f}%, "
                f"bullish momentum, squeeze_release={squeeze_release}"
            )
        else:
            signal_type = SignalType.SELL
            reasoning = (
                f"Volatility expansion: ATR +{atr_change_pct:.1f}%, "
                f"bearish momentum, squeeze_release={squeeze_release}"
            )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            atr_change_pct, squeeze_release
        )
        
        # Wider targets for volatility plays
        stop_loss, take_profit = self._calculate_volatility_targets(
            current_price, signal_type, indicators
        )
        
        return AgentSignal(
            signal_id=self.generate_signal_id(),
            agent_name=self._agent_name,
            timestamp=self.get_current_timestamp(),
            symbol=symbol,
            signal_type=signal_type,
            confidence=confidence,
            entry_price=current_price,
            hypothesis=self.hypothesis,
            market_regime=market_data.get("market_regime"),
            stop_loss=stop_loss,
            take_profit=take_profit,
            indicators=indicators,
            reasoning=reasoning,
        )
    
    def _calculate_confidence(
        self, 
        atr_change_pct: float, 
        squeeze_release: bool
    ) -> float:
        """Calculate confidence based on ATR change and squeeze"""
        # ATR contribution (higher expansion = higher confidence)
        atr_score = min(atr_change_pct / 100, 1.0) * 0.6
        
        # Squeeze release bonus
        squeeze_score = 0.4 if squeeze_release else 0.2
        
        confidence = atr_score + squeeze_score
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_volatility_targets(
        self, 
        price: float, 
        signal_type: SignalType,
        indicators: Dict
    ) -> tuple:
        """Calculate wider targets for volatility trades"""
        atr = indicators.get("current_atr", price * 0.02)
        
        # Use 1.5 ATR for stop, 3 ATR for target (2:1 R:R)
        if signal_type == SignalType.BUY:
            stop_loss = price - (1.5 * atr)
            take_profit = price + (3 * atr)
        else:
            stop_loss = price + (1.5 * atr)
            take_profit = price - (3 * atr)
        
        return (stop_loss, take_profit)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏭 FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_volatility_spiker(env=None) -> VolatilitySpiker:
    """Factory function to create VolatilitySpiker agent"""
    return VolatilitySpiker(env)
