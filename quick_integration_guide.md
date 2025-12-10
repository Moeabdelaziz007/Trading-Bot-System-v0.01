# 🚀 AlphaAxiom + MT5 - دليل التكامل السريع

## يا محمد! هذا كل ما تحتاجه للبدء خلال 30 دقيقة ⏱️

---

## 📁 **خطوة 1: إضافة الملفات (5 دقائق)**

```bash
cd /path/to/AlphaAxiom/trading-cloud-brain

# 1. إنشاء ملف الوسيط
mkdir -p src/brokers
touch src/brokers/mt5_broker.py
# انسخ محتوى MT5Broker من Artifact السابق

# 2. إنشاء أدوات MCP
mkdir -p src/mcp
touch src/mcp/tools_mt5.py
# انسخ محتوى MT5MCPTools من Artifact السابق

# 3. تحديث __init__.py
echo "from .mt5_broker import MT5Broker" >> src/brokers/__init__.py
echo "from .tools_mt5 import MT5MCPTools" >> src/mcp/__init__.py
```

---

## ⚙️ **خطوة 2: تحديث worker.py (5 دقائق)**

افتح `src/worker.py` وأضف هذا الكود:

```python
# في أعلى الملف مع الـ imports الأخرى
from .brokers.mt5_broker import MT5Broker
from .mcp.tools_mt5 import MT5MCPTools

# داخل worker class (مثال مبسط)
async def on_fetch(self, request, env):
    # ... الكود الموجود ...
    
    # تهيئة MT5 إذا كانت البيئة موجودة
    if env.get('MT5_BRIDGE_URL'):
        mt5_broker = MT5Broker(
            bridge_url=env.MT5_BRIDGE_URL,
            auth_token=env.MT5_BRIDGE_SECRET,
            broker_name="XM Global"
        )
        mt5_tools = MT5MCPTools(mt5_broker)
        
        # إضافة الأدوات إلى الـ router الموجود
        url = URL(request.url)
        
        # مثال: endpoint جديد للذهب
        if url.pathname == '/api/mt5/gold':
            result = await mt5_tools._get_gold_price()
            return json_response(result)
        
        # مثال: endpoint للتداول الذكي
        if url.pathname == '/api/mt5/trade':
            body = await request.json()
            result = await mt5_tools._execute_smart_trade(**body)
            return json_response(result)
    
    # ... بقية الكود ...
```

---

## 🔐 **خطوة 3: إضافة Secrets (3 دقائق)**

```bash
# إضافة MT5 bridge URL و secret
wrangler secret put MT5_BRIDGE_URL
# أدخل: https://bridge.yourdomain.com (أو http://localhost:8000 للاختبار)

wrangler secret put MT5_BRIDGE_SECRET
# أدخل: your_secret_token_here
```

**أو للتطوير المحلي، أضف إلى `.dev.vars`:**

```env
MT5_BRIDGE_URL=http://localhost:8000
MT5_BRIDGE_SECRET=dev_secret_123
```

---

## 🧪 **خطوة 4: الاختبار المحلي (5 دقائق)**

```bash
# 1. شغّل MT5 bridge على جهازك (إذا كان عندك MT5)
# في terminal منفصل:
cd /path/to/mt5-bridge
python main.py

# 2. شغّل AlphaAxiom Worker
cd /path/to/AlphaAxiom/trading-cloud-brain
wrangler dev

# 3. اختبر API
curl http://localhost:8787/api/mt5/gold
```

**النتيجة المتوقعة:**
```json
{
  "success": true,
  "symbol": "XAUUSD",
  "bid": 2650.25,
  "ask": 2650.45,
  "arabic_message": "سعر الذهب: $2650.25 💰"
}
```

---

## 📱 **خطوة 5: تكامل Telegram (5 دقائق)**

أضف هذه الأوامر إلى بوت Telegram الموجود عندك:

```python
# في telegram bot handlers
from trading_cloud_brain.src.mcp.tools_mt5 import MT5MCPTools

@bot.command('/gold')
async def gold_price(update, context):
    """سعر الذهب الحالي"""
    result = await mt5_tools._get_gold_price()
    await update.message.reply_text(result['arabic_message'])

@bot.command('/mt5trade')
async def mt5_trade(update, context):
    """
    فتح صفقة ذكية
    مثال: /mt5trade XAUUSD BUY
    """
    try:
        symbol = context.args[0]  # XAUUSD
        direction = context.args[1]  # BUY or SELL
        
        result = await mt5_tools._execute_smart_trade(
            symbol=symbol,
            direction=direction,
            risk_percent=2.0,
            reason="Telegram command"
        )
        
        await update.message.reply_text(result['arabic_message'])
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")

@bot.command('/mt5status')
async def mt5_status(update, context):
    """حالة المحفظة"""
    result = await mt5_tools._get_portfolio_status()
    
    msg = f"""
💼 حالة حساب MT5

💰 الرصيد: ${result['account']['balance']:.2f}
📊 الملكية: ${result['account']['equity']:.2f}
📈 الربح: ${result['account']['profit']:.2f}

🔢 الصفقات: {result['positions']['count']}
💵 إجمالي الربح: ${result['positions']['total_profit']:.2f}

{result['arabic_summary']}
    """
    await update.message.reply_text(msg)
```

---

## 🎯 **خطوة 6: تحديث mcp_config.json (2 دقيقة)**

