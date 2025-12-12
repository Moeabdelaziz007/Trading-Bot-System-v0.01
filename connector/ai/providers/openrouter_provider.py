import os
from openai import OpenAI
from ..router import AIProvider

class OpenRouterProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            print("⚠️ OPENROUTER_API_KEY not found")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    async def fast_inference(self, prompt: str) -> str:
        # Route to cheapest/fastest available via 'auto' or specific low-cost model
        try:
            response = self.client.chat.completions.create(
                model="liquid/lfm-40b:free", # Example free/fast model
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error (OpenRouter Fast): {str(e)}"

    async def deep_reasoning(self, prompt: str) -> str:
        # Access top-tier models like Claude 3.5 Sonnet or GPT-4o via OpenRouter
        try:
            response = self.client.chat.completions.create(
                model="anthropic/claude-3.5-sonnet",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error (OpenRouter Smart): {str(e)}"
