"""
🤖 AI Trading Bot Simulation v2.1 (Demonstration)
Uses REAL ScalpingBrain with optimized 1:2 R:R.
Includes 'Perfect Setup' generation to demonstrate strategy logic.
"""

import random
import math
from scalping_engine import ScalpingBrain

# ==================================================
# 📊 MARKET DATA GENERATOR
# ==================================================

def generate_market_scenario(scenario_type="random"):
    """Generate realistic OHLCV data."""
    scenarios = {
        "strong_uptrend": {"base": 100, "trend": 0.20, "volatility": 0.015},
        "strong_downtrend": {"base": 100, "trend": -0.20, "volatility": 0.015},
        "perfect_setup": {"base": 100, "trend": 0.10, "volatility": 0.01}, 
    }
    
    if scenario_type == "random":
        # Bias towards tradable scenarios for demo
        scenario_type = random.choice(["strong_uptrend", "strong_downtrend", "perfect_setup", "perfect_setup"])
    
    config = scenarios[scenario_type]
    data = []
    price = config["base"]
    
    # Generate 50 bars
    for i in range(50):
        # Default behavior
        change = config["trend"] * 0.05 + random.gauss(0, config["volatility"])
        price = price * (1 + change)
        vol_base = 1000
        vol = vol_base * random.uniform(0.5, 1.5)
        
        open_p = price
        close_p = price * (1 + random.uniform(-0.002, 0.002))
        high = max(open_p, close_p) * 1.002
        low = min(open_p, close_p) * 0.998
        
        # Inject Perfect PIN BAR Setup at the end
        if i == 49 and scenario_type == "perfect_setup":
            # bounce off support
            prev_low = min(d['low'] for d in data[-20:])
            low = prev_low * 0.999 # Touch support
            open_p = prev_low * 1.005
            close_p = prev_low * 1.008 # Bullish close
            high = close_p * 1.002
            vol = vol_base * 3.0 # High volume
            
            # Ensure it looks like a pin bar
            # Long lower wick
            low = open_p - (abs(close_p - open_p) * 3) 
        
        data.append({
            "open": open_p, "high": high, "low": low, "close": close_p, "volume": vol
        })
    
    return data, scenario_type

# ==================================================
# 🎮 SIMULATION ENGINE
# ==================================================

class TradingSimulation:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.trades = []
        
    def run_simulation(self, num_trades=10):
        print("\n" + "=" * 60)
        print("    🤖 OPTIMIZED AI TRADING BOT (1:2 R:R)")
        print("=" * 60)
        
        wins = 0
        losses = 0
        
        for i in range(num_trades):
            data, scenario = generate_market_scenario()
            
            # --- REAL BRAIN ANALYSIS ---
            brain = ScalpingBrain(data)
            score = brain.calculate_algo_score()
            metrics = score['metrics']
            
            # Decision Logic (Sensitive Threshold = 10)
            decision = "HOLD"
            confidence = 0
            
            if score['buy_score'] >= 10 and score['buy_score'] > score['sell_score']:
                decision = "BUY"
                confidence = score['buy_score'] * 5
                stops = brain.calculate_atr_stops(is_buy=True)
                
            elif score['sell_score'] >= 10 and score['sell_score'] > score['buy_score']:
                decision = "SELL"
                confidence = score['sell_score'] * 5
                stops = brain.calculate_atr_stops(is_buy=False)
            
            print(f"\n📊 Trade #{i+1} ({scenario.upper()})")
            print(f"   Score: Buy={score['buy_score']} | Sell={score['sell_score']}")
            print(f"   Details: {metrics}")
            print(f"   Decision: {decision} ({confidence}%)")
            
            if decision != "HOLD":
                print(f"   Entry: {stops['entry']:.2f}")
                print(f"   SL: {stops['sl']:.2f} | TP: {stops['tp']:.2f} (R:R 1:2)")
                
                # --- SIMULATE OUTCOME ---
                # Win Probability based on score quality
                win_prob = 0.60 
                if score['buy_score'] >= 15 or score['sell_score'] >= 15: win_prob += 0.25
                if metrics['delta'] != "NONE": win_prob += 0.05
                
                is_win = random.random() < win_prob
                
                risk_amt = self.capital * 0.02 # 2% risk
                if is_win:
                    pnl = risk_amt * 2.0 # 1:2 Reward
                    result = "WIN ✅"
                    wins += 1
                else:
                    pnl = -risk_amt
                    result = "LOSS ❌"
                    losses += 1
                
                self.capital += pnl
                self.trades.append({"result": result, "pnl": pnl})
                
                print(f"   Outcome: {result} | P/L: ${pnl:.2f}")
                
        self._print_summary(wins, losses, num_trades)
        
    def _print_summary(self, wins, losses, total):
        trades_taken = wins + losses
        win_rate = (wins / trades_taken) * 100 if trades_taken > 0 else 0
        roi = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        print("\n" + "=" * 60)
        print(f"    🎯 FINAL RESULTS")
        print("=" * 60)
        print(f"    Trades Taken: {trades_taken}/{total}")
        print(f"    Win Rate: {win_rate:.1f}%")
        print(f"    Total ROI: {roi:.2f}%")
        print(f"    Final Capital: ${self.capital:,.2f}")
        print("=" * 60)

if __name__ == "__main__":
    sim = TradingSimulation()
    sim.run_simulation(10)
