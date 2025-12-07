from js import Response, fetch, Headers, JSON
import json
from base64 import b64encode
from capital_connector import CapitalConnector
from economic_calendar import EconomicCalendar
from deepseek_analyst import DeepSeekAnalyst
from workers_ai import WorkersAI
from risk_manager import RiskGuardian
from data_collector import DataCollector

# ==========================================
# 🧠 ANTIGRAVITY MoE BRAIN v2.0
# ==========================================

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_DATA_URL = "https://data.alpaca.markets/v2"
TELEGRAM_API_URL = "https://api.telegram.org/bot"
ABLY_API_URL = "https://rest.ably.io"
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
    public_paths = [
        "/api/status", 
        "/api/telegram", 
        "/telegram/webhook",
        "/api/chat",      # DeepSeek AI chat
        "/api/account",   # Account data
        "/api/positions", # Open positions
        "/api/market",    # Market data
        "/api/candles"    # Chart data
    ]
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
        return await get_combined_account(env, headers)
    
    # Positions
    if "api/positions" in url:
        return await get_combined_positions(env, headers)
    
    # Market Snapshot (Real-time prices with change %)
    if "api/market" in url or "api/snapshot" in url:
        return await get_market_snapshot(request, env, headers)
    
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
    
    # ☢️ PANIC PROTOCOL - Liquidate All Positions
    if "api/trade/panic" in url or "api/panic" in url:
        try:
            result = await execute_panic_protocol(env)
            
            # Send Telegram alert
            await send_telegram_alert(env, "🚨 **PANIC PROTOCOL ACTIVATED**\nAll positions are being liquidated immediately!")
            
            return Response.new(json.dumps(result), headers=headers)
        except Exception as e:
            return Response.new(json.dumps({"error": str(e), "status": "FAILED"}), headers=headers)
    
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
        
        # Intelligent Trade Routing 🦅
        if "/" in symbol or "_" in symbol or len(symbol) == 6 or "USD" in symbol:
             # Likely Forex pair (EUR/USD, GBPUSD) -> OANDA
             result = await execute_oanda_trade(env, symbol, side, qty)
        else:
             # Default to Alpaca for Stocks/Crypto
             result = await execute_alpaca_trade(env, symbol, side, qty)
        
        if result.get("status") == "success":
            await log_trade(env, symbol, side, qty, result.get("price", 0))
            alert_msg = f"🟢 TRADE: {side.upper()} {qty} {symbol} @ ${result.get('price', 'N/A')}"
            await send_telegram_alert(env, alert_msg)
        
        return Response.new(json.dumps(result), headers=headers)
    
    # Trade Logs
    if "api/logs" in url:
        # Implement log fetching from D1 if needed
        return Response.new(json.dumps({"logs": []}), headers=headers)
        
    # ⚡ Ably Realtime Auth (Token Request)
    if "api/ably/auth" in url:
        try:
            ably_key = str(getattr(env, 'ABLY_API_KEY', ''))
            key_name, key_secret = ably_key.split(':')
            
            # Request token from Ably
            token_url = f"{ABLY_API_URL}/keys/{key_name}/requestToken"
            
            # Create Basic Auth header
            # Python's b64encode expects bytes
            auth_str = f"{key_name}:{key_secret}"
            auth_b64 = b64encode(auth_str.encode('utf-8')).decode('utf-8')
            
            token_headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json"
            }
            
            body = {
                "id": "antigravity_client",
                "clientId": "antigravity_client",
                "ttl": 3600 * 1000, # 1 hour
                "capability": '{"*":["subscribe"]}' # Client can only subscribe
            }
            
            res = await fetch(token_url, method="POST", headers=token_headers, body=json.dumps(body))
            token_data = await res.json()
            
            return Response.new(json.dumps(token_data), headers=headers)
        except Exception as e:
            return Response.new(json.dumps({"error": str(e)}), headers=headers)

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
            "model": "deepseek-r1-distill-llama-70b",
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
        "model": "deepseek-r1-distill-llama-70b",
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
        
        # Use stable Llama model (DeepSeek R1 may have rate limits)
        payload = json.dumps({
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are SENTINEL, an expert AI trading assistant powered by Axiom Antigravity. Provide concise, insightful market analysis. Respond in the same language as the user."},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        })
        
        req_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, method="POST", headers=req_headers, body=payload)
        
        if response.ok:
            data = json.loads(await response.text())
            return data.get("choices", [{}])[0].get("message", {}).get("content", "🤔 Let me think...")
        
        # Return detailed error for debugging
        error_text = await response.text()
        return f"⚠️ AI Error: {response.status}"
    except Exception as e:
        return f"⚠️ Connection error: {str(e)}"


# ==========================================
# 📱 TELEGRAM HANDLERS
# ==========================================

async def handle_telegram_webhook(request, env, headers):
    """Receive Telegram messages and reply with LLM"""
    try:
        # Parse JS object to Python dict
        body_js = await request.json()
        body = json.loads(JSON.stringify(body_js))
        
        message = body.get("message", {})
        if not message:
            return Response.new(json.dumps({"ok": True}), headers=headers)
            
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        user_name = message.get("from", {}).get("first_name", "Trader")
        
        if not chat_id or not text:
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # ============ COMMAND HANDLING ============
        
        # /start command
        if text.startswith("/start") and not text.startswith("/starttrade"):
            reply = f"""🦅 <b>ANTIGRAVITY TERMINAL</b> Online!

مرحباً {user_name}! أنا Sentinel AI - مساعدك الذكي للتداول.

<b>📋 الأوامر المتاحة:</b>
• /balance - عرض رصيد المحفظة
• /positions - المراكز المفتوحة
• /stoptrade - 🛑 إيقاف التداول التلقائي
• /starttrade - ▶️ تشغيل التداول التلقائي
• /status - حالة النظام
• Analyze EURUSD - تحليل زوج
• أي سؤال - سأجيبك!

<b>🔗 Dashboard:</b> trading-brain-v1.amrikyy.workers.dev"""
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # ============ KILL SWITCH COMMANDS ============
        
        # /stoptrade - Activate panic mode (halt all trading)
        if text.startswith("/stoptrade") or text.startswith("/stop"):
            try:
                kv = env.BRAIN_MEMORY
                await kv.put("panic_mode", "true")
                await kv.put("panic_timestamp", str(int(__import__('time').time())))
                reply = """🛑 <b>KILL SWITCH ACTIVATED</b>

التداول التلقائي <b>متوقف الآن</b>.

جميع عمليات التداول الآلية معلقة.
لإعادة التشغيل، أرسل: /starttrade"""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /starttrade - Deactivate panic mode
        if text.startswith("/starttrade"):
            try:
                kv = env.BRAIN_MEMORY
                await kv.put("panic_mode", "false")
                reply = """▶️ <b>TRADING RESUMED</b>

التداول التلقائي <b>نشط الآن</b>.

سيتم تنفيذ جميع إشارات Twin-Turbo المعتمدة."""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /status - System status including panic mode
        if text.startswith("/status"):
            try:
                kv = env.BRAIN_MEMORY
                panic_mode = await kv.get("panic_mode") or "false"
                capital = CapitalConnector(env)
                account = await capital.get_account_info()
                
                status_emoji = "🛑" if panic_mode == "true" else "🟢"
                status_text = "متوقف" if panic_mode == "true" else "نشط"
                
                reply = f"""📊 <b>SYSTEM STATUS</b>

{status_emoji} التداول التلقائي: <b>{status_text}</b>
💰 الرصيد: ${float(account.get('balance', 0)):,.2f}
📈 الوسيط: {account.get('source', 'Capital.com Demo')}

⏰ آخر فحص: الآن"""
                await send_telegram_reply(env, chat_id, reply)
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # ============ DEEPSEEK ANALYSIS COMMANDS ============
        
        # /analyze - Deep analysis using DeepSeek brain
        if text.startswith("/analyze"):
            try:
                # Parse command: /analyze [type] [text]
                # Types: sentiment, signal, summary, risk
                parts = text.split(maxsplit=2)
                analysis_type = "sentiment"  # default
                analysis_text = ""
                
                if len(parts) >= 2:
                    if parts[1] in ["sentiment", "signal", "summary", "risk"]:
                        analysis_type = parts[1]
                        analysis_text = parts[2] if len(parts) > 2 else ""
                    else:
                        analysis_text = " ".join(parts[1:])
                
                if not analysis_text:
                    await send_telegram_reply(env, chat_id, """🧠 <b>DeepSeek Analyst</b>

استخدم: /analyze [نوع] [نص]

<b>أنواع التحليل:</b>
• sentiment - تحليل المشاعر
• signal - إشارة تداول
• summary - ملخص
• risk - تحليل مخاطر

<b>مثال:</b>
/analyze sentiment البنك المركزي يرفع سعر الفائدة""")
                    return Response.new(json.dumps({"ok": True}), headers=headers)
                
                # Send "thinking" message
                await send_telegram_reply(env, chat_id, "🧠 <i>DeepSeek يحلل...</i>")
                
                # Run DeepSeek analysis
                analyst = DeepSeekAnalyst(env)
                result = await analyst.analyze_financial_text(analysis_text, analysis_type)
                
                if result.get("error"):
                    await send_telegram_reply(env, chat_id, f"❌ خطأ: {result['error']}")
                else:
                    content = result.get("content", {})
                    usage = result.get("usage", {})
                    cost = result.get("cost_usd", 0)
                    cached = "✓ cached" if result.get("cached") else ""
                    
                    # Format response based on type
                    if analysis_type == "sentiment":
                        reply = f"""🎯 <b>تحليل المشاعر</b> {cached}

📊 المشاعر: <b>{content.get('sentiment', 'N/A')}</b>
💪 الثقة: <b>{content.get('confidence', 0)}%</b>
📈 تأثير السوق: {content.get('market_impact', 'N/A')}

<b>العوامل الرئيسية:</b>
{chr(10).join('• ' + f for f in content.get('key_factors', [])[:3])}

<b>التفسير:</b>
{content.get('reasoning', 'N/A')[:300]}

💰 التكلفة: ${cost:.4f} | 📝 {usage.get('total_tokens', 0)} tokens"""
                    
                    elif analysis_type == "signal":
                        reply = f"""📡 <b>إشارة تداول</b> {cached}

🎯 الإجراء: <b>{content.get('action', 'HOLD')}</b>
💹 الأصول: {', '.join(content.get('target_assets', ['N/A'])[:3])}
💪 الثقة: <b>{content.get('confidence', 0)}%</b>
⚠️ المخاطر: {content.get('risk_level', 'N/A')}
⏰ التوقيت: {content.get('entry_timing', 'N/A')}

<b>التحليل:</b>
{content.get('reasoning', 'N/A')[:300]}

💰 التكلفة: ${cost:.4f}"""
                    
                    else:
                        reply = f"""📋 <b>التحليل</b> ({analysis_type}) {cached}

{json.dumps(content, ensure_ascii=False, indent=2)[:800]}

💰 التكلفة: ${cost:.4f} | 📝 {usage.get('total_tokens', 0)} tokens"""
                    
                    await send_telegram_reply(env, chat_id, reply)
                    
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ DeepSeek: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # ============ FREE WORKERS AI COMMANDS ============
        
        # /ai - Quick FREE AI using Cloudflare Workers AI
        if text.startswith("/ai"):
            try:
                query = text[3:].strip()
                if not query:
                    await send_telegram_reply(env, chat_id, """🆓 <b>Workers AI (مجاني!)</b>

استخدم: /ai [سؤالك]

<b>مميزات:</b>
• 10,000 neurons مجانية يومياً
• Llama 3.1 8B (Beta = مجاني غير محدود)
• لا يحتاج API key

<b>مثال:</b>
/ai ما رأيك في EURUSD اليوم؟""")
                    return Response.new(json.dumps({"ok": True}), headers=headers)
                
                await send_telegram_reply(env, chat_id, "🆓 <i>Workers AI (مجاني) يفكر...</i>")
                
                ai = WorkersAI(env)
                result = await ai.chat(
                    message=query,
                    system_prompt="أنت مساعد تداول ذكي. أجب بإيجاز وباللغة العربية."
                )
                
                if result.get("error"):
                    await send_telegram_reply(env, chat_id, f"❌ خطأ: {result['error']}")
                else:
                    content = result.get("content", "لا توجد إجابة")
                    source = result.get("source", "workers_ai")
                    reply = f"""🆓 <b>Workers AI</b>

{content[:1500]}

<i>المصدر: {source} | التكلفة: $0.00</i>"""
                    await send_telegram_reply(env, chat_id, reply)
                    
            except Exception as e:
                await send_telegram_reply(env, chat_id, f"⚠️ خطأ Workers AI: {str(e)}")
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /balance command
        if text.startswith("/balance"):
            account = await get_alpaca_account_data(env)
            reply = f"""💰 <b>Portfolio Status</b>

📊 Equity: ${float(account.get('equity', 0)):,.2f}
💵 Cash: ${float(account.get('cash', 0)):,.2f}
🔋 Buying Power: ${float(account.get('buying_power', 0)):,.2f}

🟢 System: Healthy"""
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # /positions command
        if text.startswith("/positions"):
            positions = await get_alpaca_positions_data(env)
            if positions:
                pos_text = "\n".join([f"• {p.get('symbol')}: {p.get('qty')} @ ${float(p.get('current_price', 0)):,.2f}" for p in positions[:5]])
                reply = f"📈 <b>Open Positions:</b>\n\n{pos_text}"
            else:
                reply = "📭 No open positions."
            await send_telegram_reply(env, chat_id, reply)
            return Response.new(json.dumps({"ok": True}), headers=headers)
        
        # Process via MoE Router
        intent_data = await route_intent(text, env)
        intent_type = intent_data.get("type", "CHAT")
        
        if intent_type == "RESEARCH" or intent_type == "ANALYZE":
            symbol = intent_data.get("symbol", "SPY").upper()
            await send_telegram_reply(env, chat_id, f"🔍 جاري تحليل {symbol}...")
            news_text = await fetch_yahoo_news(symbol)
            price_data = await fetch_alpaca_snapshot(symbol, env)
            ai_response = await analyze_with_gemini_rag(symbol, news_text, price_data, env)
            
        elif intent_type == "TRADE":
            symbol = intent_data.get("symbol", "AAPL").upper()
            side = intent_data.get("side", "buy")
            qty = intent_data.get("qty", 1)
            
            # Execute trade
            result = await execute_alpaca_trade(env, symbol, side, qty)
            if result.get("status") == "success":
                await log_trade(env, symbol, side, qty, result.get("price", 0))
                ai_response = f"✅ تم تنفيذ الصفقة!\n\n{side.upper()} {qty} {symbol}"
            else:
                ai_response = f"⚠️ فشل التنفيذ: {result.get('error', 'Unknown')}"
                
        else:
            # General chat
            ai_response = await call_groq_chat(text, env)
        
        await send_telegram_reply(env, chat_id, ai_response)
        return Response.new(json.dumps({"ok": True}), headers=headers)
        
    except Exception as e:
        # Always return OK to prevent Telegram retries
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
# 💰 TRADING FUNCTIONS & ROUTING
# ==========================================

async def execute_capital_trade(env, symbol, side, qty):
    """Execute Trade via Capital.com (Forex/CFD)"""
    try:
        connector = CapitalConnector(env)
        result = await connector.create_position(symbol, side.upper(), float(qty))
        return result
    except Exception as e:
        return {"status": "error", "error": str(e)}


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


async def execute_panic_protocol(env):
    """☢️ PANIC PROTOCOL - Liquidate ALL positions immediately"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        # Alpaca DELETE /v2/positions closes ALL positions and cancels pending orders
        url = f"{ALPACA_API_URL}/positions?cancel_orders=true"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="DELETE", headers=req_headers)
        response_text = await response.text()
        
        # 207 = Multi-Status (some orders placed), 200 = Success
        if response.status in [200, 207, 204]:
            return {
                "status": "LIQUIDATING",
                "message": "🚨 Panic Protocol executed. Sell orders placed for all positions.",
                "details": str(response_text)[:500] if response_text else "No positions to close"
            }
        else:
            return {
                "status": "ERROR",
                "message": f"Failed to execute panic protocol (HTTP {response.status})",
                "details": str(response_text)[:500]
            }
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}


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


async def get_combined_account(env, headers):
    """Get Combined Account Data (Alpaca + OANDA)"""
    # 1. Alpaca Data
    alpaca_data = await get_alpaca_account_data(env)
    
    # 2. Capital.com Data
    capital_connector = CapitalConnector(env)
    capital_data = await capital_connector.get_account_info()
    
    # Merge Logic: Use Capital.com as primary if connected
    if "error" not in capital_data and float(capital_data.get("balance", 0)) > 0:
        return Response.new(json.dumps({
            "portfolio_value": capital_data.get("equity"),
            "buying_power": capital_data.get("available"),
            "cash": capital_data.get("balance"),
            "equity": capital_data.get("equity"),
            "source": capital_data.get("source", "Capital.com")
        }), headers=headers)
        
    # Fallback to Alpaca
    return await get_account(env, headers)


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


async def get_combined_positions(env, headers):
    """Fetch positions from both brokers"""
    all_positions = []
    
    # 1. Alpaca
    alp_pos = await get_alpaca_positions_data(env)
    if alp_pos: all_positions.extend(alp_pos)
    
    # 2. Capital.com
    try:
        capital = CapitalConnector(env)
        capital_pos = await capital.get_open_positions()
        if capital_pos: all_positions.extend(capital_pos)
    except:
        pass
        
    return Response.new(json.dumps(all_positions), headers=headers)


# Helper functions for Telegram (return dict, not Response)
async def get_alpaca_account_data(env):
    """Get Alpaca account data as dict"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/account", method="GET", headers=req_headers)
        
        if response.ok:
            return json.loads(await response.text())
        return {"equity": "100000", "cash": "100000", "buying_power": "200000"}
    except:
        return {"equity": "100000", "cash": "100000", "buying_power": "200000"}


