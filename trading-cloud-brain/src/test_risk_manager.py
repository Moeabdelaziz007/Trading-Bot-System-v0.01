"""
Standalone Unit tests for Kelly Criterion and Chaos Factor
(Avoids importing Cloudflare Worker-specific modules)
"""

import random
import math

# ==================================================
# 📊 KELLY CRITERION (Copy from risk_manager.py)
# ==================================================

def calculate_kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> dict:
    """
    Kelly Criterion for optimal position sizing.
    Formula: f* = (p * b - q) / b
    """
    if avg_loss <= 0 or win_rate < 0 or win_rate > 1:
        return {"kelly_fraction": 0, "error": "Invalid inputs"}
    
    p = win_rate
    q = 1 - p
    b = avg_win / avg_loss  # Payout ratio
    
    # Kelly Formula: f* = (p * b - q) / b
    kelly = (p * b - q) / b if b > 0 else 0
    
    # Safety caps
    half_kelly = kelly / 2
    quarter_kelly = kelly / 4
    safe_kelly = min(half_kelly, 0.025)
    
    return {
        "full_kelly": round(kelly * 100, 2),
        "half_kelly": round(half_kelly * 100, 2),
        "quarter_kelly": round(quarter_kelly * 100, 2),
        "recommended_pct": round(safe_kelly * 100, 2),
        "payout_ratio": round(b, 2),
        "edge": round((p * b - q) * 100, 2)
    }

# ==================================================
# 🎲 CHAOS FACTOR (Copy from risk_manager.py)
# ==================================================

def apply_chaos_factor(value: float, chaos_level: str = "medium") -> dict:
    """
    Apply human-like randomization to values to avoid pattern detection.
    """
    variance_map = {
        "low": 0.005,      # ±0.5%
        "medium": 0.02,    # ±2%
        "high": 0.05       # ±5%
    }
    variance = variance_map.get(chaos_level, 0.02)
    
    # 1. Value Dithering (Gaussian noise)
    dither = random.gauss(0, variance)
    chaotic_value = value * (1 + dither)
    
    # 2. Precision Variance (random decimal places)
    decimals = random.choice([2, 3, 4, 5])
    chaotic_value = round(chaotic_value, decimals)
    
    # 3. Weibull Delay (human-like reaction time)
    weibull_delay = random.weibullvariate(0.5, 1.5)
    human_delay = max(0.15, weibull_delay)
    
    return {
        "original": value,
        "chaotic": chaotic_value,
        "dither_pct": round(dither * 100, 3),
        "precision": decimals,
        "human_delay_sec": round(human_delay, 3),
        "chaos_level": chaos_level
    }

# ==================================================
# 🧪 TESTS
# ==================================================

def test_kelly_criterion():
    print("\n🧪 Test 1: Kelly Criterion Position Sizing...")
    
    # Test case: 60% win rate, avg win $150, avg loss $100
    result = calculate_kelly_fraction(
        win_rate=0.60,
        avg_win=150,
        avg_loss=100
    )
    
    print(f"   Win Rate: 60%")
    print(f"   Avg Win: $150, Avg Loss: $100")
    print(f"   Payout Ratio: {result['payout_ratio']}")
    print(f"   Full Kelly: {result['full_kelly']}%")
    print(f"   Half Kelly: {result['half_kelly']}%")
    print(f"   Quarter Kelly: {result['quarter_kelly']}%")
    print(f"   Recommended: {result['recommended_pct']}%")
    print(f"   Edge: {result['edge']}%")
    
    assert result['payout_ratio'] == 1.5, "Payout ratio should be 1.5"
    assert result['full_kelly'] > 0, "Kelly should be positive with edge"
    assert result['half_kelly'] < result['full_kelly'], "Half Kelly < Full Kelly"
    print("   ✅ Kelly Criterion calculated correctly!")

def test_kelly_no_edge():
    print("\n🧪 Test 2: Kelly with No Edge...")
    
    # 50% win rate, 1:1 payout = no edge
    result = calculate_kelly_fraction(
        win_rate=0.50,
        avg_win=100,
        avg_loss=100
    )
    
    print(f"   Win Rate: 50%, Payout: 1:1")
    print(f"   Full Kelly: {result['full_kelly']}%")
    print(f"   Edge: {result['edge']}%")
    
    assert result['full_kelly'] == 0, "No edge = 0 Kelly"
    print("   ✅ Correctly returns 0 for no edge!")

def test_kelly_negative_edge():
    print("\n🧪 Test 3: Kelly with Negative Edge...")
    
    # 40% win rate, 1:1 payout = negative edge
    result = calculate_kelly_fraction(
        win_rate=0.40,
        avg_win=100,
        avg_loss=100
    )
    
    print(f"   Win Rate: 40%, Payout: 1:1")
    print(f"   Full Kelly: {result['full_kelly']}%")
    print(f"   Edge: {result['edge']}%")
    
    assert result['full_kelly'] < 0, "Negative edge = negative Kelly (don't bet!)"
    print("   ✅ Correctly shows negative Kelly for losing strategy!")

def test_chaos_factor():
    print("\n🧪 Test 4: Chaos Factor Value Dithering...")
    
    original_value = 100.0
    results = []
    
    for i in range(5):
        result = apply_chaos_factor(original_value, chaos_level="medium")
        results.append(result)
        if i == 0:
            print(f"   Original: {result['original']}")
            print(f"   Chaotic: {result['chaotic']}")
            print(f"   Dither: {result['dither_pct']}%")
            print(f"   Precision: {result['precision']} decimals")
            print(f"   Human Delay: {result['human_delay_sec']}s")
    
    # Check that values are different (randomized)
    chaotic_values = [r['chaotic'] for r in results]
    unique_values = len(set(chaotic_values))
    
    print(f"   Unique values in 5 runs: {unique_values}")
    assert unique_values >= 2, "Should produce varied outputs"
    print("   ✅ Chaos Factor produces varied human-like values!")

def test_weibull_distribution():
    print("\n🧪 Test 5: Weibull Delay Distribution...")
    
    delays = []
    for _ in range(100):
        result = apply_chaos_factor(100.0)
        delays.append(result['human_delay_sec'])
    
    avg_delay = sum(delays) / len(delays)
    min_delay = min(delays)
    max_delay = max(delays)
    
    print(f"   Avg Delay: {avg_delay:.3f}s")
    print(f"   Min Delay: {min_delay:.3f}s")
    print(f"   Max Delay: {max_delay:.3f}s")
    
    assert min_delay >= 0.15, "Min should be physiological floor (150ms)"
    assert avg_delay < 2.0, "Avg should be reasonable"
    print("   ✅ Weibull delays look human-like!")

if __name__ == "__main__":
    print("=" * 55)
    print("    RISK MANAGER UNIT TESTS (Kelly + Chaos)")
    print("=" * 55)
    
    test_kelly_criterion()
    test_kelly_no_edge()
    test_kelly_negative_edge()
    test_chaos_factor()
    test_weibull_distribution()
    
    print("\n" + "=" * 55)
    print("    ALL TESTS PASSED ✅")
    print("=" * 55)
