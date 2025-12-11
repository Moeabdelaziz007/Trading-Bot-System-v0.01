"""
🌐 API HANDLERS - Extracted from worker.py
Handles all HTTP API endpoints for AlphaAxiom Trading System

Endpoints:
- /api/account - Account info
- /api/positions - Open positions  
- /api/candles - Chart data
- /api/market - Market snapshot
- /api/dashboard - Unified dashboard data
- /api/chat - MoE Chat handler
"""

from js import Response, fetch, Headers, JSON
import json
from base64 import b64encode

# Constants
ALPACA_API_URL = "https://paper-api.alpaca.markets/v2"
ALPACA_PAPER_URL = "https://paper-api.alpaca.markets"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
ABLY_API_URL = "https://rest.ably.io"


# ==========================================
# 📊 ACCOUNT ENDPOINTS
# ==========================================

async def get_account(env, headers):
    """Get Alpaca account info"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/account", method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            return Response.new(json.dumps({
                "portfolio_value": data.get("portfolio_value", "0"),
                "buying_power": data.get("buying_power", "0"),
                "cash": data.get("cash", "0"),
                "equity": data.get("equity", "0")
            }), headers=headers)
        
        return Response.new(json.dumps({"portfolio_value": "100000", "buying_power": "200000", "cash": "100000"}), headers=headers)
    except:
        return Response.new(json.dumps({"portfolio_value": "100000", "buying_power": "200000", "cash": "100000"}), headers=headers)


async def get_combined_account(env, headers):
    """Get Combined Account Data (Alpaca + OANDA)"""
    alpaca_data = await get_alpaca_account_data(env)
    
    try:
        from capital_connector import CapitalConnector
        capital_connector = CapitalConnector(env)
        capital_data = await capital_connector.get_account_info()
        
        if "error" not in capital_data and float(capital_data.get("balance", 0)) > 0:
            return Response.new(json.dumps({
                "portfolio_value": capital_data.get("equity"),
                "buying_power": capital_data.get("available"),
                "cash": capital_data.get("balance"),
                "equity": capital_data.get("equity"),
                "source": capital_data.get("source", "Capital.com")
            }), headers=headers)
    except:
        pass
        
    return await get_account(env, headers)


async def get_account_data(env):
    """Helper: Get account data without Response wrapper"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(ALPACA_PAPER_URL + "/v2/account", method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            return {
                "balance": float(data.get("cash", 0)),
                "equity": float(data.get("equity", 0)),
                "buying_power": float(data.get("buying_power", 0)),
                "day_trades": int(data.get("daytrade_count", 0))
            }
        return {"balance": 0, "equity": 0}
    except:
        return {"balance": 0, "equity": 0}


async def get_alpaca_account_data(env):
    """Get Alpaca account data as dict"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/account", method="GET", headers=req_headers)
        
        if response.ok:
            return json.loads(await response.text())
        return {"equity": "100000", "cash": "100000", "buying_power": "200000"}
    except:
        return {"equity": "100000", "cash": "100000", "buying_power": "200000"}


# ==========================================
# 📈 POSITIONS ENDPOINTS
# ==========================================

async def get_positions(env, headers):
    """Get Alpaca positions"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/positions", method="GET", headers=req_headers)
        
        if response.ok:
            positions = json.loads(await response.text())
            return Response.new(json.dumps(positions), headers=headers)
        
        return Response.new(json.dumps([]), headers=headers)
    except:
        return Response.new(json.dumps([]), headers=headers)


async def get_combined_positions(env, headers):
    """Fetch positions from both brokers"""
    all_positions = []
    
    alp_pos = await get_alpaca_positions_data(env)
    if alp_pos: all_positions.extend(alp_pos)
    
    try:
        from capital_connector import CapitalConnector
        capital = CapitalConnector(env)
        capital_pos = await capital.get_open_positions()
        if capital_pos: all_positions.extend(capital_pos)
    except:
        pass
    
    try:
        from oanda_connector import OandaBroker
        oanda = OandaBroker(env)
        oanda_pos = await oanda.get_positions()
        if oanda_pos: all_positions.extend(oanda_pos)
    except:
        pass
        
    return Response.new(json.dumps(all_positions), headers=headers)


