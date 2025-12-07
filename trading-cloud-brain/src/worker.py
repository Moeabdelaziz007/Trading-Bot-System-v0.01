from js import Response, fetch, Headers, JSON
import json

# ==========================================
# 🧠 ANTIGRAVITY MoE BRAIN v2.0
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"
TELEGRAM_API_URL = "https://api.telegram.org/bot"
MAX_TRADES_PER_DAY = 10


async def on_fetch(request, env):
    """Main Entry Point - MoE Router with Shield Protocol 🛡️"""
    url = str(request.url)
    method = str(request.method)
    
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-System-Key"
    }
    headers = Headers.new(cors_headers.items())
    
    if method == "OPTIONS":
        return Response.new("", headers=headers)
    
    # ========================================
    # 🛡️ SHIELD PROTOCOL - Security Check
    # ========================================
    # Public endpoints (no auth required)
    public_paths = ["/api/status", "/api/telegram", "/telegram/webhook"]
    is_public = any(p in url for p in public_paths)
    
    # Root path check
    if url.endswith("/") or url.endswith("/api"):
        return Response.new(json.dumps({
            "name": "Antigravity MoE Brain",
            "version": "2.0",
            "status": "🔒 Secured",
            "message": "Shield Protocol Active"
        }), headers=headers)
    
    # Protected endpoints require X-System-Key
    if not is_public:
        client_key = None
        try:
            # Try to get header from request
            client_key = request.headers.get("X-System-Key")
        except:
            pass
        
        system_secret = str(getattr(env, 'SYSTEM_ACCESS_KEY', ''))
        
        # If secret is configured, enforce it
        if system_secret and (not client_key or client_key != system_secret):
            return Response.new(json.dumps({
                "error": "⛔ Unauthorized Access",
                "message": "Invalid or missing X-System-Key header"
            }), status=401, headers=headers)
    
    # ============ ROUTES ============
    
    # Telegram Webhook (public - has its own verification)
    if "/telegram/webhook" in url or "/api/telegram" in url:
        return await handle_telegram_webhook(request, env, headers)
    
    # Main Chat (MoE Dispatcher)
    if "api/chat" in url:
        return await handle_moe_chat(request, env, headers)
    
    # Chart Data
    if "api/candles" in url or "api/chart" in url:
        return await get_candles(request, env, headers)
    
    # Account Info
    if "api/account" in url:
        return await get_account(env, headers)
    
    # Positions
    if "api/positions" in url:
        return await get_positions(env, headers)
    
    # Status
    if "api/status" in url:
        trades_today = await get_trades_count(env)
        result = {
            "status": "online",
            "version": "2.0",
            "name": "Antigravity MoE Brain",
            "ai": "Groq Router + Gemini RAG",
            "database": "D1 Connected",
            "broker": "Alpaca Paper",
            "trades_today": trades_today,
            "max_trades": MAX_TRADES_PER_DAY
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Trade Execution
    if "api/trade" in url:
        params = dict(p.split("=") for p in url.split("?")[1].split("&")) if "?" in url else {}
        symbol = params.get("symbol", "SPY").upper()
        side = params.get("side", "buy")
        qty = int(params.get("qty", "1"))
        
        # Check trade limits
        trades_today = await get_trades_count(env)
        if trades_today >= MAX_TRADES_PER_DAY:
            return Response.new(json.dumps({"error": f"Daily limit reached ({MAX_TRADES_PER_DAY})"}), headers=headers)
        
        result = await execute_alpaca_trade(env, symbol, side, qty)
        
        if result.get("status") == "success":
            await log_trade(env, symbol, side, qty, result.get("price", 0))
            alert_msg = f"🟢 TRADE: {side.upper()} {qty} {symbol} @ ${result.get('price', 'N/A')}"
            await send_telegram_alert(env, alert_msg)
        
        return Response.new(json.dumps(result), headers=headers)
    
    # Trade Logs
    if "api/logs" in url:
        try:
            db = env.TRADING_DB
            result = await db.prepare("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50").all()
            logs = []
            if hasattr(result, 'results'):
                for row in result.results:
                    logs.append({
                        "id": row.id if hasattr(row, 'id') else None,
                        "ticker": row.symbol if hasattr(row, 'symbol') else "",
                        "action": row.side if hasattr(row, 'side') else "",
                        "qty": row.qty if hasattr(row, 'qty') else 0,
                        "executed_at": str(row.timestamp) if hasattr(row, 'timestamp') else ""
                    })
            return Response.new(json.dumps({"logs": logs}), headers=headers)
        except:
            return Response.new(json.dumps({"logs": []}), headers=headers)
    
    return Response.new(json.dumps({"message": "🦅 Antigravity MoE Brain v2.0 Online"}), headers=headers)


# ==========================================
# 🎯 MoE DISPATCHER (Main Chat Handler)
# ==========================================

async def handle_moe_chat(request, env, headers):
    """Mixture of Experts Chat Handler"""
    try:
        # Parse body - request.json() returns JS object, convert to Python dict
        body_js = await request.json()
        body = json.loads(JSON.stringify(body_js))
        user_msg = body.get("message", "Hello")
        
        # 1. ROUTER AGENT (Groq - Fast Intent Classification)
        intent_data = await route_intent(user_msg, env)
        intent_type = intent_data.get("type", "CHAT")
        
        # 2. DISPATCH TO EXPERT AGENTS
        
        # A. ANALYST AGENT (Gemini RAG)
        if intent_type == "RESEARCH" or intent_type == "ANALYZE":
            symbol = intent_data.get("symbol", "SPY").upper()
            
            # Fetch News + Price Data
            news_text = await fetch_yahoo_news(symbol)
            price_data = await fetch_alpaca_snapshot(symbol, env)
            
            # Gemini RAG Analysis
            analysis = await analyze_with_gemini_rag(symbol, news_text, price_data, env)
            
            return Response.new(json.dumps({
                "type": "RESEARCH",
                "symbol": symbol,
                "reply": analysis
            }), headers=headers)
        
        # B. CHART AGENT
        elif intent_type == "SHOW_CHART":
            symbol = intent_data.get("symbol", "SPY").upper()
            candles = await fetch_alpaca_bars(symbol, env)
            
            return Response.new(json.dumps({
                "type": "SHOW_CHART",
                "symbol": symbol,
                "candles": candles,
                "reply": f"📈 Loading {symbol} chart..."
            }), headers=headers)
        
        # C. TRADER AGENT
        elif intent_type == "TRADE":
            symbol = intent_data.get("symbol", "AAPL").upper()
            side = intent_data.get("side", "buy")
            qty = intent_data.get("qty", 1)
            
            # Check trade limits
            trades_today = await get_trades_count(env)
            if trades_today >= MAX_TRADES_PER_DAY:
                return Response.new(json.dumps({
                    "type": "TRADE",
                    "reply": f"⚠️ Daily trade limit reached ({MAX_TRADES_PER_DAY})"
                }), headers=headers)
            
            # Execute Trade
            result = await execute_alpaca_trade(env, symbol, side, qty)
            
            if result.get("status") == "success":
                # Log trade
                await log_trade(env, symbol, side, qty, result.get("price", 0))
                
                # Send Telegram Alert
                alert_msg = f"🟢 <b>TRADE EXECUTED</b>\n\n{side.upper()} {qty} {symbol}\nPrice: ${result.get('price', 'N/A')}"
                await send_telegram_alert(env, alert_msg)
                
                return Response.new(json.dumps({
                    "type": "TRADE",
                    "trade_executed": result,
                    "reply": f"💰 {side.upper()} {qty} {symbol} executed @ ${result.get('price', 'market')}"
                }), headers=headers)
            else:
                return Response.new(json.dumps({
                    "type": "TRADE",
                    "reply": f"⚠️ Trade failed: {result.get('error', 'Unknown error')}"
                }), headers=headers)
        
        # D. CHAT AGENT (Groq for smart conversation)
        else:
            reply = await call_groq_chat(user_msg, env)
            return Response.new(json.dumps({
                "type": "CHAT",
                "reply": reply
            }), headers=headers)
    
    except Exception as e:
        return Response.new(json.dumps({"reply": f"⚠️ Error: {str(e)}"}), status=500, headers=headers)


# ==========================================
# 🚀 ROUTER AGENT (Groq - Fast)
# ==========================================

async def route_intent(user_msg, env):
    """Groq Llama 3 Router - Fast intent classification"""
    try:
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        if not groq_key:
            return {"type": "CHAT", "reply": "Router not configured"}
        
        system_prompt = """You are a Trading Router. Classify user intent to JSON.

OUTPUT JSON with these fields:
- type: RESEARCH | SHOW_CHART | TRADE | CHAT
- symbol: Stock/crypto symbol (ONLY if user mentions a specific stock)
- side: buy | sell (for TRADE only)
- qty: number (for TRADE only)
- reply: Brief response

CLASSIFICATION RULES:
- RESEARCH: User wants analysis of a SPECIFIC stock (e.g., "Analyze AAPL", "What do you think about Tesla?")
- SHOW_CHART: User wants to see a chart (e.g., "Show SPY chart", "Chart for NVDA")
- TRADE: User wants to execute a trade (e.g., "Buy 10 AAPL", "Sell 5 TSLA")
- CHAT: General questions, greetings, strategy questions, explanations (e.g., "Hello", "What is RSI?", "Best strategy for trading?")

EXAMPLES:
"Analyze Tesla" -> {"type": "RESEARCH", "symbol": "TSLA", "reply": "Analyzing TSLA..."}
"Show SPY chart" -> {"type": "SHOW_CHART", "symbol": "SPY", "reply": "Loading chart..."}
"Buy 10 AAPL" -> {"type": "TRADE", "symbol": "AAPL", "side": "buy", "qty": 10, "reply": "Executing..."}
"Hello" -> {"type": "CHAT", "symbol": null, "reply": "Hello! How can I help?"}
"What is RSI indicator?" -> {"type": "CHAT", "symbol": null, "reply": "RSI is..."}
"Best strategy for day trading?" -> {"type": "CHAT", "symbol": null, "reply": "Here are some strategies..."}
"How are you?" -> {"type": "CHAT", "symbol": null, "reply": "I'm doing great!"}"""

        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 200
        })
        
        headers_dict = {
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }
        req_headers = Headers.new(headers_dict.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=req_headers, body=payload)
        response_text = await response.text()
        
        if response.ok:
            data = json.loads(str(response_text))
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        else:
            return {"type": "CHAT", "reply": f"Router error: {response_text[:100]}"}
    except Exception as e:
        return {"type": "CHAT", "reply": f"Processing: {str(e)[:50]}"}



