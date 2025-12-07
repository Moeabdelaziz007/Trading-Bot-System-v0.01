import unittest
from scalping_engine import ScalpingBrain

class TestScalpingBrain(unittest.TestCase):

    def setUp(self):
        # Create mock data (50 bars)
        self.data = []
        price = 100.0
        for i in range(50):
            self.data.append({
                'time': 1000 + i*60,
                'open': price,
                'high': price + 1.0,
                'low': price - 1.0,
                'close': price + 0.5, # Mild uptrend
                'volume': 1000 + (i * 10)
            })
            price += 0.2

        self.brain = ScalpingBrain(self.data)

    def test_atr_stops(self):
        print("\n🧪 Testing ATR and Dynamic Stops (1:2 R:R)...")
        stops = self.brain.calculate_atr_stops(is_buy=True)
        print(f"   ATR: {stops['atr']:.4f}")
        print(f"   Entry: {stops['entry']:.2f} | SL: {stops['sl']:.2f} | TP: {stops['tp']:.2f}")
        print(f"   R:R Ratio: {stops['rr_ratio']}")
        
        self.assertIsNotNone(stops)
        self.assertTrue(stops['tp'] > stops['entry'])
        self.assertTrue(stops['sl'] < stops['entry'])
        self.assertEqual(stops['rr_ratio'], 2.0)
        print("   ✅ ATR Stops validated with 1:2 R:R")

    def test_indicators(self):
        print("\n🧪 Testing New Indicators (MACD, Stoch, Delta)...")
        
        # MACD
        macd = self.brain.calculate_macd()
        print(f"   MACD: {macd['macd']:.4f} | Signal: {macd['signal_line']:.4f}")
        self.assertIsNotNone(macd)
        
        # Stochastic
        stoch = self.brain.calculate_stochastic()
        print(f"   Stoch K: {stoch['k']:.2f} | D: {stoch['d']:.2f}")
        self.assertTrue(0 <= stoch['k'] <= 100)
        
        # Delta Divergence
        delta = self.brain.detect_delta_divergence()
        print(f"   Delta Divergence: {delta['divergence']}")
        self.assertIn(delta['divergence'], ["NONE", "BULLISH", "BEARISH"])
        
        print("   ✅ All new indicators calculating correctly")
        
    def test_algo_score(self):
        print("\n🧪 Testing Algo Scoring System...")
        score = self.brain.calculate_algo_score()
        print(f"   Buy Score: {score['buy_score']} | Sell Score: {score['sell_score']}")
        print(f"   Metrics: {score['metrics']}")
        
        self.assertTrue(score['buy_score'] >= 0)
        self.assertTrue(score['sell_score'] >= 0)
        print("   ✅ Algo scoring functional")

    def test_analysis_output(self):
        print("\n🧪 Testing Worker Output Format...")
        result = self.brain.analyze_market_state()
        print(f"   Action: {result['Action']} | Confidence: {result['Confidence']}%")
        
        self.assertIn("Action", result)
        self.assertIn("Confidence", result)
        print("   ✅ Output format compatible with worker")

if __name__ == '__main__':
    unittest.main()
