"""
💾 KV CACHE LAYER - Response Caching for CPU/Latency Optimization
Uses Cloudflare KV for persistent caching across edge locations

This module implements:
1. Persistent response caching with TTL
2. Smart cache key generation
3. Cache-aside pattern for API responses
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict


class KVCacheLayer:
    """
    Cloudflare KV-backed cache layer for reducing:
    - CPU time (by avoiding repeated AI calls)
    - Latency (by serving cached responses from edge)
    - API costs (by reducing external API calls)
    """
    
    def __init__(self, kv_binding=None, default_ttl: int = 300, namespace: str = "cache"):
        """
        Args:
            kv_binding: Cloudflare KV namespace binding
            default_ttl: Default cache TTL in seconds (5 minutes)
            namespace: Cache key prefix for organization
        """
        self.kv = kv_binding
        self.DEFAULT_TTL = default_ttl
        self.NAMESPACE = namespace
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
    
    def _make_key(self, identifier: str) -> str:
        """Generate a namespaced cache key"""
        # Hash long identifiers to keep keys manageable
        if len(identifier) > 64:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"{self.NAMESPACE}:{identifier}"
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from cache
        
        Args:
            key: The cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self.kv:
            return None
        
        full_key = self._make_key(key)
        
        try:
            value = await self.kv.get(full_key)
            
            if value is None:
                self.stats["misses"] += 1
                return None
            
            # Parse JSON if stored as JSON
            try:
                parsed = json.loads(value)
                self.stats["hits"] += 1
                return parsed
            except json.JSONDecodeError:
                self.stats["hits"] += 1
                return value
                
        except Exception as e:
            self.stats["errors"] += 1
            print(f"⚠️ KV Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set a value in cache
        
        Args:
            key: The cache key
            value: The value to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.kv:
            return False
        
        full_key = self._make_key(key)
        ttl = ttl or self.DEFAULT_TTL
        
        try:
            # Serialize complex objects to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            await self.kv.put(full_key, str(value), expirationTtl=ttl)
            self.stats["sets"] += 1
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            print(f"⚠️ KV Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        if not self.kv:
            return False
        
        full_key = self._make_key(key)
        
        try:
            await self.kv.delete(full_key)
            return True
        except Exception as e:
            self.stats["errors"] += 1
            return False
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_fn, 
        ttl: Optional[int] = None
    ) -> Any:
        """
        Cache-aside pattern: Get from cache or fetch and cache
        
        Args:
            key: The cache key
            fetch_fn: Async function to call if cache miss
            ttl: TTL for the cached value
            
        Returns:
            The cached or freshly fetched value
        """
        # Try cache first
        cached = await self.get(key)
        if cached is not None:
            return cached
        
        # Cache miss - fetch fresh data
        fresh_value = await fetch_fn()
        
        # Cache the result
        await self.set(key, fresh_value, ttl)
        
        return fresh_value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": f"{hit_rate:.1f}%"
        }


# ============================================
# CACHE STRATEGIES FOR DIFFERENT DATA TYPES
# ============================================

class MarketDataCache(KVCacheLayer):
    """Specialized cache for market data with short TTL"""
    
    def __init__(self, kv_binding=None):
        super().__init__(kv_binding, default_ttl=60, namespace="market")
    
    async def get_price(self, symbol: str) -> Optional[Dict]:
        """Get cached price for a symbol"""
        return await self.get(f"price:{symbol}")
    
    async def set_price(self, symbol: str, data: Dict):
        """Cache price data for a symbol (1 minute TTL)"""
        await self.set(f"price:{symbol}", data, ttl=60)


class AIResponseCache(KVCacheLayer):
    """Specialized cache for AI responses with longer TTL"""
    
    def __init__(self, kv_binding=None):
        super().__init__(kv_binding, default_ttl=300, namespace="ai")
    
    async def get_analysis(self, prompt_hash: str) -> Optional[str]:
        """Get cached AI analysis"""
        return await self.get(f"analysis:{prompt_hash}")
    
    async def set_analysis(self, prompt_hash: str, response: str, ttl: int = 300):
        """Cache AI analysis (5 minute default TTL)"""
        await self.set(f"analysis:{prompt_hash}", response, ttl=ttl)


class DashboardCache(KVCacheLayer):
    """Specialized cache for dashboard data"""
    
    def __init__(self, kv_binding=None):
        super().__init__(kv_binding, default_ttl=30, namespace="dashboard")
    
    async def get_snapshot(self) -> Optional[Dict]:
        """Get cached dashboard snapshot"""
        return await self.get("snapshot")
    
    async def set_snapshot(self, data: Dict):
        """Cache dashboard snapshot (30 second TTL)"""
        await self.set("snapshot", data, ttl=30)
