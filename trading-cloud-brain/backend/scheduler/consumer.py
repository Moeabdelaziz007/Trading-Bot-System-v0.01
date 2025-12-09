"""
📨 AXIOM NERVE CENTER - QUEUE CONSUMER
Handles Async Execution & Broadcasts

Responsibilities:
- Trade Execution (Broker API)
- Signal Broadcast (Telegram/Ably)
- Idempotency & Retries
"""

import json
from js import fetch, Headers

# ==========================================
# 🛠️ BROKER SERVICE (Mock/Generic)
# ==========================================

class BrokerService:
    def __init__(self, env):
        self.env = env
        # In a real scenario, we would load keys here
        # self.api_key = env.BROKER_API_KEY

    async def execute_trade(self, symbol, action, size, strategy):
        """
        Execute trade against Broker API.
        Current implementation: Generic Fetch / Mock
        """
        print(f"💰 EXECUTING: {action} {size} {symbol} ({strategy})")

        # 1. Idempotency Check (Prevent duplicates)
        # Unique ID based on params + approx time (minute precision) to avoid double execution in short window
        import time
        minute_ts = int(time.time() / 60)
        trade_id = f"{symbol}-{action}-{size}-{strategy}-{minute_ts}"

        # Check D1 if we already processed this
        try:
            existing = await self.env.TRADING_DB.prepare(
                "SELECT id FROM trade_logs WHERE trade_id = ?"
            ).bind(trade_id).first()

            if existing:
                print(f"⚠️ Duplicate trade detected: {trade_id}")
                return {"status": "skipped", "reason": "duplicate"}
        except:
            pass # If DB fails, proceed with caution (or fail open depending on risk preference)

        # 2. Call Broker API
        # Using a generic mock url or real if keys exist
        success = True # Simulate success

        # SIMULATION: If we were calling Hyperliquid/IBKR
        # response = await fetch("https://api.hyperliquid.xyz/exchange", ...)
        # if response.status not in [200, 201]: success = False

        if success:
            # 3. Log to D1
            try:
                await self.env.TRADING_DB.prepare(
                    "INSERT INTO trade_logs (trade_id, symbol, action, size, strategy, timestamp) VALUES (?, ?, ?, ?, ?, datetime('now'))"
                ).bind(trade_id, symbol, action, size, strategy).run()
            except Exception as e:
                print(f"⚠️ Failed to log trade: {e}")

            return {"status": "filled", "price": 0, "id": trade_id}
        else:
            raise Exception("Broker API Failed")


# ==========================================
# 📡 BROADCAST SERVICE
# ==========================================

class BroadcastService:
    def __init__(self, env):
        self.env = env

    async def send_telegram(self, message):
        token = getattr(self.env, 'TELEGRAM_BOT_TOKEN', None)
        chat_id = getattr(self.env, 'TELEGRAM_CHAT_ID', None)

        if not token or not chat_id:
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        await fetch(url, {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            })
        })

    async def send_ably(self, channel, data):
        key = getattr(self.env, 'ABLY_API_KEY', None)
        if not key:
            return

        import base64
        # Ably REST API
        # Basic Auth
        auth_str = base64.b64encode(key.encode()).decode()

        url = f"https://rest.ably.io/channels/{channel}/messages"
        await fetch(url, {
            "method": "POST",
            "headers": {
                "Authorization": f"Basic {auth_str}",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "name": "signal",
                "data": json.dumps(data)
            })
        })

    async def broadcast(self, type, message_data):
        """Fan-out to Telegram and Ably"""
        tasks = []

        # Format message for Telegram
        if type == "ALERT":
            text = f"🚨 <b>{message_data.get('title', 'ALERT')}</b>\n{message_data.get('body', '')}"
            tasks.append(self.send_telegram(text))

        # Send raw data to Ably
        tasks.append(self.send_ably("axiom_signals", message_data))

        # Run concurrently
        # In pure Python async we'd use gather, in Workers we rely on the runtime handling async tasks
        for t in tasks:
            await t


# ==========================================
# 📨 QUEUE CONSUMER CLASS
# ==========================================

class QueueConsumer:
    def __init__(self, env):
        self.env = env
        self.broker = BrokerService(env)
        self.broadcaster = BroadcastService(env)

    async def process_batch(self, batch):
        """
        Process a batch of messages from Cloudflare Queues.
        """
        for message in batch.messages:
            try:
                queue_name = batch.queue
                body = message.body # Already parsed JSON usually, or needs json.loads
                if isinstance(body, str):
                    body = json.loads(body)

                print(f"📨 Processing {queue_name}: {body}")

                if queue_name == "trade-queue" or queue_name == "trade-execution":
                    await self.broker.execute_trade(
                        symbol=body.get("symbol"),
                        action=body.get("action"),
                        size=body.get("size"),
                        strategy=body.get("strategy")
                    )

                elif queue_name == "broadcast-queue" or queue_name == "signal-broadcast":
                    await self.broadcaster.broadcast(
                        type=body.get("type", "ALERT"),
                        message_data=body
                    )

                # Acknowledge success
                message.ack()

            except Exception as e:
                print(f"❌ Error processing message: {e}")
                # Retry logic: Cloudflare Queues supports explicit retry
                message.retry()

# Export for binding
async def queue(batch, env, ctx):
    consumer = QueueConsumer(env)
    await consumer.process_batch(batch)
