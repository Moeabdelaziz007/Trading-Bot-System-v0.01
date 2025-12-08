"""
Signal Synthesizer: The Alchemist
Converts 4 weak signals into 1 strong Alpha signal.
"""

class SignalSynthesizer:
    """
    Combines Price, Technicals, Sentiment, and Volume
    into a single composite trading signal.
    
    Formula (From V2.1 Architecture):
    - Price Momentum: 35%
    - Technicals (RSI/MACD): 30%
    - Sentiment: 25%
    - Volume/Volatility: 10%
    """
    
    WEIGHTS = {
        "price": 0.35,
        "technicals": 0.30,
        "sentiment": 0.25,
        "volume": 0.10
    }
    
    SIGNAL_THRESHOLDS = {
        "STRONG_BUY": 0.7,
        "BUY": 0.3,
        "NEUTRAL": -0.3,
        "SELL": -0.7,
        # Below -0.7 is STRONG_SELL
    }

    def _normalize_rsi(self, rsi: float) -> float:
        """
        Convert RSI (0-100) to signal (-1 to +1).
        RSI < 30 = Oversold (Bullish) = +1
        RSI > 70 = Overbought (Bearish) = -1
        """
        if rsi <= 30:
            return 1.0
        elif rsi >= 70:
            return -1.0
        else:
            # Linear interpolation in the middle zone
            return (50 - rsi) / 20

    def _normalize_macd(self, macd_val: float, macd_signal: float) -> float:
        """
        MACD crossover signal.
        MACD > Signal = Bullish = +1
        MACD < Signal = Bearish = -1
        """
        diff = macd_val - macd_signal
        return max(-1, min(1, diff * 10))  # Scale and clamp

    def _classify_signal(self, score: float) -> str:
        """Convert numeric score to signal direction."""
        if score >= self.SIGNAL_THRESHOLDS["STRONG_BUY"]:
            return "STRONG_BUY"
        elif score >= self.SIGNAL_THRESHOLDS["BUY"]:
            return "BUY"
        elif score >= self.SIGNAL_THRESHOLDS["NEUTRAL"]:
            return "NEUTRAL"
        elif score >= self.SIGNAL_THRESHOLDS["SELL"]:
            return "SELL"
        else:
            return "STRONG_SELL"

    def synthesize(
        self,
        price_change_pct: float,
        rsi_14: float,
        macd_value: float,
        macd_signal: float,
        sentiment_score: float,
        volume_change_pct: float = 0
    ) -> dict:
        """
        Generate composite Alpha signal.
        
        Args:
            price_change_pct: Recent price change (e.g., 0.02 = 2%)
            rsi_14: RSI value (0-100)
            macd_value: MACD line value
            macd_signal: MACD signal line value
            sentiment_score: News sentiment (-1 to +1)
            volume_change_pct: Volume change percentage
            
        Returns:
            {
                "direction": "BUY|SELL|...",
                "confidence": 0.0-1.0,
                "factors": ["RSI Oversold", "Bullish News"]
            }
        """
        factors = []
        
        # 1. Price Momentum (35%)
        price_signal = max(-1, min(1, price_change_pct * 10))
        if price_change_pct > 0.01:
            factors.append("Positive Momentum")
        elif price_change_pct < -0.01:
            factors.append("Negative Momentum")
        
        # 2. Technicals - RSI (15%) + MACD (15%)
        rsi_signal = self._normalize_rsi(rsi_14)
        macd_sig = self._normalize_macd(macd_value, macd_signal)
        tech_signal = (rsi_signal + macd_sig) / 2
        
        if rsi_14 < 35:
            factors.append("RSI Oversold")
        elif rsi_14 > 65:
            factors.append("RSI Overbought")
        if macd_value > macd_signal:
            factors.append("MACD Bullish Cross")
        
        # 3. Sentiment (25%)
        sent_signal = sentiment_score
        if sentiment_score > 0.3:
            factors.append("Bullish News")
        elif sentiment_score < -0.3:
            factors.append("Bearish News")
        
        # 4. Volume (10%)
        vol_signal = max(-1, min(1, volume_change_pct))
        if volume_change_pct > 0.5:
            factors.append("High Volume Surge")
        
        # Weighted Combination
        composite_score = (
            price_signal * self.WEIGHTS["price"] +
            tech_signal * self.WEIGHTS["technicals"] +
            sent_signal * self.WEIGHTS["sentiment"] +
            vol_signal * self.WEIGHTS["volume"]
        )
        
        # Confidence is the absolute value (0 to 1)
        confidence = abs(composite_score)
        
        return {
            "direction": self._classify_signal(composite_score),
            "confidence": round(confidence, 2),
            "raw_score": round(composite_score, 3),
            "factors": factors
        }
