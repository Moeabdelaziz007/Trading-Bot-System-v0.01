"""
🧪 Unit Tests for Custom Exceptions
Tests the exception hierarchy and formatting.
"""

import unittest
from core import (
    AntigravityError,
    TradingError, InsufficientBalanceError, PositionNotFoundError, 
    TradeExecutionError, TradeLimitExceededError,
    APIError, BrokerConnectionError, RateLimitError, AuthenticationError,
    AnalysisError, InsufficientDataError, IndicatorCalculationError,
    ConfigurationError, MissingSecretError,
    SafetyError, PanicModeActiveError, DailyLossLimitError
)


class TestExceptions(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_base_exception(self):
        """Test base AntigravityError."""
        print("\n🧪 Test: Base Exception...")
        err = AntigravityError("Test error", code="TEST")
        
        self.assertEqual(err.message, "Test error")
        self.assertEqual(err.code, "TEST")
        
        d = err.to_dict()
        self.assertTrue(d["error"])
        self.assertEqual(d["code"], "TEST")
        print("   ✅ Base exception works!")
    
    def test_insufficient_balance(self):
        """Test InsufficientBalanceError."""
        print("\n🧪 Test: InsufficientBalanceError...")
        err = InsufficientBalanceError(required=1000, available=500, symbol="EURUSD")
        
        self.assertEqual(err.code, "INSUFFICIENT_BALANCE")
        self.assertIn("1000", err.message)
        self.assertIn("500", err.message)
        
        d = err.to_dict()
        self.assertEqual(d["details"]["required"], 1000)
        print("   ✅ InsufficientBalanceError works!")
    
    def test_trade_execution_error(self):
        """Test TradeExecutionError."""
        print("\n🧪 Test: TradeExecutionError...")
        err = TradeExecutionError(symbol="EURUSD", side="buy", reason="Market closed")
        
        self.assertEqual(err.code, "TRADE_EXECUTION_FAILED")
        self.assertIn("EURUSD", err.message)
        self.assertIn("BUY", err.message)
        print("   ✅ TradeExecutionError works!")
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        print("\n🧪 Test: RateLimitError...")
        err = RateLimitError(service="Groq", retry_after=60)
        
        self.assertEqual(err.code, "RATE_LIMIT_EXCEEDED")
        self.assertIn("60", err.message)
        print("   ✅ RateLimitError works!")
    
    def test_insufficient_data_error(self):
        """Test InsufficientDataError."""
        print("\n🧪 Test: InsufficientDataError...")
        err = InsufficientDataError(required=100, available=50, indicator="SMA")
        
        self.assertEqual(err.code, "INSUFFICIENT_DATA")
        self.assertIn("SMA", err.message)
        print("   ✅ InsufficientDataError works!")
    
    def test_panic_mode_error(self):
        """Test PanicModeActiveError."""
        print("\n🧪 Test: PanicModeActiveError...")
        err = PanicModeActiveError()
        
        self.assertEqual(err.code, "PANIC_MODE_ACTIVE")
        self.assertIn("Panic", err.message)
        print("   ✅ PanicModeActiveError works!")
    
    def test_telegram_format(self):
        """Test Telegram formatting."""
        print("\n🧪 Test: Telegram Format...")
        err = BrokerConnectionError(broker="Capital.com", reason="Timeout")
        
        tg = err.to_telegram()
        self.assertIn("❌", tg)
        self.assertIn("<b>", tg)
        self.assertIn("BROKER_CONNECTION_ERROR", tg)
        print("   ✅ Telegram format works!")
    
    def test_exception_hierarchy(self):
        """Test exception inheritance."""
        print("\n🧪 Test: Exception Hierarchy...")
        
        # Trading hierarchy
        self.assertTrue(issubclass(InsufficientBalanceError, TradingError))
        self.assertTrue(issubclass(TradingError, AntigravityError))
        
        # API hierarchy
        self.assertTrue(issubclass(RateLimitError, APIError))
        self.assertTrue(issubclass(APIError, AntigravityError))
        
        print("   ✅ Exception hierarchy correct!")
    
    def test_catching_by_base_class(self):
        """Test catching specific exceptions by base class."""
        print("\n🧪 Test: Catching by Base Class...")
        
        try:
            raise InsufficientBalanceError(1000, 500)
        except TradingError as e:
            self.assertEqual(e.code, "INSUFFICIENT_BALANCE")
        
        try:
            raise RateLimitError("Groq")
        except APIError as e:
            self.assertEqual(e.code, "RATE_LIMIT_EXCEEDED")
        
        print("   ✅ Base class catching works!")


if __name__ == "__main__":
    print("=" * 60)
    print("    EXCEPTION TESTS")
    print("=" * 60)
    
    unittest.main(verbosity=0)
