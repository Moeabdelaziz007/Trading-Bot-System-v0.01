import os
from openai import OpenAI
from ..router import AIProvider

class ZAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("ZAI_API_KEY")
        if not self.api_key:
            print("⚠️ ZAI_API_KEY not found")
        
        # Z.AI is OpenAI-compatible
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )

    async def fast_inference(self, prompt: str) -> str:
        # Use GLM-4-Flash for speed if available, or GLM-4-Air
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error (Z.AI Fast): {str(e)}"

    async def deep_reasoning(self, prompt: str) -> str:
        # Use GLM-4.6 for maximum intelligence
        try:
            response = self.client.chat.completions.create(
                model="glm-4-plus", # Or specific 4.6 alias if different
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error (Z.AI Smart): {str(e)}"
