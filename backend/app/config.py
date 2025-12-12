# backend/app/config.py
# ==============================================
# TRADING SYSTEM 0.1 - CONFIGURATION
# ==============================================

import os
from dotenv import load_dotenv
from app.utils.secrets_manager import secrets

load_dotenv()

# ============================================
# DEMO MODE (للعروض التقديمية)
# ============================================
DEMO_MODE = secrets.get_secret("DEMO_MODE", "true").lower() == "true"

# ============================================
# ALPACA API (Stocks, Gold, ETFs)
# Paper Trading: https://app.alpaca.markets/paper/dashboard
# ============================================
ALPACA_KEY = secrets.get_secret("ALPACA_KEY", "demo_key")
ALPACA_SECRET = secrets.get_secret("ALPACA_SECRET", "demo_secret")
ALPACA_ENDPOINT = secrets.get_secret("ALPACA_ENDPOINT", "https://paper-api.alpaca.markets")

# ============================================
# BINANCE API (Crypto via Jesse or Direct)
# ============================================
BINANCE_KEY = secrets.get_secret("BINANCE_KEY", "")
BINANCE_SECRET = secrets.get_secret("BINANCE_SECRET", "")

# ============================================
# ASSET MAPPINGS
# ============================================
ASSET_SYMBOL_MAP = {
    # Crypto
    "BTC": "BTC/USDT",
    "ETH": "ETH/USDT",
    "SOL": "SOL/USDT",
    
    # Stocks
    "TSLA": "TSLA",
    "NVDA": "NVDA",
    "AAPL": "AAPL",
    "SPY": "SPY",
    "QQQ": "QQQ",
    
    # Gold & Commodities (ETFs for simplicity)
    "GOLD": "GLD",      # SPDR Gold Trust ETF
    "XAUUSD": "GLD",
    "SILVER": "SLV",    # iShares Silver Trust ETF
    "XAGUSD": "SLV",
    "OIL": "USO",       # United States Oil Fund
}

# ============================================
# RISK MANAGEMENT
# ============================================
MAX_POSITION_SIZE_PERCENT = 5.0  # Max 5% of portfolio per trade
DEFAULT_STOP_LOSS_PERCENT = 2.0  # Default SL: -2%
DEFAULT_TAKE_PROFIT_PERCENT = 4.0  # Default TP: +4%

# ============================================
# AI MODEL API KEYS
# ============================================
ZHIPU_API_KEY = secrets.get_secret("ZHIPU_API_KEY", "")  # GLM-4 / Z.ai
OPENROUTER_API_KEY = secrets.get_secret("OPENROUTER_API_KEY", "")  # Multi-Model Gateway
GROQ_API_KEY = secrets.get_secret("GROQ_API_KEY", "")  # Groq LPU
GEMINI_API_KEY = secrets.get_secret("GEMINI_API_KEY", "")  # Google Gemini
DEEPSEEK_API_KEY = secrets.get_secret("DEEPSEEK_API_KEY", "")  # DeepSeek
