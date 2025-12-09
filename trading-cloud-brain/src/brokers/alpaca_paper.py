"""
📈 Alpaca Paper Trading Connector
موصل Alpaca للتداول الورقي - الأسهم وصناديق ETF

AlphaAxiom Learning Loop v2.0
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Features:
- Paper Trading API integration
- Zero-cost execution on stocks/ETFs
- Order management with slippage tracking
- Position monitoring for Learning Loop feedback
- Integration with Mini-Agent Swarm

API Documentation: https://docs.alpaca.markets/
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 DATA STRUCTURES | هياكل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class TimeInForce(Enum):
    DAY = "day"      # Day order
    GTC = "gtc"      # Good 'til cancelled
    IOC = "ioc"      # Immediate or cancel
    FOK = "fok"      # Fill or kill


class OrderStatus(Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    PENDING_NEW = "pending_new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class AlpacaOrder:
    """Order structure for Alpaca API"""
    symbol: str
    qty: float
    side: OrderSide
    order_type: OrderType = OrderType.MARKET
    time_in_force: TimeInForce = TimeInForce.DAY
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    client_order_id: Optional[str] = None
    
    # Response fields (filled after submission)
    order_id: Optional[str] = None
    status: Optional[OrderStatus] = None
    filled_qty: Optional[float] = None
    filled_avg_price: Optional[float] = None
    submitted_at: Optional[str] = None
    filled_at: Optional[str] = None
    
    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to Alpaca API request format"""
        data = {
            "symbol": self.symbol,
            "qty": str(self.qty),
            "side": self.side.value,
            "type": self.order_type.value,
            "time_in_force": self.time_in_force.value,
        }
        
        if self.limit_price:
            data["limit_price"] = str(self.limit_price)
        if self.stop_price:
            data["stop_price"] = str(self.stop_price)
        if self.client_order_id:
            data["client_order_id"] = self.client_order_id
            
        return data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "order_id": self.order_id,
            "status": self.status.value if self.status else None,
            "filled_qty": self.filled_qty,
            "filled_avg_price": self.filled_avg_price,
            "client_order_id": self.client_order_id,
        }


