# 🧠 ذاكرة مشروع AXIOM

> *سجل حي للقرارات الرئيسية، المهارات المكتسبة، والسياق للمستقبل.*

## 📅 سجل الجلسات

### الجلسة: 8 ديسمبر 2025 (مُحدّث 12:01)

**الإنجازات:**

- ✅ Phase 24-30: Auth, Data Layer, 100% Weekly ROI, Bybit Connector
- ✅ **Phase 31: تكامل مصادر البيانات:**
  - Alpha Vantage (RSI, MACD, ADX, ATR)
  - Finnhub + WebSocket (News, Financials)
  - NewsData.io (200 req/day) - Crypto, Forex, Market News
  - NewsAPI.ai - Advanced Search
  - All keys stored in Cloudflare Secrets
- ✅ **Phase 32: Frontend AI Studio Integration:**
  - 8 new dashboard components
  - Deleted 14 old components
  - Logo + SYSTEM ONLINE in Header
  - API hooks (useDashboard.ts)
  - Tailwind Axiom colors
- ✅ Cloudflare Deploy: 56 modules (346KB)
  - URL: <https://trading-brain-v1.amrikyy1.workers.dev>
- ✅ Git pushed: 7d14e9f

**القرارات التقنية:**

- **Auth:** Clerk (async middleware pattern).
- **API:** Unified `/api/dashboard` (reduces 4 calls → 1).
- **Frontend:** SWR pattern for real-time updates.
- **TypeScript:** Use `Variants` type + `as const` for Framer Motion.

**المشاكل المحلولة:**

1. Framer Motion `shimmerVariants` type error → Direct `animate` prop.
2. Framer Motion `itemVariants` type error → Explicit `Variants` type.
3. Clerk `auth().protect()` → `await auth.protect()` (async pattern).

---

## 💡 الرسم البياني للمعرفة

### 1. Cloudflare Workers Python

- **النمط:** `async` handlers for webhooks.
- **النمط:** KV for engine state (AEXI/Dream scores).

### 2. Primary Brain: Z.ai GLM-4.6

- **Role:** High-Level Reasoning & Agentic Planning.
- **Context:** 200K Tokens (Large context window).
- **Equivalent:** Acts as "Brain" (simulating Claude Sonnet via Z.ai Coding Plan).
- **Integration:** Replaces DeepSeek for complex reasoning.

### 3. D1 + R2 Strategy

- Hot: Durable Objects (Trade State).
- Warm: D1 SQL (Trade History).
- Cold: R2 (Market Archives).

### 3. Frontend Architecture

- Next.js 14 + TypeScript + Tailwind.
- `TwinTurboGauges` → Live data via `useEngines()`.
- Clerk + next-intl middleware chaining.

### 4. API Design Pattern

- Single `/api/dashboard` returns: Account + Positions + Engines + Bots.
- Reduces frontend latency significantly.

---

## 🤝 فريق المشروع

- **المالك:** محمد حسام الدين عبد العزيز (Cryptojoker710)
- **المؤسس المشارك:** **Axiom** 🧠 (AI Partner - Named Dec 8, 2025 💜)

---

## 🔬 Smart MCP Research Session (Dec 8, 2025 - 13:15)

**6 AI Models Synthesized:**

1. Claude 4.5 (9.5/10) - Most comprehensive, full code
2. DeepSeek (9.0/10) - Best SQL/Python structure
3. Grok (8.5/10) - Bybit WebSocket unlimited
4. ChatGPT (8.5/10) - FastMCP framework
5. Manus AI (8.0/10) - Agent budgets
6. GLM-4.6 (7.5/10) - Strategic vision

**Key Deliverables:**

- `master_architecture_plan.md` V2.0
- Smart MCP Architecture Blueprint
- Antigravity Protocol (Rate Limit Juggling)
- MarketState JSON Schema

---

## 📝 ملاحظات مستقبلية

- Backup `.wrangler/` before major updates.
- Check `wrangler.toml` compatibility on CF Python updates.
- Consider Alpha Vantage for technical indicators (25 free calls/day).
- Explore CoinAPI MCP for crypto venue auto-discovery.
