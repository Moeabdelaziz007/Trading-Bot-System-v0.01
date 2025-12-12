import os
import asyncio
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod

class AIProvider(ABC):
    @abstractmethod
    async def fast_inference(self, prompt: str) -> str:
        """fast / cheap models (e.g. Llama 70B, Gemini Flash)"""
        pass

    @abstractmethod
    async def deep_reasoning(self, prompt: str) -> str:
        """smart / expensive models (e.g. GLM-4.6, GPT-4)"""
        pass

class AIRouter:
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.default_fast = "groq"
        self.default_smart = "zai" # GLM-4.6

    def register_provider(self, name: str, provider: AIProvider):
        self.providers[name] = provider

    async def route(self, prompt: str, role: str = "analyst", require_speed: bool = True) -> str:
        """
        Routes the request to the best provider based on role and requirements.
        """
        # 1. SPECIAL CASE: Sentinel -> Speed (Groq)
        if role == "sentinel":
            return await self._get_provider("groq").fast_inference(prompt)
        
        # 2. SPECIAL CASE: Analyst -> Reasoning (Z.AI / Gemini)
        if role == "analyst":
            return await self._get_provider("zai").deep_reasoning(prompt)

        # 3. SPECIAL CASE: Journalist -> Multimodal/Creative (Gemini/OpenRouter)
        if role == "journalist":
             return await self._get_provider("gemini").fast_inference(prompt)

        # Default fallback
        if require_speed:
            return await self._get_provider(self.default_fast).fast_inference(prompt)
        else:
            return await self._get_provider(self.default_smart).deep_reasoning(prompt)

    def _get_provider(self, name: str) -> AIProvider:
        provider = self.providers.get(name)
        if not provider:
            # Fallback to OpenRouter if primary missing
            return self.providers.get("openrouter") 
        return provider

# Singleton instance
ai_router = AIRouter()

# Register Providers
try:
    from .providers.groq_provider import GroqProvider
    ai_router.register_provider("groq", GroqProvider())
except Exception as e:
    print(f"⚠️ Failed to load Groq: {e}")

try:
    from .providers.zai_provider import ZAIProvider
    ai_router.register_provider("zai", ZAIProvider())
except Exception as e:
    print(f"⚠️ Failed to load Z.AI: {e}")

try:
    from .providers.gemini_provider import GeminiProvider
    ai_router.register_provider("gemini", GeminiProvider())
except Exception as e:
    print(f"⚠️ Failed to load Gemini: {e}")

try:
    from .providers.openrouter_provider import OpenRouterProvider
    ai_router.register_provider("openrouter", OpenRouterProvider())
except Exception as e:
    print(f"⚠️ Failed to load OpenRouter: {e}")

