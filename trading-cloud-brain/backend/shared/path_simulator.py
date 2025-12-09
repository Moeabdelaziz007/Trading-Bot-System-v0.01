"""
🔮 PATH SIMULATOR: Regime-Adaptive Price Simulation
Uses GBM for Trending, Ornstein-Uhlenbeck for Mean-Reverting.
"""

import random
import math
from typing import Dict, List

class PathSimulator:
    """
    Monte Carlo path simulation for Edge MCTS.
    Adapts simulation model based on detected regime.
    """
    
    def __init__(self, volatility: float = 0.02, theta: float = 0.1):
        self.volatility = volatility  # Daily volatility
        self.theta = theta  # Mean reversion speed (for OU process)
    
    def simulate_single_path(
        self,
        current_price: float,
        regime: str,
        steps: int = 10,
        drift: float = 0.0,
        mean_price: float = None
    ) -> Dict:
        """
        Simulate one price path based on regime.
        
        Args:
            current_price: Starting price
            regime: "TRENDING", "MEAN_REVERTING", or "RANDOM"
            steps: Number of time steps to simulate
            drift: Momentum-based drift (for trending)
            mean_price: Price to revert to (for mean-reverting)
        
        Returns:
            Dict with final_price, path, and pnl
        """
        price = current_price
        path = [price]
        
        if regime == "TRENDING":
            # Geometric Brownian Motion with drift
            for _ in range(steps):
                # dS = μS dt + σS dW
                dt = 1.0 / steps
                dW = random.gauss(0, math.sqrt(dt))
                price *= (1 + drift * dt + self.volatility * dW)
                path.append(price)
        
        elif regime == "MEAN_REVERTING":
            # Ornstein-Uhlenbeck Process
            if mean_price is None:
                mean_price = current_price
            
            for _ in range(steps):
                # dX = θ(μ - X)dt + σdW
                dt = 1.0 / steps
                dW = random.gauss(0, math.sqrt(dt))
                price += self.theta * (mean_price - price) * dt + self.volatility * price * dW
                path.append(max(price, 0.01))  # Prevent negative prices
        
        else:  # RANDOM
            # Pure Brownian Motion (no edge)
            for _ in range(steps):
                dt = 1.0 / steps
                dW = random.gauss(0, math.sqrt(dt))
                price *= (1 + self.volatility * dW)
                path.append(price)
        
        return {
            "final_price": path[-1],
            "path": path,
            "pnl": path[-1] - current_price,
            "pnl_percent": ((path[-1] - current_price) / current_price) * 100
        }
    
    def run_swarm(
        self,
        state_tensor: Dict,
        num_simulations: int = 20,
        steps: int = 10
    ) -> Dict:
        """
        Run multiple simulations (Edge MCTS style).
        
        Args:
            state_tensor: Market state dictionary
            num_simulations: Number of paths to simulate
            steps: Steps per path
        
        Returns:
            Aggregated results with win rate and recommended action
        """
        current_price = state_tensor.get("price", 100)
        regime = state_tensor.get("regime", "RANDOM")
        momentum = state_tensor.get("momentum", 0)
        sma_200 = state_tensor.get("sma_200", current_price)
        
        # Don't simulate if random regime
        if regime == "RANDOM":
            return {
                "action": "HOLD",
                "reason": "Random Walk Detected (H ≈ 0.5)",
                "win_rate": 0.5,
                "expected_pnl": 0,
                "simulations": 0
            }
        
        # Run simulations
        results = []
        for _ in range(num_simulations):
            result = self.simulate_single_path(
                current_price=current_price,
                regime=regime,
                steps=steps,
                drift=momentum,
                mean_price=sma_200
            )
            results.append(result)
        
        # Aggregate
        wins = sum(1 for r in results if r["pnl"] > 0)
        win_rate = wins / num_simulations
        avg_pnl = sum(r["pnl"] for r in results) / num_simulations
        avg_pnl_percent = sum(r["pnl_percent"] for r in results) / num_simulations
        
        # Decision logic
        if regime == "TRENDING":
            if momentum > 0 and win_rate > 0.6:
                action = "BUY"
            elif momentum < 0 and win_rate > 0.6:
                action = "SELL"
            else:
                action = "HOLD"
        else:  # MEAN_REVERTING
            if current_price < sma_200 * 0.98 and win_rate > 0.6:
                action = "BUY"  # Below mean, expect reversion up
            elif current_price > sma_200 * 1.02 and win_rate > 0.6:
                action = "SELL"  # Above mean, expect reversion down
            else:
                action = "HOLD"
        
        return {
            "action": action,
            "regime": regime,
            "win_rate": round(win_rate, 3),
            "expected_pnl": round(avg_pnl, 4),
            "expected_pnl_percent": round(avg_pnl_percent, 2),
            "simulations": num_simulations,
            "confidence": "HIGH" if win_rate > 0.7 else "MEDIUM" if win_rate > 0.55 else "LOW"
        }


# Quick test
if __name__ == "__main__":
    simulator = PathSimulator(volatility=0.02)
    
    # Test trending market
    state = {
        "price": 50000,
        "regime": "TRENDING",
        "momentum": 0.01,
        "sma_200": 48000
    }
    result = simulator.run_swarm(state, num_simulations=50)
    print(f"Trending: {result}")
    
    # Test mean reverting
    state["regime"] = "MEAN_REVERTING"
    state["price"] = 45000  # Below SMA
    result = simulator.run_swarm(state, num_simulations=50)
    print(f"Mean Reverting: {result}")
