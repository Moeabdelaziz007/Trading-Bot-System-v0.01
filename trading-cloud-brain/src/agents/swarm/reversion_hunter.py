"""
🎯 Reversion Hunter - Mean Reversion Detector
صياد الارتداد - كاشف العودة للمتوسط

AlphaAxiom Mini-Agent Swarm
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Hypothesis:
    Price overextension from key moving averages (EMA20) 
    will revert to the mean.
    
    الفرضية: المبالغة السعرية البعيدة عن المتوسطات المتحركة
    ستعود للمتوسط.

Indicators:
    - RSI(7) < 20 or > 80 (oversold/overbought)
    - Bollinger Bands(20, 2) - price at bands
    - Distance from EMA20 (> 2 standard deviations)

Entry Trigger:
    RSI extreme + Price at Bollinger Band + 2σ from EMA
"""

from typing import Optional, Dict, Any, List
import math
from .base_mini_agent import (
    BaseMiniAgent,
    AgentSignal,
    SignalType,
)


class ReversionHunter(BaseMiniAgent):
    """
    🎯 Reversion Hunter Agent
    Tests the mean reversion hypothesis
    
    يختبر فرضية العودة للمتوسط
    """
    
    # Agent configuration
    RSI_PERIOD = 7
    RSI_OVERSOLD = 20
    RSI_OVERBOUGHT = 80
    BB_PERIOD = 20
    BB_STD = 2
    EMA_PERIOD = 20
    DEVIATION_THRESHOLD = 2.0  # Standard deviations from EMA
    
    @property
    def hypothesis(self) -> str:
        return (
            "Mean reversion: Overextended prices (RSI extreme + "
            "2σ from EMA) revert to the mean."
        )
    
    @property
    def timeframes(self) -> List[str]:
        return ["5M", "15M"]
    
    def __init__(self, env=None):
        super().__init__(env)
        self.watchlist = ["BTCUSD", "ETHUSD", "SPY", "EURUSD"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 INDICATOR CALCULATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_indicators(self, ohlcv: List[Dict]) -> Dict[str, Any]:
        """Calculate mean reversion indicators"""
        if len(ohlcv) < self.BB_PERIOD + 10:
            return {}
        
        closes = [c["close"] for c in ohlcv]
        highs = [c["high"] for c in ohlcv]
        lows = [c["low"] for c in ohlcv]
        
        # Calculate RSI
        rsi = self._calculate_rsi(closes, self.RSI_PERIOD)
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger(
            closes, self.BB_PERIOD, self.BB_STD
        )
        
        # Calculate EMA and distance
        ema = self._calculate_ema(closes, self.EMA_PERIOD)
        current_ema = ema[-1]
        current_price = closes[-1]
        
        # Calculate standard deviation for distance
        std_dev = self._calculate_std(closes[-self.EMA_PERIOD:])
        
        # Distance from EMA in standard deviations
        if std_dev > 0:
            ema_distance_std = (current_price - current_ema) / std_dev
        else:
            ema_distance_std = 0
        
        # Price position relative to Bollinger Bands
        bb_position = self._get_bb_position(
            current_price, bb_upper, bb_middle, bb_lower
        )
        
        return {
            "rsi": rsi,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "ema": current_ema,
            "std_dev": std_dev,
            "ema_distance_std": ema_distance_std,
            "bb_position": bb_position,
            "is_oversold": rsi < self.RSI_OVERSOLD,
            "is_overbought": rsi > self.RSI_OVERBOUGHT,
            "at_upper_band": current_price >= bb_upper,
            "at_lower_band": current_price <= bb_lower,
        }
    
    def _calculate_rsi(self, prices: List[float], period: int) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return 50
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_bollinger(
        self, 
        prices: List[float], 
        period: int, 
        num_std: float
    ) -> tuple:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return (prices[-1], prices[-1], prices[-1])
        
        # Middle band (SMA)
        middle = sum(prices[-period:]) / period
        
        # Standard deviation
        std = self._calculate_std(prices[-period:])
        
        upper = middle + (num_std * std)
        lower = middle - (num_std * std)
        
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
    
    def _get_bb_position(
        self, 
        price: float, 
        upper: float, 
        middle: float, 
        lower: float
    ) -> str:
        """Get price position relative to Bollinger Bands"""
        if price >= upper:
            return "ABOVE_UPPER"
        elif price <= lower:
            return "BELOW_LOWER"
        elif price > middle:
            return "UPPER_HALF"
        else:
            return "LOWER_HALF"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎯 SIGNAL GENERATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def analyze_market(
        self, 
        symbol: str, 
        market_data: Dict[str, Any]
    ) -> Optional[AgentSignal]:
        """
        Analyze market for mean reversion opportunities
        
        Entry conditions:
        - RSI < 20 (oversold) or RSI > 80 (overbought)
        - Price at Bollinger Band extremes
        - Price > 2 standard deviations from EMA
        """
        indicators = market_data.get("indicators", {})
        current_price = market_data.get("current_price", 0)
        
        if not indicators or current_price == 0:
            return None
        
        # Extract indicators
        rsi = indicators.get("rsi", 50)
        is_oversold = indicators.get("is_oversold", False)
        is_overbought = indicators.get("is_overbought", False)
        at_upper_band = indicators.get("at_upper_band", False)
        at_lower_band = indicators.get("at_lower_band", False)
        ema_distance = indicators.get("ema_distance_std", 0)
        
        signal_type = None
        
        # Oversold reversal (BUY signal)
        if (is_oversold and at_lower_band and 
                ema_distance < -self.DEVIATION_THRESHOLD):
            signal_type = SignalType.BUY
            reasoning = (
                f"Oversold reversal: RSI={rsi:.1f}, "
                f"at lower Bollinger, {abs(ema_distance):.1f}σ below EMA"
            )
        
        # Overbought reversal (SELL signal)
        elif (is_overbought and at_upper_band and 
              ema_distance > self.DEVIATION_THRESHOLD):
            signal_type = SignalType.SELL
            reasoning = (
                f"Overbought reversal: RSI={rsi:.1f}, "
                f"at upper Bollinger, {ema_distance:.1f}σ above EMA"
            )
        
        if signal_type is None:
            return None
        
        # Calculate confidence
        confidence = self._calculate_confidence(rsi, ema_distance)
        
        # Calculate targets (tighter for mean reversion)
        stop_loss, take_profit = self._calculate_reversion_targets(
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
    
    def _calculate_confidence(self, rsi: float, ema_distance: float) -> float:
        """Calculate confidence based on RSI extreme and distance"""
        # RSI contribution (more extreme = higher confidence)
        if rsi < self.RSI_OVERSOLD:
            rsi_score = (self.RSI_OVERSOLD - rsi) / self.RSI_OVERSOLD * 0.5
        elif rsi > self.RSI_OVERBOUGHT:
            rsi_score = (rsi - self.RSI_OVERBOUGHT) / 20 * 0.5
        else:
            rsi_score = 0
        
        # Distance contribution (farther = higher confidence)
        distance_score = min(abs(ema_distance) / 4, 1.0) * 0.5
        
        confidence = rsi_score + distance_score
        return min(max(confidence, 0.0), 1.0)
    
    def _calculate_reversion_targets(
        self, 
        price: float, 
        signal_type: SignalType,
        indicators: Dict
    ) -> tuple:
        """Calculate targets for mean reversion trade"""
        ema = indicators.get("ema", price)
        bb_middle = indicators.get("bb_middle", price)
        
        # Target: Return to EMA or middle Bollinger
        target = (ema + bb_middle) / 2
        
        if signal_type == SignalType.BUY:
            stop_loss = price * 0.985  # 1.5% stop
            take_profit = target
        else:
            stop_loss = price * 1.015
            take_profit = target
        
        return (stop_loss, take_profit)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏭 FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_reversion_hunter(env=None) -> ReversionHunter:
    """Factory function to create ReversionHunter agent"""
    return ReversionHunter(env)
