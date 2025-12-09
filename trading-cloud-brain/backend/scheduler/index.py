"""
⏰ AXIOM SCHEDULER WORKER
The Heartbeat - Cron Jobs & R2 Archiving

Responsibilities:
- Save candles to R2 every minute
- Dispatch Scalper every 5 minutes
- Dispatch Journalist every 15 minutes
- Dispatch Strategist every hour
- Risk Guardian checks every minute
"""

import json
from datetime import datetime
from js import fetch

# ==========================================
# 💾 R2 DATA LAKE
# ==========================================

async def save_candles_to_r2(env, symbol: str, candles: list):
    """
    Store candles in R2 with date-based partitioning.
    Zero egress cost for reads!
    """
    now = datetime.utcnow()
    key = f"candles/{symbol}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}.json"
    
    try:
        # Get existing data if any
        existing = await env.MARKET_ARCHIVE.get(key)
        if existing:
            existing_data = json.loads(await existing.text())
            # Append new candles, avoiding duplicates
            existing_timestamps = {c['timestamp'] for c in existing_data}
            new_candles = [c for c in candles if c['timestamp'] not in existing_timestamps]
            all_candles = existing_data + new_candles
        else:
            all_candles = candles
        
        # Save to R2
        await env.MARKET_ARCHIVE.put(key, json.dumps(all_candles))
        return {"status": "saved", "key": key, "count": len(all_candles)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def fetch_market_data(env, symbols: list):
    """
    Fetch latest candles from brokers.
    """
    all_candles = {}
    
    for symbol in symbols:
        try:
            # Call Trading Brain for data
            response = await env.TRADING_BRAIN.fetch(
                f"/api/candles?symbol={symbol}&limit=5"
            )
            data = await response.json()
            all_candles[symbol] = data.get('candles', [])
        except Exception as e:
            all_candles[symbol] = []
    
    return all_candles


# ==========================================
# 🤖 AGENT DISPATCHERS
# ==========================================

async def dispatch_scalper(env):
    """Dispatch the 5-minute Scalper strategy."""
    try:
        response = await env.TRADING_BRAIN.fetch("/api/run-scalper", {
            "method": "POST"
        })
        return await response.json()
    except Exception as e:
        return {"error": str(e)}


async def dispatch_journalist(env):
    """Dispatch the 15-minute News Agent."""
    try:
        response = await env.TRADING_BRAIN.fetch("/api/run-journalist", {
            "method": "POST"
        })
        return await response.json()
    except Exception as e:
        return {"error": str(e)}


async def dispatch_strategist(env):
    """Dispatch the hourly Strategist Agent."""
    try:
        response = await env.TRADING_BRAIN.fetch("/api/run-strategist", {
            "method": "POST"
        })
        return await response.json()
    except Exception as e:
        return {"error": str(e)}


async def check_risk_guardian(env):
    """Run Risk Guardian checks every minute."""
    try:
        response = await env.TRADING_BRAIN.fetch("/api/risk-check", {
            "method": "POST"
        })
        return await response.json()
    except Exception as e:
        return {"error": str(e)}


# ==========================================
# ⏰ MAIN CRON HANDLER
# ==========================================

async def on_scheduled(event, env, ctx):
    """
    Cron Trigger Handler.
    Runs every minute with intelligent dispatch.
    """
    now = datetime.utcnow()
    current_minute = now.minute
    current_hour = now.hour
    
    results = {"timestamp": now.isoformat(), "actions": []}
    
    # 1. RISK GUARDIAN (Every minute)
    risk_result = await check_risk_guardian(env)
    results["actions"].append({"agent": "RiskGuardian", "result": risk_result})
    
    # 2. R2 ARCHIVING (Every minute)
    watchlist = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
    candles_data = await fetch_market_data(env, watchlist)
    for symbol, candles in candles_data.items():
        if candles:
            save_result = await save_candles_to_r2(env, symbol, candles)
            results["actions"].append({"agent": "R2Archive", "symbol": symbol, "result": save_result})
    
    # 3. SCALPER (Every 5 minutes)
    if current_minute % 5 == 0:
        scalper_result = await dispatch_scalper(env)
        results["actions"].append({"agent": "Scalper", "result": scalper_result})
    
    # 4. JOURNALIST (Every 15 minutes)
    if current_minute % 15 == 0:
        journalist_result = await dispatch_journalist(env)
        results["actions"].append({"agent": "Journalist", "result": journalist_result})
    
    # 5. STRATEGIST (Every hour)
    if current_minute == 0:
        strategist_result = await dispatch_strategist(env)
        results["actions"].append({"agent": "Strategist", "result": strategist_result})
    
    # Log results to KV for debugging
    await env.BRAIN_MEMORY.put(
        f"cron:log:{now.isoformat()}",
        json.dumps(results),
        expirationTtl=86400  # 24 hours
    )
    
    return results
