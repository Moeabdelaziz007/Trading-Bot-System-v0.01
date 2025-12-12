import asyncio
from backend.app.core.decision_engine import DecisionEngine

async def test_censor_brain():
    print("🧠 Testing The Censor Brain (Regime Filter)...\n")
    
    engine = DecisionEngine()
    
    # Mock Account for Risk Checks
    account = {"equity": 10000.0, "balance": 10000.0}

    # Scene 1: Choppy Market (Low Volatility, flat)
    choppy_data = [{'close': 100 + (i%2)*0.1, 'volume': 1000} for i in range(50)]
    print(f"📉 Scenario 1: Choppy Data (Close: {choppy_data[-1]['close']})")
    decision = await engine.evaluate_trade("BTC/USD", choppy_data, account)
    print(f"   -> Decision: {decision['action']}")
    print(f"   -> Reason: {decision['reason']}")
    print("-" * 40)
    
    # Scene 2: High Volatility (Big swings)
    high_vol_data = [{'close': 100 + (i%2)*5.0, 'volume': 5000} for i in range(50)]
    print(f"⚡ Scenario 2: High Volatility (Close: {high_vol_data[-1]['close']})")
    decision = await engine.evaluate_trade("BTC/USD", high_vol_data, account)
    print(f"   -> Decision: {decision['action']}")
    print(f"   -> Reason: {decision['reason']}")
    print("-" * 40)
    
    # Scene 3: Trending Market (Steady climb) -> Should Trigger 1% Risk Cap Calculation
    trending_data = [{'close': 100 + i*0.5, 'volume': 2000} for i in range(50)]
    print(f"🚀 Scenario 3: Trending Data (Close: {trending_data[-1]['close']})")
    decision = await engine.evaluate_trade("BTC/USD", trending_data, account)
    print(f"   -> Decision: {decision['action']}")
    print(f"   -> Reason: {decision['reason']}")
    print(f"   -> Quantity: {decision.get('quantity', 'N/A')} (Risk Cap: {decision.get('max_risk_cap', 'N/A')})")
    print("-" * 40)

if __name__ == "__main__":
    asyncio.run(test_censor_brain())
