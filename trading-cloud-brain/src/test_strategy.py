import unittest
import sys
from unittest.mock import MagicMock

sys.modules['js'] = MagicMock()

from strategy import TradingBrain

class TestTradingBrain(unittest.TestCase):
    
    def setUp(self):
        self.data = []
        for i in range(250):
            self.data.append({
                'open': 100 + i * 0.1,
                'high': 101 + i * 0.1,
                'low': 99 + i * 0.1,
                'close': 100 + i * 0.1,
                'volume': 1000 + i * 5
            })
    
    def test_scalp_mode(self):
        brain = TradingBrain(self.data[:60], mode="SCALP")
        result = brain.analyze()
        self.assertIn('signal', result)
        self.assertIn('atr', result)
        print(f"✅ Scalp signal: {result['signal']}")
    
    def test_swing_mode(self):
        brain = TradingBrain(self.data, mode="SWING")
        result = brain.analyze()
        self.assertIn('signal', result)
        self.assertIn('rsi', result)
        print(f"✅ Swing signal: {result['signal']}")
    
    def test_indicators(self):
        brain = TradingBrain(self.data, mode="SCALP")
        atr = brain._calc_atr()
        rsi = brain._calc_rsi()
        self.assertIsNotNone(atr)
        self.assertGreater(rsi, 0)
        print(f"✅ ATR: {atr:.5f}, RSI: {rsi:.2f}")

if __name__ == '__main__':
    unittest.main()
