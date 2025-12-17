"""
🧬 ALPHA LOOP - The Self-Learning Engine
=========================================
Inspired by Google's AlphaGo self-play learning.

Purpose:
    - Analyze past trade outcomes
    - Identify winning patterns
    - Adjust strategy weights dynamically
    - Evolve trading behavior over time

The Loop:
    1. COLLECT: Gather trade history (wins/losses)
    2. ANALYZE: Calculate strategy performance metrics
    3. EVOLVE: Adjust weights using gradient-free optimization
    4. PERSIST: Save new weights to config
    5. REPEAT: Run weekly

Philosophy:
    "The system that trades today should be smarter than yesterday."
"""

import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


# =====================
# DATA STRUCTURES
# =====================

@dataclass
class TradeOutcome:
    """Single trade result for learning."""
    symbol: str
    side: str  # 'buy' or 'sell'
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percent: float
    duration_minutes: int
    strategy_used: str  # 'cipher', 'news', 'manual'
    signals_at_entry: Dict[str, float]  # {'mfi': 45, 'rsi': 30, ...}
    timestamp: datetime
    
    @property
    def is_win(self) -> bool:
        return self.pnl > 0


@dataclass
class StrategyWeight:
    """Weight configuration for a strategy component."""
    name: str
    weight: float  # 0.0 to 1.0
    win_rate: float = 0.5
    avg_pnl: float = 0.0
    total_trades: int = 0
    last_updated: Optional[datetime] = None


@dataclass
class AlphaState:
    """Current state of the Alpha Loop."""
    version: int = 1
    generation: int = 0
    strategy_weights: Dict[str, StrategyWeight] = field(default_factory=dict)
    performance_history: List[Dict] = field(default_factory=list)
    last_evolution: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'version': self.version,
            'generation': self.generation,
            'strategy_weights': {k: asdict(v) for k, v in self.strategy_weights.items()},
            'performance_history': self.performance_history,
            'last_evolution': self.last_evolution.isoformat() if self.last_evolution else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AlphaState':
        state = cls()
        state.version = data.get('version', 1)
        state.generation = data.get('generation', 0)
        state.performance_history = data.get('performance_history', [])
        
        if data.get('last_evolution'):
            state.last_evolution = datetime.fromisoformat(data['last_evolution'])
        
        for name, weight_data in data.get('strategy_weights', {}).items():
            if 'last_updated' in weight_data and weight_data['last_updated']:
                weight_data['last_updated'] = datetime.fromisoformat(weight_data['last_updated'])
            state.strategy_weights[name] = StrategyWeight(**weight_data)
        
        return state


# =====================
# PERFORMANCE ANALYZER
# =====================

class PerformanceAnalyzer:
    """Analyzes trade outcomes to calculate strategy performance."""
    
    @staticmethod
    def calculate_strategy_stats(
        trades: List[TradeOutcome],
        strategy_name: str
    ) -> Dict[str, float]:
        """Calculate performance metrics for a specific strategy."""
        strategy_trades = [t for t in trades if t.strategy_used == strategy_name]
        
        if not strategy_trades:
            return {'win_rate': 0.5, 'avg_pnl': 0.0, 'sharpe': 0.0, 'total': 0}
        
        wins = sum(1 for t in strategy_trades if t.is_win)
        total_pnl = sum(t.pnl for t in strategy_trades)
        pnl_list = [t.pnl for t in strategy_trades]
        
        # Calculate Sharpe-like ratio
        import statistics
        if len(pnl_list) > 1:
            avg_pnl = statistics.mean(pnl_list)
            std_pnl = statistics.stdev(pnl_list)
            sharpe = avg_pnl / std_pnl if std_pnl > 0 else 0
        else:
            avg_pnl = pnl_list[0] if pnl_list else 0
            sharpe = 0
        
        return {
            'win_rate': wins / len(strategy_trades),
            'avg_pnl': avg_pnl,
            'total_pnl': total_pnl,
            'sharpe': sharpe,
            'total': len(strategy_trades)
        }
    
    @staticmethod
    def identify_patterns(trades: List[TradeOutcome]) -> List[Dict]:
        """Identify winning patterns from trade history."""
        patterns = []
        
        # Pattern 1: MFI Oversold Bounce
        mfi_bounce_trades = [
            t for t in trades 
            if t.signals_at_entry.get('mfi', 50) < 25
        ]
        if mfi_bounce_trades:
            win_rate = sum(1 for t in mfi_bounce_trades if t.is_win) / len(mfi_bounce_trades)
            if win_rate > 0.6:
                patterns.append({
                    'name': 'MFI Oversold Bounce',
                    'condition': 'MFI < 25',
                    'win_rate': win_rate,
                    'sample_size': len(mfi_bounce_trades)
                })
        
        # Pattern 2: Price Above VWAP
        vwap_trades = [
            t for t in trades
            if t.signals_at_entry.get('price_above_vwap', False)
        ]
        if vwap_trades:
            win_rate = sum(1 for t in vwap_trades if t.is_win) / len(vwap_trades)
            if win_rate > 0.55:
                patterns.append({
                    'name': 'VWAP Trend Follow',
                    'condition': 'Price > VWAP',
                    'win_rate': win_rate,
                    'sample_size': len(vwap_trades)
                })
        
        return patterns


