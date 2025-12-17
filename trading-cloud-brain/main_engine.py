#!/usr/bin/env python3
"""
💰 AXIOM ALPHA - MAIN ENGINE (The Heartbeat)
=============================================
The 24/7 autonomous trading engine. This is the "Money Machine".

Architecture:
    ┌────────────────────────────────────────────┐
    │              MAIN ENGINE LOOP              │
    │  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
    │  │ Market  │→ │ Signal  │→ │   Trade     │ │
    │  │  Data   │  │ Analysis│  │  Execution  │ │
    │  └─────────┘  └─────────┘  └─────────────┘ │
    │       ↑                           │        │
    │       └───────── Feedback ────────┘        │
    └────────────────────────────────────────────┘

Runs in background. Controlled via config file or Voice CLI.

Usage:
    python main_engine.py              # Start the engine
    python main_engine.py --mode demo  # Demo mode (no real trades)
    python main_engine.py --once       # Run one cycle and exit
"""

import os
import sys
import json
import asyncio
import logging
import signal
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('axiom_engine.log')
    ]
)
logger = logging.getLogger('axiom.engine')

# Import our engine components
try:
    from src.engine import (
        PortfolioManager,
        CipherEngine,
        NewsFilter,
        AladdinRiskEngine,
        AlphaLoop,
        TradeOutcome
    )
    from src.adapters import AdapterFactory
    ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Engine modules not fully available: {e}")
    ENGINE_AVAILABLE = False


# =====================
# CONFIGURATION (Freqtrade-Inspired)
# =====================

@dataclass
class RiskManagement:
    """Risk management settings (Freqtrade-inspired)."""
    max_open_trades: int = 3
    stake_amount: str = "5%"  # Percentage or fixed amount
    stoploss: float = -0.05  # -5% stop loss
    stoploss_on_exchange: bool = True
    trailing_stop: bool = True
    trailing_stop_positive: float = 0.01  # 1% profit to activate
    trailing_stop_positive_offset: float = 0.02  # 2% offset


@dataclass
class ExchangeConfig:
    """Exchange-specific configuration."""
    name: str = "bybit"
    pair_whitelist: List[str] = None
    pair_blacklist: List[str] = None
    
    def __post_init__(self):
        if self.pair_whitelist is None:
            self.pair_whitelist = ["BTC/USDT", "ETH/USDT", "XAU/USD"]
        if self.pair_blacklist is None:
            self.pair_blacklist = ["USDC/USDT", "USDT/DAI"]


@dataclass
class EngineConfig:
    """
    Engine configuration (Freqtrade-inspired structure).
    
    Loaded from JSON file. Supports:
    - Persistent dry_run_wallet (doesn't reset on restart)
    - Pair whitelist/blacklist
    - Trailing stop configuration
    """
    # Core settings
    trading_mode: str = "dry_run"  # dry_run, paper, live
    mode: str = "scalping"  # scalping, swing, sniper
    cycle_interval_seconds: int = 60
    
    # Freqtrade-style additions
    dry_run_wallet: float = 10000.0  # Persistent simulated balance
    
    # Legacy compatibility
    symbols: List[str] = None
    risk_level: str = "medium"
    max_trades_per_day: int = 10
    exchanges: Dict[str, bool] = None
    auto_trade: bool = False
    
    # Nested configs (will be dicts in JSON)
    risk_management: Dict = None
    exchange: Dict = None
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["BTCUSDT", "XAUUSD"]
        if self.exchanges is None:
            self.exchanges = {"bybit": True, "mt5": False}
        if self.risk_management is None:
            self.risk_management = asdict(RiskManagement())
        if self.exchange is None:
            self.exchange = asdict(ExchangeConfig())
    
    @classmethod
    def load(cls, path: str = "engine_config.json") -> 'EngineConfig':
        """Load config from JSON file."""
        config_path = Path(path)
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
            logger.info(f"📦 Loaded config from {path}")
            return cls(**data)
        logger.info("📦 Using default configuration")
        return cls()
    
    def save(self, path: str = "engine_config.json") -> None:
        """Save config to JSON file (preserves dry_run_wallet)."""
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
        logger.info(f"💾 Config saved to {path}")
    
    def update_wallet(self, pnl: float) -> None:
        """Update dry_run_wallet with trade P&L."""
        self.dry_run_wallet += pnl
        logger.info(f"💰 Wallet updated: ${self.dry_run_wallet:.2f}")
    
    def get_stake_amount(self) -> float:
        """Calculate actual stake amount from config."""
        stake = self.risk_management.get("stake_amount", "5%")
        if isinstance(stake, str) and stake.endswith("%"):
            percentage = float(stake.rstrip("%")) / 100
            return self.dry_run_wallet * percentage
        return float(stake)


