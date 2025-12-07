# 🤖 Axiom Antigravity - Telegram Bot Full Setup Guide

## 📱 Bot Identity

### Avatar

![Trading Assistant Avatar](/docs/assets/trading_bot_avatar.png)

**Bot Name:** Axiom Trading Assistant  
**Username:** @AxiomTradingBot (example)  
**Persona:** Professional Arab financial advisor, friendly and expert

---

## 🔧 Step 1: BotFather Setup

### Create the Bot

```
1. Open Telegram, search @BotFather
2. Send /newbot
3. Enter bot name: "Axiom Trading Assistant"
4. Enter username: axiom_trading_bot (must end with 'bot')
5. Save the API TOKEN (keep secret!)
```

### Configure Bot Settings

```
/setdescription
→ 🦅 Axiom Antigravity - Your AI Trading Assistant
   تحليلات ذكية، إشارات تداول، وتنفيذ آلي
   Powered by DeepSeek + Workers AI

/setabouttext
→ AI Trading Hub | Forex & Stocks
   Zero-Cost Infrastructure
   Built with ❤️ by Axiom

/setuserpic
→ Upload the generated avatar image

/setcommands
→ start - ابدأ المحادثة
   status - حالة النظام
   balance - رصيد المحفظة
   positions - المراكز المفتوحة
   analyze - تحليل DeepSeek
   ai - سؤال سريع (مجاني)
   stoptrade - إيقاف التداول
   starttrade - تشغيل التداول
```

---

## 🌐 Step 2: Webhook Setup (Custom Domain)

### Option A: Cloudflare Workers Domain (Current)

```bash
# Your webhook URL
https://trading-brain-v1.amrikyy.workers.dev/telegram/webhook

# Set webhook via API
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://trading-brain-v1.amrikyy.workers.dev/telegram/webhook"}'
```

### Option B: Custom Domain (e.g., api.axiom.app)

```bash
# 1. Add DNS record in Cloudflare Dashboard:
#    Type: CNAME
#    Name: api
#    Target: trading-brain-v1.amrikyy.workers.dev

# 2. Add route in wrangler.toml:
# routes = [{ pattern = "api.axiom.app/*", zone_name = "axiom.app" }]

# 3. Set webhook with custom domain
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d '{"url": "https://api.axiom.app/telegram/webhook"}'
```

---

## 📲 Step 3: Telegram Mini App Setup

### Create Mini App via BotFather

```
1. /newapp
2. Select your bot
3. Enter app title: "Axiom Dashboard"
4. Enter app description: "AI Trading Dashboard"
5. Upload app icon (512x512)
6. Enter Web App URL: https://axiom-trading.vercel.app
```

### Set Menu Button

```
/setmenubutton
→ Select your bot
→ Enter button text: "📊 Dashboard"
→ Enter URL: https://axiom-trading.vercel.app
```

### Integrate Telegram Web App SDK

```html
<!-- Add to frontend/public/index.html -->
<script src="https://telegram.org/js/telegram-web-app.js"></script>

<script>
  // Initialize Telegram Web App
  const tg = window.Telegram.WebApp;
  tg.ready();
  
  // Get user data
  const user = tg.initDataUnsafe.user;
  console.log('User:', user.first_name);
  
  // Theme sync
  document.body.style.backgroundColor = tg.themeParams.bg_color;
  
  // Main button
  tg.MainButton.text = "تنفيذ الصفقة";
  tg.MainButton.show();
  tg.MainButton.onClick(() => {
    // Execute trade
  });
</script>
```

---

## 🔑 Step 4: Secrets Configuration

### Add to Cloudflare Dashboard

```bash
# Via CLI
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put TELEGRAM_CHAT_ID

# Or via Dashboard:
# Workers & Pages → trading-brain-v1 → Settings → Variables → Secrets
```

### Required Secrets

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | From BotFather |
| `TELEGRAM_CHAT_ID` | Your chat/group ID |
| `GROQ_API_KEY` | For AI chat |
| `DEEPSEEK_API_KEY` | For deep analysis |
| `CAPITAL_API_KEY` | Broker access |

---

## 🧪 Step 5: Testing

### Test Webhook

```bash
# Check webhook info
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Send test message
curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{"chat_id": "<CHAT_ID>", "text": "🧪 Test from API"}'
```

### Test Bot Commands

```
/start - Should show welcome message
/status - Should show system status
/ai ما هو EURUSD؟ - Should respond with AI
/analyze sentiment الذهب يرتفع - Deep analysis
```

---

## 📊 Available Commands

| Command | Description | AI Used |
|---------|-------------|---------|
| `/start` | Welcome message | - |
| `/status` | System status | - |
| `/balance` | Portfolio value | - |
| `/positions` | Open trades | - |
| `/stoptrade` | Kill switch ON | - |
| `/starttrade` | Resume trading | - |
| `/ai [text]` | Quick AI chat | Workers AI (FREE) |
| `/analyze [type] [text]` | Deep analysis | DeepSeek |

---

## 🚀 Production Checklist

- [ ] Bot created in BotFather
- [ ] Avatar uploaded
- [ ] Commands configured
- [ ] Webhook set to Worker URL
- [ ] All secrets added
- [ ] Mini App linked (optional)
- [ ] Test all commands working

---

*Last Updated: Dec 7, 2025*
