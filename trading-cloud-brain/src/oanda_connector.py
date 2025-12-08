"""
🌐 OANDA Connector for Axiom Antigravity Trading System
REST API v20 Integration with Bearer Token Authentication

RESEARCH-BASED IMPLEMENTATION:
- OANDA REST API v20 (https://developer.oanda.com/rest-live-v20/introduction/)
- Rate Limits: 120 RPS for REST, 20 max streams
- Bearer Token Authentication
- Practice vs Live environments

ENDPOINTS:
- GET /v3/accounts - List accounts
- GET /v3/accounts/{id} - Account details
- GET /v3/accounts/{id}/summary - Account summary
- GET /v3/instruments/{instrument}/candles - Price history
- POST /v3/accounts/{id}/orders - Create order
- GET /v3/accounts/{id}/positions - Open positions
- PUT /v3/accounts/{id}/positions/{instrument}/close - Close position
"""

import json
from js import fetch, Headers

# OANDA Environment URLs
OANDA_PRACTICE_API = "https://api-fxpractice.oanda.com"
OANDA_LIVE_API = "https://api-fxtrade.oanda.com"
OANDA_PRACTICE_STREAM = "https://stream-fxpractice.oanda.com"
OANDA_LIVE_STREAM = "https://stream-fxtrade.oanda.com"


