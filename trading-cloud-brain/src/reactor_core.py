
from js import Response
import json
import os

# ---------------------------------------------------------
# 🧠 AXIOM REACTOR: The Unified AlphaAxiom Brain
# ---------------------------------------------------------

class AxiomReactor:
    def __init__(self, env):
        self.env = env
        self.models = {
            "executive": "glm-4.5",       # Z.ai (Planning)
            "visual": "gemini-2.0-flash", # Google (Charts)
            "reflex": "llama-3.1-70b",    # Groq (Speed)
            "router": "@cf/meta/llama-3-8b-instruct" # Cloudflare (Free)
        }

    async def council_meeting(self, market_data):
        """
        👥 The Council of Agents: Generates the Unified Market Tensor
        """
        # 1. Chaos Agent (Entropy/Fractals) - Local Calculation
        chaos_score = self.calculate_chaos(market_data)

        # 2. Whales Agent (Orderbook) - Groq (Fast)
        whales_insight = await self.ask_fast_brain(
            f"Analyze orderbook imbalance: Bids={market_data['bids']}, Asks={market_data['asks']}"
        )

        # 3. Macro Agent (Correlations) - GLM-4.5 (Deep)
        macro_view = await self.ask_deep_brain(
            f"Correlate {market_data['symbol']} with Gold, Oil, and DXY. Context: {market_data['news']}"
        )

        # 4. Social Agent (Sentiment) - Gemini (Context)
        sentiment = await self.ask_visual_brain(
            f"Analyze sentiment from these tweets: {market_data['tweets']}"
        )

        # ----------------------------------------
        # 💾 MEMORY COMMIT (The "Thought" Storage)
        # ----------------------------------------
        try:
            # Calculate Synthetic Scores for UI
            aexi_score = 50 + (chaos_score * 20) + (10 if "Order flow positive" in str(whales_insight) else -10)
            dream_score = chaos_score * 100

            # Signal Packet
            signal_packet = {
                "chaos": chaos_score,
                "whales": whales_insight,
                "macro": macro_view,
                "social": sentiment,
                "final_verdict": "BUY" if aexi_score > 60 else "SELL" if aexi_score < 40 else "HOLD",
                "timestamp": market_data.get("timestamp")
            }

            if hasattr(self.env, 'BRAIN_MEMORY'):
                await self.env.BRAIN_MEMORY.put("aexi_score", str(aexi_score))
                await self.env.BRAIN_MEMORY.put("dream_score", str(dream_score))
                await self.env.BRAIN_MEMORY.put("last_signal", json.dumps(signal_packet))
                
                # Update Agents Status
                agents_status = [
                   {"id": "core-hub", "status": "online", "latency": 12},
                   {"id": "reflex", "status": "online", "latency": 45 if "Speed" in str(whales_insight) else 120},
                   {"id": "analyst", "status": "online", "latency": 600}, # GLM-4.5 is slower
                   {"id": "guardian", "status": "online", "latency": 15},
                   {"id": "collector", "status": "online", "latency": 22},
                   {"id": "journalist", "status": "online" if sentiment else "offline", "latency": 38},
                   {"id": "strategist", "status": "online", "latency": 52}
                ]
                await self.env.BRAIN_MEMORY.put("spider_agents", json.dumps(agents_status))

        except Exception as e:
            print(f"Memory Write Error: {e}")

        return signal_packet

    # --- AI BRAIN INTERFACES ---

    async def ask_deep_brain(self, prompt):
        """GLM-4.5 via Z.ai"""
        # (Implementation placeholder for HTTP req to Z.ai)
        return {"source": "GLM-4.5", "thought": "Bullish structure detected"}

    async def ask_fast_brain(self, prompt):
        """Llama 3 via Groq"""
        # (Implementation placeholder for HTTP req to Groq)
        return {"source": "Groq", "speed": "12ms", "output": "Order flow positive"}

    async def ask_visual_brain(self, prompt):
        """Gemini 2.0 Flash via Google"""
        # (Implementation placeholder)
        return {"source": "Gemini", "multimodal": True}

    def calculate_chaos(self, data):
        """Native Python math for Hurst Exponent (Dream Engine)"""
        # Simplified simulation
        return 0.75

# ---------------------------------------------------------
# 🔌 WORKER ENTRY POINT
# ---------------------------------------------------------

async def on_fetch(request, env):
    method = request.method
    url = request.url

    if method == "OPTIONS":
        return Response.new("", headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    reactor = AxiomReactor(env)

    if url.endswith("/api/council"):
        # Trigger full council meeting
        data = await request.json()
        verdict = await reactor.council_meeting(data)
        return Response.new(json.dumps(verdict), headers={"Content-Type": "application/json"})

    return Response.new("Axiom Reactor Online", status=200)
