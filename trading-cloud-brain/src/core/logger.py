"""
📋 Production-Grade Structured Logger for AlphaAxiom
Outputs pure JSON for Cloudflare Workers Logs with correlation ID tracing.

Features:
- Pure JSON output (machine-readable)
- Correlation ID for request tracing
- ISO 8601 timestamps
- Trading-specific log methods
- BigQuery-compatible schema
"""

import json
import uuid
from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, Dict, Optional


class LogLevel(IntEnum):
    """Log level enumeration with severity."""
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    CRITICAL = 50


class Logger:
    """
    📋 Production Structured Logger for Cloudflare Workers.
    
    Outputs pure JSON format:
    {"timestamp": "...", "level": "INFO", "module": "worker", "event": "REQUEST", "correlation_id": "...", "context": {...}}
    
    Usage:
        log = Logger("worker")
        log.set_correlation_id("abc-123")
        log.info("Request received", path="/api/status")
    """
    
    _correlation_id: Optional[str] = None
    
    def __init__(self, module: str = "antigravity", level: LogLevel = LogLevel.INFO, production: bool = True):
        """
        Initialize logger.
        
        Args:
            module: Module name (appears in logs)
            level: Minimum log level to output
            production: If True, output pure JSON. If False, pretty print.
        """
        self.module = module
        self.level = level
        self.production = production
        self._context: Dict[str, Any] = {}
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set correlation ID for request tracing."""
        self._correlation_id = correlation_id
    
    def new_correlation_id(self) -> str:
        """Generate and set a new correlation ID."""
        self._correlation_id = str(uuid.uuid4())[:8]
        return self._correlation_id
    
    def set_context(self, **kwargs) -> None:
        """Set persistent context that appears in all logs."""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear persistent context."""
        self._context = {}
        self._correlation_id = None
    
    def _log(self, level: LogLevel, event: str, **kwargs) -> Dict[str, Any]:
        """
        Internal log method - outputs pure JSON.
        
        Args:
            level: Log severity level
            event: Event name (e.g., "REQUEST", "TRADE_EXECUTED")
            **kwargs: Additional context fields
        """
        if level < self.level:
            return {}
        
        # Build log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.name,
            "module": self.module,
            "event": event,
        }
        
        # Add correlation ID if set
        if self._correlation_id:
            log_entry["correlation_id"] = self._correlation_id
        
        # Merge persistent context and kwargs
        context = {**self._context, **kwargs}
        if context:
            log_entry["context"] = context
        
        # Output
        if self.production:
            # Pure JSON - one line, no emojis
            print(json.dumps(log_entry, default=str, separators=(",", ":")))
        else:
            # Dev mode - pretty print with emojis
            emoji = self._get_emoji(level)
            print(f"{emoji} [{level.name}] {self.module}: {event}", end="")
            if context:
                print(f" | {context}")
            else:
                print()
        
        return log_entry
    
    def _get_emoji(self, level: LogLevel) -> str:
        """Get emoji for log level (dev mode only)."""
        return {
            LogLevel.DEBUG: "🔍",
            LogLevel.INFO: "ℹ️",
            LogLevel.WARN: "⚠️",
            LogLevel.ERROR: "❌",
            LogLevel.CRITICAL: "🚨"
        }.get(level, "📝")
    
    # ==========================================
    # 📋 STANDARD LOG METHODS
    # ==========================================
    
    def debug(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log debug event."""
        return self._log(LogLevel.DEBUG, event, **kwargs)
    
    def info(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log info event."""
        return self._log(LogLevel.INFO, event, **kwargs)
    
    def warn(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log warning event."""
        return self._log(LogLevel.WARN, event, **kwargs)
    
    def warning(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log warning event (alias)."""
        return self._log(LogLevel.WARN, event, **kwargs)
    
    def error(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log error event."""
        return self._log(LogLevel.ERROR, event, **kwargs)
    
    def critical(self, event: str, **kwargs) -> Dict[str, Any]:
        """Log critical event."""
        return self._log(LogLevel.CRITICAL, event, **kwargs)
    
    # ==========================================
    # 📊 TRADING-SPECIFIC LOGS
    # ==========================================
    
    def trade_signal(self, symbol: str, action: str, confidence: int, **kwargs) -> Dict[str, Any]:
        """Log a trading signal."""
        return self.info("TRADE_SIGNAL", symbol=symbol, action=action, confidence=confidence, **kwargs)
    
    def trade_executed(self, symbol: str, side: str, qty: float, price: float, **kwargs) -> Dict[str, Any]:
        """Log a trade execution."""
        return self.info("TRADE_EXECUTED", symbol=symbol, side=side, qty=qty, price=price, **kwargs)
    
    def trade_rejected(self, symbol: str, reason: str, **kwargs) -> Dict[str, Any]:
        """Log a rejected trade."""
        return self.warn("TRADE_REJECTED", symbol=symbol, reason=reason, **kwargs)
    
    def panic_mode(self, activated: bool, reason: str = None) -> Dict[str, Any]:
        """Log panic mode activation/deactivation."""
        if activated:
            return self.critical("PANIC_MODE_ON", reason=reason)
        return self.info("PANIC_MODE_OFF")
    
    # ==========================================
    # 🔌 API/REQUEST LOGS
    # ==========================================
    
    def request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """Log incoming request."""
        return self.debug("REQUEST", method=method, path=path, **kwargs)
    
    def response(self, status: int, duration_ms: float = None, **kwargs) -> Dict[str, Any]:
        """Log response."""
        level = LogLevel.INFO if status < 400 else LogLevel.ERROR
        return self._log(level, "RESPONSE", status=status, duration_ms=duration_ms, **kwargs)
    
    def api_call(self, service: str, endpoint: str, status: int = None, **kwargs) -> Dict[str, Any]:
        """Log external API call."""
        return self.debug("API_CALL", service=service, endpoint=endpoint, status=status, **kwargs)
    
    # ==========================================
    # 📈 ANALYSIS LOGS
    # ==========================================
    
    def analysis(self, engine: str, symbol: str, result: dict, **kwargs) -> Dict[str, Any]:
        """Log analysis result."""
        return self.debug("ANALYSIS", engine=engine, symbol=symbol, result=result, **kwargs)
    
    def twin_turbo(self, aexi_score: float, dream_score: float, triggered: bool) -> Dict[str, Any]:
        """Log Twin-Turbo engine status."""
        level = LogLevel.INFO if triggered else LogLevel.DEBUG
        return self._log(level, "TWIN_TURBO", aexi_score=aexi_score, dream_score=dream_score, triggered=triggered)
    
    # ==========================================
    # 🏥 HEALTH & OBSERVABILITY
    # ==========================================
    
    def health_check(self, healthy: bool, components: dict = None) -> Dict[str, Any]:
        """Log health check result."""
        level = LogLevel.INFO if healthy else LogLevel.ERROR
        return self._log(level, "HEALTH_CHECK", healthy=healthy, components=components)


# ==========================================
# 🌐 GLOBAL LOGGER INSTANCE
# ==========================================

# Default logger instance (production mode)
log = Logger("antigravity", LogLevel.INFO, production=True)


def get_logger(module: str = "antigravity", level: LogLevel = LogLevel.INFO, production: bool = True) -> Logger:
    """Get a logger instance."""
    return Logger(module, level, production)