# =====================
# WEIGHT OPTIMIZER
# =====================

class WeightOptimizer:
    """
    Gradient-free optimization for strategy weights.
    Uses a simple evolutionary algorithm.
    """
    
    def __init__(self, learning_rate: float = 0.1, momentum: float = 0.9):
        self.learning_rate = learning_rate
        self.momentum = momentum
        self._velocity = {}
    
    def evolve_weights(
        self,
        current_weights: Dict[str, StrategyWeight],
        performance: Dict[str, Dict]
    ) -> Dict[str, StrategyWeight]:
        """
        Evolve weights based on recent performance.
        
        Algorithm:
            - Increase weight for strategies with win_rate > 50%
            - Decrease weight for strategies with win_rate < 50%
            - Apply momentum for smooth transitions
            - Normalize to sum = 1.0
        """
        new_weights = {}
        
        for name, weight in current_weights.items():
            stats = performance.get(name, {'win_rate': 0.5, 'sharpe': 0})
            
            # Calculate gradient (simple: positive if performing well)
            gradient = (stats['win_rate'] - 0.5) + (stats.get('sharpe', 0) * 0.1)
            
            # Apply momentum
            if name not in self._velocity:
                self._velocity[name] = 0
            self._velocity[name] = self.momentum * self._velocity[name] + gradient
            
            # Update weight
            new_value = weight.weight + self.learning_rate * self._velocity[name]
            new_value = max(0.1, min(0.9, new_value))  # Clamp between 0.1 and 0.9
            
            new_weights[name] = StrategyWeight(
                name=name,
                weight=new_value,
                win_rate=stats['win_rate'],
                avg_pnl=stats.get('avg_pnl', 0),
                total_trades=stats.get('total', 0),
                last_updated=datetime.now()
            )
        
        # Normalize weights
        total = sum(w.weight for w in new_weights.values())
        if total > 0:
            for w in new_weights.values():
                w.weight /= total
        
        return new_weights


# =====================
# MAIN ALPHA LOOP
# =====================

class AlphaLoop:
    """
    The Self-Learning Engine.
    
    Usage:
        loop = AlphaLoop(state_path='alpha_state.json')
        await loop.run_evolution(trades_from_last_week)
    """
    
    DEFAULT_STRATEGIES = ['cipher', 'news', 'momentum', 'reversal']
    
    def __init__(
        self,
        state_path: str = 'alpha_state.json',
        evolution_interval_days: int = 7
    ):
        self.state_path = Path(state_path)
        self.evolution_interval = timedelta(days=evolution_interval_days)
        self.analyzer = PerformanceAnalyzer()
        self.optimizer = WeightOptimizer()
        self.state = self._load_state()
    
    def _load_state(self) -> AlphaState:
        """Load state from disk or create new."""
        if self.state_path.exists():
            try:
                with open(self.state_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"🧬 Loaded Alpha state (Generation {data.get('generation', 0)})")
                return AlphaState.from_dict(data)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        
        # Initialize default state
        state = AlphaState()
        for strategy in self.DEFAULT_STRATEGIES:
            state.strategy_weights[strategy] = StrategyWeight(
                name=strategy,
                weight=1.0 / len(self.DEFAULT_STRATEGIES)
            )
        return state
    
    def _save_state(self) -> None:
        """Persist state to disk."""
        with open(self.state_path, 'w') as f:
            json.dump(self.state.to_dict(), f, indent=2, default=str)
        logger.info(f"🧬 Saved Alpha state (Generation {self.state.generation})")
    
    async def run_evolution(self, trades: List[TradeOutcome]) -> Dict:
        """
        Execute one evolution cycle.
        
        Returns:
            Dict with evolution results
        """
        logger.info("🧬 Starting Alpha Loop evolution...")
        
        # 1. ANALYZE: Calculate performance for each strategy
        performance = {}
        for strategy in self.state.strategy_weights.keys():
            performance[strategy] = self.analyzer.calculate_strategy_stats(trades, strategy)
        
        # 2. IDENTIFY PATTERNS
        patterns = self.analyzer.identify_patterns(trades)
        
        # 3. EVOLVE: Update weights
        old_weights = {k: v.weight for k, v in self.state.strategy_weights.items()}
        self.state.strategy_weights = self.optimizer.evolve_weights(
            self.state.strategy_weights,
            performance
        )
        new_weights = {k: v.weight for k, v in self.state.strategy_weights.items()}
        
        # 4. UPDATE STATE
        self.state.generation += 1
        self.state.last_evolution = datetime.now()
        self.state.performance_history.append({
            'generation': self.state.generation,
            'timestamp': datetime.now().isoformat(),
            'performance': performance,
            'weight_changes': {
                k: {'old': old_weights.get(k, 0), 'new': new_weights.get(k, 0)}
                for k in new_weights
            }
        })
        
        # Keep only last 52 weeks of history
        self.state.performance_history = self.state.performance_history[-52:]
        
        # 5. PERSIST
        self._save_state()
        
        result = {
            'generation': self.state.generation,
            'performance': performance,
            'patterns_found': patterns,
            'weight_changes': {
                k: f"{old_weights.get(k, 0):.2f} → {new_weights.get(k, 0):.2f}"
                for k in new_weights
            }
        }
        
        logger.info(f"🧬 Evolution complete! Generation {self.state.generation}")
        return result
    
    def get_strategy_weight(self, strategy: str) -> float:
        """Get current weight for a strategy."""
        weight = self.state.strategy_weights.get(strategy)
        return weight.weight if weight else 0.25
    
    def should_evolve(self) -> bool:
        """Check if it's time for evolution."""
        if self.state.last_evolution is None:
            return True
        return datetime.now() - self.state.last_evolution >= self.evolution_interval
    
    def get_report(self) -> str:
        """Generate a human-readable report."""
        lines = [
            "═" * 50,
            "🧬 ALPHA LOOP STATUS REPORT",
            "═" * 50,
            f"Generation: {self.state.generation}",
            f"Last Evolution: {self.state.last_evolution or 'Never'}",
            "",
            "📊 Current Strategy Weights:",
        ]
        
        for name, weight in sorted(
            self.state.strategy_weights.items(),
            key=lambda x: x[1].weight,
            reverse=True
        ):
            bar = "█" * int(weight.weight * 20)
            lines.append(f"  {name:12} {bar} {weight.weight:.1%} (WR: {weight.win_rate:.1%})")
        
        lines.append("")
        lines.append("═" * 50)
        
        return "\n".join(lines)


