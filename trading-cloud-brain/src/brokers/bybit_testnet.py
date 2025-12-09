"""
🔗 Bybit Testnet Paper Trading Connector
موصل Bybit Testnet للتداول الورقي - العملات المشفرة وعملات الميم

AlphaAxiom Learning Loop v2.0
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Features:
- Testnet (Paper Trading) for high-volume crypto
- Meme coins and altcoins support
- Up to 100x leverage on perpetuals
- 24/7 trading (crypto never sleeps!)
- Integration with Mini-Agent Swarm

Testnet: https://testnet.bybit.com/
API Docs: https://bybit-exchange.github.io/docs/
"""

import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 DATA STRUCTURES | هياكل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BybitOrderSide(Enum):
    BUY = "Buy"
    SELL = "Sell"


class BybitOrderType(Enum):
    MARKET = "Market"
    LIMIT = "Limit"


class BybitCategory(Enum):
    SPOT = "spot"
    LINEAR = "linear"  # USDT Perpetuals
    INVERSE = "inverse"


@dataclass
class BybitOrder:
    """Order structure for Bybit API"""
    symbol: str
    qty: float
    side: BybitOrderSide
    category: BybitCategory = BybitCategory.LINEAR
    order_type: BybitOrderType = BybitOrderType.MARKET
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reduce_only: bool = False
    
    # Response fields
    order_id: Optional[str] = None
    order_link_id: Optional[str] = None
    status: Optional[str] = None
    filled_qty: Optional[float] = None
    avg_price: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "order_id": self.order_id,
            "status": self.status,
        }


