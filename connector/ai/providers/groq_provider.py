import os
from groq import Groq
from ..router import AIProvider

class GroqProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️ GROQ_API_KEY not found")
        self.client = Groq(api_key=self.api_key)

    async def fast_inference(self, prompt: str) -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                model="llama3-70b-8192",
                temperature=0.5,
                max_tokens=1024,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error (Groq): {str(e)}"

    async def deep_reasoning(self, prompt: str) -> str:
        # Groq is primarily for speed, but Llama 3 70B is smart enough for some reasoning
        return await self.fast_inference(prompt)