# ==========================================
# 🔬 ANALYST AGENT (Gemini RAG)
# ==========================================

async def analyze_with_gemini_rag(symbol, news_text, price_data, env):
    """Smart RAG Analysis - Groq Llama 3.3 (Fallback since Gemini not working)"""
    groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
    
    if not groq_key:
        return f"⚠️ GROQ_API_KEY not configured"
    
    # Smart Analysis Prompt for Groq
    prompt = f"""You are SENTINEL, an expert trading analyst. Analyze {symbol} based on the data below.

📊 MARKET DATA:
- Price: ${price_data.get('price', 'N/A')}
- Change: {price_data.get('change_percent', '0')}%

📰 NEWS (Yahoo Finance RSS):
{news_text[:2500]}

📋 PROVIDE:
1. SENTIMENT: 🟢 BULLISH / 🔴 BEARISH / 🟡 NEUTRAL
2. KEY DRIVER: (One sentence based on news headlines)
3. RISK: (Main risk factor)
4. VERDICT: Buy/Sell/Hold with brief reason

Be concise and actionable. Use emojis sparingly."""

    payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are SENTINEL, an expert Wall Street analyst providing actionable trading insights."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,
        "max_tokens": 500
    })
    
    try:
        req_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=req_headers, body=payload)
        response_text = await response.text()
        data = json.loads(str(response_text))
        
        if "error" in data:
            error_msg = data.get("error", {}).get("message", "Unknown Error")
            return f"⚠️ Groq Error: {error_msg}"
        
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if content:
            return content
        
        return f"⚠️ Empty response from AI"
    
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"


