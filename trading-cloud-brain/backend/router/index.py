"""
🚪 AXIOM ROUTER WORKER
The Only Public-Facing Gateway

Responsibilities:
- Validate X-Proxy-Signature from Next.js
- Rate Limiting
- Route to internal TRADING_BRAIN or DREAM_ENGINE
- CORS handling

All other workers are INTERNAL ONLY (no public access).
"""

from js import Response, Headers
import json
import hmac
import hashlib
import time

# ==========================================
# 🛡️ SIGNATURE VERIFICATION
# ==========================================

def verify_proxy_signature(request, env) -> bool:
    """
    Verify that request came from our Next.js proxy.
    Uses HMAC-SHA256 signature.
    """
    signature = request.headers.get('X-Proxy-Signature')
    timestamp = request.headers.get('X-Proxy-Timestamp')
    
    if not signature or not timestamp:
        return False
    
    # Check timestamp freshness (5 minute window)
    try:
        ts = int(timestamp)
        if abs(time.time() * 1000 - ts) > 300000:  # 5 minutes
            return False
    except:
        return False
    
    # Verify HMAC signature
    secret = str(getattr(env, 'PROXY_SECRET', ''))
    if not secret:
        return False
    
    expected = hmac.new(
        secret.encode(),
        timestamp.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)


# ==========================================
# 🚦 RATE LIMITING
# ==========================================

async def check_rate_limit(env, user_id: str, endpoint: str) -> tuple:
    """
    Token bucket rate limiting using KV.
    Returns (allowed: bool, remaining: int)
    """
    key = f"rate:{user_id}:{endpoint}"
    limit = 60  # requests per minute
    window = 60  # seconds
    
    try:
        data = await env.RATE_LIMIT_KV.get(key)
        current_time = int(time.time())
        
        if data:
            bucket = json.loads(data)
            window_start = bucket.get("window_start", current_time)
            count = bucket.get("count", 0)
            
            if current_time - window_start >= window:
                bucket = {"window_start": current_time, "count": 1}
            elif count >= limit:
                return False, 0
            else:
                bucket["count"] = count + 1
        else:
            bucket = {"window_start": current_time, "count": 1}
        
        await env.RATE_LIMIT_KV.put(key, json.dumps(bucket), expirationTtl=window * 2)
        return True, limit - bucket["count"]
    except Exception as e:
        # Fail open on error
        return True, limit


# ==========================================
# 🌐 CORS HEADERS
# ==========================================

def get_cors_headers():
    return {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Proxy-Signature, X-Proxy-Timestamp, X-Proxy-User-Id"
    }


# ==========================================
# 🚀 MAIN ROUTER
# ==========================================

async def on_fetch(request, env):
    """
    Main HTTP Entry Point - Routes to internal workers.
    """
    url = str(request.url)
    method = str(request.method)
    headers = Headers.new(get_cors_headers().items())
    
    # Handle CORS preflight
    if method == "OPTIONS":
        return Response.new("", headers=headers)
    
    # ===== PUBLIC ENDPOINTS (no auth) =====
    if "/api/status" in url or "/api/health" in url:
        return Response.new(json.dumps({
            "name": "Axiom Router",
            "version": "4.0",
            "status": "🟢 Online",
            "architecture": "Micro-Workers"
        }), headers=headers)
    
    # ===== SIGNATURE VERIFICATION =====
    if not verify_proxy_signature(request, env):
        return Response.new(json.dumps({
            "error": "⛔ Invalid Proxy Signature",
            "message": "Direct access to workers is forbidden. Use the Next.js proxy."
        }), status=403, headers=headers)
    
    # Get user ID from proxy headers
    user_id = request.headers.get('X-Proxy-User-Id', 'anonymous')
    
    # ===== RATE LIMITING =====
    endpoint = url.split('/')[-1].split('?')[0]
    allowed, remaining = await check_rate_limit(env, user_id, endpoint)
    
    if not allowed:
        return Response.new(json.dumps({
            "error": "🚦 Rate Limit Exceeded",
            "retry_after": 60
        }), status=429, headers=headers)
    
    # ===== ROUTE TO INTERNAL WORKERS =====
    
    # Trading Brain (main logic)
    if "/api/trading" in url or "/api/dashboard" in url or "/api/positions" in url:
        return await env.TRADING_BRAIN.fetch(request)
    
    # Dream Engine (math/chaos)
    if "/api/math" in url or "/api/chaos" in url or "/api/analyze" in url:
        return await env.DREAM_ENGINE.fetch(request)
    
    # MCP (AI signals)
    if "/api/mcp" in url or "/api/signals" in url:
        return await env.TRADING_BRAIN.fetch(request)
    
    # Chat (AI)
    if "/api/chat" in url:
        return await env.TRADING_BRAIN.fetch(request)
    
    # Default: Not found
    return Response.new(json.dumps({
        "error": "🔍 Endpoint Not Found",
        "available": ["/api/trading", "/api/math", "/api/mcp", "/api/chat"]
    }), status=404, headers=headers)
