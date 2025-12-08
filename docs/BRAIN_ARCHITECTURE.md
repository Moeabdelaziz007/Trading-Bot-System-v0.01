# 🧠 Brain Architecture - Antigravity Trading System

## Overview

The Antigravity Brain is a Mixture of Experts (MoE) architecture running on Cloudflare Workers.

```
┌─────────────────────────────────────────────────────────────┐
│                    🧠 ANTIGRAVITY BRAIN                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    CORTEX (Decisions)               │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │ Trading  │  │   Risk   │  │  Twin    │          │    │
│  │  │  Brain   │  │ Guardian │  │  Turbo   │          │    │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │    │
│  └───────┼─────────────┼─────────────┼─────────────────┘    │
│          │             │             │                       │
│  ┌───────▼─────────────▼─────────────▼─────────────────┐    │
│  │                   SENSORS (Input)                    │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │    │
│  │  │  Data    │  │ Economic │  │ Pattern  │          │    │
│  │  │Collector │  │ Calendar │  │ Scanner  │          │    │
│  │  └──────────┘  └──────────┘  └──────────┘          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  ACTUATORS (Output)                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │ Broker   │  │ Telegram │  │   Ably   │           │   │
│  │  │ Gateway  │  │  Alerts  │  │ Realtime │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              ⚠️ STATE LAYER (MISSING)                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │ │
│  │  │  Trade   │  │  Order   │  │   Cron   │              │ │
│  │  │  State   │  │   Lock   │  │  Guard   │              │ │
│  │  └──────────┘  └──────────┘  └──────────┘              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Cloudflare Cron Schedule

| Cron | Frequency | Brain Part | Modules |
|------|-----------|------------|---------|
| `* * * * *` | Every 1 min | Risk Layer | RiskGuardian, Calendar |
| `*/5 * * * *` | Every 5 min | Fast Brain | TradingBrain[SCALP], PatternScanner |
| `0 */4 * * *` | Every 4 hrs | Slow Brain | TradingBrain[SWING] |

---

## Module → Brain Part Mapping

### CORTEX (Decision Layer)

```python
# Runs in on_scheduled()
TradingBrain(mode="SCALP")  # Fast decisions (5 min)
TradingBrain(mode="SWING")  # Slow decisions (4 hr)
TwinTurbo.analyze()         # AEXI + Dream intelligence
RiskGuardian.check()        # Safety override (1 min)
```

### SENSORS (Input Layer)

```python
# Data gathering before decisions
DataCollector.fetch_candles()     # Price data
EconomicCalendar.check_alerts()   # News events
PatternScanner.scan_all()         # Chart patterns
BrokerGateway.get_market_data()   # Real-time quotes
```

### ACTUATORS (Output Layer)

```python
# Execution after decisions
BrokerGateway.place_order()       # Execute trades
send_telegram_alert()             # Send signals
ably_publish()                    # Real-time updates
```

### STATE (Coordination Layer) ⚠️ NEEDED

```python
# Prevent race conditions
TradeState.lock_symbol()          # Lock before order
TradeState.record_trade()         # Track open trades
CronGuard.acquire()               # One cron at a time
```

---

## Worker Entry Points

| Function | Trigger | Purpose |
|----------|---------|---------|
| `on_fetch(request, env)` | HTTP Request | API endpoints |
| `on_scheduled(event, env)` | Cron Trigger | Automated trading |

---

## Data Flow

```
1. CRON TRIGGER (Every 5 min)
   │
   ▼
2. RISK CHECK (RiskGuardian)
   │ Is it safe to trade?
   ▼
3. DATA COLLECTION (Sensors)
   │ Fetch candles, news, patterns
   ▼
4. SIGNAL GENERATION (Brain)
   │ TradingBrain + TwinTurbo
   ▼
5. STATE CHECK (⚠️ MISSING)
   │ Am I already in a trade?
   ▼
6. ORDER EXECUTION (Actuators)
   │ BrokerGateway.place_order()
   ▼
7. NOTIFICATION (Telegram)
   │ Alert user
   ▼
8. STATE UPDATE (⚠️ MISSING)
   │ Record trade, unlock symbol
```