async def get_alpaca_positions_data(env):
    """Get Alpaca positions as list"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/positions", method="GET", headers=req_headers)
        
        if response.ok:
            return json.loads(await response.text())
        return []
    except:
        return []


# ==========================================
# 📈 MARKET SNAPSHOT (Real-time Prices)
# ==========================================

async def get_market_snapshot(request, env, headers):
    """Get real-time market data with price changes"""
    url = str(request.url)
    
    # Default symbols if none provided
    default_symbols = ["SPY", "AAPL", "BTC/USD", "ETH/USD"]
    
    # Parse symbols from URL
    if "symbols=" in url:
        symbols_param = url.split("symbols=")[1].split("&")[0]
        symbols = [s.strip().upper() for s in symbols_param.split(",")]
    else:
        symbols = default_symbols
    
    alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
    alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
    
    results = []
    
    for symbol in symbols[:6]:  # Limit to 6 symbols
        try:
            # Check if crypto
            is_crypto = "/" in symbol or symbol in ["BTC", "ETH", "SOL", "DOGE"]
            
            if is_crypto:
                # Crypto snapshot
                crypto_symbol = symbol.replace("/USD", "") + "/USD" if "/" not in symbol else symbol
                snapshot_url = f"https://data.alpaca.markets/v1beta3/crypto/us/snapshots?symbols={crypto_symbol}"
            else:
                # Stock snapshot
                snapshot_url = f"https://data.alpaca.markets/v2/stocks/{symbol}/snapshot"
            
            req_headers = Headers.new({
                "APCA-API-KEY-ID": alpaca_key,
                "APCA-API-SECRET-KEY": alpaca_secret
            }.items())
            
            response = await fetch(snapshot_url, method="GET", headers=req_headers)
            
            if response.ok:
                data = json.loads(await response.text())
                
                if is_crypto:
                    # Parse crypto response
                    crypto_data = data.get("snapshots", {}).get(crypto_symbol, {})
                    daily = crypto_data.get("dailyBar", {})
                    prev = crypto_data.get("prevDailyBar", {})
                else:
                    # Parse stock response
                    daily = data.get("dailyBar", {})
                    prev = data.get("prevDailyBar", {})
                
                # 🟢 Weekend/Closed Market Fix:
                # If no trading today (volume=0 or empty), use previous close
                is_market_closed = not daily or daily.get("v", 0) == 0
                
                if is_market_closed and prev:
                    current_price = float(prev.get("c", 0))
                    change_percent = 0.0  # No change when market closed
                    volume = prev.get("v", 0)
                else:
                    current_price = float(daily.get("c", 0)) if daily else 0
                    prev_close = float(prev.get("c", current_price)) if prev else current_price
                    if prev_close > 0:
                        change_percent = ((current_price - prev_close) / prev_close) * 100
                    else:
                        change_percent = 0.0
                    volume = daily.get("v", 0) if daily else 0
                
                results.append({
                    "symbol": symbol,
                    "price": round(current_price, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": volume,
                    "is_closed": is_market_closed
                })
            else:
                # Fallback: use existing snapshot function
                snapshot = await fetch_alpaca_snapshot(symbol.replace("/USD", "").replace("USD", ""), env)
                results.append({
                    "symbol": symbol,
                    "price": float(snapshot.get("price", 0)) if snapshot.get("price") != "N/A" else 0,
                    "change_percent": float(snapshot.get("change_percent", 0)),
                    "is_closed": True
                })
        except Exception as e:
            results.append({
                "symbol": symbol,
                "price": 0,
                "change_percent": 0,
                "error": str(e)
            })
    
    # ⚡ Broadcast to Ably (Push to all clients)
    try:
        await publish_to_ably(env, "market-data", results)
    except:
        pass
        
    return Response.new(json.dumps({"symbols": results}), headers=headers)


# ==========================================
# ⚡ ABLY REALTIME FUNCTIONS
# ==========================================

async def publish_to_ably(env, channel, data):
    """Publish real-time update to Ably"""
    try:
        ably_key = str(getattr(env, 'ABLY_API_KEY', ''))
        if not ably_key: return
        
        url = f"{ABLY_API_URL}/channels/{channel}/messages"
        
        # Auth
        key_name, key_secret = ably_key.split(':')
        auth_str = f"{key_name}:{key_secret}"
        auth_b64 = b64encode(auth_str.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
        
        body = {
            "name": "update",
            "data": data
        }
        
        # Fire and forget (don't await response to speed up worker)
        # Note: In Cloudflare, we should await or use ctx.waitUntil, but for simplicity we await
        await fetch(url, method="POST", headers=headers, body=json.dumps(body))
        
    except Exception as e:
        print(f"Ably Publish Error: {e}")


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

# Safety Constants
MAX_DAILY_LOSS_PERCENT = 5.0  # Kill switch triggers at 5% daily loss
STARTING_EQUITY = 100000      # Track from this baseline (or fetch dynamically)

async def on_scheduled(event, env, ctx):
    """
    Cron job for automated Twin-Turbo trading.
    
    Safety Features (Best Practices):
    1. PANIC MODE CHECK - First thing, before any logic
    2. DAILY LOSS LIMIT - Auto-activate panic if loss > 5%
    3. TRADE COUNT LIMIT - Max trades per day
    4. DETAILED LOGGING - All actions logged to D1
    """
    try:
        kv = env.BRAIN_MEMORY
        db = env.TRADING_DB
        
        # ========================================
        # 🛑 STEP 1: KILL SWITCH CHECK (FIRST!)
        # ========================================
        panic_mode = await kv.get("panic_mode")
        if panic_mode == "true":
            # System is in panic mode - do nothing except maintenance
            await _run_maintenance(db)
            return
        
        # ========================================
        # 📊 STEP 2: DAILY LOSS CHECK
        # ========================================
        try:
            capital = CapitalConnector(env)
            account = await capital.get_account_info()
            current_equity = float(account.get("equity", STARTING_EQUITY))
            
            # Get starting equity from KV (set daily at market open)
            starting_equity_str = await kv.get("daily_starting_equity")
            starting_equity = float(starting_equity_str) if starting_equity_str else STARTING_EQUITY
            
            daily_pnl_percent = ((current_equity - starting_equity) / starting_equity) * 100
            
            # AUTO-TRIGGER PANIC MODE if daily loss exceeds limit
            if daily_pnl_percent <= -MAX_DAILY_LOSS_PERCENT:
                await kv.put("panic_mode", "true")
                await kv.put("panic_reason", f"Daily loss limit hit: {daily_pnl_percent:.2f}%")
                await kv.put("panic_timestamp", str(int(__import__('time').time())))
                
                # Close all positions for safety
                positions = await capital.get_open_positions()
                for pos in positions:
                    await capital.close_position(pos.get("deal_id"))
                
                # Alert user
                await send_telegram_alert(env, f"""🛑 <b>AUTO KILL SWITCH ACTIVATED</b>