async def get_alpaca_positions_data(env):
    """Get Alpaca positions as list"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(f"{ALPACA_API_URL}/positions", method="GET", headers=req_headers)
        
        if response.ok:
            return json.loads(await response.text())
        return []
    except:
        return []


# ==========================================
# 📊 MARKET DATA ENDPOINTS
# ==========================================

async def get_candles(request, env, headers):
    """API endpoint for candles with KV Caching"""
    url = str(request.url)
    symbol = "SPY"
    
    if "symbol=" in url:
        symbol = url.split("symbol=")[1].split("&")[0].upper()
    
    # KV Cache Check
    cache_key = f"candles_{symbol}"
    try:
        if hasattr(env, 'BRAIN_MEMORY'):
            cached = await env.BRAIN_MEMORY.get(cache_key)
            if cached:
                return Response.new(json.dumps({"symbol": symbol, "candles": json.loads(cached), "cached": True}), headers=headers)
    except:
        pass

    candles = await fetch_alpaca_bars(symbol, env)
    
    # Cache Result
    try:
        if hasattr(env, 'BRAIN_MEMORY') and candles:
            await env.BRAIN_MEMORY.put(cache_key, json.dumps(candles), expiration_ttl=60)
    except:
        pass
        
    return Response.new(json.dumps({"symbol": symbol, "candles": candles}), headers=headers)


async def fetch_alpaca_bars(symbol, env):
    """Fetch candles from Alpaca for charting"""
    try:
        alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
        alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
        
        is_crypto = symbol in ["BTC", "ETH", "BTCUSD", "ETHUSD", "SOL", "DOGE"]
        
        if is_crypto:
            clean_symbol = symbol.replace("USD", "") + "/USD"
            url = f"https://data.alpaca.markets/v1beta3/crypto/us/bars?symbols={clean_symbol}&timeframe=1Hour&limit=100"
        else:
            url = f"https://data.alpaca.markets/v2/stocks/{symbol}/bars?timeframe=1Hour&limit=100"
        
        req_headers = Headers.new({
            "APCA-API-KEY-ID": alpaca_key,
            "APCA-API-SECRET-KEY": alpaca_secret
        }.items())
        
        response = await fetch(url, method="GET", headers=req_headers)
        
        if response.ok:
            data = json.loads(await response.text())
            
            if is_crypto:
                bars = data.get("bars", {}).get(clean_symbol, [])
            else:
                bars = data.get("bars", [])
            
            return [{"t": b.get("t"), "o": b.get("o"), "h": b.get("h"), "l": b.get("l"), "c": b.get("c"), "v": b.get("v")} for b in bars]
        
        return generate_demo_candles()
    except:
        return generate_demo_candles()


def generate_demo_candles():
    """Generate demo candle data"""
    import random
    candles = []
    base_price = 100.0
    
    for i in range(100):
        open_price = base_price + random.uniform(-2, 2)
        close_price = open_price + random.uniform(-3, 3)
        high_price = max(open_price, close_price) + random.uniform(0, 1)
        low_price = min(open_price, close_price) - random.uniform(0, 1)
        
        candles.append({
            "t": f"2024-01-{(i % 30) + 1:02d}T{i % 24:02d}:00:00Z",
            "o": round(open_price, 2),
            "h": round(high_price, 2),
            "l": round(low_price, 2),
            "c": round(close_price, 2),
            "v": random.randint(1000, 100000)
        })
        base_price = close_price
    
    return candles


async def get_market_snapshot(request, env, headers):
    """Get real-time market data with price changes"""
    url = str(request.url)
    
    default_symbols = ["SPY", "AAPL", "BTC/USD", "ETH/USD"]
    
    if "symbols=" in url:
        symbols_param = url.split("symbols=")[1].split("&")[0]
        symbols = [s.strip().upper() for s in symbols_param.split(",")]
    else:
        symbols = default_symbols
    
    alpaca_key = str(getattr(env, 'ALPACA_KEY', ''))
    alpaca_secret = str(getattr(env, 'ALPACA_SECRET', ''))
    
    results = []
    
    for symbol in symbols[:6]:
        try:
            is_crypto = "/" in symbol or symbol in ["BTC", "ETH", "SOL", "DOGE"]
            
            if is_crypto:
                crypto_symbol = symbol.replace("/USD", "") + "/USD" if "/" not in symbol else symbol
                snapshot_url = f"https://data.alpaca.markets/v1beta3/crypto/us/snapshots?symbols={crypto_symbol}"
            else:
                snapshot_url = f"https://data.alpaca.markets/v2/stocks/{symbol}/snapshot"
            
            req_headers = Headers.new({
                "APCA-API-KEY-ID": alpaca_key,
                "APCA-API-SECRET-KEY": alpaca_secret
            }.items())
            
            response = await fetch(snapshot_url, method="GET", headers=req_headers)
            
            if response.ok:
                data = json.loads(await response.text())
                
                if is_crypto:
                    crypto_data = data.get("snapshots", {}).get(crypto_symbol, {})
                    daily = crypto_data.get("dailyBar", {})
                    prev = crypto_data.get("prevDailyBar", {})
                else:
                    daily = data.get("dailyBar", {})
                    prev = data.get("prevDailyBar", {})
                
                is_market_closed = not daily or daily.get("v", 0) == 0
                
                if is_market_closed and prev:
                    current_price = float(prev.get("c", 0))
                    change_percent = 0.0
                    volume = prev.get("v", 0)
                else:
                    current_price = float(daily.get("c", 0)) if daily else 0
                    prev_close = float(prev.get("c", current_price)) if prev else current_price
                    if prev_close > 0:
                        change_percent = ((current_price - prev_close) / prev_close) * 100
                    else:
                        change_percent = 0.0
                    volume = daily.get("v", 0) if daily else 0
                
                results.append({
                    "symbol": symbol,
                    "price": round(current_price, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": volume,
                    "is_closed": is_market_closed
                })
            else:
                results.append({"symbol": symbol, "price": 0, "change_percent": 0, "error": "Failed to fetch"})
        except Exception as e:
            results.append({"symbol": symbol, "price": 0, "change_percent": 0, "error": str(e)})
    
    # Broadcast to Ably
    try:
        await publish_to_ably(env, "market-data", results)
    except:
        pass
        
    return Response.new(json.dumps({"symbols": results}), headers=headers)


# ==========================================
# 🎯 DASHBOARD ENDPOINT
# ==========================================

async def get_dashboard_snapshot(env, headers):
    """Aggregated Dashboard Data - Single Request for All UI Needs"""
    results = {}
    
    try:
        results["account"] = await get_account_data(env)
    except:
        results["account"] = {"balance": 0, "equity": 0}
    
    try:
        results["positions"] = await get_alpaca_positions_data(env) or []
    except:
        results["positions"] = []
    
    try:
        kv = env.BRAIN_MEMORY
        aexi_score = await kv.get("aexi_score")
        dream_score = await kv.get("dream_score")
        last_signal = await kv.get("last_signal")
        
        results["engines"] = {
            "aexi": float(aexi_score) if aexi_score else 50.0,
            "dream": float(dream_score) if dream_score else 50.0,
            "last_signal": json.loads(last_signal) if last_signal else None
        }
        
        # Spider Brain Agents
        spider_agents = await kv.get("spider_agents")
        results["spider_agents"] = json.loads(spider_agents) if spider_agents else []
    except:
        results["engines"] = {"aexi": 50.0, "dream": 50.0, "last_signal": None}
        results["spider_agents"] = []
    
    try:
        db = env.TRADING_DB
        bots_result = await db.prepare("SELECT * FROM bots WHERE active = 1 LIMIT 5").all()
        results["bots"] = bots_result.results if bots_result else []
    except:
        results["bots"] = []
    
    from datetime import datetime
    results["timestamp"] = datetime.utcnow().isoformat()
    
    return Response.new(json.dumps(results), headers=headers)


# ==========================================
# ⚡ ABLY REALTIME
# ==========================================

async def publish_to_ably(env, channel, data):
    """Publish real-time update to Ably"""
    try:
        ably_key = str(getattr(env, 'ABLY_API_KEY', ''))
        if not ably_key: return
        
        url = f"{ABLY_API_URL}/channels/{channel}/messages"
        
        key_name, key_secret = ably_key.split(':')
        auth_str = f"{key_name}:{key_secret}"
        auth_b64 = b64encode(auth_str.encode('utf-8')).decode('utf-8')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
        
        body = {"name": "update", "data": data}
        
        await fetch(url, method="POST", headers=headers, body=json.dumps(body))
    except Exception as e:
        print(f"Ably Publish Error: {e}")
