"""
🧠 THE CENSOR BRAIN - Decision Engine
Acts as the supreme gatekeeper for all trading decisions.
Integrates "The Market Regime Filter" to prevent trading in hostile environments.

Logic:
1. Check Market Regime (Dream Engine / Chaos Theory).
   - If CHOPPY or HIGH_VOL -> HOLD immediately.
   - If TRENDING -> Proceed to AI Analysis.
2. If Trending, trigger AI Council (Gemini + Perplexity).
3. Synthesize Signal + Confidence.
4. Log to BigQuery.
"""

import json
import sys
import os
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

# 🛠️ SYSTEM PATH HACK: Enable importing from 'trading-cloud-brain' (hyphenated dir)
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up to Root: backend/app/core -> backend/app -> backend -> ROOT
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
brain_src = os.path.join(root_dir, "trading-cloud-brain/src")

if brain_src not in sys.path:
    sys.path.append(brain_src)

try:
    from dream_engine import DreamMachine
except ImportError:
    DreamMachine = None
    print("⚠️ [DecisionEngine] DreamMachine import failed. Using Simulation Mode.")

try:
    from data.bq_sink import BigQuerySink
except ImportError:
    BigQuerySink = None

# 🚀 AlphaAPI Gateway - Fire-and-Forget Broadcaster
try:
    from .signal_broadcaster import broadcaster
except ImportError:
    broadcaster = None
    print("⚠️ [DecisionEngine] SignalBroadcaster not available.")


class MarketRegime(Enum):
    TRENDING = "TRENDING"
    CHOPPY = "CHOPPY"
    HIGH_VOL = "HIGH_VOL"
    UNKNOWN = "UNKNOWN"