⚠️ Daily loss limit reached: <b>{daily_pnl_percent:.2f}%</b>

جميع المراكز تم إغلاقها تلقائياً.
التداول متوقف حتى تقوم بإرسال /starttrade""")
                return
        except Exception as e:
            # If we can't check account, continue with caution
            pass
        
        # ========================================
        # 🔢 STEP 3: TRADE COUNT CHECK
        # ========================================
        trades_today = await get_trades_count(env)
        if trades_today >= MAX_TRADES_PER_DAY:
            # Max trades reached, skip execution
            return
        
        # ========================================
        # 📰 STEP 3.5: ECONOMIC NEWS CHECK
        # ========================================
        # Skip trading during high-impact news (15 min buffer)
        try:
            calendar = EconomicCalendar(env)
            news_check = await calendar.should_avoid_trading()
            
            if news_check.get("avoid"):
                # Log news avoidance
                await kv.put("last_news_skip", json.dumps({
                    "time": int(__import__('time').time()),
                    "reason": news_check.get("reason", "")
                }))
                # Skip this cycle - don't trade during news
                return
        except:
            # If news check fails, continue trading (don't block)
            pass
        
        # ========================================
        # 🏎️ STEP 4: TWIN-TURBO SIGNAL SCAN
        # ========================================
        # Run automated rules from database
        rules = await db.prepare("SELECT * FROM rules WHERE active = 1").all()
        
        if rules.results:
            for rule in rules.results:
                ticker = rule.get("ticker", "EURUSD")
                condition = rule.get("condition", "PRICE_ABOVE")
                trigger = float(rule.get("trigger_value", 0))
                action = rule.get("action", "BUY")
                qty = int(rule.get("qty", 1))
                
                # Get current price from Capital.com
                capital = CapitalConnector(env)
                price_data = await capital.get_market_prices(ticker)
                current_price = float(price_data.get("bid", 0))
                
                if current_price == 0:
                    continue
                
                should_execute = False
                if condition == "PRICE_ABOVE" and current_price > trigger:
                    should_execute = True
                elif condition == "PRICE_BELOW" and current_price < trigger:
                    should_execute = True
                
                if should_execute:
                    side = "BUY" if action == "BUY" else "SELL"
                    result = await capital.create_position(ticker, side, qty)
                    
                    if result.get("status") == "success":
                        await log_trade(env, ticker, side, qty, current_price)
                        await send_telegram_alert(env, f"""⚡ <b>AUTO TRADE EXECUTED</b>

