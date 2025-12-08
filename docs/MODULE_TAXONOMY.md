# 🧩 Module Taxonomy - Trading System v0.1

## Module Types (8 Categories)

| # | Type | Icon | Purpose |
|---|------|------|---------|
| 1 | CORE | 🔧 | Infrastructure, utilities |
| 2 | SENSOR | 👁️ | Data input, market feeds |
| 3 | BRAIN | 🧠 | Decision making, strategies |
| 4 | RISK | 🛡️ | Safety, kill switches |
| 5 | EXECUTOR | 🦾 | Order execution |
| 6 | NOTIFIER | 📢 | Alerts, notifications |
| 7 | AI | 🤖 | LLM services |
| 8 | STATE | ⚡ | Coordination, locks |

---

## Current Modules by Type

### 🔧 CORE (Infrastructure)

| Module | Location | Status |
|--------|----------|--------|
| Logger | `src/core/logger.py` | ✅ Consolidated |
| Exceptions | `src/core/exceptions.py` | ✅ Consolidated |
| RateLimiter | `src/core/rate_limiter.py` | ✅ Consolidated |

### 👁️ SENSOR (Data Input)

| Module | Location | Status |
|--------|----------|--------|
| PatternScanner | `src/patterns/` | ✅ NEW |
| DataCollector | `src/data_collector.py` | ⚠️ Standalone |
| EconomicCalendar | `src/economic_calendar.py` | ⚠️ Standalone |

### 🧠 BRAIN (Decisions)

| Module | Location | Status |
|--------|----------|--------|
| TradingBrain | `src/strategy/` | ✅ Consolidated |
| TwinTurbo | `src/intelligence/` | ✅ Consolidated |

### 🛡️ RISK (Safety)

| Module | Location | Status |
|--------|----------|--------|
| RiskGuardian | `src/risk_manager.py` | ⚠️ Standalone |

### 🦾 EXECUTOR (Orders)

| Module | Location | Status |
|--------|----------|--------|
| BrokerGateway | `src/brokers/` | ✅ Consolidated |
| OandaProvider | `src/brokers/oanda.py` | ✅ Consolidated |
| CapitalProvider | `src/brokers/capital.py` | ✅ Consolidated |

### 📢 NOTIFIER (Alerts)

| Module | Location | Status |
|--------|----------|--------|
| Telegram | `worker.py` | ⚠️ Embedded |
| Ably | `worker.py` | ⚠️ Embedded |

### 🤖 AI (LLM Services)

| Module | Location | Status |
|--------|----------|--------|
| DeepSeekAnalyst | `src/deepseek_analyst.py` | ⚠️ Standalone |
| WorkersAI | `src/workers_ai.py` | ⚠️ Standalone |
| Groq/Gemini | `worker.py` | ⚠️ Embedded |

### ⚡ STATE (Coordination)

| Module | Location | Status |
|--------|----------|--------|
| TradeState | - | ❌ MISSING |
| OrderLock | - | ❌ MISSING |
| CronGuard | - | ❌ MISSING |

---

## Priority Matrix

| Priority | Category | Issue | Solution |
|----------|----------|-------|----------|
| 🔴 High | STATE | Missing entirely | Phase 18: Durable Objects |
| 🟡 Medium | SENSOR | Not consolidated | MarketFeed package |
| 🟡 Medium | AI | Not consolidated | AnalystCore package |
| 🟢 Low | NOTIFIER | Embedded | Extract to package |

---

## Legacy Files (Duplicates to Remove)

```
src/
├── aexi_engine.py        → intelligence/twin_turbo.py
├── dream_engine.py       → intelligence/twin_turbo.py
├── scalping_engine.py    → strategy/trading_brain.py
├── long_term_engine.py   → strategy/trading_brain.py
├── capital_connector.py  → brokers/capital.py
└── oanda_connector.py    → brokers/oanda.py
```
