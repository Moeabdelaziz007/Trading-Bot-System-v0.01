"""
🐦 ZERO-COST SOCIAL SENTIMENT (Nitter Scraping)
Scrapes Nitter (Twitter Mirror) RSS feeds to detect retail FOMO.
"""

from js import fetch
import re
from datetime import datetime

class SocialSentimentMCP:
    NITTER_INSTANCES = [
        "https://nitter.net",
        "https://nitter.cz",
        "https://nitter.privacydev.net"
    ]
    
    async def get_sentiment(self, ticker: str):
        """
        Scrapes partial RSS feed for $TICKER to count volume.
        Returns: { score: 0-100, volume: int, trend: "BULLISH"|"BEARISH" }
        """
        # Clean ticker
        clean_ticker = ticker.replace("$", "").upper()
        query = f"%24{clean_ticker}" # $TICKER encoded
        
        total_mentions = 0
        sentiment_score = 0
        
        # Try instances until one works
        for instance in self.NITTER_INSTANCES:
            try:
                url = f"{instance}/search/rss?q={query}"
                res = await fetch(url)
                if res.status != 200:
                    continue
                    
                text = await res.text()
                
                # Simple Regex Counting (Fast & Zero Cost)
                # Count items (tweets)
                mentions = len(re.findall(r"<item>", text))
                
                # Basic Sentiment Keywords
                bullish = len(re.findall(r"(?i)(moon|bull|buying|long|pump|gem)", text))
                bearish = len(re.findall(r"(?i)(dump|bear|selling|short|rekt|scam)", text))
                
                total_mentions = mentions
                if mentions > 0:
                    sentiment_score = ((bullish - bearish) / mentions) * 100
                
                break # Success
            except:
                continue
        
        # Normalize score to 0-100 range (50 is neutral)
        normalized_score = max(0, min(100, 50 + sentiment_score))
        
        return {
            "source": "nitter_rss",
            "ticker": clean_ticker,
            "mentions_last_hour": total_mentions, # Proxy since RSS is recent
            "sentiment_score": round(normalized_score, 2),
            "trend": "BULLISH" if normalized_score > 60 else "BEARISH" if normalized_score < 40 else "NEUTRAL",
            "timestamp": datetime.utcnow().isoformat()
        }