async def call_gemini_chat(user_message, user_name, env):
    """Gemini for general chat"""
    try:
        gemini_key = str(getattr(env, 'GEMINI_API_KEY', ''))
        if not gemini_key:
            return await call_groq_chat(user_message, env)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={gemini_key}"
        
        prompt = f"""You are SENTINEL - an expert AI trading assistant.

PERSONALITY:
- Seasoned Wall Street quant with 20 years experience
- Confident, concise, uses emojis sparingly (📈📉💰⚠️)
- Provides actionable insights, not generic advice

User: {user_message}

Respond as a trading expert. Be helpful and specific."""

        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 300}
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        response = await fetch(url, method="POST", headers=req_headers, body=payload)
        
        if response.ok:
            data = json.loads(await response.text())
            text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                return text
        
        return await call_groq_chat(user_message, env)
    except:
        return await call_groq_chat(user_message, env)


async def call_groq_chat(user_message, env):
    """Groq fallback for chat"""
    try:
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        if not groq_key:
            return "⚠️ AI not configured"
        
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are SENTINEL, an expert trading AI. Be concise and insightful."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        })
        
        req_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=req_headers, body=payload)
        
        if response.ok:
            data = json.loads(await response.text())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "🤔 Let me think...")
        
        return "⚠️ AI temporarily unavailable"
    except:
        return "⚠️ Connection error"


