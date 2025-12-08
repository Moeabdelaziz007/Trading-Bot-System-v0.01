"""
🛡️ Custom Exceptions for Axiom Antigravity Trading System
Provides domain-specific exceptions with clear error messages.

Hierarchy:
- AntigravityError (base)
  ├── TradingError
  │   ├── InsufficientBalanceError
  │   ├── PositionNotFoundError
  │   └── TradeExecutionError
  ├── APIError
  │   ├── BrokerConnectionError
  │   ├── RateLimitError
  │   └── AuthenticationError
  ├── AnalysisError
  │   ├── InsufficientDataError
  │   └── IndicatorCalculationError
  └── ConfigurationError
"""


# ==========================================
# 🛡️ BASE EXCEPTION
# ==========================================

class AntigravityError(Exception):
    """Base exception for all Antigravity errors."""
    
    def __init__(self, message: str, code: str = None, details: dict = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        """Convert exception to JSON-serializable dict."""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details
        }
    
    def to_telegram(self) -> str:
        """Format error for Telegram message."""
        return f"❌ <b>خطأ: {self.code}</b>\n{self.message}"


# ==========================================
# 💰 TRADING ERRORS
# ==========================================

class TradingError(AntigravityError):
    """Base exception for trading-related errors."""
    
    def __init__(self, message: str, code: str = "TRADING_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class InsufficientBalanceError(TradingError):
    """Raised when account balance is insufficient for trade."""
    
    def __init__(self, required: float, available: float, symbol: str = None):
        self.required = required
        self.available = available
        message = f"Insufficient balance. Required: ${required:.2f}, Available: ${available:.2f}"
        super().__init__(
            message,
            code="INSUFFICIENT_BALANCE",
            details={"required": required, "available": available, "symbol": symbol}
        )


class PositionNotFoundError(TradingError):
    """Raised when trying to close a non-existent position."""
    
    def __init__(self, symbol: str, position_id: str = None):
        self.symbol = symbol
        message = f"Position not found for {symbol}"
        super().__init__(
            message,
            code="POSITION_NOT_FOUND",
            details={"symbol": symbol, "position_id": position_id}
        )


class TradeExecutionError(TradingError):
    """Raised when trade execution fails at broker."""
    
    def __init__(self, symbol: str, side: str, reason: str):
        self.symbol = symbol
        self.side = side
        self.reason = reason
        message = f"Failed to execute {side.upper()} {symbol}: {reason}"
        super().__init__(
            message,
            code="TRADE_EXECUTION_FAILED",
            details={"symbol": symbol, "side": side, "reason": reason}
        )


class TradeLimitExceededError(TradingError):
    """Raised when daily/hourly trade limits are exceeded."""
    
    def __init__(self, current: int, limit: int, period: str = "day"):
        self.current = current
        self.limit = limit
        message = f"Trade limit exceeded. {current}/{limit} trades today."
        super().__init__(
            message,
            code="TRADE_LIMIT_EXCEEDED",
            details={"current": current, "limit": limit, "period": period}
        )


class RateLimitExceededError(TradingError):
    """Raised when API rate limits are exceeded."""
    
    def __init__(self, limit: int, reset_in: int):
        self.limit = limit
        self.reset_in = reset_in
        message = f"Rate limit exceeded. Retry in {reset_in} seconds."
        super().__init__(
            message,
            code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "reset_in": reset_in}
        )


# ==========================================
# 🔌 API ERRORS
# ==========================================

class APIError(AntigravityError):
    """Base exception for API-related errors."""
    
    def __init__(self, message: str, code: str = "API_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class BrokerConnectionError(APIError):
    """Raised when connection to broker fails."""
    
    def __init__(self, broker: str, reason: str = None):
        self.broker = broker
        message = f"Failed to connect to {broker}"
        if reason:
            message += f": {reason}"
        super().__init__(
            message,
            code="BROKER_CONNECTION_ERROR",
            details={"broker": broker, "reason": reason}
        )


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, service: str, retry_after: int = None):
        self.service = service
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {service}"
        if retry_after:
            message += f". Retry after {retry_after}s"
        super().__init__(
            message,
            code="RATE_LIMIT_EXCEEDED",
            details={"service": service, "retry_after": retry_after}
        )


class AuthenticationError(APIError):
    """Raised when API authentication fails."""
    
    def __init__(self, service: str, reason: str = "Invalid credentials"):
        self.service = service
        message = f"Authentication failed for {service}: {reason}"
        super().__init__(
            message,
            code="AUTH_FAILED",
            details={"service": service, "reason": reason}
        )


