# 💎 Future Gems - Research Archive

> **Note:** This file contains deep research results for future integration phases.
> Current focus: Capital.com + Alpaca testing.

---

## 🏦 Broker Integration Gems (For Live Trading)

### Top Tier Brokers for Future

| Broker | Why It's a Gem | Latency | API Type | Min Deposit |
|--------|----------------|---------|----------|-------------|
| **OANDA** | Best Free API (v20), Python lib ready | ~20ms | REST + MT5 | $0 |
| **Pepperstone** | Fastest ECN execution, 0.0 spreads | ~12ms | FIX + MT5 | $200 |
| **IC Markets** | Raw spreads, cTrader Automate | ~15ms | cTrader API | $200 |
| **FXCM** | Multi-SDK support (REST/JAVA/FIX) | ~25ms | ForexConnect | $50 |
| **Interactive Brokers** | TWS API, CCXT support | <1s | TWS + REST | $0 |
| **Exness** | MT5 EAs, 0.0 pip spreads | ~30ms | MT5 API | $10 |
| **Axi** | Free VPS for live, Autochartist | ~20ms | MT5 | $0 |

### CCXT Universal Connector

```python
# Supports 120+ exchanges with unified interface
pip install ccxt

import ccxt
oanda = ccxt.oanda({'apiKey': 'xxx'})
ticker = oanda.fetch_ticker('EUR/USD')
```

---

## 🧠 Advanced LLM Gems (Chinese Open-Source)

### Top Free APIs (Dec 2025)

| LLM | Performance | Free Limits | Best For |
|-----|-------------|-------------|----------|
| **Google AI Studio (Gemini 3.0)** | Multimodal, strong reasoning | 1M tokens/day | Analysis |
| **Groq (Llama 4 Scout)** | Blazing fast | 14k req/day | Real-time |
| **OpenRouter** | 300+ models | ~1k tokens/model | Rotation |
| **Together AI** | 100+ open models | 1M tokens/month | Testing |

### Chinese Open-Source (UNLIMITED - Local)

| Model | Why It's Top | How to Run |
|-------|--------------|------------|
| **DeepSeek R1** | Beats GPT-5.1 in reasoning | `ollama run deepseek-r1` |
| **Qwen 2.5** | Multimodal like Gemini 3.0 | `ollama run qwen2.5` |
| **GLM-4** | Strong analysis | Hugging Face |
| **ChatGLM** | Chat quality like GPT-5 | Open-source |
| **Kimi** | Fast reasoning | API or local |

### Ollama Setup (Unlimited Tokens)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Run DeepSeek R1 locally
ollama run deepseek-r1

# OpenAI-compatible endpoint
curl http://localhost:11434/v1/chat/completions
```

---

## 📋 Integration Priority (Future)

1. ✅ **Phase 1 (Current):** Capital.com Demo + Alpaca Paper
2. 🔜 **Phase 2:** OANDA v20 API
3. ⏳ **Phase 3:** DeepSeek R1 via Ollama (local)
4. ⏳ **Phase 4:** CCXT Universal Multi-Broker
5. ⏳ **Phase 5:** Pepperstone FIX (Scalping)

---

*Last Updated: Dec 7, 2025*
