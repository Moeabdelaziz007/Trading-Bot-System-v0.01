"""
🔮 AXIOM DREAM ENGINE WORKER
The Chaos Math Processor

Responsibilities:
- AEXI Protocol (Exhaustion Detection)
- Dream Machine (Chaos/Entropy Analysis)
- Pattern Recognition
- Fractal Dimension Calculation

This worker handles all CPU-intensive math without blocking the main brain.
"""

from js import Response, Headers
import json
import math
from datetime import datetime

# ==========================================
# 🌐 RESPONSE HELPERS
# ==========================================

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json"
    }.items())
    return Response.new(json.dumps(data), status=status, headers=headers)


# ==========================================
# 📊 AEXI PROTOCOL (Market Exhaustion)
# ==========================================

def calculate_aexi(candles: list) -> dict:
    """
    AEXI Protocol - Adaptive Exhaustion Index
    Uses Z-Score and velocity factors to detect trend exhaustion.
    """
    if len(candles) < 20:
        return {"signal": "NO_DATA", "score": 0}
    
    closes = [c.get('close', c.get('c', 0)) for c in candles]
    
    # Mean and Standard Deviation
    mean = sum(closes) / len(closes)
    variance = sum((x - mean) ** 2 for x in closes) / len(closes)
    std = math.sqrt(variance) if variance > 0 else 1
    
    # Z-Score of last price
    z_score = (closes[-1] - mean) / std if std > 0 else 0
    
    # Velocity (rate of change)
    velocity = (closes[-1] - closes[-5]) / closes[-5] * 100 if closes[-5] != 0 else 0
    
    # Exhaustion Score
    exhaustion = abs(z_score) * abs(velocity) / 10
    
    # Signal
    if z_score > 2 and velocity > 0:
        signal = "SELL"  # Overbought
    elif z_score < -2 and velocity < 0:
        signal = "BUY"   # Oversold
    else:
        signal = "NEUTRAL"
    
    return {
        "signal": signal,
        "z_score": round(z_score, 4),
        "velocity": round(velocity, 4),
        "exhaustion": round(exhaustion, 4)
    }


# ==========================================
# 🌀 DREAM MACHINE (Chaos Analysis)
# ==========================================

def calculate_entropy(candles: list) -> float:
    """
    Shannon Entropy - Measures market randomness.
    High entropy = unpredictable market.
    """
    if len(candles) < 10:
        return 0
    
    changes = []
    closes = [c.get('close', c.get('c', 0)) for c in candles]
    
    for i in range(1, len(closes)):
        if closes[i-1] != 0:
            pct_change = (closes[i] - closes[i-1]) / closes[i-1]
            # Bucket into categories
            if pct_change > 0.01:
                changes.append("UP_BIG")
            elif pct_change > 0:
                changes.append("UP")
            elif pct_change < -0.01:
                changes.append("DOWN_BIG")
            elif pct_change < 0:
                changes.append("DOWN")
            else:
                changes.append("FLAT")
    
    # Calculate probabilities
    from collections import Counter
    counts = Counter(changes)
    total = len(changes)
    
    entropy = 0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    
    return round(entropy, 4)


def calculate_fractal_dimension(candles: list) -> float:
    """
    Approximate Fractal Dimension using box-counting method.
    Higher value = more chaotic/complex market.
    """
    if len(candles) < 20:
        return 1.0
    
    closes = [c.get('close', c.get('c', 0)) for c in candles]
    
    # Normalize to 0-1 range
    min_price = min(closes)
    max_price = max(closes)
    range_price = max_price - min_price if max_price != min_price else 1
    normalized = [(p - min_price) / range_price for p in closes]
    
    # Calculate path length
    path_length = 0
    for i in range(1, len(normalized)):
        dx = 1 / len(normalized)  # Time step
        dy = abs(normalized[i] - normalized[i-1])
        path_length += math.sqrt(dx**2 + dy**2)
    
    # Fractal dimension approximation
    if path_length > 0:
        fd = 1 + math.log(path_length) / math.log(len(closes))
        return round(min(2, max(1, fd)), 4)
    
    return 1.0


def analyze_chaos(candles: list, mode: str = "SCALP") -> dict:
    """
    Full Chaos Analysis combining AEXI and Dream Machine.
    """
    aexi = calculate_aexi(candles)
    entropy = calculate_entropy(candles)
    fractal = calculate_fractal_dimension(candles)
    
    # Chaos Score (0-100)
    chaos_score = min(100, (entropy / 2.5) * 50 + (fractal - 1) * 50)
    
    # Confidence based on chaos
    # Lower chaos = higher confidence in signals
    confidence = max(0, 100 - chaos_score) if aexi["signal"] != "NEUTRAL" else 0
    
    # Mode adjustments
    if mode == "SWING":
        # Swing needs longer confirmation
        if abs(aexi["z_score"]) < 2.5:
            aexi["signal"] = "NEUTRAL"
    
    return {
        "signal": aexi["signal"],
        "confidence": round(confidence, 2),
        "aexi": aexi,
        "chaos": {
            "entropy": entropy,
            "fractal_dimension": fractal,
            "chaos_score": round(chaos_score, 2),
            "market_state": "CHAOTIC" if chaos_score > 60 else "TRENDING" if chaos_score < 30 else "MIXED"
        },
        "mode": mode,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==========================================
# 🚀 MAIN ROUTER
# ==========================================

async def on_fetch(request, env):
    """Internal API Router for Math Operations."""
    url = str(request.url)
    method = str(request.method)
    
    try:
        # Analysis endpoint
        if "/api/analyze" in url and method == "POST":
            body = json.loads(await request.text())
            candles = body.get("candles", [])
            mode = body.get("mode", "SCALP")
            
            result = analyze_chaos(candles, mode)
            
            # Cache result
            cache_key = f"analysis:{body.get('symbol', 'unknown')}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
            await env.RESULTS_KV.put(cache_key, json.dumps(result), expirationTtl=300)
            
            return json_response(result)
        
        # Get cached result
        if "/api/result" in url:
            params = {}
            if "?" in url:
                params = dict(p.split("=") for p in url.split("?")[1].split("&"))
            result_id = params.get("id", "")
            
            cached = await env.RESULTS_KV.get(result_id)
            if cached:
                return json_response(json.loads(cached))
            return json_response({"error": "Result not found"}, 404)
        
        # Health check
        if "/api/health" in url:
            return json_response({"status": "OK", "engine": "Dream Machine v2.0"})
        
        return json_response({"error": "Unknown endpoint"}, 404)
        
    except Exception as e:
        return json_response({"error": str(e)}, 500)


# ==========================================
# 📨 QUEUE CONSUMER (for async jobs)
# ==========================================

async def on_queue_batch(messages, env, ctx):
    """
    Process async math jobs from queue.
    """
    results = []
    
    for msg in messages:
        try:
            task = json.loads(msg.body)
            
            if task.get("type") == "chaos_analysis":
                result = analyze_chaos(task["candles"], task.get("mode", "SCALP"))
                
                # Store result
                await env.RESULTS_KV.put(
                    f"result:{task['id']}",
                    json.dumps(result),
                    expirationTtl=300
                )
                
                results.append({"id": task["id"], "status": "done"})
        except Exception as e:
            results.append({"id": task.get("id", "unknown"), "error": str(e)})
    
    return {"processed": len(results), "results": results}
