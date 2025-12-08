"""
📋 Structured Logger for Axiom Antigravity Trading System
Provides consistent logging with levels, timestamps, and context.

Features:
- Structured JSON logging for Cloudflare
- Log levels: DEBUG, INFO, WARN, ERROR, CRITICAL
- Request/Response logging decorator
- Trade activity tracking
- Performance metrics
"""

import json
from enum import IntEnum


class LogLevel(IntEnum):
    """Log level enumeration with severity."""
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50


class Logger:
    """
    📋 Structured Logger for Cloudflare Workers.
    
    Usage:
        log = Logger("worker", LogLevel.INFO)
        log.info("Request received", path="/api/status")
        log.error("Trade failed", symbol="EURUSD", reason="timeout")
    """
    
    def __init__(self, name: str = "antigravity", level: LogLevel = LogLevel.INFO):
        """
        Initialize logger.
        
        Args:
            name: Logger name (appears in logs)
            level: Minimum log level to output
        """
        self.name = name
        self.level = level
        self._context = {}
    
    def set_context(self, **kwargs):
        """Set persistent context that appears in all logs."""
        self._context.update(kwargs)
    
    def clear_context(self):
        """Clear persistent context."""
        self._context = {}
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """
        Internal log method.
        
        Args:
            level: Log severity level
            message: Log message
            **kwargs: Additional context fields
        """
        if level < self.level:
            return
        
        log_entry = {
            "level": level.name,
            "logger": self.name,
            "message": message,
            **self._context,
            **kwargs
        }
        
        # Format based on level
        emoji = self._get_emoji(level)
        
        # For Cloudflare Workers, print outputs to console
        # which is captured in Workers logs
        print(f"{emoji} [{level.name}] {self.name}: {message}", end="")
        
        # Add context if present
        if kwargs:
            print(f" | {json.dumps(kwargs, default=str)}", end="")
        
        print()  # Newline
        
        return log_entry
    
    def _get_emoji(self, level: LogLevel) -> str:
        """Get emoji for log level."""
        return {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARN: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨"
        }.get(level, "📝")
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        return self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        return self._log(LogLevel.INFO, message, **kwargs)
    
    def warn(self, message: str, **kwargs):
        """Log warning message."""
        return self._log(LogLevel.WARN, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        return self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        return self._log(LogLevel.CRITICAL, message, **kwargs)
    
    # ==========================================
    # 📊 TRADING-SPECIFIC LOGS
    # ==========================================
    
    def trade_signal(self, symbol: str, action: str, confidence: int, **kwargs):
        """Log a trading signal."""
        self.info(
            f"Signal: {action} {symbol}",
            event="TRADE_SIGNAL",
            symbol=symbol,
            action=action,
            confidence=confidence,
            **kwargs
        )
    
    def trade_executed(self, symbol: str, side: str, qty: float, price: float, **kwargs):
        """Log a trade execution."""
        self.info(
            f"Trade Executed: {side.upper()} {qty} {symbol} @ ${price}",
            event="TRADE_EXECUTED",
            symbol=symbol,
            side=side,
            qty=qty,
            price=price,
            **kwargs
        )
    
    def trade_rejected(self, symbol: str, reason: str, **kwargs):
        """Log a rejected trade."""
        self.warn(
            f"Trade Rejected: {symbol} - {reason}",
            event="TRADE_REJECTED",
            symbol=symbol,
            reason=reason,
            **kwargs
        )
    
    def panic_mode(self, activated: bool, reason: str = None):
        """Log panic mode activation/deactivation."""
        if activated:
            self.critical(
                "PANIC MODE ACTIVATED",
                event="PANIC_MODE_ON",
                reason=reason
            )
        else:
            self.info(
                "Panic mode deactivated",
                event="PANIC_MODE_OFF"
            )
    
    # ==========================================
    # 🔌 API/REQUEST LOGS
    # ==========================================
    
    def request(self, method: str, path: str, **kwargs):
        """Log incoming request."""
        self.debug(
            f"{method} {path}",
            event="REQUEST",
            method=method,
            path=path,
            **kwargs
        )
    
    def response(self, status: int, duration_ms: float = None, **kwargs):
        """Log response."""
        level = LogLevel.INFO if status < 400 else LogLevel.ERROR
        self._log(
            level,
            f"Response: {status}",
            event="RESPONSE",
            status=status,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def api_call(self, service: str, endpoint: str, status: int = None, **kwargs):
        """Log external API call."""
        self.debug(
            f"API: {service} -> {endpoint}",
            event="API_CALL",
            service=service,
            endpoint=endpoint,
            status=status,
            **kwargs
        )
    
    # ==========================================
    # 📈 ANALYSIS LOGS
    # ==========================================
    
    def analysis(self, engine: str, symbol: str, result: dict, **kwargs):
        """Log analysis result."""
        self.debug(
            f"Analysis: {engine} on {symbol}",
            event="ANALYSIS",
            engine=engine,
            symbol=symbol,
            result=result,
            **kwargs
        )
    
    def twin_turbo(self, aexi_score: float, dream_score: float, triggered: bool):
        """Log Twin-Turbo engine status."""
        level = LogLevel.INFO if triggered else LogLevel.DEBUG
        self._log(
            level,
            f"Twin-Turbo: AEXI={aexi_score:.1f}, Dream={dream_score:.1f}",
            event="TWIN_TURBO",
            aexi_score=aexi_score,
            dream_score=dream_score,
            triggered=triggered
        )


# ==========================================
# 🌐 GLOBAL LOGGER INSTANCE
# ==========================================

# Default logger instance
log = Logger("antigravity", LogLevel.INFO)


def get_logger(name: str = "antigravity", level: LogLevel = LogLevel.INFO) -> Logger:
    """Get a logger instance."""
    return Logger(name, level)
