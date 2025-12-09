"""Brokers Package
Exports Broker interface, Providers, Gateway, and Paper Trading connectors.

Core Providers:
    - OandaProvider: Forex trading
    - CapitalProvider: CFDs & Forex
    - PepperstoneProvider: Multi-asset
    - ICMarketsProvider: ECN trading

Paper Trading (NEW in v2.0):
    - AlpacaPaperConnector: US Stocks/ETFs paper trading
    - BybitTestnetConnector: Crypto/Meme coins testnet
    - PaperTradingGateway: Unified routing with safety layers
"""

from .base import Broker
from .oanda import OandaProvider
from .capital import CapitalProvider
from .pepperstone import PepperstoneProvider
from .icmarkets import ICMarketsProvider
from .gateway import BrokerGateway

# Paper Trading Connectors (NEW in v2.0)
try:
    from .alpaca_paper import AlpacaPaperConnector
    from .bybit_testnet import BybitTestnetConnector
    from .paper_trading_gateway import (
        PaperTradingGateway,
        LeverageManager,
        CircuitBreakerV2,
        BrokerType,
        VolatilityLevel
    )
    _PAPER_TRADING_AVAILABLE = True
except ImportError:
    _PAPER_TRADING_AVAILABLE = False

__all__ = [
    # Core
    'Broker',
    'OandaProvider',
    'CapitalProvider',
    'PepperstoneProvider',
    'ICMarketsProvider',
    'BrokerGateway',
    # Paper Trading (v2.0)
    'AlpacaPaperConnector',
    'BybitTestnetConnector',
    'PaperTradingGateway',
    'LeverageManager',
    'CircuitBreakerV2',
    'BrokerType',
    'VolatilityLevel',
]

