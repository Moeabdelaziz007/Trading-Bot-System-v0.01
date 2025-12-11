"""
🚦 AI GATEKEEPER - Rate Limiting & Caching for AI API Calls
Protects against free tier violations (Gemini: 15 RPM limit)

This module implements:
1. Rate limiting (14 req/min safety margin)
2. Response caching (5 min TTL)
3. Fallback mechanisms when rate limited
"""

import time
from collections import deque
from typing import Optional, Dict, Any
import json
import hashlib


class AIGatekeeper:
    """
    The AI Gatekeeper prevents API rate limit violations by:
    - Tracking request timestamps in a sliding window
    - Caching responses to avoid duplicate calls
    - Falling back to heuristics when rate limited
    """
    
    def __init__(self, limit: int = 14, window: int = 60, cache_ttl: int = 300):
        """
        Args:
            limit: Max requests per window (14 < 15 for safety)
            window: Time window in seconds (60 = 1 minute)
            cache_ttl: Cache TTL in seconds (300 = 5 minutes)
        """
        self.request_timestamps = deque()
        self.LIMIT = limit
        self.WINDOW = window
        self.CACHE_TTL = cache_ttl
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "rate_limited": 0,
            "api_calls": 0
        }
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate a hash key for caching"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        return time.time() - cache_entry.get("timestamp", 0) < self.CACHE_TTL
    
    def _clean_old_timestamps(self):
        """Remove timestamps outside the current window"""
        current_time = time.time()
        while self.request_timestamps and self.request_timestamps[0] < current_time - self.WINDOW:
            self.request_timestamps.popleft()
    
    def _can_make_request(self) -> bool:
        """Check if we're within rate limits"""
        self._clean_old_timestamps()
        return len(self.request_timestamps) < self.LIMIT
    
    async def ask(self, prompt: str, model: str = "gemini-1.5-flash", fallback_fn=None) -> Dict[str, Any]:
        """
        Smart AI request with caching and rate limiting
        
        Args:
            prompt: The prompt to send
            model: The model to use
            fallback_fn: Optional fallback function when rate limited
        
        Returns:
            Response dict with 'response', 'source', and metadata
        """
        self.stats["total_requests"] += 1
        cache_key = self._get_cache_key(prompt)
        
        # 1. Check Cache First
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            self.stats["cache_hits"] += 1
            return {
                "response": self.cache[cache_key]["response"],
                "source": "cache",
                "cached_at": self.cache[cache_key]["timestamp"],
                "model": model
            }
        
        # 2. Check Rate Limit
        if not self._can_make_request():
            self.stats["rate_limited"] += 1
            
            # Try fallback
            if fallback_fn:
                fallback_response = await fallback_fn(prompt)
                return {
                    "response": fallback_response,
                    "source": "fallback",
                    "reason": "rate_limited",
                    "model": "fallback"
                }
            
            # Default fallback
            return {
                "response": "HOLD",
                "source": "rate_limit_protection",
                "reason": f"Rate limit reached: {self.LIMIT} requests per {self.WINDOW}s",
                "model": "none"
            }
        
        # 3. Make API Call
        self.request_timestamps.append(time.time())
        self.stats["api_calls"] += 1
        
        # Placeholder for actual API call
        # In production, this would call the actual AI API
        response = await self._call_ai_api(prompt, model)
        
        # 4. Cache Response
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        return {
            "response": response,
            "source": "api",
            "model": model
        }
    
    async def _call_ai_api(self, prompt: str, model: str) -> str:
        """
        Placeholder for actual AI API calls.
        Override this in production with real API integration.
        """
        # This would be replaced with actual API calls to Gemini/GLM/Groq
        return f"AI Response for: {prompt[:50]}..."
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        self._clean_old_timestamps()
        return {
            **self.stats,
            "current_window_usage": len(self.request_timestamps),
            "limit": self.LIMIT,
            "cache_size": len(self.cache),
            "cache_hit_rate": (self.stats["cache_hits"] / self.stats["total_requests"] * 100) 
                              if self.stats["total_requests"] > 0 else 0
        }
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "rate_limited": 0,
            "api_calls": 0
        }


# Singleton instance for global use
ai_gatekeeper = AIGatekeeper()
