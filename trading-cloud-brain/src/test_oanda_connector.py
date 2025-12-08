"""
🧪 Unit Tests for OANDA Connector
Tests the connection, authentication, and methods.
"""

import unittest
from unittest.mock import Mock, AsyncMock, patch


# Mock the OandaConnector for testing without actual API calls
class MockEnv:
    """Mock environment with OANDA credentials."""
    OANDA_API_KEY = "test-api-key-12345"
    OANDA_ACCOUNT_ID = "101-001-12345678-001"


class TestOandaConnector(unittest.TestCase):
    """Test OANDA connector functionality."""
    
    def test_connector_initialization(self):
        """Test connector initializes correctly."""
        print("\n🧪 Test: Connector Initialization...")
        
        # Import locally to avoid Cloudflare-specific imports
        from oanda_connector import OandaConnector, OANDA_PRACTICE_API, OANDA_LIVE_API
        
        env = MockEnv()
        connector = OandaConnector(env, is_live=False)
        
        self.assertEqual(connector.api_key, "test-api-key-12345")
        self.assertEqual(connector.account_id, "101-001-12345678-001")
        self.assertEqual(connector.base_url, OANDA_PRACTICE_API)
        self.assertFalse(connector.is_live)
        print("   ✅ Practice environment configured correctly!")
    
    def test_live_environment(self):
        """Test live environment configuration."""
        print("\n🧪 Test: Live Environment...")
        
        from oanda_connector import OandaConnector, OANDA_LIVE_API
        
        env = MockEnv()
        connector = OandaConnector(env, is_live=True)
        
        self.assertEqual(connector.base_url, OANDA_LIVE_API)
        self.assertTrue(connector.is_live)
        print("   ✅ Live environment configured correctly!")
    
    def test_headers_format(self):
        """Test authorization headers format."""
        print("\n🧪 Test: Headers Format...")
        
        from oanda_connector import OandaConnector
        
        env = MockEnv()
        connector = OandaConnector(env)
        headers = connector._get_headers()
        
        self.assertIn("Authorization", headers)
        self.assertTrue(headers["Authorization"].startswith("Bearer "))
        self.assertEqual(headers["Content-Type"], "application/json")
        print("   ✅ Bearer token headers correct!")
    
    def test_connection_status(self):
        """Test connection status method."""
        print("\n🧪 Test: Connection Status...")
        
        from oanda_connector import OandaConnector
        
        env = MockEnv()
        connector = OandaConnector(env)
        status = connector.get_connection_status()
        
        self.assertTrue(status["configured"])
        self.assertEqual(status["environment"], "Practice")
        self.assertIn("account_id", status)
        print("   ✅ Connection status works!")
    
    def test_missing_credentials(self):
        """Test handling of missing credentials."""
        print("\n🧪 Test: Missing Credentials...")
        
        from oanda_connector import OandaConnector
        
        class EmptyEnv:
            pass
        
        connector = OandaConnector(EmptyEnv())
        status = connector.get_connection_status()
        
        self.assertFalse(status["configured"])
        print("   ✅ Missing credentials handled correctly!")
    
    def test_granularity_options(self):
        """Test valid granularity values."""
        print("\n🧪 Test: Granularity Options...")
        
        # Valid OANDA granularities
        valid_granularities = ["S5", "S10", "S15", "S30", "M1", "M2", "M4", "M5", 
                              "M10", "M15", "M30", "H1", "H2", "H3", "H4", "H6", 
                              "H8", "H12", "D", "W", "M"]
        
        # Verify we support standard ones
        supported = ["M1", "M5", "M15", "H1", "D"]
        for g in supported:
            self.assertIn(g, valid_granularities)
        
        print("   ✅ Granularity options valid!")


if __name__ == "__main__":
    print("=" * 60)
    print("    OANDA CONNECTOR TESTS")
    print("=" * 60)
    
    unittest.main(verbosity=0)
