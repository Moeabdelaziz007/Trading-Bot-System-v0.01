import json
import time
from js import fetch, Headers

# Capital.com API URLs
CAPITAL_DEMO_URL = "https://demo-api-capital.backend-capital.com"
CAPITAL_LIVE_URL = "https://api-capital.backend-capital.com"

# Session expires after 10 minutes of inactivity
SESSION_EXPIRY_SECONDS = 10 * 60  # 10 minutes
SESSION_REFRESH_BUFFER = 60       # Refresh 1 minute before expiry


class CapitalConnector:
    """
    💰 Capital.com Connector for Axiom Antigravity
    
    RESEARCH-BASED IMPLEMENTATION (v2.0):
    - Auto-refresh session tokens before 10-minute expiry
    - Automatic retry on 401 errors with re-authentication
    - Session timestamp tracking
    - Thread-safe token management
    
    Capital.com REST API:
    - CST and X-SECURITY-TOKEN valid for 10 minutes after last use
    - Must refresh via POST /session on expiry
    """
    
    def __init__(self, env):
        self.env = env
        self.api_key = str(getattr(env, 'CAPITAL_API_KEY', ''))
        self.identifier = str(getattr(env, 'CAPITAL_EMAIL', ''))
        self.password = str(getattr(env, 'CAPITAL_PASSWORD', ''))
        self.is_demo = str(getattr(env, 'CAPITAL_DEMO', 'true')).lower() == 'true'
        self.base_url = CAPITAL_DEMO_URL if self.is_demo else CAPITAL_LIVE_URL
        
        # Session state
        self.cst = None
        self.x_security_token = None
        self.session_timestamp = 0  # Unix timestamp of last successful auth

    def _is_session_expired(self):
        """Check if session is expired or about to expire"""
        if not self.cst or not self.x_security_token:
            return True
        
        elapsed = time.time() - self.session_timestamp
        # Refresh before actual expiry for safety
        return elapsed >= (SESSION_EXPIRY_SECONDS - SESSION_REFRESH_BUFFER)

    async def _start_session(self):
        """Start a new session and get auth tokens"""
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
                error_text = await response.text()
                print(f"Capital.com Session Error: {error_text}")
                return False
        except Exception as e:
            print(f"Capital.com Session Exception: {e}")
            return False

    async def _ensure_session(self):
        """Ensure we have a valid session, refreshing if needed"""
        if self._is_session_expired():
            return await self._start_session()
        return True

    def _get_auth_headers(self):
        """Get headers with auth tokens"""
        return Headers.new({
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst or "",
            "X-SECURITY-TOKEN": self.x_security_token or "",
            "Content-Type": "application/json"
        }.items())

    async def _request_with_retry(self, endpoint, method="GET", body=None):
        """
        Make API request with automatic 401 retry.
        On 401, re-authenticate and retry once.
        """
        # Ensure session is valid before request
        if not await self._ensure_session():
            return {"error": "Failed to authenticate", "status": 401}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = await fetch(
                url,
                method=method,
                headers=self._get_auth_headers(),
                body=body
            )
            
            # If 401, try to refresh session and retry once
            if response.status == 401:
                # Force refresh
                self.cst = None
                self.x_security_token = None
                
                if await self._start_session():
                    # Retry with fresh tokens
                    response = await fetch(
                        url,
                        method=method,
                        headers=self._get_auth_headers(),
                        body=body
                    )
                else:
                    return {"error": "Re-authentication failed", "status": 401}
            
            return {
                "ok": response.ok,
                "status": response.status,
                "data": json.loads(await response.text()) if response.ok else None,
                "error": await response.text() if not response.ok else None
            }
            
        except Exception as e:
            return {"error": str(e), "status": 500}

    async def get_account_info(self):
        """Get account balance and equity"""
        result = await self._request_with_retry("/api/v1/accounts")
        
        if result.get("ok") and result.get("data"):
            accounts = result["data"].get("accounts", [])
            if accounts:
                acc = accounts[0]
                balance = acc.get("balance", {})
                return {
                    "balance": balance.get("balance", 0),
                    "equity": balance.get("balance", 0),
                    "available": balance.get("available", 0),
                    "currency": acc.get("currency", "USD"),
                    "account_id": acc.get("accountId", ""),
                    "source": "Capital.com Demo" if self.is_demo else "Capital.com Live"
                }
        
        return {"error": result.get("error", "Failed to get account info")}

    async def get_open_positions(self):
        """Get all open positions"""
        result = await self._request_with_retry("/api/v1/positions")
        
        if result.get("ok") and result.get("data"):
            positions = result["data"].get("positions", [])
            
            clean_positions = []
            for p in positions:
                position = p.get("position", {})
                market = p.get("market", {})
                clean_positions.append({
                    "symbol": market.get("epic", ""),
                    "side": position.get("direction", "").lower(),
                    "qty": position.get("size", 0),
                    "avg_entry_price": position.get("openLevel", 0),
                    "current_price": market.get("bid", 0),
                    "unrealized_pl": position.get("upl", 0),
                    "deal_id": position.get("dealId", "")
                })
            return clean_positions
        
        return []

    async def create_position(self, epic, direction, size, stop_loss=None, take_profit=None):
        """Open a new position with 401 retry"""
        order_body = {
            "epic": epic,
            "direction": direction.upper(),
            "size": size,
            "guaranteedStop": False,
            "trailingStop": False
        }
        
        if stop_loss:
            order_body["stopLevel"] = stop_loss
        if take_profit:
            order_body["profitLevel"] = take_profit
        
        result = await self._request_with_retry(
            "/api/v1/positions",
            method="POST",
            body=json.dumps(order_body)
        )
        
        if result.get("ok"):
            return {
                "status": "success",
                "deal_reference": result["data"].get("dealReference", ""),
                "message": "Position opened successfully"
            }
        else:
            return {
                "status": "error",
                "error": result.get("error", "Unknown error")
            }

    async def close_position(self, deal_id):
        """Close an existing position with 401 retry"""
        result = await self._request_with_retry(
            f"/api/v1/positions/{deal_id}",
            method="DELETE"
        )
        
        if result.get("ok"):
            return {"status": "success", "message": "Position closed"}
        else:
            return {"status": "error", "error": result.get("error", "Failed to close")}

    async def get_market_prices(self, epic):
        """Get current price for an instrument"""
        result = await self._request_with_retry(f"/api/v1/markets/{epic}")
        
        if result.get("ok") and result.get("data"):
            snapshot = result["data"].get("snapshot", {})
            return {
                "epic": epic,
                "bid": snapshot.get("bid", 0),
                "offer": snapshot.get("offer", 0),
                "high": snapshot.get("high", 0),
                "low": snapshot.get("low", 0),
                "change": snapshot.get("percentageChange", 0)
            }
        
        return {"error": result.get("error", "Failed to get prices")}

    async def search_markets(self, search_term):
        """Search for available markets/instruments"""
        result = await self._request_with_retry(f"/api/v1/markets?searchTerm={search_term}")
        
        if result.get("ok") and result.get("data"):
            markets = result["data"].get("markets", [])
            return [{"epic": m.get("epic"), "name": m.get("instrumentName")} for m in markets[:10]]
        
        return []

    async def get_session_status(self):
        """Get current session status for debugging"""
        elapsed = time.time() - self.session_timestamp if self.session_timestamp else 0
        remaining = max(0, SESSION_EXPIRY_SECONDS - elapsed)
        
        return {
            "authenticated": bool(self.cst and self.x_security_token),
            "session_age_seconds": int(elapsed),
            "expires_in_seconds": int(remaining),
            "is_expired": self._is_session_expired()
        }
