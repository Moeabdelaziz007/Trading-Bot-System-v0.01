"""
Broker Gateway
Managing Broker selection and unified access.
"""

from .base import Broker
# from .oanda import OandaProvider
# from .capital import CapitalProvider
import logging

class ConfigurationError(Exception):
    pass


class BrokerGateway:
    """
    Factory and Manager for Broker instances.
    Selects the active broker based on environment configuration.
    """
    
    def __init__(self, env):
        self.env = env
        self.log = logging.getLogger("broker.gateway")
        # self.active_broker: Broker = self._initialize_broker()
        self.active_broker = None
        
    def _initialize_broker(self) -> Broker:
        """Initialize the configured broker."""
        return None # Legacy disabled

            
    async def get_account(self):
        """Get account summary from active broker."""
        return await self.active_broker.get_account_summary()
        
    async def get_positions(self):
        """Get open positions from active broker."""
        return await self.active_broker.get_open_positions()
        
    async def execute_trade(self, signal: dict):
        """
        Execute a trade signal.
        Signal format: {symbol, side, amount, sl_pips, tp_pips, ...}
        """
        self.log.info(f"Executing trade: {signal}")
        return await self.active_broker.place_order(
            symbol=signal.get("symbol"),
            side=signal.get("side"),
            amount=signal.get("amount"),
            sl_pips=signal.get("sl_pips"),
            tp_pips=signal.get("tp_pips")
        )

    async def close_trade(self, symbol: str):
        """Close trade for symbol."""
        return await self.active_broker.close_position(symbol)
        
    async def get_market_data(self, symbol: str, timeframe: str = "M5", limit: int = 100):
        """Get candles."""
        return await self.active_broker.get_candles(symbol, timeframe, limit)
