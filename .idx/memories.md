# 🧠 ذاكرة مشروع AXIOM

> *سجل حي للقرارات الرئيسية، المهارات المكتسبة، والسياق للمستقبل.*

## 📅 سجل الجلسات

### الجلسة: 8 ديسمبر 2025 (مُحدّث 09:55)

**الإنجازات:**

- ✅ Phase 24 (Auth): Clerk integration complete.
- ✅ Phase 25 (Data Layer): `/api/dashboard` + `useMarketStream` hook.
- ✅ Phase 29: MCP/API Research complete.
- ✅ Phase 30: **100% Weekly ROI Implementation:**
  - Fast RSI (7-period) + EMA 9/21 Crossover
  - MultiTimeframeScalper class (1M/5M/15M alignment)
  - HighLeverageRiskManager (100x support)
  - Bybit Perpetuals Connector (NEW)
  - OANDA Scalping Enhancement
  - 9 new tests passing
- ✅ Skill System: Level 4 achieved (Expert)
- ✅ Git pushed: c48d566

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

### 2. D1 + R2 Strategy

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
- **المؤسس المشارك:** Gemini Quantum Super Skills (AI Partner)

---

## 📝 ملاحظات مستقبلية

- Backup `.wrangler/` before major updates.
- Check `wrangler.toml` compatibility on CF Python updates.
- Consider Alpha Vantage for technical indicators (25 free calls/day).
- Explore CoinAPI MCP for crypto venue auto-discovery.
