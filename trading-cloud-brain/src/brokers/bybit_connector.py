"""
🔗 Bybit Perpetuals Connector for AXIOM 100% Weekly ROI
Supports: USDT Perpetuals, WebSocket real-time data

FEATURES:
- REST API for orders and positions
- WebSocket for real-time 1M/5M/15M candles
- High leverage support (up to 100x)
- Position management and PnL tracking

REQUIREMENTS:
pip install pybit
"""

import hmac
import hashlib
import time
import json
from typing import Optional, Dict, List


class BybitConnector:
    """
    Bybit USDT Perpetuals Connector.
    Designed for high-frequency scalping with 100x leverage.
    """
    
    # API Endpoints
    BASE_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"
    
    # WebSocket Endpoints
    WS_PUBLIC = "wss://stream.bybit.com/v5/public/linear"
    WS_PRIVATE = "wss://stream.bybit.com/v5/private"
    WS_TESTNET = "wss://stream-testnet.bybit.com/v5/public/linear"
    
    def __init__(self, api_key: str = "", api_secret: str = "", testnet: bool = False):
        """
        Initialize Bybit connector.
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet for paper trading
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.base_url = self.TESTNET_URL if testnet else self.BASE_URL
        
    def _generate_signature(self, params: dict) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        timestamp = str(int(time.time() * 1000))
        param_str = timestamp + self.api_key + "5000"  # 5s recv_window
        
        if params:
            param_str += "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _get_headers(self, params: dict = None) -> dict:
        """Get authenticated headers."""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(params or {})
        
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": "5000",
            "Content-Type": "application/json"
        }
    
    # ==========================================
    # 📊 MARKET DATA (Public - No Auth Required)
    # ==========================================
    
    async def get_klines(self, 
                         symbol: str, 
                         interval: str = "1", 
                         limit: int = 200) -> List[dict]:
        """
        Get candlestick/kline data.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            interval: Timeframe - "1" (1m), "5" (5m), "15" (15m), "60" (1h)
            limit: Number of candles (max 200)
        
        Returns:
            List of OHLCV candles
        """
        from js import fetch
        
        url = f"{self.base_url}/v5/market/kline"
        params = f"?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
        
        response = await fetch(url + params)
        data = await response.json()
        
        if data.get("retCode") != 0:
            raise Exception(f"Bybit Error: {data.get('retMsg')}")
        
        # Convert to standard format
        candles = []
        for item in data.get("result", {}).get("list", []):
            candles.append({
                "time": int(item[0]),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5])
            })
        
        return list(reversed(candles))  # Oldest first
    
    async def get_ticker(self, symbol: str) -> dict:
        """Get latest ticker for a symbol."""
        from js import fetch
        
        url = f"{self.base_url}/v5/market/tickers?category=linear&symbol={symbol}"
        
        response = await fetch(url)
        data = await response.json()
        
        if data.get("retCode") != 0:
            raise Exception(f"Bybit Error: {data.get('retMsg')}")
        
        ticker = data.get("result", {}).get("list", [{}])[0]
        
        return {
            "symbol": ticker.get("symbol"),
            "lastPrice": float(ticker.get("lastPrice", 0)),
            "bid": float(ticker.get("bid1Price", 0)),
            "ask": float(ticker.get("ask1Price", 0)),
            "volume24h": float(ticker.get("volume24h", 0)),
            "change24h": float(ticker.get("price24hPcnt", 0)) * 100
        }
    
    # ==========================================
    # 💰 TRADING (Authenticated)
    # ==========================================
    
    async def set_leverage(self, symbol: str, leverage: int) -> dict:
        """
        Set leverage for a symbol.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            leverage: Leverage value (1-100)
        """
        from js import fetch
        
        url = f"{self.base_url}/v5/position/set-leverage"
        
        body = {
            "category": "linear",
            "symbol": symbol,
            "buyLeverage": str(leverage),
            "sellLeverage": str(leverage)
        }
        
        response = await fetch(
            url,
            method="POST",
            headers=self._get_headers(body),
            body=json.dumps(body)
        )
        
        data = await response.json()
        return data
    
    async def place_order(self,
                          symbol: str,
                          side: str,
                          qty: float,
                          order_type: str = "Market",
                          price: float = None,
                          stop_loss: float = None,
                          take_profit: float = None,
                          reduce_only: bool = False) -> dict:
        """
        Place a new order.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            side: "Buy" or "Sell"
            qty: Order quantity
            order_type: "Market" or "Limit"
            price: Limit price (required for Limit orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            reduce_only: Close position only
        
        Returns:
            Order response with orderId
        """
        from js import fetch
        
        url = f"{self.base_url}/v5/order/create"
        
        body = {
            "category": "linear",
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": str(qty),
            "timeInForce": "GTC"
        }
        
        if price and order_type == "Limit":
            body["price"] = str(price)
        
        if stop_loss:
            body["stopLoss"] = str(stop_loss)
        
        if take_profit:
            body["takeProfit"] = str(take_profit)
        
        if reduce_only:
            body["reduceOnly"] = True
        
        response = await fetch(
            url,
            method="POST",
            headers=self._get_headers(body),
            body=json.dumps(body)
        )
        
        data = await response.json()
        
        if data.get("retCode") != 0:
            raise Exception(f"Order Error: {data.get('retMsg')}")
        
        return data.get("result", {})
    
    async def get_positions(self, symbol: str = None) -> List[dict]:
        """Get all open positions."""
        from js import fetch
        
        url = f"{self.base_url}/v5/position/list?category=linear"
        if symbol:
            url += f"&symbol={symbol}"
        
        response = await fetch(url, headers=self._get_headers())
        data = await response.json()
        
        positions = []
        for pos in data.get("result", {}).get("list", []):
            if float(pos.get("size", 0)) > 0:
                positions.append({
                    "symbol": pos.get("symbol"),
                    "side": pos.get("side"),
                    "size": float(pos.get("size", 0)),
                    "entryPrice": float(pos.get("avgPrice", 0)),
                    "leverage": int(pos.get("leverage", 1)),
                    "unrealizedPnl": float(pos.get("unrealisedPnl", 0)),
                    "liquidationPrice": float(pos.get("liqPrice", 0))
                })
        
        return positions
    
    async def close_position(self, symbol: str, side: str) -> dict:
        """
        Close a position.
        
        Args:
            symbol: Trading pair
            side: Original side ("Buy" to close long, "Sell" to close short)
        """
        # Get current position size
        positions = await self.get_positions(symbol)
        
        for pos in positions:
            if pos["symbol"] == symbol:
                # Place opposite order to close
                close_side = "Sell" if side == "Buy" else "Buy"
                return await self.place_order(
                    symbol=symbol,
                    side=close_side,
                    qty=pos["size"],
                    order_type="Market",
                    reduce_only=True
                )
        
        return {"error": "No position found"}
    
    async def get_wallet_balance(self) -> dict:
        """Get USDT wallet balance."""
        from js import fetch
        
        url = f"{self.base_url}/v5/account/wallet-balance?accountType=UNIFIED"
        
        response = await fetch(url, headers=self._get_headers())
        data = await response.json()
        
        coins = data.get("result", {}).get("list", [{}])[0].get("coin", [])
        
        for coin in coins:
            if coin.get("coin") == "USDT":
                return {
                    "coin": "USDT",
                    "balance": float(coin.get("walletBalance", 0)),
                    "available": float(coin.get("availableToWithdraw", 0)),
                    "unrealizedPnl": float(coin.get("unrealisedPnl", 0))
                }
        
        return {"coin": "USDT", "balance": 0, "available": 0}
    
    # ==========================================
    # 🚀 HIGH-LEVEL TRADING FUNCTIONS
    # ==========================================
    
    async def scalp_trade(self,
                          symbol: str,
                          side: str,
                          leverage: int,
                          position_pct: float,
                          stop_loss: float,
                          take_profit: float) -> dict:
        """
        Execute a scalp trade with full risk management.
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            side: "Buy" (long) or "Sell" (short)
            leverage: Leverage to use (1-100)
            position_pct: Percentage of account to use (0.01-1.0)
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Trade execution result
        """
        # 1. Get account balance
        wallet = await self.get_wallet_balance()
        available = wallet.get("available", 0)
        
        if available <= 0:
            return {"error": "Insufficient balance"}
        
        # 2. Set leverage
        await self.set_leverage(symbol, leverage)
        
        # 3. Calculate position size
        ticker = await self.get_ticker(symbol)
        price = ticker.get("lastPrice", 0)
        
        margin = available * position_pct
        notional = margin * leverage
        qty = notional / price
        
        # Round qty to appropriate decimals (BTC = 3, others = 0)
        if "BTC" in symbol:
            qty = round(qty, 3)
        else:
            qty = round(qty, 2)
        
        # 4. Place order with SL/TP
        order = await self.place_order(
            symbol=symbol,
            side=side,
            qty=qty,
            order_type="Market",
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        return {
            "success": True,
            "order": order,
            "details": {
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "leverage": leverage,
                "margin": margin,
                "notional": notional,
                "stop_loss": stop_loss,
                "take_profit": take_profit
            }
        }


# ==========================================
# 📡 WEBSOCKET HANDLER FOR REAL-TIME DATA
# ==========================================

class BybitWebSocket:
    """
    WebSocket handler for real-time candle data.
    Used for 1M/5M/15M scalping signals.
    """
    
    WS_URL = "wss://stream.bybit.com/v5/public/linear"
    
    def __init__(self, symbols: List[str], intervals: List[str] = ["1", "5", "15"]):
        """
        Initialize WebSocket for multiple symbols and intervals.
        
        Args:
            symbols: List of trading pairs (e.g., ["BTCUSDT", "ETHUSDT"])
            intervals: Timeframes to subscribe (e.g., ["1", "5", "15"])
        """
        self.symbols = symbols
        self.intervals = intervals
        self.callbacks = {}
    
    def on_candle(self, callback):
        """Register callback for new candle data."""
        self.callbacks["candle"] = callback
    
    def get_subscription_message(self) -> dict:
        """Generate WebSocket subscription message."""
        topics = []
        
        for symbol in self.symbols:
            for interval in self.intervals:
                topics.append(f"kline.{interval}.{symbol}")
        
        return {
            "op": "subscribe",
            "args": topics
        }
    
    async def handle_message(self, data: dict):
        """Process incoming WebSocket message."""
        topic = data.get("topic", "")
        
        if "kline" in topic and "candle" in self.callbacks:
            kline_data = data.get("data", [{}])[0]
            
            candle = {
                "symbol": topic.split(".")[-1],
                "interval": topic.split(".")[1],
                "time": int(kline_data.get("start", 0)),
                "open": float(kline_data.get("open", 0)),
                "high": float(kline_data.get("high", 0)),
                "low": float(kline_data.get("low", 0)),
                "close": float(kline_data.get("close", 0)),
                "volume": float(kline_data.get("volume", 0)),
                "confirm": kline_data.get("confirm", False)  # True when candle closed
            }
            
            await self.callbacks["candle"](candle)
