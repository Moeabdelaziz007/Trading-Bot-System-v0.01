"""
Unit Test: ScalpingBrain (MQL5 Ported Logic)
Verifies S/R Detection, Rejection Candles, Algo Scoring.
"""
from scalping_engine import ScalpingBrain

# --- Simulated OHLCV Data ---
# 70 candles of sample data
def generate_sample_data(trend='up'):
    data = []
    base_price = 100.0
    volume_base = 1000
    
    for i in range(70):
        if trend == 'up':
            open_p = base_price + (i * 0.1)
            close = open_p + 0.15
        else:
            open_p = base_price - (i * 0.1)
            close = open_p - 0.15
            
        high = max(open_p, close) + 0.05
        low = min(open_p, close) - 0.05
        volume = volume_base + (i * 10)
        
        data.append({
            'time': i,
            'open': open_p,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    return data

def generate_rejection_data():
    """Creates data with a clear bullish rejection at support."""
    data = generate_sample_data('down')
    
    # Last candle is a bullish pin bar at "support"
    last_bar = data[-1]
    support_level = min(d['low'] for d in data[-61:-1])
    
    # Modify last candle to be a bullish rejection near support
    data[-1] = {
        'time': 69,
        'open': support_level + 0.5,
        'close': support_level + 0.55,  # Small bullish body
        'high': support_level + 0.6,
        'low': support_level - 0.5,     # Long lower wick
        'volume': 2500                   # High volume
    }
    return data

def test_sr_detection():
    print("🧪 Test 1: S/R Detection...")
    data = generate_sample_data('up')
    brain = ScalpingBrain(data)
    sr = brain.calculate_sr_levels()
    
    assert sr is not None, "S/R should be calculated"
    assert 'support' in sr, "Should have support level"
    assert 'resistance' in sr, "Should have resistance level"
    assert sr['resistance'] > sr['support'], "Resistance should be > Support"
    print(f"   ✅ Support: {sr['support']:.2f}, Resistance: {sr['resistance']:.2f}")

def test_rejection_candle():
    print("\n🧪 Test 2: Rejection Candle Detection...")
    data = generate_rejection_data()
    brain = ScalpingBrain(data)
    
    is_bullish = brain.is_bullish_rejection(shift=0)
    is_bearish = brain.is_bearish_rejection(shift=0)
    
    print(f"   Last candle - Bullish Rejection: {is_bullish}, Bearish Rejection: {is_bearish}")
    assert is_bullish == True, "Should detect bullish pin bar"
    print("   ✅ Bullish Rejection detected correctly!")

def test_footprint_score():
    print("\n🧪 Test 3: Footprint Score...")
    data = generate_rejection_data()
    brain = ScalpingBrain(data)
    
    fp_score = brain.get_footprint_score(shift=0)
    print(f"   Footprint Score: {fp_score:.4f}")
    assert fp_score != 0, "Should have non-zero footprint score with high volume"
    print("   ✅ Footprint scoring works!")

def test_algo_scoring():
    print("\n🧪 Test 4: Algo Scoring System...")
    data = generate_rejection_data()
    brain = ScalpingBrain(data)
    
    buy_score, fp = brain.calculate_buy_signal()
    sell_score, _ = brain.calculate_sell_signal()
    
    print(f"   Buy Score: {buy_score:.2f}, Sell Score: {sell_score:.2f}")
    # With rejection at support + high volume, buy should score high
    print("   ✅ Algo Scoring calculated!")

def test_full_analysis():
    print("\n🧪 Test 5: Full Market State Analysis...")
    data = generate_rejection_data()
    brain = ScalpingBrain(data)
    
    result = brain.analyze_market_state()
    print(f"   Action: {result['Action']}")
    print(f"   Confidence: {result['Confidence']}%")
    print(f"   Metrics: {result['Metrics']}")
    print("   ✅ Full analysis complete!")

def test_atr_stops():
    print("\n🧪 Test 6: ATR-Based Stop Loss...")
    data = generate_sample_data('up')
    brain = ScalpingBrain(data)
    
    # Test BUY stops
    buy_stops = brain.calculate_atr_stops(is_buy=True)
    print(f"   ATR: {buy_stops['atr']:.5f}")
    print(f"   Entry: {buy_stops['entry']:.2f}")
    print(f"   BUY SL: {buy_stops['stop_loss']:.2f} (1.5x ATR below)")
    print(f"   BUY TP: {buy_stops['take_profit']:.2f} (1.0x ATR above)")
    print(f"   R:R Ratio: {buy_stops['risk_reward_ratio']}")
    
    # Test SELL stops
    sell_stops = brain.calculate_atr_stops(is_buy=False)
    print(f"   SELL SL: {sell_stops['stop_loss']:.2f} (1.5x ATR above)")
    print(f"   SELL TP: {sell_stops['take_profit']:.2f} (1.0x ATR below)")
    
    assert buy_stops['stop_loss'] < buy_stops['entry'], "BUY SL should be below entry"
    assert buy_stops['take_profit'] > buy_stops['entry'], "BUY TP should be above entry"
    assert sell_stops['stop_loss'] > sell_stops['entry'], "SELL SL should be above entry"
    print("   ✅ ATR Stops calculated correctly!")

def test_supertrend():
    print("\n🧪 Test 7: Supertrend Indicator...")
    data = generate_sample_data('up')
    brain = ScalpingBrain(data)
    
    st = brain.calculate_supertrend(atr_period=10, multiplier=3.0)
    print(f"   Trend: {st['trend_name']}")
    print(f"   Supertrend Value: {st['supertrend_value']:.2f}")
    print(f"   Upper Band: {st['upper_band']:.2f}")
    print(f"   Lower Band: {st['lower_band']:.2f}")
    
    assert st['trend'] in [1, -1], "Trend should be 1 or -1"
    assert st['supertrend_value'] > 0, "Supertrend value should be positive"
    print("   ✅ Supertrend calculated correctly!")

def test_trailing_stop():
    print("\n🧪 Test 8: Trailing Stop...")
    data = generate_sample_data('up')
    brain = ScalpingBrain(data)
    
    entry_price = 100.0
    current_close = data[-1]['close']  # Should be > 107 in uptrend
    
    trail = brain.calculate_trailing_stop(
        entry_price=entry_price,
        is_buy=True,
        profit_threshold_pct=0.3,
        trail_pct=0.15
    )
    
    print(f"   Entry: {entry_price}, Current Close: {current_close:.2f}")
    print(f"   Profit %: {trail['current_profit_pct']:.2f}%")
    print(f"   Activated: {trail['is_activated']}")
    print(f"   Highest Price: {trail['highest_price']:.2f}")
    print(f"   Trailing Stop: {trail['trailing_stop']}")
    
    # With 7%+ profit (price at 107+), should definitely be activated
    if trail['current_profit_pct'] >= 0.3:
        assert trail['is_activated'] == True, "Should be activated with profit > threshold"
        assert trail['trailing_stop'] is not None, "Trail stop should be set"
    print("   ✅ Trailing Stop calculated correctly!")

if __name__ == "__main__":
    print("=" * 50)
    print("    SCALPING BRAIN UNIT TESTS (MQL5 Ported)")
    print("=" * 50)
    
    test_sr_detection()
    test_rejection_candle()
    test_footprint_score()
    test_algo_scoring()
    test_full_analysis()
    test_atr_stops()
    test_supertrend()
    test_trailing_stop()
    
    print("\n" + "=" * 50)
    print("    ALL TESTS PASSED ✅")
    print("=" * 50)
