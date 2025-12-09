"""
📊 Performance Monitor Agent - وكيل المراقبة
Signal Integration & Meta-Manager System

AlphaAxiom Learning Loop v2.0
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

This module implements:
- Softmax Ensemble Weighting (دمج الإشارات بالـ Softmax)
- Regime-Based Weight Adjustment (الترجيح القائم على نظام السوق)
- Kelly Criterion Position Sizing (معيار كيلي لحجم الصفقة)
- Triple Barrier Labeling (طريقة الحاجز الثلاثي)

Reference: Research document on Mini-Agent Swarm architecture
"""

import json
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List, Tuple  # noqa: F401

from .base_mini_agent import (
    AgentSignal,
    SignalType,
    MarketRegime,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 DATA STRUCTURES | هياكل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BarrierType(Enum):
    """Triple Barrier types | أنواع الحاجز الثلاثي"""
    UPPER = "UPPER"      # Take profit hit
    LOWER = "LOWER"      # Stop loss hit
    VERTICAL = "VERTICAL"  # Time limit reached


@dataclass
class TradeLabel:
    """
    Trade labeling result using Triple Barrier Method
    نتيجة تسمية الصفقة باستخدام طريقة الحاجز الثلاثي
    """
    signal_id: str
    label: int  # 1 (win), -1 (loss), 0 (neutral)
    barrier_hit: BarrierType
    pnl_percent: float
    duration_minutes: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "label": self.label,
            "barrier_hit": self.barrier_hit.value,
            "pnl_percent": self.pnl_percent,
            "duration_minutes": self.duration_minutes,
        }


@dataclass
class EnsembleDecision:
    """
    Final decision from signal ensemble
    القرار النهائي من دمج الإشارات
    """
    final_signal: float  # -1 to 1
    signal_type: SignalType
    position_size: float  # Kelly-derived position size
    agent_weights: Dict[str, float]
    confidence: float
    symbol: str
    timestamp: int
    regime: MarketRegime
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_signal": self.final_signal,
            "signal_type": self.signal_type.value,
            "position_size": self.position_size,
            "agent_weights": self.agent_weights,
            "confidence": self.confidence,
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "regime": self.regime.value,
            "reasoning": self.reasoning,
        }


