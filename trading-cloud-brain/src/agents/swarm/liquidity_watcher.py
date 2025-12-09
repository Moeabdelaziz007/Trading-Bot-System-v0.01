"""
💧 Liquidity Watcher - Volume Anomaly Detector
مراقب السيولة - كاشف شذوذ الحجم

AlphaAxiom Mini-Agent Swarm
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Hypothesis:
    Sudden large volume spikes without immediate price follow-through 
    indicate accumulation/distribution and precede major price moves.
    
    الفرضية: قفزات الحجم الكبيرة المفاجئة بدون متابعة سعرية
    تشير إلى تجميع/توزيع وتسبق حركات سعرية كبيرة.

Indicators:
    - OBV (On-Balance Volume)
    - Volume spike (> 3x average)
    - Price change relative to volume
    - Cumulative Volume Delta (if available)

Entry Trigger:
    Volume 3x average with minimal price movement (< 0.5%)
"""

from typing import Optional, Dict, Any, List
from .base_mini_agent import (
    BaseMiniAgent,
    AgentSignal,
    SignalType,
)


class LiquidityWatcher(BaseMiniAgent):
    """
    💧 Liquidity Watcher Agent
    Tests the volume-precedes-price hypothesis
    
    يختبر فرضية أن الحجم يسبق السعر
    """
    
    # Agent configuration
    VOLUME_SPIKE_MULTIPLIER = 3.0
    PRICE_CHANGE_THRESHOLD = 0.5  # Max price change % for anomaly
    OBV_DIVERGENCE_PERIODS = 10
    
    @property
    def hypothesis(self) -> str:
        return (
            "Volume precedes price: High volume (>3x avg) with "
            "minimal price movement signals upcoming directional move."
        )
    
    @property
    def timeframes(self) -> List[str]:
        return ["1M", "5M"]
    
    def __init__(self, env=None):
        super().__init__(env)
        self.watchlist = ["BTCUSD", "ETHUSD", "SPY"]
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 INDICATOR CALCULATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_indicators(self, ohlcv: List[Dict]) -> Dict[str, Any]:
        """Calculate volume-based indicators"""
        if len(ohlcv) < 30:
            return {}
        
        closes = [c["close"] for c in ohlcv]
        volumes = [c["volume"] for c in ohlcv]
        opens = [c["open"] for c in ohlcv]
        
        # Calculate OBV
        obv = self._calculate_obv(closes, volumes)
        
        # Volume analysis
        avg_volume = sum(volumes[-20:]) / 20
        current_volume = volumes[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        # Price change analysis
        current_price = closes[-1]
        prev_price = closes[-2]
        price_change_pct = abs(current_price - prev_price) / prev_price * 100
        
        # OBV divergence detection
        obv_trend = self._detect_obv_divergence(
            closes[-self.OBV_DIVERGENCE_PERIODS:],
            obv[-self.OBV_DIVERGENCE_PERIODS:]
        )
        
        # Volume spike with minimal price movement
        volume_spike = volume_ratio >= self.VOLUME_SPIKE_MULTIPLIER
        price_stable = price_change_pct < self.PRICE_CHANGE_THRESHOLD
        anomaly_detected = volume_spike and price_stable
        
        # Determine likely direction from OBV and candle color
        candle_bullish = closes[-1] > opens[-1]
        obv_bullish = obv[-1] > obv[-2] if len(obv) > 1 else False
        
        return {
            "obv": obv[-1] if obv else 0,
            "obv_change": obv[-1] - obv[-2] if len(obv) > 1 else 0,
            "avg_volume": avg_volume,
            "current_volume": current_volume,
            "volume_ratio": volume_ratio,
            "price_change_pct": price_change_pct,
            "volume_spike": volume_spike,
            "price_stable": price_stable,
            "anomaly_detected": anomaly_detected,
            "obv_divergence": obv_trend,
            "candle_bullish": candle_bullish,
            "obv_bullish": obv_bullish,
            "likely_direction": "UP" if obv_bullish else "DOWN",
        }
    
    def _calculate_obv(
        self, 
        closes: List[float], 
        volumes: List[float]
    ) -> List[float]:
        """Calculate On-Balance Volume"""
        if len(closes) < 2:
            return [0]
        
        obv = [0]
        
        for i in range(1, len(closes)):
            if closes[i] > closes[i-1]:
                obv.append(obv[-1] + volumes[i])
            elif closes[i] < closes[i-1]:
                obv.append(obv[-1] - volumes[i])
            else:
                obv.append(obv[-1])
        
        return obv
    
    def _detect_obv_divergence(
        self, 
        prices: List[float], 
        obvs: List[float]
    ) -> str:
        """
        Detect OBV divergence
        Returns: 'BULLISH', 'BEARISH', or 'NONE'
        """
        if len(prices) < 3 or len(obvs) < 3:
            return "NONE"
        
        # Price trend
        price_up = prices[-1] > prices[0]
        price_down = prices[-1] < prices[0]
        
        # OBV trend
        obv_up = obvs[-1] > obvs[0]
        obv_down = obvs[-1] < obvs[0]
        
        # Bullish divergence: Price down, OBV up
        if price_down and obv_up:
            return "BULLISH"
        
        # Bearish divergence: Price up, OBV down
        if price_up and obv_down:
            return "BEARISH"
        
        return "NONE"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎯 SIGNAL GENERATION
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def analyze_market(
        self, 
        symbol: str, 
        market_data: Dict[str, Any]
    ) -> Optional[AgentSignal]:
        """
        Analyze market for volume anomalies
        
        Entry conditions:
        - Volume > 3x average
        - Price change < 0.5% (absorption)
        - OBV direction suggests likely move
        """
        indicators = market_data.get("indicators", {})
        current_price = market_data.get("current_price", 0)
        
        if not indicators or current_price == 0:
            return None
        
        # Check for volume anomaly
        anomaly_detected = indicators.get("anomaly_detected", False)
        
        if not anomaly_detected:
            return None
        
        # Determine direction
        obv_divergence = indicators.get("obv_divergence", "NONE")
        likely_direction = indicators.get("likely_direction", "UP")
        obv_bullish = indicators.get("obv_bullish", False)
        volume_ratio = indicators.get("volume_ratio", 0)
        
        signal_type = None
        
        # Strong bullish signals
        if obv_divergence == "BULLISH" or (obv_bullish and likely_direction == "UP"):
            signal_type = SignalType.BUY
            reasoning = (
                f"Volume anomaly (accumulation): {volume_ratio:.1f}x volume, "
                f"OBV divergence={obv_divergence}, likely UP move"
            )
        
        # Strong bearish signals
        elif obv_divergence == "BEARISH" or (not obv_bullish and likely_direction == "DOWN"):
            signal_type = SignalType.SELL
            reasoning = (
                f"Volume anomaly (distribution): {volume_ratio:.1f}x volume, "
                f"OBV divergence={obv_divergence}, likely DOWN move"
            )
        
        if signal_type is None:
            return None
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            volume_ratio, obv_divergence
        )
        
        # Calculate targets
        stop_loss, take_profit = self.calculate_targets(
            current_price, signal_type
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
        volume_ratio: float, 
        obv_divergence: str
    ) -> float:
        """Calculate confidence based on volume and divergence"""
        # Volume ratio contribution
        volume_score = min(volume_ratio / 6, 1.0) * 0.6
        
        # Divergence contribution
        if obv_divergence in ("BULLISH", "BEARISH"):
            divergence_score = 0.4
        else:
            divergence_score = 0.2
        
        confidence = volume_score + divergence_score
        return min(max(confidence, 0.0), 1.0)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏭 FACTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_liquidity_watcher(env=None) -> LiquidityWatcher:
    """Factory function to create LiquidityWatcher agent"""
    return LiquidityWatcher(env)
