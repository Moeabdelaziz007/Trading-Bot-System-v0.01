"""
🧠 AXIOM TRADING BRAIN WORKER
The Core Logic Engine

Responsibilities:
- Trading strategies (Scalper, Swing, Strategist)
- Signal generation and validation
- Position management
- AI chat integration
- MCP Intelligence
"""

from js import Response, Headers, fetch
import json
from datetime import datetime

# ==========================================
# 🌐 CORS & RESPONSE HELPERS
# ==========================================

def json_response(data, status=200):
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }.items())
    return Response.new(json.dumps(data), status=status, headers=headers)


# ==========================================
# 📊 MARKET DATA
# ==========================================

async def get_candles(env, symbol: str, limit: int = 100):
    """Fetch candles from R2 or broker."""
    try:
        # Try R2 first (cached data)
        now = datetime.utcnow()
        key = f"candles/{symbol}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}.json"
        cached = await env.MARKET_ARCHIVE.get(key)
        
        if cached:
            candles = json.loads(await cached.text())
            return candles[-limit:]
        
        # Fallback to broker API
        # TODO: Implement broker fetch
        return []
    except Exception as e:
        return []


async def get_positions(env):
    """Get open positions from database."""
    try:
        result = await env.TRADING_DB.prepare(
            "SELECT * FROM positions WHERE status = 'OPEN'"
        ).all()
        return result.results if result else []
    except:
        return []


# ==========================================
# 🤖 TRADING STRATEGIES
# ==========================================

async def run_scalper(env):
    """5-minute Scalping Strategy."""
    watchlist = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
    signals = []
    
    for symbol in watchlist:
        candles = await get_candles(env, symbol, 300)
        if not candles:
            continue
        
        # Send to Dream Engine for chaos analysis
        try:
            response = await env.DREAM_ENGINE.fetch("/api/analyze", {
                "method": "POST",
                "body": json.dumps({
                    "symbol": symbol,
                    "candles": candles[-50:],
                    "mode": "SCALP"
                })
            })
            analysis = await response.json()
            
            if analysis.get("signal") not in ["NEUTRAL", "NO_DATA"]:
                signals.append({
                    "symbol": symbol,
                    "signal": analysis.get("signal"),
                    "confidence": analysis.get("confidence", 0),
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            pass
    
    return {"strategy": "Scalper", "signals": signals}


async def run_journalist(env):
    """15-minute News Analysis."""
    # TODO: Implement news fetching and sentiment analysis
    return {"strategy": "Journalist", "status": "pending"}


async def run_strategist(env):
    """Hourly Deep Strategy Analysis."""
    # TODO: Implement long-term strategy
    return {"strategy": "Strategist", "status": "pending"}


async def check_risk(env):
    """Risk Guardian checks."""
    # TODO: Implement risk checks
    return {"risk": "OK", "kill_switch": False}


# ==========================================
# 🧠 AI CHAT (MoE)
# ==========================================

async def handle_chat(env, message: str, user_id: str):
    """AI Chat using Groq."""
    groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
    if not groq_key:
        return {"error": "Groq API key not configured"}
    
    try:
        response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {groq_key}",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "model": "llama-3.1-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are Axiom, an AI trading assistant."},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 1000
            })
        })
        
        data = await response.json()
        return {
            "response": data["choices"][0]["message"]["content"],
            "model": "llama-3.1-70b"
        }
    except Exception as e:
        return {"error": str(e)}


# ==========================================
# 📡 MCP INTELLIGENCE
# ==========================================

async def get_mcp_signals(env):
    """Get latest AI signals from MCP."""
    try:
        result = await env.TRADING_DB.prepare(
            "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10"
        ).all()
        return result.results if result else []
    except:
        return []


async def get_dashboard(env):
    """Unified dashboard snapshot."""
    positions = await get_positions(env)
    signals = await get_mcp_signals(env)
    risk = await check_risk(env)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "positions": positions,
        "signals": signals,
        "risk": risk,
        "status": "ACTIVE"
    }


# ==========================================
# 🚀 MAIN ROUTER
# ==========================================

async def on_fetch(request, env):
    """Internal API Router."""
    url = str(request.url)
    method = str(request.method)
    
    try:
        # Dashboard
        if "/api/dashboard" in url:
            data = await get_dashboard(env)
            return json_response(data)
        
        # Positions
        if "/api/positions" in url:
            positions = await get_positions(env)
            return json_response({"positions": positions})
        
        # Candles
        if "/api/candles" in url:
            # Parse query params
            params = {}
            if "?" in url:
                params = dict(p.split("=") for p in url.split("?")[1].split("&"))
            symbol = params.get("symbol", "EURUSD")
            limit = int(params.get("limit", "100"))
            
            candles = await get_candles(env, symbol, limit)
            return json_response({"candles": candles})
        
        # MCP Signals
        if "/api/signals" in url or "/api/mcp" in url:
            signals = await get_mcp_signals(env)
            return json_response({"signals": signals})
        
        # Run Scalper
        if "/api/run-scalper" in url:
            result = await run_scalper(env)
            return json_response(result)
        
        # Run Journalist
        if "/api/run-journalist" in url:
            result = await run_journalist(env)
            return json_response(result)
        
        # Run Strategist
        if "/api/run-strategist" in url:
            result = await run_strategist(env)
            return json_response(result)
        
        # Risk Check
        if "/api/risk-check" in url:
            result = await check_risk(env)
            return json_response(result)
        
        # AI Chat
        if "/api/chat" in url and method == "POST":
            body = json.loads(await request.text())
            message = body.get("message", "")
            user_id = body.get("user_id", "anonymous")
            result = await handle_chat(env, message, user_id)
            return json_response(result)
        
        return json_response({"error": "Unknown endpoint"}, 404)
        
    except Exception as e:
        return json_response({"error": str(e)}, 500)
