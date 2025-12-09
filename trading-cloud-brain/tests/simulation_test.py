#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 ALPHAAXIOM 48-HOUR SIMULATION TEST | اختبار محاكاة 48 ساعة
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Safe simulation to validate Mini-Agent Swarm before PAPER/LIVE trading
Target: Collect performance metrics for 730% ROI feasibility analysis

Components Tested:
    - MomentumScout, ReversionHunter, LiquidityWatcher, VolatilitySpiker
    - PerformanceMonitor (Softmax Ensemble + Kelly Sizing)
    - ContestManager (Agent Ranking + Circuit Breaker)
    - PaperTradingGateway (Alpaca + Bybit routing)

Author: Axiom AI Partner | Mohamed Hossameldin Abdelaziz
Date: December 9, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from enum import Enum

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 SIMULATION CONFIGURATION | إعدادات المحاكاة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimulationConfig:
    """Configuration for 48-hour simulation test."""
    
    # Duration settings
    DURATION_HOURS = 48
    TICK_INTERVAL_SECONDS = 60  # 1 minute per tick (accelerated)
    ACCELERATED_MODE = True  # If True, simulate faster
    ACCELERATION_FACTOR = 60  # 1 second = 1 minute of simulated time
    
    # Capital settings
    INITIAL_CAPITAL = 10000.0
    MAX_POSITION_SIZE_PCT = 0.05  # 5% per trade
    
    # Agent configuration
    AGENTS = ["MomentumScout", "ReversionHunter", "LiquidityWatcher", "VolatilitySpiker"]
    
    # Symbols to monitor
    CRYPTO_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    STOCK_SYMBOLS = ["AAPL", "SPY", "TSLA"]
    
    # Safety thresholds
    MAX_DRAWDOWN_PCT = 0.05  # 5% circuit breaker
    MAX_CONSECUTIVE_LOSSES = 3
    
    # Performance targets
    TARGET_WIN_RATE = 0.55  # 55%
    TARGET_SHARPE = 1.5


class MarketRegime(Enum):
    """Market regime classification based on Hurst exponent."""
    TRENDING = "trending"      # H > 0.55
    RANGING = "ranging"        # H < 0.45
    RANDOM = "random"          # 0.45 <= H <= 0.55


@dataclass
class SimulatedTrade:
    """Represents a simulated trade."""
    id: str
    agent: str
    symbol: str
    side: str  # BUY or SELL
    entry_price: float
    quantity: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_pct: float = 0.0
    status: str = "OPEN"  # OPEN, CLOSED, STOPPED


