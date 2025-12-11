"""
📋 Structured Logger V2 for Axiom Antigravity Trading System
Uses structlog for strict JSON output, compatible with BigQuery ingestion.

Features:
- Pure JSON output (no emojis in production)
- Async-safe processor chain
- BigQuery-ready schema: timestamp, level, event, module, context
- Environment-aware: JSON in production, colored console in dev
"""

import os
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from collections import deque
import threading

# Check if structlog is available, fallback to simple JSON if not
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class JSONLogRenderer:
    """
    Custom JSON renderer that outputs BigQuery-compatible log entries.
    Schema: timestamp, level, event, module, context (nested)
    """
    
    def __call__(self, logger: Any, method_name: str, event_dict: Dict[str, Any]) -> str:
        # Extract standard fields
        timestamp = event_dict.pop("timestamp", datetime.now(timezone.utc).isoformat())
        level = event_dict.pop("level", method_name.upper())
        event = event_dict.pop("event", "LOG")
        module = event_dict.pop("module", "unknown")
        
        # Everything else goes into context
        context = event_dict
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "event": event,
            "module": module,
            "context": context
        }
        
        return json.dumps(log_entry, default=str, separators=(",", ":"))


class LogBuffer:
    """
    Thread-safe buffer for log entries, used by BigQuery sink.
    """
    
    def __init__(self, max_size: int = 1000):
        self._buffer: deque = deque(maxlen=max_size)
        self._lock = threading.Lock()
    
    def append(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self._buffer.append(entry)
    
    def flush(self) -> list:
        with self._lock:
            entries = list(self._buffer)
            self._buffer.clear()
            return entries
    
    def __len__(self) -> int:
        return len(self._buffer)


# Global log buffer for BigQuery streaming
_log_buffer = LogBuffer()


def get_log_buffer() -> LogBuffer:
    """Get the global log buffer instance."""
    return _log_buffer


def add_timestamp(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add ISO timestamp to log entry."""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def add_level(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add log level to entry."""
    event_dict["level"] = method_name.upper()
    return event_dict


def buffer_for_bigquery(logger: Any, method_name: str, event_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Add log entry to buffer for async BigQuery streaming."""
    # Only buffer INFO and above
    level_priority = {"debug": 0, "info": 1, "warning": 2, "error": 3, "critical": 4}
    if level_priority.get(method_name, 1) >= 1:
        _log_buffer.append(event_dict.copy())
    return event_dict


def configure_logging(
    module_name: str = "antigravity",
    production: bool = None,
    enable_buffer: bool = True
) -> Any:
    """
    Configure and return a structured logger.
    
    Args:
        module_name: Name of the module (appears in logs)
        production: Force production mode (JSON output). Auto-detects if None.
        enable_buffer: Enable buffering for BigQuery streaming.
    
    Returns:
        Configured logger instance
    """
    # Auto-detect environment
    if production is None:
        production = os.getenv("NODE_ENV", "development") == "production"
    
    processors = [
        add_timestamp,
        add_level,
        structlog.stdlib.add_log_level if STRUCTLOG_AVAILABLE else add_level,
        structlog.processors.add_log_level if STRUCTLOG_AVAILABLE else add_level,
    ]
    
    # Add buffer processor if enabled
    if enable_buffer:
        processors.append(buffer_for_bigquery)
    
    if STRUCTLOG_AVAILABLE:
        if production:
            # Production: Pure JSON output
            processors.append(JSONLogRenderer())
        else:
            # Development: Colored console output
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(module_name).bind(module=module_name)
    else:
        # Fallback: Simple JSON logger without structlog
        return SimpleJSONLogger(module_name, production)


class SimpleJSONLogger:
    """
    Fallback logger when structlog is not installed.
    Outputs strict JSON to stdout.
    """
    
    def __init__(self, module: str, production: bool = True):
        self.module = module
        self.production = production
        self._context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "SimpleJSONLogger":
        """Add persistent context."""
        self._context.update(kwargs)
        return self
    
    def _log(self, level: str, event: str, **kwargs) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "event": event,
            "module": self.module,
            "context": {**self._context, **kwargs}
        }
        
        # Buffer for BigQuery
        _log_buffer.append(entry)
        
        if self.production:
            print(json.dumps(entry, default=str, separators=(",", ":")))
        else:
            # Dev mode: Pretty print
            emoji = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}.get(level.upper(), "📝")
            print(f"{emoji} [{level.upper()}] {self.module}: {event}", end="")
            if kwargs:
                print(f" | {kwargs}")
            else:
                print()
    
    def debug(self, event: str, **kwargs): self._log("debug", event, **kwargs)
    def info(self, event: str, **kwargs): self._log("info", event, **kwargs)
    def warning(self, event: str, **kwargs): self._log("warning", event, **kwargs)
    def warn(self, event: str, **kwargs): self._log("warning", event, **kwargs)
    def error(self, event: str, **kwargs): self._log("error", event, **kwargs)
    def critical(self, event: str, **kwargs): self._log("critical", event, **kwargs)
    
    # Trading-specific methods
    def trade_signal(self, symbol: str, action: str, confidence: int, **kwargs):
        self.info("TRADE_SIGNAL", symbol=symbol, action=action, confidence=confidence, **kwargs)
    
    def trade_executed(self, symbol: str, side: str, qty: float, price: float, **kwargs):
        self.info("TRADE_EXECUTED", symbol=symbol, side=side, qty=qty, price=price, **kwargs)
    
    def trade_rejected(self, symbol: str, reason: str, **kwargs):
        self.warning("TRADE_REJECTED", symbol=symbol, reason=reason, **kwargs)


# Default logger instance (auto-configured)
log = configure_logging()


def get_logger(module_name: str = "antigravity") -> Any:
    """Get a logger instance for a specific module."""
    return configure_logging(module_name)
