
import json
import asyncio
from js import fetch, Headers, Response

class CapitalConnector:
    """
    🏦 Axiom Capital.com Connector
    
    Handles secure authentication, session management, and API communication 
    with Capital.com's Trading API.
    
    Features:
    - Session Management (CST & X-SECURITY-TOKEN)
    - Auto-Reconnection logic
    - Account Information Retrieval
    - Market Navigation
    """
    
    BASE_URL = "https://api-capital.backend-capital.com" # Live URL
    DEMO_URL = "https://demo-api-capital.backend-capital.com"
    
    def __init__(self, env):
        self.env = env
        self.api_key = str(getattr(env, 'CAPITAL_API_KEY', ''))
        self.identifier = str(getattr(env, 'CAPITAL_EMAIL', ''))
        self.password = str(getattr(env, 'CAPITAL_PASSWORD', ''))
        self.is_demo = str(getattr(env, 'CAPITAL_DEMO', 'true')).lower() == 'true'
        
        self.base_url = self.DEMO_URL if self.is_demo else self.BASE_URL
        
        # Session Tokens
        self.cst = None
        self.security_token = None
        
    async def create_session(self):
        """
        Create a new trading session and store tokens.
        """
        url = f"{self.base_url}/api/v1/session"
        
        headers = {
            "Content-Type": "application/json",
            "X-CAP-API-KEY": self.api_key
        }
        
        body = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False
        }
        
        try:
            resp = await fetch(url, method="POST", headers=Headers.new(headers.items()), body=json.dumps(body))
            
            if resp.status == 200:
                # Capture Tokens from Response Headers
                self.cst = resp.headers.get("CST")
                self.security_token = resp.headers.get("X-SECURITY-TOKEN")
                
                data = json.loads(await resp.text())
                return {"status": "success", "accountType": data.get("accountType"), "clientId": data.get("clientId")}
            else:
                error_text = await resp.text()
                return {"status": "error", "code": resp.status, "message": error_text}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_account_info(self, retry_count=0):
        """
        Fetch account balance, margin, and equity.
        """
        if not self.cst or not self.security_token:
            await self.create_session()
            
        url = f"{self.base_url}/api/v1/accounts"
        
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token
        }
        
        try:
            resp = await fetch(url, method="GET", headers=Headers.new(headers.items()))
            
            if resp.status == 200:
                data = json.loads(await resp.text())
                # Return the primary account info
                if "accounts" in data and len(data["accounts"]) > 0:
                    acc = data["accounts"][0]
                    return {
                        "status": "success",
                        "balance": acc.get("balance", {}).get("balance", 0),
                        "deposit": acc.get("balance", {}).get("deposit", 0),
                        "profit_loss": acc.get("balance", {}).get("pl", 0),
                        "available": acc.get("balance", {}).get("available", 0)
                    }
                return {"status": "error", "message": "No logic accounts found"}
            elif resp.status == 401:
                # Session expired, retry once only
                if retry_count < 1:
                    await self.create_session()
                    return await self.get_account_info(retry_count=1)
                else:
                    return {"status": "error", "code": 401, "message": "Unauthorized: Check Credentials"}
            else:
                return {"status": "error", "code": resp.status, "message": await resp.text()}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def search_market(self, query):
        """
        Search for market symbols (e.g., 'Gold', 'BTC').
        """
        if not self.cst:
            await self.create_session()
            
        url = f"{self.base_url}/api/v1/markets?searchTerm={query}"
        
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "CST": self.cst,
            "X-SECURITY-TOKEN": self.security_token
        }
        
        try:
            resp = await fetch(url, method="GET", headers=Headers.new(headers.items()))
            data = json.loads(await resp.text())
            
            markets = []
            if "markets" in data:
                for m in data["markets"]:
                    markets.append({
                        "symbol": m.get("symbol"),
                        "name": m.get("instrumentName"),
                        "status": m.get("marketStatus"),
                        "epic": m.get("epic") # Important for trading
                    })
            return {"status": "success", "markets": markets}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
