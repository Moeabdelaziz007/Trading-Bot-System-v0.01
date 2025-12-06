from js import Response, fetch, JSON
import json
import datetime

# ==========================================
# 🧠 DUAL-CORE BRAIN (Cloudflare Python Worker)
# ==========================================

# CORS Headers for all responses
CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type"
}

async def on_fetch(request, env):
    """
    Main request handler - routes to different endpoints
    """
    url = request.url
    method = request.method
    
    # Handle CORS preflight
    if method == "OPTIONS":
        return Response.new("", headers=CORS_HEADERS)
    
    # ============ API ROUTES ============
    
    # 1. CHAT ENDPOINT (Gemini)
    if method == "POST" and "api/chat" in url:
        return await handle_chat(request, env)
    
    # 2. TRADE ENDPOINT
    if method == "POST" and "api/trade" in url:
        return await handle_trade(request, env)
    
    # 3. MARKET DATA ENDPOINT
    if "api/market" in url:
        return await handle_market(request, env)
    
    # 4. STATUS ENDPOINT
    if "api/status" in url:
        return await handle_status(env)
    
    # 5. BRAIN STATUS
    if "api/brain" in url:
        return await handle_brain_status(env)
    
    # Default response
    return Response.new(json.dumps({
        "status": "online",
        "message": "Sentinel Brain Online 🟢",
        "endpoints": ["/api/chat", "/api/trade", "/api/market/{symbol}", "/api/status", "/api/brain"]
    }), headers=CORS_HEADERS)


