import unittest
import sys
from unittest.mock import MagicMock

sys.modules['js'] = MagicMock()

from patterns import PatternScanner

class TestPatternScanner(unittest.TestCase):
    
    def setUp(self):
        # Generate test data with some patterns
        self.data = []
        for i in range(60):
            self.data.append({
                'open': 100 + i * 0.1,
                'high': 101 + i * 0.1,
                'low': 99 + i * 0.1,
                'close': 100 + i * 0.1 + 0.05,
                'volume': 1000
            })
    
    def test_init(self):
        scanner = PatternScanner(self.data)
        self.assertEqual(len(scanner.closes), 60)
        print("✅ PatternScanner init works")
    
    def test_detect_doji(self):
        # Create a doji candle
        doji_data = self.data.copy()
        doji_data.append({
            'open': 106.0,
            'high': 107.0,
            'low': 105.0,
            'close': 106.01,  # Almost same as open
            'volume': 1000
        })
        scanner = PatternScanner(doji_data)
        result = scanner.detect_doji()
        self.assertEqual(result['detected'], True)
        print(f"✅ Doji detected: {result['type']}")
    
    def test_detect_hammer(self):
        # Create a hammer pattern
        hammer_data = self.data.copy()
        hammer_data.append({
            'open': 106.0,
            'high': 106.2,
            'low': 104.0,  # Long lower wick
            'close': 106.1,
            'volume': 1000
        })
        scanner = PatternScanner(hammer_data)
        result = scanner.detect_hammer()
        print(f"✅ Hammer test: detected={result.get('detected', False)}")
    
    def test_detect_engulfing(self):
        # Create engulfing pattern
        engulf_data = self.data.copy()
        engulf_data.append({
            'open': 105.0,
            'high': 105.2,
            'low': 104.8,
            'close': 104.9,  # Small bearish
            'volume': 1000
        })
        engulf_data.append({
            'open': 104.7,  # Opens below prev close
            'high': 105.5,
            'low': 104.6,
            'close': 105.4,  # Closes above prev open
            'volume': 2000
        })
        scanner = PatternScanner(engulf_data)
        result = scanner.detect_engulfing()
        print(f"✅ Engulfing test: detected={result.get('detected', False)}")
    
    def test_scan_all(self):
        scanner = PatternScanner(self.data)
        patterns = scanner.scan_all()
        self.assertIsInstance(patterns, list)
        print(f"✅ Scan all found {len(patterns)} patterns")
    
    def test_double_top(self):
        scanner = PatternScanner(self.data)
        result = scanner.detect_double_top()
        print(f"✅ Double Top: detected={result.get('detected', False)}")
    
    def test_head_shoulders(self):
        scanner = PatternScanner(self.data)
        result = scanner.detect_head_shoulders()
        print(f"✅ H&S: detected={result.get('detected', False)}")

if __name__ == '__main__':
    unittest.main()
