"""
🔗 Bybit Adapter - Universal Interface Implementation
======================================================
Wraps the existing BybitConnector to conform to the ExchangeAdapter interface.
Supports Bybit V5 Unified Trading Account (Perpetuals).
"""

import asyncio
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

# Import the existing connector
from src.brokers.bybit_connector import BybitConnector

logger = logging.getLogger(__name__)


class BybitAdapter(ExchangeAdapter):
    """
    Bybit V5 Perpetuals Adapter.
    
    Wraps BybitConnector to provide a unified interface compatible
    with the Portfolio Manager and Aladdin Risk Engine.
    
    Features:
        - USDT Perpetuals trading
        - Up to 100x leverage
        - Real-time WebSocket data (via connector)
    """
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        testnet: bool = False
    ):
        """
        Initialize Bybit Adapter.
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet for paper trading
        """
        self._connector = BybitConnector(
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
        self._api_key = api_key
        self._connected = False
        self._testnet = testnet
        
        logger.info(f"🔗 BybitAdapter initialized (testnet={testnet})")
    
    @property
    def name(self) -> str:
        return "bybit"
    
    @property
    def is_connected(self) -> bool:
        return self._connected and bool(self._api_key)
    
    async def connect(self) -> bool:
        """Test connection by fetching wallet balance."""
        try:
            # Test the connection
            balance = self._connector.get_wallet_balance()
            if balance is not None:
                self._connected = True
                logger.info(f"✅ Bybit connected. Balance: ${balance:.2f}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Bybit connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close connection (Bybit is stateless REST, so just reset flag)."""
        self._connected = False
        logger.info("🔌 Bybit disconnected")
    
    # =====================
    # ACCOUNT OPERATIONS
    # =====================
    
    async def get_balance(self) -> float:
        """Get available USDT balance."""
        try:
            balance = await asyncio.to_thread(
                self._connector.get_wallet_balance
            )
            return float(balance) if balance else 0.0
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0
    
    async def get_equity(self) -> float:
        """Get total equity (balance + unrealized PnL)."""
        # Bybit's get_wallet_balance returns equity
        return await self.get_balance()
    
    # =====================
    # TRADING OPERATIONS
    # =====================
    
    async def buy(
        self,
        symbol: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1
    ) -> OrderResult:
        """Open a long position."""
        return await self._execute_order(
            symbol=symbol,
            side="Buy",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            leverage=leverage
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
            side="Sell",
            size=size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            leverage=leverage
        )
    
    async def _execute_order(
        self,
        symbol: str,
        side: str,
        size: float,
        stop_loss: Optional[float],
        take_profit: Optional[float],
        leverage: int
    ) -> OrderResult:
        """Internal method to execute orders."""
        try:
            # Set leverage first
            if leverage > 1:
                await asyncio.to_thread(
                    self._connector.set_leverage,
                    symbol,
                    leverage
                )
            
            # Place order
            result = await asyncio.to_thread(
                self._connector.place_order,
                symbol=symbol,
                side=side,
                qty=size,
                order_type="Market",
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            if result and result.get('retCode') == 0:
                order_id = result.get('result', {}).get('orderId', '')
                return OrderResult(
                    success=True,
                    order_id=str(order_id),
                    symbol=symbol,
                    side=side.lower(),
                    size=size,
                    message="Order executed successfully",
                    raw_response=result
                )
            else:
                return OrderResult(
                    success=False,
                    symbol=symbol,
                    side=side.lower(),
                    size=size,
                    message=result.get('retMsg', 'Unknown error'),
                    raw_response=result
                )
                
        except Exception as e:
            logger.error(f"Order execution failed: {e}")
            return OrderResult(
                success=False,
                symbol=symbol,
                side=side.lower(),
                size=size,
                message=str(e)
            )
    
    async def close_position(
        self,
        symbol: str,
        position_id: Optional[str] = None
    ) -> OrderResult:
        """Close a position by symbol."""
        try:
            # Get current position to determine side
            positions = await self.get_positions()
            position = next((p for p in positions if p.symbol == symbol), None)
            
            if not position:
                return OrderResult(
                    success=False,
                    symbol=symbol,
                    message="No position found"
                )
            
            # Close by placing opposite order
            close_side = "Sell" if position.is_long else "Buy"
            result = await asyncio.to_thread(
                self._connector.close_position,
                symbol,
                "Buy" if position.is_long else "Sell"
            )
            
            return OrderResult(
                success=True,
                symbol=symbol,
                side=close_side.lower(),
                message="Position closed",
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
            result = await self.close_position(position.symbol)
            results.append(result)
        
        logger.info(f"🚨 Closed {len(results)} positions")
        return results
    
    # =====================
    # POSITION QUERIES
    # =====================
    
    async def get_positions(self) -> List[Position]:
        """Get all open positions."""
        try:
            raw_positions = await asyncio.to_thread(
                self._connector.get_positions
            )
            
            positions = []
            for pos in (raw_positions or []):
                if float(pos.get('size', 0)) > 0:
                    side = OrderSide.BUY if pos.get('side') == 'Buy' else OrderSide.SELL
                    positions.append(Position(
                        symbol=pos.get('symbol', ''),
                        side=side,
                        size=float(pos.get('size', 0)),
                        entry_price=float(pos.get('avgPrice', 0)),
                        current_price=float(pos.get('markPrice', 0)),
                        pnl=float(pos.get('unrealisedPnl', 0)),
                        pnl_percent=float(pos.get('unrealisedPnlPcnt', 0)) * 100,
                        leverage=int(pos.get('leverage', 1))
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
            ticker = await asyncio.to_thread(
                self._connector.get_ticker,
                symbol
            )
            return float(ticker.get('lastPrice', 0))
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
        # Map timeframe to Bybit interval
        tf_map = {
            '1m': '1', '5m': '5', '15m': '15', '30m': '30',
            '1h': '60', '4h': '240', '1d': 'D', 'd1': 'D'
        }
        interval = tf_map.get(timeframe.lower(), '60')
        
        try:
            raw_candles = await asyncio.to_thread(
                self._connector.get_klines,
                symbol,
                interval,
                limit
            )
            
            return [
                {
                    'time': int(c.get('startTime', 0)),
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
AdapterFactory.register('bybit', BybitAdapter)
