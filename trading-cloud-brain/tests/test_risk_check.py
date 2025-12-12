import sys
from unittest.mock import MagicMock, AsyncMock
import unittest
import asyncio
import os

# Mock js module before importing backend.logic.index
sys.modules['js'] = MagicMock()
sys.modules['js'].Response = MagicMock()
sys.modules['js'].Headers = MagicMock()
sys.modules['js'].fetch = AsyncMock()

# Now we can import the module
sys.path.append(os.path.join(os.getcwd(), 'trading-cloud-brain'))

# We need to ensure we can import the module even if it has relative imports or specific environment needs
# The file `backend/logic/index.py` is stand-alone enough given our mocks.
from backend.logic.index import check_risk

class TestRiskCheck(unittest.TestCase):
    def setUp(self):
        self.env = MagicMock()
        self.mock_kv = AsyncMock()
        self.env.BRAIN_MEMORY = self.mock_kv
        self.mock_db = MagicMock()
        self.env.TRADING_DB = self.mock_db

    def test_check_risk_panic_mode(self):
        """Test that panic_mode=true triggers CRITICAL risk and kill switch."""
        async def run_test():
            # Setup
            self.mock_kv.get.side_effect = lambda key: "true" if key == "panic_mode" else None

            # Action
            result = await check_risk(self.env)

            # Assert
            self.assertEqual(result["risk"], "CRITICAL")
            self.assertTrue(result["kill_switch"])
            self.assertIn("Kill switch activated via KV (panic_mode)", result["details"])

        asyncio.run(run_test())

    def test_check_risk_news_lockdown(self):
        """Test that news_lockdown=true triggers HIGH risk."""
        async def run_test():
            # Setup
            self.mock_kv.get.side_effect = lambda key: "true" if key == "news_lockdown" else None

            # Action
            result = await check_risk(self.env)

            # Assert
            self.assertEqual(result["risk"], "HIGH")
            self.assertFalse(result["kill_switch"])
            self.assertIn("News Lockdown Active", result["details"])

        asyncio.run(run_test())

    def test_check_risk_ok(self):
        """Test that no flags triggers OK status."""
        async def run_test():
            # Setup
            self.mock_kv.get.return_value = None

            # Mock get_positions returning empty list (via D1 mock)
            # check_risk calls get_positions which calls env.TRADING_DB.prepare().all()
            mock_result = MagicMock()
            mock_result.results = []

            mock_query = MagicMock()
            mock_query.all = AsyncMock(return_value=mock_result)

            self.env.TRADING_DB.prepare.return_value = mock_query

            # Action
            result = await check_risk(self.env)

            # Assert
            self.assertEqual(result["risk"], "OK")
            self.assertFalse(result["kill_switch"])
            self.assertEqual(result["details"], [])

        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main()
