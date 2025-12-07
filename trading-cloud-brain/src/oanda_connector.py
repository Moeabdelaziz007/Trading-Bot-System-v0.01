import json
from js import fetch, Headers

# OANDA API URLs
OANDA_PRACTICE_URL = "https://api-fxpractice.oanda.com/v3"
OANDA_LIVE_URL = "https://api-fxtrade.oanda.com/v3"

class OandaConnector:
    """
    🦅 OANDA Connector for Axiom Antigravity
    Handles Real/Demo Forex Trading via OANDA v20 API
    """
    def __init__(self, env):
        self.env = env
        self.account_id = str(getattr(env, 'OANDA_ACCOUNT_ID', ''))
        self.api_key = str(getattr(env, 'OANDA_API_KEY', ''))
        self.is_demo = str(getattr(env, 'OANDA_DEMO', 'true')).lower() == 'true'
        self.base_url = OANDA_PRACTICE_URL if self.is_demo else OANDA_LIVE_URL
        
    def _get_headers(self):
        return Headers.new({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "RFC3339"
        }.items())

    async def get_account_summary(self):
        """Get Account Balance & Equity"""
        try:
            if not self.api_key or not self.account_id:
                return {"error": "OANDA credentials missing"}
                
            url = f"{self.base_url}/accounts/{self.account_id}/summary"
            response = await fetch(url, method="GET", headers=self._get_headers())
            
            if response.ok:
                data = json.loads(await response.text())
                account = data.get("account", {})
                return {
                    "balance": account.get("balance", "0.0"),
                    "equity": account.get("NAV", "0.0"), # Net Asset Value is Equity
                    "unrealized_pl": account.get("unrealizedPL", "0.0"),
                    "margin_used": account.get("marginUsed", "0.0"),
                    "margin_available": account.get("marginAvailable", "0.0"),
                    "currency": account.get("currency", "USD")
                }
            return {"error": f"OANDA Error: {response.status}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_open_positions(self):
        """Get all open positions"""
        try:
            if not self.api_key or not self.account_id:
                return []
                
            url = f"{self.base_url}/accounts/{self.account_id}/openPositions"
            response = await fetch(url, method="GET", headers=self._get_headers())
            
            if response.ok:
                data = json.loads(await response.text())
                oanda_positions = data.get("positions", [])
                
                clean_positions = []
                for p in oanda_positions:
                    # OANDA separates long and short units
                    long_units = int(p.get("long", {}).get("units", 0))
                    short_units = int(p.get("short", {}).get("units", 0))
                    
                    if long_units > 0:
                        clean_positions.append({
                            "symbol": p.get("instrument").replace("_", "/"),
                            "side": "buy",
                            "qty": long_units,
                            "avg_entry_price": p.get("long", {}).get("averagePrice", "0"),
                            "unrealized_pl": p.get("long", {}).get("unrealizedPL", "0")
                        })
                    
                    if short_units < 0: # Short units are negative in OANDA sometimes, or just checked by existence
                        clean_positions.append({
                            "symbol": p.get("instrument").replace("_", "/"),
                            "side": "sell",
                            "qty": abs(short_units),
                            "avg_entry_price": p.get("short", {}).get("averagePrice", "0"),
                            "unrealized_pl": p.get("short", {}).get("unrealizedPL", "0")
                        })
                        
                return clean_positions
            return []
        except Exception as e:
            print(f"OANDA Positions Error: {e}")
            return []

    async def create_market_order(self, symbol, units):
        """
        Place Market Order
        symbol: e.g. "EUR_USD"
        units: positive for buy, negative for sell
        """
        try:
            if not self.api_key: return {"status": "error", "error": "No API Key"}
            
            # Format symbol (EUR/USD -> EUR_USD)
            instrument = symbol.replace("/", "_").replace("-", "_").upper()
            
            body = json.dumps({
                "order": {
                    "units": str(units),
                    "instrument": instrument,
                    "timeInForce": "FOK",
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            })
            
            url = f"{self.base_url}/accounts/{self.account_id}/orders"
            response = await fetch(url, method="POST", headers=self._get_headers(), body=body)
            
            data = json.loads(await response.text())
            
            if response.status == 201:
                fill = data.get("orderFillTransaction", {})
                return {
                    "status": "success",
                    "price": fill.get("price", "0"),
                    "id": fill.get("orderID", ""),
                    "units": fill.get("units", "0")
                }
            else:
                return {"status": "error", "error": str(data)}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_candles(self, symbol, granularity="H1", count=100):
        """Get historical candles"""
        try:
            instrument = symbol.replace("/", "_").upper()
            url = f"{self.base_url}/instruments/{instrument}/candles?count={count}&granularity={granularity}&price=M"
            
            response = await fetch(url, method="GET", headers=self._get_headers())
            if response.ok:
                data = json.loads(await response.text())
                candles = []
                for c in data.get("candles", []):
                    candles.append({
                        "time": c.get("time").split("T")[0], # Simple date
                        "open": float(c.get("mid", {}).get("o", 0)),
                        "high": float(c.get("mid", {}).get("h", 0)),
                        "low": float(c.get("mid", {}).get("l", 0)),
                        "close": float(c.get("mid", {}).get("c", 0)),
                        "volume": int(c.get("volume", 0))
                    })
                return candles
            return []
        except:
            return []

