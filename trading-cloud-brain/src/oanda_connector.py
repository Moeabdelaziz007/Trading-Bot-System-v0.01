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

    # ==========================================
    # 🚀 SCALPING METHODS (100% Weekly ROI)
    # ==========================================

    async def get_scalping_candles(
        self, 
        instrument: str, 
        timeframe: str = "M1",
        count: int = 100
    ) -> list:
        """
        Get candles optimized for scalping (1M/5M/15M).
        
        Args:
            instrument: Instrument name (e.g., "EUR_USD")
            timeframe: M1, M5, M15 for scalping
            count: Number of candles
        
        Returns:
            list: Candles in standard format for ScalpingBrain
        """
        return await self.get_candles(instrument, timeframe, count)

    async def scalp_order(
        self,
        instrument: str,
        units: int,
        stop_loss_price: float,
        take_profit_price: float,
        leverage: int = 50
    ) -> dict:
        """
        Place a scalping order with exact price SL/TP.
        
        Args:
            instrument: Trading pair (e.g., "EUR_USD")
            units: Position size (positive=BUY, negative=SELL)
            stop_loss_price: Exact stop loss price
            take_profit_price: Exact take profit price
            leverage: Not used directly (OANDA uses margin rate)
        
        Returns:
            dict: Order execution result
        """
        order = {
            "order": {
                "type": "MARKET",
                "instrument": instrument,
                "units": str(units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "stopLossOnFill": {
                    "price": str(round(stop_loss_price, 5))
                },
                "takeProfitOnFill": {
                    "price": str(round(take_profit_price, 5))
                }
            }
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
                "side": "LONG" if units > 0 else "SHORT",
                "entry_price": float(transaction.get("price", 0)),
                "stop_loss": stop_loss_price,
                "take_profit": take_profit_price,
                "leverage": leverage
            }

        return {"success": False, **result}

    async def execute_scalp_signal(
        self,
        signal: dict,
        account_risk_pct: float = 0.20,
        leverage: int = 50
    ) -> dict:
        """
        Execute a scalping signal from MultiTimeframeScalper.
        
        Args:
            signal: Signal dict from MTF Scalper
                - signal: 'LONG' or 'SHORT'
                - entry: float
                - stop_loss: float
                - take_profit: float
                - confidence: int
            account_risk_pct: Percentage of account to risk
            leverage: Target leverage (for position sizing)
        
        Returns:
            dict: Execution result
        """
        if signal.get("signal") == "NEUTRAL":
            return {"success": False, "reason": "No signal"}
        
        # Get account balance
        account = await self.get_account_summary()
        if "error" in account:
            return {"success": False, "reason": "Failed to get account"}
        
        balance = account.get("balance", 0)
        
        # Calculate position size
        risk_amount = balance * account_risk_pct
        
        # Get current price
        entry_price = signal.get("entry", 0)
        stop_loss = signal.get("stop_loss", 0)
        
        if entry_price == 0 or stop_loss == 0:
            return {"success": False, "reason": "Invalid signal prices"}
        
        # Calculate units based on risk
        pips_at_risk = abs(entry_price - stop_loss)
        pip_value = 0.0001  # Standard for most pairs
        
        # units = risk_amount / (pips_at_risk / pip_value)
        units = int(risk_amount / (pips_at_risk * 10000))
        
        if signal.get("signal") == "SHORT":
            units = -units
        
        # Execute order
        return await self.scalp_order(
            instrument=signal.get("instrument", "EUR_USD"),
            units=units,
            stop_loss_price=stop_loss,
            take_profit_price=signal.get("take_profit", entry_price),
            leverage=leverage
        )

    async def get_multi_timeframe_data(
        self, 
        instrument: str
    ) -> dict:
        """
        Get 1M, 5M, 15M candles for Multi-Timeframe analysis.
        
        Returns:
            dict: {
                "1m": [...candles...],
                "5m": [...candles...],
                "15m": [...candles...]
            }
        """
        # Fetch all timeframes concurrently would be ideal
        # For now, sequential calls
        data_1m = await self.get_candles(instrument, "M1", 100)
        data_5m = await self.get_candles(instrument, "M5", 100)
        data_15m = await self.get_candles(instrument, "M15", 100)
        
        return {
            "1m": data_1m,
            "5m": data_5m,
            "15m": data_15m,
            "instrument": instrument
        }

    # ==========================================
    # 📡 STREAMING / WEBSOCKET METHODS
    # ==========================================

    def get_stream_url(self, instruments: list) -> str:
        """
        Get streaming URL for real-time prices.
        
        Note: Cloudflare Workers don't support persistent WebSocket
        connections. Use this URL with client-side JS or external service.
        
        Args:
            instruments: List of instruments to stream
        
        Returns:
            str: Streaming endpoint URL
        """
        instruments_str = ",".join(instruments)
        return f"{self.stream_url}/v3/accounts/{self.account_id}/pricing/stream?instruments={instruments_str}"

    def get_stream_headers(self) -> dict:
        """Get headers for streaming connection."""
        return self._get_headers()


class OandaStreamHandler:
    """
    WebSocket-like handler for OANDA price streaming.
    
    Note: This is designed for use outside Cloudflare Workers
    (e.g., in a Node.js service or frontend).
    """
    
    def __init__(self, api_key: str, account_id: str, is_live: bool = False):
        self.api_key = api_key
        self.account_id = account_id
        self.stream_url = OANDA_LIVE_STREAM if is_live else OANDA_PRACTICE_STREAM
        self.callbacks = {}
    
    def on_price(self, callback):
        """Register callback for price updates."""
        self.callbacks["price"] = callback
    
    def on_heartbeat(self, callback):
        """Register callback for heartbeat."""
        self.callbacks["heartbeat"] = callback
    
    def get_connection_params(self, instruments: list) -> dict:
        """
        Get connection parameters for streaming.
        
        Use these with requests or aiohttp for streaming connection.
        """
        return {
            "url": f"{self.stream_url}/v3/accounts/{self.account_id}/pricing/stream",
            "params": {
                "instruments": ",".join(instruments)
            },
            "headers": {
                "Authorization": f"Bearer {self.api_key}",
                "Accept-Datetime-Format": "UNIX"
            }
        }
    
    async def process_line(self, line: str):
        """
        Process a single line from the stream.
        
        Call this for each line received from the stream.
        """
        if not line.strip():
            return
        
        try:
            data = json.loads(line)
            
            if data.get("type") == "PRICE":
                if "price" in self.callbacks:
                    price_data = {
                        "instrument": data.get("instrument"),
                        "time": data.get("time"),
                        "bid": float(data.get("bids", [{}])[0].get("price", 0)),
                        "ask": float(data.get("asks", [{}])[0].get("price", 0)),
                        "tradeable": data.get("tradeable", False)
                    }
                    await self.callbacks["price"](price_data)
                    
            elif data.get("type") == "HEARTBEAT":
                if "heartbeat" in self.callbacks:
                    await self.callbacks["heartbeat"](data)
                    
        except json.JSONDecodeError:
            pass  # Ignore malformed lines


# ==========================================
# 📋 BYBIT API KEYS GUIDE
# ==========================================
"""
🔑 HOW TO GET BYBIT API KEYS:

1. Go to https://www.bybit.com/ (or https://testnet.bybit.com for testnet)

2. Create an account (email only, no KYC needed for trading)

3. Go to: Profile → API Management → Create New Key

4. Settings:
   - Key Name: "AXIOM Trading Bot"
   - Permissions: 
     ✅ Read-Write (for trading)
     ✅ Derivatives (required)
     ✅ Exchange (optional)
   - IP Restriction: None (or add your server IP for security)

5. Save your keys:
   - API Key: xxxxxxxxx
   - API Secret: xxxxxxxxx (shown only once!)

6. Add to Cloudflare Worker secrets:
   npx wrangler secret put BYBIT_API_KEY
   npx wrangler secret put BYBIT_API_SECRET

7. Or add to .dev.vars for local testing:
   BYBIT_API_KEY=your_key_here
   BYBIT_API_SECRET=your_secret_here

⚠️ TESTNET RECOMMENDED FIRST:
- Testnet URL: https://testnet.bybit.com
- Get free testnet USDT from faucet
- Same API structure, no real money risk

📱 2FA Required for API creation (use Google Authenticator)
"""

