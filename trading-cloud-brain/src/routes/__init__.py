# Routes Module for AlphaAxiom Backend
# Extracted from worker.py for better maintainability

from .telegram import handle_telegram_webhook, send_telegram_alert, send_telegram_reply
from .cron import on_scheduled
from .api import (
    get_account, get_combined_account, get_account_data, get_alpaca_account_data,
    get_positions, get_combined_positions, get_alpaca_positions_data,
    get_candles, fetch_alpaca_bars, get_market_snapshot,
    get_dashboard_snapshot, publish_to_ably
)

__all__ = [
    # Telegram
    'handle_telegram_webhook', 'send_telegram_alert', 'send_telegram_reply',
    # Cron
    'on_scheduled',
    # API
    'get_account', 'get_combined_account', 'get_account_data', 'get_alpaca_account_data',
    'get_positions', 'get_combined_positions', 'get_alpaca_positions_data',
    'get_candles', 'fetch_alpaca_bars', 'get_market_snapshot',
    'get_dashboard_snapshot', 'publish_to_ably',
]
