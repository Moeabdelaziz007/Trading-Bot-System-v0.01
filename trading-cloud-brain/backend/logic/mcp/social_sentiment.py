"""
🐦 Social Sentiment MCP - Nitter Scraper
Zero-Cost Twitter/X Analysis using Nitter RSS

Responsibilities:
- Scrape Nitter RSS feeds for cashtags ($BTC, $TSLA)
- Detect volume spikes in mentions
- Analyze sentiment (simple keyword match)
"""

import json
from js import fetch
from datetime import datetime

class NitterScraper:
    def __init__(self, instances=None):
        # Public Nitter instances (fallback list)
        self.instances = instances or [
            "https://nitter.net",
            "https://nitter.cz",
            "https://nitter.moomoo.me"
        ]
        self.current_instance_idx = 0

    def _get_instance(self):
        """Rotate instances to avoid rate limits"""
        url = self.instances[self.current_instance_idx]
        self.current_instance_idx = (self.current_instance_idx + 1) % len(self.instances)
        return url

    async def fetch_mentions(self, ticker: str):
        """
        Fetch latest mentions for a ticker from Nitter RSS.
        """
        ticker = ticker.upper().replace("$", "")
        base_url = self._get_instance()
        rss_url = f"{base_url}/search/rss?f=tweets&q=%24{ticker}"

        try:
            response = await fetch(rss_url, {
                "headers": {
                    "User-Agent": "Mozilla/5.0 (compatible; AxiomBot/2.0)"
                }
            })

            if response.status != 200:
                return {"error": f"HTTP {response.status}", "mentions": []}

            xml_text = await response.text()

            # Simple XML parsing (Regex is faster/lighter than xml.etree in Workers)
            import re
            # Extract items
            items = re.findall(r'<item>(.*?)</item>', xml_text, re.DOTALL)

            parsed_items = []
            for item in items[:20]:  # Analyze last 20 tweets
                title_match = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                date_match = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
                desc_match = re.search(r'<description>(.*?)</description>', item, re.DOTALL)

                if title_match:
                    text = title_match.group(1).replace("<![CDATA[", "").replace("]]>", "")
                    parsed_items.append({
                        "text": text,
                        "date": date_match.group(1) if date_match else "",
                        "sentiment": self._analyze_sentiment(text)
                    })

            # Calculate metrics
            total = len(parsed_items)
            bullish = sum(1 for i in parsed_items if i['sentiment'] == 'BULLISH')
            bearish = sum(1 for i in parsed_items if i['sentiment'] == 'BEARISH')

            sentiment_score = 50
            if total > 0:
                sentiment_score = 50 + ((bullish - bearish) / total) * 50

            return {
                "ticker": ticker,
                "volume": total,
                "bullish_count": bullish,
                "bearish_count": bearish,
                "sentiment_score": round(sentiment_score, 2),
                "latest_tweets": parsed_items[:5]
            }

        except Exception as e:
            return {"error": str(e), "mentions": []}

    def _analyze_sentiment(self, text: str):
        """Simple keyword-based sentiment analysis"""
        text = text.lower()
        bull_words = ["buy", "long", "moon", "rocket", "bull", "up", "breakout", "call"]
        bear_words = ["sell", "short", "dump", "crash", "bear", "down", "breakdown", "put"]

        bull_score = sum(1 for w in bull_words if w in text)
        bear_score = sum(1 for w in bear_words if w in text)

        if bull_score > bear_score:
            return "BULLISH"
        elif bear_score > bull_score:
            return "BEARISH"
        return "NEUTRAL"
