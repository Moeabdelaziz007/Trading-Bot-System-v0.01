"""
🛡️ ALPHAAXIOM INFRASTRUCTURE UTILITIES
Zero-Cost Compliance Layer for Free Tier Protection

Modules:
- ai_gatekeeper: Rate limiting for AI APIs (Gemini: 14 RPM)
- db_batcher: Write batching for D1 (95% reduction)
- kv_cache: Persistent response caching via Cloudflare KV
"""

from .ai_gatekeeper import AIGatekeeper, ai_gatekeeper
from .db_batcher import DatabaseBatcher, D1BatchWriter, db_batcher
from .kv_cache import KVCacheLayer, MarketDataCache, AIResponseCache, DashboardCache

__all__ = [
    # AI Rate Limiting
    "AIGatekeeper",
    "ai_gatekeeper",
    
    # Database Batching
    "DatabaseBatcher",
    "D1BatchWriter",
    "db_batcher",
    
    # Caching
    "KVCacheLayer",
    "MarketDataCache",
    "AIResponseCache",
    "DashboardCache",
]
