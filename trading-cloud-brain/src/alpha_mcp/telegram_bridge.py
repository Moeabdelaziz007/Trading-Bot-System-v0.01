"""
🔗 TelegramMCPBridge v1.0-beta
Connects Telegram Bot with AlphaMCP Tools and Causal Inference Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part of AlphaAxiom Learning Loop v2.0 Integration

Flow: Telegram → Intent Detection → MCP Tools → Causal Analysis → Response
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum


class UserIntent(Enum):
    """أنواع نوايا المستخدم المدعومة."""
    ANALYZE_MARKET = "analyze_market"
    POSITION_SIZE = "position_size"
    RISK_ASSESSMENT = "risk_assessment"
    RSI_ANALYSIS = "rsi_analysis"
    KELLY_CRITERION = "kelly_criterion"
    MULTI_TIMEFRAME = "multi_timeframe"
    BACKTEST = "backtest"
    SYSTEM_INFO = "system_info"
    MARKET_CALENDAR = "market_calendar"
    GENERAL_QUESTION = "general_question"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """نتيجة تحليل النية."""
    intent: UserIntent
    confidence: float
    extracted_params: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@dataclass
class ToolResponse:
    """استجابة الأداة."""
    tool_name: str
    success: bool
    result: Dict[str, Any]
    execution_time_ms: float
    causal_context: Optional[Dict] = None


class IntentDetector:
    """
    كاشف النوايا - يحول رسائل Telegram إلى نوايا قابلة للتنفيذ.
    يستخدم تطابق الأنماط المتقدم مع دعم اللغة العربية والإنجليزية.
    """
    
    # Patterns for intent detection (Arabic + English)
    INTENT_PATTERNS = {
        UserIntent.ANALYZE_MARKET: [
            r"(?:analyze|حلل|تحليل)\s*(?:market|السوق)?",
            r"(?:market|سوق)\s*(?:analysis|تحليل)",
            r"(?:what|ما|كيف).*(?:market|السوق|الأسواق)",
            r"(?:sentiment|مشاعر|اتجاه)\s*(?:market|السوق)?",
        ],
        UserIntent.POSITION_SIZE: [
            r"(?:position|حجم|مركز)\s*(?:size|sizing|الحجم)?",
            r"(?:how much|كم|ماذا).*(?:trade|أتداول|تداول)",
            r"(?:lot|لوت)\s*(?:size|حجم)?",
            r"(?:risk|مخاطرة).*(?:per|لكل)\s*(?:trade|صفقة)",
        ],
        UserIntent.RISK_ASSESSMENT: [
            r"(?:risk|مخاطر|مخاطرة)\s*(?:assessment|تقييم)?",
            r"(?:portfolio|محفظة)\s*(?:risk|مخاطر)?",
            r"(?:evaluate|قيم).*(?:risk|مخاطر)",
            r"(?:hedge|تحوط)",
        ],
        UserIntent.RSI_ANALYSIS: [
            r"\brsi\b",
            r"(?:rsi|مؤشر القوة)\s*(?:analysis|تحليل)?",
            r"(?:overbought|ذروة شراء)",
            r"(?:oversold|ذروة بيع)",
            r"(?:divergence|تباعد)",
        ],
        UserIntent.KELLY_CRITERION: [
            r"\bkelly\b",
            r"(?:kelly|كيلي)\s*(?:criterion|معيار)?",
            r"(?:optimal|أمثل)\s*(?:position|bet|حجم)",
            r"(?:money|إدارة)\s*(?:management|رأس المال)",
        ],
        UserIntent.MULTI_TIMEFRAME: [
            r"(?:multi|متعدد).*(?:timeframe|إطار)",
            r"(?:mtf|htf|ltf)",
            r"(?:timeframe|إطار زمني)\s*(?:analysis|تحليل)?",
            r"(?:4h|1h|15m|1d|daily|weekly).*(?:analysis|تحليل)?",
        ],
        UserIntent.BACKTEST: [
            r"(?:backtest|باكتست|اختبار)",
            r"(?:historical|تاريخي)\s*(?:test|اختبار)",
            r"(?:simulate|محاكاة)\s*(?:strategy|استراتيجية)?",
        ],
        UserIntent.SYSTEM_INFO: [
            r"(?:status|حالة)\s*(?:system|النظام)?",
            r"(?:server|سيرفر)\s*(?:info|معلومات)?",
            r"(?:version|إصدار)",
            r"(?:about|حول)\s*(?:you|الأداة)?",
        ],
        UserIntent.MARKET_CALENDAR: [
            r"(?:calendar|تقويم|جدول)",
            r"(?:events|أحداث)\s*(?:today|اليوم)?",
            r"(?:economic|اقتصادي)\s*(?:news|أخبار)?",
            r"(?:what|ما).*(?:today|اليوم).*(?:market|سوق)?",
        ],
    }
    
    # Symbol extraction patterns
    SYMBOL_PATTERNS = [
        r"\b(EUR/?USD|GBP/?USD|USD/?JPY|AUD/?USD|USD/?CAD|USD/?CHF|NZD/?USD)\b",
        r"\b(XAU/?USD|GOLD|ذهب)\b",
        r"\b(BTC/?USD|ETH/?USD|BITCOIN|ETHEREUM)\b",
        r"\b(US30|US500|NAS100|DAX|SPX)\b",
    ]
    
    def detect(self, message: str) -> IntentResult:
        """
        اكتشاف نية المستخدم من الرسالة.
        """
        message_lower = message.lower().strip()
        
        best_intent = UserIntent.UNKNOWN
        best_confidence = 0.0
        extracted_params = {}
        
        # Check each intent pattern
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, message_lower, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    match_ratio = len(match.group()) / len(message_lower)
                    confidence = min(0.9, 0.5 + match_ratio)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_intent = intent
        
        # Extract trading symbol if present
        for pattern in self.SYMBOL_PATTERNS:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                symbol = match.group().upper().replace("/", "")
                extracted_params["symbol"] = symbol
                best_confidence += 0.1  # Boost confidence with symbol
                break
        
        # Extract numbers (could be prices, percentages, etc.)
        numbers = re.findall(r"\b(\d+(?:\.\d+)?)\b", message)
        if numbers:
            extracted_params["numbers"] = [float(n) for n in numbers[:5]]
        
        # If no specific intent found but has symbol, default to market analysis
        if best_intent == UserIntent.UNKNOWN and "symbol" in extracted_params:
            best_intent = UserIntent.ANALYZE_MARKET
            best_confidence = 0.6
        
        return IntentResult(
            intent=best_intent,
            confidence=min(1.0, best_confidence),
            extracted_params=extracted_params,
            raw_text=message
        )


class TelegramMCPBridge:
    """
    الجسر الرئيسي بين Telegram وأدوات MCP.
    يدير دورة الحياة الكاملة: استلام → تحليل → تنفيذ → ردود.
    """
    
    def __init__(
        self,
        env: Any,
        causal_engine: Optional[Any] = None,
        learning_connector: Optional[Any] = None
    ):
        """
        تهيئة الجسر.
        
        Args:
            env: بيئة Cloudflare Worker
            causal_engine: محرك الاستدلال السببي
            learning_connector: موصل حلقة التعلم
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.db = getattr(env, 'DB', None)
        self.causal_engine = causal_engine
        self.learning_connector = learning_connector
        self.intent_detector = IntentDetector()
        
        # Import tools lazily
        self._tools_module = None
        
    def _get_tools(self):
        """Lazy load MCP tools."""
        if self._tools_module is None:
            from . import moe_axiom_tools
            self._tools_module = moe_axiom_tools
        return self._tools_module
    
    async def process_message(
        self,
        message: str,
        chat_id: int,
        user_name: str = "Trader"
    ) -> ToolResponse:
        """
        معالجة رسالة Telegram وتوجيهها للأداة المناسبة.
        
        Args:
            message: نص الرسالة
            chat_id: معرف المحادثة
            user_name: اسم المستخدم
            
        Returns:
            ToolResponse: استجابة الأداة
        """
        start_time = datetime.now()
        
        # Step 1: Detect intent
        intent_result = self.intent_detector.detect(message)
        
        # Step 2: Route to appropriate tool
        tool_result = await self._route_to_tool(intent_result)
        
        # Step 3: Log for causal analysis
        if self.learning_connector:
            await self.learning_connector.capture_interaction(
                intent=intent_result,
                tool_response=tool_result,
                chat_id=chat_id
            )
        
        # Step 4: Build causal context if available
        causal_context = None
        if self.causal_engine and tool_result.get("success"):
            causal_context = await self._build_causal_context(
                intent_result,
                tool_result
            )
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return ToolResponse(
            tool_name=intent_result.intent.value,
            success=tool_result.get("success", False),
            result=tool_result,
            execution_time_ms=execution_time,
            causal_context=causal_context
        )
    
    async def _route_to_tool(self, intent: IntentResult) -> Dict[str, Any]:
        """
        توجيه النية للأداة المناسبة.
        """
        tools = self._get_tools()
        params = intent.extracted_params
        
        try:
            if intent.intent == UserIntent.ANALYZE_MARKET:
                return await self._call_market_analysis(tools, params)
                
            elif intent.intent == UserIntent.POSITION_SIZE:
                return await self._call_position_sizing(tools, params)
                
            elif intent.intent == UserIntent.RISK_ASSESSMENT:
                return await self._call_risk_assessment(tools, params)
                
            elif intent.intent == UserIntent.RSI_ANALYSIS:
                return await self._call_rsi_analysis(tools, params)
                
            elif intent.intent == UserIntent.KELLY_CRITERION:
                return await self._call_kelly_criterion(tools, params)
                
            elif intent.intent == UserIntent.MULTI_TIMEFRAME:
                return await self._call_multi_timeframe(tools, params)
                
            elif intent.intent == UserIntent.BACKTEST:
                return await self._call_backtest(tools, params)
                
            elif intent.intent == UserIntent.SYSTEM_INFO:
                return tools.get_server_info()
                
            elif intent.intent == UserIntent.MARKET_CALENDAR:
                return tools.market_calendar_today()
                
            else:
                return {
                    "success": False,
                    "error": "لم أفهم طلبك. جرب: تحليل EURUSD أو حجم المركز",
                    "suggestions": [
                        "analyze EURUSD",
                        "position size",
                        "RSI analysis",
                        "market calendar"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"خطأ في التنفيذ: {str(e)}"
            }
    
    async def _call_market_analysis(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ تحليل السوق."""
        symbol = params.get("symbol", "EURUSD")
        
        result = tools.alphaaxiom_market_analysis(
            symbol=symbol,
            include_sentiment=True,
            timeframe="15M"
        )
        
        return {"success": True, **result}
    
    async def _call_position_sizing(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ حساب حجم المركز."""
        numbers = params.get("numbers", [])
        
        account_balance = numbers[0] if len(numbers) > 0 else 10000
        risk_per_trade = numbers[1] if len(numbers) > 1 else 1.0
        stop_loss_pips = numbers[2] if len(numbers) > 2 else 30
        
        result = tools.intelligent_position_sizing(
            account_balance=account_balance,
            risk_per_trade_percent=risk_per_trade,
            stop_loss_pips=stop_loss_pips,
            pip_value=10.0
        )
        
        return {"success": True, **result}
    
    async def _call_risk_assessment(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ تقييم المخاطر."""
        # Build sample positions from context or defaults
        positions = [
            {
                "symbol": params.get("symbol", "EURUSD"),
                "size": 0.1,
                "pnl": 50,
                "entry_price": 1.0850,
                "current_price": 1.0900
            }
        ]
        
        result = tools.portfolio_risk_assessment(
            positions=positions,
            account_balance=10000.0,
            daily_var_limit=2.0
        )
        
        return {"success": True, **result}
    
    async def _call_rsi_analysis(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ تحليل RSI."""
        # Generate sample prices or use provided
        prices = params.get("prices", [
            1.0850, 1.0855, 1.0848, 1.0860, 1.0865,
            1.0858, 1.0870, 1.0875, 1.0868, 1.0880,
            1.0885, 1.0878, 1.0890, 1.0895, 1.0888,
            1.0900
        ])
        
        result = tools.advanced_rsi_analysis(
            prices=prices,
            period=14
        )
        
        return {"success": True, **result}
    
    async def _call_kelly_criterion(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ معيار كيلي."""
        numbers = params.get("numbers", [])
        
        win_rate = numbers[0] / 100 if len(numbers) > 0 else 0.55
        avg_win = numbers[1] if len(numbers) > 1 else 50
        avg_loss = numbers[2] if len(numbers) > 2 else 30
        
        result = tools.calculate_kelly_criterion(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss
        )
        
        return {"success": True, **result}
    
    async def _call_multi_timeframe(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ تحليل متعدد الأطر الزمنية."""
        symbol = params.get("symbol", "EURUSD")
        
        # Build sample timeframe data
        timeframe_data = {
            "1H": {"trend": "bullish", "strength": 0.65},
            "4H": {"trend": "bullish", "strength": 0.70},
            "1D": {"trend": "neutral", "strength": 0.50}
        }
        
        result = tools.multi_timeframe_analysis(
            symbol=symbol,
            timeframe_data=timeframe_data
        )
        
        return {"success": True, **result}
    
    async def _call_backtest(
        self,
        tools,
        params: Dict
    ) -> Dict[str, Any]:
        """تنفيذ محاكاة الاستراتيجية."""
        result = tools.strategy_backtest_simulation(
            strategy_name="RSI_Reversal",
            historical_trades=50,
            initial_capital=10000.0
        )
        
        return {"success": True, **result}
    
    async def _build_causal_context(
        self,
        intent: IntentResult,
        tool_result: Dict
    ) -> Dict[str, Any]:
        """
        بناء السياق السببي لتحليل العلاقات.
        """
        return {
            "intent_type": intent.intent.value,
            "intent_confidence": intent.confidence,
            "tool_success": tool_result.get("success", False),
            "symbol": intent.extracted_params.get("symbol"),
            "timestamp": datetime.now().isoformat(),
            "for_causal_tracking": True
        }
    
    def format_response_for_telegram(
        self,
        response: ToolResponse,
        user_name: str = "Trader"
    ) -> str:
        """
        تنسيق الاستجابة لـ Telegram.
        """
        if not response.success:
            error = response.result.get("error", "خطأ غير معروف")
            suggestions = response.result.get("suggestions", [])
            
            msg = f"❌ <b>خطأ</b>\n\n{error}"
            if suggestions:
                msg += "\n\n<b>جرب:</b>\n"
                msg += "\n".join(f"• {s}" for s in suggestions)
            return msg
        
        result = response.result
        tool = response.tool_name
        
        # Format based on tool type
        if tool == "analyze_market":
            return self._format_market_analysis(result)
        elif tool == "position_size":
            return self._format_position_size(result)
        elif tool == "risk_assessment":
            return self._format_risk_assessment(result)
        elif tool == "rsi_analysis":
            return self._format_rsi_analysis(result)
        elif tool == "kelly_criterion":
            return self._format_kelly(result)
        elif tool == "system_info":
            return self._format_system_info(result)
        elif tool == "market_calendar":
            return self._format_calendar(result)
        else:
            return f"📊 <b>النتيجة:</b>\n\n<pre>{json.dumps(result, indent=2, ensure_ascii=False)[:1000]}</pre>"
    
    def _format_market_analysis(self, result: Dict) -> str:
        """تنسيق تحليل السوق."""
        signal = result.get("signal", {})
        conditions = result.get("market_conditions", {})
        
        return f"""📊 <b>تحليل السوق</b>
━━━━━━━━━━━━━━━━━━━

🎯 <b>الرمز:</b> {signal.get('symbol', 'N/A')}
📈 <b>الإجراء:</b> {signal.get('action', 'HOLD')}
💪 <b>الثقة:</b> {signal.get('confidence', 0)*100:.1f}%

📉 <b>حالة السوق:</b>
• التقلب: {conditions.get('volatility', 'N/A')}
• الاتجاه: {conditions.get('trend', 'N/A')}
• المشاعر: {conditions.get('sentiment', 'N/A')}

🎯 <b>المستويات:</b>
• دخول: {signal.get('entry_price', 'N/A')}
• وقف: {signal.get('stop_loss', 'N/A')}
• هدف: {signal.get('take_profit', 'N/A')}

💡 <b>التحليل:</b>
{signal.get('reasoning', 'لا يوجد')[:200]}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_position_size(self, result: Dict) -> str:
        """تنسيق حجم المركز."""
        return f"""💰 <b>حجم المركز الأمثل</b>
━━━━━━━━━━━━━━━━━━━

📊 <b>الحساب:</b> ${result.get('account_balance', 0):,.2f}
⚠️ <b>المخاطرة:</b> {result.get('risk_percent', 0):.2f}%

🎯 <b>النتيجة:</b>
• حجم المركز: {result.get('position_size_usd', 'N/A')}
• اللوت: {result.get('recommended_lots', 'N/A')}
• المخاطرة بالدولار: ${result.get('risk_amount', 0):.2f}

💡 <b>التوصية:</b>
{result.get('recommendation', 'لا يوجد')}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_risk_assessment(self, result: Dict) -> str:
        """تنسيق تقييم المخاطر."""
        return f"""⚠️ <b>تقييم المخاطر</b>
━━━━━━━━━━━━━━━━━━━

📊 <b>مستوى المخاطرة:</b> {result.get('overall_risk_level', 'N/A')}
📈 <b>VaR اليومي:</b> {result.get('daily_var', 'N/A')}
💰 <b>استخدام رأس المال:</b> {result.get('capital_utilization', 'N/A')}

{result.get('risk_status', '')}

💡 <b>التوصيات:</b>
{chr(10).join('• ' + r for r in result.get('recommendations', [])[:3])}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_rsi_analysis(self, result: Dict) -> str:
        """تنسيق تحليل RSI."""
        return f"""📊 <b>تحليل RSI</b>
━━━━━━━━━━━━━━━━━━━

📈 <b>RSI الحالي:</b> {result.get('current_rsi', 0):.2f}
🎯 <b>المنطقة:</b> {result.get('zone', 'N/A')}
💪 <b>قوة الإشارة:</b> {result.get('signal_strength', 'N/A')}

📉 <b>التباعد:</b> {result.get('divergence', 'لا يوجد')}
📊 <b>الاتجاه:</b> {result.get('trend', 'N/A')}

💡 <b>التوصية:</b>
{result.get('recommendation', 'لا يوجد')}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_kelly(self, result: Dict) -> str:
        """تنسيق معيار كيلي."""
        return f"""🧮 <b>معيار كيلي</b>
━━━━━━━━━━━━━━━━━━━

📊 <b>كيلي الخام:</b> {result.get('raw_kelly', 0):.4f}
🎯 <b>كيلي المعدل:</b> {result.get('adjusted_kelly', 0):.4f}

💰 <b>الحجم الموصى:</b>
• نسبة: {result.get('recommended_position_size', 'N/A')}
• دولار: {result.get('position_size_usd', 'N/A')}
• لوت: {result.get('optimal_lots', 'N/A')}

⚠️ <b>المخاطرة:</b> {result.get('risk_level', 'N/A')}
📈 <b>القيمة المتوقعة:</b> ${result.get('expected_value', 0):.2f}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_system_info(self, result: Dict) -> str:
        """تنسيق معلومات النظام."""
        return f"""ℹ️ <b>معلومات النظام</b>
━━━━━━━━━━━━━━━━━━━

🚀 <b>الإصدار:</b> {result.get('version', 'N/A')}
📊 <b>الأدوات:</b> {result.get('tools_count', 0)}
⏰ <b>الوقت:</b> {result.get('server_time', 'N/A')}

💡 <b>الأدوات المتاحة:</b>
{chr(10).join('• ' + t for t in result.get('available_tools', [])[:5])}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
    
    def _format_calendar(self, result: Dict) -> str:
        """تنسيق التقويم."""
        events = result.get("events", [])
        events_text = "\n".join(
            f"• {e.get('time', '')}: {e.get('event', '')} ({e.get('impact', '')})"
            for e in events[:5]
        ) if events else "لا توجد أحداث مهمة اليوم"
        
        return f"""📅 <b>تقويم السوق</b>
━━━━━━━━━━━━━━━━━━━

📊 <b>التاريخ:</b> {result.get('date', 'N/A')}
🕐 <b>حالة السوق:</b> {result.get('market_status', 'N/A')}

📋 <b>الأحداث المهمة:</b>
{events_text}

━━━━━━━━━━━━━━━━━━━
🧠 <i>AlphaMCP v1.0-beta</i>"""