async def handle_chat(request, env):
    """Chat with Gemini AI"""
    try:
        body = await request.json()
        user_msg = body.get("message", "")
        
        # Get strategy context from KV
        strategy_raw = await env.BRAIN_MEMORY.get("current_strategy")
        strategy = json.loads(strategy_raw) if strategy_raw else {"bias": "NEUTRAL"}
        
        # Call Gemini
        gemini_key = env.GEMINI_API_KEY
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
        
        prompt = f"""
        Role: Expert Trading Assistant 'Sentinel'.
        Strategy Bias: {strategy.get('bias')}
        User: {user_msg}
        
        Be concise. If user wants to trade, provide confirmation with symbol, side, qty.
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        gemini_res = await fetch(gemini_url, method="POST", headers=headers, body=json.dumps(payload))
        gemini_data = await gemini_res.json()
        
        try:
            reply = gemini_data['candidates'][0]['content']['parts'][0]['text']
        except:
            reply = "AI connection issue. Please try again."
        
        return Response.new(json.dumps({"reply": reply, "status": "success"}), headers=CORS_HEADERS)
        
    except Exception as e:
        return Response.new(json.dumps({"error": str(e)}), status=500, headers=CORS_HEADERS)


async def handle_trade(request, env):
    """Handle trade execution (Demo mode)"""
    try:
        body = await request.json()
        symbol = body.get("symbol", "BTCUSD")
        side = body.get("side", "buy")
        qty = body.get("qty", 1)
        order_type = body.get("type", "market")
        
        # Demo execution - simulate successful trade
        order_id = f"ORD-{datetime.datetime.now().strftime('%H%M%S')}"
        
        # Get current price estimate
        price = 98500 if "BTC" in symbol else 100
        
        result = {
            "status": "success",
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": qty,
            "price": price,
            "type": order_type,
            "filled": True,
            "message": f"✅ Demo Order Executed: {side.upper()} {qty} {symbol} @ ${price}"
        }
        
        # Log to KV
        await env.BRAIN_MEMORY.put(f"trade_{order_id}", json.dumps(result))
        
        return Response.new(json.dumps(result), headers=CORS_HEADERS)
        
    except Exception as e:
        return Response.new(json.dumps({"status": "error", "error": str(e)}), status=500, headers=CORS_HEADERS)


async def handle_market(request, env):
    """Get market data for a symbol"""
    try:
        url = request.url
        # Extract symbol from URL
        symbol = "BTC/USDT"
        if "AAPL" in url or "apple" in url.lower():
            symbol = "AAPL"
        elif "GLD" in url or "gold" in url.lower():
            symbol = "GLD"
        elif "XAUUSD" in url:
            symbol = "XAUUSD"
        
        # Fetch BTC price from CoinGecko as base
        btc_res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
        btc_data = await btc_res.json()
        
        if "BTC" in symbol:
            price = btc_data['bitcoin']['usd']
            change = btc_data['bitcoin']['usd_24h_change']
        elif symbol == "AAPL":
            price = 242.50
            change = 1.25
        elif symbol in ["GLD", "XAUUSD"]:
            price = 2650.80
            change = 0.45
        else:
            price = 100.00
            change = 0.0
        
        result = {
            "symbol": symbol,
            "price": price,
            "change": change * price / 100,
            "change_percent": round(change, 2),
            "high": price * 1.02,
            "low": price * 0.98,
            "volume": 1500000000,
            "asset_type": "crypto" if "BTC" in symbol else "stock",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return Response.new(json.dumps(result), headers=CORS_HEADERS)
        
    except Exception as e:
        # Return demo data on error
        return Response.new(json.dumps({
            "symbol": "BTC/USDT",
            "price": 98500,
            "change": 1250,
            "change_percent": 1.28,
            "high": 99500,
            "low": 97200,
            "volume": 1500000000,
            "asset_type": "crypto",
            "timestamp": datetime.datetime.now().isoformat()
        }), headers=CORS_HEADERS)


async def handle_status(env):
    """System status endpoint"""
    strategy_raw = await env.BRAIN_MEMORY.get("current_strategy")
    strategy = json.loads(strategy_raw) if strategy_raw else {"bias": "NEUTRAL"}
    
    return Response.new(json.dumps({
        "status": "online",
        "ai_status": "ready",
        "mode": "demo",
        "strategy_bias": strategy.get("bias", "NEUTRAL"),
        "last_update": strategy.get("last_updated", "N/A"),
        "endpoints_active": 5
    }), headers=CORS_HEADERS)


async def handle_brain_status(env):
    """Get brain/strategy status"""
    strategy_raw = await env.BRAIN_MEMORY.get("current_strategy")
    strategy = json.loads(strategy_raw) if strategy_raw else {"bias": "NEUTRAL", "raw_analysis": "Initializing..."}
    
    return Response.new(json.dumps({
        "strategic_engine": {
            "model": "DeepSeek V3",
            "status": "active",
            "bias": strategy.get("bias", "NEUTRAL")
        },
        "execution_engine": {
            "model": "Gemini Flash",
            "status": "ready"
        },
        "last_analysis": strategy.get("raw_analysis", "N/A"),
        "updated_at": strategy.get("last_updated", "N/A")
    }), headers=CORS_HEADERS)


async def on_scheduled(event, env, ctx):
    """
    ⏰ THE LOOP: Updates Strategy Every Minute (DeepSeek Layer)
    """
    print("⏰ Heartbeat: Analyzing Market...")
    
    # 1. Fetch Market Data
    try:
        btc_res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
        btc_data = await btc_res.json()
        price = btc_data['bitcoin']['usd']
        change_24h = btc_data['bitcoin']['usd_24h_change']
    except:
        price = 98000
        change_24h = 0
    
    # 2. Call DeepSeek
    deepseek_key = env.DEEPSEEK_API_KEY
    ds_url = "https://api.deepseek.com/v1/chat/completions"
    
    ds_payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a hedge fund algo. Analyze price & trend. Return JSON: {bias: 'BULLISH'|'BEARISH', reason: '...'}, max 50 words."},
            {"role": "user", "content": f"BTC Price: {price}, 24h Change: {change_24h}%"}
        ],
        "temperature": 0.0
    }
    
    headers = {
        "Authorization": f"Bearer {deepseek_key}",
        "Content-Type": "application/json"
    }
    
    try:
        ds_res = await fetch(ds_url, method="POST", headers=headers, body=json.dumps(ds_payload))
        ds_json = await ds_res.json()
        strategy_content = ds_json['choices'][0]['message']['content']
        
        final_strategy = {
            "bias": "BULLISH" if change_24h > 0 else "BEARISH",
            "raw_analysis": strategy_content,
            "last_updated": str(datetime.datetime.now())
        }
        
    except Exception as e:
        final_strategy = {"bias": "NEUTRAL", "error": str(e), "last_updated": str(datetime.datetime.now())}
    
    # 3. Save to Memory
    await env.BRAIN_MEMORY.put("current_strategy", json.dumps(final_strategy))
    print("✅ Strategy Updated via DeepSeek")
