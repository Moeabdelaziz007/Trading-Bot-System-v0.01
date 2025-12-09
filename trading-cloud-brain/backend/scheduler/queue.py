"""
⚡ QUEUE CONSUMER
Handles Async Trade Execution and Alerts.
Decouples "Thinking" (Brain) from "Doing" (API Calls).
"""

import json
from js import fetch

async def execute_trade(env, trade: dict):
    """
    Execute trade via Broker API.
    Retries automatically on failure.
    """
    symbol = trade.get("symbol")
    action = trade.get("action")
    size = trade.get("size")
    
    # 1. Deduplication (Idempotency)
    # Check if trade ID already exists in D1
    # await env.TRADING_DB.prepare(...).first()
    
    # 2. Broker Routing
    # Simulating broker call
    broker_url = "https://api.hyperliquid.xyz/exchange" # Example
    
    # In a real scenario, we use the Broker classes from shared/brokers.py
    # For now, we simulate the network call
    print(f"Executing {action} {size} {symbol} on Hyperliquid...")
    
    # Simulate API call failure for testing retry
    # if random.random() < 0.1: raise Exception("Broker API Timeout")
    
    return {"status": "filled", "price": 50000}


async def broadcast_signal(env, signal: dict):
    """
    Push alerts to multiple channels (Telegram, Ably).
    """
    message = signal.get("message")
    
    # 1. Telegram
    if hasattr(env, 'TELEGRAM_BOT_TOKEN'):
        chat_id = env.TELEGRAM_CHAT_ID
        url = f"https://api.telegram.org/bot{env.TELEGRAM_BOT_TOKEN}/sendMessage"
        await fetch(url, {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"chat_id": chat_id, "text": message})
        })
        
    # 2. Ably Realtime
    if hasattr(env, 'ABLY_API_KEY'):
        # Ably logic here
        pass


async def on_queue(batch, env, ctx):
    """
    Main Queue Entry Point.
    Cloudflare automatically retries explicit NACKs.
    """
    for msg in batch:
        try:
            body = json.loads(msg.body)
            msg_type = body.get("type", "unknown")
            
            if msg_type == "TRADE_EXECUTION":
                await execute_trade(env, body)
                msg.ack()
                
            elif msg_type == "SIGNAL_BROADCAST":
                await broadcast_signal(env, body)
                msg.ack()
                
            else:
                # Unknown message, ack to remove from queue
                print(f"Unknown message type: {msg_type}")
                msg.ack()
                
        except Exception as e:
            print(f"Failed to process message {msg.id}: {e}")
            # Retry with exponential backoff (handled by Cloudflare)
            msg.retry()
