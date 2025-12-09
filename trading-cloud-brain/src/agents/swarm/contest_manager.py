"""
🏆 Contest Manager - مدير المنافسة
Agent Competition & Safety Systems

AlphaAxiom Learning Loop v2.0
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

This module implements:
- Agent Ranking & Competition (تصنيف وتنافس الوكلاء)
- Circuit Breaker Pattern (قاطع الدائرة)
- Data Freshness Validation (التحقق من حداثة البيانات)
- Emergency Stop System (نظام الإيقاف الطارئ)
- Slippage Control (التحكم في الانزلاق)

Reference: Research document on Mini-Agent Swarm architecture
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List

from .base_mini_agent import (
    AgentSignal,
    SignalType,
    MarketRegime,
    BaseMiniAgent,
)
from .performance_monitor import (
    PerformanceMonitor,
    AgentMemoryRecord,
    EnsembleDecision,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 DATA STRUCTURES | هياكل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CircuitState(Enum):
    """Circuit breaker states | حالات قاطع الدائرة"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Emergency stop active
    HALF_OPEN = "HALF_OPEN"  # Testing recovery


class OrderType(Enum):
    """Order execution types | أنواع الأوامر"""
    MARKET = "MARKET"      # Market order
    LIMIT = "LIMIT"        # Limit order (slippage control)


@dataclass
class AgentRanking:
    """
    Agent ranking in the competition
    ترتيب الوكيل في المنافسة
    """
    agent_name: str
    rank: int  # 1-4
    score: float
    weight_multiplier: float  # Applied to base weight
    is_silenced: bool  # Zero weight if True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "rank": self.rank,
            "score": self.score,
            "weight_multiplier": self.weight_multiplier,
            "is_silenced": self.is_silenced,
        }


@dataclass
class CircuitBreakerState:
    """
    Circuit breaker state tracking
    تتبع حالة قاطع الدائرة
    """
    state: CircuitState
    consecutive_failures: int
    daily_loss_percent: float
    last_failure_time: Optional[str]
    recovery_attempts: int
    last_check_time: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "consecutive_failures": self.consecutive_failures,
            "daily_loss_percent": self.daily_loss_percent,
            "last_failure_time": self.last_failure_time,
            "recovery_attempts": self.recovery_attempts,
            "last_check_time": self.last_check_time,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CircuitBreakerState":
        data["state"] = CircuitState(data["state"])
        return cls(**data)
    
    @classmethod
    def default(cls) -> "CircuitBreakerState":
        return cls(
            state=CircuitState.CLOSED,
            consecutive_failures=0,
            daily_loss_percent=0.0,
            last_failure_time=None,
            recovery_attempts=0,
            last_check_time=datetime.now().isoformat(),
        )


@dataclass
class DataFreshnessCheck:
    """
    Result of data freshness validation
    نتيجة التحقق من حداثة البيانات
    """
    is_fresh: bool
    data_age_seconds: int
    max_age_seconds: int
    source: str
    timestamp: str
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_fresh": self.is_fresh,
            "data_age_seconds": self.data_age_seconds,
            "max_age_seconds": self.max_age_seconds,
            "source": self.source,
            "timestamp": self.timestamp,
            "reason": self.reason,
        }


