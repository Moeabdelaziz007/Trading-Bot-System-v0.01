"""
🏛️ SEC Filings MCP - EDGAR Fetcher
Zero-Cost Regulatory Intelligence

Responsibilities:
- Fetch latest 8-K filings from SEC EDGAR RSS
- Detect keywords (Merger, Earnings, Bankruptcy)
"""

from js import fetch
import json

class EDGARFetcher:
    def __init__(self):
        self.base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        # Using a mirror/alternative if SEC blocks automated requests without proper User-Agent
        # But standard SEC RSS usually works with valid User-Agent

    async def get_latest_filings(self, ticker: str):
        """
        Fetch latest 8-K filings for a specific ticker.
        """
        ticker = ticker.upper()
        # RSS feed for specific company
        # Note: We need the CIK for accurate lookup, but ticker search works too
        rss_url = f"{self.base_url}?action=getcompany&CIK={ticker}&type=8-K&dateb=&owner=exclude&count=10&output=atom"

        try:
            # SEC requires a properly formatted User-Agent: "Sample Company Name AdminContact@sample.com"
            headers = {
                "User-Agent": "AxiomTradingBot axiom.admin@axiom.trade",
                "Accept-Encoding": "gzip, deflate",
                "Host": "www.sec.gov"
            }

            response = await fetch(rss_url, {"headers": headers})

            if response.status != 200:
                return {"error": f"SEC Error {response.status}", "filings": []}

            xml_text = await response.text()

            # Extract Entries
            import re
            entries = re.findall(r'<entry>(.*?)</entry>', xml_text, re.DOTALL)

            filings = []
            for entry in entries:
                title_match = re.search(r'<title>(.*?)</title>', entry, re.DOTALL)
                link_match = re.search(r'<link.*?href="(.*?)".*?>', entry, re.DOTALL)
                date_match = re.search(r'<updated>(.*?)</updated>', entry, re.DOTALL)
                summary_match = re.search(r'<summary type="html">(.*?)</summary>', entry, re.DOTALL)

                if title_match:
                    title = title_match.group(1)
                    # Check for significant events
                    impact = "NEUTRAL"
                    if "Item 1.01" in summary_match.group(1) if summary_match else "": # Entry into a Material Definitive Agreement
                        impact = "HIGH"
                    elif "Item 1.03" in summary_match.group(1) if summary_match else "": # Bankruptcy
                        impact = "CRITICAL"
                    elif "Item 2.02" in summary_match.group(1) if summary_match else "": # Results of Operations (Earnings)
                        impact = "HIGH"

                    filings.append({
                        "title": title,
                        "link": link_match.group(1) if link_match else "",
                        "date": date_match.group(1) if date_match else "",
                        "impact": impact
                    })

            return {
                "ticker": ticker,
                "total_filings": len(filings),
                "latest_filings": filings
            }

        except Exception as e:
            return {"error": str(e), "filings": []}
