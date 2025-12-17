"""
💼 Portfolio Manager - The Orchestrator
========================================
Central controller that manages all exchange adapters, routes trades
through Aladdin Risk Engine, and maintains portfolio state.

Responsibilities:
    - Manages multiple exchange adapters (Bybit, MT5)
    - Routes trades through Aladdin for risk approval
    - Tracks all positions across exchanges
    - Provides unified portfolio view
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from src.adapters import ExchangeAdapter, AdapterFactory, Position, OrderResult
from src.engine.aladdin import AladdinRiskEngine, RiskAssessment

logger = logging.getLogger(__name__)


@dataclass
class PortfolioState:
    """Current state of the entire portfolio."""
    total_balance: float
    total_equity: float
    unrealized_pnl: float
    positions_count: int
    positions: List[Position]
    exchanges: Dict[str, bool]  # Exchange name -> connected status
    timestamp: datetime


class PortfolioManager:
    """
    Central Portfolio Manager - The Brain's right hand.
    
    Orchestrates trading across multiple exchanges while enforcing
    risk management rules via Aladdin Risk Engine.
    
    Usage:
        pm = PortfolioManager()
        await pm.add_adapter('bybit', api_key='...', api_secret='...')
        await pm.add_adapter('mt5', bridge_url='...', auth_token='...')
        
        # Trade with automatic risk management
        result = await pm.execute_trade(
            exchange='bybit',
            symbol='BTCUSDT',
            side='buy',
            size=0.1
        )
    """
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,
        max_portfolio_risk: float = 0.10,
        correlation_threshold: float = 0.80
    ):
        """
        Initialize Portfolio Manager.
        
        Args:
            max_risk_per_trade: Max risk per trade (default 2%)
            max_portfolio_risk: Max total portfolio risk (default 10%)
            correlation_threshold: Correlation threshold for risk reduction
        """
        self._adapters: Dict[str, ExchangeAdapter] = {}
        self._aladdin = AladdinRiskEngine(
            max_risk_per_trade=max_risk_per_trade,
            max_portfolio_risk=max_portfolio_risk,
            correlation_threshold=correlation_threshold
        )
        self._running = False
        
        logger.info("💼 Portfolio Manager initialized")
    
    # =====================
    # ADAPTER MANAGEMENT
    # =====================
    
    async def add_adapter(
        self,
        name: str,
        **config
    ) -> bool:
        """
        Add and connect an exchange adapter.
        
        Args:
            name: Adapter name ('bybit', 'mt5')
            **config: Adapter-specific configuration
        
        Returns:
            True if connection successful
        """
        try:
            adapter = AdapterFactory.create(name, **config)
            connected = await adapter.connect()
            
            if connected:
                self._adapters[name] = adapter
                logger.info(f"✅ Added adapter: {name}")
                return True
            else:
                logger.error(f"❌ Failed to connect adapter: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding adapter {name}: {e}")
            return False
    
    async def remove_adapter(self, name: str) -> None:
        """Remove and disconnect an adapter."""
        if name in self._adapters:
            await self._adapters[name].disconnect()
            del self._adapters[name]
            logger.info(f"🔌 Removed adapter: {name}")
    
    def get_adapter(self, name: str) -> Optional[ExchangeAdapter]:
        """Get a specific adapter."""
        return self._adapters.get(name)
    
    def list_adapters(self) -> List[str]:
        """List all connected adapters."""
        return list(self._adapters.keys())
    
    # =====================
    # TRADING OPERATIONS
    # =====================
    
    async def execute_trade(
        self,
        exchange: str,
        symbol: str,
        side: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1,
        bypass_aladdin: bool = False
    ) -> OrderResult:
        """
        Execute a trade with Aladdin risk management.
        
        Args:
            exchange: Exchange to trade on ('bybit', 'mt5')
            symbol: Trading symbol
            side: 'buy' or 'sell'
            size: Position size
            stop_loss: Stop loss price
            take_profit: Take profit price
            leverage: Leverage (for crypto)
            bypass_aladdin: Skip risk checks (DANGEROUS)
        
        Returns:
            OrderResult with execution details
        """
        adapter = self._adapters.get(exchange)
        if not adapter:
            return OrderResult(
                success=False,
                symbol=symbol,
                side=side,
                message=f"Exchange '{exchange}' not connected"
            )
        
        # Get current state for risk evaluation
        balance = await adapter.get_balance()
        current_positions = await self._get_all_positions_dict()
        
        # Evaluate with Aladdin (unless bypassed)
        if not bypass_aladdin:
            assessment = self._aladdin.evaluate_trade(
                symbol=symbol,
                proposed_size=size,
                side=side,
                account_balance=balance,
                current_positions=current_positions
            )
            
            if not assessment.approved:
                logger.warning(f"⛔ Trade rejected by Aladdin: {assessment.reason}")
                return OrderResult(
                    success=False,
                    symbol=symbol,
                    side=side,
                    size=size,
                    message=f"ALADDIN BLOCKED: {assessment.reason}"
                )
            
            # Use adjusted size
            size = assessment.adjusted_size
            
            if assessment.adjusted_size != assessment.original_size:
                logger.info(
                    f"🛡️ Aladdin adjusted size: {assessment.original_size} -> {assessment.adjusted_size}"
                )
        
        # Execute trade on adapter
        if side.lower() == 'buy':
            result = await adapter.buy(
                symbol=symbol,
                size=size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=leverage
            )
        else:
            result = await adapter.sell(
                symbol=symbol,
                size=size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                leverage=leverage
            )
        
        if result.success:
            logger.info(f"✅ Trade executed: {exchange}/{symbol} {side} {size}")
        
        return result
    
    async def close_position(
        self,
        exchange: str,
        symbol: str,
        position_id: Optional[str] = None
    ) -> OrderResult:
        """Close a specific position."""
        adapter = self._adapters.get(exchange)
        if not adapter:
            return OrderResult(
                success=False,
                symbol=symbol,
                message=f"Exchange '{exchange}' not connected"
            )
        
        return await adapter.close_position(symbol, position_id)
    
    async def emergency_close_all(self) -> Dict[str, List[OrderResult]]:
        """
        EMERGENCY: Close all positions on all exchanges.
        
        Returns:
            Dict of {exchange: [OrderResults]}
        """
        logger.critical("🚨 EMERGENCY CLOSE ALL TRIGGERED")
        
        results = {}
        for name, adapter in self._adapters.items():
            results[name] = await adapter.close_all_positions()
        
        return results
    
    # =====================
    # PORTFOLIO QUERIES
    # =====================
    
    async def get_portfolio_state(self) -> PortfolioState:
        """Get complete portfolio state across all exchanges."""
        total_balance = 0.0
        total_equity = 0.0
        all_positions = []
        exchanges = {}
        
        for name, adapter in self._adapters.items():
            try:
                balance = await adapter.get_balance()
                equity = await adapter.get_equity()
                positions = await adapter.get_positions()
                
                total_balance += balance
                total_equity += equity
                all_positions.extend(positions)
                exchanges[name] = adapter.is_connected
                
            except Exception as e:
                logger.error(f"Error getting state from {name}: {e}")
                exchanges[name] = False
        
        unrealized_pnl = sum(p.pnl for p in all_positions)
        
        return PortfolioState(
            total_balance=total_balance,
            total_equity=total_equity,
            unrealized_pnl=unrealized_pnl,
            positions_count=len(all_positions),
            positions=all_positions,
            exchanges=exchanges,
            timestamp=datetime.now()
        )
    
    async def get_all_positions(self) -> List[Position]:
        """Get all positions across all exchanges."""
        positions = []
        for adapter in self._adapters.values():
            positions.extend(await adapter.get_positions())
        return positions
    
    async def _get_all_positions_dict(self) -> Dict[str, dict]:
        """Get positions as dict for Aladdin evaluation."""
        positions = await self.get_all_positions()
        return {
            p.symbol: {
                'side': p.side.value,
                'size': p.size,
                'pnl': p.pnl
            }
            for p in positions
        }
    
    # =====================
    # PRICE DATA
    # =====================
    
    async def update_prices(self) -> None:
        """Update price cache for all tracked symbols."""
        positions = await self.get_all_positions()
        symbols = set(p.symbol for p in positions)
        
        for name, adapter in self._adapters.items():
            for symbol in symbols:
                try:
                    price = await adapter.get_price(symbol)
                    self._aladdin.update_price(symbol, price)
                except Exception:
                    pass  # Skip if symbol not on this exchange
    
    # =====================
    # LIFECYCLE
    # =====================
    
    async def start(self) -> None:
        """Start the Portfolio Manager background tasks."""
        self._running = True
        logger.info("🚀 Portfolio Manager started")
        
        # Start price update loop
        asyncio.create_task(self._price_update_loop())
    
    async def stop(self) -> None:
        """Stop the Portfolio Manager and disconnect all adapters."""
        self._running = False
        
        for name in list(self._adapters.keys()):
            await self.remove_adapter(name)
        
        logger.info("🛑 Portfolio Manager stopped")
    
    async def _price_update_loop(self) -> None:
        """Background loop to update prices for correlation calculation."""
        while self._running:
            try:
                await self.update_prices()
            except Exception as e:
                logger.error(f"Price update error: {e}")
            
            await asyncio.sleep(60)  # Update every minute
