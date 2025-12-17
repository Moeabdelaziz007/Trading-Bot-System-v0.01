"""
📉 MT5 Adapter - Universal Interface Implementation
====================================================
Wraps the existing MT5Broker to conform to the ExchangeAdapter interface.
Supports Forex, Metals, and Indices via MT5 Bridge.
"""

import logging
from typing import Dict, List, Optional, Any

from .base import (
    ExchangeAdapter,
    AdapterFactory,
    Position,
    OrderResult,
    OrderSide,
    OrderType
)

# Import the existing broker
from src.brokers.mt5_broker import MT5Broker

logger = logging.getLogger(__name__)


class MT5Adapter(ExchangeAdapter):
    """
    MetaTrader 5 Adapter.
    
    Wraps MT5Broker to provide a unified interface compatible
    with the Portfolio Manager and Aladdin Risk Engine.
    
    Features:
        - Forex pairs (EURUSD, GBPUSD, etc.)
        - Metals (XAUUSD Gold, XAGUSD Silver)
        - Indices (US30, NAS100, etc.)
    
    Note:
        Requires MT5 Bridge running on Windows VPS.
    """
    
    def __init__(
        self,
        bridge_url: str,
        auth_token: str,
        broker_name: str = "XM Global"
    ):
        """
        Initialize MT5 Adapter.
        
        Args:
            bridge_url: URL of MT5 Bridge API (e.g., http://localhost:8080)
            auth_token: Authentication token for bridge
            broker_name: Broker name for logging
        """
        self._broker = MT5Broker(
            bridge_url=bridge_url,
            auth_token=auth_token,
            broker_name=broker_name
        )
        self._broker_name = broker_name
        self._connected = False
        
        logger.info(f"📉 MT5Adapter initialized ({broker_name})")
    
    @property
    def name(self) -> str:
        return "mt5"
    
    @property
    def is_connected(self) -> bool:
        return self._connected
    
    async def connect(self) -> bool:
        """Test connection via health check."""
        try:
            result = await self._broker.health_check()
            if result.get('status') == 'online':
                self._connected = True
                logger.info(f"✅ MT5 connected ({self._broker_name})")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ MT5 connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close connection."""
        self._connected = False
        logger.info("🔌 MT5 disconnected")
    
    # =====================
    # IRONCLAD RECONNECTION (Phase 5 Enhancement)
    # =====================
    
    async def _ensure_connection(self, max_retries: int = 3) -> bool:
        """
        Ensure MT5 connection is alive. Auto-reconnect if needed.
        
        Inspired by Kevin Dave's MT5 Python robustness patterns.
        """
        if self._connected:
            return True
        
        for attempt in range(1, max_retries + 1):
            logger.warning(f"🔄 MT5 Reconnection attempt {attempt}/{max_retries}...")
            try:
                if await self.connect():
                    logger.info("✅ MT5 Reconnected successfully!")
                    return True
            except Exception as e:
                logger.error(f"Reconnection attempt {attempt} failed: {e}")
            
            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)
        
        logger.error("❌ MT5 Reconnection failed after all retries!")
        return False
    
    async def _with_reconnect(self, operation_name: str, coro):
        """
        Wrapper that auto-reconnects before executing an operation.
        
        Usage:
            result = await self._with_reconnect("get_balance", self._broker.get_account_info())
        """
        if not await self._ensure_connection():
            raise ConnectionError(f"Cannot execute {operation_name}: MT5 disconnected")
        return await coro
    
    # =====================
    # ACCOUNT OPERATIONS
    # =====================
    
    async def get_balance(self) -> float:
        """Get available balance."""
        try:
            info = await self._broker.get_account_info()
            return float(info.get('balance', 0))
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0
    
    async def get_equity(self) -> float:
        """Get total equity."""
        try:
            info = await self._broker.get_account_info()
            return float(info.get('equity', 0))
        except Exception as e:
            logger.error(f"Failed to get equity: {e}")
            return 0.0
    
    # =====================
    # TRADING OPERATIONS
    # =====================
    
    async def buy(
        self,
        symbol: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1  # MT5 leverage is set at account level
    ) -> OrderResult:
        """Open a long position."""
        return await self._execute_order(
            symbol=symbol,
            action="buy",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    async def sell(
        self,
        symbol: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1
    ) -> OrderResult:
        """Open a short position."""
        return await self._execute_order(
            symbol=symbol,
            action="sell",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
    
    async def _execute_order(
        self,
        symbol: str,
        action: str,
        size: float,
        stop_loss: Optional[float],
        take_profit: Optional[float]
    ) -> OrderResult:
        """Internal method to execute orders via MT5 Bridge."""
        try:
            result = await self._broker.execute_trade(
                symbol=symbol,
                action=action,
                volume=size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment="AxiomAlpha"
            )
            
            if result.get('success'):
                return OrderResult(
                    success=True,
                    order_id=str(result.get('ticket', '')),
                    symbol=symbol,
                    side=action,
                    size=size,
                    price=float(result.get('price', 0)),
                    message="Order executed successfully",
                    raw_response=result
                )
            else:
                return OrderResult(
                    success=False,
                    symbol=symbol,
                    side=action,
                    size=size,
                    message=result.get('comment', 'Unknown error'),
                    raw_response=result
                )
                
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return OrderResult(
                success=False,
                symbol=symbol,
                side=action,
                size=size,
                message=str(e)
            )
    
    async def close_position(
        self,
        symbol: str,
        position_id: Optional[str] = None
    ) -> OrderResult:
        """Close a position by ticket ID."""
        try:
            if position_id:
                result = await self._broker.close_position(int(position_id))
            else:
                # Find position by symbol and close it
                positions = await self._broker.get_positions(symbol)
                if not positions:
                    return OrderResult(
                        success=False,
                        symbol=symbol,
                        message="No position found"
                    )
                result = await self._broker.close_position(positions[0].get('ticket'))
            
            return OrderResult(
                success=result.get('success', False),
                symbol=symbol,
                message=result.get('comment', 'Position closed'),
                raw_response=result
            )
            
        except Exception as e:
            logger.error(f"Close position failed: {e}")
            return OrderResult(
                success=False,
                symbol=symbol,
                message=str(e)
            )
    
    async def close_all_positions(self) -> List[OrderResult]:
        """Emergency close all positions."""
        results = []
        positions = await self.get_positions()
        
        for position in positions:
            result = await self.close_position(
                position.symbol,
                str(position.ticket) if position.ticket else None
            )
            results.append(result)
        
        logger.info(f"🚨 Closed {len(results)} MT5 positions")
        return results
    
    # =====================
    # POSITION QUERIES
    # =====================
    
    async def get_positions(self) -> List[Position]:
        """Get all open positions."""
        try:
            raw_positions = await self._broker.get_positions()
            
            positions = []
            for pos in (raw_positions or []):
                side = OrderSide.BUY if pos.get('type') == 'buy' else OrderSide.SELL
                positions.append(Position(
                    symbol=pos.get('symbol', ''),
                    side=side,
                    size=float(pos.get('volume', 0)),
                    entry_price=float(pos.get('open_price', 0)),
                    current_price=float(pos.get('current_price', 0)),
                    pnl=float(pos.get('profit', 0)),
                    pnl_percent=0.0,  # Calculate if needed
                    leverage=1,  # MT5 leverage is account-level
                    ticket=int(pos.get('ticket', 0))
                ))
            
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for a specific symbol."""
        positions = await self.get_positions()
        return next((p for p in positions if p.symbol == symbol), None)
    
    # =====================
    # MARKET DATA
    # =====================
    
    async def get_price(self, symbol: str) -> float:
        """Get current price."""
        try:
            data = await self._broker.get_live_price(symbol)
            # Return mid price
            bid = float(data.get('bid', 0))
            ask = float(data.get('ask', 0))
            return (bid + ask) / 2 if bid and ask else 0.0
        except Exception as e:
            logger.error(f"Failed to get price: {e}")
            return 0.0
    
    async def get_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical candles."""
        # Map timeframe to MT5 format
        tf_map = {
            '1m': 'M1', '5m': 'M5', '15m': 'M15', '30m': 'M30',
            '1h': 'H1', '4h': 'H4', '1d': 'D1', 'd1': 'D1'
        }
        mt5_tf = tf_map.get(timeframe.lower(), 'H1')
        
        try:
            raw_candles = await self._broker.get_historical_data(
                symbol=symbol,
                timeframe=mt5_tf,
                bars_count=limit
            )
            
            return [
                {
                    'time': c.get('time', 0),
                    'open': float(c.get('open', 0)),
                    'high': float(c.get('high', 0)),
                    'low': float(c.get('low', 0)),
                    'close': float(c.get('close', 0)),
                    'volume': float(c.get('volume', 0))
                }
                for c in (raw_candles or [])
            ]
            
        except Exception as e:
            logger.error(f"Failed to get candles: {e}")
            return []


# Register adapter with factory
AdapterFactory.register('mt5', MT5Adapter)
