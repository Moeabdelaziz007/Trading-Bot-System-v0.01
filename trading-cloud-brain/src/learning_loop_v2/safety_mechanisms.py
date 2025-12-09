#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛡️ SAFETY MECHANISMS | آليات الأمان
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Implement comprehensive safety checks for Mini-Agent Swarm
Components:
    - TradingModeGuard: Enforce SIMULATION | PAPER | LIVE modes
    - DriftGuardIntegration: Block trades during drift detection
    - SafetyOrchestrator: Coordinate all safety checks

Author: Axiom AI Partner | Mohamed Hossameldin Abdelaziz
Date: December 9, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Any
from enum import Enum


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 ENUMS & CONSTANTS | التعدادات والثوابت
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TradingMode(Enum):
    """Trading execution modes."""
    SIMULATION = "SIMULATION"  # Logs only, no API calls
    PAPER = "PAPER"            # Paper trading APIs
    LIVE = "LIVE"              # Real money trading


class SafetyStatus(Enum):
    """Safety check result status."""
    SAFE = "SAFE"              # All checks passed
    BLOCKED = "BLOCKED"        # Trade blocked by safety
    WARNING = "WARNING"        # Proceed with caution
    ERROR = "ERROR"            # System error


class BlockReason(Enum):
    """Reasons for blocking a trade."""
    MODE_SIMULATION = "MODE_SIMULATION"
    DRIFT_DETECTED = "DRIFT_DETECTED"
    CIRCUIT_BREAKER = "CIRCUIT_BREAKER"
    DRAWDOWN_LIMIT = "DRAWDOWN_LIMIT"
    DATA_STALE = "DATA_STALE"
    CONSECUTIVE_LOSSES = "CONSECUTIVE_LOSSES"
    MANUAL_HALT = "MANUAL_HALT"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️ TRADING MODE GUARD | حارس وضع التداول
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class TradingModeGuard:
    """
    Enforces TRADING_MODE compliance.
    Routes trades to appropriate handlers based on mode.
    """
    
    def __init__(self, mode: Optional[str] = None):
        self.mode = self._parse_mode(
            mode or os.environ.get("TRADING_MODE", "SIMULATION")
        )
    
    def _parse_mode(self, mode_str: str) -> TradingMode:
        """Parse mode string to enum."""
        mode_str = mode_str.upper().strip()
        try:
            return TradingMode(mode_str)
        except ValueError:
            # Default to SIMULATION for safety
            return TradingMode.SIMULATION
    
    def can_execute(self) -> Tuple[bool, Optional[BlockReason]]:
        """Check if trading execution is allowed."""
        if self.mode == TradingMode.SIMULATION:
            return False, BlockReason.MODE_SIMULATION
        return True, None
    
    def get_api_mode(self) -> str:
        """Get API mode for broker connections."""
        if self.mode == TradingMode.PAPER:
            return "paper"
        elif self.mode == TradingMode.LIVE:
            return "live"
        return "simulation"
    
    def is_live(self) -> bool:
        """Check if in live trading mode."""
        return self.mode == TradingMode.LIVE
    
    def is_paper(self) -> bool:
        """Check if in paper trading mode."""
        return self.mode == TradingMode.PAPER


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 DRIFT GUARD INTEGRATION | تكامل حارس الانحراف
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class DriftStatus:
    """Status of the DriftGuard system."""
    drift_detected: bool = False
    current_accuracy: float = 1.0
    baseline_accuracy: float = 0.55
    deviation: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)