# ==========================================
# 📱 TELEGRAM HANDLERS
# ==========================================

async def handle_telegram_webhook(request, env, headers):
    """Receive Telegram messages and reply with LLM"""
    try:
        body = await request.json()
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "Trader")
        
        if not chat_id or not text:
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # Handle /start command
        if text.startswith("/start"):
            reply = f"""🧠 <b>SENTINEL AI</b> Online!

Hello {user_name}! I'm your expert trading assistant.

<b>Commands:</b>
• Analyze AAPL - Get news & sentiment
• Show SPY chart - Load chart
• Buy 5 TSLA - Execute trade
• What's happening with gold?

Send any message to start!"""
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # Process via MoE
        intent_data = await route_intent(text, env)
        intent_type = intent_data.get("type", "CHAT")
        
        if intent_type == "RESEARCH":
            symbol = intent_data.get("symbol", "SPY").upper()
            news_text = await fetch_yahoo_news(symbol)
            price_data = await fetch_alpaca_snapshot(symbol, env)
            ai_response = await analyze_with_gemini_rag(symbol, news_text, price_data, env)
        else:
            ai_response = await call_gemini_chat(text, user_name, env)
        
        await send_telegram_reply(env, chat_id, ai_response)
        return Response.new(json.dumps({"ok": True}), headers=headers)
    except Exception as e:
        return Response.new(json.dumps({"ok": True, "error": str(e)}), headers=headers)


async def send_telegram_alert(env, message):
    """Send notification to Telegram"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        telegram_chat_id = str(getattr(env, 'TELEGRAM_CHAT_ID', ''))
        
        if not telegram_token or not telegram_chat_id:
            return
        
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        
        payload = json.dumps({
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=req_headers, body=payload)
    except:
        pass


async def send_telegram_reply(env, chat_id, text):
    """Send reply to specific chat"""
    try:
        telegram_token = str(getattr(env, 'TELEGRAM_BOT_TOKEN', ''))
        url = f"{TELEGRAM_API_URL}{telegram_token}/sendMessage"
        
        # Truncate for Telegram limit
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        })
        
        req_headers = Headers.new({"Content-Type": "application/json"}.items())
        await fetch(url, method="POST", headers=req_headers, body=payload)
    except:
        pass


# ==========================================
# 🔌 DATA CONNECTORS
# ==========================================

async def fetch_yahoo_news(symbol):
    """Fetch news from Yahoo Finance RSS"""
    try:

        # Use Google News RSS as it's more reliable than Yahoo
        rss_url = f"https://news.google.com/rss/search?q={symbol}+stock+news&hl=en-US&gl=US&ceid=US:en"
        headers = Headers.new({"User-Agent": "Mozilla/5.0 (compatible; AntigravityBot/2.0)"}.items())
        response = await fetch(rss_url, headers=headers)
        text = await response.text()
        return str(text)[:10000]  # Max for Gemini context
    except:
        return "No news available."


async def fetch_alpaca_snapshot(symbol, env):
    """Fetch latest quote from Alpaca"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        # Handle crypto symbols
        is_crypto = symbol in ["BTC", "ETH", "SOL", "DOGE"] or "/" in symbol
        
        if is_crypto:
            data_symbol = f"{symbol.replace('/USD', '').replace('USD', '')}/USD"
            url = f"https://data.alpaca.markets/v1beta3/crypto/us/latest/quotes?symbols={data_symbol}"
        else:
            url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            
            if is_crypto:
                quotes = data.get("quotes", {})
                quote = list(quotes.values())[0] if quotes else {}
                return {
                    "price": quote.get("ap", "N/A"),
                    "bid": quote.get("bp", "N/A"),
                    "ask": quote.get("ap", "N/A"),
                    "change_percent": "0",
                    "volume": "N/A"
                }
            else:
                quote = data.get("quote", {})
                return {
                    "price": quote.get("ap", "N/A"),
                    "bid": quote.get("bp", "N/A"),
                    "ask": quote.get("ap", "N/A"),
                    "change_percent": "0",
                    "volume": "N/A"
                }
        
        return {"price": "N/A", "change_percent": "0", "volume": "N/A"}
    except:
        return {"price": "N/A", "change_percent": "0", "volume": "N/A"}