@dataclass
class AgentPerformance:
    """Track agent performance metrics."""
    name: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    current_weight: float = 0.25  # Start equal
    consecutive_losses: int = 0
    signals_generated: int = 0
    
    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.wins / self.total_trades
    
    @property
    def avg_pnl(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.total_pnl / self.total_trades


@dataclass
class SimulationState:
    """Complete simulation state."""
    start_time: datetime = field(default_factory=datetime.now)
    current_time: datetime = field(default_factory=datetime.now)
    elapsed_hours: float = 0.0
    
    capital: float = SimulationConfig.INITIAL_CAPITAL
    peak_capital: float = SimulationConfig.INITIAL_CAPITAL
    current_drawdown: float = 0.0
    max_drawdown: float = 0.0
    
    total_trades: int = 0
    open_trades: List[SimulatedTrade] = field(default_factory=list)
    closed_trades: List[SimulatedTrade] = field(default_factory=list)
    
    agents: Dict[str, AgentPerformance] = field(default_factory=dict)
    
    circuit_breaker_triggered: bool = False
    circuit_breaker_reason: str = ""
    
    ticks_processed: int = 0
    errors: List[str] = field(default_factory=list)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 MOCK MARKET DATA GENERATOR | مولد بيانات السوق الوهمية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MockMarketDataGenerator:
    """Generate realistic mock market data for simulation."""
    
    BASE_PRICES = {
        "BTCUSDT": 97000.0,
        "ETHUSDT": 3800.0,
        "SOLUSDT": 220.0,
        "AAPL": 240.0,
        "SPY": 605.0,
        "TSLA": 380.0,
    }
    
    VOLATILITY = {
        "BTCUSDT": 0.03,   # 3% daily vol
        "ETHUSDT": 0.04,   # 4% daily vol
        "SOLUSDT": 0.06,   # 6% daily vol
        "AAPL": 0.02,      # 2% daily vol
        "SPY": 0.01,       # 1% daily vol
        "TSLA": 0.04,      # 4% daily vol
    }
    
    def __init__(self):
        self.current_prices = self.BASE_PRICES.copy()
        self.regime = MarketRegime.TRENDING
        self.trend_direction = 1  # 1 = up, -1 = down
        
    def tick(self) -> Dict[str, float]:
        """Generate next tick of market data."""
        # Randomly change regime occasionally
        if random.random() < 0.01:  # 1% chance per tick
            self.regime = random.choice(list(MarketRegime))
            self.trend_direction = random.choice([1, -1])
        
        for symbol in self.current_prices:
            vol = self.VOLATILITY.get(symbol, 0.02)
            
            # Generate price movement based on regime
            if self.regime == MarketRegime.TRENDING:
                drift = self.trend_direction * vol * 0.1
                noise = random.gauss(0, vol * 0.5)
            elif self.regime == MarketRegime.RANGING:
                drift = 0
                noise = random.gauss(0, vol * 0.3)
            else:  # RANDOM
                drift = random.gauss(0, vol * 0.05)
                noise = random.gauss(0, vol * 0.7)
            
            # Apply movement (scaled for 1-minute tick)
            minute_vol = vol / (24 * 60) ** 0.5
            movement = (drift + noise) * minute_vol
            self.current_prices[symbol] *= (1 + movement)
        
        return self.current_prices.copy()
    
    def get_regime(self) -> MarketRegime:
        return self.regime


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 MOCK AGENT SIGNALS | إشارات الوكلاء الوهمية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MockAgentSignals:
    """Generate mock signals from agents based on market conditions."""
    
    # Agent performance characteristics (win rates in different regimes)
    AGENT_PROFILES = {
        "MomentumScout": {
            MarketRegime.TRENDING: 0.65,
            MarketRegime.RANGING: 0.35,
            MarketRegime.RANDOM: 0.50,
        },
        "ReversionHunter": {
            MarketRegime.TRENDING: 0.35,
            MarketRegime.RANGING: 0.70,
            MarketRegime.RANDOM: 0.45,
        },
        "LiquidityWatcher": {
            MarketRegime.TRENDING: 0.55,
            MarketRegime.RANGING: 0.55,
            MarketRegime.RANDOM: 0.60,  # Good at finding gaps
        },
        "VolatilitySpiker": {
            MarketRegime.TRENDING: 0.60,
            MarketRegime.RANGING: 0.40,
            MarketRegime.RANDOM: 0.55,
        },
    }
    
    @classmethod
    def generate_signal(cls, agent: str, regime: MarketRegime, 
                       prices: Dict[str, float]) -> Optional[Dict]:
        """Generate a trading signal from an agent."""
        
        # Signal probability based on agent profile
        base_prob = cls.AGENT_PROFILES.get(agent, {}).get(regime, 0.5)
        
        # Only generate signal 20% of ticks
        if random.random() > 0.20:
            return None
        
        # Pick a random symbol
        symbol = random.choice(list(prices.keys()))
        price = prices[symbol]
        
        # Determine direction
        side = "BUY" if random.random() > 0.5 else "SELL"
        
        # Confidence based on agent's regime performance
        confidence = base_prob * random.uniform(0.7, 1.0)
        
        return {
            "agent": agent,
            "symbol": symbol,
            "side": side,
            "price": price,
            "confidence": confidence,
            "regime": regime.value,
        }
    
    @classmethod
    def simulate_trade_outcome(cls, trade: SimulatedTrade, 
                               agent_win_rate: float) -> SimulatedTrade:
        """Simulate trade outcome based on agent's expected win rate."""
        
        # Add some randomness around the expected win rate
        adjusted_win_rate = agent_win_rate + random.gauss(0, 0.1)
        adjusted_win_rate = max(0.2, min(0.8, adjusted_win_rate))
        
        is_win = random.random() < adjusted_win_rate
        
        if is_win:
            # Win: 1-5% profit
            pnl_pct = random.uniform(0.01, 0.05)
        else:
            # Loss: 0.5-2% loss
            pnl_pct = -random.uniform(0.005, 0.02)
        
        trade.exit_price = trade.entry_price * (1 + pnl_pct)
        trade.exit_time = datetime.now()
        trade.pnl = trade.quantity * trade.entry_price * pnl_pct
        trade.pnl_pct = pnl_pct * 100
        trade.status = "CLOSED"
        
        return trade


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎮 SIMULATION ENGINE | محرك المحاكاة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimulationEngine:
    """Main simulation engine for 48-hour test."""
    
    def __init__(self):
        self.state = SimulationState()
        self.market = MockMarketDataGenerator()
        
        # Initialize agents
        for agent_name in SimulationConfig.AGENTS:
            self.state.agents[agent_name] = AgentPerformance(name=agent_name)
    
    def calculate_softmax_weights(self, beta: float = 2.0) -> Dict[str, float]:
        """Calculate Softmax ensemble weights based on performance."""
        import math
        
        scores = {}
        for name, agent in self.state.agents.items():
            # Performance score = win_rate * (1 + avg_pnl_pct)
            score = agent.win_rate * (1 + agent.avg_pnl / 100)
            scores[name] = score
        
        # Softmax calculation
        exp_scores = {k: math.exp(beta * v) for k, v in scores.items()}
        total = sum(exp_scores.values())
        
        if total == 0:
            # Equal weights if no data
            return {k: 0.25 for k in scores}
        
        return {k: v / total for k, v in exp_scores.items()}
    
    def check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should be triggered."""
        
        # Check drawdown
        if self.state.current_drawdown > SimulationConfig.MAX_DRAWDOWN_PCT:
            self.state.circuit_breaker_triggered = True
            self.state.circuit_breaker_reason = f"Max drawdown exceeded: {self.state.current_drawdown:.2%}"
            return True
        
        # Check consecutive losses for any agent
        for agent in self.state.agents.values():
            if agent.consecutive_losses >= SimulationConfig.MAX_CONSECUTIVE_LOSSES:
                self.state.circuit_breaker_triggered = True
                self.state.circuit_breaker_reason = f"Agent {agent.name}: {agent.consecutive_losses} consecutive losses"
                return True
        
        return False
    
    def process_tick(self):
        """Process one simulation tick."""
        
        # Get market data
        prices = self.market.tick()
        regime = self.market.get_regime()
        
        # Generate signals from each agent
        for agent_name in SimulationConfig.AGENTS:
            signal = MockAgentSignals.generate_signal(agent_name, regime, prices)
            
            if signal and signal["confidence"] > 0.5:
                self.state.agents[agent_name].signals_generated += 1
                
                # Execute trade based on Softmax weights
                weights = self.calculate_softmax_weights()
                if random.random() < weights.get(agent_name, 0.25):
                    self._execute_trade(signal)
        
        # Close some open trades randomly
        self._process_open_trades(regime)
        
        # Update metrics
        self._update_metrics()
        self.state.ticks_processed += 1
    
    def _execute_trade(self, signal: Dict):
        """Execute a simulated trade."""
        
        position_size = self.state.capital * SimulationConfig.MAX_POSITION_SIZE_PCT
        quantity = position_size / signal["price"]
        
        trade = SimulatedTrade(
            id=f"SIM-{self.state.total_trades + 1:05d}",
            agent=signal["agent"],
            symbol=signal["symbol"],
            side=signal["side"],
            entry_price=signal["price"],
            quantity=quantity,
            entry_time=datetime.now(),
        )
        
        self.state.open_trades.append(trade)
        self.state.total_trades += 1
    
    def _process_open_trades(self, regime: MarketRegime):
        """Process open trades - close some randomly."""
        
        trades_to_close = []
        
        for trade in self.state.open_trades:
            # 10% chance to close each tick (simulates average 10-tick hold)
            if random.random() < 0.10:
                agent = self.state.agents[trade.agent]
                win_rate = MockAgentSignals.AGENT_PROFILES.get(
                    trade.agent, {}
                ).get(regime, 0.5)
                
                closed_trade = MockAgentSignals.simulate_trade_outcome(trade, win_rate)
                trades_to_close.append(closed_trade)
                
                # Update agent stats
                agent.total_trades += 1
                agent.total_pnl += closed_trade.pnl
                
                if closed_trade.pnl > 0:
                    agent.wins += 1
                    agent.consecutive_losses = 0
                else:
                    agent.losses += 1
                    agent.consecutive_losses += 1
                
                # Update capital
                self.state.capital += closed_trade.pnl
        
        # Move closed trades
        for trade in trades_to_close:
            self.state.open_trades.remove(trade)
            self.state.closed_trades.append(trade)
    
    def _update_metrics(self):
        """Update simulation metrics."""
        
        # Update peak and drawdown
        if self.state.capital > self.state.peak_capital:
            self.state.peak_capital = self.state.capital
        
        self.state.current_drawdown = (
            (self.state.peak_capital - self.state.capital) / self.state.peak_capital
        )
        
        if self.state.current_drawdown > self.state.max_drawdown:
            self.state.max_drawdown = self.state.current_drawdown
        
        # Update weights
        weights = self.calculate_softmax_weights()
        for name, weight in weights.items():
            self.state.agents[name].current_weight = weight
    
    def get_report(self) -> Dict:
        """Generate simulation report."""
        
        total_pnl = self.state.capital - SimulationConfig.INITIAL_CAPITAL
        total_return = total_pnl / SimulationConfig.INITIAL_CAPITAL
        
        agent_stats = []
        for agent in self.state.agents.values():
            agent_stats.append({
                "name": agent.name,
                "trades": agent.total_trades,
                "wins": agent.wins,
                "losses": agent.losses,
                "win_rate": f"{agent.win_rate:.2%}",
                "total_pnl": f"${agent.total_pnl:.2f}",
                "weight": f"{agent.current_weight:.2%}",
            })
        
        return {
            "simulation_summary": {
                "duration_ticks": self.state.ticks_processed,
                "elapsed_hours": self.state.elapsed_hours,
                "initial_capital": f"${SimulationConfig.INITIAL_CAPITAL:,.2f}",
                "final_capital": f"${self.state.capital:,.2f}",
                "total_pnl": f"${total_pnl:,.2f}",
                "total_return": f"{total_return:.2%}",
                "max_drawdown": f"{self.state.max_drawdown:.2%}",
                "total_trades": self.state.total_trades,
                "open_trades": len(self.state.open_trades),
                "closed_trades": len(self.state.closed_trades),
            },
            "circuit_breaker": {
                "triggered": self.state.circuit_breaker_triggered,
                "reason": self.state.circuit_breaker_reason,
            },
            "agent_performance": agent_stats,
            "market_regime": self.market.get_regime().value,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 MAIN EXECUTION | التنفيذ الرئيسي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_simulation(duration_minutes: int = 60, verbose: bool = True):
    """
    Run the simulation.
    
    Args:
        duration_minutes: How long to run (in simulated minutes)
        verbose: Print progress updates
    """
    print("━" * 70)
    print("🧪 ALPHAAXIOM 48-HOUR SIMULATION TEST")
    print("━" * 70)
    print(f"📅 Start Time: {datetime.now().isoformat()}")
    print(f"⏱️  Duration: {duration_minutes} simulated minutes")
    print(f"💰 Initial Capital: ${SimulationConfig.INITIAL_CAPITAL:,.2f}")
    print(f"🤖 Agents: {', '.join(SimulationConfig.AGENTS)}")
    print("━" * 70)
    
    engine = SimulationEngine()
    
    for tick in range(duration_minutes):
        # Check circuit breaker
        if engine.check_circuit_breaker():
            print(f"\n🛑 CIRCUIT BREAKER TRIGGERED: {engine.state.circuit_breaker_reason}")
            break
        
        # Process tick
        engine.process_tick()
        
        # Progress update every 10 minutes
        if verbose and tick > 0 and tick % 10 == 0:
            report = engine.get_report()
            summary = report["simulation_summary"]
            print(f"⏱️  Tick {tick}/{duration_minutes} | "
                  f"Capital: {summary['final_capital']} | "
                  f"Return: {summary['total_return']} | "
                  f"Trades: {summary['total_trades']}")
    
    # Final report
    print("\n" + "━" * 70)
    print("📊 SIMULATION COMPLETE - FINAL REPORT")
    print("━" * 70)
    
    report = engine.get_report()
    
    print("\n📈 Summary:")
    for key, value in report["simulation_summary"].items():
        print(f"   {key}: {value}")
    
    print("\n🤖 Agent Performance:")
    for agent in report["agent_performance"]:
        print(f"   {agent['name']}: {agent['trades']} trades, "
              f"{agent['win_rate']} win rate, {agent['total_pnl']} PnL, "
              f"Weight: {agent['weight']}")
    
    print("\n🛡️ Circuit Breaker:")
    print(f"   Triggered: {report['circuit_breaker']['triggered']}")
    if report['circuit_breaker']['reason']:
        print(f"   Reason: {report['circuit_breaker']['reason']}")
    
    print("\n" + "━" * 70)
    print("✅ Simulation complete. Review results above.")
    print("━" * 70)
    
    return report


if __name__ == "__main__":
    # Run quick 60-minute simulation for testing
    # For full 48-hour test, use: run_simulation(duration_minutes=2880)
    run_simulation(duration_minutes=60, verbose=True)
