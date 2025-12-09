"""
🏃 Momentum Scout - Breakout Continuation Detector
كشاف الزخم - كاشف استمرار الاختراقات

AlphaAxiom Mini-Agent Swarm
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Hypothesis:
    Strong, sudden price breakouts on low timeframes (1M/5M) 
    will continue for the next 5-10 candles.
    
    الفرضية: الاختراقات القوية المفاجئة في الأطر الزمنية المنخفضة
    ستستمر لمدة 5-10 شموع قادمة.

Indicators:
    - EMA(9, 21) crossover
    - Volume Spike (> 2x average)
    - ADX > 25 (strong trend)
    - Price crosses EMA21

Entry Trigger:
    Price crosses above EMA21 with 2x volume spike AND ADX > 25
"""

from typing import Optional, Dict, Any, List
from .base_mini_agent import (
    BaseMiniAgent,
    AgentSignal,
    SignalType,
)


class MomentumScout(BaseMiniAgent):
    """
    🏃 Momentum Scout Agent
    Tests the breakout continuation hypothesis
    
    يختبر فرضية استمرار الاختراقات
    """
    
    # Agent configuration
    EMA_FAST = 9
    EMA_SLOW = 21
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25
    VOLUME_MULTIPLIER = 2.0
    CONTINUATION_CANDLES = 5  # Expected continuation period
    
    @property
    def hypothesis(self) -> str:
        return (
            "Strong breakouts continue: When price crosses EMA21 with "
            "2x volume spike and ADX > 25, momentum continues for 5-10 candles."
        )
    
    @property
    def timeframes(self) -> List[str]:
        return ["1M", "5M"]
    
    def __init__(self, env=None):
        super().__init__(env)
        self.watchlist = ["BTCUSD", "ETHUSD", "SPY", "EURUSD", "XAUUSD"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 INDICATOR CALCULATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_indicators(self, ohlcv: List[Dict]) -> Dict[str, Any]:
        """
        Calculate momentum indicators
        
        Returns:
            Dictionary with EMA, ADX, and volume metrics
        """
        if len(ohlcv) < self.EMA_SLOW + 10:
            return {}
        
        closes = [c["close"] for c in ohlcv]
        volumes = [c["volume"] for c in ohlcv]
        highs = [c["high"] for c in ohlcv]
        lows = [c["low"] for c in ohlcv]
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(closes, self.EMA_FAST)
        ema_slow = self._calculate_ema(closes, self.EMA_SLOW)
        
        # Calculate ADX
        adx = self._calculate_adx(highs, lows, closes, self.ADX_PERIOD)
        
        # Volume analysis
        avg_volume = sum(volumes[-20:]) / 20
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # EMA crossover detection
        prev_close = closes[-2]
        curr_close = closes[-1]
        prev_ema_slow = ema_slow[-2] if len(ema_slow) > 1 else ema_slow[-1]
        curr_ema_slow = ema_slow[-1]
        
        # Bullish crossover: price crosses above EMA21
        bullish_crossover = prev_close <= prev_ema_slow and curr_close > curr_ema_slow
        # Bearish crossover: price crosses below EMA21
        bearish_crossover = prev_close >= prev_ema_slow and curr_close < curr_ema_slow
        
        return {
            "ema_fast": ema_fast[-1],
            "ema_slow": ema_slow[-1],
            "adx": adx,
            "avg_volume": avg_volume,
            "current_volume": current_volume,
            "volume_ratio": volume_ratio,
            "bullish_crossover": bullish_crossover,
            "bearish_crossover": bearish_crossover,
            "price_above_ema_slow": curr_close > curr_ema_slow,
            "ema_fast_above_slow": ema_fast[-1] > ema_slow[-1],
        }
    
    def _calculate_ema(self, prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices.copy()
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]  # Start with SMA
        
        for price in prices[period:]:
            ema.append((price - ema[-1]) * multiplier + ema[-1])
        
        return ema
    
    def _calculate_adx(
        self, 
        highs: List[float], 
        lows: List[float], 
        closes: List[float], 
        period: int
    ) -> float:
        """
        Calculate Average Directional Index (simplified)
        Returns single ADX value
        """
        if len(highs) < period * 2:
            return 0
        
        # Simplified ADX calculation
        # In production, use TA-Lib or full implementation
        
        tr_list = []
        plus_dm = []
        minus_dm = []
        
        for i in range(1, len(highs)):
            high_diff = highs[i] - highs[i-1]
            low_diff = lows[i-1] - lows[i]
            
            tr = max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i-1]),
                abs(lows[i] - closes[i-1])
            )
            tr_list.append(tr)
            
            if high_diff > low_diff and high_diff > 0:
                plus_dm.append(high_diff)
            else:
                plus_dm.append(0)
            
            if low_diff > high_diff and low_diff > 0:
                minus_dm.append(low_diff)
            else:
                minus_dm.append(0)
        
        if len(tr_list) < period:
            return 0
        
        # Simple smoothed averages
        atr = sum(tr_list[-period:]) / period
        avg_plus_dm = sum(plus_dm[-period:]) / period
        avg_minus_dm = sum(minus_dm[-period:]) / period
        
        if atr == 0:
            return 0
        
        plus_di = (avg_plus_dm / atr) * 100
        minus_di = (avg_minus_dm / atr) * 100
        
        di_sum = plus_di + minus_di
        if di_sum == 0:
            return 0
        
        dx = abs(plus_di - minus_di) / di_sum * 100
        
        return dx  # Simplified ADX (would need smoothing for accuracy)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎯 SIGNAL GENERATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def analyze_market(
        self, 
        symbol: str, 
        market_data: Dict[str, Any]
    ) -> Optional[AgentSignal]:
        """
        Analyze market for momentum breakout opportunities
        
        Entry conditions:
        - Price crosses EMA21 (bullish or bearish)
        - Volume > 2x average
        - ADX > 25 (strong trend)
        """
        indicators = market_data.get("indicators", {})
        current_price = market_data.get("current_price", 0)
        
        if not indicators or current_price == 0:
            return None
        
        # Extract indicators
        adx = indicators.get("adx", 0)
        volume_ratio = indicators.get("volume_ratio", 0)
        bullish_crossover = indicators.get("bullish_crossover", False)
        bearish_crossover = indicators.get("bearish_crossover", False)
        
        # Check entry conditions
        volume_spike = volume_ratio >= self.VOLUME_MULTIPLIER
        strong_trend = adx >= self.ADX_THRESHOLD
        
        signal_type = None
        
        # Bullish momentum breakout
        if bullish_crossover and volume_spike and strong_trend:
            signal_type = SignalType.BUY
            reasoning = (
                f"Bullish breakout: Price crossed above EMA{self.EMA_SLOW} "
                f"with {volume_ratio:.1f}x volume and ADX={adx:.1f}"
            )
        
        # Bearish momentum breakout
        elif bearish_crossover and volume_spike and strong_trend:
            signal_type = SignalType.SELL
            reasoning = (
                f"Bearish breakout: Price crossed below EMA{self.EMA_SLOW} "
                f"with {volume_ratio:.1f}x volume and ADX={adx:.1f}"
            )
        
        if signal_type is None:
            return None
        
        # Calculate confidence based on signal strength
        confidence = self._calculate_confidence(adx, volume_ratio)
        
        # Calculate targets
        stop_loss, take_profit = self.calculate_targets(current_price, signal_type)
        
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
    
    def _calculate_confidence(self, adx: float, volume_ratio: float) -> float:
        """
        Calculate signal confidence based on indicator strength
        
        Higher ADX and volume ratio = higher confidence
        """
        # ADX contribution (0-0.5)
        adx_score = min(adx / 50, 1.0) * 0.5
        
        # Volume contribution (0-0.5)
        volume_score = min(volume_ratio / 4, 1.0) * 0.5
        
        confidence = adx_score + volume_score
        
        return min(max(confidence, 0.0), 1.0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏭 FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_momentum_scout(env=None) -> MomentumScout:
    """Factory function to create MomentumScout agent"""
    return MomentumScout(env)