class NetworkError(APIError):
    """Raised when network connection fails."""
    
    def __init__(self, service: str, reason: str):
        self.service = service
        message = f"Network error connecting to {service}: {reason}"
        super().__init__(
            message,
            code="NETWORK_ERROR",
            details={"service": service, "reason": reason}
        )


class MaintenanceError(APIError):
    """Raised when service is under maintenance."""
    
    def __init__(self, service: str, eta: str = None):
        self.service = service
        message = f"Service {service} is under maintenance"
        if eta:
            message += f" (ETA: {eta})"
        super().__init__(
            message,
            code="MAINTENANCE_ERROR",
            details={"service": service, "eta": eta}
        )


# ==========================================
# 📊 ANALYSIS ERRORS
# ==========================================

class AnalysisError(AntigravityError):
    """Base exception for analysis-related errors."""
    
    def __init__(self, message: str, code: str = "ANALYSIS_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class InsufficientDataError(AnalysisError):
    """Raised when there's not enough data for analysis."""
    
    def __init__(self, required: int, available: int, indicator: str = None):
        self.required = required
        self.available = available
        message = f"Insufficient data. Need {required} bars, have {available}"
        if indicator:
            message = f"{indicator}: {message}"
        super().__init__(
            message,
            code="INSUFFICIENT_DATA",
            details={"required": required, "available": available, "indicator": indicator}
        )


class IndicatorCalculationError(AnalysisError):
    """Raised when indicator calculation fails."""
    
    def __init__(self, indicator: str, reason: str):
        self.indicator = indicator
        message = f"Failed to calculate {indicator}: {reason}"
        super().__init__(
            message,
            code="INDICATOR_CALC_ERROR",
            details={"indicator": indicator, "reason": reason}
        )


class DataRetrievalError(AnalysisError):
    """Raised when data cannot be retrieved."""
    
    def __init__(self, source: str, symbol: str, reason: str):
        self.source = source
        self.symbol = symbol
        message = f"Failed to retrieve data for {symbol} from {source}: {reason}"
        super().__init__(
            message,
            code="DATA_RETRIEVAL_ERROR",
            details={"source": source, "symbol": symbol, "reason": reason}
        )


class DataValidationError(AnalysisError):
    """Raised when data validation fails."""
    
    def __init__(self, field: str, value: str, constraint: str):
        message = f"Invalid data for {field}: {value} (Constraint: {constraint})"
        super().__init__(
            message,
            code="DATA_VALIDATION_ERROR",
            details={"field": field, "value": value, "constraint": constraint}
        )


# ==========================================
# ⚙️ CONFIGURATION ERRORS
# ==========================================

class ConfigurationError(AntigravityError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, config_key: str, reason: str = "Missing or invalid"):
        self.config_key = config_key
        message = f"Configuration error for '{config_key}': {reason}"
        super().__init__(
            message,
            code="CONFIG_ERROR",
            details={"config_key": config_key, "reason": reason}
        )


class MissingSecretError(ConfigurationError):
    """Raised when a required secret is not configured."""
    
    def __init__(self, secret_name: str):
        self.secret_name = secret_name
        super().__init__(
            secret_name,
            reason=f"Secret '{secret_name}' not configured. Use: wrangler secret put {secret_name}"
        )


class InvalidEnvironmentError(ConfigurationError):
    """Raised when environment configuration is invalid."""
    
    def __init__(self, env: str, expected: str):
        message = f"Invalid environment '{env}'. Expected: {expected}"
        super().__init__(
            message,
            code="INVALID_ENV_ERROR",
            details={"current": env, "expected": expected}
        )


# ==========================================
# 🛑 SAFETY ERRORS
# ==========================================

class SafetyError(AntigravityError):
    """Base exception for safety-related errors."""
    
    def __init__(self, message: str, code: str = "SAFETY_ERROR", **kwargs):
        super().__init__(message, code, **kwargs)


class PanicModeActiveError(SafetyError):
    """Raised when trading is attempted during panic mode."""
    
    def __init__(self, activated_at: str = None):
        message = "Trading halted: Panic mode is active"
        super().__init__(
            message,
            code="PANIC_MODE_ACTIVE",
            details={"activated_at": activated_at}
        )


class DailyLossLimitError(SafetyError):
    """Raised when daily loss limit is exceeded."""
    
    def __init__(self, loss_percent: float, limit_percent: float):
        self.loss_percent = loss_percent
        self.limit_percent = limit_percent
        message = f"Daily loss limit exceeded: {loss_percent:.2f}% (limit: {limit_percent:.2f}%)"
        super().__init__(
            message,
            code="DAILY_LOSS_LIMIT",
            details={"loss_percent": loss_percent, "limit_percent": limit_percent}
        )