@dataclass
class BybitPosition:
    """Position structure"""
    symbol: str
    side: str  # "Buy" or "Sell"
    size: float
    entry_price: float
    mark_price: float
    leverage: int
    unrealized_pnl: float
    liq_price: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "size": self.size,
            "entry_price": self.entry_price,
            "mark_price": self.mark_price,
            "leverage": self.leverage,
            "unrealized_pnl": self.unrealized_pnl,
            "liq_price": self.liq_price,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔗 BYBIT TESTNET CONNECTOR | موصل Bybit Testnet
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BybitTestnetConnector:
    """
    Bybit Testnet Connector for crypto paper trading
    موصل Bybit Testnet للتداول الورقي للعملات المشفرة
    
    Perfect for testing crypto and meme coin strategies.
    24/7 operation with high leverage capability.
    """
    
    # API Endpoints
    MAINNET_URL = "https://api.bybit.com"
    TESTNET_URL = "https://api-testnet.bybit.com"
    
    # Popular trading pairs for meme coins
    MEME_COINS = [
        "DOGEUSDT",
        "SHIBUSDT",
        "PEPEUSDT",
        "FLOKIUSDT",
        "BONKUSDT",
        "WIFUSDT",
    ]
    
    # High volume pairs
    MAJOR_PAIRS = [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "XRPUSDT",
        "ADAUSDT",
        "AVAXUSDT",
    ]
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        testnet: bool = True,
        env=None
    ):
        """
        Initialize Bybit Testnet connector
        
        Args:
            api_key: Bybit Testnet API Key
            api_secret: Bybit Testnet API Secret
            testnet: Always True for paper trading
            env: Cloudflare Workers environment
        """
        self.env = env
        self.testnet = testnet
        
        # Get credentials from env if not provided
        if env:
            self.api_key = api_key or getattr(env, 'BYBIT_TESTNET_KEY', '')
            self.api_secret = api_secret or getattr(env, 'BYBIT_TESTNET_SECRET', '')
        else:
            self.api_key = api_key
            self.api_secret = api_secret
        
        self.base_url = self.TESTNET_URL if testnet else self.MAINNET_URL
        
        # Order tracking for learning loop
        self._pending_orders: Dict[str, BybitOrder] = {}
        
        self._log(f"🔗 Bybit {'Testnet' if testnet else 'Mainnet'} initialized")
    
    def _generate_signature(self, timestamp: str, params: str) -> str:
        """Generate HMAC SHA256 signature"""
        recv_window = "5000"
        param_str = f"{timestamp}{self.api_key}{recv_window}{params}"
        
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_auth_headers(self, params: str = "") -> Dict[str, str]:
        """Get authenticated headers"""
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, params)
        
        return {
            "X-BAPI-API-KEY": self.api_key,
            "X-BAPI-SIGN": signature,
            "X-BAPI-TIMESTAMP": timestamp,
            "X-BAPI-RECV-WINDOW": "5000",
            "Content-Type": "application/json",
        }
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💰 ACCOUNT MANAGEMENT | إدارة الحساب
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_wallet_balance(self, coin: str = "USDT") -> Dict[str, Any]:
        """
        Get wallet balance
        الحصول على رصيد المحفظة
        """
        try:
            from js import fetch, Headers
            
            params = f"accountType=UNIFIED&coin={coin}"
            url = f"{self.base_url}/v5/account/wallet-balance?{params}"
            
            headers = Headers.new()
            for key, value in self._get_auth_headers(params).items():
                headers.set(key, value)
            
            response = await fetch(url, method="GET", headers=headers)
            data = await response.json()
            
            if data.get("retCode") != 0:
                raise Exception(f"Bybit Error: {data.get('retMsg')}")
            
            result = data.get("result", {})
            account_list = result.get("list", [{}])[0]
            coins = account_list.get("coin", [])
            
            # Find specified coin
            balance_info = next(
                (c for c in coins if c.get("coin") == coin),
                {}
            )
            
            return {
                "coin": coin,
                "equity": float(balance_info.get("equity", 0)),
                "available": float(balance_info.get("availableToWithdraw", 0)),
                "wallet_balance": float(balance_info.get("walletBalance", 0)),
                "unrealized_pnl": float(balance_info.get("unrealisedPnl", 0)),
            }
            
        except Exception as e:
            self._log(f"❌ Error getting balance: {e}")
            return {"error": str(e)}
    
    async def get_positions(
        self,
        category: str = "linear",
        symbol: str = None
    ) -> List[BybitPosition]:
        """
        Get open positions
        الحصول على المراكز المفتوحة
        """
        try:
            from js import fetch, Headers
            
            params = f"category={category}"
            if symbol:
                params += f"&symbol={symbol}"
            
            url = f"{self.base_url}/v5/position/list?{params}"
            
            headers = Headers.new()
            for key, value in self._get_auth_headers(params).items():
                headers.set(key, value)
            
            response = await fetch(url, method="GET", headers=headers)
            data = await response.json()
            
            if data.get("retCode") != 0:
                raise Exception(f"Bybit Error: {data.get('retMsg')}")
            
            positions = []
            for pos in data.get("result", {}).get("list", []):
                if float(pos.get("size", 0)) > 0:
                    positions.append(BybitPosition(
                        symbol=pos.get("symbol"),
                        side=pos.get("side"),
                        size=float(pos.get("size", 0)),
                        entry_price=float(pos.get("avgPrice", 0)),
                        mark_price=float(pos.get("markPrice", 0)),
                        leverage=int(pos.get("leverage", 1)),
                        unrealized_pnl=float(pos.get("unrealisedPnl", 0)),
                        liq_price=float(pos.get("liqPrice", 0)),
                    ))
            
            return positions
            
        except Exception as e:
            self._log(f"❌ Error getting positions: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 MARKET DATA | بيانات السوق
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get latest ticker for a symbol"""
        try:
            from js import fetch
            
            url = f"{self.base_url}/v5/market/tickers?category=linear&symbol={symbol}"
            response = await fetch(url)
            data = await response.json()
            
            if data.get("retCode") != 0:
                raise Exception(f"Bybit Error: {data.get('retMsg')}")
            
            ticker = data.get("result", {}).get("list", [{}])[0]
            
            return {
                "symbol": ticker.get("symbol"),
                "last_price": float(ticker.get("lastPrice", 0)),
                "bid": float(ticker.get("bid1Price", 0)),
                "ask": float(ticker.get("ask1Price", 0)),
                "volume_24h": float(ticker.get("volume24h", 0)),
                "change_24h": float(ticker.get("price24hPcnt", 0)) * 100,
            }
            
        except Exception as e:
            self._log(f"❌ Error getting ticker: {e}")
            return {"error": str(e)}
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "5",
        limit: int = 100
    ) -> List[Dict]:
        """
        Get candlestick data
        الحصول على بيانات الشموع
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "PEPEUSDT")
            interval: "1", "5", "15", "60", "240", "D"
            limit: Number of candles (max 200)
        """
        try:
            from js import fetch
            
            url = (f"{self.base_url}/v5/market/kline?"
                   f"category=linear&symbol={symbol}"
                   f"&interval={interval}&limit={limit}")
            
            response = await fetch(url)
            data = await response.json()
            
            if data.get("retCode") != 0:
                raise Exception(f"Bybit Error: {data.get('retMsg')}")
            
            candles = []
            for item in data.get("result", {}).get("list", []):
                candles.append({
                    "time": int(item[0]),
                    "open": float(item[1]),
                    "high": float(item[2]),
                    "low": float(item[3]),
                    "close": float(item[4]),
                    "volume": float(item[5]),
                })
            
            return list(reversed(candles))  # Oldest first
            
        except Exception as e:
            self._log(f"❌ Error getting klines: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📝 ORDER MANAGEMENT | إدارة الأوامر
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def set_leverage(
        self,
        symbol: str,
        leverage: int
    ) -> Dict[str, Any]:
        """
        Set leverage for a symbol
        تعيين الرافعة المالية للرمز
        """
        try:
            from js import fetch, Headers
            
            body = {
                "category": "linear",
                "symbol": symbol,
                "buyLeverage": str(leverage),
                "sellLeverage": str(leverage),
            }
            body_str = json.dumps(body)
            
            headers = Headers.new()
            for key, value in self._get_auth_headers(body_str).items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.base_url}/v5/position/set-leverage",
                method="POST",
                headers=headers,
                body=body_str
            )
            
            data = await response.json()
            self._log(f"✅ Leverage set to {leverage}x for {symbol}")
            
            return data
            
        except Exception as e:
            self._log(f"❌ Error setting leverage: {e}")
            return {"error": str(e)}
    
    async def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "Market",
        price: float = None,
        stop_loss: float = None,
        take_profit: float = None,
        reduce_only: bool = False,
        agent_name: str = "unknown"
    ) -> BybitOrder:
        """
        Submit a new order
        تقديم أمر جديد
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "PEPEUSDT")
            qty: Order quantity
            side: "Buy" or "Sell"
            order_type: "Market" or "Limit"
            price: Limit price (for Limit orders)
            stop_loss: Stop loss price
            take_profit: Take profit price
            reduce_only: Close position only
            agent_name: Mini-agent for tracking
        """
        try:
            from js import fetch, Headers
            
            # Generate order link ID for tracking
            order_link_id = f"axiom_{agent_name}_{int(time.time()*1000)}"
            
            # Create order object
            order = BybitOrder(
                symbol=symbol.upper(),
                qty=qty,
                side=BybitOrderSide[side.upper()],
                order_type=BybitOrderType[order_type.upper()],
                price=price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reduce_only=reduce_only,
                order_link_id=order_link_id,
            )
            
            # Build request body
            body = {
                "category": "linear",
                "symbol": order.symbol,
                "side": order.side.value,
                "orderType": order.order_type.value,
                "qty": str(qty),
                "orderLinkId": order_link_id,
            }
            
            if price:
                body["price"] = str(price)
            if stop_loss:
                body["stopLoss"] = str(stop_loss)
            if take_profit:
                body["takeProfit"] = str(take_profit)
            if reduce_only:
                body["reduceOnly"] = True
            
            body_str = json.dumps(body)
            
            headers = Headers.new()
            for key, value in self._get_auth_headers(body_str).items():
                headers.set(key, value)
            
            self._log(f"📤 Submitting order: {body}")
            
            response = await fetch(
                f"{self.base_url}/v5/order/create",
                method="POST",
                headers=headers,
                body=body_str
            )
            
            data = await response.json()
            
            if data.get("retCode") != 0:
                raise Exception(f"Order failed: {data.get('retMsg')}")
            
            result = data.get("result", {})
            order.order_id = result.get("orderId")
            order.status = "submitted"
            
            # Store for tracking
            self._pending_orders[order_link_id] = order
            
            self._log(f"✅ Order submitted: {order.order_id}")
            
            return order
            
        except Exception as e:
            self._log(f"❌ Error submitting order: {e}")
            raise
    
    async def cancel_order(
        self,
        symbol: str,
        order_id: str = None,
        order_link_id: str = None
    ) -> Dict[str, Any]:
        """Cancel an open order"""
        try:
            from js import fetch, Headers
            
            body = {
                "category": "linear",
                "symbol": symbol,
            }
            
            if order_id:
                body["orderId"] = order_id
            elif order_link_id:
                body["orderLinkId"] = order_link_id
            
            body_str = json.dumps(body)
            
            headers = Headers.new()
            for key, value in self._get_auth_headers(body_str).items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.base_url}/v5/order/cancel",
                method="POST",
                headers=headers,
                body=body_str
            )
            
            data = await response.json()
            self._log(f"✅ Order cancelled")
            
            return data
            
        except Exception as e:
            self._log(f"❌ Error cancelling order: {e}")
            return {"error": str(e)}
    
    async def close_position(
        self,
        symbol: str,
        side: str = None
    ) -> Dict[str, Any]:
        """
        Close position for a symbol
        إغلاق مركز لرمز معين
        """
        try:
            # Get current position to determine size and side
            positions = await self.get_positions(symbol=symbol)
            
            if not positions:
                return {"message": "No position to close"}
            
            pos = positions[0]
            
            # Submit opposite order to close
            close_side = "Sell" if pos.side == "Buy" else "Buy"
            
            return await self.submit_order(
                symbol=symbol,
                qty=pos.size,
                side=close_side,
                reduce_only=True,
                agent_name="close_position"
            )
            
        except Exception as e:
            self._log(f"❌ Error closing position: {e}")
            return {"error": str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🎰 MEME COIN UTILITIES | أدوات عملات الميم
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_meme_coin_movers(self) -> List[Dict[str, Any]]:
        """
        Get top moving meme coins
        الحصول على أفضل عملات الميم المتحركة
        """
        movers = []
        
        for symbol in self.MEME_COINS:
            try:
                ticker = await self.get_ticker(symbol)
                if "error" not in ticker:
                    movers.append({
                        "symbol": symbol,
                        "price": ticker.get("last_price"),
                        "change_24h": ticker.get("change_24h"),
                        "volume_24h": ticker.get("volume_24h"),
                    })
            except Exception:
                pass
        
        # Sort by 24h change (absolute value for volatility)
        movers.sort(key=lambda x: abs(x.get("change_24h", 0)), reverse=True)
        
        return movers
    
    def _log(self, message: str) -> None:
        """Print log with prefix"""
        mode = "Testnet" if self.testnet else "Mainnet"
        print(f"[Bybit{mode}] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connector status"""
        return {
            "name": "BybitTestnetConnector",
            "version": "1.0.0",
            "mode": "testnet" if self.testnet else "mainnet",
            "has_credentials": bool(self.api_key and self.api_secret),
            "pending_orders": len(self._pending_orders),
            "meme_coins": self.MEME_COINS,
            "major_pairs": self.MAJOR_PAIRS,
        }
