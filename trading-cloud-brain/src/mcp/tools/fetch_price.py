"""
Fetch Tools: Price Data Workers
Fetches real-time price from Finnhub and Bybit APIs.
"""

from js import fetch
import json

async def get_finnhub_price(symbol: str, api_key: str) -> dict:
    """
    Fetch price from Finnhub (Stocks/Forex).
    
    Args:
        symbol: Stock symbol (e.g., "AAPL")
        api_key: Finnhub API key
        
    Returns:
        {"current": float, "change_pct": float, "source": "finnhub"}
    """
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
    
    try:
        response = await fetch(url)
        data = await response.json()
        
        # Finnhub returns: c=current, pc=previous close, dp=percent change
        current = data.get("c", 0)
        prev_close = data.get("pc", current)
        change_pct = (current - prev_close) / prev_close if prev_close else 0
        
        return {
            "current": current,
            "change_pct": round(change_pct, 4),
            "high": data.get("h", current),
            "low": data.get("l", current),
            "source": "finnhub"
        }
    except Exception as e:
        return {"error": str(e), "source": "finnhub"}


async def get_bybit_price(symbol: str) -> dict:
    """
    Fetch price from Bybit (Crypto - FREE & Unlimited!).
    
    Args:
        symbol: Crypto pair (e.g., "BTCUSDT")
        
    Returns:
        {"current": float, "change_pct": float, "source": "bybit"}
    """
    # Bybit public API - No auth needed!
    url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
    
    try:
        response = await fetch(url)
        data = await response.json()
        
        if data.get("retCode") == 0 and data.get("result", {}).get("list"):
            ticker = data["result"]["list"][0]
            return {
                "current": float(ticker.get("lastPrice", 0)),
                "change_pct": float(ticker.get("price24hPcnt", 0)),
                "high_24h": float(ticker.get("highPrice24h", 0)),
                "low_24h": float(ticker.get("lowPrice24h", 0)),
                "volume_24h": float(ticker.get("volume24h", 0)),
                "source": "bybit"
            }
        else:
            return {"error": data.get("retMsg", "Unknown error"), "source": "bybit"}
    except Exception as e:
        return {"error": str(e), "source": "bybit"}