class DriftGuardIntegration:
    """
    Integrates with DriftGuard to block trades during drift.
    Monitors model performance and triggers alerts.
    """
    
    def __init__(self, threshold: float = 0.1):
        self.threshold = threshold  # 10% deviation threshold
        self.status = DriftStatus()
    
    def update_status(
        self, 
        current_accuracy: float, 
        baseline_accuracy: float = 0.55
    ) -> DriftStatus:
        """Update drift status based on current vs baseline accuracy."""
        deviation = baseline_accuracy - current_accuracy
        drift_detected = deviation > self.threshold
        
        self.status = DriftStatus(
            drift_detected=drift_detected,
            current_accuracy=current_accuracy,
            baseline_accuracy=baseline_accuracy,
            deviation=deviation,
            last_check=datetime.now()
        )
        
        return self.status
    
    def can_trade(self) -> Tuple[bool, Optional[BlockReason]]:
        """Check if trading is safe based on drift status."""
        if self.status.drift_detected:
            return False, BlockReason.DRIFT_DETECTED
        return True, None
    
    def get_status_dict(self) -> Dict:
        """Get drift status as dictionary."""
        return {
            "drift_detected": self.status.drift_detected,
            "current_accuracy": round(self.status.current_accuracy, 4),
            "baseline_accuracy": self.status.baseline_accuracy,
            "deviation": round(self.status.deviation, 4),
            "threshold": self.threshold,
            "last_check": self.status.last_check.isoformat()
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛑 CIRCUIT BREAKER | قاطع الدائرة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class CircuitBreakerState:
    """State of the circuit breaker."""
    is_open: bool = False
    reason: Optional[BlockReason] = None
    triggered_at: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None
    consecutive_failures: int = 0
    daily_drawdown: float = 0.0


class CircuitBreaker:
    """
    Implements circuit breaker pattern for trading safety.
    Halts trading on:
        - 3 consecutive API failures
        - 5% daily drawdown
        - Manual halt
    """
    
    MAX_CONSECUTIVE_FAILURES = 3
    MAX_DAILY_DRAWDOWN = 0.05  # 5%
    COOLDOWN_MINUTES = 30
    
    def __init__(self):
        self.state = CircuitBreakerState()
    
    def record_failure(self) -> None:
        """Record an API or trade failure."""
        self.state.consecutive_failures += 1
        
        if self.state.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self._trip(BlockReason.CONSECUTIVE_LOSSES)
    
    def record_success(self) -> None:
        """Record a successful operation."""
        self.state.consecutive_failures = 0
    
    def update_drawdown(self, current_drawdown: float) -> None:
        """Update daily drawdown percentage."""
        self.state.daily_drawdown = current_drawdown
        
        if current_drawdown >= self.MAX_DAILY_DRAWDOWN:
            self._trip(BlockReason.DRAWDOWN_LIMIT)
    
    def _trip(self, reason: BlockReason) -> None:
        """Trip the circuit breaker."""
        self.state.is_open = True
        self.state.reason = reason
        self.state.triggered_at = datetime.now()
        self.state.cooldown_until = (
            datetime.now() + timedelta(minutes=self.COOLDOWN_MINUTES)
        )
    
    def reset(self) -> None:
        """Reset the circuit breaker."""
        self.state = CircuitBreakerState()
    
    def can_trade(self) -> Tuple[bool, Optional[BlockReason]]:
        """Check if trading is allowed."""
        # Check cooldown
        if self.state.cooldown_until:
            if datetime.now() < self.state.cooldown_until:
                return False, self.state.reason
            else:
                # Cooldown expired, reset
                self.reset()
        
        if self.state.is_open:
            return False, self.state.reason
        
        return True, None
    
    def get_status_dict(self) -> Dict:
        """Get circuit breaker status as dictionary."""
        return {
            "is_open": self.state.is_open,
            "reason": self.state.reason.value if self.state.reason else None,
            "consecutive_failures": self.state.consecutive_failures,
            "daily_drawdown": round(self.state.daily_drawdown, 4),
            "max_drawdown": self.MAX_DAILY_DRAWDOWN,
            "triggered_at": (
                self.state.triggered_at.isoformat() 
                if self.state.triggered_at else None
            ),
            "cooldown_until": (
                self.state.cooldown_until.isoformat() 
                if self.state.cooldown_until else None
            )
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📡 DATA FRESHNESS CHECKER | مدقق حداثة البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class DataFreshnessChecker:
    """
    Ensures market data is fresh before trading.
    Blocks trades if data is stale.
    """
    
    MAX_STALE_SECONDS = 60  # 1 minute
    
    def __init__(self):
        self.last_data_timestamps: Dict[str, datetime] = {}
    
    def update_timestamp(self, symbol: str) -> None:
        """Update the last data timestamp for a symbol."""
        self.last_data_timestamps[symbol] = datetime.now()
    
    def is_fresh(self, symbol: str) -> bool:
        """Check if data for symbol is fresh."""
        if symbol not in self.last_data_timestamps:
            return False
        
        age = datetime.now() - self.last_data_timestamps[symbol]
        return age.total_seconds() < self.MAX_STALE_SECONDS
    
    def can_trade(self, symbol: str) -> Tuple[bool, Optional[BlockReason]]:
        """Check if data is fresh enough to trade."""
        if not self.is_fresh(symbol):
            return False, BlockReason.DATA_STALE
        return True, None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️ SAFETY ORCHESTRATOR | منسق الأمان
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class SafetyCheckResult:
    """Result of a complete safety check."""
    status: SafetyStatus
    can_trade: bool
    block_reasons: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "can_trade": self.can_trade,
            "block_reasons": [r.value for r in self.block_reasons],
            "warnings": self.warnings,
            "timestamp": self.timestamp.isoformat()
        }


class SafetyOrchestrator:
    """
    Coordinates all safety checks before trade execution.
    Single point of entry for all safety validations.
    """
    
    def __init__(self, trading_mode: Optional[str] = None):
        self.mode_guard = TradingModeGuard(trading_mode)
        self.drift_guard = DriftGuardIntegration()
        self.circuit_breaker = CircuitBreaker()
        self.freshness_checker = DataFreshnessChecker()
        self.manual_halt = False
    
    def set_manual_halt(self, halt: bool) -> None:
        """Manually halt or resume trading."""
        self.manual_halt = halt
    
    def check_all(self, symbol: str) -> SafetyCheckResult:
        """
        Run all safety checks for a trade.
        Returns comprehensive result.
        """
        block_reasons = []
        warnings = []
        
        # Check 1: Trading Mode
        can_trade_mode, mode_reason = self.mode_guard.can_execute()
        if not can_trade_mode and mode_reason:
            if mode_reason == BlockReason.MODE_SIMULATION:
                # Simulation is not a block, just a mode
                warnings.append("SIMULATION mode - trades logged only")
            else:
                block_reasons.append(mode_reason)
        
        # Check 2: Manual Halt
        if self.manual_halt:
            block_reasons.append(BlockReason.MANUAL_HALT)
        
        # Check 3: Drift Guard
        can_trade_drift, drift_reason = self.drift_guard.can_trade()
        if not can_trade_drift and drift_reason:
            block_reasons.append(drift_reason)
        
        # Check 4: Circuit Breaker
        can_trade_cb, cb_reason = self.circuit_breaker.can_trade()
        if not can_trade_cb and cb_reason:
            block_reasons.append(cb_reason)
        
        # Check 5: Data Freshness
        can_trade_fresh, fresh_reason = self.freshness_checker.can_trade(symbol)
        if not can_trade_fresh and fresh_reason:
            block_reasons.append(fresh_reason)
        
        # Determine final status
        if block_reasons:
            status = SafetyStatus.BLOCKED
            can_trade = False
        elif warnings:
            status = SafetyStatus.WARNING
            can_trade = self.mode_guard.mode != TradingMode.SIMULATION
        else:
            status = SafetyStatus.SAFE
            can_trade = True
        
        return SafetyCheckResult(
            status=status,
            can_trade=can_trade,
            block_reasons=block_reasons,
            warnings=warnings
        )
    
    def get_full_status(self) -> Dict:
        """Get status of all safety components."""
        return {
            "trading_mode": self.mode_guard.mode.value,
            "manual_halt": self.manual_halt,
            "drift_guard": self.drift_guard.get_status_dict(),
            "circuit_breaker": self.circuit_breaker.get_status_dict(),
            "timestamp": datetime.now().isoformat()
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🏭 FACTORY | المصنع
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_safety_instance: Optional[SafetyOrchestrator] = None


def get_safety_orchestrator() -> SafetyOrchestrator:
    """Get or create the global safety orchestrator."""
    global _safety_instance
    if _safety_instance is None:
        _safety_instance = SafetyOrchestrator()
    return _safety_instance


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST | اختبار
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("━" * 60)
    print("🛡️ SAFETY MECHANISMS TEST")
    print("━" * 60)
    
    # Create safety orchestrator
    safety = SafetyOrchestrator(trading_mode="SIMULATION")
    
    # Update data freshness
    safety.freshness_checker.update_timestamp("BTCUSDT")
    
    # Run safety check
    result = safety.check_all("BTCUSDT")
    
    print(f"\n📋 Safety Check Result:")
    print(f"   Status: {result.status.value}")
    print(f"   Can Trade: {result.can_trade}")
    print(f"   Block Reasons: {[r.value for r in result.block_reasons]}")
    print(f"   Warnings: {result.warnings}")
    
    # Test circuit breaker
    print(f"\n🛑 Testing Circuit Breaker:")
    for i in range(4):
        safety.circuit_breaker.record_failure()
        print(f"   Failure #{i+1}: Open={safety.circuit_breaker.state.is_open}")
    
    result2 = safety.check_all("BTCUSDT")
    print(f"   After 4 failures: {result2.status.value}")
    
    # Test drift guard
    print(f"\n🔍 Testing Drift Guard:")
    safety.circuit_breaker.reset()
    safety.drift_guard.update_status(current_accuracy=0.40)  # Below threshold
    result3 = safety.check_all("BTCUSDT")
    print(f"   With drift detected: {result3.status.value}")
    print(f"   Block reasons: {[r.value for r in result3.block_reasons]}")
    
    # Full status
    print(f"\n📊 Full Safety Status:")
    status = safety.get_full_status()
    for key, value in status.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        else:
            print(f"   {key}: {value}")
    
    print("\n" + "━" * 60)
    print("✅ Safety mechanisms test complete!")
    print("━" * 60)