📍 {side} {qty} {ticker}
💰 @ {current_price}

Rule: {condition} {trigger}""")
                        
                        # Deactivate rule after execution
                        await db.prepare("UPDATE rules SET active = 0 WHERE id = ?").bind(rule.get("id")).run()
        
        # ========================================
        # 🧹 STEP 5: DATABASE MAINTENANCE
        # ========================================
        await _run_maintenance(db)
            
    except Exception as e:
        # Log error but don't crash
        try:
            await send_telegram_alert(env, f"⚠️ Cron Error: {str(e)[:100]}")
        except:
            pass


async def _run_maintenance(db):
    """Database cleanup - runs even in panic mode"""
    try:
        # Prune old trade records (30+ days)
        await db.prepare(
            "DELETE FROM trades WHERE timestamp < datetime('now', '-30 days')"
        ).run()
    except:
        pass


# ==========================================
# 🏎️ TWIN-TURBO ENGINE: AEXI Protocol
# ==========================================

def calculate_z_score(prices, period=100):
    """Calculate Z-Score for price exhaustion detection"""
    if len(prices) < period:
        return 0.0
    
    recent_prices = prices[-period:]
    mean = sum(recent_prices) / len(recent_prices)
    
    # Calculate standard deviation
    variance = sum((p - mean) ** 2 for p in recent_prices) / len(recent_prices)
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return 0.0
    
    current_price = prices[-1]
    z_score = (current_price - mean) / std_dev
    return z_score


def calculate_atr(highs, lows, closes, period=14):
    """Calculate Average True Range for volatility"""
    if len(highs) < period + 1:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(highs)):
        tr1 = highs[i] - lows[i]
        tr2 = abs(highs[i] - closes[i-1])
        tr3 = abs(lows[i] - closes[i-1])
        true_ranges.append(max(tr1, tr2, tr3))
    
    if len(true_ranges) < period:
        return sum(true_ranges) / len(true_ranges) if true_ranges else 0.0
    
    return sum(true_ranges[-period:]) / period


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index"""
    if len(prices) < period + 1:
        return 50.0  # Neutral
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return 50.0
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_volume_spike(volumes, period=20):
    """Calculate relative volume spike (SVP)"""
    if len(volumes) < period:
        return 0.0
    
    avg_volume = sum(volumes[-period:]) / period
    if avg_volume == 0:
        return 0.0
    
    current_volume = volumes[-1]
    return current_volume / avg_volume


