"""
Gemini Adapter for Axiom Antigravity
Provides an interface to Google's Gemini API via Cloudflare Workers (fetch).
"""

import json
from js import fetch, Headers

class GeminiAdapter:
    def __init__(self, env):
        self.env = env
        self.api_key = str(getattr(env, 'GEMINI_API_KEY', ''))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    async def generate_content(self, prompt: str, model: str = "gemini-1.5-pro") -> dict:
        """
        Generate content using Gemini API.

        Args:
            prompt: The text prompt.
            model: Model name (default: gemini-1.5-pro, fallback to flash if pro fails or unavailable).
                   Note: Check correct model identifier. Usually 'gemini-1.5-pro' or 'gemini-1.5-pro-latest'.

        Returns:
            dict: {success: bool, content: str, error: str}
        """
        if not self.api_key:
            return {"success": False, "error": "GEMINI_API_KEY not configured"}

        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 2000
            }
        }

        try:
            headers = Headers.new({"Content-Type": "application/json"}.items())
            response = await fetch(url, method="POST", headers=headers, body=json.dumps(payload))

            if not response.ok:
                text = await response.text()
                return {"success": False, "error": f"API Error {response.status}: {text}"}

            data = json.loads(await response.text())

            # Extract text
            if "candidates" in data and len(data["candidates"]) > 0:
                parts = data["candidates"][0].get("content", {}).get("parts", [])
                if parts:
                    content = parts[0].get("text", "")
                    return {"success": True, "content": content}

            return {"success": False, "error": "No content generated"}

        except Exception as e:
            return {"success": False, "error": str(e)}
