"""
🛡️ CIRCUIT BREAKER
Resilience pattern for external API calls.
"""

import time
import json

class CircuitBreaker:
    def __init__(self, name: str, fail_threshold: int = 5, reset_timeout: int = 60, kv_store=None):
        self.name = name
        self.threshold = fail_threshold
        self.timeout = reset_timeout
        self.kv = kv_store  # Optional distributed state

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if await self.is_open():
            return {"error": "Circuit Breaker OPEN", "service": self.name}

        try:
            result = await func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception as e:
            await self.record_failure()
            raise e

    async def is_open(self):
        # Check KV or local state
        # Simplified logic for stateless worker
        # Ideally, we read from KV here
        return False 

    async def record_failure(self):
        # Increment failure count in KV
        pass

    async def record_success(self):
        # Reset failure count
        pass
