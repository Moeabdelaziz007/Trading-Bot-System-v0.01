from js import Response, Headers
import json

# ==========================================
# 🧠 TRADING BRAIN - Cloudflare Python Worker
# Simplified version for stability
# ==========================================

def on_fetch(request, env):
    """
    Synchronous handler - more stable for Cloudflare Python Workers
    """
    url = str(request.url)
    method = str(request.method)
    
    # CORS Headers
    headers = Headers.new({
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }.items())
    
    # Handle CORS preflight
    if method == "OPTIONS":
        return Response.new("", headers=headers)
    
    # ============ API ROUTES ============
    
    # Trade endpoint (Demo)
    if "api/trade" in url:
        result = {
            "status": "success",
            "order_id": "ORD-DEMO-001",
            "message": "✅ Demo Order Executed Successfully!",
            "symbol": "BTCUSD",
            "side": "buy",
            "qty": 1,
            "price": 98500,
            "filled": True,
            "mode": "demo"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Status endpoint
    if "api/status" in url:
        result = {
            "status": "online",
            "ai_status": "ready",
            "mode": "demo",
            "strategy_bias": "BULLISH",
            "message": "Sentinel Brain Online 🟢"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Market data endpoint
    if "api/market" in url:
        # Demo market data
        result = {
            "symbol": "BTC/USDT",
            "price": 98500,
            "change": 1250,
            "change_percent": 1.28,
            "high": 99500,
            "low": 97200,
            "volume": 1500000000,
            "asset_type": "crypto",
            "timestamp": "2025-12-06T15:00:00Z"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Brain status endpoint
    if "api/brain" in url:
        result = {
            "strategic_engine": {
                "model": "DeepSeek V3",
                "status": "active",
                "bias": "BULLISH"
            },
            "execution_engine": {
                "model": "Gemini Flash",
                "status": "ready"
            },
            "last_analysis": "BTC showing bullish momentum",
            "updated_at": "2025-12-06T15:00:00Z"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Chat endpoint (simplified - no external API for stability)
    if "api/chat" in url:
        result = {
            "reply": "🤖 Sentinel AI is online! I'm currently operating in demo mode. The market bias is BULLISH. How can I assist with your trading today?",
            "status": "success"
        }
        return Response.new(json.dumps(result), headers=headers)
    
    # Default response
    result = {
        "status": "online",
        "message": "Sentinel Trading Brain Online 🟢",
        "version": "1.0.0",
        "endpoints": ["/api/chat", "/api/trade", "/api/market", "/api/status", "/api/brain"]
    }
    return Response.new(json.dumps(result), headers=headers)
