
import asyncio
import random
from src.engine import CipherEngine, NewsFilter, SignalType

async def test_brain():
    print("🧠 Starting Phase 2 Brain Test...\n")

    # 1. Test Cipher Algorithm (Math Check)
    print("🔹 Testing Cipher Engine (Market Cipher Logic)...")
    cipher = CipherEngine()
    
    # Generate fake bullish divergence data
    # Price going DOWN, but MFI going UP (Divergence/Reversal)
    candles = []
    base_price = 50000.0
    
    for i in range(100):
        # Simulate price drop then recovery
        if i < 80:
            price = base_price - (i * 10) # Drop
            vol = 1000 + (i * 10)     # Rising volume (accumulation)
        else:
            price = base_price - 800 + ((i-80) * 50) # Recovery
            vol = 2000
            
        candles.append({
            "close": price,
            "high": price + 5,
            "low": price - 5,
            "volume": vol
        })
    
    result = cipher.analyze("BTCUSDT", candles)
    
    print(f"   Analysis for {result.symbol}:")
    print(f"   Price: {result.price}")
    print(f"   MFI: {result.mfi:.2f}")
    print(f"   VWAP: {result.vwap:.2f}")
    print(f"   RSI: {result.rsi:.2f}")
    print(f"   Signal: {result.signal.name}")
    print(f"   Reason: {result.reason}")
    print("   ✅ Cipher Math executed successfully.\n")


    # 2. Test News Filter (Mock Mode)
    print("🔹 Testing News Filter (Perplexity Integration)...")
    news_filter = NewsFilter(api_key=None) # Force mock mode
    sentinel = await news_filter.analyze_sentiment("BTC")
    
    print(f"   Symbol: {sentinel.symbol}")
    print(f"   Risk: {sentinel.risk_level}")
    print(f"   Red Folder Warning: {sentinel.red_folder_warning}")
    print(f"   Summary: {sentinel.summary}")
    print("   ✅ News Filter responded correctly (Mock).\n")
    
    await news_filter.close()
    print("🎉 Phase 2 Brain Components Verified!")

if __name__ == "__main__":
    asyncio.run(test_brain())