@dataclass
class SwarmContestState:
    """
    Complete contest state for the swarm
    حالة المنافسة الكاملة للسرب
    """
    rankings: List[AgentRanking]
    circuit_breaker: CircuitBreakerState
    last_contest_update: str
    total_trades_today: int
    winning_trades_today: int
    losing_trades_today: int
    is_trading_allowed: bool
    reason_if_blocked: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "rankings": [r.to_dict() for r in self.rankings],
            "circuit_breaker": self.circuit_breaker.to_dict(),
            "last_contest_update": self.last_contest_update,
            "total_trades_today": self.total_trades_today,
            "winning_trades_today": self.winning_trades_today,
            "losing_trades_today": self.losing_trades_today,
            "is_trading_allowed": self.is_trading_allowed,
            "reason_if_blocked": self.reason_if_blocked,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏆 CONTEST MANAGER | مدير المنافسة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ContestManager:
    """
    Manages agent competition, ranking, and safety systems
    إدارة منافسة وتصنيف الوكلاء وأنظمة الأمان
    
    Features:
    - Dynamic agent ranking with weight multipliers
    - Circuit breaker for emergency protection
    - Data freshness validation
    - Slippage control via limit orders
    """
    
    # Circuit Breaker thresholds
    MAX_CONSECUTIVE_FAILURES = 3
    MAX_DAILY_LOSS_PERCENT = 5.0
    HALF_OPEN_WAIT_MINUTES = 15
    
    # Data freshness
    MAX_DATA_AGE_SECONDS = 60  # 1 minute max delay
    
    # Ranking weight multipliers
    TOP_RANK_BOOST = 1.2       # +20% for top 2
    BOTTOM_RANK_PENALTY = 0.9  # -10% for bottom 2
    
    # Volatility threshold for limit orders
    HIGH_VOLATILITY_ATR_THRESHOLD = 0.03  # 3% ATR = high vol
    
    # Agent names
    AGENT_NAMES = [
        "MomentumScout",
        "ReversionHunter",
        "LiquidityWatcher",
        "VolatilitySpiker",
    ]
    
    def __init__(self, env=None):
        """
        Initialize Contest Manager
        
        Args:
            env: Cloudflare Workers environment
        """
        self.env = env
        self.performance_monitor = PerformanceMonitor(env)
        self._circuit_state = CircuitBreakerState.default()
        self._log("🏆 Contest Manager initialized")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎖️ AGENT RANKING & COMPETITION
    # تصنيف ومنافسة الوكلاء
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def rank_agents(
        self,
        symbol: str,
        current_regime: MarketRegime = MarketRegime.RANDOM_WALK
    ) -> List[AgentRanking]:
        """
        Rank agents based on recent performance
        تصنيف الوكلاء بناءً على الأداء الأخير
        
        Ranking algorithm:
        1. Load performance records
        2. Calculate composite score (Sharpe + Win Rate)
        3. Sort by score
        4. Apply weight multipliers (Top 2: +20%, Bottom 2: -10%)
        
        Args:
            symbol: Trading symbol for context
            current_regime: Current market regime
            
        Returns:
            List of AgentRanking sorted by rank
        """
        # Load agent records
        records = await self.performance_monitor._load_agent_records(symbol)
        
        # Calculate composite scores
        agent_scores = []
        for name, record in records.items():
            # Score = 0.6 * normalized_sharpe + 0.4 * win_rate
            sharpe_norm = min(1.0, max(0, (record.sharpe_ratio + 2) / 4))
            score = 0.6 * sharpe_norm + 0.4 * record.win_rate
            agent_scores.append((name, score, record))
        
        # Sort by score descending
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Create rankings with weight multipliers
        rankings = []
        for i, (name, score, record) in enumerate(agent_scores):
            rank = i + 1
            
            # Apply multipliers: Top 2 get boost, Bottom 2 get penalty
            if rank <= 2:
                multiplier = self.TOP_RANK_BOOST
            else:
                multiplier = self.BOTTOM_RANK_PENALTY
            
            # Check if agent should be silenced based on regime
            is_silenced = self._should_silence_agent(
                name, current_regime, record
            )
            
            rankings.append(AgentRanking(
                agent_name=name,
                rank=rank,
                score=score,
                weight_multiplier=0.0 if is_silenced else multiplier,
                is_silenced=is_silenced,
            ))
        
        self._log(f"🎖️ Rankings: {[(r.agent_name, r.rank) for r in rankings]}")
        
        return rankings
    
    def _should_silence_agent(
        self,
        agent_name: str,
        regime: MarketRegime,
        record: AgentMemoryRecord
    ) -> bool:
        """
        Determine if agent should be silenced (weight = 0)
        تحديد ما إذا كان يجب إسكات الوكيل (الوزن = صفر)
        
        Silencing conditions:
        - Momentum in mean-reverting market (H < 0.45)
        - Mean reversion in strong trend (H > 0.55)
        - Any agent with win rate < 30% (recent poor performance)
        """
        # Silence momentum in mean-reverting regime
        if agent_name == "MomentumScout" and regime == MarketRegime.MEAN_REVERTING:
            self._log("🔇 Silencing MomentumScout: Mean-reverting regime")
            return True
        
        # Silence mean reversion in strong trend
        if agent_name == "ReversionHunter" and regime == MarketRegime.TRENDING:
            self._log("🔇 Silencing ReversionHunter: Trending regime")
            return True
        
        # Silence any agent with very poor recent performance
        if record.total_trades >= 10 and record.win_rate < 0.30:
            self._log(f"🔇 Silencing {agent_name}: Win rate {record.win_rate:.1%}")
            return True
        
        return False
    
    def apply_rankings_to_agents(
        self,
        agents: List[BaseMiniAgent],
        rankings: List[AgentRanking]
    ) -> None:
        """
        Apply ranking weights and pause status to agents
        تطبيق أوزان التصنيف وحالة الإيقاف على الوكلاء
        """
        ranking_map = {r.agent_name: r for r in rankings}
        
        for agent in agents:
            agent_name = agent.__class__.__name__
            if agent_name in ranking_map:
                ranking = ranking_map[agent_name]
                agent.current_weight = ranking.weight_multiplier
                agent.is_paused = ranking.is_silenced
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ⚡ CIRCUIT BREAKER PATTERN
    # نمط قاطع الدائرة
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def check_circuit_breaker(self) -> bool:
        """
        Check if trading is allowed based on circuit breaker state
        التحقق من السماح بالتداول بناءً على حالة قاطع الدائرة
        
        Returns:
            True if trading allowed, False if blocked
        """
        # Load state from KV
        state = await self._load_circuit_state()
        
        if state.state == CircuitState.OPEN:
            # Check if we can transition to half-open
            if state.last_failure_time:
                last_failure = datetime.fromisoformat(state.last_failure_time)
                wait_time = timedelta(minutes=self.HALF_OPEN_WAIT_MINUTES)
                
                if datetime.now() - last_failure >= wait_time:
                    # Transition to half-open for testing
                    state.state = CircuitState.HALF_OPEN
                    state.recovery_attempts += 1
                    await self._save_circuit_state(state)
                    self._log("🟡 Circuit breaker: HALF-OPEN (testing recovery)")
                    return True
            
            self._log("🔴 Circuit breaker: OPEN (trading blocked)")
            return False
        
        if state.state == CircuitState.HALF_OPEN:
            # Allow limited trading for testing
            self._log("🟡 Circuit breaker: HALF-OPEN (limited trading)")
            return True
        
        # CLOSED state - normal operation
        return True
    
    async def record_api_failure(self) -> None:
        """
        Record an API failure (Alpaca, data source, etc.)
        تسجيل فشل في واجهة API
        """
        state = await self._load_circuit_state()
        state.consecutive_failures += 1
        state.last_failure_time = datetime.now().isoformat()
        
        # Check if circuit should open
        if state.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            state.state = CircuitState.OPEN
            self._log(f"🔴 Circuit OPENED: {state.consecutive_failures} consecutive failures")
            await self._send_emergency_alert("Circuit breaker opened: API failures")
        
        await self._save_circuit_state(state)
    
    async def record_api_success(self) -> None:
        """
        Record a successful API call (resets failure counter)
        تسجيل نجاح استدعاء API (يعيد تعيين عداد الفشل)
        """
        state = await self._load_circuit_state()
        
        if state.state == CircuitState.HALF_OPEN:
            # Recovery successful, close circuit
            state.state = CircuitState.CLOSED
            self._log("🟢 Circuit CLOSED: Recovery successful")
        
        state.consecutive_failures = 0
        await self._save_circuit_state(state)
    
    async def record_daily_loss(self, loss_percent: float) -> None:
        """
        Record daily loss and check threshold
        تسجيل الخسارة اليومية والتحقق من الحد
        """
        state = await self._load_circuit_state()
        state.daily_loss_percent += loss_percent
        
        # Check if daily loss exceeds threshold
        if state.daily_loss_percent >= self.MAX_DAILY_LOSS_PERCENT:
            state.state = CircuitState.OPEN
            self._log(f"🔴 Circuit OPENED: Daily loss {state.daily_loss_percent:.1f}%")
            await self._send_emergency_alert(
                f"Circuit breaker opened: Daily loss {state.daily_loss_percent:.1f}%"
            )
        
        await self._save_circuit_state(state)
    
    async def reset_daily_counters(self) -> None:
        """Reset daily counters (call at market open)"""
        state = await self._load_circuit_state()
        state.daily_loss_percent = 0.0
        
        # If circuit was open due to daily loss, allow retry
        if state.state == CircuitState.OPEN:
            state.state = CircuitState.HALF_OPEN
            self._log("🟡 Daily reset: Circuit set to HALF-OPEN")
        
        await self._save_circuit_state(state)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 DATA FRESHNESS VALIDATION
    # التحقق من حداثة البيانات
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def validate_data_freshness(
        self,
        data_timestamp: int,
        source: str = "Alpaca"
    ) -> DataFreshnessCheck:
        """
        Validate that market data is fresh enough for trading
        التحقق من أن بيانات السوق حديثة بما يكفي للتداول
        
        Args:
            data_timestamp: Unix timestamp of latest candle
            source: Data source name
            
        Returns:
            DataFreshnessCheck with validation result
        """
        current_time = int(datetime.now().timestamp())
        age_seconds = current_time - data_timestamp
        
        is_fresh = age_seconds <= self.MAX_DATA_AGE_SECONDS
        
        reason = ""
        if not is_fresh:
            reason = (
                f"Data too old: {age_seconds}s > {self.MAX_DATA_AGE_SECONDS}s max. "
                f"Possible network delay or market closed."
            )
            self._log(f"⚠️ Stale data from {source}: {age_seconds}s old")
        
        return DataFreshnessCheck(
            is_fresh=is_fresh,
            data_age_seconds=age_seconds,
            max_age_seconds=self.MAX_DATA_AGE_SECONDS,
            source=source,
            timestamp=datetime.now().isoformat(),
            reason=reason,
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💹 SLIPPAGE CONTROL
    # التحكم في الانزلاق
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def determine_order_type(
        self,
        current_atr_percent: float,
        signal: AgentSignal
    ) -> OrderType:
        """
        Determine order type based on volatility
        تحديد نوع الأمر بناءً على التقلبات
        
        Use limit orders during high volatility to control slippage
        
        Args:
            current_atr_percent: ATR as percentage of price
            signal: The trading signal
            
        Returns:
            LIMIT for high volatility, MARKET otherwise
        """
        if current_atr_percent >= self.HIGH_VOLATILITY_ATR_THRESHOLD:
            self._log(f"📉 High volatility ({current_atr_percent:.2%}): Using LIMIT order")
            return OrderType.LIMIT
        
        return OrderType.MARKET
    
    def calculate_limit_price(
        self,
        current_price: float,
        signal_type: SignalType,
        slippage_buffer: float = 0.001  # 0.1% buffer
    ) -> float:
        """
        Calculate limit price with slippage buffer
        حساب سعر الحد مع هامش الانزلاق
        """
        if signal_type == SignalType.BUY:
            # Bid slightly above current for fills
            return current_price * (1 + slippage_buffer)
        else:
            # Ask slightly below current for fills
            return current_price * (1 - slippage_buffer)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🚀 COMPLETE ORCHESTRATION
    # التنسيق الكامل
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def run_contest_cycle(
        self,
        agents: List[BaseMiniAgent],
        symbol: str,
        market_data: Dict[str, Any],
        regime: MarketRegime = MarketRegime.RANDOM_WALK,
        is_squeeze: bool = False
    ) -> Optional[EnsembleDecision]:
        """
        Complete contest cycle orchestration
        دورة المنافسة الكاملة
        
        Pipeline:
        1. Check circuit breaker
        2. Validate data freshness
        3. Rank agents
        4. Apply weights
        5. Collect signals
        6. Make ensemble decision
        
        Args:
            agents: List of mini-agents
            symbol: Trading symbol
            market_data: Current market data
            regime: Detected market regime
            is_squeeze: Volatility squeeze detected
            
        Returns:
            EnsembleDecision or None if blocked
        """
        self._log(f"🏁 Starting contest cycle for {symbol}")
        
        # Step 1: Check circuit breaker
        if not await self.check_circuit_breaker():
            self._log("🛑 Contest blocked: Circuit breaker OPEN")
            return None
        
        # Step 2: Validate data freshness
        data_ts = market_data.get("timestamp", 0)
        freshness = self.validate_data_freshness(data_ts)
        if not freshness.is_fresh:
            self._log(f"🛑 Contest blocked: {freshness.reason}")
            return None
        
        # Step 3: Rank agents
        rankings = await self.rank_agents(symbol, regime)
        
        # Step 4: Apply rankings to agents
        self.apply_rankings_to_agents(agents, rankings)
        
        # Step 5: Collect signals from all active agents
        signals = []
        for agent in agents:
            if not agent.is_paused:
                try:
                    signal = await agent.analyze_market(symbol, market_data)
                    if signal:
                        signals.append(signal)
                except Exception as e:
                    self._log(f"❌ Error from {agent._agent_name}: {e}")
                    await self.record_api_failure()
        
        if not signals:
            self._log("⚠️ No signals generated")
            return None
        
        # Record success (at least one signal generated)
        await self.record_api_success()
        
        # Step 6: Make ensemble decision
        decision = await self.performance_monitor.make_ensemble_decision(
            agent_signals=signals,
            symbol=symbol,
            regime=regime,
            is_squeeze_breakout=is_squeeze,
        )
        
        self._log(f"✅ Contest complete: {decision.signal_type.value}")
        
        return decision
    
    async def process_trade_outcome(
        self,
        signal: AgentSignal,
        price_path: List[Dict]
    ) -> None:
        """
        Process trade outcome and update agent weights
        معالجة نتيجة الصفقة وتحديث أوزان الوكلاء
        """
        # Label the trade using Triple Barrier
        label = self.performance_monitor.label_trade(signal, price_path)
        
        # Load and update agent record
        records = await self.performance_monitor._load_agent_records(signal.symbol)
        
        if signal.agent_name in records:
            updated = self.performance_monitor.update_agent_weights(
                signal.agent_name,
                label,
                records[signal.agent_name]
            )
            records[signal.agent_name] = updated
            
            # Save updated records
            await self.performance_monitor.save_agent_records(
                signal.symbol, records
            )
        
        # Record loss if applicable
        if label.label == -1:
            await self.record_daily_loss(abs(label.pnl_percent))
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💾 KV STORAGE
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def _load_circuit_state(self) -> CircuitBreakerState:
        """Load circuit breaker state from KV"""
        try:
            if self.env and hasattr(self.env, 'SWARM_MEMORY'):
                data_str = await self.env.SWARM_MEMORY.get("circuit_breaker_state")
                if data_str:
                    return CircuitBreakerState.from_dict(json.loads(data_str))
        except Exception as e:
            self._log(f"⚠️ Error loading circuit state: {e}")
        
        return CircuitBreakerState.default()
    
    async def _save_circuit_state(self, state: CircuitBreakerState) -> None:
        """Save circuit breaker state to KV"""
        try:
            state.last_check_time = datetime.now().isoformat()
            if self.env and hasattr(self.env, 'SWARM_MEMORY'):
                await self.env.SWARM_MEMORY.put(
                    "circuit_breaker_state",
                    json.dumps(state.to_dict())
                )
        except Exception as e:
            self._log(f"❌ Error saving circuit state: {e}")
    
    async def _send_emergency_alert(self, message: str) -> None:
        """Send emergency alert via Telegram"""
        self._log(f"🚨 EMERGENCY: {message}")
        
        # In real implementation, send via Telegram webhook
        # try:
        #     webhook_url = self.env.TELEGRAM_WEBHOOK
        #     payload = {"text": f"🚨 EMERGENCY: {message}"}
        #     await fetch(webhook_url, method="POST", body=json.dumps(payload))
        # except Exception as e:
        #     self._log(f"Failed to send alert: {e}")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 STATUS & MONITORING
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_contest_state(self, symbol: str) -> SwarmContestState:
        """Get complete contest state for monitoring"""
        rankings = await self.rank_agents(symbol)
        circuit_state = await self._load_circuit_state()
        
        is_allowed = circuit_state.state != CircuitState.OPEN
        reason = ""
        if not is_allowed:
            reason = f"Circuit breaker OPEN: {circuit_state.consecutive_failures} failures"
        
        return SwarmContestState(
            rankings=rankings,
            circuit_breaker=circuit_state,
            last_contest_update=datetime.now().isoformat(),
            total_trades_today=0,  # Would load from KV
            winning_trades_today=0,
            losing_trades_today=0,
            is_trading_allowed=is_allowed,
            reason_if_blocked=reason,
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get Contest Manager status"""
        return {
            "name": "ContestManager",
            "version": "1.0.0",
            "max_consecutive_failures": self.MAX_CONSECUTIVE_FAILURES,
            "max_daily_loss_percent": self.MAX_DAILY_LOSS_PERCENT,
            "max_data_age_seconds": self.MAX_DATA_AGE_SECONDS,
            "top_rank_boost": self.TOP_RANK_BOOST,
            "bottom_rank_penalty": self.BOTTOM_RANK_PENALTY,
        }
    
    def _log(self, message: str) -> None:
        """Print log with prefix"""
        print(f"[ContestManager] {message}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📅 CRON TRIGGER HANDLER
# معالج المشغل الزمني
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def on_scheduled(env, ctx) -> None:
    """
    Cron Trigger handler for scheduled swarm execution
    معالج المشغل الزمني لتنفيذ السرب المجدول
    
    Called every 15 minutes during trading hours
    يتم استدعاؤه كل 15 دقيقة خلال ساعات التداول
    
    wrangler.toml config:
    [triggers]
    crons = ["*/15 13-21 * * 1-5"]
    """
    from .base_mini_agent import get_all_agents
    
    print("⏰ Cron trigger: Starting swarm cycle")
    
    # Initialize components
    contest_manager = ContestManager(env)
    agents = get_all_agents(env)
    
    # Default watchlist
    symbols = ["BTCUSD", "ETHUSD", "SPY"]
    
    for symbol in symbols:
        try:
            # Fetch market data (placeholder - use Alpaca in production)
            market_data = {
                "symbol": symbol,
                "timestamp": int(datetime.now().timestamp()),
                "ohlcv": [],  # Would fetch from Alpaca
            }
            
            # Run contest cycle
            decision = await contest_manager.run_contest_cycle(
                agents=agents,
                symbol=symbol,
                market_data=market_data,
                regime=MarketRegime.RANDOM_WALK,
            )
            
            if decision and decision.signal_type != SignalType.HOLD:
                print(f"📊 {symbol}: {decision.signal_type.value} @ {decision.position_size:.1%}")
                
                # Execute trade via Alpaca Paper API
                # await execute_alpaca_trade(env, decision)
                
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            await contest_manager.record_api_failure()
    
    print("✅ Cron cycle complete")
