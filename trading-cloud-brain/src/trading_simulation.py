"""
🤖 AI Trading Bot Simulation
Uses ALL 14 tools integrated into the Axiom Antigravity system.

This simulation demonstrates:
1. Market data generation (realistic scenarios)
2. ScalpingBrain analysis (indicators, S/R, signals)
3. LongTermBrain analysis (Golden Cross, ADX, RSI)
4. RiskGuardian validation (Kelly Criterion, Chaos Factor)
5. Trade execution and P/L tracking
"""

import random
import math

# ==================================================
# 📊 SIMULATED MARKET DATA GENERATOR
# ==================================================

def generate_market_scenario(scenario_type="random"):
    """Generate realistic OHLCV data for different market conditions."""
    
    scenarios = {
        "strong_uptrend": {"base": 100, "trend": 0.15, "volatility": 0.02},
        "strong_downtrend": {"base": 100, "trend": -0.15, "volatility": 0.02},
        "sideways": {"base": 100, "trend": 0, "volatility": 0.01},
        "volatile_up": {"base": 100, "trend": 0.05, "volatility": 0.05},
        "volatile_down": {"base": 100, "trend": -0.05, "volatility": 0.05},
    }
    
    if scenario_type == "random":
        scenario_type = random.choice(list(scenarios.keys()))
    
    config = scenarios[scenario_type]
    data = []
    price = config["base"]
    volume_base = 10000
    
    for i in range(50):
        # Add trend + random noise
        change = config["trend"] + random.gauss(0, config["volatility"])
        price = price * (1 + change)
        
        high = price * (1 + random.uniform(0.001, 0.01))
        low = price * (1 - random.uniform(0.001, 0.01))
        open_price = random.uniform(low, high)
        volume = volume_base * random.uniform(0.5, 2.0)
        
        data.append({
            "open": open_price,
            "high": high,
            "low": low,
            "close": price,
            "volume": volume
        })
    
    return data, scenario_type

# ==================================================
# 📈 SCALPING BRAIN (All Tools)
# ==================================================