# =====================
# BACKGROUND SCHEDULER
# =====================

class AlphaScheduler:
    """Runs the Alpha Loop on a schedule."""
    
    def __init__(self, loop: AlphaLoop, trade_fetcher: callable):
        self.loop = loop
        self.trade_fetcher = trade_fetcher  # async function to get trades
        self.running = False
    
    async def start(self):
        """Start the weekly evolution scheduler."""
        self.running = True
        logger.info("🧬 Alpha Scheduler started. Running weekly evolution checks.")
        
        while self.running:
            if self.loop.should_evolve():
                try:
                    trades = await self.trade_fetcher()
                    results = await self.loop.run_evolution(trades)
                    logger.info(f"🧬 Weekly evolution complete: {results}")
                except Exception as e:
                    logger.error(f"Evolution failed: {e}")
            
            # Check every hour
            await asyncio.sleep(3600)
    
    def stop(self):
        self.running = False


# =====================
# DEMO / TEST
# =====================

async def demo():
    """Demo the Alpha Loop with mock data."""
    print("🧬 Alpha Loop Demo\n")
    
    # Create mock trades
    mock_trades = [
        TradeOutcome(
            symbol='BTCUSDT', side='buy', entry_price=50000, exit_price=51000,
            pnl=100, pnl_percent=2.0, duration_minutes=60, strategy_used='cipher',
            signals_at_entry={'mfi': 20, 'rsi': 25, 'price_above_vwap': False},
            timestamp=datetime.now()
        ),
        TradeOutcome(
            symbol='XAUUSD', side='buy', entry_price=2000, exit_price=2010,
            pnl=50, pnl_percent=0.5, duration_minutes=120, strategy_used='news',
            signals_at_entry={'mfi': 55, 'rsi': 60, 'price_above_vwap': True},
            timestamp=datetime.now()
        ),
        TradeOutcome(
            symbol='BTCUSDT', side='sell', entry_price=52000, exit_price=50000,
            pnl=-200, pnl_percent=-4.0, duration_minutes=30, strategy_used='momentum',
            signals_at_entry={'mfi': 80, 'rsi': 75, 'price_above_vwap': True},
            timestamp=datetime.now()
        ),
    ]
    
    # Initialize and run
    loop = AlphaLoop(state_path='/tmp/alpha_demo_state.json')
    
    print("Before Evolution:")
    print(loop.get_report())
    
    results = await loop.run_evolution(mock_trades)
    
    print("\nAfter Evolution:")
    print(loop.get_report())
    
    print("\n📊 Evolution Results:")
    print(json.dumps(results, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(demo())