@dataclass
class AlpacaPosition:
    """Position structure"""
    symbol: str
    qty: float
    side: str  # "long" or "short"
    entry_price: float
    current_price: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    market_value: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_percent": self.unrealized_pnl_percent,
            "market_value": self.market_value,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📈 ALPACA PAPER CONNECTOR | موصل ألباكا للتداول الورقي
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AlpacaPaperConnector:
    """
    Alpaca Paper Trading Connector for stocks and ETFs
    موصل ألباكا للتداول الورقي للأسهم وصناديق ETF
    
    Zero-cost paper trading with real market data.
    Perfect for testing Mini-Agent Swarm strategies.
    """
    
    # API Endpoints
    PAPER_BASE_URL = "https://paper-api.alpaca.markets"
    DATA_URL = "https://data.alpaca.markets"
    
    # Trading Hours (US Eastern)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    MARKET_CLOSE_HOUR = 16
    MARKET_CLOSE_MINUTE = 0
    
    def __init__(
        self,
        api_key: str = "",
        api_secret: str = "",
        env=None
    ):
        """
        Initialize Alpaca Paper Trading connector
        
        Args:
            api_key: Alpaca API Key (from env.ALPACA_API_KEY)
            api_secret: Alpaca API Secret (from env.ALPACA_API_SECRET)
            env: Cloudflare Workers environment object
        """
        self.env = env
        
        # Get credentials from env if not provided
        if env:
            self.api_key = api_key or getattr(env, 'ALPACA_API_KEY', '')
            self.api_secret = api_secret or getattr(env, 'ALPACA_API_SECRET', '')
        else:
            self.api_key = api_key
            self.api_secret = api_secret
        
        # Track orders for learning loop
        self._pending_orders: Dict[str, AlpacaOrder] = {}
        
        self._log("📈 Alpaca Paper Connector initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated headers for API requests"""
        return {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret,
            "Content-Type": "application/json",
        }
    
    def _generate_client_order_id(self, symbol: str, agent_name: str) -> str:
        """Generate unique client order ID for tracking"""
        timestamp = int(time.time() * 1000)
        hash_input = f"{symbol}_{agent_name}_{timestamp}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"axiom_{agent_name}_{short_hash}"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 💰 ACCOUNT MANAGEMENT | إدارة الحساب
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_account(self) -> Dict[str, Any]:
        """
        Get paper trading account information
        الحصول على معلومات حساب التداول الورقي
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/account",
                method="GET",
                headers=headers
            )
            
            data = await response.json()
            
            return {
                "id": data.get("id"),
                "equity": float(data.get("equity", 0)),
                "cash": float(data.get("cash", 0)),
                "buying_power": float(data.get("buying_power", 0)),
                "portfolio_value": float(data.get("portfolio_value", 0)),
                "day_trade_count": int(data.get("daytrade_count", 0)),
                "pattern_day_trader": data.get("pattern_day_trader", False),
                "trading_blocked": data.get("trading_blocked", False),
                "account_blocked": data.get("account_blocked", False),
                "currency": data.get("currency", "USD"),
                "status": data.get("status"),
            }
            
        except Exception as e:
            self._log(f"❌ Error getting account: {e}")
            return {"error": str(e)}
    
    async def get_positions(self) -> List[AlpacaPosition]:
        """
        Get all open positions
        الحصول على جميع المراكز المفتوحة
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/positions",
                method="GET",
                headers=headers
            )
            
            data = await response.json()
            
            positions = []
            for pos in data:
                positions.append(AlpacaPosition(
                    symbol=pos.get("symbol"),
                    qty=float(pos.get("qty", 0)),
                    side=pos.get("side"),
                    entry_price=float(pos.get("avg_entry_price", 0)),
                    current_price=float(pos.get("current_price", 0)),
                    unrealized_pnl=float(pos.get("unrealized_pl", 0)),
                    unrealized_pnl_percent=float(pos.get("unrealized_plpc", 0)) * 100,
                    market_value=float(pos.get("market_value", 0)),
                ))
            
            return positions
            
        except Exception as e:
            self._log(f"❌ Error getting positions: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 MARKET DATA | بيانات السوق
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get latest quote for a symbol
        الحصول على آخر سعر لرمز
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.DATA_URL}/v2/stocks/{symbol}/quotes/latest",
                method="GET",
                headers=headers
            )
            
            data = await response.json()
            quote = data.get("quote", {})
            
            return {
                "symbol": symbol,
                "bid": float(quote.get("bp", 0)),
                "ask": float(quote.get("ap", 0)),
                "bid_size": int(quote.get("bs", 0)),
                "ask_size": int(quote.get("as", 0)),
                "timestamp": quote.get("t"),
            }
            
        except Exception as e:
            self._log(f"❌ Error getting quote for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    async def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Min",
        limit: int = 100
    ) -> List[Dict]:
        """
        Get historical bars/candles
        الحصول على الشموع التاريخية
        
        Args:
            symbol: Stock symbol (e.g., "AAPL")
            timeframe: "1Min", "5Min", "15Min", "1Hour", "1Day"
            limit: Number of bars (max 10000)
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            # Calculate start time based on limit
            end = datetime.utcnow()
            start = end - timedelta(days=7)  # Last 7 days
            
            url = (f"{self.DATA_URL}/v2/stocks/{symbol}/bars"
                   f"?timeframe={timeframe}&limit={limit}"
                   f"&start={start.isoformat()}Z")
            
            response = await fetch(url, method="GET", headers=headers)
            data = await response.json()
            
            bars = []
            for bar in data.get("bars", []):
                bars.append({
                    "time": bar.get("t"),
                    "open": float(bar.get("o", 0)),
                    "high": float(bar.get("h", 0)),
                    "low": float(bar.get("l", 0)),
                    "close": float(bar.get("c", 0)),
                    "volume": int(bar.get("v", 0)),
                })
            
            return bars
            
        except Exception as e:
            self._log(f"❌ Error getting bars for {symbol}: {e}")
            return []
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📝 ORDER MANAGEMENT | إدارة الأوامر
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def submit_order(
        self,
        symbol: str,
        qty: float,
        side: str,
        order_type: str = "market",
        limit_price: float = None,
        stop_price: float = None,
        time_in_force: str = "day",
        agent_name: str = "unknown"
    ) -> AlpacaOrder:
        """
        Submit a new order
        تقديم أمر جديد
        
        Args:
            symbol: Stock symbol (e.g., "AAPL", "SPY")
            qty: Number of shares
            side: "buy" or "sell"
            order_type: "market", "limit", "stop", "stop_limit"
            limit_price: Limit price (for limit/stop_limit orders)
            stop_price: Stop price (for stop/stop_limit orders)
            time_in_force: "day", "gtc", "ioc", "fok"
            agent_name: Mini-agent that generated signal (for tracking)
        """
        try:
            from js import fetch, Headers
            
            # Create order object
            order = AlpacaOrder(
                symbol=symbol.upper(),
                qty=qty,
                side=OrderSide(side.lower()),
                order_type=OrderType(order_type.lower()),
                time_in_force=TimeInForce(time_in_force.lower()),
                limit_price=limit_price,
                stop_price=stop_price,
                client_order_id=self._generate_client_order_id(symbol, agent_name)
            )
            
            # Prepare request
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            body = json.dumps(order.to_api_dict())
            
            self._log(f"📤 Submitting order: {order.to_api_dict()}")
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/orders",
                method="POST",
                headers=headers,
                body=body
            )
            
            data = await response.json()
            
            # Update order with response
            order.order_id = data.get("id")
            order.status = OrderStatus(data.get("status", "new"))
            order.filled_qty = float(data.get("filled_qty", 0))
            order.filled_avg_price = float(data.get("filled_avg_price") or 0)
            order.submitted_at = data.get("submitted_at")
            order.filled_at = data.get("filled_at")
            
            # Store for tracking
            self._pending_orders[order.client_order_id] = order
            
            self._log(f"✅ Order submitted: {order.order_id} - {order.status.value}")
            
            return order
            
        except Exception as e:
            self._log(f"❌ Error submitting order: {e}")
            raise
    
    async def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status by ID
        الحصول على حالة الأمر بالمعرف
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/orders/{order_id}",
                method="GET",
                headers=headers
            )
            
            return await response.json()
            
        except Exception as e:
            self._log(f"❌ Error getting order {order_id}: {e}")
            return {"error": str(e)}
    
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an open order
        إلغاء أمر مفتوح
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/orders/{order_id}",
                method="DELETE",
                headers=headers
            )
            
            if response.status == 204:
                self._log(f"✅ Order {order_id} cancelled")
                return True
            
            return False
            
        except Exception as e:
            self._log(f"❌ Error cancelling order: {e}")
            return False
    
    async def close_position(self, symbol: str) -> Dict[str, Any]:
        """
        Close position for a symbol
        إغلاق مركز لرمز معين
        """
        try:
            from js import fetch, Headers
            
            headers = Headers.new()
            for key, value in self._get_headers().items():
                headers.set(key, value)
            
            response = await fetch(
                f"{self.PAPER_BASE_URL}/v2/positions/{symbol}",
                method="DELETE",
                headers=headers
            )
            
            data = await response.json()
            self._log(f"✅ Position closed for {symbol}")
            
            return data
            
        except Exception as e:
            self._log(f"❌ Error closing position for {symbol}: {e}")
            return {"error": str(e)}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 LEARNING LOOP INTEGRATION | تكامل حلقة التعلم
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_order_for_learning(
        self,
        client_order_id: str
    ) -> Dict[str, Any]:
        """
        Get order details for learning loop feedback
        الحصول على تفاصيل الأمر لتغذية حلقة التعلم
        
        Returns enriched order data including slippage calculation
        """
        if client_order_id not in self._pending_orders:
            return {"error": "Order not found"}
        
        order = self._pending_orders[client_order_id]
        
        if not order.order_id:
            return {"error": "Order not submitted yet"}
        
        # Fetch current order status
        current_order = await self.get_order(order.order_id)
        
        # Calculate slippage if filled
        slippage = 0.0
        if order.limit_price and current_order.get("filled_avg_price"):
            filled_price = float(current_order.get("filled_avg_price"))
            slippage = abs(filled_price - order.limit_price) / order.limit_price * 100
        
        return {
            "client_order_id": client_order_id,
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "qty": order.qty,
            "order_type": order.order_type.value,
            "requested_price": order.limit_price,
            "filled_price": float(current_order.get("filled_avg_price") or 0),
            "filled_qty": float(current_order.get("filled_qty") or 0),
            "status": current_order.get("status"),
            "slippage_pct": slippage,
            "submitted_at": order.submitted_at,
            "filled_at": current_order.get("filled_at"),
        }
    
    def is_market_open(self) -> bool:
        """Check if US stock market is currently open"""
        now = datetime.utcnow()
        # Convert to Eastern (UTC-5)
        eastern_hour = (now.hour - 5) % 24
        
        # Check if weekday
        if now.weekday() >= 5:  # Saturday or Sunday
            return False
        
        # Check market hours (9:30 AM - 4:00 PM ET)
        if eastern_hour < self.MARKET_OPEN_HOUR:
            return False
        if eastern_hour == self.MARKET_OPEN_HOUR and now.minute < self.MARKET_OPEN_MINUTE:
            return False
        if eastern_hour >= self.MARKET_CLOSE_HOUR:
            return False
        
        return True
    
    def _log(self, message: str) -> None:
        """Print log with prefix"""
        print(f"[AlpacaPaper] {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get connector status"""
        return {
            "name": "AlpacaPaperConnector",
            "version": "1.0.0",
            "market_open": self.is_market_open(),
            "pending_orders": len(self._pending_orders),
            "has_credentials": bool(self.api_key and self.api_secret),
        }