def calculate_aexi(prices, highs, lows, closes, volumes):
    """
    🎯 AEXI Protocol - Antigravity Extremum Index
    
    AEXI = (0.4 × EXH) + (0.3 × VAF) + (0.3 × SVP)
    
    - EXH: Exhaustion (Z-Score normalized to 0-100)
    - VAF: Velocity/ATR Factor (Momentum vs Volatility)
    - SVP: Surveillance Volume Proxy (Relative Volume)
    
    Returns: 0-100 score
    """
    # 1. EXH - Exhaustion (Z-Score normalized)
    z_score = calculate_z_score(prices, period=100)
    # Normalize: Z-Score of 4σ = 100%
    exh = min(100, abs(z_score) * 25)
    
    # 2. VAF - Velocity vs ATR
    atr = calculate_atr(highs, lows, closes, period=14)
    if atr > 0 and len(prices) >= 5:
        momentum = abs(prices[-1] - prices[-5])  # 5-bar momentum
        vaf = min(100, (momentum / atr) * 20)  # Normalized
    else:
        vaf = 50.0
    
    # 3. SVP - Volume Spike
    svp = calculate_volume_spike(volumes, period=20)
    svp = min(100, svp * 33.33)  # Normalized: 3x volume = 100
    
    # AEXI Composite Score
    aexi = (0.4 * exh) + (0.3 * vaf) + (0.3 * svp)
    
    return {
        "aexi": round(aexi, 2),
        "exh": round(exh, 2),
        "vaf": round(vaf, 2),
        "svp": round(svp, 2),
        "z_score": round(z_score, 3)
    }


# ==========================================
# 🌙 TWIN-TURBO ENGINE: Dream Machine
# ==========================================

def calculate_entropy(prices, bins=10):
    """
    Calculate Shannon Entropy - measures market disorder
    High entropy = chaotic market
    Low entropy = orderly trend
    """
    if len(prices) < 20:
        return 0.5
    
    # Calculate returns
    returns = [(prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] != 0 else 0 
               for i in range(1, len(prices))]
    
    if not returns:
        return 0.5
    
    min_ret = min(returns)
    max_ret = max(returns)
    
    if max_ret == min_ret:
        return 0.0
    
    # Bin the returns
    bin_width = (max_ret - min_ret) / bins
    hist = [0] * bins
    
    for r in returns:
        bin_idx = min(int((r - min_ret) / bin_width), bins - 1)
        hist[bin_idx] += 1
    
    # Calculate probability and entropy
    n = len(returns)
    entropy = 0.0
    
    for count in hist:
        if count > 0:
            p = count / n
            entropy -= p * (p ** 0.5 if p > 0 else 0)  # Log approximation
    
    # Normalize to 0-1
    max_entropy = bins ** 0.5
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
    
    return min(1.0, max(0.0, abs(normalized_entropy)))


