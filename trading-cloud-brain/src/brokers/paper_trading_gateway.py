"""
🌐 Unified Paper Trading Gateway
بوابة التداول الورقي الموحدة - Alpaca + Bybit

AlphaAxiom Learning Loop v2.0
Author: Axiom AI Partner
Status: ACTIVE as of December 9, 2025

Features:
- Unified interface for Alpaca (stocks) and Bybit (crypto)
- Smart routing based on asset type
- Integrated leverage management for crypto
- Circuit breaker and safety protocols
- Learning Loop integration for trade feedback

Asset Routing:
- Stocks/ETFs (AAPL, SPY, etc.) → Alpaca Paper
- Crypto (BTCUSDT, PEPEUSDT, etc.) → Bybit Testnet
"""

import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 DATA STRUCTURES | هياكل البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AssetClass(Enum):
    """Asset classification for routing"""
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"
    MEME_COIN = "meme_coin"


class BrokerType(Enum):
    """Broker types"""
    ALPACA = "alpaca"
    BYBIT = "bybit"


class VolatilityLevel(Enum):
    """Volatility levels for leverage management"""
    LOW = "low"        # ATR < 1%
    MEDIUM = "medium"  # 1% <= ATR < 3%
    HIGH = "high"      # ATR >= 3%


@dataclass
class TradeRequest:
    """Unified trade request structure"""
    symbol: str
    qty: float
    side: str  # "buy" or "sell"
    order_type: str = "market"
    limit_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    agent_name: str = "unknown"
    leverage: int = 1
    reduce_only: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "qty": self.qty,
            "side": self.side,
            "order_type": self.order_type,
            "limit_price": self.limit_price,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "agent_name": self.agent_name,
            "leverage": self.leverage,
        }


