"""
📰 News Filter - The Semantic Scanner
=====================================
Uses Perplexity API to scan real-world news for high-impact events.
Prevents trading during "Red Folder" events or extreme FUD.
"""

import os
import logging
import asyncio
import json
from dataclasses import dataclass
from typing import Optional, List
import httpx

logger = logging.getLogger(__name__)

@dataclass
class NewsSentinel:
    """Result of news analysis."""
    symbol: str
    sentiment_score: float  # -1.0 (Bearish) to 1.0 (Bullish)
    risk_level: str         # LOW, MEDIUM, HIGH, EXTREME
    summary: str
    red_folder_warning: bool
    source_count: int

class NewsFilter:
    """
    Interface to Perplexity API for real-time market intelligence.
    """
    
    BASE_URL = "https://api.perplexity.ai/chat/completions"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self.client = httpx.AsyncClient(timeout=30.0)
        
        if not self.api_key:
            logger.warning("⚠️ No PERPLEXITY_API_KEY found. News Filter running in MOCK mode.")

    async def analyze_sentiment(self, symbol: str) -> NewsSentinel:
        """
        Query Perplexity for real-time sentiment analysis.
        """
        if not self.api_key:
            return self._mock_response(symbol)
            
        try:
            prompt = self._build_prompt(symbol)
            
            payload = {
                "model": "sonar-reasoning-pro", # Using their reasoning model
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a financial risk analyst. Output ONLY valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(self.BASE_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Parse JSON from markdown block if necessary
            clean_json = self._extract_json(content)
            result = json.loads(clean_json)
            
            return NewsSentinel(
                symbol=symbol,
                sentiment_score=result.get("sentiment_score", 0.0),
                risk_level=result.get("risk_level", "MEDIUM"),
                summary=result.get("summary", "No summary available"),
                red_folder_warning=result.get("red_folder_warning", False),
                source_count=len(result.get("citations", []))
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze news for {symbol}: {e}")
            return self._mock_response(symbol, is_error=True)

    def _build_prompt(self, symbol: str) -> str:
        """
        Enhanced prompt inspired by 'Hacking the Markets' Perplexity Finance.
        
        Instead of generic sentiment, we ask for specific TRADE KILLERS:
        - CPI/FOMC events
        - Major hacks/lawsuits
        - Stablecoin depegs
        """
        return f"""
You are a financial risk analyst. Analyze the last 24 hours of news for: {symbol}.

IMPORTANT: Answer these SPECIFIC questions as boolean flags:

1. FOMC_EVENT: Is there a Federal Reserve meeting or speech today/tomorrow?
2. CPI_EVENT: Is there a CPI/inflation data release today?
3. MAJOR_HACK: Is there news of a crypto hack > $50M in the last 24h?
4. SEC_ACTION: Is there an SEC lawsuit or enforcement against a major exchange?
5. STABLECOIN_RISK: Is USDT, USDC, or DAI trading below $0.99?
6. WAR_ESCALATION: Is there breaking news of military conflict escalation?

Also provide:
- Overall sentiment: -1.0 (bearish) to 1.0 (bullish)
- Risk level: LOW, MEDIUM, HIGH, or EXTREME
- One sentence summary

Return ONLY this JSON format:
{{
    "fomc_event": bool,
    "cpi_event": bool,
    "major_hack": bool,
    "sec_action": bool,
    "stablecoin_risk": bool,
    "war_escalation": bool,
    "red_folder_warning": bool (true if ANY of the above is true),
    "sentiment_score": float,
    "risk_level": "LOW"|"MEDIUM"|"HIGH"|"EXTREME",
    "summary": "string"
}}
"""

    def _extract_json(self, content: str) -> str:
        """Helper to extract JSON from Markdown code blocks."""
        if "```json" in content:
            return content.split("```json")[1].split("```")[0].strip()
        if "```" in content:
            return content.split("```")[1].split("```")[0].strip()
        return content

    def _mock_response(self, symbol: str, is_error: bool = False) -> NewsSentinel:
        """Fallback response when API is unavailable."""
        return NewsSentinel(
            symbol=symbol,
            sentiment_score=0.0,
            risk_level="UNKNOWN" if is_error else "LOW",
            summary="News analysis unavailable (Mock Mode)" if not is_error else "API Error",
            red_folder_warning=False,
            source_count=0
        )
    
    async def close(self):
        await self.client.aclose()
