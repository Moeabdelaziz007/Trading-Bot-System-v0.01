import unittest
import sys
from unittest.mock import MagicMock

# Mock js module
sys.modules['js'] = MagicMock()

from intelligence import TwinTurbo

class TestTwinTurbo(unittest.TestCase):
    
    def setUp(self):
        # Generate sample data
        self.data = []
        for i in range(60):
            self.data.append({
                'open': 100 + i * 0.5,
                'high': 101 + i * 0.5,
                'low': 99 + i * 0.5,
                'close': 100 + i * 0.5,
                'volume': 1000 + i * 10
            })
    
    def test_init(self):
        turbo = TwinTurbo(self.data)
        self.assertEqual(len(turbo.closes), 60)
        print("✅ TwinTurbo init works")
    
    def test_aexi(self):
        turbo = TwinTurbo(self.data)
        aexi = turbo.get_aexi()
        self.assertIn('score', aexi)
        self.assertIn('signal', aexi)
        self.assertIn('components', aexi)
        print(f"✅ AEXI score: {aexi['score']}")
    
    def test_dream(self):
        turbo = TwinTurbo(self.data)
        dream = turbo.get_dream()
        self.assertIn('score', dream)
        self.assertIn('regime', dream)
        self.assertIn('components', dream)
        print(f"✅ Dream score: {dream['score']}")
    
    def test_analyze(self):
        turbo = TwinTurbo(self.data)
        result = turbo.analyze()
        self.assertIn('aexi', result)
        self.assertIn('dream', result)
        self.assertIn('combined_signal', result)
        self.assertIn('confidence', result)
        print(f"✅ Combined signal: {result['combined_signal']}")

if __name__ == '__main__':
    unittest.main()
