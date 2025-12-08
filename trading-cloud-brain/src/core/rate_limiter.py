"""
🚦 Rate Limiter for Axiom Antigravity Trading System
Implements IP-based rate limiting using KV storage.

Features:
- Token bucket algorithm
- Per-endpoint limits
- KV-based persistence
- Rate limit headers in response

Usage:
    limiter = RateLimiter(env.BRAIN_MEMORY)
    allowed, info = await limiter.check(client_ip, endpoint)
    if not allowed:
        return rate_limit_response(info)
"""


class RateLimitConfig:
    """Rate limit configuration for different endpoints."""
    
    # Format: (requests_per_window, window_seconds)
    ENDPOINTS = {
        # Public endpoints - more generous
        "/api/status": (60, 60),           # 60 req/min
        "/api/market": (30, 60),           # 30 req/min
        "/api/candles": (20, 60),          # 20 req/min
        
        # AI endpoints - limited due to API costs
        "/api/chat": (10, 60),             # 10 req/min
        "/api/analyze": (5, 60),           # 5 req/min
        
        # Trading endpoints - strict limits
        "/api/trade": (5, 60),             # 5 trades/min
        "/api/panic": (1, 300),            # 1 panic/5min
        
        # Telegram - moderate
        "/telegram/webhook": (30, 60),     # 30 msg/min
        
        # Default for unlisted endpoints
        "default": (30, 60)                # 30 req/min
    }


class RateLimiter:
    """
    🚦 Token Bucket Rate Limiter using KV Storage.
    
    Attributes:
        kv: KV namespace for storing rate limit data
    """
    
    def __init__(self, kv):
        """
        Initialize rate limiter.
        
        Args:
            kv: Cloudflare KV namespace (env.BRAIN_MEMORY)
        """
        self.kv = kv
    
    async def check(self, client_ip: str, endpoint: str) -> tuple:
        """
        Check if request is allowed under rate limit.
        
        Args:
            client_ip: Client IP address
            endpoint: Request endpoint path
        
        Returns:
            tuple: (allowed: bool, info: dict)
                - allowed: True if request is allowed
                - info: Rate limit info (remaining, reset, limit)
        """
        import time
        
        # Get config for endpoint
        config = self._get_config(endpoint)
        limit, window = config
        
        # Build KV key: rate:{ip}:{endpoint_hash}
        key = f"rate:{client_ip}:{self._hash_endpoint(endpoint)}"
        
        try:
            # Get current counter
            data = await self.kv.get(key)
            current_time = int(time.time())
            
            if data:
                # Parse existing data
                import json
                bucket = json.loads(data)
                window_start = bucket.get("window_start", current_time)
                count = bucket.get("count", 0)
                
                # Check if window has expired
                if current_time - window_start >= window:
                    # Reset window
                    bucket = {"window_start": current_time, "count": 1}
                else:
                    # Check limit
                    if count >= limit:
                        # Rate limited!
                        reset_at = window_start + window
                        return False, {
                            "limited": True,
                            "limit": limit,
                            "remaining": 0,
                            "reset": reset_at,
                            "retry_after": reset_at - current_time
                        }
                    else:
                        # Increment counter
                        bucket["count"] = count + 1
            else:
                # New bucket
                bucket = {"window_start": current_time, "count": 1}
            
            # Save updated bucket (expires after window)
            import json
            await self.kv.put(key, json.dumps(bucket), expirationTtl=window * 2)
            
            # Return success with headers
            return True, {
                "limited": False,
                "limit": limit,
                "remaining": limit - bucket["count"],
                "reset": bucket["window_start"] + window
            }
            
        except Exception as e:
            # On error, allow request (fail open)
            print(f"⚠️ Rate limiter error: {e}")
            return True, {"limited": False, "error": str(e)}
    
    def _get_config(self, endpoint: str) -> tuple:
        """Get rate limit config for endpoint."""
        # Exact match
        if endpoint in RateLimitConfig.ENDPOINTS:
            return RateLimitConfig.ENDPOINTS[endpoint]
        
        # Partial match (for paths like /api/trade?symbol=X)
        for path, config in RateLimitConfig.ENDPOINTS.items():
            if endpoint.startswith(path):
                return config
        
        # Default
        return RateLimitConfig.ENDPOINTS["default"]
    
    def _hash_endpoint(self, endpoint: str) -> str:
        """Create short hash of endpoint for KV key."""
        # Use first path segment only
        parts = endpoint.split("?")[0].split("/")
        if len(parts) >= 3:
            return parts[2][:10]  # e.g., "trade", "status"
        return "default"
    
    @staticmethod
    def get_headers(info: dict) -> dict:
        """
        Get rate limit headers for response.
        
        Args:
            info: Rate limit info from check()
        
        Returns:
            dict: Headers to add to response
        """
        return {
            "X-RateLimit-Limit": str(info.get("limit", 0)),
            "X-RateLimit-Remaining": str(info.get("remaining", 0)),
            "X-RateLimit-Reset": str(info.get("reset", 0))
        }


def rate_limit_response(info: dict) -> dict:
    """
    Create a rate limit exceeded response.
    
    Args:
        info: Rate limit info from check()
    
    Returns:
        dict: Response body for 429 error
    """
    return {
        "error": "Rate limit exceeded",
        "code": "RATE_LIMIT_EXCEEDED",
        "retry_after": info.get("retry_after", 60),
        "message": f"Too many requests. Try again in {info.get('retry_after', 60)} seconds."
    }