# =====================
# MAIN ENGINE
# =====================

class AxiomEngine:
    """
    The 24/7 Autonomous Trading Engine.
    
    Lifecycle:
        1. Initialize adapters (Bybit, MT5)
        2. Start market data loop
        3. Run analysis (Cipher + News)
        4. Execute trades via Portfolio Manager
        5. Log outcomes for Alpha Loop learning
        6. Repeat
    """
    
    BANNER = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ███╗                   ║
    ║    ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗ ████║                   ║
    ║    ███████║ ╚███╔╝ ██║██║   ██║██╔████╔██║                   ║
    ║    ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╔╝██║                   ║
    ║    ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚═╝ ██║                   ║
    ║    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝     ╚═╝                   ║
    ║                                                              ║
    ║              💰  MONEY MACHINE v1.0  💰                      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    
    def __init__(self, config: Optional[EngineConfig] = None, demo_mode: bool = False):
        self.config = config or EngineConfig.load()
        self.demo_mode = demo_mode
        self.running = False
        self.cycle_count = 0
        self.trades_today = 0
        self.last_reset = datetime.now().date()
        
        # Initialize components
        self.portfolio_manager = PortfolioManager() if ENGINE_AVAILABLE else None
        self.cipher = CipherEngine() if ENGINE_AVAILABLE else None
        self.news_filter = NewsFilter() if ENGINE_AVAILABLE else None
        self.alpha_loop = AlphaLoop() if ENGINE_AVAILABLE else None
        
        # Trade history for learning
        self.trade_history: List[TradeOutcome] = []
        
        logger.info("⚡ Axiom Engine initialized")
    
    async def start(self) -> None:
        """Start the engine's main loop."""
        print(self.BANNER)
        logger.info(f"🚀 Starting Axiom Engine (Mode: {self.config.mode})")
        logger.info(f"📊 Symbols: {self.config.symbols}")
        logger.info(f"⚠️ Auto-Trade: {'ENABLED' if self.config.auto_trade else 'DISABLED (Manual Mode)'}")
        
        if self.demo_mode:
            logger.info("🎮 DEMO MODE - No real trades will be executed")
        
        self.running = True
        
        # Connect to exchanges
        await self._connect_exchanges()
        
        # Main loop
        while self.running:
            try:
                await self._run_cycle()
                await asyncio.sleep(self.config.cycle_interval_seconds)
            except asyncio.CancelledError:
                logger.info("Engine loop cancelled")
                break
            except Exception as e:
                logger.error(f"Cycle error: {e}")
                await asyncio.sleep(10)  # Wait before retry
        
        await self._shutdown()
    
    async def _connect_exchanges(self) -> None:
        """Connect to configured exchanges."""
        if not self.portfolio_manager:
            logger.warning("Portfolio Manager not available")
            return
        
        for exchange, enabled in self.config.exchanges.items():
            if enabled:
                try:
                    # Get credentials from environment
                    if exchange == "bybit":
                        success = await self.portfolio_manager.add_adapter(
                            "bybit",
                            api_key=os.getenv("BYBIT_API_KEY", ""),
                            api_secret=os.getenv("BYBIT_API_SECRET", ""),
                            testnet=self.demo_mode
                        )
                    elif exchange == "mt5":
                        success = await self.portfolio_manager.add_adapter(
                            "mt5",
                            bridge_url=os.getenv("MT5_BRIDGE_URL", "http://localhost:5000"),
                            auth_token=os.getenv("MT5_AUTH_TOKEN", "")
                        )
                    
                    if success:
                        logger.info(f"✅ Connected to {exchange}")
                    else:
                        logger.warning(f"⚠️ Failed to connect to {exchange}")
                        
                except Exception as e:
                    logger.error(f"Exchange connection error ({exchange}): {e}")
    
    async def _run_cycle(self) -> None:
        """Execute one analysis/trading cycle."""
        self.cycle_count += 1
        cycle_start = datetime.now()
        
        # Reset daily counter
        if datetime.now().date() != self.last_reset:
            self.trades_today = 0
            self.last_reset = datetime.now().date()
        
        logger.info(f"━━━ Cycle #{self.cycle_count} ━━━")
        
        for symbol in self.config.symbols:
            try:
                # 1. Get market data
                candles = await self._fetch_candles(symbol)
                if not candles:
                    continue
                
                # 2. Run Cipher analysis
                if self.cipher:
                    analysis = self.cipher.analyze(symbol, candles)
                    logger.info(f"📊 {symbol}: MFI={analysis.mfi:.1f}, Signal={analysis.signal.name}")
                else:
                    analysis = None
                
                # 3. Check news sentiment
                if self.news_filter:
                    sentiment = await self.news_filter.analyze_sentiment(symbol)
                    if sentiment.red_folder_warning:
                        logger.warning(f"🔴 RED FOLDER WARNING for {symbol}: {sentiment.summary}")
                        continue  # Skip trading during high-impact events
                else:
                    sentiment = None
                
                # 4. Generate trade decision
                decision = self._make_decision(symbol, analysis, sentiment)
                
                if decision and decision.get("action") != "hold":
                    await self._execute_decision(symbol, decision)
                    
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
        
        # 5. Check for weekly evolution
        if self.alpha_loop and self.alpha_loop.should_evolve():
            logger.info("🧬 Running weekly Alpha Loop evolution...")
            await self.alpha_loop.run_evolution(self.trade_history)
            self.trade_history = []  # Reset after evolution
        
        cycle_time = (datetime.now() - cycle_start).total_seconds()
        logger.info(f"━━━ Cycle complete ({cycle_time:.1f}s) ━━━")
    
    async def _fetch_candles(self, symbol: str) -> Optional[List[Dict]]:
        """Fetch recent candles for analysis."""
        if not self.portfolio_manager or not self.portfolio_manager._adapters:
            # Return mock data for demo
            return self._generate_mock_candles()
        
        # Try to get candles from first available adapter
        for adapter in self.portfolio_manager._adapters.values():
            try:
                candles = await adapter.get_candles(symbol, timeframe="1h", limit=100)
                return candles
            except Exception:
                continue
        
        return self._generate_mock_candles()
    
    def _generate_mock_candles(self) -> List[Dict]:
        """Generate mock candles for demo mode."""
        import random
        base_price = 50000
        candles = []
        for i in range(100):
            price = base_price + random.uniform(-500, 500)
            candles.append({
                "close": price,
                "high": price + random.uniform(0, 100),
                "low": price - random.uniform(0, 100),
                "volume": random.uniform(1000, 5000)
            })
            base_price = price
        return candles
    
    def _make_decision(self, symbol: str, analysis, sentiment) -> Optional[Dict]:
        """Combine signals to make a trading decision."""
        if not analysis:
            return {"action": "hold", "reason": "No analysis available"}
        
        # Get strategy weight from Alpha Loop
        cipher_weight = 1.0
        if self.alpha_loop:
            cipher_weight = self.alpha_loop.get_strategy_weight("cipher")
        
        # Simple decision logic (can be enhanced)
        if analysis.signal.name in ["STRONG_BUY", "BUY"] and analysis.strength > 0.6:
            return {
                "action": "buy",
                "size": self._calculate_size(analysis.strength * cipher_weight),
                "reason": analysis.reason,
                "confidence": analysis.strength
            }
        elif analysis.signal.name in ["STRONG_SELL", "SELL"] and analysis.strength > 0.6:
            return {
                "action": "sell",
                "size": self._calculate_size(analysis.strength * cipher_weight),
                "reason": analysis.reason,
                "confidence": analysis.strength
            }
        
        return {"action": "hold", "reason": "No clear signal"}
    
    def _calculate_size(self, strength: float) -> float:
        """Calculate position size based on risk level."""
        base_sizes = {"low": 0.01, "medium": 0.05, "high": 0.1}
        base = base_sizes.get(self.config.risk_level, 0.05)
        return round(base * strength, 4)
    
    async def _execute_decision(self, symbol: str, decision: Dict) -> None:
        """Execute a trading decision."""
        if self.trades_today >= self.config.max_trades_per_day:
            logger.warning(f"⚠️ Max trades per day reached ({self.config.max_trades_per_day})")
            return
        
        action = decision["action"]
        size = decision["size"]
        
        logger.info(f"💡 Decision: {action.upper()} {size} {symbol} ({decision['reason']})")
        
        if not self.config.auto_trade:
            logger.info("📝 Auto-trade disabled. Logged for manual review.")
            return
        
        if self.demo_mode:
            logger.info(f"🎮 [DEMO] Would execute: {action} {size} {symbol}")
            self.trades_today += 1
            return
        
        # Real execution
        if self.portfolio_manager:
            try:
                result = await self.portfolio_manager.execute_trade(
                    exchange="bybit",  # Default exchange
                    symbol=symbol,
                    side=action,
                    size=size
                )
                
                if result.success:
                    logger.info(f"✅ Trade executed: {result.order_id}")
                    self.trades_today += 1
                else:
                    logger.error(f"❌ Trade failed: {result.message}")
                    
            except Exception as e:
                logger.error(f"Execution error: {e}")
    
    async def _shutdown(self) -> None:
        """Clean shutdown of the engine."""
        logger.info("🛑 Shutting down Axiom Engine...")
        
        if self.portfolio_manager:
            await self.portfolio_manager.stop()
        
        if self.news_filter:
            await self.news_filter.close()
        
        # Save final state
        if self.alpha_loop and self.trade_history:
            await self.alpha_loop.run_evolution(self.trade_history)
        
        self.config.save()
        logger.info("👋 Engine shutdown complete")
    
    def stop(self) -> None:
        """Signal the engine to stop."""
        self.running = False


# =====================
# SIGNAL HANDLERS
# =====================

engine_instance: Optional[AxiomEngine] = None

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {sig}")
    if engine_instance:
        engine_instance.stop()


# =====================
# ENTRY POINT
# =====================

async def main():
    """Main entry point."""
    global engine_instance
    
    import argparse
    parser = argparse.ArgumentParser(description="Axiom Alpha Trading Engine")
    parser.add_argument("--mode", choices=["scalping", "swing", "sniper"], default="scalping")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode (no real trades)")
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--config", default="engine_config.json", help="Config file path")
    args = parser.parse_args()
    
    # Load or create config
    config = EngineConfig.load(args.config)
    config.mode = args.mode
    
    # Create engine
    engine_instance = AxiomEngine(config=config, demo_mode=args.demo)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    if args.once:
        # Run single cycle
        await engine_instance._connect_exchanges()
        await engine_instance._run_cycle()
    else:
        # Start continuous operation
        await engine_instance.start()


if __name__ == "__main__":
    asyncio.run(main())
