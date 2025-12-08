"""
Fetch Tools: Technical Indicators
Fetches RSI, MACD, ADX from Alpha Vantage.
"""

from js import fetch
import json

async def get_alpha_vantage_technicals(symbol: str, api_key: str) -> dict:
    """
    Fetch technical indicators from Alpha Vantage.
    EXPENSIVE: Costs 3 credits (25/day limit).
    
    Makes 3 API calls: RSI, MACD, ADX (but we batch if possible)
    
    Returns:
        {
            "rsi_14": float,
            "macd": {"value": float, "signal": float, "histogram": float},
            "adx": float,
            "source": "alpha_vantage"
        }
    """
    base_url = "https://www.alphavantage.co/query"
    
    results = {
        "rsi_14": None,
        "macd": None,
        "adx": None,
        "source": "alpha_vantage"
    }
    
    try:
        # RSI
        rsi_url = f"{base_url}?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={api_key}"
        rsi_resp = await fetch(rsi_url)
        rsi_data = await rsi_resp.json()
        
        if "Technical Analysis: RSI" in rsi_data:
            latest_date = list(rsi_data["Technical Analysis: RSI"].keys())[0]
            results["rsi_14"] = float(rsi_data["Technical Analysis: RSI"][latest_date]["RSI"])
        
        # MACD
        macd_url = f"{base_url}?function=MACD&symbol={symbol}&interval=daily&series_type=close&apikey={api_key}"
        macd_resp = await fetch(macd_url)
        macd_data = await macd_resp.json()
        
        if "Technical Analysis: MACD" in macd_data:
            latest_date = list(macd_data["Technical Analysis: MACD"].keys())[0]
            macd_entry = macd_data["Technical Analysis: MACD"][latest_date]
            results["macd"] = {
                "value": float(macd_entry.get("MACD", 0)),
                "signal": float(macd_entry.get("MACD_Signal", 0)),
                "histogram": float(macd_entry.get("MACD_Hist", 0))
            }
        
        # ADX
        adx_url = f"{base_url}?function=ADX&symbol={symbol}&interval=daily&time_period=14&apikey={api_key}"
        adx_resp = await fetch(adx_url)
        adx_data = await adx_resp.json()
        
        if "Technical Analysis: ADX" in adx_data:
            latest_date = list(adx_data["Technical Analysis: ADX"].keys())[0]
            results["adx"] = float(adx_data["Technical Analysis: ADX"][latest_date]["ADX"])
    
    except Exception as e:
        results["error"] = str(e)
    
    return results
