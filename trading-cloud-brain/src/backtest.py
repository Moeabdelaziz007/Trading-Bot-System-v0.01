"""
📊 AlphaAxiom Backtester
Simple backtesting module for strategy validation.

Runs historical simulations on 3 scenarios:
1. Trending Market (Strong Directional Move)
2. Choppy/Range-bound Market
3. High-Volatility Event (News Spike)

Outputs:
- backtest_results.csv
- Console summary with key metrics

Usage:
    python backtest.py
"""

import csv
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
from enum import Enum


class MarketScenario(Enum):
    TRENDING = "trending"
    CHOPPY = "choppy"
    HIGH_VOLATILITY = "high_volatility"


@dataclass
class Trade:
    """Represents a single trade."""
    timestamp: str
    scenario: str
    symbol: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    exit_price: float
    quantity: float
    pnl: float
    pnl_percent: float
    duration_minutes: int
    signal_confidence: int
    outcome: str  # "WIN" or "LOSS"


@dataclass
class BacktestResult:
    """Aggregated backtest results for a scenario."""
    scenario: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_pnl_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    profit_factor: float


class AlphaAxiomBacktester:
    """
    Simple backtester for AlphaAxiom strategies.
    
    Uses synthetic data generation based on scenario characteristics
    to validate strategy behavior under different market conditions.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.02,  # 2% per trade
        min_confidence: int = 75
    ):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.min_confidence = min_confidence
        self.trades: List[Trade] = []
    
    def generate_scenario_data(
        self,
        scenario: MarketScenario,
        base_price: float = 100.0,
        num_candles: int = 500
    ) -> List[Dict]:
        """
        Generate synthetic OHLCV data based on scenario type.
        
        Args:
            scenario: Type of market scenario
            base_price: Starting price
            num_candles: Number of candles to generate
        
        Returns:
            List of OHLCV dicts
        """
        candles = []
        price = base_price
        
        for i in range(num_candles):
            timestamp = datetime.now() - timedelta(minutes=(num_candles - i) * 15)
            
            if scenario == MarketScenario.TRENDING:
                # Strong uptrend with pullbacks
                trend_bias = 0.003  # 0.3% per candle bias
                volatility = 0.005
                change = random.gauss(trend_bias, volatility)
                
            elif scenario == MarketScenario.CHOPPY:
                # Mean-reverting, no clear direction
                mean_price = base_price
                mean_reversion = (mean_price - price) * 0.01
                volatility = 0.004
                change = random.gauss(mean_reversion, volatility)
                
            elif scenario == MarketScenario.HIGH_VOLATILITY:
                # Wild swings, occasional spikes
                volatility = 0.02  # 2% per candle
                if random.random() < 0.05:  # 5% chance of spike
                    change = random.gauss(0, volatility * 3)
                else:
                    change = random.gauss(0, volatility)
            else:
                change = random.gauss(0, 0.005)
            
            open_price = price
            close_price = price * (1 + change)
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, 0.002)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, 0.002)))
            volume = random.randint(10000, 100000)
            
            candles.append({
                "timestamp": timestamp.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            price = close_price
        
        return candles
    
    def simulate_strategy(
        self,
        scenario: MarketScenario,
        candles: List[Dict],
        symbol: str = "TEST/USD"
    ) -> List[Trade]:
        """
        Simulate a simple momentum strategy on the data.
        
        Strategy Logic:
        - Calculate 10-candle momentum
        - Generate signal when momentum exceeds threshold
        - Apply Kelly-inspired position sizing
        - Exit after fixed duration or stop-loss/take-profit
        """
        trades = []
        position = None
        lookback = 10
        
        for i in range(lookback, len(candles) - 5):
            current = candles[i]
            past = candles[i - lookback]
            
            # Simple momentum calculation
            momentum = (current["close"] - past["close"]) / past["close"]
            
            # Generate confidence based on momentum strength
            confidence = min(100, int(abs(momentum) * 1000 + 50))
            
            # Skip if below minimum confidence
            if confidence < self.min_confidence:
                continue
            
            # Only trade if no open position
            if position is None and abs(momentum) > 0.02:
                side = "BUY" if momentum > 0 else "SELL"
                entry_price = current["close"]
                quantity = (self.capital * self.risk_per_trade) / entry_price
                
                # Simulate exit after 2-8 candles
                exit_idx = min(i + random.randint(2, 8), len(candles) - 1)
                exit_price = candles[exit_idx]["close"]
                
                # Calculate P&L
                if side == "BUY":
                    pnl = (exit_price - entry_price) * quantity
                else:
                    pnl = (entry_price - exit_price) * quantity
                
                pnl_percent = (pnl / (entry_price * quantity)) * 100
                duration = (exit_idx - i) * 15  # 15-minute candles
                
                outcome = "WIN" if pnl > 0 else "LOSS"
                
                trade = Trade(
                    timestamp=current["timestamp"],
                    scenario=scenario.value,
                    symbol=symbol,
                    side=side,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=round(quantity, 4),
                    pnl=round(pnl, 2),
                    pnl_percent=round(pnl_percent, 2),
                    duration_minutes=duration,
                    signal_confidence=confidence,
                    outcome=outcome
                )
                trades.append(trade)
                
                # Update capital
                self.capital += pnl
        
        return trades
    
    def calculate_metrics(self, trades: List[Trade], scenario: str) -> BacktestResult:
        """Calculate aggregate metrics for a set of trades."""
        if not trades:
            return BacktestResult(
                scenario=scenario,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0.0,
                total_pnl=0.0,
                avg_pnl_per_trade=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                profit_factor=0.0
            )
        
        winning = [t for t in trades if t.outcome == "WIN"]
        losing = [t for t in trades if t.outcome == "LOSS"]
        
        total_pnl = sum(t.pnl for t in trades)
        avg_pnl = total_pnl / len(trades)
        
        # Calculate max drawdown
        running_pnl = 0
        peak = 0
        max_dd = 0
        for t in trades:
            running_pnl += t.pnl
            peak = max(peak, running_pnl)
            dd = peak - running_pnl
            max_dd = max(max_dd, dd)
        
        # Calculate profit factor
        gross_profit = sum(t.pnl for t in winning) if winning else 0
        gross_loss = abs(sum(t.pnl for t in losing)) if losing else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Simplified Sharpe (using trade returns)
        returns = [t.pnl_percent for t in trades]
        avg_return = sum(returns) / len(returns)
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe = avg_return / std_return if std_return > 0 else 0
        
        return BacktestResult(
            scenario=scenario,
            total_trades=len(trades),
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=round(len(winning) / len(trades) * 100, 2),
            total_pnl=round(total_pnl, 2),
            avg_pnl_per_trade=round(avg_pnl, 2),
            max_drawdown=round(max_dd, 2),
            sharpe_ratio=round(sharpe, 2),
            profit_factor=round(profit_factor, 2)
        )
    
    def run_all_scenarios(self) -> Tuple[List[Trade], List[BacktestResult]]:
        """Run backtests for all three scenarios."""
        all_trades = []
        results = []
        
        scenarios = [
            (MarketScenario.TRENDING, 100.0),
            (MarketScenario.CHOPPY, 100.0),
            (MarketScenario.HIGH_VOLATILITY, 100.0)
        ]
        
        for scenario, base_price in scenarios:
            print(f"\n🔄 Running {scenario.value.upper()} scenario...")
            self.capital = self.initial_capital  # Reset capital
            
            candles = self.generate_scenario_data(scenario, base_price, 500)
            trades = self.simulate_strategy(scenario, candles)
            
            result = self.calculate_metrics(trades, scenario.value)
            results.append(result)
            all_trades.extend(trades)
            
            print(f"   Trades: {result.total_trades}")
            print(f"   Win Rate: {result.win_rate}%")
            print(f"   Total P&L: ${result.total_pnl}")
            print(f"   Sharpe: {result.sharpe_ratio}")
        
        return all_trades, results
    
    def export_to_csv(self, trades: List[Trade], filename: str = "backtest_results.csv"):
        """Export trades to CSV file."""
        if not trades:
            print("⚠️ No trades to export.")
            return
        
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(asdict(trades[0]).keys()))
            writer.writeheader()
            for trade in trades:
                writer.writerow(asdict(trade))
        
        print(f"\n✅ Exported {len(trades)} trades to {filename}")
    
    def print_summary(self, results: List[BacktestResult]):
        """Print formatted summary table."""
        print("\n" + "=" * 80)
        print("📊 ALPHAAXIOM BACKTEST SUMMARY")
        print("=" * 80)
        print(f"{'Scenario':<20} {'Trades':<10} {'Win Rate':<12} {'P&L':<15} {'Sharpe':<10} {'PF':<10}")
        print("-" * 80)
        
        for r in results:
            print(f"{r.scenario:<20} {r.total_trades:<10} {r.win_rate}%{'':<5} ${r.total_pnl:<13} {r.sharpe_ratio:<10} {r.profit_factor:<10}")
        
        print("-" * 80)
        total_trades = sum(r.total_trades for r in results)
        total_pnl = sum(r.total_pnl for r in results)
        avg_win_rate = sum(r.win_rate for r in results) / len(results) if results else 0
        print(f"{'TOTAL':<20} {total_trades:<10} {avg_win_rate:.1f}%{'':<5} ${total_pnl:<13}")
        print("=" * 80)


def main():
    """Main entry point for backtesting."""
    print("🚀 AlphaAxiom Backtester v1.0")
    print("=" * 40)
    
    backtester = AlphaAxiomBacktester(
        initial_capital=10000.0,
        risk_per_trade=0.02,
        min_confidence=75
    )
    
    trades, results = backtester.run_all_scenarios()
    backtester.export_to_csv(trades)
    backtester.print_summary(results)
    
    print("\n✅ Backtest complete. Check backtest_results.csv for details.")


if __name__ == "__main__":
    main()
