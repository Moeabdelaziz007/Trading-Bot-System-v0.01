
import json
from datetime import datetime
import asyncio

class CreditManager:
    """
    Refined 'Banker' for API credits.
    Manages daily budgets for free-tier APIs using Cloudflare KV.
    """

    # Daily Limits
    LIMITS = {
        "finnhub": 60,      # calls per minute (tracked differently) or strict daily
        "alpha_vantage": 25, # calls per day
        "news_data": 200,    # credits per day
    }
    
    # Costs per operation
    COSTS = {
        "price": 1,
        "news": 2,
        "technicals": 3
    }

    def __init__(self, kv_binding=None):
        self.kv = kv_binding


    def _get_date_key(self):
        return datetime.utcnow().strftime("%Y-%m-%d")

    async def get_remaining_credits(self, api_name: str) -> int:
        """Get remaining credits for an API for today."""
        date_key = self._get_date_key()
        key = f"credits:{api_name}:{date_key}"
        
        used_str = await self.kv.get(key)
        used = int(used_str) if used_str else 0
        
        limit = self.LIMITS.get(api_name, 0)
        return max(0, limit - used)

    async def check_credits(self, api_name: str, cost: int = 1) -> bool:
        """Check if we can afford this call."""
        remaining = await self.get_remaining_credits(api_name)
        return remaining >= cost

    async def deduct_credit(self, api_name: str, cost: int = 1) -> bool:
        """
        Deduct credits. Returns True if successful, False if out of budget.
        This is atomic-ish via KV but strictly we might have race conditions 
        in high concurrency without Durable Objects.
        For Zero-Cost/Low-Volume, this is acceptable.
        """
        date_key = self._get_date_key()
        key = f"credits:{api_name}:{date_key}"
        
        # Optimistic locking or simple increment? 
        # KV doesn't have atomic increment. We read-modify-write.
        # Acceptance of small race condition error for free tier.
        
        used_str = await self.kv.get(key)
        used = int(used_str) if used_str else 0
        
        limit = self.LIMITS.get(api_name, 0)
        
        if used + cost > limit:
            return False
            
        new_used = used + cost
        # Exipre in 24 hours to auto-cleanup
        await self.kv.put(key, str(new_used), expirationTtl=86400)
        return True

    async def reset_daily_counters_if_needed(self):
        # KV expiration handles this automatically!
        pass
