"""
🔌 Universal Exchange Adapter Interface
========================================
Abstract base class for all exchange adapters (Bybit, MT5, Binance, etc.)
Provides a unified API for the Portfolio Manager to interact with any exchange.

Design Pattern: Adapter + Factory
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order direction."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order execution type."""
    MARKET = "market"
    LIMIT = "limit"


@dataclass
class Position:
    """Standardized position representation."""
    symbol: str
    side: OrderSide
    size: float
    entry_price: float
    current_price: float
    pnl: float
    pnl_percent: float
    leverage: int = 1
    ticket: Optional[int] = None  # For MT5 compatibility
    
    @property
    def is_long(self) -> bool:
        return self.side == OrderSide.BUY
    
    @property
    def is_short(self) -> bool:
        return self.side == OrderSide.SELL


@dataclass
class OrderResult:
    """Standardized order execution result."""
    success: bool
    order_id: Optional[str] = None
    symbol: str = ""
    side: str = ""
    size: float = 0.0
    price: float = 0.0
    message: str = ""
    raw_response: Optional[Dict] = None


class ExchangeAdapter(ABC):
    """
    Abstract Base Class for Exchange Adapters.
    
    All exchange-specific implementations (Bybit, MT5, Binance) must
    implement these methods to ensure a unified interface for the
    Portfolio Manager and Trading Engine.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the exchange name (e.g., 'bybit', 'mt5')."""
        pass
    
    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the adapter is connected to the exchange."""
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the exchange.
        Returns True if successful.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the exchange."""
        pass
    
    # =====================
    # ACCOUNT OPERATIONS
    # =====================
    
    @abstractmethod
    async def get_balance(self) -> float:
        """
        Get available account balance in base currency (USD/USDT).
        Returns the tradeable balance.
        """
        pass
    
    @abstractmethod
    async def get_equity(self) -> float:
        """
        Get total account equity (balance + unrealized PnL).
        """
        pass
    
    # =====================
    # TRADING OPERATIONS
    # =====================
    
    @abstractmethod
    async def buy(
        self,
        symbol: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1
    ) -> OrderResult:
        """
        Open a long position (buy).
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT', 'EURUSD')
            size: Position size in lots or contracts
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            leverage: Leverage multiplier (default 1)
        
        Returns:
            OrderResult with execution details
        """
        pass
    
    @abstractmethod
    async def sell(
        self,
        symbol: str,
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        leverage: int = 1
    ) -> OrderResult:
        """
        Open a short position (sell).
        
        Args:
            symbol: Trading pair
            size: Position size
            stop_loss: Stop loss price (optional)
            take_profit: Take profit price (optional)
            leverage: Leverage multiplier
        
        Returns:
            OrderResult with execution details
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        symbol: str,
        position_id: Optional[str] = None
    ) -> OrderResult:
        """
        Close an open position.
        
        Args:
            symbol: Trading pair
            position_id: Specific position ID/ticket (for MT5)
        
        Returns:
            OrderResult confirming closure
        """
        pass
    
    @abstractmethod
    async def close_all_positions(self) -> List[OrderResult]:
        """
        Emergency: Close ALL open positions.
        
        Returns:
            List of OrderResults for each closed position
        """
        pass
    
    # =====================
    # POSITION QUERIES
    # =====================
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """
        Get all open positions.
        
        Returns:
            List of Position objects
        """
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """
        Get position for a specific symbol.
        
        Returns:
            Position object or None if no position exists
        """
        pass
    
    # =====================
    # MARKET DATA
    # =====================
    
    @abstractmethod
    async def get_price(self, symbol: str) -> float:
        """
        Get current market price for a symbol.
        
        Returns:
            Current price as float
        """
        pass
    
    @abstractmethod
    async def get_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get historical OHLCV candles.
        
        Args:
            symbol: Trading pair
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', 'D1')
            limit: Number of candles to fetch
        
        Returns:
            List of candle dicts with keys: open, high, low, close, volume, time
        """
        pass


# =====================
# ADAPTER FACTORY
# =====================

class AdapterFactory:
    """
    Factory for creating exchange adapters.
    Supports dynamic adapter registration and creation.
    """
    
    _adapters: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, adapter_class: type) -> None:
        """Register an adapter class."""
        cls._adapters[name.lower()] = adapter_class
        logger.info(f"🔌 Registered adapter: {name}")
    
    @classmethod
    def create(cls, name: str, **kwargs) -> ExchangeAdapter:
        """
        Create an adapter instance.
        
        Args:
            name: Adapter name ('bybit', 'mt5', etc.)
            **kwargs: Adapter-specific configuration
        
        Returns:
            Configured ExchangeAdapter instance
        
        Raises:
            ValueError: If adapter not found
        """
        adapter_class = cls._adapters.get(name.lower())
        if not adapter_class:
            available = list(cls._adapters.keys())
            raise ValueError(f"Unknown adapter '{name}'. Available: {available}")
        
        return adapter_class(**kwargs)
    
    @classmethod
    def list_adapters(cls) -> List[str]:
        """List all registered adapter names."""
        return list(cls._adapters.keys())
