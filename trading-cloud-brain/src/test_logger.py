"""
🧪 Unit Tests for Logger
Tests the structured logging functionality.
"""

import unittest
from io import StringIO
import sys
from core import Logger, LogLevel, log, get_logger


class TestLogger(unittest.TestCase):
    """Test Logger class."""
    
    def setUp(self):
        """Capture stdout for testing."""
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output
    
    def tearDown(self):
        """Restore stdout."""
        sys.stdout = self.original_stdout
    
    def get_output(self):
        """Get captured output."""
        return self.held_output.getvalue()
    
    def test_log_levels(self):
        """Test different log levels."""
        print("\n🧪 Test: Log Levels...", file=self.original_stdout)
        logger = Logger("test", LogLevel.DEBUG)
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warn("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        output = self.get_output()
        self.assertIn("DEBUG", output)
        self.assertIn("INFO", output)
        self.assertIn("WARN", output)
        self.assertIn("ERROR", output)
        self.assertIn("CRITICAL", output)
        print("   ✅ Log levels work!", file=self.original_stdout)
    
    def test_log_level_filtering(self):
        """Test that logs below level are filtered."""
        print("\n🧪 Test: Level Filtering...", file=self.original_stdout)
        logger = Logger("test", LogLevel.WARN)
        
        logger.debug("Should not appear")
        logger.info("Should not appear")
        logger.warn("Should appear")
        
        output = self.get_output()
        self.assertNotIn("DEBUG", output)
        self.assertNotIn("INFO", output)
        self.assertIn("WARN", output)
        print("   ✅ Level filtering works!", file=self.original_stdout)
    
    def test_context_in_logs(self):
        """Test that kwargs appear in logs."""
        print("\n🧪 Test: Context in Logs...", file=self.original_stdout)
        logger = Logger("test", LogLevel.DEBUG)
        
        logger.info("Trade executed", symbol="EURUSD", price=1.0850)
        
        output = self.get_output()
        self.assertIn("EURUSD", output)
        self.assertIn("1.085", output)
        print("   ✅ Context logging works!", file=self.original_stdout)
    
    def test_trade_signal(self):
        """Test trade signal logging."""
        print("\n🧪 Test: Trade Signal...", file=self.original_stdout)
        logger = Logger("test", LogLevel.DEBUG)
        
        logger.trade_signal("EURUSD", "BUY", 85)
        
        output = self.get_output()
        self.assertIn("Signal", output)
        self.assertIn("BUY", output)
        self.assertIn("EURUSD", output)
        print("   ✅ Trade signal logging works!", file=self.original_stdout)
    
    def test_trade_executed(self):
        """Test trade executed logging."""
        print("\n🧪 Test: Trade Executed...", file=self.original_stdout)
        logger = Logger("test", LogLevel.DEBUG)
        
        logger.trade_executed("EURUSD", "buy", 1000, 1.0850)
        
        output = self.get_output()
        self.assertIn("Trade Executed", output)
        self.assertIn("BUY", output)
        print("   ✅ Trade executed logging works!", file=self.original_stdout)
    
    def test_twin_turbo(self):
        """Test Twin-Turbo logging."""
        print("\n🧪 Test: Twin-Turbo...", file=self.original_stdout)
        logger = Logger("test", LogLevel.DEBUG)
        
        logger.twin_turbo(85.5, 72.3, True)
        
        output = self.get_output()
        self.assertIn("Twin-Turbo", output)
        self.assertIn("AEXI", output)
        self.assertIn("Dream", output)
        print("   ✅ Twin-Turbo logging works!", file=self.original_stdout)
    
    def test_global_logger(self):
        """Test global logger instance."""
        print("\n🧪 Test: Global Logger...", file=self.original_stdout)
        
        self.assertIsInstance(log, Logger)
        test_logger = get_logger("custom", LogLevel.DEBUG)
        self.assertEqual(test_logger.name, "custom")
        print("   ✅ Global logger works!", file=self.original_stdout)


if __name__ == "__main__":
    print("=" * 60)
    print("    LOGGER TESTS")
    print("=" * 60)
    
    # Run with regular output
    unittest.main(verbosity=0)