class ScalpingBrain:
    """Scalping analysis with all 14 tools."""
    
    # Configuration
    ATR_PERIOD = 14
    ATR_SL_MULT = 1.5
    ATR_TP_MULT = 1.0
    SR_LOOKBACK = 20
    
    def __init__(self, data):
        self.data = data
    
    # Tool 1: ATR
    def calculate_atr(self, period=None):
        period = period or self.ATR_PERIOD
        if len(self.data) < period + 1:
            return None
        
        tr_sum = 0
        for i in range(-period, 0):
            high = self.data[i]['high']
            low = self.data[i]['low']
            prev_close = self.data[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_sum += tr
        
        return tr_sum / period
    
    # Tool 2: ATR-Based Stops
    def calculate_atr_stops(self, is_buy):
        atr = self.calculate_atr()
        if not atr:
            return None
        
        current = self.data[-1]['close']
        sl_dist = atr * self.ATR_SL_MULT
        tp_dist = atr * self.ATR_TP_MULT
        
        if is_buy:
            return {"entry": current, "sl": current - sl_dist, "tp": current + tp_dist, "atr": atr}
        else:
            return {"entry": current, "sl": current + sl_dist, "tp": current - tp_dist, "atr": atr}
    
    # Tool 3: Support/Resistance
    def calculate_sr_levels(self):
        lookback = min(self.SR_LOOKBACK, len(self.data))
        recent = self.data[-lookback:]
        
        support = min(d['low'] for d in recent)
        resistance = max(d['high'] for d in recent)
        
        return {"support": support, "resistance": resistance}
    
    # Tool 4: Rejection Candle (Pin Bar)
    def detect_rejection_candle(self):
        if len(self.data) < 2:
            return {"bullish": False, "bearish": False}
        
        candle = self.data[-1]
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return {"bullish": False, "bearish": False}
        
        upper_wick = candle['high'] - max(candle['close'], candle['open'])
        lower_wick = min(candle['close'], candle['open']) - candle['low']
        
        bullish = lower_wick > body * 2 and lower_wick > upper_wick
        bearish = upper_wick > body * 2 and upper_wick > lower_wick
        
        return {"bullish": bullish, "bearish": bearish}
    
    # Tool 5: Volume Profile (POC)
    def calculate_poc(self):
        volumes = {}
        for d in self.data[-20:]:
            price_level = round(d['close'], 1)
            volumes[price_level] = volumes.get(price_level, 0) + d['volume']
        
        if not volumes:
            return self.data[-1]['close']
        
        return max(volumes, key=volumes.get)
    
    # Tool 6: VWAP
    def calculate_vwap(self):
        cumulative_tp_vol = 0
        cumulative_vol = 0
        
        for d in self.data[-20:]:
            typical_price = (d['high'] + d['low'] + d['close']) / 3
            cumulative_tp_vol += typical_price * d['volume']
            cumulative_vol += d['volume']
        
        return cumulative_tp_vol / cumulative_vol if cumulative_vol > 0 else 0
    
    # Tool 7: Footprint Score (Delta)
    def calculate_footprint_score(self):
        if len(self.data) < 5:
            return 0
        
        buy_vol = sum(d['volume'] for d in self.data[-5:] if d['close'] > d['open'])
        sell_vol = sum(d['volume'] for d in self.data[-5:] if d['close'] <= d['open'])
        total_vol = buy_vol + sell_vol
        
        return (buy_vol - sell_vol) / total_vol if total_vol > 0 else 0
    
    # Tool 8: Algo Scoring
    def calculate_algo_score(self):
        buy_score = 0
        sell_score = 0
        
        sr = self.calculate_sr_levels()
        rejection = self.detect_rejection_candle()
        footprint = self.calculate_footprint_score()
        vwap = self.calculate_vwap()
        current = self.data[-1]['close']
        
        # Near support + bullish rejection
        if current < sr['support'] * 1.02 and rejection['bullish']:
            buy_score += 2
        
        # Near resistance + bearish rejection
        if current > sr['resistance'] * 0.98 and rejection['bearish']:
            sell_score += 2
        
        # Footprint bias
        if footprint > 0.3:
            buy_score += 1
        elif footprint < -0.3:
            sell_score += 1
        
        # VWAP position
        if current > vwap:
            buy_score += 0.5
        else:
            sell_score += 0.5
        
        return {"buy_score": buy_score, "sell_score": sell_score}
    
    # Tool 9: Supertrend
    def calculate_supertrend(self, multiplier=3.0):
        if len(self.data) < 15:
            return {"trend": 0, "trend_name": "UNKNOWN"}
        
        atr = self.calculate_atr(10)
        if not atr:
            return {"trend": 0, "trend_name": "UNKNOWN"}
        
        current = self.data[-1]
        hl2 = (current['high'] + current['low']) / 2
        upper = hl2 + (multiplier * atr)
        lower = hl2 - (multiplier * atr)
        
        # Determine trend based on price vs bands
        prev_close = self.data[-2]['close']
        trend = 1 if current['close'] > lower else -1
        
        return {
            "trend": trend,
            "trend_name": "UPTREND" if trend == 1 else "DOWNTREND",
            "value": lower if trend == 1 else upper
        }
    
    # Tool 10: Trailing Stop
    def calculate_trailing_stop(self, entry_price, is_buy, profit_threshold=0.3):
        current = self.data[-1]['close']
        
        if is_buy:
            profit_pct = ((current - entry_price) / entry_price) * 100
            highest = max(d['high'] for d in self.data[-20:])
        else:
            profit_pct = ((entry_price - current) / entry_price) * 100
            highest = min(d['low'] for d in self.data[-20:])
        
        activated = profit_pct >= profit_threshold
        trail = highest * 0.998 if is_buy else highest * 1.002
        
        return {
            "activated": activated,
            "profit_pct": profit_pct,
            "trailing_stop": trail if activated else None
        }

# ==================================================
# 📉 LONG TERM BRAIN (Tools 11-13)
# ==================================================

class LongTermBrain:
    """Long-term analysis for Golden Cross strategy."""
    
    def __init__(self, data):
        self.data = data
    
    # Tool 11: RSI
    def calculate_rsi(self, period=14):
        if len(self.data) < period + 1:
            return 50
        
        gains = []
        losses = []
        
        for i in range(-period, 0):
            change = self.data[i]['close'] - self.data[i-1]['close']
            if change > 0:
                gains.append(change)
            else:
                losses.append(abs(change))
        
        avg_gain = sum(gains) / period if gains else 0.0001
        avg_loss = sum(losses) / period if losses else 0.0001
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    # Tool 12: ADX
    def calculate_adx(self, period=14):
        if len(self.data) < period + 1:
            return {"adx": 25, "plus_di": 25, "minus_di": 25}
        
        plus_dm_sum = 0
        minus_dm_sum = 0
        tr_sum = 0
        
        for i in range(-period, 0):
            high = self.data[i]['high']
            low = self.data[i]['low']
            prev_high = self.data[i-1]['high']
            prev_low = self.data[i-1]['low']
            prev_close = self.data[i-1]['close']
            
            up_move = high - prev_high
            down_move = prev_low - low
            
            plus_dm = up_move if up_move > down_move and up_move > 0 else 0
            minus_dm = down_move if down_move > up_move and down_move > 0 else 0
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            
            plus_dm_sum += plus_dm
            minus_dm_sum += minus_dm
            tr_sum += tr
        
        plus_di = (plus_dm_sum / tr_sum) * 100 if tr_sum > 0 else 0
        minus_di = (minus_dm_sum / tr_sum) * 100 if tr_sum > 0 else 0
        
        dx = abs(plus_di - minus_di) / (plus_di + minus_di) * 100 if (plus_di + minus_di) > 0 else 0
        adx = dx  # Simplified
        
        return {"adx": round(adx, 2), "plus_di": round(plus_di, 2), "minus_di": round(minus_di, 2)}
    
    # Tool 13: EMA
    def calculate_ema(self, period):
        if len(self.data) < period:
            return self.data[-1]['close']
        
        multiplier = 2 / (period + 1)
        ema = self.data[-period]['close']
        
        for i in range(-period + 1, 0):
            ema = (self.data[i]['close'] - ema) * multiplier + ema
        
        return ema

# ==================================================
# 🛡️ RISK GUARDIAN (Tool 14: Kelly + Chaos)
# ==================================================

class RiskGuardian:
    """Risk management with Kelly Criterion and Chaos Factor."""
    
    # Tool 14a: Kelly Criterion
    def calculate_kelly(self, win_rate, avg_win, avg_loss):
        if avg_loss <= 0:
            return {"recommended": 0}
        
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p
        
        kelly = (p * b - q) / b if b > 0 else 0
        safe_kelly = min(kelly / 2, 0.025)  # Half Kelly, max 2.5%
        
        return {
            "full_kelly": round(kelly * 100, 2),
            "recommended": round(max(0, safe_kelly) * 100, 2),
            "edge": round((p * b - q) * 100, 2)
        }
    
    # Tool 14b: Chaos Factor
    def apply_chaos(self, value, level="medium"):
        variance = {"low": 0.005, "medium": 0.02, "high": 0.05}[level]
        dither = random.gauss(0, variance)
        chaotic = round(value * (1 + dither), random.choice([2, 3, 4]))
        delay = max(0.15, random.weibullvariate(0.5, 1.5))
        
        return {"original": value, "chaotic": chaotic, "delay": round(delay, 3)}

# ==================================================
# 🎮 TRADING SIMULATION ENGINE
# ==================================================

class TradingSimulation:
    """Complete trading simulation using all 14 tools."""
    
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.trades = []
        self.position = None
        
    def run_simulation(self, num_trades=10):
        """Run multiple trading scenarios."""
        
        print("\n" + "=" * 70)
        print("    🤖 AI TRADING BOT SIMULATION (14 TOOLS)")
        print("=" * 70)
        print(f"    Initial Capital: ${self.initial_capital:,.2f}")
        print("=" * 70)
        
        for i in range(num_trades):
            print(f"\n{'─' * 70}")
            print(f"📊 TRADE #{i + 1}")
            print(f"{'─' * 70}")
            
            # Generate market scenario
            data, scenario = generate_market_scenario()
            print(f"\n🌍 Market Scenario: {scenario.upper()}")
            print(f"   Current Price: ${data[-1]['close']:.2f}")
            
            # Initialize brains
            scalper = ScalpingBrain(data)
            strategist = LongTermBrain(data)
            guardian = RiskGuardian()
            
            # ===== TOOL ANALYSIS =====
            print(f"\n📈 SCALPING BRAIN ANALYSIS:")
            
            # Tool 1-2: ATR & Stops
            atr = scalper.calculate_atr()
            print(f"   [1] ATR(14): {atr:.4f}")
            
            # Tool 3: S/R Levels
            sr = scalper.calculate_sr_levels()
            print(f"   [3] Support: ${sr['support']:.2f} | Resistance: ${sr['resistance']:.2f}")
            
            # Tool 4: Rejection Candle
            rejection = scalper.detect_rejection_candle()
            print(f"   [4] Pin Bar: Bull={rejection['bullish']} | Bear={rejection['bearish']}")
            
            # Tool 5: POC
            poc = scalper.calculate_poc()
            print(f"   [5] POC (Volume Profile): ${poc:.2f}")
            
            # Tool 6: VWAP
            vwap = scalper.calculate_vwap()
            print(f"   [6] VWAP: ${vwap:.2f}")
            
            # Tool 7: Footprint
            footprint = scalper.calculate_footprint_score()
            print(f"   [7] Footprint Delta: {footprint:.3f}")
            
            # Tool 8: Algo Score
            algo = scalper.calculate_algo_score()
            print(f"   [8] Algo Score: BUY={algo['buy_score']:.1f} | SELL={algo['sell_score']:.1f}")
            
            # Tool 9: Supertrend
            supertrend = scalper.calculate_supertrend()
            print(f"   [9] Supertrend: {supertrend['trend_name']}")
            
            print(f"\n📉 LONG TERM BRAIN ANALYSIS:")
            
            # Tool 11: RSI
            rsi = strategist.calculate_rsi()
            print(f"   [11] RSI(14): {rsi}")
            
            # Tool 12: ADX
            adx = strategist.calculate_adx()
            print(f"   [12] ADX: {adx['adx']} | +DI: {adx['plus_di']} | -DI: {adx['minus_di']}")
            
            # Tool 13: EMA
            ema20 = strategist.calculate_ema(20)
            ema50 = strategist.calculate_ema(50) if len(data) >= 50 else ema20
            print(f"   [13] EMA20: ${ema20:.2f} | EMA50: ${ema50:.2f}")
            
            # ===== DECISION ENGINE =====
            print(f"\n🧠 AI DECISION ENGINE:")
            
            # Calculate composite signal
            buy_signals = 0
            sell_signals = 0
            
            # Supertrend bias
            if supertrend['trend'] == 1:
                buy_signals += 2
            else:
                sell_signals += 2
            
            # RSI conditions
            if rsi < 30:
                buy_signals += 1.5
            elif rsi > 70:
                sell_signals += 1.5
            
            # ADX trend strength
            if adx['adx'] > 25:
                if adx['plus_di'] > adx['minus_di']:
                    buy_signals += 1
                else:
                    sell_signals += 1
            
            # Footprint bias
            if footprint > 0.2:
                buy_signals += 1
            elif footprint < -0.2:
                sell_signals += 1
            
            # Price vs VWAP
            current_price = data[-1]['close']
            if current_price > vwap:
                buy_signals += 0.5
            else:
                sell_signals += 0.5
            
            # Algo score addition
            buy_signals += algo['buy_score']
            sell_signals += algo['sell_score']
            
            total_signals = buy_signals + sell_signals
            buy_confidence = (buy_signals / total_signals * 100) if total_signals > 0 else 50
            
            decision = "BUY" if buy_signals > sell_signals else "SELL" if sell_signals > buy_signals else "HOLD"
            confidence = max(buy_confidence, 100 - buy_confidence)
            
            print(f"   Buy Signals: {buy_signals:.1f} | Sell Signals: {sell_signals:.1f}")
            print(f"   Decision: {decision} | Confidence: {confidence:.1f}%")
            
            # ===== RISK MANAGEMENT =====
            print(f"\n🛡️ RISK GUARDIAN:")
            
            # Tool 14a: Kelly Criterion
            # Simulate historical performance
            win_rate = 0.55 + random.uniform(-0.1, 0.1)
            avg_win = atr * 1.5
            avg_loss = atr * 1.0
            
            kelly = guardian.calculate_kelly(win_rate, avg_win, avg_loss)
            print(f"   [14a] Kelly: Full={kelly['full_kelly']:.1f}% | Safe={kelly['recommended']:.1f}%")
            print(f"         Edge: {kelly['edge']:.1f}%")
            
            # Tool 14b: Chaos Factor
            trade_amount = self.capital * (kelly['recommended'] / 100)
            chaos = guardian.apply_chaos(trade_amount)
            print(f"   [14b] Chaos: ${chaos['original']:.2f} → ${chaos['chaotic']:.2f}")
            print(f"         Human Delay: {chaos['delay']:.3f}s")
            
            # ===== EXECUTE TRADE =====
            if decision != "HOLD" and confidence >= 55:
                is_buy = decision == "BUY"
                stops = scalper.calculate_atr_stops(is_buy)
                
                print(f"\n✅ EXECUTING {decision}:")
                print(f"   Entry: ${stops['entry']:.2f}")
                print(f"   Stop Loss: ${stops['sl']:.2f}")
                print(f"   Take Profit: ${stops['tp']:.2f}")
                print(f"   Position Size: ${chaos['chaotic']:.2f}")
                
                # Simulate outcome based on scenario
                outcome = self._simulate_outcome(scenario, is_buy, stops)
                
                print(f"\n📊 OUTCOME: {outcome['result']}")
                print(f"   Exit Price: ${outcome['exit_price']:.2f}")
                print(f"   P/L: ${outcome['pnl']:.2f} ({outcome['pnl_pct']:.2f}%)")
                
                # Update capital
                self.capital += outcome['pnl']
                self.trades.append(outcome)
            else:
                print(f"\n⏸️ NO TRADE: Confidence too low ({confidence:.1f}%)")
        
        # ===== FINAL REPORT =====
        self._print_summary()
    
    def _simulate_outcome(self, scenario, is_buy, stops):
        """Simulate trade outcome based on market scenario."""
        
        # Base probabilities adjusted by scenario
        scenario_probs = {
            "strong_uptrend": {"buy_win": 0.75, "sell_win": 0.30},
            "strong_downtrend": {"buy_win": 0.30, "sell_win": 0.75},
            "sideways": {"buy_win": 0.45, "sell_win": 0.45},
            "volatile_up": {"buy_win": 0.60, "sell_win": 0.40},
            "volatile_down": {"buy_win": 0.40, "sell_win": 0.60},
        }
        
        probs = scenario_probs.get(scenario, {"buy_win": 0.50, "sell_win": 0.50})
        win_prob = probs["buy_win"] if is_buy else probs["sell_win"]
        
        won = random.random() < win_prob
        
        if won:
            exit_price = stops['tp']
            result = "WIN ✅"
        else:
            exit_price = stops['sl']
            result = "LOSS ❌"
        
        if is_buy:
            pnl_pct = ((exit_price - stops['entry']) / stops['entry']) * 100
        else:
            pnl_pct = ((stops['entry'] - exit_price) / stops['entry']) * 100
        
        position_size = self.capital * 0.02  # 2% risk
        pnl = position_size * (pnl_pct / 100)
        
        return {
            "result": result,
            "exit_price": exit_price,
            "pnl": pnl,
            "pnl_pct": pnl_pct,
            "won": won
        }
    
    def _print_summary(self):
        """Print final simulation summary."""
        
        print("\n" + "=" * 70)
        print("    📊 SIMULATION SUMMARY")
        print("=" * 70)
        
        wins = sum(1 for t in self.trades if t['won'])
        losses = len(self.trades) - wins
        win_rate = (wins / len(self.trades) * 100) if self.trades else 0
        
        total_pnl = self.capital - self.initial_capital
        roi = (total_pnl / self.initial_capital) * 100
        
        print(f"\n   📈 Performance Metrics:")
        print(f"   ├─ Trades: {len(self.trades)}")
        print(f"   ├─ Wins: {wins} | Losses: {losses}")
        print(f"   ├─ Win Rate: {win_rate:.1f}%")
        print(f"   ├─ Initial Capital: ${self.initial_capital:,.2f}")
        print(f"   ├─ Final Capital: ${self.capital:,.2f}")
        print(f"   ├─ Total P/L: ${total_pnl:,.2f}")
        print(f"   └─ ROI: {roi:.2f}%")
        
        verdict = "🎯 BOT IS PROFITABLE!" if total_pnl > 0 else "⚠️ BOT NEEDS OPTIMIZATION"
        print(f"\n   {verdict}")
        print("=" * 70)

# ==================================================
# 🚀 RUN SIMULATION
# ==================================================

if __name__ == "__main__":
    sim = TradingSimulation(initial_capital=10000)
    sim.run_simulation(num_trades=10)
