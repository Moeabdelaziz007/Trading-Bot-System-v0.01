"""
🧠 STATE TENSOR: Holographic Market View
Inspired by AlphaZero's board representation.
"""

import math
import json
from typing import List, Dict, Optional

class StateTensor:
    """
    Multi-dimensional market state for AlphaAxiom decision making.
    Combines: Price, Chaos Metrics, Social Sentiment, Macro Factors.
    """
    
    def __init__(self):
        # Dimension 1: Price/Volume
        self.price_matrix = []  # Shape: (T, 5) - OHLCV
        self.current_price = 0.0
        self.sma_20 = 0.0
        self.sma_200 = 0.0
        self.momentum = 0.0
        
        # Dimension 2: Chaos Metrics (from Dream Engine)
        self.hurst_exponent = 0.5  # 0-1, 0.5 = random walk
        self.fractal_dimension = 1.5  # 1-2, lower = trending
        self.entropy = 0.5  # 0-1, higher = more chaotic
        
        # Dimension 3: Social/Sentiment
        self.sentiment_score = 0.0  # -1 to +1
        self.social_volume = 0  # mentions count
        
        # Dimension 4: Macro
        self.correlation_matrix = {}  # asset correlations
        
        # Derived
        self.regime = "RANDOM"  # TRENDING, MEAN_REVERTING, RANDOM
    
    @classmethod
    def from_candles(cls, candles: List[Dict], chaos_metrics: Dict = None, sentiment: Dict = None):
        """
        Build StateTensor from raw market data.
        """
        tensor = cls()
        
        if not candles:
            return tensor
        
        # Extract OHLCV
        closes = [c['close'] for c in candles]
        tensor.current_price = closes[-1]
        tensor.price_matrix = [[c['open'], c['high'], c['low'], c['close'], c.get('volume', 0)] for c in candles]
        
        # Calculate SMAs
        if len(closes) >= 20:
            tensor.sma_20 = sum(closes[-20:]) / 20
        if len(closes) >= 200:
            tensor.sma_200 = sum(closes[-200:]) / 200
        
        # Momentum (rate of change)
        if len(closes) >= 10:
            tensor.momentum = (closes[-1] - closes[-10]) / closes[-10] if closes[-10] != 0 else 0
        
        # Add chaos metrics
        if chaos_metrics:
            tensor.hurst_exponent = chaos_metrics.get('hurst', 0.5)
            tensor.fractal_dimension = chaos_metrics.get('fdi', 1.5)
            tensor.entropy = chaos_metrics.get('entropy', 0.5)
        
        # Add sentiment
        if sentiment:
            tensor.sentiment_score = sentiment.get('score', 0.0)
            tensor.social_volume = sentiment.get('volume', 0)
        
        # Determine regime
        tensor.regime = tensor._detect_regime()
        
        return tensor
    
    def _detect_regime(self) -> str:
        """
        Use Hurst Exponent to detect market regime.
        H > 0.55 = Trending
        H < 0.45 = Mean Reverting
        Else = Random (no trade zone)
        """
        if self.hurst_exponent > 0.55:
            return "TRENDING"
        elif self.hurst_exponent < 0.45:
            return "MEAN_REVERTING"
        else:
            return "RANDOM"
    
    def to_embedding(self) -> List[float]:
        """
        Flatten tensor for neural network input.
        """
        # Normalize values to 0-1 range
        embedding = [
            self.current_price / 100000,  # Normalize for BTC-scale
            self.momentum + 0.5,  # Shift to 0-1
            self.hurst_exponent,
            self.fractal_dimension / 2,
            self.entropy,
            (self.sentiment_score + 1) / 2,  # -1,1 -> 0,1
        ]
        return embedding
    
    def to_dict(self) -> Dict:
        """
        Serialize for R2 storage and Worker communication.
        """
        return {
            "price": self.current_price,
            "sma_20": self.sma_20,
            "sma_200": self.sma_200,
            "momentum": self.momentum,
            "chaos": {
                "hurst": self.hurst_exponent,
                "fdi": self.fractal_dimension,
                "entropy": self.entropy
            },
            "sentiment": {
                "score": self.sentiment_score,
                "volume": self.social_volume
            },
            "regime": self.regime
        }
    
    def should_trade(self) -> bool:
        """
        Basic filter: Don't trade in random regime.
        """
        return self.regime != "RANDOM"


class HurstCalculator:
    """
    Calculate Hurst Exponent using R/S Analysis.
    H > 0.5 = Trending (Persistence)
    H < 0.5 = Mean Reverting (Anti-persistence)
    H = 0.5 = Random Walk
    """
    
    @staticmethod
    def calculate(prices: List[float], min_window: int = 10) -> float:
        """
        Rescaled Range (R/S) method for Hurst Exponent.
        """
        if len(prices) < min_window * 2:
            return 0.5  # Default to random
        
        # Log returns
        returns = [math.log(prices[i] / prices[i-1]) if prices[i-1] != 0 else 0 
                   for i in range(1, len(prices))]
        
        n = len(returns)
        rs_values = []
        sizes = []
        
        # Calculate R/S for different window sizes
        for size in [10, 20, 40, 80]:
            if size > n:
                break
            
            num_windows = n // size
            rs_for_size = []
            
            for i in range(num_windows):
                window = returns[i * size:(i + 1) * size]
                
                # Mean-adjusted cumulative deviation
                mean = sum(window) / len(window)
                cumdev = [sum(window[:j+1]) - (j+1) * mean for j in range(len(window))]
                
                # Range
                R = max(cumdev) - min(cumdev)
                
                # Standard deviation
                variance = sum((x - mean) ** 2 for x in window) / len(window)
                S = math.sqrt(variance) if variance > 0 else 1
                
                if S > 0:
                    rs_for_size.append(R / S)
            
            if rs_for_size:
                rs_values.append(sum(rs_for_size) / len(rs_for_size))
                sizes.append(size)
        
        # Linear regression to find H
        if len(rs_values) < 2:
            return 0.5
        
        log_sizes = [math.log(s) for s in sizes]
        log_rs = [math.log(rs) if rs > 0 else 0 for rs in rs_values]
        
        # Simple linear regression
        n = len(log_sizes)
        sum_x = sum(log_sizes)
        sum_y = sum(log_rs)
        sum_xy = sum(x * y for x, y in zip(log_sizes, log_rs))
        sum_x2 = sum(x * x for x in log_sizes)
        
        denominator = n * sum_x2 - sum_x ** 2
        if denominator == 0:
            return 0.5
        
        H = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Clamp to valid range
        return max(0.0, min(1.0, H))
