import os
from google import genai
from google.genai import types
from ..router import AIProvider

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("⚠️ GOOGLE_API_KEY not found")
        
        self.client = genai.Client(api_key=self.api_key)

    async def fast_inference(self, prompt: str) -> str:
        # Gemini 2.0 Flash is extremely fast
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Error (Gemini Fast): {str(e)}"

    async def deep_reasoning(self, prompt: str) -> str:
        # Gemini 2.0 Flash Thinking or Pro (future)
        # For now, 2.0 Flash is also the best reasoning model available in preview
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-thinking-exp", 
                contents=prompt
            )
            return response.text
        except Exception as e:
            # Fallback to standard flash if thinking model unavailable
            return await self.fast_inference(prompt)
