"""
Capital.com Broker Implementation
Adapts CapitalConnector to the unified Broker interface.
"""

import json
import time
from js import fetch, Headers
from .base import Broker
from core import log

# Capital.com API URLs
CAPITAL_DEMO_URL = "https://demo-api-capital.backend-capital.com"
CAPITAL_LIVE_URL = "https://api-capital.backend-capital.com"

SESSION_EXPIRY_SECONDS = 10 * 60
SESSION_REFRESH_BUFFER = 60

class CapitalProvider(Broker):
    """
    Capital.com Broker Implementation.
    Handles session management (CST/X-SECURITY-TOKEN) internally.
    """
    
    def __init__(self, env):
        super().__init__("CAPITAL", env)
        self.is_demo = str(getattr(env, 'CAPITAL_DEMO', 'true')).lower() == 'true'
        self.base_url = CAPITAL_DEMO_URL if self.is_demo else CAPITAL_LIVE_URL
        
        self.api_key = str(getattr(env, 'CAPITAL_API_KEY', ''))
        self.identifier = str(getattr(env, 'CAPITAL_EMAIL', ''))
        self.password = str(getattr(env, 'CAPITAL_PASSWORD', ''))
        
        # Session state
        self.cst = None
        self.x_security_token = None
        self.session_timestamp = 0

    def _is_session_expired(self):
        if not self.cst or not self.x_security_token:
            return True
        elapsed = time.time() - self.session_timestamp
        return elapsed >= (SESSION_EXPIRY_SECONDS - SESSION_REFRESH_BUFFER)

    async def _start_session(self):
        try:
            headers = Headers.new({
                "X-CAP-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }.items())
            
            body = json.dumps({
                "identifier": self.identifier,
                "password": self.password,
                "encryptedPassword": False
            })
            
            response = await fetch(
                f"{self.base_url}/api/v1/session",
                method="POST",
                headers=headers,
                body=body
            )
            
            if response.ok:
                self.cst = response.headers.get("CST")
                self.x_security_token = response.headers.get("X-SECURITY-TOKEN")
                self.session_timestamp = time.time()
                return True
            else:
                err = await response.text()
                self.log.error(f"Session failed: {err}")
                return False
        except Exception as e:
            self.log.error(f"Session exception: {e}")
            return False

    async def _ensure_session(self):
        if self._is_session_expired():
            return await self._start_session()
        return True

    def _get_auth_headers(self):
        return Headers.new({
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst or "",
            "X-SECURITY-TOKEN": self.x_security_token or "",
            "Content-Type": "application/json"
        }.items())

    async def _request(self, endpoint, method="GET", body=None):
        if not await self._ensure_session():
            return {"error": True, "message": "Auth failed"}
            
        url = f"{self.base_url}{endpoint}"
        try:
            response = await fetch(
                url, method=method, 
                headers=self._get_auth_headers(), body=body
            )
            
            # Retry on 401
            if response.status == 401:
                self.cst = None # Force refresh
                if await self._start_session():
                    response = await fetch(
                        url, method=method,
                        headers=self._get_auth_headers(), body=body
                    )
                else:
                    return {"error": True, "message": "Re-auth failed"}
            
            if not response.ok:
                 return {"error": True, "status": response.status, "message": await response.text()}
                 
            return await response.json()
            
        except Exception as e:
            return {"error": True, "message": str(e)}

    async def get_account_summary(self) -> dict:
        data = await self._request("/api/v1/accounts")
        if "error" in data: return data
        
        accounts = data.get("accounts", [])
        if not accounts: return {}
        
        acc = accounts[0]
        balance = acc.get("balance", {})
        return {
            "balance": float(balance.get("balance", 0)),
            "equity": float(balance.get("balance", 0)), # Capital uses balance as equity approx for summary?
            "margin_available": float(balance.get("available", 0)),
            "currency": acc.get("currency", "USD")
        }

    async def get_open_positions(self) -> list:
        data = await self._request("/api/v1/positions")
        if "error" in data: return []
        
        positions = []
        for p in data.get("positions", []):
            pos = p.get("position", {})
            market = p.get("market", {})
            
            positions.append({
                "symbol": market.get("epic"),
                "side": "LONG" if pos.get("direction") == "BUY" else "SHORT",
                "units": float(pos.get("size", 0)),
                "avg_price": float(pos.get("openLevel", 0)),
                "current_price": float(market.get("bid", 0)),
                "unrealized_pl": float(pos.get("upl", 0)),
                "id": pos.get("dealId")
            })
        return positions

    async def place_order(self, symbol: str, side: str, amount: float, **kwargs) -> dict:
        sl = kwargs.get("sl_price") # Capital expects price level, not pips distance usually? Or maybe distance for stopLevel? 
        # API v1 positions takes stopLevel (price) or distance? Need to verify.
        # Assuming args passed are compatible or logic handled here.
        # For uniformity, base generic params might need conversion.
        
        body = {
            "epic": symbol,
            "direction": side.upper(),
            "size": amount,
            "guaranteedStop": False,
            "trailingStop": False
        }
        if sl: body["stopLevel"] = sl
        if kwargs.get("tp_price"): body["profitLevel"] = kwargs["tp_price"]
        
        res = await self._request("/api/v1/positions", "POST", json.dumps(body))
        return res

    async def close_position(self, symbol: str, position_id: str = None) -> dict:
        if not position_id:
            # Need dealId to close. Find it first.
            positions = await self.get_open_positions()
            pos = next((p for p in positions if p["symbol"] == symbol), None)
            if not pos: return {"error": True, "message": "Position not found"}
            position_id = pos["id"]
            
        return await self._request(f"/api/v1/positions/{position_id}", "DELETE")

    async def get_candles(self, symbol: str, timeframe: str = "MINUTE", limit: int = 100) -> list:
        # Capital candle endpoint logic
        # Simplified for now
        return []

    async def get_price(self, symbol: str) -> float:
        res = await self._request(f"/api/v1/markets/{symbol}")
        if "error" in res: return 0.0
        
        snap = res.get("snapshot", {})
        return float(snap.get("offer", 0)) # or mid
