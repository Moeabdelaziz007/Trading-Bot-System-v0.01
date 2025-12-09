"""
⏰ AXIOM SCHEDULER WORKER
The Heartbeat - Cron Jobs, Queues & Orchestration

Responsibilities:
- Dynamic Cron (Smart Scheduling)
- Queue Consumer (Trade/Broadcast)
- Agent Dispatch (Logic Layer)
- R2 Archiving
"""

import json
from datetime import datetime
from js import fetch

# Import Queue Consumer logic
# Renamed to consumer to avoid stdlib collision
from consumer import queue

# ==========================================
# 💾 R2 DATA LAKE
# ==========================================

async def fetch_market_data(env, symbols: list):
    """
    Fetch latest candles from brokers/Logic for archiving.
    """
    all_candles = {}
    
    # In production, we'd call the Brain or Broker directly.
    # For now, we mock a simple fetch or call the Brain if available.
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

async def save_candles_to_r2(env, symbol: str, candles: list):
    """
    Store candles in R2 with date-based partitioning.
    """
    now = datetime.utcnow()
    key = f"candles/{symbol}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}.json"

    try:
        # Get existing data if any (Optimistic: assume append needed)
        existing = await env.MARKET_ARCHIVE.get(key)
        all_candles = candles

        if existing:
            existing_data = json.loads(await existing.text())
            existing_timestamps = {c['timestamp'] for c in existing_data}
            new_candles = [c for c in candles if c['timestamp'] not in existing_timestamps]
            all_candles = existing_data + new_candles

        await env.MARKET_ARCHIVE.put(key, json.dumps(all_candles))
        return {"status": "saved", "count": len(all_candles)}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ==========================================
# 🧠 DYNAMIC CRON LOGIC (Task 2)
# ==========================================

def calculate_atr(candles, period=14):
    """Calculate Average True Range from candles"""
    if not candles or len(candles) < period + 1:
        return 0.0

    true_ranges = []
    for i in range(1, len(candles)):
        high = float(candles[i].get('high', 0))
        low = float(candles[i].get('low', 0))
        prev_close = float(candles[i-1].get('close', 0))

        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        true_ranges.append(tr)

    return sum(true_ranges[-period:]) / period if true_ranges else 0.0

async def calculate_atr_and_toggle_mode(env):
    """
    Calculate Volatility (ATR) and toggle Turbo Mode.
    If Volatility > Threshold -> Turbo Mode = TRUE
    """
    try:
        # 1. Fetch reference data (e.g. BTCUSD for volatility proxy)
        response = await env.TRADING_BRAIN.fetch(
            f"/api/candles?symbol=BTCUSD&limit=20"
        )
        data = await response.json()
        candles = data.get('candles', [])

        if not candles:
            return {"status": "no_data"}

        # 2. Calculate ATR
        atr = calculate_atr(candles)
        current_price = float(candles[-1].get('close', 1))
        atr_percent = (atr / current_price) * 100

        # 3. Determine Threshold (e.g., 0.5% ATR is high volatility for 5m candles)
        VOLATILITY_THRESHOLD = 0.5

        # 4. Toggle Flag
        new_state = "FALSE"
        if atr_percent > VOLATILITY_THRESHOLD:
            new_state = "TRUE"

        # Only write if changed to save KV writes
        current_state = await env.BRAIN_MEMORY.get("AEXI_VOLATILITY_FLAG")
        if current_state != new_state:
            await env.BRAIN_MEMORY.put("AEXI_VOLATILITY_FLAG", new_state)
            print(f"🔄 MODE CHANGED: {current_state} -> {new_state} (ATR: {atr_percent:.2f}%)")

        return {"atr": atr, "atr_pct": atr_percent, "mode": new_state}

    except Exception as e:
        return {"error": str(e)}

async def should_run_execution(env, current_minute):
    """
    Decide if we should run based on Volatility Mode.
    """
    try:
        volatility_flag = await env.BRAIN_MEMORY.get("AEXI_VOLATILITY_FLAG")

        if volatility_flag == "TRUE":
            # Turbo Mode: Every minute
            return True
        else:
            # Sleepy Mode: Every 5 minutes
            return current_minute % 5 == 0
    except:
        # Default safety
        return current_minute % 5 == 0


# ==========================================
# 🤖 AGENT DISPATCHERS
# ==========================================

async def dispatch_logic(env, endpoint):
    """Helper to call the Logic Brain."""
    try:
        response = await env.TRADING_BRAIN.fetch(f"/api/{endpoint}", {
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
    Cron Trigger Handler with Smart Scheduling.
    """
    now = datetime.utcnow()
    current_minute = now.minute
    
    results = {"timestamp": now.isoformat(), "actions": []}
    
    # 1. ALWAYS RUN: Risk Guardian & Data Archiving
    # Risk Check
    risk_result = await dispatch_logic(env, "risk-check")
    results["actions"].append({"agent": "RiskGuardian", "result": risk_result})
    
    # R2 Archiving (Restored)
    watchlist = ["BTCUSD", "EURUSD"]
    candles_data = await fetch_market_data(env, watchlist)
    for symbol, candles in candles_data.items():
        if candles:
            save_result = await save_candles_to_r2(env, symbol, candles)
            results["actions"].append({"agent": "R2Archive", "symbol": symbol, "result": save_result})

    # Update Volatility Flag (Auto-Toggle)
    # We run this every minute to ensure we catch volatility spikes quickly
    atr_result = await calculate_atr_and_toggle_mode(env)
    results["actions"].append({"agent": "VolatilityScanner", "result": atr_result})
    
    # 2. SMART SCHEDULING: Execution Logic
    should_run = await should_run_execution(env, current_minute)
    
    if should_run:
        # Dispatch Scalper
        scalper_result = await dispatch_logic(env, "run-scalper")
        results["actions"].append({"agent": "Scalper", "result": scalper_result})

        # Dispatch Journalist (Every 15 min)
        if current_minute % 15 == 0:
            journalist_result = await dispatch_logic(env, "run-journalist")
            results["actions"].append({"agent": "Journalist", "result": journalist_result})

    # 3. HOURLY TASKS
    if current_minute == 0:
        strategist_result = await dispatch_logic(env, "run-strategist")
        results["actions"].append({"agent": "Strategist", "result": strategist_result})

    # Log to KV for debugging
    await env.BRAIN_MEMORY.put(
        f"cron:log:{now.isoformat()}",
        json.dumps(results),
        expirationTtl=3600
    )
    
    return results

# Expose handlers
# on_scheduled is picked up automatically by 'index.py' main
# queue is imported from consumer.py
