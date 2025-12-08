"""
Broker Interface
Defines the abstract base class for all broker connectors.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from core import Logger, LogLevel

class Broker(ABC):
    """
    Abstract Base Class for Broker Connectors.
    Enforces unified interface for all brokers (Capital, Oanda, etc).
    """
    
    def __init__(self, name: str, env: dict):
        self.name = name
        self.env = env
        self.log = Logger(f"broker.{name.lower()}", LogLevel.INFO)
    
    @abstractmethod
    async def get_account_summary(self) -> Dict:
        """Get account balance and status."""
        pass
    
    @abstractmethod
    async def get_open_positions(self) -> List[Dict]:
        """Get list of open positions."""
        pass
    
    @abstractmethod
    async def place_order(self, symbol: str, side: str, amount: float, price: float = None, **kwargs) -> Dict:
        """Place a market or limit order."""
        pass
    
    @abstractmethod
    async def close_position(self, symbol: str, position_id: str = None) -> Dict:
        """Close an open position."""
        pass
    
    @abstractmethod
    async def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict]:
        """Fetch historical candle data."""
        pass
    
    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        """Get current market price."""
        pass
