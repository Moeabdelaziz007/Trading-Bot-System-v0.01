import unittest
import sys
import json
from unittest.mock import MagicMock, AsyncMock

sys.modules['js'] = MagicMock()

from state import StateManager

class MockKV:
    """Mock KV storage for testing."""
    def __init__(self):
        self.store = {}
    
    async def get(self, key):
        return self.store.get(key)
    
    async def put(self, key, value, **kwargs):
        self.store[key] = value
    
    async def delete(self, key):
        if key in self.store:
            del self.store[key]
    
    async def list(self, prefix=""):
        return {"keys": [{"name": k} for k in self.store if k.startswith(prefix)]}

class MockEnv:
    def __init__(self):
        self.BRAIN_MEMORY = MockKV()

class TestStateManager(unittest.TestCase):
    
    def test_init(self):
        env = MockEnv()
        state = StateManager(env)
        self.assertIsNotNone(state.kv)
        print("✅ StateManager init works")
    
    def test_acquire_lock(self):
        import asyncio
        env = MockEnv()
        state = StateManager(env)
        
        async def test():
            # First lock should succeed
            result1 = await state.acquire_lock("EURUSD")
            self.assertTrue(result1)
            
            # Second lock should fail (already locked)
            result2 = await state.acquire_lock("EURUSD")
            self.assertFalse(result2)
            
            # Release and try again
            await state.release_lock("EURUSD")
            result3 = await state.acquire_lock("EURUSD")
            self.assertTrue(result3)
            
            print("✅ Symbol locking works")
        
        asyncio.run(test())
    
    def test_record_trade(self):
        import asyncio
        env = MockEnv()
        state = StateManager(env)
        
        async def test():
            trade = {
                "symbol": "EURUSD",
                "side": "BUY",
                "amount": 0.1,
                "entry_price": 1.0850
            }
            trade_id = await state.record_trade(trade)
            self.assertTrue(trade_id.startswith("EURUSD_"))
            
            # Check open trades
            trades = await state.get_open_trades()
            self.assertEqual(len(trades), 1)
            self.assertEqual(trades[0]['symbol'], "EURUSD")
            
            print("✅ Trade recording works")
        
        asyncio.run(test())
    
    def test_cron_lock(self):
        import asyncio
        env = MockEnv()
        state = StateManager(env)
        
        async def test():
            # First cron should get lock
            result1 = await state.acquire_cron_lock("scalper_5min")
            self.assertTrue(result1)
            
            # Second cron should fail
            result2 = await state.acquire_cron_lock("scalper_5min")
            self.assertFalse(result2)
            
            # Release and try again
            await state.release_cron_lock("scalper_5min")
            result3 = await state.acquire_cron_lock("scalper_5min")
            self.assertTrue(result3)
            
            print("✅ Cron locking works")
        
        asyncio.run(test())
    
    def test_has_open_position(self):
        import asyncio
        env = MockEnv()
        state = StateManager(env)
        
        async def test():
            # No positions initially
            has_pos = await state.has_open_position("EURUSD")
            self.assertFalse(has_pos)
            
            # Record a trade
            await state.record_trade({
                "symbol": "EURUSD",
                "side": "BUY",
                "entry_price": 1.0850
            })
            
            # Now should have position
            has_pos = await state.has_open_position("EURUSD")
            self.assertTrue(has_pos)
            
            print("✅ Position check works")
        
        asyncio.run(test())

if __name__ == '__main__':
    unittest.main()