أضف هذا إلى `mcp_config.json`:

```json
{
  "mcpServers": {
    "capital": { "enabled": true },
    "alpaca": { "enabled": true },
    "oanda": { "enabled": true },
    "bybit": { "enabled": true },
    "coinbase": { "enabled": true },
    
    "mt5-forex": {
      "enabled": true,
      "description": "MT5/XM Global - Gold & Forex Trading",
      "broker": "XM Global",
      "markets": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"],
      "tools": [
        "mt5_gold_price",
        "mt5_execute_smart_trade",
        "mt5_portfolio_status",
        "mt5_market_scan",
        "mt5_close_all"
      ],
      "features": {
        "arabic_support": true,
        "auto_risk_management": true,
        "real_time_prices": true
      }
    }
  }
}
```

---

## 🚀 **خطوة 7: النشر (5 دقائق)**

```bash
# 1. تأكد من أن كل شيء يعمل محلياً
wrangler dev

# 2. انشر على Cloudflare
wrangler deploy

# 3. اختبر على Production
curl https://your-worker.workers.dev/api/mt5/gold
```

---

## 🎉 **خطوة 8: الاستخدام الفعلي!**

### من Telegram:
```
/gold
> سعر الذهب: $2650.25 💰

/mt5trade XAUUSD BUY
> ✅ تم فتح صفقة BUY XAUUSD
> الحجم: 0.05 لوت
> المخاطرة: $40.00

/mt5status
> 💼 حالة حساب MT5
> 💰 الرصيد: $2000.00
> 📊 الملكية: $2015.50
> 📈 الربح: $15.50
```

### من API مباشرة:
```bash
# سعر الذهب
curl https://your-worker.workers.dev/api/mt5/gold

# فتح صفقة
curl -X POST https://your-worker.workers.dev/api/mt5/trade \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "direction": "BUY",
    "risk_percent": 2
  }'

# حالة المحفظة
curl https://your-worker.workers.dev/api/mt5/status
```

---

## 🔥 **الميزات التي أضفناها لمشروعك:**

✅ **6 أدوات MCP جديدة** للذهب والفوركس
✅ **تكامل سلس** مع البنية الموجودة (Capital، Alpaca، etc.)
✅ **دعم كامل للعربية** في جميع الرسائل
✅ **إدارة مخاطر ذكية** (2% لكل صفقة)
✅ **تكلفة صفر** (يعمل ضمن Cloudflare Workers المجاني)
✅ **تكامل مع Telegram Bot الموجود**
✅ **متوافق مع الهيكل المعماري** لـ AlphaAxiom

---

## 🎓 **الخطوات التالية (اختياري - بعد النجاح):**

1. **أضف WebSocket للأسعار الحية**
   - تحديثات real-time كل 0.1 ثانية
   - Perfect للسكالبينج!

2. **أضف وسطاء MT5 آخرين**
   - Exness، ICM، FXTM
   - Multi-account support

3. **أضف التحليل الفني المتقدم**
   - RSI، MACD، Bollinger Bands
   - استخدم مؤشراتك الموجودة في `src/indicators/`

4. **أضف Learning Loop**
   - تسجيل كل صفقة
   - التعلم من النتائج
   - تحسين الأوزان تلقائياً

---

## 🆘 **المشاكل الشائعة والحلول:**

### Problem 1: "MT5 bridge not connected"
```bash
# Solution: تأكد من أن MT5 bridge يعمل
curl http://localhost:8000/api/v1/health

# Expected: {"status": "healthy", "mt5_connected": true}
```

### Problem 2: "Trade failed - Invalid volume"
```python
# Solution: تأكد من أن lot size صحيح
# XM Global minimum: 0.01 lots
# Maximum: 100 lots
```

### Problem 3: "Symbol not found"
```python
# Solution: Enable symbol in MT5
# Right-click on Market Watch → Show All
```

---

## 💡 **نصائح احترافية:**

1. **ابدأ بحساب Demo أولاً!**
   - اختبر كل شيء على demo
   - بعد أسبوع ناجح، انتقل لـ live

2. **استخدم risk management دائماً**
   - لا تخاطر بأكثر من 2% لكل صفقة
   - Max 3 صفقات مفتوحة في نفس الوقت

3. **راقب السبريد**
   - تداول فقط عند spread منخفض (<20 pips)
   - أفضل أوقات: London session، NY session

4. **استخدم الـ Telegram Bot**
   - اجعله يرسل لك تنبيهات
   - راقب حسابك من أي مكان

---

## 🎯 **الملخص:**

✅ **ملفين Python فقط** (mt5_broker.py + tools_mt5.py)
✅ **3 أسطر تعديل** في worker.py
✅ **2 secrets** في Cloudflare
✅ **5 دقائق نشر**
✅ **تكلفة: $0**

**والنتيجة:** نظام تداول ذهب/فوركس كامل يعمل مع AlphaAxiom! 🚀

---

## 📞 **هل تحتاج مساعدة؟**

أخبرني:
- ❓ أي خطوة غير واضحة؟
- 🔧 تريد مزيد من التفصيل في أي جزء؟
- 💡 عندك أفكار لميزات إضافية؟
- 🐛 واجهت مشكلة معينة؟

**أنا معك خطوة بخطوة حتى يعمل كل شيء بشكل مثالي!** 💪🔥
