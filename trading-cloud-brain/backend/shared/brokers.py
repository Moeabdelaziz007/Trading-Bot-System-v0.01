"""
🏦 BROKER INTEGRATIONS
Zero-Cost institutional grade connections.
"""

from js import fetch
import json

# ==========================================
# 🚀 HYPERLIQUID (DEX)
# ==========================================

class HyperliquidBroker:
    BASE_URL = "https://api.hyperliquid.xyz"

    def __init__(self, wallet, private_key):
        self.wallet = wallet
        self.key = private_key
    
    async def get_market_data(self, coin: str):
        """Fetch L2 Book from Hyperliquid."""
        try:
            res = await fetch(f"{self.BASE_URL}/info", {
                "method": "POST",
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "type": "l2Book",
                    "coin": coin
                })
            })
            return await res.json()
        except Exception as e:
            return {"error": str(e)}

    # Note: Full trading requires signing logic which is complex in pure Python environment
    # without compiling cython libraries. For the MVP, we use the Info API.


# ==========================================
# 💼 IBKR WEB API (REST)
# ==========================================

class IBKRWebBroker:
    """
    Connects to Client Portal Web API Gateway (CP Gateway).
    Start container: docker run -p 5000:5000 voyz/ibeam
    """
    
    def __init__(self, gateway_url="https://localhost:5000", verify_ssl=False):
        self.base = gateway_url
        self.verify = verify_ssl

    async def check_health(self):
        try:
            res = await fetch(f"{self.base}/v1/api/tickle")
            return await res.json()
        except:
            return {"status": "offline"}

    async def place_order(self, account_id, symbol, action, quantity):
        order_body = {
            "acctId": account_id,
            "conid": await self._get_conid(symbol),
            "orderType": "MKT",
            "side": action, # BUY/SELL
            "quantity": quantity,
            "tif": "GTC"
        }
        
        res = await fetch(f"{self.base}/v1/api/iserver/account/{account_id}/order", {
            "method": "POST",
            "body": json.dumps(order_body)
        })
        return await res.json()

    async def _get_conid(self, symbol):
        # Helper to lookup contract ID
        # Mock for now
        return 123456 
