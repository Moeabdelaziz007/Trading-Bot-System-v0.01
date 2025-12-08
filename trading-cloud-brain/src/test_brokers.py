import unittest
from unittest.mock import MagicMock
import sys

# Mock 'js' module for local testing
mock_js = MagicMock()
mock_js.fetch = MagicMock()
mock_js.Headers = MagicMock()
sys.modules['js'] = mock_js

# Mock Environment
class MockEnv:
    def __init__(self, broker="OANDA"):
        self.PRIMARY_BROKER = broker
        self.OANDA_API_KEY = "test_key"
        self.OANDA_ACCOUNT_ID = "test_id"
        self.CAPITAL_API_KEY = "test_cap_key"
        self.CAPITAL_EMAIL = "test@test.com"
        self.CAPITAL_PASSWORD = "pass"
        self.TRADING_MODE = "PAPER"

from brokers import BrokerGateway, OandaProvider, CapitalProvider

class TestBrokerGateway(unittest.TestCase):
    
    def test_gateway_oanda(self):
        env = MockEnv("OANDA")
        gateway = BrokerGateway(env)
        self.assertIsInstance(gateway.active_broker, OandaProvider)
        print("✅ Gateway selects OANDA correctly")
        
    def test_gateway_capital(self):
        env = MockEnv("CAPITAL")
        gateway = BrokerGateway(env)
        self.assertIsInstance(gateway.active_broker, CapitalProvider)
        print("✅ Gateway selects CAPITAL correctly")
        
    def test_oanda_init(self):
        env = MockEnv("OANDA")
        broker = OandaProvider(env)
        self.assertEqual(broker.name, "OANDA")
        print("✅ OandaProvider initializes correctly")
        
    def test_capital_init(self):
        env = MockEnv("CAPITAL")
        broker = CapitalProvider(env)
        self.assertEqual(broker.name, "CAPITAL")
        print("✅ CapitalProvider initializes correctly")

if __name__ == '__main__':
    unittest.main()
