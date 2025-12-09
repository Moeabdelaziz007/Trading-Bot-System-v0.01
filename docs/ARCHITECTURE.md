# 🏗️ Axiom Antigravity - Architecture Documentation

> System Architecture v1.0 | Trading System v0.1

---

## 📊 System Context (C4 Level 1)

```mermaid
graph TB
    subgraph External["🌐 External Systems"]
        Alpaca["Alpaca API<br/>(Stocks/Crypto)"]
        Capital["Capital.com<br/>(Forex/CFD)"]
        Telegram["Telegram Bot<br/>(@your_bot)"]
        Groq["Groq API<br/>(LLama 3 Fast)"]
        Gemini["Gemini API<br/>(Analysis)"]
        DeepSeek["DeepSeek API<br/>(Strategy)"]
    end

    subgraph Users["👤 Users"]
        Trader["Trader"]
        Admin["Admin"]
    end

    subgraph System["⚡ Axiom Antigravity"]
        Frontend["📱 Frontend<br/>(Next.js)"]
        Backend["🔧 Backend<br/>(FastAPI)"]
        CloudBrain["🧠 Cloud Brain<br/>(CF Workers)"]
    end

    Trader --> Frontend
    Trader --> Telegram
    Admin --> Telegram
    
    Frontend --> CloudBrain
    Backend --> CloudBrain
    Telegram --> CloudBrain
    
    CloudBrain --> Alpaca
    CloudBrain --> Capital
    CloudBrain --> Groq
    CloudBrain --> Gemini
    CloudBrain --> DeepSeek
```

---

## 🧠 Cloud Brain Containers (C4 Level 2)

```mermaid
graph TB
    subgraph CloudBrain["🧠 Trading Cloud Brain (Cloudflare Workers)"]
        Worker["worker.py<br/>MoE Router"]
        
        subgraph Engines["Trading Engines"]
            Scalping["ScalpingBrain<br/>14 Technical Tools"]
            LongTerm["LongTermBrain<br/>Golden Cross"]
            AEXI["AEXIEngine<br/>Exhaustion Index"]
            Dream["DreamMachine<br/>Chaos Theory"]
        end
        
        subgraph Connectors["Data Connectors"]
            CapitalConn["CapitalConnector"]
            DeepSeekAn["DeepSeekAnalyst"]
            EconCal["EconomicCalendar"]
        end
        
        subgraph Guards["Risk Management"]
            RiskGuard["RiskGuardian<br/>Kelly + Chaos"]
        end
    end
    
    subgraph Storage["💾 Storage"]
        D1[("D1 Database<br/>SQLite")]
        KV[("KV Storage<br/>Cache")]
    end
    
    subgraph AI["🤖 Workers AI"]
        WAI["llama-2-7b<br/>Edge Inference"]
    end
    
    Worker --> Engines
    Worker --> Connectors
    Worker --> Guards
    Worker --> D1
    Worker --> KV
    Worker --> WAI
```

---

## 📁 Codebase Structure

```
Trading.System-0.1/
├── frontend/                   # 📱 Vite + React 19 Dashboard
│   └── src/components/        # React components
│
├── backend/                    # 🔧 FastAPI Server
│   ├── main.py                # 14 endpoints + WebSocket
│   └── dual_brain.py          # DeepSeek + Gemini
│
├── trading-cloud-brain/        # 🧠 Cloudflare Workers
│   ├── src/
│   │   ├── worker.py          # Main router (2420 lines)
│   │   ├── scalping_engine.py # 14 technical indicators
│   │   ├── long_term_engine.py# Golden Cross logic
│   │   ├── aexi_engine.py     # Exhaustion detection
│   │   ├── dream_engine.py    # Chaos analysis
│   │   ├── risk_manager.py    # Kelly + Chaos Factor
│   │   ├── capital_connector.py
│   │   └── deepseek_analyst.py
│   ├── wrangler.toml          # Worker config
│   └── schema.sql             # D1 schema
│
└── docs/                       # 📖 Documentation
```

---

## ⚡ Trading Flow

```mermaid
sequenceDiagram
    participant Cron as ⏰ Cron (1min)
    participant Worker as 🧠 Worker
    participant Scalping as ScalpingBrain
    participant AEXI as AEXI Engine
    participant Dream as Dream Machine
    participant Risk as RiskGuardian
    participant Analyst as Analyst (Groq)
    participant Capital as Capital.com
    participant TG as Telegram

    Cron->>Worker: Trigger
    Worker->>Capital: Fetch OHLCV
    Capital-->>Worker: Market Data
    
    par Technical Analysis
        Worker->>Scalping: analyze_market_state()
        Worker->>AEXI: get_aexi_score()
        Worker->>Dream: get_dream_score()
    end
    
    Worker->>Worker: detect_twin_turbo_signal()
    
    alt Signal Detected
        Worker->>Analyst: consult_the_analyst()
        Analyst-->>Worker: {confidence: 85%}
        
        alt Confidence ≥ 75%
            Worker->>Risk: validate_signal()
            Risk-->>Worker: Kelly sizing
            Worker->>Capital: Execute Trade
            Worker->>TG: 📊 Signal Alert
        else Confidence < 75%
            Worker->>TG: ⚠️ Rejected (low confidence)
        end
    end
```

---

## 🔐 Data Models

### D1 Database Tables

| Table | Purpose |
|-------|---------|
| `trading_rules` | Active trading rules |
| `rules` | Rule definitions |
| `trade_logs` | Trade history |
| `user_context` | User preferences |
| `system_state` | Kill switch, panic mode |

### Key Environment Variables

| Variable | Type | Description |
|----------|------|-------------|
| `ABLY_API_KEY` | 🔐 Secret | Real-time updates |
| `CAPITAL_API_KEY` | 🔐 Secret | Capital.com trading |
| `GROQ_API_KEY` | 🔐 Secret | LLM inference |
| `DEEPSEEK_API_KEY` | 🔐 Secret | Strategy analysis |
| `TELEGRAM_BOT_TOKEN` | 🔐 Secret | Bot authentication |

---

## 🎯 AI Agents

| Agent | Model | Purpose | Cost |
|-------|-------|---------|------|
| **Router** | Groq Llama 3 | Intent classification | Free |
| **Analyst** | Groq Llama 3.3 | Signal validation | Free |
| **Strategist** | DeepSeek | Deep analysis | ~$0.001/call |
| **Edge AI** | Workers AI Llama | Fallback | Free |

---

## 🚦 Safety Systems

```mermaid
graph LR
    subgraph Safety["🛡️ Risk Controls"]
        Kill["Kill Switch<br/>(Manual)"]
        Panic["Panic Protocol<br/>(Auto @ 5% loss)"]
        MaxTrades["Max Daily Trades<br/>(Limit)"]
        NewsGuard["News Guard<br/>(Event Filter)"]
    end
    
    Signal --> Safety
    Safety -->|Pass| Execute
    Safety -->|Fail| Block
```

---

*Generated: 2025-12-08*