class DecisionEngine:
    """
    The Central Nervous System for Trade Execution.
    Enforces "Survival First" by censoring trades in bad regimes.
    """
    
    def __init__(self, context: Dict[str, Any] = None):
        self.context = context or {}
        # Sensitivity thresholds derived from Backtest
        self.DREAM_THRESHOLD_CHAOS = 70.0  # Above 70 = High Vol/Chaos
        self.DREAM_THRESHOLD_ORDER = 30.0  # Below 30 = Trending/Order
    
    def get_market_regime(self, market_data: list) -> MarketRegime:
        """
        Determines the current market regime using Chaos Theory (Dream Machine).
        """
        if not market_data:
            return MarketRegime.UNKNOWN
            
        # 1. Use DreamMachine if available (PREFERRED)
        if DreamMachine:
            engine = DreamMachine(market_data)
            score_data = engine.get_dream_score()
            score = score_data['score']
            is_chaotic = score_data['is_chaotic']
            
            # Primary Classification (Dream/Chaos Theory)
            if score >= self.DREAM_THRESHOLD_CHAOS:
                return MarketRegime.HIGH_VOL
            elif score <= self.DREAM_THRESHOLD_ORDER:
                return MarketRegime.TRENDING
            
            # Secondary Classification for Ambiguous Scores (30-70)
            # Use Trend Efficiency Ratio (ER) to rescue strong trends that look "chaotic" due to speed
            try:
                closes = [c['close'] for c in market_data]
                if len(closes) > 10:
                    net_change = abs(closes[-1] - closes[-10])
                    total_path = sum(abs(closes[i] - closes[i-1]) for i in range(len(closes)-9, len(closes)))
                    efficiency_ratio = net_change / total_path if total_path > 0 else 0
                    
                    # If price moved in a straight line (ER > 0.5), it is Trending regardless of Chaos score
                    if efficiency_ratio > 0.5:
                        return MarketRegime.TRENDING
            except Exception:
                pass
                
            return MarketRegime.CHOPPY
        
        # 2. Simulation Mode (Fallback)
        # Improved logic to distinguish TREND from VOLATILITY
        closes = [c['close'] for c in market_data]
        if len(closes) < 10: 
            return MarketRegime.UNKNOWN
            
        # A. Calculate volatility (Range / Price)
        recent_range = max(closes[-10:]) - min(closes[-10:])
        volatility_pct = recent_range / closes[-1]
        
        # B. Calculate Directional Strength (ADX-lite proxy)
        # Check if price is consistently moving in one direction
        direction = closes[-1] - closes[-10]
        uni_directional_move = abs(direction)
        noise = sum(abs(closes[i] - closes[i-1]) for i in range(len(closes)-9, len(closes)))
        efficiency_ratio = uni_directional_move / noise if noise > 0 else 0
        
        # C. Classification Logic
        if efficiency_ratio > 0.6: 
            # Very efficient, smooth move = Trending (regardless of volatility magnitude)
            return MarketRegime.TRENDING
            
        if volatility_pct > 0.02: 
            # High volatility but low efficiency = High Vol/Chaos
            return MarketRegime.HIGH_VOL
            
        if volatility_pct < 0.005:
            # Low volatility, low efficiency = Dead/Choppy
            return MarketRegime.CHOPPY
            
        # Default fallback
        # Check moving average alignment
        ma_20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else sum(closes) / len(closes)
        dist_from_ma = (closes[-1] - ma_20) / ma_20
        
        if abs(dist_from_ma) > 0.01: # 1% away from MA
            return MarketRegime.TRENDING
            
        return MarketRegime.CHOPPY

    def calculate_max_position_size(self, price: float, account_info: dict, stop_loss: float = 0) -> float:
        """
        Calculates max position size based on 1% risk cap.
        From Jules' RiskGuardian logic.
        """
        equity = float(account_info.get("equity", 0))
        if equity <= 0: return 0
        
        # Rule: Max Risk per trade = 1% of Equity
        max_risk_amount = equity * 0.01
        
        if stop_loss > 0:
            risk_per_unit = abs(price - stop_loss)
            if risk_per_unit > 0:
                max_qty = max_risk_amount / risk_per_unit
                return round(max_qty, 4)
        
        # Fallback if no SL: Cap notional value at 5% of equity (Conservative) or using implied volatility
        # For simplicity/safety, we'll cap nominal exposure at 2% risk equivalent assuming a 50% drop??
        # Better: Assume 50% crash risk -> 1% of equity / 0.5 = 2% position size
        # Or just stick to the 1% risk rule strictly requiring SL.
        return 0

    async def evaluate_trade(self, symbol: str, market_data: list, account_info: dict) -> Dict[str, Any]:
        """
        Main decision pipeline with UNIFIED RISK LOGIC.
        
        Flow:
        1. Regime Filter (The Censor Brain) -> Stop if Bad
        2. Hard Risk Checks (Kill Switch, News Guard) -> Stop if Bad
        3. AI Analysis (Council) -> Get Signal
        4. Position Sizing (1% Cap) -> Limit Risk
        """
        
        # 🛑 STEP 1: The Regime Filter (Censor Brain)
        regime = self.get_market_regime(market_data)
        
        if regime in [MarketRegime.CHOPPY, MarketRegime.HIGH_VOL]:
            decision = {
                "action": "HOLD",
                "reason": f"RISK_ADJUSTMENT: System optimized for trending markets only. Current Regime: {regime.value}",
                "regime": regime.value,
                "confidence": 0,
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._log_to_bq(decision)
            return decision

        # 🛑 STEP 2: Hard Risk Rules (Jules' RiskGuardian Logic)
        # A. Kill Switch Check (Mocking KV interaction for this core module)
        if self.context.get("panic_mode") == "true":
             return {"action": "HOLD", "reason": "KILL SWITCH ACTIVATED"}

        # B. News Guard (Placeholder logic - would check EconomicCalendar)
        # if self.economic_calendar.is_event_imminent(symbol):
        #    return {"action": "HOLD", "reason": "HIGH IMPACT NEWS IMMINENT"}

        # ✅ STEP 3: AI Council (Only if Trending & Safe)
        ai_signal = await self._call_ai_council(symbol, market_data)
        
        if ai_signal['action'] != "BUY":
            decision = {
                "action": "HOLD", 
                "reason": ai_signal['reason'],
                "regime": regime.value,
                "confidence": ai_signal['confidence']
            }
            await self._log_to_bq(decision)
            return decision

        # 🛑 STEP 4: Position Sizing & 1% Cap (Jules' Logic)
        # Calculate max size allowed
        current_price = market_data[-1]['close'] if market_data else 0
        # Assume AI provided a Stop Loss, or calculate standard ATR stop
        # Mocking ATR stop for calculation: 2% below price
        stop_loss = current_price * 0.98 
        
        max_qty = self.calculate_max_position_size(current_price, account_info, stop_loss)
        
        if max_qty <= 0:
             return {"action": "HOLD", "reason": "Risk Calc Zero or Insufficient Equity"}
             
        decision = {
            "action": "BUY",
            "reason": f"TREND_CONFIRMED ({regime.value}) + {ai_signal['reason']}",
            "regime": regime.value,
            "confidence": ai_signal['confidence'],
            "symbol": symbol,
            "quantity": max_qty,
            "max_risk_cap": "1.0%",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._log_to_bq(decision)
        
        # 🚀 Fire-and-Forget: Broadcast to AlphaAPI Gateway for external clients
        if broadcaster and decision['action'] in ["BUY", "SELL"]:
            broadcaster.broadcast(decision)
        
        return decision

    async def _call_ai_council(self, symbol: str, market_data: list) -> Dict[str, Any]:
        """
        Simulates the AI gathering strategic & tactical intel.
        """
        # Placeholder for Gemini/Perplexity Calls
        # Real impl would use: await agent_router.route("TRADE", symbol)
        return {
            "action": "BUY",
            "confidence": 88,
            "reason": "AI Council Consensus: Breakout imminent supported by volume."
        }

    async def _log_to_bq(self, decision: Dict[str, Any]):
        """Log decision to BigQuery."""
        if BigQuerySink:
            # sink = BigQuerySink()
            # await sink.insert_row("trade_decisions", decision)
            pass
        else:
            print(f"📊 [BQ Log]: {json.dumps(decision)}")