@dataclass
class TradeResult:
    """Unified trade result"""
    success: bool
    order_id: Optional[str]
    broker: BrokerType
    symbol: str
    side: str
    qty: float
    filled_price: Optional[float]
    slippage_pct: float = 0.0
    error: Optional[str] = None
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "order_id": self.order_id,
            "broker": self.broker.value,
            "symbol": self.symbol,
            "side": self.side,
            "qty": self.qty,
            "filled_price": self.filled_price,
            "slippage_pct": self.slippage_pct,
            "error": self.error,
            "timestamp": self.timestamp,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️ LEVERAGE MANAGER | مدير الرافعة المالية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LeverageManager:
    """
    Smart leverage manager for crypto trading
    مدير الرافعة الذكي للتداول بالعملات المشفرة
    
    Conservative rules to protect capital:
    - Low volatility → Max 3x leverage
    - Medium volatility → Max 2x leverage
    - High volatility → No leverage (1x)
    - Drawdown > 2% → Cut leverage in half
    """
    
    # Leverage rules based on volatility
    LEVERAGE_RULES = {
        VolatilityLevel.LOW: 3,
        VolatilityLevel.MEDIUM: 2,
        VolatilityLevel.HIGH: 1,
    }
    
    # ATR thresholds for volatility classification
    ATR_THRESHOLDS = {
        "low": 0.01,    # < 1%
        "high": 0.03,   # >= 3%
    }
    
    # Maximum allowed leverage (safety cap)
    MAX_LEVERAGE = 5
    
    # Drawdown threshold for leverage reduction
    DRAWDOWN_THRESHOLD = 0.02  # 2%
    
    def __init__(self, env=None):
        self.env = env
        self.daily_pnl = 0.0
        self.starting_equity = 0.0
        self._log("🛡️ LeverageManager initialized")
    
    def calculate_safe_leverage(
        self,
        symbol: str,
        atr_percent: float,
        current_drawdown: float = 0.0,
        requested_leverage: int = 1
    ) -> int:
        """
        Calculate safe leverage based on conditions
        حساب الرافعة الآمنة بناءً على الظروف
        
        Args:
            symbol: Trading symbol
            atr_percent: ATR as percentage of price
            current_drawdown: Current drawdown percentage
            requested_leverage: User requested leverage
            
        Returns:
            Safe leverage value (1-5)
        """
        # Determine volatility level
        if atr_percent < self.ATR_THRESHOLDS["low"]:
            volatility = VolatilityLevel.LOW
        elif atr_percent >= self.ATR_THRESHOLDS["high"]:
            volatility = VolatilityLevel.HIGH
        else:
            volatility = VolatilityLevel.MEDIUM
        
        # Get base leverage from rules
        base_leverage = self.LEVERAGE_RULES[volatility]
        
        # Apply drawdown penalty
        if current_drawdown >= self.DRAWDOWN_THRESHOLD:
            base_leverage = max(1, base_leverage // 2)
            self._log(f"⚠️ Drawdown {current_drawdown:.1%}: Leverage halved")
        
        # Cap at maximum and requested
        safe_leverage = min(base_leverage, self.MAX_LEVERAGE, requested_leverage)
        
        self._log(f"📊 {symbol}: ATR={atr_percent:.2%}, "
                  f"Vol={volatility.value}, Leverage={safe_leverage}x")
        
        return safe_leverage
    
    def _log(self, message: str) -> None:
        print(f"[LeverageManager] {message}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚡ CIRCUIT BREAKER V2 | قاطع الدائرة المحسن
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CircuitBreakerV2:
    """
    Enhanced circuit breaker for dual-broker system
    قاطع الدائرة المحسن للنظام ثنائي الوسيط
    
    Separate thresholds for stocks vs crypto due to volatility differences
    """
    
    # Per-broker thresholds
    THRESHOLDS = {
        BrokerType.ALPACA: {
            "max_daily_loss_pct": 5.0,
            "max_consecutive_failures": 3,
            "cooldown_minutes": 15,
        },
        BrokerType.BYBIT: {
            "max_daily_loss_pct": 3.0,  # Stricter for crypto
            "max_consecutive_failures": 3,
            "cooldown_minutes": 30,  # Longer cooldown
        },
    }
    
    def __init__(self, env=None):
        self.env = env
        
        # Per-broker state
        self._state = {
            BrokerType.ALPACA: {
                "is_open": False,
                "consecutive_failures": 0,
                "daily_loss_pct": 0.0,
                "last_failure_time": None,
            },
            BrokerType.BYBIT: {
                "is_open": False,
                "consecutive_failures": 0,
                "daily_loss_pct": 0.0,
                "last_failure_time": None,
            },
        }
        
        self._log("⚡ CircuitBreakerV2 initialized")
    
    def is_trading_allowed(self, broker: BrokerType) -> bool:
        """Check if trading is allowed for a broker"""
        state = self._state[broker]
        
        if state["is_open"]:
            # Check if cooldown has passed
            if state["last_failure_time"]:
                cooldown = self.THRESHOLDS[broker]["cooldown_minutes"]
                elapsed = (datetime.now() - state["last_failure_time"]).seconds / 60
                
                if elapsed >= cooldown:
                    self._close_circuit(broker)
                    return True
                
                self._log(f"🔴 {broker.value}: Circuit OPEN, "
                          f"{cooldown - elapsed:.0f}min remaining")
                return False
        
        return True
    
    def record_success(self, broker: BrokerType) -> None:
        """Record successful trade"""
        state = self._state[broker]
        state["consecutive_failures"] = 0
    
    def record_failure(self, broker: BrokerType) -> None:
        """Record failed trade/API call"""
        state = self._state[broker]
        state["consecutive_failures"] += 1
        state["last_failure_time"] = datetime.now()
        
        threshold = self.THRESHOLDS[broker]["max_consecutive_failures"]
        if state["consecutive_failures"] >= threshold:
            self._open_circuit(broker)
    
    def record_loss(self, broker: BrokerType, loss_pct: float) -> None:
        """Record daily loss"""
        state = self._state[broker]
        state["daily_loss_pct"] += loss_pct
        
        threshold = self.THRESHOLDS[broker]["max_daily_loss_pct"]
        if state["daily_loss_pct"] >= threshold:
            self._open_circuit(broker)
            self._log(f"🔴 {broker.value}: Daily loss {state['daily_loss_pct']:.1f}%")
    
    def _open_circuit(self, broker: BrokerType) -> None:
        """Open circuit breaker"""
        self._state[broker]["is_open"] = True
        self._state[broker]["last_failure_time"] = datetime.now()
        self._log(f"🔴 {broker.value}: Circuit OPENED")
    
    def _close_circuit(self, broker: BrokerType) -> None:
        """Close circuit breaker (reset)"""
        self._state[broker]["is_open"] = False
        self._state[broker]["consecutive_failures"] = 0
        self._log(f"🟢 {broker.value}: Circuit CLOSED (reset)")
    
    def reset_daily(self) -> None:
        """Reset daily counters (call at market open)"""
        for broker in BrokerType:
            self._state[broker]["daily_loss_pct"] = 0.0
        self._log("📅 Daily counters reset")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            broker.value: {
                "is_open": state["is_open"],
                "failures": state["consecutive_failures"],
                "daily_loss": state["daily_loss_pct"],
            }
            for broker, state in self._state.items()
        }
    
    def _log(self, message: str) -> None:
        print(f"[CircuitBreakerV2] {message}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 UNIFIED PAPER TRADING GATEWAY | البوابة الموحدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PaperTradingGateway:
    """
    Unified gateway for paper trading across Alpaca and Bybit
    بوابة موحدة للتداول الورقي عبر Alpaca و Bybit
    
    Routes trades to appropriate broker based on asset type:
    - Stocks/ETFs → Alpaca Paper Trading
    - Crypto → Bybit Testnet
    
    Includes:
    - Smart leverage management
    - Circuit breaker protection
    - Slippage tracking for learning loop
    - TRADING_MODE compliance
    """
    
    # Crypto suffixes
    CRYPTO_SUFFIXES = ["USDT", "USD", "BUSD", "USDC"]
    
    # Known stock tickers (subset)
    STOCK_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "SPY", "QQQ"]
    
    def __init__(self, env=None):
        """
        Initialize unified gateway
        
        Args:
            env: Cloudflare Workers environment
        """
        self.env = env
        
        # Initialize components
        self.leverage_manager = LeverageManager(env)
        self.circuit_breaker = CircuitBreakerV2(env)
        
        # Broker instances (lazy loaded)
        self._alpaca = None
        self._bybit = None
        
        # Get trading mode
        self._trading_mode = self._get_trading_mode()
        
        # Trade tracking for learning loop
        self._trade_log: List[TradeResult] = []
        
        self._log("🌐 PaperTradingGateway initialized")
        self._log(f"   Trading Mode: {self._trading_mode}")
    
    def _get_trading_mode(self) -> str:
        """Get TRADING_MODE from environment"""
        if self.env:
            return getattr(self.env, 'TRADING_MODE', 'SIMULATION')
        return 'SIMULATION'
    
    def _get_alpaca(self):
        """Lazy load Alpaca connector"""
        if self._alpaca is None:
            from .alpaca_paper import AlpacaPaperConnector
            self._alpaca = AlpacaPaperConnector(env=self.env)
        return self._alpaca
    
    def _get_bybit(self):
        """Lazy load Bybit connector"""
        if self._bybit is None:
            from .bybit_testnet import BybitTestnetConnector
            self._bybit = BybitTestnetConnector(env=self.env, testnet=True)
        return self._bybit
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔀 ASSET ROUTING | توجيه الأصول
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def classify_asset(self, symbol: str) -> AssetClass:
        """
        Classify asset type from symbol
        تصنيف نوع الأصل من الرمز
        """
        symbol_upper = symbol.upper()
        
        # Check for crypto suffixes
        for suffix in self.CRYPTO_SUFFIXES:
            if symbol_upper.endswith(suffix):
                # Check for meme coins
                base = symbol_upper.replace(suffix, "")
                if base in ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF"]:
                    return AssetClass.MEME_COIN
                return AssetClass.CRYPTO
        
        # Check for known stock tickers
        if symbol_upper in self.STOCK_TICKERS:
            return AssetClass.STOCK
        
        # Check for ETF patterns
        if len(symbol_upper) <= 4 and symbol_upper.isalpha():
            return AssetClass.ETF
        
        # Default to crypto if unclear
        return AssetClass.CRYPTO
    
    def get_broker_for_asset(self, symbol: str) -> BrokerType:
        """
        Get appropriate broker for asset
        الحصول على الوسيط المناسب للأصل
        """
        asset_class = self.classify_asset(symbol)
        
        if asset_class in [AssetClass.STOCK, AssetClass.ETF]:
            return BrokerType.ALPACA
        
        return BrokerType.BYBIT
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📤 TRADE EXECUTION | تنفيذ الصفقات
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def execute_trade(
        self,
        request: TradeRequest,
        atr_percent: float = 0.02
    ) -> TradeResult:
        """
        Execute trade through appropriate broker
        تنفيذ الصفقة عبر الوسيط المناسب
        
        Args:
            request: Trade request with all parameters
            atr_percent: Current ATR for leverage calculation
            
        Returns:
            TradeResult with execution details
        """
        # Check trading mode
        if self._trading_mode == "SIMULATION":
            return self._simulate_trade(request)
        
        # Determine broker
        broker = self.get_broker_for_asset(request.symbol)
        
        # Check circuit breaker
        if not self.circuit_breaker.is_trading_allowed(broker):
            return TradeResult(
                success=False,
                order_id=None,
                broker=broker,
                symbol=request.symbol,
                side=request.side,
                qty=request.qty,
                filled_price=None,
                error="Circuit breaker OPEN",
                timestamp=datetime.now().isoformat(),
            )
        
        try:
            if broker == BrokerType.ALPACA:
                result = await self._execute_alpaca(request)
            else:
                # Calculate safe leverage for crypto
                safe_leverage = self.leverage_manager.calculate_safe_leverage(
                    symbol=request.symbol,
                    atr_percent=atr_percent,
                    requested_leverage=request.leverage,
                )
                request.leverage = safe_leverage
                result = await self._execute_bybit(request)
            
            # Record success
            self.circuit_breaker.record_success(broker)
            
            # Log for learning
            self._trade_log.append(result)
            
            return result
            
        except Exception as e:
            # Record failure
            self.circuit_breaker.record_failure(broker)
            
            return TradeResult(
                success=False,
                order_id=None,
                broker=broker,
                symbol=request.symbol,
                side=request.side,
                qty=request.qty,
                filled_price=None,
                error=str(e),
                timestamp=datetime.now().isoformat(),
            )
    
    async def _execute_alpaca(self, request: TradeRequest) -> TradeResult:
        """Execute trade via Alpaca Paper"""
        alpaca = self._get_alpaca()
        
        order = await alpaca.submit_order(
            symbol=request.symbol,
            qty=request.qty,
            side=request.side,
            order_type=request.order_type,
            limit_price=request.limit_price,
            agent_name=request.agent_name,
        )
        
        return TradeResult(
            success=order.status is not None,
            order_id=order.order_id,
            broker=BrokerType.ALPACA,
            symbol=request.symbol,
            side=request.side,
            qty=request.qty,
            filled_price=order.filled_avg_price,
            timestamp=datetime.now().isoformat(),
        )
    
    async def _execute_bybit(self, request: TradeRequest) -> TradeResult:
        """Execute trade via Bybit Testnet"""
        bybit = self._get_bybit()
        
        # Set leverage first
        if request.leverage > 1:
            await bybit.set_leverage(request.symbol, request.leverage)
        
        order = await bybit.submit_order(
            symbol=request.symbol,
            qty=request.qty,
            side=request.side.capitalize(),
            order_type=request.order_type.capitalize(),
            price=request.limit_price,
            stop_loss=request.stop_loss,
            take_profit=request.take_profit,
            reduce_only=request.reduce_only,
            agent_name=request.agent_name,
        )
        
        return TradeResult(
            success=order.order_id is not None,
            order_id=order.order_id,
            broker=BrokerType.BYBIT,
            symbol=request.symbol,
            side=request.side,
            qty=request.qty,
            filled_price=order.avg_price,
            timestamp=datetime.now().isoformat(),
        )
    
    def _simulate_trade(self, request: TradeRequest) -> TradeResult:
        """Simulate trade in SIMULATION mode"""
        self._log(f"🧪 SIMULATION: {request.side} {request.qty} {request.symbol}")
        
        return TradeResult(
            success=True,
            order_id=f"sim_{int(time.time()*1000)}",
            broker=self.get_broker_for_asset(request.symbol),
            symbol=request.symbol,
            side=request.side,
            qty=request.qty,
            filled_price=request.limit_price or 0.0,
            timestamp=datetime.now().isoformat(),
        )
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 ACCOUNT & POSITIONS | الحساب والمراكز
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    async def get_all_positions(self) -> Dict[str, List[Dict]]:
        """
        Get positions from all brokers
        الحصول على المراكز من جميع الوسطاء
        """
        result = {
            "alpaca": [],
            "bybit": [],
        }
        
        try:
            alpaca = self._get_alpaca()
            positions = await alpaca.get_positions()
            result["alpaca"] = [p.to_dict() for p in positions]
        except Exception as e:
            self._log(f"⚠️ Error getting Alpaca positions: {e}")
        
        try:
            bybit = self._get_bybit()
            positions = await bybit.get_positions()
            result["bybit"] = [p.to_dict() for p in positions]
        except Exception as e:
            self._log(f"⚠️ Error getting Bybit positions: {e}")
        
        return result
    
    async def get_total_equity(self) -> Dict[str, float]:
        """
        Get total equity across all brokers
        الحصول على إجمالي حقوق الملكية
        """
        equity = {
            "alpaca_usd": 0.0,
            "bybit_usdt": 0.0,
            "total_usd": 0.0,
        }
        
        try:
            alpaca = self._get_alpaca()
            account = await alpaca.get_account()
            equity["alpaca_usd"] = account.get("equity", 0.0)
        except Exception:
            pass
        
        try:
            bybit = self._get_bybit()
            balance = await bybit.get_wallet_balance()
            equity["bybit_usdt"] = balance.get("equity", 0.0)
        except Exception:
            pass
        
        equity["total_usd"] = equity["alpaca_usd"] + equity["bybit_usdt"]
        
        return equity
    
    async def close_all_positions(
        self,
        broker: BrokerType = None
    ) -> Dict[str, Any]:
        """
        Close all positions (panic protocol)
        إغلاق جميع المراكز (بروتوكول الطوارئ)
        """
        results = {"alpaca": [], "bybit": []}
        
        if broker is None or broker == BrokerType.ALPACA:
            try:
                alpaca = self._get_alpaca()
                positions = await alpaca.get_positions()
                for pos in positions:
                    result = await alpaca.close_position(pos.symbol)
                    results["alpaca"].append(result)
            except Exception as e:
                results["alpaca"].append({"error": str(e)})
        
        if broker is None or broker == BrokerType.BYBIT:
            try:
                bybit = self._get_bybit()
                positions = await bybit.get_positions()
                for pos in positions:
                    result = await bybit.close_position(pos.symbol)
                    results["bybit"].append(result)
            except Exception as e:
                results["bybit"].append({"error": str(e)})
        
        self._log("🚨 PANIC PROTOCOL: All positions closed")
        
        return results
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📈 LEARNING LOOP INTEGRATION | تكامل حلقة التعلم
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_trade_log(self) -> List[Dict]:
        """Get trade log for learning loop analysis"""
        return [t.to_dict() for t in self._trade_log]
    
    def clear_trade_log(self) -> None:
        """Clear trade log after processing"""
        self._trade_log = []
    
    def get_status(self) -> Dict[str, Any]:
        """Get gateway status"""
        return {
            "name": "PaperTradingGateway",
            "version": "1.0.0",
            "trading_mode": self._trading_mode,
            "circuit_breaker": self.circuit_breaker.get_status(),
            "trades_logged": len(self._trade_log),
            "brokers": {
                "alpaca": "loaded" if self._alpaca else "lazy",
                "bybit": "loaded" if self._bybit else "lazy",
            },
        }
    
    def _log(self, message: str) -> None:
        print(f"[PaperTradingGateway] {message}")