@dataclass
class AgentMemoryRecord:
    """
    Agent performance record stored in KV (.idx format)
    سجل أداء الوكيل المخزن في KV
    """
    agent_name: str
    wins: int = 0
    losses: int = 0
    neutral: int = 0
    avg_pnl: float = 0.0
    sharpe_ratio: float = 0.0
    weight_score: float = 0.25  # Default equal weight
    last_updated: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "wins": self.wins,
            "losses": self.losses,
            "neutral": self.neutral,
            "avg_pnl": self.avg_pnl,
            "sharpe_ratio": self.sharpe_ratio,
            "weight_score": self.weight_score,
            "last_updated": self.last_updated,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMemoryRecord":
        return cls(**data)
    
    @property
    def total_trades(self) -> int:
        return self.wins + self.losses + self.neutral
    
    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.5  # Neutral default
        return self.wins / self.total_trades


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧠 PERFORMANCE MONITOR | وكيل المراقبة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PerformanceMonitor:
    """
    Meta-Manager Agent for Signal Ensemble & Performance Tracking
    الوكيل الرئيسي لدمج الإشارات وتتبع الأداء
    
    Implements:
    - Softmax ensemble weighting: W_i = exp(β * P_i) / Σ exp(β * P_j)
    - Regime-based weight adjustment
    - Kelly criterion position sizing
    - Triple barrier trade labeling
    """
    
    # Default parameters
    TEMPERATURE_BETA = 2.0  # Softmax temperature (higher = more selective)
    HALF_KELLY_FACTOR = 0.5  # Conservative position sizing
    
    # Triple Barrier defaults
    DEFAULT_TAKE_PROFIT_PERCENT = 2.0  # Upper barrier
    DEFAULT_STOP_LOSS_PERCENT = 1.0    # Lower barrier
    DEFAULT_TIME_LIMIT_HOURS = 24      # Vertical barrier
    
    # Regime weight multipliers
    LOW_VOL_MR_BOOST = 1.5     # Mean reversion boost in low volatility
    LOW_VOL_MOM_REDUCE = 0.5   # Momentum reduction in low volatility
    SQUEEZE_MR_SILENCE = 0.0   # Silence mean reversion on squeeze breakout
    
    # Agent name mapping
    AGENT_NAMES = [
        "MomentumScout",
        "ReversionHunter",
        "LiquidityWatcher",
        "VolatilitySpiker",
    ]
    
    def __init__(self, env=None):
        """
        Initialize Performance Monitor
        
        Args:
            env: Cloudflare Workers environment for KV access
        """
        self.env = env
        self._log("🧠 Performance Monitor initialized")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎯 SOFTMAX ENSEMBLE WEIGHTING
    # دمج الإشارات بالـ Softmax
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_softmax_weights(
        self,
        performance_scores: Dict[str, float],
        beta: Optional[float] = None
    ) -> Dict[str, float]:
        """
        Calculate Softmax weights for agent ensemble
        حساب أوزان Softmax لمجموعة الوكلاء
        
        Formula: W_i = exp(β * P_i) / Σ exp(β * P_j)
        
        Args:
            performance_scores: {agent_name: sharpe_ratio}
            beta: Temperature parameter (higher = more selective)
            
        Returns:
            Dictionary of agent weights (sum = 1.0)
        """
        if beta is None:
            beta = self.TEMPERATURE_BETA
        
        if not performance_scores:
            # Equal weights if no data
            n = len(self.AGENT_NAMES)
            return {name: 1.0 / n for name in self.AGENT_NAMES}
        
        # Calculate exp(β * P_i) for each agent
        exp_scores = {}
        max_score = max(performance_scores.values())  # For numerical stability
        
        for agent, score in performance_scores.items():
            # Subtract max for numerical stability (prevents overflow)
            exp_scores[agent] = math.exp(beta * (score - max_score))
        
        # Normalize to get probabilities
        total_exp = sum(exp_scores.values())
        
        weights = {}
        for agent, exp_score in exp_scores.items():
            weights[agent] = exp_score / total_exp
        
        self._log(f"📊 Softmax weights: {weights}")
        return weights
    
    def apply_regime_adjustment(
        self,
        base_weights: Dict[str, float],
        regime: MarketRegime,
        is_squeeze_breakout: bool = False
    ) -> Dict[str, float]:
        """
        Adjust weights based on current market regime
        تعديل الأوزان بناءً على نظام السوق الحالي
        
        Args:
            base_weights: Softmax weights before adjustment
            regime: Current market regime (trending/mean-reverting/random)
            is_squeeze_breakout: True if volatility squeeze detected
            
        Returns:
            Adjusted weights (re-normalized to sum=1)
        """
        adjusted = base_weights.copy()
        
        # Squeeze breakout scenario - silence mean reversion
        if is_squeeze_breakout:
            self._log("⚡ Squeeze breakout: Silencing ReversionHunter")
            if "ReversionHunter" in adjusted:
                adjusted["ReversionHunter"] = self.SQUEEZE_MR_SILENCE
        
        # Low volatility / mean-reverting regime
        elif regime == MarketRegime.MEAN_REVERTING:
            self._log("📉 Low volatility regime: Boosting mean reversion")
            if "ReversionHunter" in adjusted:
                adjusted["ReversionHunter"] *= self.LOW_VOL_MR_BOOST
            if "MomentumScout" in adjusted:
                adjusted["MomentumScout"] *= self.LOW_VOL_MOM_REDUCE
        
        # Trending regime - boost momentum
        elif regime == MarketRegime.TRENDING:
            self._log("📈 Trending regime: Boosting momentum")
            if "MomentumScout" in adjusted:
                adjusted["MomentumScout"] *= 1.3
            if "ReversionHunter" in adjusted:
                adjusted["ReversionHunter"] *= 0.7
        
        # Re-normalize to sum=1
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted
    
    def ensemble_signals(
        self,
        agent_signals: List[AgentSignal],
        weights: Dict[str, float]
    ) -> Tuple[float, SignalType, float]:
        """
        Combine agent signals into final ensemble decision
        دمج إشارات الوكلاء في قرار نهائي
        
        Formula: S_final = Σ (W_i * S_i)
        
        Args:
            agent_signals: List of signals from all agents
            weights: Agent weights from softmax
            
        Returns:
            (final_signal: -1 to 1, signal_type, confidence)
        """
        if not agent_signals:
            return (0.0, SignalType.HOLD, 0.0)
        
        # Convert signals to numeric: BUY=1, SELL=-1, HOLD=0
        signal_values = {}
        for signal in agent_signals:
            if signal.signal_type == SignalType.BUY:
                signal_values[signal.agent_name] = signal.confidence
            elif signal.signal_type == SignalType.SELL:
                signal_values[signal.agent_name] = -signal.confidence
            else:
                signal_values[signal.agent_name] = 0.0
        
        # Calculate weighted sum: S_final = Σ (W_i * S_i)
        final_signal = 0.0
        for agent, weight in weights.items():
            if agent in signal_values:
                final_signal += weight * signal_values[agent]
        
        # Determine signal type
        if final_signal > 0.3:
            signal_type = SignalType.BUY
        elif final_signal < -0.3:
            signal_type = SignalType.SELL
        else:
            signal_type = SignalType.HOLD
        
        confidence = abs(final_signal)
        
        self._log(f"🎯 Ensemble: S_final={final_signal:.4f}, Type={signal_type.value}")
        
        return (final_signal, signal_type, confidence)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💰 KELLY CRITERION POSITION SIZING
    # معيار كيلي لتحديد حجم الصفقة
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def calculate_kelly_fraction(
        self,
        win_probability: float,
        reward_risk_ratio: float = 2.0
    ) -> float:
        """
        Calculate Kelly Criterion position size
        حساب حجم الصفقة بمعيار كيلي
        
        Formula: f* = (p(b+1) - 1) / b
        Where:
            p = win probability
            b = reward-to-risk ratio
            
        Uses Half-Kelly for reduced volatility
        
        Args:
            win_probability: Historical win rate (0-1)
            reward_risk_ratio: Expected R:R from trade
            
        Returns:
            Position size as fraction of capital (0-1)
        """
        p = win_probability
        b = reward_risk_ratio
        
        # Kelly formula: f* = (p(b+1) - 1) / b
        kelly_full = (p * (b + 1) - 1) / b
        
        # Apply Half-Kelly for reduced equity curve volatility
        kelly_half = max(0, kelly_full * self.HALF_KELLY_FACTOR)
        
        # Cap at 25% max position
        kelly_capped = min(kelly_half, 0.25)
        
        self._log(f"💰 Kelly: p={p:.2f}, b={b:.1f}, "
                 f"full={kelly_full:.3f}, half={kelly_capped:.3f}")
        
        return kelly_capped
    
    def get_position_size(
        self,
        agent_records: Dict[str, AgentMemoryRecord],
        confidence: float
    ) -> float:
        """
        Get recommended position size based on swarm performance
        
        Args:
            agent_records: Performance records from KV
            confidence: Ensemble signal confidence
            
        Returns:
            Position size as fraction of capital
        """
        # Calculate aggregate win rate across swarm
        total_wins = sum(r.wins for r in agent_records.values())
        total_trades = sum(r.total_trades for r in agent_records.values())
        
        if total_trades < 10:
            # Not enough data, use conservative 5%
            return 0.05
        
        win_rate = total_wins / total_trades
        
        # Use 2:1 R:R as default
        kelly_size = self.calculate_kelly_fraction(win_rate, 2.0)
        
        # Scale by confidence
        final_size = kelly_size * confidence
        
        return final_size
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🏷️ TRIPLE BARRIER LABELING
    # طريقة الحاجز الثلاثي للتسمية
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def label_trade(
        self,
        signal: AgentSignal,
        price_path: List[Dict],
        take_profit_pct: Optional[float] = None,
        stop_loss_pct: Optional[float] = None,
        time_limit_hours: Optional[float] = None
    ) -> TradeLabel:
        """
        Label a trade using Triple Barrier Method
        تسمية الصفقة باستخدام طريقة الحاجز الثلاثي
        
        Barriers:
        - Upper: Take profit level
        - Lower: Stop loss level
        - Vertical: Time limit
        
        Args:
            signal: Original trading signal
            price_path: List of {timestamp, price} during trade
            take_profit_pct: Upper barrier (%)
            stop_loss_pct: Lower barrier (%)
            time_limit_hours: Vertical barrier (hours)
            
        Returns:
            TradeLabel with outcome classification
        """
        if take_profit_pct is None:
            take_profit_pct = self.DEFAULT_TAKE_PROFIT_PERCENT
        if stop_loss_pct is None:
            stop_loss_pct = self.DEFAULT_STOP_LOSS_PERCENT
        if time_limit_hours is None:
            time_limit_hours = self.DEFAULT_TIME_LIMIT_HOURS
        
        entry_price = signal.entry_price
        is_long = signal.signal_type == SignalType.BUY
        
        # Calculate barrier levels
        if is_long:
            upper_barrier = entry_price * (1 + take_profit_pct / 100)
            lower_barrier = entry_price * (1 - stop_loss_pct / 100)
        else:
            upper_barrier = entry_price * (1 - take_profit_pct / 100)
            lower_barrier = entry_price * (1 + stop_loss_pct / 100)
        
        time_limit_minutes = time_limit_hours * 60
        
        # Find which barrier was hit first
        for i, point in enumerate(price_path):
            price = point.get("price", point.get("close", entry_price))
            elapsed_minutes = i  # Assuming 1-minute intervals
            
            # Check upper barrier (take profit)
            if (is_long and price >= upper_barrier) or \
               (not is_long and price <= upper_barrier):
                pnl = take_profit_pct if is_long else take_profit_pct
                return TradeLabel(
                    signal_id=signal.signal_id,
                    label=1,  # Win
                    barrier_hit=BarrierType.UPPER,
                    pnl_percent=pnl,
                    duration_minutes=elapsed_minutes,
                )
            
            # Check lower barrier (stop loss)
            if (is_long and price <= lower_barrier) or \
               (not is_long and price >= lower_barrier):
                pnl = -stop_loss_pct if is_long else -stop_loss_pct
                return TradeLabel(
                    signal_id=signal.signal_id,
                    label=-1,  # Loss
                    barrier_hit=BarrierType.LOWER,
                    pnl_percent=pnl,
                    duration_minutes=elapsed_minutes,
                )
            
            # Check vertical barrier (time limit)
            if elapsed_minutes >= time_limit_minutes:
                current_pnl = ((price / entry_price) - 1) * 100
                if not is_long:
                    current_pnl = -current_pnl
                return TradeLabel(
                    signal_id=signal.signal_id,
                    label=0,  # Neutral
                    barrier_hit=BarrierType.VERTICAL,
                    pnl_percent=current_pnl,
                    duration_minutes=elapsed_minutes,
                )
        
        # If no barrier hit (incomplete data), return neutral
        final_price = price_path[-1].get("price", entry_price) if price_path else entry_price
        final_pnl = ((final_price / entry_price) - 1) * 100
        
        return TradeLabel(
            signal_id=signal.signal_id,
            label=0,
            barrier_hit=BarrierType.VERTICAL,
            pnl_percent=final_pnl,
            duration_minutes=len(price_path),
        )
    
    def update_agent_weights(
        self,
        agent_name: str,
        trade_label: TradeLabel,
        current_record: AgentMemoryRecord
    ) -> AgentMemoryRecord:
        """
        Update agent weights based on trade outcome
        تحديث أوزان الوكيل بناءً على نتيجة الصفقة
        
        Learning feedback:
        - Label=1 (win): Increase weight
        - Label=-1 (loss): Decrease weight
        - Label=0 (neutral): Minimal adjustment
        
        Args:
            agent_name: Name of the agent
            trade_label: Outcome from Triple Barrier
            current_record: Current performance record
            
        Returns:
            Updated AgentMemoryRecord
        """
        record = AgentMemoryRecord(
            agent_name=agent_name,
            wins=current_record.wins,
            losses=current_record.losses,
            neutral=current_record.neutral,
            avg_pnl=current_record.avg_pnl,
            sharpe_ratio=current_record.sharpe_ratio,
            weight_score=current_record.weight_score,
        )
        
        # Update counts
        if trade_label.label == 1:
            record.wins += 1
        elif trade_label.label == -1:
            record.losses += 1
        else:
            record.neutral += 1
        
        # Update average PnL (exponential moving average)
        alpha = 0.1  # Learning rate
        record.avg_pnl = (1 - alpha) * record.avg_pnl + alpha * trade_label.pnl_percent
        
        # Recalculate Sharpe ratio approximation
        # Using simplified formula: (avg_pnl / volatility)
        record.sharpe_ratio = self._estimate_sharpe(record)
        
        # Update weight score (normalized 0-1)
        record.weight_score = self._calculate_weight_score(record)
        
        record.last_updated = datetime.now().isoformat()
        
        self._log(f"📈 Updated {agent_name}: wins={record.wins}, "
                 f"losses={record.losses}, weight={record.weight_score:.3f}")
        
        return record
    
    def _estimate_sharpe(self, record: AgentMemoryRecord) -> float:
        """Estimate Sharpe ratio from record"""
        if record.total_trades < 5:
            return 0.0
        
        # Simple approximation
        win_rate = record.win_rate
        avg_pnl = record.avg_pnl
        
        # Assume volatility proportional to (1 - win_rate)
        volatility = max(0.1, 1 - win_rate)
        
        return avg_pnl / volatility
    
    def _calculate_weight_score(self, record: AgentMemoryRecord) -> float:
        """Calculate normalized weight score"""
        if record.total_trades < 3:
            return 0.25  # Default equal weight
        
        # Combine win rate and Sharpe
        win_factor = record.win_rate
        sharpe_factor = min(1.0, max(0, (record.sharpe_ratio + 2) / 4))
        
        return 0.5 * win_factor + 0.5 * sharpe_factor
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎲 COMPLETE DECISION FLOW
    # تدفق القرار الكامل
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def make_ensemble_decision(
        self,
        agent_signals: List[AgentSignal],
        symbol: str,
        regime: MarketRegime = MarketRegime.RANDOM_WALK,
        is_squeeze_breakout: bool = False
    ) -> EnsembleDecision:
        """
        Complete decision pipeline from signals to action
        خط أنابيب القرار الكامل من الإشارات إلى الإجراء
        
        Pipeline:
        1. Load agent records from KV
        2. Calculate Softmax weights
        3. Apply regime adjustment
        4. Ensemble signals
        5. Calculate Kelly position size
        
        Args:
            agent_signals: Signals from all mini-agents
            symbol: Trading symbol
            regime: Current market regime
            is_squeeze_breakout: Volatility squeeze detected
            
        Returns:
            EnsembleDecision with final action
        """
        # Step 1: Load agent performance from KV
        agent_records = await self._load_agent_records(symbol)
        
        # Step 2: Calculate base Softmax weights
        performance_scores = {
            name: record.sharpe_ratio 
            for name, record in agent_records.items()
        }
        base_weights = self.calculate_softmax_weights(performance_scores)
        
        # Step 3: Apply regime-based adjustment
        adjusted_weights = self.apply_regime_adjustment(
            base_weights, regime, is_squeeze_breakout
        )
        
        # Step 4: Ensemble the signals
        final_signal, signal_type, confidence = self.ensemble_signals(
            agent_signals, adjusted_weights
        )
        
        # Step 5: Calculate position size with Kelly
        position_size = self.get_position_size(agent_records, confidence)
        
        # Build reasoning
        reasoning_parts = []
        for signal in agent_signals:
            reasoning_parts.append(
                f"{signal.agent_name}: {signal.signal_type.value} "
                f"(conf={signal.confidence:.2f}, w={adjusted_weights.get(signal.agent_name, 0):.2f})"
            )
        reasoning = " | ".join(reasoning_parts)
        
        decision = EnsembleDecision(
            final_signal=final_signal,
            signal_type=signal_type,
            position_size=position_size,
            agent_weights=adjusted_weights,
            confidence=confidence,
            symbol=symbol,
            timestamp=int(datetime.now().timestamp()),
            regime=regime,
            reasoning=reasoning,
        )
        
        self._log(f"🎯 Decision: {signal_type.value} @ {position_size:.1%} size")
        
        return decision
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💾 KV STORAGE (.idx FILES)
    # تخزين KV (ملفات .idx)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def _load_agent_records(
        self, 
        symbol: str
    ) -> Dict[str, AgentMemoryRecord]:
        """
        Load agent performance records from Cloudflare KV
        تحميل سجلات أداء الوكلاء من KV
        
        Schema stored in KV (per symbol):
        {
            "symbol": "AAPL",
            "agents": {
                "MomentumScout": {...},
                "ReversionHunter": {...}
            },
            "last_updated": "2025-..."
        }
        """
        records = {}
        
        try:
            if self.env and hasattr(self.env, 'SWARM_MEMORY'):
                # Load from Cloudflare KV
                key = f"swarm_perf_{symbol}"
                data_str = await self.env.SWARM_MEMORY.get(key)
                
                if data_str:
                    data = json.loads(data_str)
                    for name, agent_data in data.get("agents", {}).items():
                        records[name] = AgentMemoryRecord.from_dict(agent_data)
        except Exception as e:
            self._log(f"⚠️ Error loading records: {e}")
        
        # Ensure all agents have a record (default if missing)
        for name in self.AGENT_NAMES:
            if name not in records:
                records[name] = AgentMemoryRecord(agent_name=name)
        
        return records
    
    async def save_agent_records(
        self,
        symbol: str,
        records: Dict[str, AgentMemoryRecord]
    ) -> bool:
        """
        Save agent performance records to Cloudflare KV
        حفظ سجلات أداء الوكلاء في KV
        """
        try:
            data = {
                "symbol": symbol,
                "agents": {
                    name: record.to_dict() 
                    for name, record in records.items()
                },
                "last_updated": datetime.now().isoformat(),
            }
            
            if self.env and hasattr(self.env, 'SWARM_MEMORY'):
                key = f"swarm_perf_{symbol}"
                await self.env.SWARM_MEMORY.put(key, json.dumps(data))
                self._log(f"💾 Saved records for {symbol}")
                return True
            
            return False
            
        except Exception as e:
            self._log(f"❌ Error saving records: {e}")
            return False
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔧 UTILITY METHODS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_status(self) -> Dict[str, Any]:
        """Get Performance Monitor status"""
        return {
            "name": "PerformanceMonitor",
            "version": "1.0.0",
            "temperature_beta": self.TEMPERATURE_BETA,
            "kelly_factor": self.HALF_KELLY_FACTOR,
            "take_profit_pct": self.DEFAULT_TAKE_PROFIT_PERCENT,
            "stop_loss_pct": self.DEFAULT_STOP_LOSS_PERCENT,
            "time_limit_hours": self.DEFAULT_TIME_LIMIT_HOURS,
        }
    
    def _log(self, message: str) -> None:
        """Print log with prefix"""
        print(f"[PerformanceMonitor] {message}")
