"""
🎯 Finage API Connector
Simple, unified API for Stocks, Forex, and Crypto prices.
Free tier: Good daily limits.
"""

import json
from js import fetch

class FinageConnector:
    """
    Finage.co.uk API Wrapper
    Supports: US Stocks, Forex, Crypto
    """
    
    BASE_URL = "https://api.finage.co.uk"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    async def get_stock_price(self, symbol):
        """Get last price for US stock (e.g., AAPL, TSLA)"""
        url = f"{self.BASE_URL}/last/stock/{symbol}?apikey={self.api_key}"
        
        try:
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "symbol" in data:
                return {
                    "status": "success",
                    "symbol": data.get("symbol"),
                    "price": float(data.get("price", 0)),
                    "bid": float(data.get("bid", 0)),
                    "ask": float(data.get("ask", 0)),
                    "timestamp": data.get("timestamp"),
                    "source": "finage"
                }
            else:
                return {"status": "error", "message": data.get("message", "Unknown error")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_forex_price(self, pair):
        """Get last price for Forex pair (e.g., EURUSD, GBPUSD)"""
        url = f"{self.BASE_URL}/last/forex/{pair}?apikey={self.api_key}"
        
        try:
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "symbol" in data:
                return {
                    "status": "success",
                    "symbol": data.get("symbol"),
                    "price": float(data.get("price", 0)),
                    "bid": float(data.get("bid", 0)),
                    "ask": float(data.get("ask", 0)),
                    "timestamp": data.get("timestamp"),
                    "source": "finage"
                }
            else:
                return {"status": "error", "message": data.get("message", "Unknown error")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_crypto_price(self, pair):
        """Get last price for Crypto (e.g., BTCUSD, ETHUSD)"""
        url = f"{self.BASE_URL}/last/crypto/{pair}?apikey={self.api_key}"
        
        try:
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "symbol" in data:
                return {
                    "status": "success",
                    "symbol": data.get("symbol"),
                    "price": float(data.get("price", 0)),
                    "bid": float(data.get("bid", 0)),
                    "ask": float(data.get("ask", 0)),
                    "timestamp": data.get("timestamp"),
                    "source": "finage"
                }
            else:
                return {"status": "error", "message": data.get("message", "Unknown error")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_aggregates(self, symbol, market_type="stock", timespan="day", start_date="2024-12-01", end_date="2024-12-08"):
        """
        Get aggregated OHLCV data
        market_type: "stock", "forex", "crypto"
        """
        url = f"{self.BASE_URL}/agg/{market_type}/{symbol}/1/{timespan}/{start_date}/{end_date}?apikey={self.api_key}"
        
        try:
            resp = await fetch(url)
            data = json.loads(await resp.text())
            
            if "results" in data:
                return {
                    "status": "success",
                    "symbol": symbol,
                    "results": data.get("results", []),
                    "source": "finage"
                }
            else:
                return {"status": "error", "message": data.get("message", "Unknown error")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