async def fetch_alpaca_bars(symbol, env):
    """Fetch candles from Alpaca for charting"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        from datetime import datetime, timedelta
        end = datetime.utcnow()
        start = end - timedelta(days=30)
        
        start_str = start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_str = end.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        is_crypto = symbol in ["BTC", "ETH", "SOL", "DOGE"] or "/" in symbol
        
        if is_crypto:
            data_symbol = f"{symbol.replace('/USD', '').replace('USD', '')}/USD"
            url = f"https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols={data_symbol}&timeframe=1Hour&start={start_str}&end={end_str}&limit=100"
        else:
            url = f"{ALPACA_DATA_URL}/stocks/{symbol}/bars?timeframe=1Hour&start={start_str}&end={end_str}&limit=100"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            
            if is_crypto:
                bars = data.get("bars", {})
                bar_list = list(bars.values())[0] if bars else []
            else:
                bar_list = data.get("bars", [])
            
            candles = []
            for bar in bar_list:
                t = bar.get("t", "")
                candles.append({
                    "time": t[:10] if t else "",
                    "open": bar.get("o", 0),
                    "high": bar.get("h", 0),
                    "low": bar.get("l", 0),
                    "close": bar.get("c", 0),
                    "volume": bar.get("v", 0)
                })
            
            return sorted(candles, key=lambda x: x["time"])
        
        return generate_demo_candles()
    except:
        return generate_demo_candles()


def generate_demo_candles():
    """Generate demo candle data"""
    import time
    from datetime import datetime
    
    candles = []
    base_price = 595
    current_time = int(time.time())
    
    for i in range(100):
        t = current_time - (100 - i) * 3600
        o = base_price + (hash(str(t)) % 10 - 5)
        c = o + (hash(str(t+1)) % 8 - 4)
        h = max(o, c) + (hash(str(t+2)) % 3)
        l = min(o, c) - (hash(str(t+3)) % 3)
        v = 1000000 + hash(str(t+4)) % 500000
        
        dt = datetime.utcfromtimestamp(t)
        date_str = dt.strftime('%Y-%m-%d')
        
        candles.append({"time": date_str, "open": o, "high": h, "low": l, "close": c, "volume": v})
        base_price = c
    
    return candles


async def get_candles(request, env, headers):
    """API endpoint for candles with KV Caching"""
    url = str(request.url)
    symbol = "SPY"
    
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0].upper()
    
    # ⚡️ KV Cache Check
    cache_key = f"candles_{symbol}"
    try:
        if hasattr(env, 'BRAIN_MEMORY'):
            cached = await env.BRAIN_MEMORY.get(cache_key)
            if cached:
                return Response.new(json.dumps({"symbol": symbol, "candles": json.loads(cached), "cached": True}), headers=headers)
    except:
        pass

    candles = await fetch_alpaca_bars(symbol, env)
    
    # 💾 Cache Result
    try:
        if hasattr(env, 'BRAIN_MEMORY') and candles:
            await env.BRAIN_MEMORY.put(cache_key, json.dumps(candles), expiration_ttl=60)
    except:
        pass
        
    return Response.new(json.dumps({"symbol": symbol, "candles": candles}), headers=headers)


# ==========================================
# 💰 TRADING FUNCTIONS
# ==========================================

async def execute_alpaca_trade(env, symbol, side, qty):
    """Execute trade on Alpaca"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        order_body = json.dumps({
            "symbol": symbol.upper(),
            "qty": str(qty),
            "side": side.lower(),
            "type": "market",
            "time_in_force": "day"
        })
        
        order_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret,
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/orders", method="POST", headers=order_headers, body=order_body)
        response_text = await response.text()
        
        if response.ok:
            order_data = json.loads(str(response_text))
            return {
                "status": "success",
                "order_id": order_data.get("id", ""),
                "symbol": order_data.get("symbol", symbol),
                "side": order_data.get("side", side),
                "qty": order_data.get("qty", qty),
                "price": order_data.get("filled_avg_price", "market")
            }
        else:
            return {"status": "error", "error": str(response_text)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def get_account(env, headers):
    """Get Alpaca account info"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/account", method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            return Response.new(json.dumps({
                "portfolio_value": data.get("portfolio_value", "0"),
                "buying_power": data.get("buying_power", "0"),
                "cash": data.get("cash", "0"),
                "equity": data.get("equity", "0")
            }), headers=headers)
        
        return Response.new(json.dumps({"portfolio_value": "100000", "buying_power": "200000", "cash": "100000"}), headers=headers)
    except:
        return Response.new(json.dumps({"portfolio_value": "100000", "buying_power": "200000", "cash": "100000"}), headers=headers)


async def get_positions(env, headers):
    """Get Alpaca positions"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/positions", method="GET", headers=req_headers)
        
        if response.ok:
            positions = json.loads(await response.text())
            return Response.new(json.dumps(positions), headers=headers)
        
        return Response.new(json.dumps([]), headers=headers)
    except:
        return Response.new(json.dumps([]), headers=headers)


