"""
Fetch Tools: News Sentiment
Fetches news and computes sentiment from NewsData.io.
"""

from js import fetch
import json

async def get_newsdata_sentiment(symbol: str, api_key: str) -> dict:
    """
    Fetch news from NewsData.io and compute sentiment.
    
    Args:
        symbol: Stock/Crypto symbol for news search
        api_key: NewsData.io API key
        
    Returns:
        {
            "score": float (-1.0 to 1.0),
            "headline_count": int,
            "headlines": list,
            "source": "newsdata"
        }
    """
    # NewsData.io endpoint
    url = f"https://newsdata.io/api/1/news?apikey={api_key}&q={symbol}&language=en&category=business"
    
    try:
        response = await fetch(url)
        data = await response.json()
        
        if data.get("status") != "success" or not data.get("results"):
            return {
                "score": 0,
                "headline_count": 0,
                "headlines": [],
                "source": "newsdata"
            }
        
        articles = data.get("results", [])
        headlines = [a.get("title", "") for a in articles[:5]]
        
        # Basic keyword-based sentiment (can be upgraded to Workers AI)
        positive_words = ["surge", "jump", "gain", "rise", "bullish", "profit", "grow", "beat", "strong"]
        negative_words = ["crash", "fall", "drop", "bearish", "loss", "decline", "weak", "miss", "fear"]
        
        total_score = 0
        for article in articles[:10]:
            title = article.get("title", "").lower()
            desc = article.get("description", "").lower() or ""
            text = title + " " + desc
            
            pos_count = sum(1 for w in positive_words if w in text)
            neg_count = sum(1 for w in negative_words if w in text)
            
            if pos_count > neg_count:
                total_score += 0.5
            elif neg_count > pos_count:
                total_score -= 0.5
        
        # Normalize to -1 to 1
        avg_score = total_score / max(len(articles[:10]), 1)
        normalized_score = max(-1, min(1, avg_score))
        
        return {
            "score": round(normalized_score, 2),
            "headline_count": len(articles),
            "headlines": headlines,
            "source": "newsdata"
        }
    
    except Exception as e:
        return {"error": str(e), "score": 0, "source": "newsdata"}
