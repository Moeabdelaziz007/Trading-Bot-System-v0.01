"""
OANDA Broker Implementation
Adapts OandaConnector to the unified Broker interface.
"""

import json
from js import fetch, Headers
from .base import Broker
from core import log

# OANDA Environment URLs
OANDA_PRACTICE_API = "https://api-fxpractice.oanda.com"
OANDA_LIVE_API = "https://api-fxtrade.oanda.com"


class OandaProvider(Broker):
    """
    OANDA Broker Implementation.
    """
    
    def __init__(self, env):
        super().__init__("OANDA", env)
        self.is_live = getattr(env, 'TRADING_MODE', 'PAPER') == 'LIVE'
        self.api_key = getattr(env, 'OANDA_API_KEY', None)
        self.account_id = getattr(env, 'OANDA_ACCOUNT_ID', None)
        
        self.base_url = OANDA_LIVE_API if self.is_live else OANDA_PRACTICE_API
        
        if not self.api_key or not self.account_id:
            self.log.warning("OANDA credentials missing")

    def _get_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "UNIX"
        }

    async def _request(self, endpoint: str, method: str = "GET", body: dict = None) -> dict:
        if not self.api_key:
            return {"error": True, "message": "OANDA API Key missing"}
            
        try:
            url = f"{self.base_url}{endpoint}"
            headers = Headers.new()
            for k, v in self._get_headers().items():
                headers.set(k, v)
                
            options = {"method": method, "headers": headers}
            if body and method in ["POST", "PUT"]:
                options["body"] = json.dumps(body)
                
            response = await fetch(url, **options)
            
            if not response.ok:
                return {
                    "error": True, 
                    "status": response.status, 
                    "message": f"HTTP {response.status}"
                }
                
            return await response.json()
            
        except Exception as e:
            self.log.error(f"Request failed: {e}")
            return {"error": True, "message": str(e)}

    async def get_account_summary(self) -> dict:
        data = await self._request(f"/v3/accounts/{self.account_id}/summary")
        if "error" in data: return data
        
        acc = data.get("account", {})
        return {
            "balance": float(acc.get("balance", 0)),
            "equity": float(acc.get("NAV", 0)),
            "margin_used": float(acc.get("marginUsed", 0)),
            "free_margin": float(acc.get("marginAvailable", 0)),
            "currency": acc.get("currency", "USD")
        }

    async def get_open_positions(self) -> list:
        data = await self._request(f"/v3/accounts/{self.account_id}/openPositions")
        if "error" in data: return []
        
        positions = []
        for p in data.get("positions", []):
            long_units = float(p.get("long", {}).get("units", 0))
            short_units = float(p.get("short", {}).get("units", 0))
            
            if long_units != 0 or short_units != 0:
                side = "LONG" if long_units > 0 else "SHORT"
                units = long_units + short_units
                avg_price = float(p.get("long" if side == "LONG" else "short", {}).get("averagePrice", 0))
                
                positions.append({
                    "symbol": p.get("instrument"),
                    "side": side,
                    "units": units,
                    "avg_price": avg_price,
                    "unrealized_pl": float(p.get("unrealizedPL", 0))
                })
        return positions

    async def place_order(self, symbol: str, side: str, amount: float, **kwargs) -> dict:
        units = int(amount) if side.upper() == "BUY" else -int(amount)
        
        order = {
            "order": {
                "type": "MARKET",
                "instrument": symbol,
                "units": str(units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT"
            }
        }
        
        if "sl_pips" in kwargs:
             order["order"]["stopLossOnFill"] = {"distance": str(kwargs["sl_pips"])}
        if "tp_pips" in kwargs:
             order["order"]["takeProfitOnFill"] = {"distance": str(kwargs["tp_pips"])}
             
        res = await self._request(f"/v3/accounts/{self.account_id}/orders", "POST", order)
        return res

    async def close_position(self, symbol: str, position_id: str = None) -> dict:
        # Simplified close all for symbol
        positions = await self.get_open_positions()
        pos = next((p for p in positions if p["symbol"] == symbol), None)
        if not pos: return {"error": True, "message": "Position not found"}
        
        body = {}
        if pos["side"] == "LONG": body["longUnits"] = "ALL"
        else: body["shortUnits"] = "ALL"
            
        return await self._request(
            f"/v3/accounts/{self.account_id}/positions/{symbol}/close", 
            "PUT", body
        )

    async def get_candles(self, symbol: str, timeframe: str = "M5", limit: int = 100) -> list:
        # Map timeframe to OANDA granularity if needed
        granularity = timeframe # e.g. M5, H1
        res = await self._request(
            f"/v3/instruments/{symbol}/candles?granularity={granularity}&count={limit}&price=M"
        )
        if "error" in res: return []
        
        candles = []
        for c in res.get("candles", []):
            if c.get("complete"):
                mid = c.get("mid", {})
                candles.append({
                    "time": c.get("time"),
                    "open": float(mid.get("o", 0)),
                    "high": float(mid.get("h", 0)),
                    "low": float(mid.get("l", 0)),
                    "close": float(mid.get("c", 0)),
                    "volume": int(c.get("volume", 0))
                })
        return candles

    async def get_price(self, symbol: str) -> float:
        res = await self._request(f"/v3/accounts/{self.account_id}/pricing?instruments={symbol}")
        if "error" in res or not res.get("prices"): return 0.0
        
        price = res["prices"][0]
        bid = float(price.get("bids", [{}])[0].get("price", 0))
        ask = float(price.get("asks", [{}])[0].get("price", 0))
        return (bid + ask) / 2
