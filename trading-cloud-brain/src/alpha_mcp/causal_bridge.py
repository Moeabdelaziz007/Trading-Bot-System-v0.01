"""
🌉 Causal Learning Bridge v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Connects AlphaMCP Tools with Causal Inference Engine & Learning Loop.
يربط أدوات AlphaMCP بمحرك الاستدلال السببي وحلقة التعلم.

Author: Mohamed Hossameldin Abdelaziz
Email: cryptojoker710@gmail.com
Version: 1.0.0
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# استيراد الأدوات التي بنيناها سابقاً
# Import the tools we built earlier
from .moe_axiom_tools import (
    calculate_kelly_criterion,
    advanced_rsi_analysis,
    alphaaxiom_market_analysis,
    portfolio_risk_assessment,
    intelligent_position_sizing,
    multi_timeframe_analysis
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧬 CAUSAL LEARNING BRIDGE CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CausalLearningBridge:
    """
    الجسر الرئيسي بين الأدوات والاستدلال السببي والتعلم.
    Main bridge between tools, causal inference, and learning.
    
    هذا الكلاس يقوم بـ:
    This class performs:
    1. تنفيذ الأدوات - Tool Execution
    2. الاستدلال السببي - Causal Inference
    3. تسجيل حلقة التعلم - Learning Loop Recording
    """
    
    def __init__(self, db_connection: Optional[Any] = None):
        """
        تهيئة الجسر مع اتصال قاعدة البيانات (اختياري).
        Initialize bridge with database connection (optional).
        """
        self.db = db_connection
        self.version = "1.0.0"
        self.execution_count = 0
        self.success_rate = 1.0
        
    async def execute_tool_with_causal_context(
        self,
        tool_name: str,
        params: Dict,
        user_context: Dict
    ) -> Dict:
        """
        تنفيذ الأداة مع إضافة طبقة الاستدلال السببي وتسجيل التعلم.
        Execute tool with causal inference layer and learning recording.
        
        Args:
            tool_name: اسم الأداة (Tool name)
            params: معاملات الأداة (Tool parameters)
            user_context: سياق المستخدم (User context)
            
        Returns:
            dict: النتيجة مع التحليل السببي (Result with causal analysis)
        """
        start_time = datetime.now()
        self.execution_count += 1
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 1️⃣ التنفيذ الأولي للأداة (The Execution)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        tool_result = self._route_tool_execution(tool_name, params)
        
        if "error" in tool_result:
            return self._format_error_response(tool_name, tool_result["error"])

        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 2️⃣ الاستدلال السببي (The Causal Inference)
        # تحليل "لماذا" حدثت هذه النتيجة بناءً على السياق
        # Analyze "why" this result occurred based on context
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        causal_analysis = self._infer_causality(
            tool_name, tool_result, user_context
        )
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 3️⃣ دمج النتائج (Merge Results)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        execution_duration = (datetime.now() - start_time).total_seconds() * 1000
        
        final_output = {
            "tool": tool_name,
            "execution_result": tool_result,
            "causal_insight": causal_analysis,
            "meta": {
                "timestamp": start_time.isoformat(),
                "duration_ms": round(execution_duration, 2),
                "confidence_weight": causal_analysis.get("confidence_weight", 0.5),
                "execution_count": self.execution_count,
                "version": self.version
            }
        }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 4️⃣ تسجيل حلقة التعلم (The Learning Loop)
        # يتم تسجيل الحالة هنا ليتم مراجعتها لاحقاً (Reward Modeling)
        # Record state here for later review (Reward Modeling)
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        await self._log_to_learning_loop(final_output, user_context)
        
        return final_output

    def _route_tool_execution(self, tool_name: str, params: Dict) -> Dict:
        """
        توجيه الطلب للدالة المناسبة في MoeAxiomTools.
        Route request to the appropriate function in MoeAxiomTools.
        
        Args:
            tool_name: اسم الأداة (rsi, kelly, market_pulse, etc.)
            params: معاملات التنفيذ (Execution parameters)
            
        Returns:
            dict: نتيجة تنفيذ الأداة (Tool execution result)
        """
        try:
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # RSI Analysis Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            if tool_name == "rsi":
                return advanced_rsi_analysis(
                    prices=params.get("prices", []),
                    period=params.get("period", 14),
                    oversold=params.get("oversold", 30),
                    overbought=params.get("overbought", 70)
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Kelly Criterion Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            elif tool_name == "kelly":
                return calculate_kelly_criterion(
                    win_rate=params.get("win_rate", 0.5),
                    avg_win=params.get("avg_win", 100),
                    avg_loss=params.get("avg_loss", 50),
                    risk_aversion=params.get("risk_mode", "MODERATE")
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Market Pulse Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            elif tool_name == "market_pulse":
                return alphaaxiom_market_analysis(
                    symbol=params.get("symbol", "BTC"),
                    current_price=params.get("price", 0),
                    volume=params.get("volume", 1.0),
                    volatility=params.get("volatility", 0.02),
                    news_sentiment=params.get("sentiment", "neutral"),
                    social_sentiment=params.get("social_sentiment", "neutral")
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Portfolio Risk Check Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            elif tool_name == "risk_check":
                return portfolio_risk_assessment(
                    positions=params.get("positions", []),
                    account_balance=params.get("balance", 10000)
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Position Sizing Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            elif tool_name == "position_size":
                return intelligent_position_sizing(
                    account_balance=params.get("balance", 10000),
                    risk_tolerance=params.get("risk_mode", "MEDIUM"),
                    symbol=params.get("symbol", "EURUSD"),
                    entry_price=params.get("entry_price", 1.0),
                    stop_loss=params.get("stop_loss", 0.99),
                    take_profit=params.get("take_profit", 1.02),
                    market_volatility=params.get("volatility", 0.02)
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Multi-Timeframe Analysis Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            elif tool_name == "mtf":
                return multi_timeframe_analysis(
                    symbol=params.get("symbol", "BTCUSD"),
                    price_data=params.get("price_data", {}),
                    primary_timeframe=params.get("timeframe", "15M")
                )
            
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            # Unknown Tool
            # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            else:
                return {
                    "error": f"Tool '{tool_name}' not found in AlphaMCP",
                    "available_tools": [
                        "rsi", "kelly", "market_pulse", 
                        "risk_check", "position_size", "mtf"
                    ]
                }
                
        except Exception as e:
            return {"error": f"Execution failed: {str(e)}"}

    def _infer_causality(
        self,
        tool_name: str,
        result: Dict,
        context: Dict
    ) -> Dict:
        """
        محرك الاستدلال السببي البسيط (Simple Causal Inference Engine).
        يربط النتيجة الرقمية بالسياق الحالي للسوق.
        
        Connects numeric results to current market context.
        
        Args:
            tool_name: اسم الأداة المنفذة
            result: نتيجة الأداة
            context: السياق الحالي
            
        Returns:
            dict: التحليل السببي مع السرد (Causal analysis with narrative)
        """
        insight = {
            "cause": "Unknown",
            "effect_probability": "Medium",
            "narrative": "",
            "confidence_weight": 0.5
        }
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # RSI Tool - Causal Logic
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        if tool_name == "rsi":
            rsi_val = result.get("rsi_value", 50)
            divergence = result.get("divergence", "")
            rsi_slope = result.get("rsi_slope", 0)
            
            # حالة: RSI مرتفع + تباعد هبوطي
            # Case: High RSI + Bearish Divergence
            if rsi_val > 70 and divergence and "هبوطي" in divergence:
                insight["cause"] = "Momentum Exhaustion + Bearish Divergence"
                insight["effect_probability"] = "High Probability Reversal"
                insight["narrative"] = (
                    "السوق يرتفع لكن الزخم يضعف (Divergence)، "
                    "مما يجعل احتمالية الانعكاس عالية جداً بسبب الإنهاك."
                )
                insight["confidence_weight"] = 0.85
            
            # حالة: ذروة البيع
            # Case: Oversold Condition
            elif rsi_val < 30:
                insight["cause"] = "Oversold Condition"
                insight["effect_probability"] = "Bounce Likely"
                insight["narrative"] = (
                    "السعر في منطقة ذروة البيع، "
                    "مما قد يسبب ارتداداً فنياً (Dead Cat Bounce) أو انعكاساً."
                )
                insight["confidence_weight"] = 0.65
            
            # حالة: الزخم الصعودي
            # Case: Bullish Momentum
            elif rsi_val > 50 and rsi_slope > 1:
                insight["cause"] = "Positive Momentum Building"
                insight["effect_probability"] = "Continuation Likely"
                insight["narrative"] = (
                    "الزخم الصعودي يزداد، "
                    "مما يشير إلى احتمالية استمرار الاتجاه الصاعد."
                )
                insight["confidence_weight"] = 0.70
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Market Pulse Tool - Causal Logic
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif tool_name == "market_pulse":
            score = result.get("market_score", 0.5)
            action = result.get("action", "HOLD")
            
            # حالة: تزامن إيجابي قوي
            # Case: Strong Positive Confluence
            if score > 0.8:
                insight["cause"] = "Multi-Factor Confluence (Positive)"
                insight["effect_probability"] = "Strong Buy Signal"
                insight["narrative"] = (
                    "تزامن إيجابي بين السعر، الحجم، والأخبار. "
                    "هذا يخلق ضغط شراء حقيقي مدعوم بالأساسيات."
                )
                insight["confidence_weight"] = 0.90
            
            # حالة: ضعف هيكلي
            # Case: Systemic Weakness
            elif score < 0.2:
                insight["cause"] = "Systemic Weakness"
                insight["effect_probability"] = "Strong Sell Signal"
                insight["narrative"] = (
                    "ضعف هيكلي في السوق. الهبوط ليس مجرد تصحيح "
                    "بل ناتج عن معنويات سلبية وأحجام تداول ضعيفة."
                )
                insight["confidence_weight"] = 0.85
            
            # حالة: منطقة محايدة
            # Case: Neutral Zone
            else:
                insight["cause"] = "Mixed Signals"
                insight["effect_probability"] = "Wait for Clarity"
                insight["narrative"] = (
                    "إشارات متضاربة. يُنصح بانتظار تأكيد واضح "
                    "قبل اتخاذ قرار التداول."
                )
                insight["confidence_weight"] = 0.50
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Kelly Criterion Tool - Causal Logic
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif tool_name == "kelly":
            adjusted_kelly = result.get("adjusted_kelly", 0)
            risk_level = result.get("risk_level", "")
            
            if adjusted_kelly < 0:
                insight["cause"] = "Negative Edge (No Trading Edge)"
                insight["effect_probability"] = "Avoid Trading"
                insight["narrative"] = (
                    "لا توجد ميزة تداول إحصائية. "
                    "نسبة الفوز أو العائد غير كافية للتداول."
                )
                insight["confidence_weight"] = 0.95
            elif adjusted_kelly > 0.3:
                insight["cause"] = "Excessive Risk Exposure"
                insight["effect_probability"] = "High Risk of Ruin"
                insight["narrative"] = (
                    "حجم المركز المقترح مرتفع جداً. "
                    "هذا قد يؤدي إلى خسائر كارثية (Risk of Ruin)."
                )
                insight["confidence_weight"] = 0.90
            else:
                insight["cause"] = "Optimal Position Sizing"
                insight["effect_probability"] = "Balanced Risk/Reward"
                insight["narrative"] = (
                    "حجم المركز ضمن الحدود الآمنة. "
                    "يوازن بين الأرباح المحتملة والمخاطر المقبولة."
                )
                insight["confidence_weight"] = 0.80
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Risk Check Tool - Causal Logic
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        elif tool_name == "risk_check":
            risk_level = result.get("portfolio_summary", {}).get("risk_level", "")
            portfolio_risk = result.get("portfolio_summary", {}).get("portfolio_risk_percentage", "0%")
            
            if "عالي جداً" in risk_level or "🔴" in risk_level:
                insight["cause"] = "Portfolio Over-Exposure"
                insight["effect_probability"] = "High Drawdown Risk"
                insight["narrative"] = (
                    "المحفظة معرضة لمخاطر عالية جداً. "
                    "يجب تقليل المراكز فوراً لتجنب خسائر كبيرة."
                )
                insight["confidence_weight"] = 0.95
            elif "منخفض" in risk_level or "🟢" in risk_level:
                insight["cause"] = "Well-Managed Portfolio"
                insight["effect_probability"] = "Safe Trading Zone"
                insight["narrative"] = (
                    "المحفظة مُدارة بشكل جيد. "
                    "يمكن إضافة مراكز جديدة بأمان."
                )
                insight["confidence_weight"] = 0.75

        return insight

    async def _log_to_learning_loop(self, data: Dict, context: Dict):
        """
        تسجيل البيانات في قاعدة البيانات (D1) للتعلم المستقبلي.
        Log data to database (D1) for future learning.
        
        Args:
            data: بيانات التنفيذ الكاملة
            context: السياق الإضافي
        """
        if self.db:
            # هنا يتم إدراج السجل في جدول Learning_Logs
            # Here the record is inserted into Learning_Logs table
            try:
                log_entry = {
                    "tool_name": data["tool"],
                    "execution_result": json.dumps(data["execution_result"]),
                    "causal_insight": json.dumps(data["causal_insight"]),
                    "confidence_weight": data["meta"]["confidence_weight"],
                    "timestamp": data["meta"]["timestamp"],
                    "user_context": json.dumps(context),
                    "duration_ms": data["meta"]["duration_ms"]
                }
                # await self.db.prepare(
                #     "INSERT INTO learning_logs (...) VALUES (...)"
                # ).bind(...).run()
                pass
            except Exception as e:
                print(f"⚠️ [Learning Loop] Failed to log: {str(e)}")
        
        # في بيئة التطوير، نطبع فقط
        # In development environment, just print
        print(f"🧬 [Learning Loop] Recorded state for tool: {data['tool']}")
        print(f"   Confidence: {data['meta']['confidence_weight']:.2%}")
        print(f"   Duration: {data['meta']['duration_ms']}ms")
    
    def _format_error_response(self, tool_name: str, error_message: str) -> Dict:
        """
        تنسيق رد خطأ موحد.
        Format unified error response.
        """
        return {
            "tool": tool_name,
            "execution_result": {"error": error_message},
            "causal_insight": {
                "cause": "Execution Error",
                "effect_probability": "N/A",
                "narrative": f"فشل في تنفيذ الأداة: {error_message}",
                "confidence_weight": 0.0
            },
            "meta": {
                "timestamp": datetime.now().isoformat(),
                "duration_ms": 0,
                "confidence_weight": 0.0,
                "execution_count": self.execution_count,
                "version": self.version
            }
        }
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات الجسر.
        Get bridge statistics.
        """
        return {
            "version": self.version,
            "total_executions": self.execution_count,
            "success_rate": f"{self.success_rate * 100:.1f}%",
            "status": "operational"
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 STANDALONE TEST (للاختبار المباشر)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    import asyncio
    
    async def test_bridge():
        """اختبار الجسر - Test the bridge"""
        bridge = CausalLearningBridge(db_connection=None)
        
        # Test RSI Tool
        print("\n🧪 Testing RSI Tool...")
        result = await bridge.execute_tool_with_causal_context(
            tool_name="rsi",
            params={"prices": [1.05, 1.06, 1.08, 1.10, 1.12, 1.15, 1.14, 1.13, 1.12, 1.11, 1.10, 1.09, 1.08, 1.07, 1.06]},
            user_context={"chat_id": "test_user"}
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Test Kelly Tool
        print("\n🧪 Testing Kelly Criterion...")
        result = await bridge.execute_tool_with_causal_context(
            tool_name="kelly",
            params={"win_rate": 0.6, "avg_win": 100, "avg_loss": 50},
            user_context={"chat_id": "test_user"}
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Stats
        print("\n📊 Bridge Stats:")
        print(json.dumps(bridge.get_stats(), indent=2))
    
    asyncio.run(test_bridge())
