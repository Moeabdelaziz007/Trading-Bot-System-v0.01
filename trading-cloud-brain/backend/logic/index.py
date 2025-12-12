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

def map_symbol_to_yahoo(symbol: str):
    """Map common symbols to Yahoo Finance tickers."""
    mapping = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "JPY=X",
        "AUDUSD": "AUDUSD=X",
        "USDCAD": "CAD=X",
        "XAUUSD": "XAUUSD=X",
        "BTCUSD": "BTC-USD",
        "ETHUSD": "ETH-USD",
        "SPY": "SPY",
        "QQQ": "QQQ",
        "IWM": "IWM"
    }
    return mapping.get(symbol, symbol)


async def fetch_yahoo_candles(symbol: str, interval: str, range_param: str):
    """Fetch candles from Yahoo Finance."""
    y_symbol = map_symbol_to_yahoo(symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{y_symbol}?interval={interval}&range={range_param}"

    try:
        # Yahoo requires User-Agent
        resp = await fetch(url, {
            "method": "GET",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
            }
        })
        
        if resp.status != 200:
            return []

        data = await resp.json()
        if "chart" not in data or "result" not in data["chart"] or not data["chart"]["result"]:
            return []

        result = data["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        indicators = result.get("indicators", {}).get("quote", [{}])[0]

        opens = indicators.get("open", [])
        highs = indicators.get("high", [])
        lows = indicators.get("low", [])
        closes = indicators.get("close", [])
        volumes = indicators.get("volume", [])
        
        candles = []
        for i in range(len(timestamps)):
            # Filter out missing data (None values)
            if closes[i] is None:
                continue

            candles.append({
                "timestamp": timestamps[i],
                "open": opens[i] if opens[i] is not None else 0,
                "high": highs[i] if highs[i] is not None else 0,
                "low": lows[i] if lows[i] is not None else 0,
                "close": closes[i],
                "volume": volumes[i] if volumes[i] is not None else 0
            })
        return candles
    except Exception as e:
        return []


async def get_candles(env, symbol: str, limit: int = 100, interval: str = "1m"):
    """Fetch candles from R2 or broker fallback."""
    try:
        # Try R2 first (only for 1m data)
        if interval == "1m":
            now = datetime.utcnow()
            key = f"candles/{symbol}/{now.year}/{now.month:02d}/{now.day:02d}/{now.hour:02d}.json"
            cached = await env.MARKET_ARCHIVE.get(key)

            if cached:
                candles = json.loads(await cached.text())
                if len(candles) > 0:
                    return candles[-limit:]

        # Fallback to Yahoo Finance
        # Determine range based on interval and limit
        range_param = "1d"
        if interval == "1m":
            range_param = "1d" if limit < 1000 else "5d"
        elif interval == "1h":
            range_param = "5d" if limit < 100 else "1mo"
        elif interval == "1d":
            range_param = "2y" # Get 2 years to allow for 200 SMA calculation

        return await fetch_yahoo_candles(symbol, interval, range_param)

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
        # Use default interval="1m"
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
    """Hourly Deep Strategy Analysis (Long-term)."""
    watchlist = ["EURUSD", "GBPUSD", "BTCUSD", "ETHUSD", "SPY", "QQQ"]
    strategies = []

    for symbol in watchlist:
        # Fetch daily candles for long-term trends
        # We need at least 200 candles for SMA 200
        candles = await get_candles(env, symbol, limit=365, interval="1d")

        if len(candles) < 200:
            continue

        closes = [c["close"] for c in candles]
        current_price = closes[-1]

        # Calculate Indicators (Simple Moving Averages)
        # SMA 50
        sma_50 = sum(closes[-50:]) / 50
        # SMA 200
        sma_200 = sum(closes[-200:]) / 200

        # Analyze with Dream Engine (Market Regime)
        dream_analysis = {}
        try:
             # We send last 50 candles for Dream analysis to check *current* regime
             response = await env.DREAM_ENGINE.fetch("/api/analyze", {
                "method": "POST",
                "body": json.dumps({
                    "symbol": symbol,
                    "candles": candles[-50:],
                    "mode": "STRATEGIST"
                })
            })
             dream_analysis = await response.json()
        except:
            dream_analysis = {"signal": "UNKNOWN", "is_chaotic": True}

        # Strategy Logic
        signal = "NEUTRAL"
        confidence = 0

        # Trend Filter: Price relative to SMA 200
        trend = "BULLISH" if current_price > sma_200 else "BEARISH"

        # Golden Cross / Death Cross Condition
        # We check current state.
        golden_cross_active = sma_50 > sma_200

        # Regime Filter from Dream Engine
        # We want to trade when market is ORDERED (Low Chaos)
        is_chaotic = dream_analysis.get("is_chaotic", True)
        dream_signal = dream_analysis.get("signal", "NEUTRAL")

        # Logic:
        # 1. Bullish: Price > SMA200 AND SMA50 > SMA200 AND Not Chaotic
        # 2. Bearish: Price < SMA200 AND SMA50 < SMA200 AND Not Chaotic

        if not is_chaotic:
            if trend == "BULLISH" and golden_cross_active:
                signal = "BUY"
                confidence = 0.8
                # Boost confidence if Dream Engine also says TREND_FOLLOW
                if dream_signal == "TREND_FOLLOW":
                    confidence = 0.9
            elif trend == "BEARISH" and not golden_cross_active:
                signal = "SELL"
                confidence = 0.8
                if dream_signal == "TREND_FOLLOW":
                    confidence = 0.9

        strategies.append({
            "symbol": symbol,
            "signal": signal,
            "confidence": confidence,
            "market_regime": dream_analysis.get("regime", "UNKNOWN"),
            "trend": trend,
            "indicators": {
                "sma_50": round(sma_50, 4),
                "sma_200": round(sma_200, 4),
                "price": current_price
            },
            "timestamp": datetime.utcnow().isoformat()
        })

    return {
        "strategy": "Strategist",
        "analysis": strategies,
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_risk(env):
    """Risk Guardian checks."""
    risk_status = "OK"
    kill_switch = False
    reasons = []

    # 1. Check Kill Switch (KV)
    try:
        if hasattr(env, 'BRAIN_MEMORY'):
             panic = await env.BRAIN_MEMORY.get("panic_mode")
             if panic == "true":
                 risk_status = "CRITICAL"
                 kill_switch = True
                 reasons.append("Kill switch activated via KV (panic_mode)")
    except Exception as e:
        reasons.append(f"KV Check Failed: {str(e)}")

    # 2. Check News Lockdown (KV)
    try:
        if hasattr(env, 'BRAIN_MEMORY'):
             lockdown = await env.BRAIN_MEMORY.get("news_lockdown")
             if lockdown == "true":
                 risk_status = "HIGH" if risk_status != "CRITICAL" else risk_status
                 reasons.append("News Lockdown Active")
    except:
        pass

    # 3. Check Max Positions
    try:
        positions = await get_positions(env)
        MAX_POSITIONS = 5 # Example limit
        if len(positions) >= MAX_POSITIONS:
             risk_status = "HIGH" if risk_status != "CRITICAL" else risk_status
             reasons.append(f"Max positions exceeded ({len(positions)} >= {MAX_POSITIONS})")
    except Exception as e:
        reasons.append(f"Position Check Failed: {str(e)}")

    return {
        "risk": risk_status,
        "kill_switch": kill_switch,
        "details": reasons,
        "timestamp": datetime.utcnow().isoformat()
    }


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