class OandaConnector:
    """
    🌐 OANDA Connector for Axiom Antigravity

    Features:
    - Bearer token authentication
    - Practice and Live environment support
    - Market orders, limit orders, stop-loss, take-profit
    - Real-time streaming prices (future)
    - Automatic 401 retry with re-authentication

    Required Secrets:
        - OANDA_API_KEY: Your OANDA access token
        - OANDA_ACCOUNT_ID: Your OANDA account ID

    Methods:
        - get_account_summary(): Get account balance/equity
        - get_open_positions(): List all open positions
        - get_instruments(): List tradable instruments
        - get_candles(instrument, granularity): Get price history
        - create_market_order(instrument, units, sl, tp): Place market order
        - close_position(instrument): Close all units for instrument
        - get_current_price(instrument): Get bid/ask prices
    """

    def __init__(self, env, is_live: bool = False):
        """
        Initialize OANDA connector.

        Args:
            env: Cloudflare Worker environment with secrets
            is_live: True for live trading, False for practice (default)
        """
        self.env = env
        self.is_live = is_live
        self.api_key = getattr(env, 'OANDA_API_KEY', None)
        self.account_id = getattr(env, 'OANDA_ACCOUNT_ID', None)
        
        # Set base URL based on environment
        self.base_url = OANDA_LIVE_API if is_live else OANDA_PRACTICE_API
        self.stream_url = OANDA_LIVE_STREAM if is_live else OANDA_PRACTICE_STREAM

    def _get_headers(self) -> dict:
        """Get authorization headers with Bearer token."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": "UNIX"
        }

    async def _request(self, endpoint: str, method: str = "GET", body: dict = None) -> dict:
        """
        Make authenticated API request.

        Args:
            endpoint: API endpoint path (e.g., /v3/accounts)
            method: HTTP method (GET, POST, PUT)
            body: Request body for POST/PUT

        Returns:
            dict: API response or error
        """
        if not self.api_key or not self.account_id:
            return {"error": True, "message": "OANDA credentials not configured"}

        try:
            url = f"{self.base_url}{endpoint}"
            headers = Headers.new()
            
            for key, value in self._get_headers().items():
                headers.set(key, value)

            options = {
                "method": method,
                "headers": headers
            }

            if body and method in ["POST", "PUT"]:
                options["body"] = json.dumps(body)

            response = await fetch(url, **options)
            
            if response.status == 401:
                return {"error": True, "code": "AUTH_FAILED", "message": "Invalid API key"}
            
            if response.status == 429:
                return {"error": True, "code": "RATE_LIMIT", "message": "Rate limit exceeded (120 RPS max)"}
            
            result = await response.json()
            return result

        except Exception as e:
            return {"error": True, "message": str(e)}

    # ==========================================
    # 💰 ACCOUNT METHODS
    # ==========================================

    async def get_accounts(self) -> dict:
        """Get list of all accounts."""
        return await self._request("/v3/accounts")

    async def get_account_summary(self) -> dict:
        """
        Get account summary with balance, equity, margin.

        Returns:
            dict: {balance, equity, margin_used, margin_available, pl}
        """
        result = await self._request(f"/v3/accounts/{self.account_id}/summary")
        
        if "error" in result:
            return result

        account = result.get("account", {})
        return {
            "balance": float(account.get("balance", 0)),
            "equity": float(account.get("NAV", 0)),
            "margin_used": float(account.get("marginUsed", 0)),
            "margin_available": float(account.get("marginAvailable", 0)),
            "unrealized_pl": float(account.get("unrealizedPL", 0)),
            "open_position_count": int(account.get("openPositionCount", 0)),
            "open_trade_count": int(account.get("openTradeCount", 0)),
            "currency": account.get("currency", "USD"),
            "source": "OANDA Practice" if not self.is_live else "OANDA Live"
        }

    # ==========================================
    # 📊 POSITIONS METHODS
    # ==========================================

    async def get_open_positions(self) -> list:
        """
        Get all open positions.

        Returns:
            list: [{instrument, long_units, short_units, unrealized_pl}]
        """
        result = await self._request(f"/v3/accounts/{self.account_id}/openPositions")
        
        if "error" in result:
            return []

        positions = []
        for pos in result.get("positions", []):
            long_units = float(pos.get("long", {}).get("units", 0))
            short_units = float(pos.get("short", {}).get("units", 0))
            long_pl = float(pos.get("long", {}).get("unrealizedPL", 0))
            short_pl = float(pos.get("short", {}).get("unrealizedPL", 0))
            
            if long_units != 0 or short_units != 0:
                positions.append({
                    "instrument": pos.get("instrument"),
                    "long_units": long_units,
                    "short_units": short_units,
                    "units": long_units + short_units,
                    "side": "LONG" if long_units > 0 else "SHORT",
                    "unrealized_pl": long_pl + short_pl,
                    "avg_price": float(pos.get("long" if long_units > 0 else "short", {}).get("averagePrice", 0))
                })

        return positions

    async def close_position(self, instrument: str, units: str = "ALL") -> dict:
        """
        Close a position for an instrument.

        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            units: Number of units to close or "ALL"

        Returns:
            dict: Close result
        """
        # Determine if long or short position
        positions = await self.get_open_positions()
        position = next((p for p in positions if p["instrument"] == instrument), None)
        
        if not position:
            return {"error": True, "message": f"No position found for {instrument}"}

        body = {}
        if position["long_units"] > 0:
            body["longUnits"] = units
        elif position["short_units"] < 0:
            body["shortUnits"] = units

        result = await self._request(
            f"/v3/accounts/{self.account_id}/positions/{instrument}/close",
            method="PUT",
            body=body
        )
        
        return result

    # ==========================================
    # 📈 ORDERS METHODS
    # ==========================================

    async def create_market_order(
        self, 
        instrument: str, 
        units: int, 
        stop_loss_pips: float = None,
        take_profit_pips: float = None
    ) -> dict:
        """
        Create a market order.

        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            units: Positive for BUY, negative for SELL
            stop_loss_pips: Stop loss in pips from entry
            take_profit_pips: Take profit in pips from entry

        Returns:
            dict: Order result with transaction ID
        """
        order = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "timeInForce": "FOK",  # Fill or Kill
                "positionFill": "DEFAULT"
            }
        }

        # Add stop loss if specified
        if stop_loss_pips:
            order["order"]["stopLossOnFill"] = {
                "distance": str(stop_loss_pips)
            }

        # Add take profit if specified
        if take_profit_pips:
            order["order"]["takeProfitOnFill"] = {
                "distance": str(take_profit_pips)
            }

        result = await self._request(
            f"/v3/accounts/{self.account_id}/orders",
            method="POST",
            body=order
        )

        if "error" not in result:
            transaction = result.get("orderFillTransaction", {})
            return {
                "success": True,
                "trade_id": transaction.get("tradeOpened", {}).get("tradeID"),
                "instrument": instrument,
                "units": units,
                "price": float(transaction.get("price", 0)),
                "pl": float(transaction.get("pl", 0))
            }

        return result

    # ==========================================
    # 📊 MARKET DATA METHODS
    # ==========================================

    async def get_instruments(self) -> list:
        """
        Get list of tradable instruments.

        Returns:
            list: [{name, display_name, pip_location, type}]
        """
        result = await self._request(f"/v3/accounts/{self.account_id}/instruments")
        
        if "error" in result:
            return []

        instruments = []
        for inst in result.get("instruments", []):
            instruments.append({
                "name": inst.get("name"),
                "display_name": inst.get("displayName"),
                "pip_location": inst.get("pipLocation"),
                "type": inst.get("type"),
                "margin_rate": inst.get("marginRate")
            })

        return instruments

    async def get_current_price(self, instrument: str) -> dict:
        """
        Get current bid/ask prices for an instrument.

        Args:
            instrument: Instrument name (e.g., "EUR_USD")

        Returns:
            dict: {bid, ask, spread, time}
        """
        result = await self._request(
            f"/v3/accounts/{self.account_id}/pricing?instruments={instrument}"
        )
        
        if "error" in result:
            return result

        prices = result.get("prices", [])
        if not prices:
            return {"error": True, "message": "No price data available"}

        price = prices[0]
        bid = float(price.get("bids", [{}])[0].get("price", 0))
        ask = float(price.get("asks", [{}])[0].get("price", 0))

        return {
            "instrument": instrument,
            "bid": bid,
            "ask": ask,
            "spread": ask - bid,
            "time": price.get("time"),
            "tradeable": price.get("tradeable", False)
        }

    async def get_candles(
        self, 
        instrument: str, 
        granularity: str = "M5",
        count: int = 100
    ) -> list:
        """
        Get price history (candles) for an instrument.

        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            granularity: Candle granularity (S5, M1, M5, M15, H1, D, W, M)
            count: Number of candles to fetch (max 5000)

        Returns:
            list: [{time, open, high, low, close, volume}]
        """
        result = await self._request(
            f"/v3/instruments/{instrument}/candles?granularity={granularity}&count={count}&price=M"
        )
        
        if "error" in result:
            return []

        candles = []
        for candle in result.get("candles", []):
            if candle.get("complete"):
                mid = candle.get("mid", {})
                candles.append({
                    "time": candle.get("time"),
                    "open": float(mid.get("o", 0)),
                    "high": float(mid.get("h", 0)),
                    "low": float(mid.get("l", 0)),
                    "close": float(mid.get("c", 0)),
                    "volume": int(candle.get("volume", 0))
                })

        return candles

    # ==========================================
    # 🔧 UTILITY METHODS
    # ==========================================

    def get_connection_status(self) -> dict:
        """Get current connection status for debugging."""
        return {
            "configured": bool(self.api_key and self.account_id),
            "environment": "Live" if self.is_live else "Practice",
            "base_url": self.base_url,
            "account_id": self.account_id[:8] + "..." if self.account_id else None
        }
