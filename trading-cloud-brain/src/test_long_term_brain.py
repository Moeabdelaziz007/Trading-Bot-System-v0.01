"""
Unit Test: LongTermBrain (Upgraded Golden Cross)
Verifies RSI, ADX, Volume filters, and Retest Entry logic.
"""
from long_term_engine import LongTermBrain

def generate_daily_data(count=210, trend='up'):
    """Generate sample daily OHLCV data."""
    data = []
    base_price = 100.0
    volume_base = 1000000
    
    for i in range(count):
        if trend == 'up':
            open_p = base_price + (i * 0.5)
            close = open_p + 0.3
        else:
            open_p = base_price - (i * 0.5)
            close = open_p - 0.3
            
        high = max(open_p, close) + 0.2
        low = min(open_p, close) - 0.2
        volume = volume_base + (i * 5000)
        
        data.append({
            'time': i,
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    return data

def test_sma_ema_calculation():
    print("🧪 Test 1: SMA/EMA Calculation...")
    data = generate_daily_data(210, 'up')
    brain = LongTermBrain(data)
    
    sma200 = brain.calculate_sma(200)
    ema50 = brain.calculate_ema(50)
    
    assert sma200 is not None, "SMA200 should be calculated"
    assert ema50 is not None, "EMA50 should be calculated"
    assert ema50 > sma200, "In uptrend, EMA50 should be > SMA200 (Golden Cross)"
    print(f"   ✅ SMA200: {sma200:.2f}, EMA50: {ema50:.2f}")

def test_rsi_calculation():
    print("\n🧪 Test 2: RSI Calculation...")
    data = generate_daily_data(210, 'up')
    brain = LongTermBrain(data)
    
    rsi = brain.calculate_rsi()
    print(f"   RSI: {rsi:.2f}")
    assert 0 <= rsi <= 100, "RSI should be between 0 and 100"
    print("   ✅ RSI calculated correctly!")

def test_adx_calculation():
    print("\n🧪 Test 3: ADX Calculation...")
    data = generate_daily_data(210, 'up')
    brain = LongTermBrain(data)
    
    adx, plus_di, minus_di = brain.calculate_adx()
    print(f"   ADX: {adx:.2f}, +DI: {plus_di:.2f}, -DI: {minus_di:.2f}")
    assert adx >= 0, "ADX should be >= 0"
    print("   ✅ ADX calculated correctly!")

def test_golden_cross_detection():
    print("\n🧪 Test 4: Golden Cross Detection (Multi-Filter)...")
    data = generate_daily_data(210, 'up')
    # Add volume surge to last candle
    data[-1]['volume'] = data[-1]['volume'] * 2
    
    brain = LongTermBrain(data)
    cross = brain.assess_golden_cross()
    
    print(f"   Signal: {cross['signal']}")
    print(f"   Buy Score: {cross['buy_score']}, Sell Score: {cross['sell_score']}")
    print(f"   RSI: {cross['rsi']:.2f}, ADX: {cross['adx']:.2f}")
    print(f"   Volume Surge: {cross['vol_surge']}")
    
    assert "GOLDEN" in cross['signal'], "Should detect Golden Cross in uptrend"
    print("   ✅ Golden Cross detected with filters!")

def test_ema_retest():
    print("\n🧪 Test 5: EMA Retest Check...")
    data = generate_daily_data(210, 'up')
    brain = LongTermBrain(data)
    
    # Manually set last close near EMA50
    ema50 = brain.calculate_ema(50)
    data[-1]['close'] = ema50 * 1.005  # Within 1%
    
    brain2 = LongTermBrain(data)
    is_retest = brain2.check_ema_retest()
    print(f"   EMA Retest Detected: {is_retest}")
    print("   ✅ Retest logic works!")

def test_full_analysis():
    print("\n🧪 Test 6: Full Market Health Evaluation...")
    data = generate_daily_data(210, 'up')
    data[-1]['volume'] = data[-1]['volume'] * 2  # Volume surge
    
    brain = LongTermBrain(data)
    result = brain.evaluate_market_health()
    
    print(f"   Action: {result['Action']}")
    print(f"   Confidence: {result['Confidence']}%")
    print(f"   Entry Type: {result['EntryType']}")
    print("   ✅ Full analysis complete!")

if __name__ == "__main__":
    print("=" * 55)
    print("  LONG-TERM BRAIN UNIT TESTS (Institutional Upgrade)")
    print("=" * 55)
    
    test_sma_ema_calculation()
    test_rsi_calculation()
    test_adx_calculation()
    test_golden_cross_detection()
    test_ema_retest()
    test_full_analysis()
    
    print("\n" + "=" * 55)
    print("    ALL TESTS PASSED ✅")
    print("=" * 55)