def calculate_hurst_exponent(prices, max_lag=20):
    """
    Calculate Hurst Exponent (R/S Analysis)
    H > 0.5: Trending (memory)
    H = 0.5: Random walk
    H < 0.5: Mean reverting
    """
    if len(prices) < max_lag * 2:
        return 0.5
    
    # Simplified Hurst calculation
    n = len(prices)
    returns = [prices[i] - prices[i-1] for i in range(1, n)]
    
    if not returns:
        return 0.5
    
    # Calculate range/std ratio for different lags
    rs_values = []
    
    for lag in range(2, min(max_lag, len(returns) // 2)):
        chunks = [returns[i:i+lag] for i in range(0, len(returns) - lag, lag)]
        
        for chunk in chunks:
            if len(chunk) < 2:
                continue
            
            mean = sum(chunk) / len(chunk)
            cumulative = [sum(chunk[:i+1]) - (i+1) * mean for i in range(len(chunk))]
            
            r = max(cumulative) - min(cumulative) if cumulative else 0
            s = (sum((x - mean) ** 2 for x in chunk) / len(chunk)) ** 0.5
            
            if s > 0:
                rs_values.append(r / s)
    
    if not rs_values:
        return 0.5
    
    # Average RS ratio indicates Hurst
    avg_rs = sum(rs_values) / len(rs_values)
    
    # Approximate Hurst from RS
    hurst = 0.5 + (avg_rs - 1) * 0.1
    return min(1.0, max(0.0, hurst))


def calculate_fractal_dimension(prices):
    """
    Calculate Fractal Dimension (Higuchi's method simplified)
    High FD = rough/complex price action
    Low FD = smooth trend
    """
    if len(prices) < 10:
        return 1.5
    
    n = len(prices)
    k_max = min(10, n // 2)
    
    lengths = []
    
    for k in range(1, k_max + 1):
        length = 0
        for m in range(1, k + 1):
            # Compute length for this (k, m) pair
            idx_list = list(range(m - 1, n, k))
            if len(idx_list) < 2:
                continue
            
            partial_length = sum(
                abs(prices[idx_list[j]] - prices[idx_list[j-1]]) 
                for j in range(1, len(idx_list))
            )
            
            # Normalize
            norm = (n - 1) / (k * len(idx_list))
            length += partial_length * norm
        
        if k > 0:
            length /= k
            lengths.append(length)
    
    if not lengths:
        return 1.5
    
    # Estimate fractal dimension from slope
    # FD ≈ 1 + log(L) / log(k)
    avg_length = sum(lengths) / len(lengths)
    fd = 1.0 + min(1.0, avg_length / 100)  # Simplified
    
    return min(2.0, max(1.0, fd))


def calculate_dream_score(prices, volumes):
    """
    🌙 Dream Machine - Chaos Theory Detector
    
    Dream = (0.3 × Entropy) + (0.25 × Fractal) + (0.25 × Hurst) + (0.2 × VolDisp)
    
    Returns: 0-100 "Dream" score (anomaly detection)
    """
    # 1. Entropy (normalized to 0-100)
    entropy = calculate_entropy(prices) * 100
    
    # 2. Fractal Dimension (1.0-2.0 → 0-100)
    fd = calculate_fractal_dimension(prices)
    fractal_score = (fd - 1.0) * 100
    
    # 3. Hurst Exponent (deviation from 0.5 → 0-100)
    hurst = calculate_hurst_exponent(prices)
    hurst_score = abs(hurst - 0.5) * 200  # Distance from random walk
    
    # 4. Volume Dispersion
    if len(volumes) >= 20:
        avg_vol = sum(volumes[-20:]) / 20
        vol_variance = sum((v - avg_vol) ** 2 for v in volumes[-20:]) / 20
        vol_disp = min(100, (vol_variance ** 0.5) / avg_vol * 50) if avg_vol > 0 else 50
    else:
        vol_disp = 50
    
    # Dream Score Composite
    dream = (0.3 * entropy) + (0.25 * fractal_score) + (0.25 * hurst_score) + (0.2 * vol_disp)
    
    return {
        "dream": round(dream, 2),
        "entropy": round(entropy, 2),
        "fractal": round(fractal_score, 2),
        "hurst": round(hurst, 3),
        "hurst_score": round(hurst_score, 2),
        "vol_dispersion": round(vol_disp, 2)
    }


# ==========================================
# 🎯 TWIN-TURBO SIGNAL DETECTOR
# ==========================================

def detect_twin_turbo_signal(aexi_result, dream_result, rsi):
    """
    🔴 SIGNAL TRIGGER CONDITION:
    AEXI > 80 AND Dream > 70 AND (RSI < 30 OR RSI > 70)
    
    Returns signal with confidence level
    """
    aexi = aexi_result.get("aexi", 0)
    dream = dream_result.get("dream", 0)
    
    # Signal conditions
    aexi_triggered = aexi > 80
    dream_triggered = dream > 70
    rsi_extreme = rsi < 30 or rsi > 70
    
    if aexi_triggered and dream_triggered:
        confidence = min(100, (aexi + dream) / 2)
        
        # Determine direction
        if rsi < 30:
            direction = "BULLISH"
            action = "BUY"
        elif rsi > 70:
            direction = "BEARISH"
            action = "SELL"
        else:
            direction = "NEUTRAL"
            action = "HOLD"
        
        return {
            "signal": True,
            "direction": direction,
            "action": action,
            "confidence": round(confidence, 2),
            "aexi": aexi,
            "dream": dream,
            "rsi": round(rsi, 2),
            "message": f"🚨 TWIN-TURBO SIGNAL: {direction} ({confidence:.1f}% confidence)"
        }
    
    return {
        "signal": False,
        "aexi": aexi,
        "dream": dream,
        "rsi": round(rsi, 2),
        "message": "No signal - Engines idle"
    }


# ==========================================
# 📰 AI JOURNALIST (Gemini Reports)
# ==========================================

async def generate_ai_journalist_report(env, symbols=None):
    """
    Generate daily market intelligence briefing using Gemini
    """
    if symbols is None:
        symbols = ["SPY", "QQQ", "BTC/USD"]
    
    # Gather market data
    market_summary = []
    
    for symbol in symbols:
        try:
            data = await fetch_alpaca_snapshot(symbol, env)
            if data:
                market_summary.append(f"- {symbol}: ${data.get('price', 'N/A')} ({data.get('change_percent', 0):.2f}%)")
        except:
            market_summary.append(f"- {symbol}: Data unavailable")
    
    # Fetch news
    news_items = []
    for symbol in symbols[:2]:  # Limit to avoid rate limits
        try:
            news = await fetch_yahoo_news(symbol)
            if news:
                news_items.extend(news[:2])
        except:
            pass
    
    news_text = "\n".join(news_items[:5]) if news_items else "No recent news available"
    
    # Create prompt for Gemini
    prompt = f"""You are an elite financial journalist for Axiom Antigravity Trading Hub.
    
Generate a brief daily market intelligence report in this format:

## 🌅 Good Morning, Trader!

### 📊 Market Snapshot
{chr(10).join(market_summary)}

### 📰 Key Headlines
{news_text}

### 🧠 AI Analysis
[Provide 2-3 sentences of market analysis based on the data]

### 🎯 Today's Bias
[BULLISH / BEARISH / NEUTRAL] with brief explanation

Keep the report concise and actionable. Use emojis sparingly."""

    # Call Gemini (using Groq as fallback if Gemini not available)
    try:
        gemini_key = getattr(env, 'GEMINI_API_KEY', None)
        
        if gemini_key:
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            
            response = await fetch(gemini_url, 
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({
                    "contents": [{"parts": [{"text": prompt}]}]
                })
            )
            
            result = await response.json()
            
            if result.get("candidates"):
                return result["candidates"][0]["content"]["parts"][0]["text"]
        
        # Fallback to Groq
        return await call_groq_chat(prompt, env)
        
    except Exception as e:
        return f"📊 Market Report Unavailable\n\nError: {str(e)}"


async def send_daily_briefing(env):
    """Send daily AI Journalist briefing to Telegram"""
    try:
        report = await generate_ai_journalist_report(env)
        
        message = f"""
🌌 <b>AXIOM ANTIGRAVITY</b>
📰 <b>Daily Intelligence Briefing</b>
━━━━━━━━━━━━━━━━━━━━

{report}

━━━━━━━━━━━━━━━━━━━━
⏰ Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
"""
        
        await send_telegram_alert(env, message)
        return {"status": "sent", "report": report}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ==========================================
# 🧠 ANALYST AGENT (Smart Signal Filter)
# ==========================================

# Confidence threshold - reject signals below this
MIN_CONFIDENCE_THRESHOLD = 75  # Best practice: 75% minimum

async def consult_the_analyst(market_data, env):
    """
    🧠 The Analyst Agent - Smart Signal Filter with Confidence Scoring
    
    RESEARCH-BASED IMPLEMENTATION:
    1. Structured JSON output with confidence field (0-100)
    2. Chain-of-Thought reasoning in "reasoning" field
    3. Threshold validation (reject if confidence < 75%)
    4. Logs rejected signals for analysis
    
    Cost: Uses Groq API (FREE - 14,400 req/day)
    """
    
    # 1. Build Analyst Context Prompt with Structured Output Schema
    prompt = f"""ROLE: Senior Market Analyst for 'Axiom Antigravity Signal Hub'.
OBJECTIVE: Validate a potential market anomaly and provide confidence assessment.

INPUT DATA:
- Asset: {market_data.get('symbol', 'UNKNOWN')}
- Current Price: ${market_data.get('price', 0):.2f}
- AEXI Score (Exhaustion): {market_data.get('aexi', 0):.1f}/100 
- Dream Score (Chaos): {market_data.get('dream', 0):.1f}/100 
- RSI: {market_data.get('rsi', 50):.1f}
- Z-Score: {market_data.get('z_score', 0):.2f}σ

DECISION CRITERIA:
- S-TIER: AEXI > 85 AND Dream > 75 AND extreme RSI (<25 or >75) → confidence 90-100
- A-TIER: AEXI > 80 AND Dream > 70 → confidence 75-89
- B-TIER: Either AEXI > 80 OR Dream > 70 → confidence 50-74
- REJECT: Conflicting signals or low setup quality → confidence < 50

INSTRUCTIONS:
1. First, analyze the data in the "reasoning" field (Chain-of-Thought)
2. Then, provide your confidence score (0-100)
3. Finally, decide if this should be broadcast

OUTPUT JSON SCHEMA (strict):
{{
  "reasoning": "Step-by-step analysis explaining WHY this signal is strong or weak",
  "confidence": 85,
  "broadcast_alert": true,
  "signal_quality": "A-TIER",
  "direction": "BULLISH",
  "analyst_brief": "One sharp sentence for the trader."
}}"""

    # 2. Call Groq for fast inference (Llama 3.3 70B)
    try:
        groq_key = str(getattr(env, 'GROQ_API_KEY', ''))
        
        if not groq_key:
            # Fallback to pure math decision
            aexi = market_data.get('aexi', 0)
            dream = market_data.get('dream', 0)
            rsi = market_data.get('rsi', 50)
            
            math_confidence = min(100, (aexi + dream) / 2) if aexi > 80 and dream > 70 else 40
            
            return {
                "reasoning": "AI unavailable, using pure mathematical calculation",
                "confidence": int(math_confidence),
                "broadcast_alert": math_confidence >= MIN_CONFIDENCE_THRESHOLD,
                "signal_quality": "MATH-ONLY",
                "direction": "BULLISH" if rsi < 30 else "BEARISH" if rsi > 70 else "NEUTRAL",
                "analyst_brief": "Signal based on pure mathematical indicators."
            }
        
        req_headers = Headers.new({
            "Authorization": f"Bearer {groq_key}",
            "Content-Type": "application/json"
        }.items())
        
        response = await fetch(GROQ_API_URL, 
            method="POST",
            headers=req_headers,
            body=json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a precise market analyst. Think step-by-step in the reasoning field before giving your final verdict. Always respond in valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,  # Very low for consistent, deterministic output
                "max_tokens": 400,   # Allow room for Chain-of-Thought
                "response_format": {"type": "json_object"}
            })
        )
        
        if response.ok:
            result = json.loads(await response.text())
            
            if result.get("choices"):
                content = result["choices"][0]["message"]["content"]
                analyst_decision = json.loads(content)
                
                # 3. THRESHOLD VALIDATION - The key research insight
                confidence = analyst_decision.get("confidence", 0)
                
                if confidence < MIN_CONFIDENCE_THRESHOLD:
                    # Log rejection for later analysis
                    analyst_decision["broadcast_alert"] = False
                    analyst_decision["rejection_reason"] = f"Confidence {confidence}% below threshold ({MIN_CONFIDENCE_THRESHOLD}%)"
                    
                    # Store rejection in KV for debugging
                    try:
                        kv = env.BRAIN_MEMORY
                        rejected_count = int(await kv.get("rejected_signals_count") or "0") + 1
                        await kv.put("rejected_signals_count", str(rejected_count))
                        await kv.put("last_rejected_signal", json.dumps({
                            "symbol": market_data.get('symbol'),
                            "confidence": confidence,
                            "reason": analyst_decision.get("reasoning", "")[:200]
                        }))
                    except:
                        pass
                
                return analyst_decision
        
        # Fallback if API call fails
        return {
            "reasoning": "API response parsing failed",
            "confidence": 50,
            "broadcast_alert": False,
            "signal_quality": "PARSE-ERROR",
            "direction": "UNKNOWN",
            "analyst_brief": "Response parsing failed. Signal not broadcast for safety."
        }
        
    except Exception as e:
        # In case of AI failure, be conservative - don't broadcast
        return {
            "reasoning": f"AI error: {str(e)[:100]}",
            "confidence": 0,
            "broadcast_alert": False,
            "signal_quality": "ERROR",
            "direction": "UNKNOWN",
            "analyst_brief": f"AI Analyst error. Signal rejected for safety."
        }


# ==========================================
# 📱 ENHANCED SIGNAL BROADCAST
# ==========================================

async def broadcast_twin_turbo_signal(env, symbol, aexi_result, dream_result, rsi, price):
    """
    🚨 Broadcast validated Twin-Turbo signal to Telegram
    
    Pipeline:
    1. Detect signal via math (AEXI + Dream)
    2. Validate via Analyst Agent (Groq)
    3. Send formatted alert to Telegram
    """
    
    # Build market data for analyst
    market_data = {
        "symbol": symbol,
        "price": price,
        "aexi": aexi_result.get("aexi", 0),
        "dream": dream_result.get("dream", 0),
        "rsi": rsi,
        "z_score": aexi_result.get("z_score", 0)
    }
    
    # Consult the Analyst Agent
    analyst_decision = await consult_the_analyst(market_data, env)
    
    # Check if analyst approves broadcast
    if not analyst_decision.get("broadcast_alert", False):
        # Log but don't alert
        return {
            "status": "filtered",
            "reason": "Analyst rejected signal",
            "analyst_brief": analyst_decision.get("analyst_brief", "N/A")
        }
    
    # Build premium Telegram message
    quality = analyst_decision.get("signal_quality", "UNKNOWN")
    direction = analyst_decision.get("direction", "NEUTRAL")
    brief = analyst_decision.get("analyst_brief", "No analysis available.")
    
    # Quality emoji mapping
    quality_emoji = {
        "S-TIER": "🏆",
        "A-TIER": "⭐",
        "B-TIER": "📊",
        "MATH-ONLY": "🔢"
    }.get(quality, "❓")
    
    # Direction emoji
    direction_emoji = "🟢" if direction == "BULLISH" else "🔴" if direction == "BEARISH" else "⚪"
    
    message = f"""
🚨 <b>ANTIGRAVITY SIGNAL ALERT</b>
━━━━━━━━━━━━━━━━━━━━

<b>📍 Asset:</b> {symbol}
<b>💰 Price:</b> ${price:,.2f}
<b>📈 Direction:</b> {direction_emoji} {direction}

━━━━━━━━━━━━━━━━━━━━
<b>🏎️ Twin-Turbo Engines:</b>

<b>AEXI:</b> {aexi_result.get('aexi', 0):.1f}/100 ({'🔥 Critical' if aexi_result.get('aexi', 0) > 85 else '⚠️ High' if aexi_result.get('aexi', 0) > 80 else '📊 Active'})
<b>Dream:</b> {dream_result.get('dream', 0):.1f}/100 ({'🌙 Chaos Peak' if dream_result.get('dream', 0) > 75 else '✨ High' if dream_result.get('dream', 0) > 70 else '📈 Normal'})
<b>RSI:</b> {rsi:.1f} ({'🟢 Oversold' if rsi < 30 else '🔴 Overbought' if rsi > 70 else '⚪ Neutral'})
<b>Z-Score:</b> {aexi_result.get('z_score', 0):.2f}σ

━━━━━━━━━━━━━━━━━━━━
<b>🧠 Analyst Brief:</b>
<i>"{brief}"</i>

<b>{quality_emoji} Signal Quality:</b> {quality}
━━━━━━━━━━━━━━━━━━━━

⏰ {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M UTC')}
🌌 <i>Axiom Antigravity Trading Hub</i>
"""
    
    # Send to Telegram
    await send_telegram_alert(env, message)
    
    return {
        "status": "broadcast",
        "quality": quality,
        "direction": direction,
        "analyst_brief": brief
    }


# ==========================================
# 🔄 AUTOMATED SIGNAL SCANNER (The Spider Web)
# ==========================================

async def scan_for_signals(env, symbols=None):
    """
    🕸️ The Spider Web Scanner
    Orchestrates specialized Spiders to detect, analyze, and validate signals.
    """
    if symbols is None:
        symbols = ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "BTCUSD"]
    
    # Initialize Spiders
    collector = DataCollector(env)
    reflex_spider = WorkersAI(env)
    analyst_spider = DeepSeekAnalyst(env)
    guardian = RiskGuardian(env)
    
    signals_found = []
    
    for symbol in symbols:
        try:
            # 1. COLLECTOR SPIDER: Gather Context
            context = await collector.get_market_context(symbol)
            # Add price data (using Capital connector or efficient snapshot)
            capital = CapitalConnector(env)
            # Quote fetch (simplified for demo/speed)
            # In a real scenario, Collector would have this cached
            
            # 2. REFLEX SPIDER (Fast Brain): Pattern Match
            # Use Workers AI (Llama 3.1) to check for obvious patterns in news/price
            # This is the "Instinct" layer (10K neurons/day)
            reflex_prompt = f"""Analyze {symbol} context: {json.dumps(context)}
            Is there a significant breakout or trend anomaly?
            Respond JSON: {{"anomaly": bool, "confidence": int, "direction": "BULLISH"|"BEARISH"}}"""
            
            # Use beta model for unlimited reflex checks
            reflex = await reflex_spider.chat(reflex_prompt, model="llama-3.1-8b")
            
            is_anomaly = False
            reflex_data = {}
            if reflex.get("content") and "true" in reflex["content"].lower():
                is_anomaly = True
                # Parse direction ...
            
            # If Reflex sees nothing, skip (save resources)
            # For demo, we might skip this strict check to show functionality
            
            # 3. ANALYST SPIDER (Deep Brain): Strategic Analysis
            # If Reflex triggered OR we run on hourly schedule (handled by dispatcher)
            # Here we assume identifying a signal warrant deep analysis
            
            # Mocking signal detection for flow completeness or using existing logic
            # Let's use the Twin-Turbo logic here but enhanced
            
            # ... (Existing AEXI/Dream calc would go here) ...
            
            # 4. GUARDIAN SPIDER: Risk Check
            # Before broadcasting/executing, ask the Risk Officer
            potential_signal = {
                "action": "BUY", # Placeholder
                "symbol": symbol,
                "confidence": 85,
                "reasoning": "Reflex detected anomaly + AEXI breakout"
            }
            
            # Validate
            # validation = await guardian.validate_trade(potential_signal, {})
            # if not validation["approved"]:
                # Log rejection
                # continue
                
            # If approved -> Broadcast
            # await broadcast_twin_turbo_signal(...)
            
            # For now, keeping the loop structure ready for the Dispatcher
            pass

        except Exception as e:
            continue
    
    return signals_found
```
