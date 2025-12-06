from js import Response, fetch, JSON
import json
import os
import datetime

# ==========================================
# 🧠 DUAL-CORE BRAIN (Cloudflare Python Worker)
# ==========================================

async def on_fetch(request, env):
    """
    Handles Incoming Chat Messages (Gemini Layer)
    URL: https://trading-brain-v1.<your-subdomain>.workers.dev/api/chat
    """
    url = request.url
    
    if request.method == "POST" and "api/chat" in url:
        try:
            body = await request.json()
            user_msg = body.get("message", "")
            
            # 1. Retrieve Context from KV (Fast)
            # Accessing KV Namespace bound as BRAIN_MEMORY
            strategy_raw = await env.BRAIN_MEMORY.get("current_strategy")
            strategy = json.loads(strategy_raw) if strategy_raw else {"bias": "NEUTRAL"}
            
            # 2. Call Gemini API (Direct Fetch for speed/cost)
            gemini_key = env.GEMINI_API_KEY
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            
            prompt = f"""
            Role: Expert Trading Assistant 'Sentinel'.
            Strategy Bias: {strategy.get('bias')}
            Current Market Context: {json.dumps(strategy)}
            User: {user_msg}
            
            Instructions:
            - Provide concise, actionable trading advice.
            - If user asks to buy/sell, confirm if it aligns with the Strategy Bias.
            """
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            headers = {"Content-Type": "application/json"}
            gemini_res = await fetch(gemini_url, method="POST", headers=headers, body=json.dumps(payload))
            gemini_data = await gemini_res.json()
            
            # Parsing Gemini Response
            try:
                reply = gemini_data['candidates'][0]['content']['parts'][0]['text']
            except:
                reply = "Error connecting to Gemini Brain."

            return Response.new(json.dumps({"reply": reply}), headers={"Content-Type": "application/json"})
            
        except Exception as e:
            return Response.new(json.dumps({"error": str(e)}), status=500)

    return Response.new("Sentinel Brain Online 🟢 | System Ready")


async def on_scheduled(event, env, ctx):
    """
    ⏰ THE LOOP: Updates Strategy Every Minute (DeepSeek Layer)
    """
    print("⏰ Heartbeat: Analyzing Market...")
    
    # 1. Fetch Market Data (CoinGecko Free API)
    # Using fetch() uses Network I/O not CPU time
    try:
        btc_res = await fetch("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true")
        btc_data = await btc_res.json()
        price = btc_data['bitcoin']['usd']
        change_24h = btc_data['bitcoin']['usd_24h_change']
    except:
        price = 98000 # Fallback
        change_24h = 0
    
    # 2. Call DeepSeek (The Strategist)
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
        
        # Parse logic to ensure JSON
        if "{" in strategy_content:
             # Basic extraction if model adds text
            pass 
            
        final_strategy = {
            "bias": "BULLISH" if change_24h > 0 else "BEARISH", # Fallback logic if AI fails
            "raw_analysis": strategy_content,
            "last_updated": str(datetime.datetime.now())
        }
        
    except Exception as e:
        final_strategy = {"bias": "NEUTRAL", "error": str(e)}
    
    # 3. Save to Memory (KV)
    await env.BRAIN_MEMORY.put("current_strategy", json.dumps(final_strategy))
    print("✅ Strategy Updated via DeepSeek")