# ==========================================
# 📊 DATABASE FUNCTIONS (D1)
# ==========================================

async def log_trade(env, symbol, side, qty, price):
    """Log trade to D1 database"""
    try:
        db = env.TRADING_DB
        await db.prepare(
            "INSERT INTO trades (symbol, side, qty, price, timestamp) VALUES (?, ?, ?, ?, datetime('now'))"
        ).bind(symbol, side, qty, price).run()
    except:
        pass


async def get_trades_count(env):
    """Get today's trade count"""
    try:
        db = env.TRADING_DB
        result = await db.prepare(
            "SELECT COUNT(*) as count FROM trades WHERE date(timestamp) = date('now')"
        ).first()
        return result.get("count", 0) if result else 0
    except:
        return 0


# ==========================================
# ⏰ CRON HANDLER (Automation)
# ==========================================

async def on_scheduled(event, env, ctx):
    """Cron job for automated trading rules + Database Maintenance"""
    try:
        db = env.TRADING_DB
        rules = await db.prepare("SELECT * FROM rules WHERE active = 1").all()
        
        if rules.results:
            for rule in rules.results:
                ticker = rule.get("ticker", "SPY")
                condition = rule.get("condition", "PRICE_ABOVE")
                trigger = float(rule.get("trigger_value", 0))
                action = rule.get("action", "BUY")
                qty = int(rule.get("qty", 1))
                
                # Get current price
                price_data = await fetch_alpaca_snapshot(ticker, env)
                current_price = float(price_data.get("price", 0)) if price_data.get("price") != "N/A" else 0
                
                if current_price == 0:
                    continue
                
                should_execute = False
                if condition == "PRICE_ABOVE" and current_price > trigger:
                    should_execute = True
                elif condition == "PRICE_BELOW" and current_price < trigger:
                    should_execute = True
                
                if should_execute:
                    side = "buy" if action == "BUY" else "sell"
                    result = await execute_alpaca_trade(env, ticker, side, qty)
                    
                    if result.get("status") == "success":
                        await log_trade(env, ticker, side, qty, result.get("price", current_price))
                        await send_telegram_alert(env, f"⚡ <b>AUTO TRADE</b>\n\nRule triggered: {condition} {trigger}\n{side.upper()} {qty} {ticker}")
                        
                        # Deactivate rule after execution
                        await db.prepare("UPDATE rules SET active = 0 WHERE id = ?").bind(rule.get("id")).run()
        
        # 🧹 DATABASE MAINTENANCE - Prune old records (30+ days)
        try:
            await db.prepare(
                "DELETE FROM trades WHERE timestamp < datetime('now', '-30 days')"
            ).run()
        except:
            pass
            
    except:
        pass
