import unittest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime, timedelta
import sys
import os

# Add src to path to import the class
# Path structure:
# trading-cloud-brain/tests/test_durable_session_logic.py
# trading-cloud-brain/src/objects/durable_trade_session.py
# trading-cloud-brain/src/core/logger.py

# We need to add 'trading-cloud-brain' to sys.path so 'src.objects' works, 
# OR add 'trading-cloud-brain/src' to sys.path and adjust imports in the test.
# The code in durable_trade_session.py uses 'from src.core.logger', which implies 
# that the root context is 'trading-cloud-brain'.

# Add the project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock js module before importing 
sys.modules['js'] = MagicMock()
sys.modules['js'].Response = MagicMock()
sys.modules['js'].JSON = MagicMock()

# Import from src.objects (since we added project root)
from src.objects.durable_trade_session import DurableTradeSession

class MockRequest:
    def __init__(self, url, method="POST", body=None, headers=None):
        self.url = url
        self.method = method
        self._body = body or {}
        self.headers = headers or {}
        
    async def json(self):
        return self._body

class TestDurableTradeSession(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_state = MagicMock()
        self.mock_state.id = "test-session-id"
        self.mock_state.storage.sql = MagicMock()
        self.mock_env = MagicMock()
        
        # Setup Logger mock to avoid cluttering output
        with patch('src.objects.durable_trade_session.Logger') as MockLogger:
            self.session = DurableTradeSession(self.mock_state, self.mock_env)
            self.session.log = MagicMock()

    async def test_validation_failure(self):
        """Test that missing fields return 400."""
        req = MockRequest(
            "http://worker/positions-open", 
            body={"id": "123"} # Missing fields
        )
        response = await self.session.fetch(req)
        # Verify response is 400 (mock response doesn't hold status, but we can check the call)
        # In our implementation `_json_response` creates a Response.
        # We need to check what arguments Response.new was called with.
        
        # We can't easily inspect the 'Response.new' result without a real Response object.
        # But we can verify the mock call arguments.
        calls = sys.modules['js'].Response.new.call_args_list
        last_call = calls[-1]
        args, kwargs = last_call
        self.assertEqual(kwargs['status'], 400)
        
    async def test_circuit_half_open_logic(self):
        """Test transitions: CLOSED -> OPEN -> HALF_OPEN."""
        
        # 1. Simulate getting circuit state that IS OPEN but OLD
        # Last failure was 31 seconds ago (timeout is 30s)
        old_failure = (datetime.utcnow() - timedelta(seconds=31)).isoformat()
        
        # Mock database returning an OPEN circuit
        mock_row = MagicMock()
        mock_row.name = "alpha"
        mock_row.state = "OPEN"
        mock_row.failure_count = 5
        mock_row.last_failure_at = old_failure
        mock_row.last_success_at = None
        
        self.session.sql.exec.return_value.one.return_value = mock_row
        
        req = MockRequest("http://worker/circuit-get", body={"name": "alpha"})
        
        # We need to intercept the response body to check "state": "HALF_OPEN"
        # Since Response.new returns a mock, we inspect the arguments passed to it.
        await self.session.fetch(req)
        
        calls = sys.modules['js'].Response.new.call_args_list
        last_call = calls[-1]
        response_body_json = last_call[0][0] # First arg is body string
        response_data = json.loads(response_body_json)
        
        self.assertEqual(response_data['state'], "HALF_OPEN", "Should interpret expired OPEN as HALF_OPEN")

    async def test_circuit_trip_logic(self):
        """Test failure counting and tripping."""
        # Simulate a failure update
        req = MockRequest(
            "http://worker/circuit-update", 
            body={"name": "beta", "event": "failure", "threshold": 2}
        )
        
        # Mock current state as CLOSED with 1 failure
        mock_row = MagicMock()
        mock_row.failure_count = 1
        mock_row.state = "CLOSED"
        
        # The first exec is UPDATE/INSERT, but inside it reads first.
        # Actually in `_handle_circuit_update` implementation:
        # It runs SELECT first if failure.
        
        def side_effect(query, *args):
            # Debug print to see what queries are actually called
            # print(f"SQL Exec: {query}")
            if "SELECT failure_count" in query:
                cursor = MagicMock()
                cursor.one.return_value = mock_row
                return cursor
            return MagicMock() # For INSERT/UPDATE
            
        self.session.sql.exec.side_effect = side_effect
        
        await self.session.fetch(req)
        
        # Verify that the INSERT/UPDATE set state to OPEN (since 1+1 >= 2)
        # We look for the call that has "OPEN" in the args
        found_open_update = False
        for call in self.session.sql.exec.call_args_list:
            args = call[0]
            if "OPEN" in args:
                found_open_update = True
                break
        
        self.assertTrue(found_open_update, "Should update state to OPEN after threshold reached")

if __name__ == '__main__':
    unittest.main()
