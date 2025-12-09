"""
🔍 ZERO-COST RESEARCH TOOL (DuckDuckGo + SEC)
Gives the AI "Eyes" to read the web and filings.
"""

from js import fetch
import json
import re

class ResearchMCP:
    
    async def search_market_news(self, query: str):
        """
        Scrapes DuckDuckGo HTML for top results.
        Zero API keys required.
        """
        try:
            # Use DuckDuckGo HTML version (lighter, easier to scrape)
            url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; AxiomBot/1.0)"
            }
            
            res = await fetch(url, {"headers": headers})
            html = await res.text()
            
            # Extract results using Regex (No BeautifulSoup in Workers)
            # Pattern: <a class="result__a" href="...">Title</a>
            results = []
            matches = re.finditer(r'<a class="result__a" href="([^"]+)">(.*?)</a>', html)
            
            for i, match in enumerate(matches):
                if i >= 5: break
                link = match.group(1)
                title = re.sub(r'<.*?>', '', match.group(2)) # Strip tags
                results.append({"title": title, "link": link})
                
            return results
        except Exception as e:
            return {"error": str(e)}

    async def get_sec_filings(self, ticker: str):
        """
        Fetches latest 8-K/10-Q from SEC EDGAR API (Free).
        """
        headers = {
            "User-Agent": "AxiomTrading contact@axiom.com" # Required by SEC
        }
        
        try:
            # 1. Look up CIK (Central Index Key)
            # Simplified: Assuming we map Ticker -> CIK or use a lookup API
            # For this MVP, we'll try a direct search query if CIK mapping is missing
            
            # Using SEC RSS feed for latest filings
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}&type=8-K&output=atom"
            
            res = await fetch(url, {"headers": headers})
            xml = await res.text()
            
            # Extract latest logic
            entries = re.findall(r'<entry>.*?</entry>', xml, re.DOTALL)
            filings = []
            
            for entry in entries[:3]:
                title = re.search(r'<title>(.*?)</title>', entry).group(1)
                link = re.search(r'<link href="(.*?)"', entry).group(1)
                filings.append({"title": title, "link": link})
                
            return filings
            
        except Exception as e:
            return {"error": "Failed to fetch SEC data. Ticker might need CIK mapping."}
