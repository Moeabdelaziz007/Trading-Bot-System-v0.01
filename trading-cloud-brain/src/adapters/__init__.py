"""
🔌 Exchange Adapters Module
===========================
Unified interface for multi-exchange trading (Bybit, MT5, etc.)

Usage:
    from src.adapters import AdapterFactory, BybitAdapter, MT5Adapter
    
    # Create adapter via factory
    bybit = AdapterFactory.create('bybit', api_key='...', api_secret='...')
    
    # Or directly
    mt5 = MT5Adapter(bridge_url='...', auth_token='...')
"""

from .base import (
    ExchangeAdapter,
    AdapterFactory,
    Position,
    OrderResult,
    OrderSide,
    OrderType
)

from .bybit_adapter import BybitAdapter
from .mt5_adapter import MT5Adapter

__all__ = [
    'ExchangeAdapter',
    'AdapterFactory',
    'Position',
    'OrderResult',
    'OrderSide',
    'OrderType',
    'BybitAdapter',
    'MT5Adapter',
]

