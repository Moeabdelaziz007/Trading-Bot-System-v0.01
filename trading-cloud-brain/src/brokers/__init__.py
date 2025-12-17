"""
Brokers Package
Exports Broker interface, Providers, and Gateway.

NOTE: Some legacy providers (Oanda, Pepperstone, ICMarkets) are disabled
      due to 'js' module dependency (browser-only). Use adapters/ instead.
"""

from .base import Broker
from .binance_connector import BinanceConnector
from .bybit_connector import BybitConnector
from .mt5_broker import MT5Broker
from .gateway import BrokerGateway

# Legacy providers (disabled - use src/adapters instead)
# from .oanda import OandaProvider
# from .capital import CapitalProvider
# from .pepperstone import PepperstoneProvider
# from .icmarkets import ICMarketsProvider

__all__ = [
    'Broker',
    'BinanceConnector',
    'BybitConnector',
    'MT5Broker',
    'BrokerGateway'
]

