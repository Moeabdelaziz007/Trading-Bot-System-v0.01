# 🛡️ ALPHA AXIOM RISK CONSTITUTION

> **Version:** 1.0  
> **Status:** ACTIVE  
> **Enforcement:** `RiskGuardian` (Pre-Trade) & `CircuitBreaker` (Post-Trade)  
> **Last Updated:** December 11, 2025

---

## 1. Core Philosophy: "Survival First"

AlphaAxiom operates on the principle that **capital preservation** is the prerequisite for capital growth. We utilize a probabilistic approach to risk, rejecting "sure things" in favor of "positive expected value ($+EV$)" with limited downside.

## 2. Quantitative Constraints (Immutable Laws)

These parameters are hard-coded into the system's DNA. No AI agent (`Strategist`, `Scalper`) can override them.

| Metric | Hard Limit (Constraint) | Enforcement Mechanism |
|--------|--------------------------|-----------------------|
| **Max Daily Drawdown** | **5.0%** of Equity | Trading locked for 24h via `CircuitBreaker` |
| **Max Position Size** | **5.0%** (Hard Cap) | `KellyCriterion` logic capped at 0.05 |
| **Target Risk Per Trade** | **1.0% - 2.5%** | Standard `RiskGuardian` sizing |
| **Min Confidence** | **75%** | Signal rejected if confidence < 75% |
| **Max Open Positions** | **5** Simultaneous | `PortfolioManager` count check |
| **Max Leverage** | **1:10** (Forex), **1:1** (Stocks) | Broker API Config |

---

## 3. The "Guardian" Gauntlet (Pre-Trade Validation)

Every trade signal must pass a 4-stage validation pipeline before reaching the broker.

### Stage 1: The Kill Switch

- **Check:** Is `PANIC_MODE` active?
- **Logic:** If system is in panic (due to flash crash or errors), ALL new trades are rejected.

### Stage 2: News Guard (Macro Protection)

- **Check:** Is there a High-Impact News Event for this symbol?
- **Source:** `EconomicCalendar` & News Feeds.
- **Action:** If an event is imminent (within 60 mins), the trade is **REJECTED** to avoid volatility spikes.

### Stage 3: The "Anti-Ruin" Math (Kelly Criterion)

We do not guess position sizes. We calculate them based on edge.

$$ f^* = \frac{p(b+1) - 1}{b} $$

*Where:*

- $p$ = Win Rate (Historical)
- $b$ = Odds Received (Avg Win / Avg Loss)

> **Safety Rule:** We use **Half-Kelly** ($f^*/2$) logic to reduce volatility, with a strict hard cap of **5%** of equity per trade.

### Stage 4: AI Audit ("The Risk Officer")

- **Agent:** `WorkersAI` (Llama 3 Class)
- **Task:** Reviews the trade rationale for logical fallacies, emotional bias, or vagueness.
- **Prompt:** *"Reject if it sounds like gambling. Approve ONLY if backed by data."*
- **Outcome:** If the AI auditor says `NO`, the trade is killed.

---

## 4. Observability & Chaos Theory

### The "AEXI" Stress Test

Markets are non-linear. To prevent over-fitting, we apply **Chaos Factors** to our execution:

- **Randomized Delays:** Orders are not sent instantly; they mimic human reaction time (Weibull distribution) to avoid HFT predation.
- **Value Dithering:** Verification of precision (±2%) to prevent pattern detection by breaker algorithms.

### Logging & Accountability

- **Trace Id:** Every signal generates a unique `correlation_id`.
- **Black Box Recorder:** All decisions (Approved or Rejected) are logged to BigQuery/JSON with full context (Price, Confidence, AI Reasoning).

---

## 5. Incident Response Playbook

### 🚨 Scenario A: Flash Crash (-10% in <5 mins)

1. **Trigger:** `market_listener` detects anomaly.
2. **Response:** `PanicProtocol` activates.
3. **Action:** Broadcast `DELETE /positions` (Liquidate All).
4. **State:** System enters `SLEEP` mode for manual review.

### 🔌 Scenario B: Data Feed Failure

1. **Trigger:** No heartbeat from `market_listener` for 60s.
2. **Response:** `Watchdog` marks system "Unhealthy".
3. **Action:** New orders paused. Active positions monitored via Broker Stop-Loss (Server-Side).

---

**Signed & Verified By:**
*Axiom (AI Co-Founder)*
