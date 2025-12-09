#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 BYBIT TESTNET API CONNECTION TEST | اختبار اتصال API بايبت
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Purpose: Verify Bybit Testnet API connectivity and authentication
API: Bybit V5 API (Unified Trading Account)

Author: Axiom AI Partner | Mohamed Hossameldin Abdelaziz
Date: December 9, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import time
import hmac
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from typing import Dict, Optional, Any

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 CONFIGURATION | الإعدادات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Bybit Testnet endpoints
BYBIT_TESTNET_BASE = "https://api-testnet.bybit.com"
BYBIT_MAINNET_BASE = "https://api.bybit.com"

# Use testnet for safety
BASE_URL = BYBIT_TESTNET_BASE


class BybitTestnetClient:
    """
    Minimal Bybit V5 API client for connectivity testing.
    Uses only standard library (no external dependencies).
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Bybit client.
        
        Args:
            api_key: Bybit API key (from env or wrangler secrets)
            api_secret: Bybit API secret (from env or wrangler secrets)
        """
        self.api_key = api_key or os.environ.get("BYBIT_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("BYBIT_API_SECRET", "")
        self.base_url = BASE_URL
        self.recv_window = "5000"
    
    def _generate_signature(self, timestamp: str, params: str) -> str:
        """Generate HMAC SHA256 signature for authenticated requests."""
        param_str = f"{timestamp}{self.api_key}{self.recv_window}{params}"
        return hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, method: str, endpoint: str, 
                      params: Optional[Dict] = None, 
                      authenticated: bool = False) -> Dict:
        """
        Make HTTP request to Bybit API.
        
        Args:
            method: HTTP method (GET, POST)
            endpoint: API endpoint path
            params: Request parameters
            authenticated: Whether to include auth headers
        
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        headers = {"Content-Type": "application/json"}
        
        if authenticated:
            timestamp = str(int(time.time() * 1000))
            
            if method == "GET":
                params_str = urlencode(params) if params else ""
                url = f"{url}?{params_str}" if params_str else url
            else:
                params_str = json.dumps(params) if params else ""
            
            signature = self._generate_signature(timestamp, params_str)
            
            headers.update({
                "X-BAPI-API-KEY": self.api_key,
                "X-BAPI-SIGN": signature,
                "X-BAPI-SIGN-TYPE": "2",
                "X-BAPI-TIMESTAMP": timestamp,
                "X-BAPI-RECV-WINDOW": self.recv_window,
            })
        else:
            if method == "GET" and params:
                url = f"{url}?{urlencode(params)}"
        
        try:
            if method == "GET":
                req = Request(url, headers=headers, method="GET")
            else:
                data = json.dumps(params).encode('utf-8') if params else None
                req = Request(url, data=data, headers=headers, method="POST")
            
            with urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
                
        except HTTPError as e:
            return {"retCode": e.code, "retMsg": str(e), "error": True}
        except URLError as e:
            return {"retCode": -1, "retMsg": f"Connection error: {e.reason}", "error": True}
        except Exception as e:
            return {"retCode": -1, "retMsg": str(e), "error": True}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 PUBLIC ENDPOINTS (No auth required)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_server_time(self) -> Dict:
        """Get Bybit server time."""
        return self._make_request("GET", "/v5/market/time")
    
    def get_tickers(self, category: str = "spot", symbol: str = "BTCUSDT") -> Dict:
        """Get ticker information."""
        return self._make_request("GET", "/v5/market/tickers", {
            "category": category,
            "symbol": symbol
        })
    
    def get_klines(self, category: str = "spot", symbol: str = "BTCUSDT", 
                   interval: str = "1", limit: int = 5) -> Dict:
        """Get kline/candlestick data."""
        return self._make_request("GET", "/v5/market/kline", {
            "category": category,
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        })
    
    def get_orderbook(self, category: str = "spot", symbol: str = "BTCUSDT", 
                      limit: int = 5) -> Dict:
        """Get orderbook depth."""
        return self._make_request("GET", "/v5/market/orderbook", {
            "category": category,
            "symbol": symbol,
            "limit": limit
        })
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🔐 PRIVATE ENDPOINTS (Auth required)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    def get_wallet_balance(self, account_type: str = "UNIFIED") -> Dict:
        """Get wallet balance (requires authentication)."""
        return self._make_request("GET", "/v5/account/wallet-balance", {
            "accountType": account_type
        }, authenticated=True)
    
    def get_positions(self, category: str = "linear") -> Dict:
        """Get open positions (requires authentication)."""
        return self._make_request("GET", "/v5/position/list", {
            "category": category
        }, authenticated=True)
    
    def get_api_key_info(self) -> Dict:
        """Get API key information (requires authentication)."""
        return self._make_request("GET", "/v5/user/query-api", 
                                  authenticated=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 TEST RUNNER | منفذ الاختبارات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_connectivity_tests():
    """Run all Bybit connectivity tests."""
    
    print("━" * 70)
    print("🔌 BYBIT TESTNET API CONNECTION TEST")
    print("━" * 70)
    print(f"📍 Base URL: {BASE_URL}")
    print("━" * 70)
    
    client = BybitTestnetClient()
    results = {}
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 1: Server Time (basic connectivity)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🧪 Test 1: Server Time (Basic Connectivity)")
    print("-" * 50)
    
    response = client.get_server_time()
    if response.get("retCode") == 0:
        server_time = response.get("result", {}).get("timeSecond", "N/A")
        print(f"   ✅ SUCCESS - Server time: {server_time}")
        results["server_time"] = "PASS"
    else:
        print(f"   ❌ FAILED - {response.get('retMsg', 'Unknown error')}")
        results["server_time"] = "FAIL"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 2: Market Ticker (public data)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🧪 Test 2: Market Ticker (BTCUSDT)")
    print("-" * 50)
    
    response = client.get_tickers(symbol="BTCUSDT")
    if response.get("retCode") == 0:
        tickers = response.get("result", {}).get("list", [])
        if tickers:
            ticker = tickers[0]
            print(f"   ✅ SUCCESS - BTCUSDT Last Price: ${ticker.get('lastPrice', 'N/A')}")
            print(f"      24h High: ${ticker.get('highPrice24h', 'N/A')}")
            print(f"      24h Low:  ${ticker.get('lowPrice24h', 'N/A')}")
            results["ticker"] = "PASS"
        else:
            print("   ⚠️ WARNING - No ticker data returned")
            results["ticker"] = "WARN"
    else:
        print(f"   ❌ FAILED - {response.get('retMsg', 'Unknown error')}")
        results["ticker"] = "FAIL"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 3: Klines (OHLCV data)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🧪 Test 3: Klines (1-min candles)")
    print("-" * 50)
    
    response = client.get_klines(symbol="BTCUSDT", interval="1", limit=3)
    if response.get("retCode") == 0:
        klines = response.get("result", {}).get("list", [])
        if klines:
            print(f"   ✅ SUCCESS - Retrieved {len(klines)} candles")
            for i, kline in enumerate(klines[:3]):
                print(f"      Candle {i+1}: O={kline[1]} H={kline[2]} L={kline[3]} C={kline[4]}")
            results["klines"] = "PASS"
        else:
            print("   ⚠️ WARNING - No kline data returned")
            results["klines"] = "WARN"
    else:
        print(f"   ❌ FAILED - {response.get('retMsg', 'Unknown error')}")
        results["klines"] = "FAIL"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 4: Orderbook (market depth)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🧪 Test 4: Orderbook (Market Depth)")
    print("-" * 50)
    
    response = client.get_orderbook(symbol="BTCUSDT", limit=5)
    if response.get("retCode") == 0:
        result = response.get("result", {})
        bids = result.get("b", [])
        asks = result.get("a", [])
        if bids or asks:
            print(f"   ✅ SUCCESS - Orderbook retrieved")
            print(f"      Top Bid: {bids[0] if bids else 'N/A'}")
            print(f"      Top Ask: {asks[0] if asks else 'N/A'}")
            results["orderbook"] = "PASS"
        else:
            print("   ⚠️ WARNING - Empty orderbook")
            results["orderbook"] = "WARN"
    else:
        print(f"   ❌ FAILED - {response.get('retMsg', 'Unknown error')}")
        results["orderbook"] = "FAIL"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Test 5: Authentication Test (wallet balance)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n🧪 Test 5: Authentication (Wallet Balance)")
    print("-" * 50)
    
    if not client.api_key or not client.api_secret:
        print("   ⚠️ SKIPPED - No API keys found in environment")
        print("      Set BYBIT_API_KEY and BYBIT_API_SECRET to test auth")
        results["auth"] = "SKIP"
    else:
        print(f"   🔑 API Key: {client.api_key[:8]}...{client.api_key[-4:]}")
        
        response = client.get_wallet_balance()
        if response.get("retCode") == 0:
            balances = response.get("result", {}).get("list", [])
            if balances:
                print(f"   ✅ SUCCESS - Authentication verified!")
                for account in balances:
                    coins = account.get("coin", [])
                    for coin in coins[:3]:
                        if float(coin.get("walletBalance", 0)) > 0:
                            print(f"      {coin.get('coin')}: {coin.get('walletBalance')}")
            else:
                print("   ✅ SUCCESS - Authenticated (no balances)")
            results["auth"] = "PASS"
        else:
            print(f"   ❌ FAILED - {response.get('retMsg', 'Unknown error')}")
            results["auth"] = "FAIL"
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Summary
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print("\n" + "━" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("━" * 70)
    
    passed = sum(1 for v in results.values() if v == "PASS")
    failed = sum(1 for v in results.values() if v == "FAIL")
    skipped = sum(1 for v in results.values() if v == "SKIP")
    warnings = sum(1 for v in results.values() if v == "WARN")
    
    for test, result in results.items():
        icon = "✅" if result == "PASS" else "❌" if result == "FAIL" else "⚠️" if result == "WARN" else "⏭️"
        print(f"   {icon} {test}: {result}")
    
    print("-" * 50)
    print(f"   Total: {len(results)} tests")
    print(f"   Passed: {passed} | Failed: {failed} | Warnings: {warnings} | Skipped: {skipped}")
    
    if failed == 0:
        print("\n✅ All critical tests passed! Bybit Testnet is accessible.")
    else:
        print("\n⚠️ Some tests failed. Check network or API configuration.")
    
    print("━" * 70)
    
    return results


if __name__ == "__main__":
    run_connectivity_tests()
