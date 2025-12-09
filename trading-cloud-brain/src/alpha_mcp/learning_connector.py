"""
🔄 LearningConnector v1.0-beta
Connects AlphaMCP Tools with Causal Inference and Learning Loop
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part of AlphaAxiom Learning Loop v2.0

Responsibilities:
1. Capture tool interactions and outcomes
2. Feed data to CausalInferenceEngine for analysis
3. Track signal performance for weight optimization
4. Enable self-improvement through feedback loops
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from enum import Enum
import math


class OutcomeType(Enum):
    """أنواع النتائج."""
    CORRECT = "correct"
    INCORRECT = "incorrect"
    PARTIAL = "partial"
    PENDING = "pending"
    EXPIRED = "expired"


@dataclass
class InteractionRecord:
    """سجل التفاعل مع الأداة."""
    id: str
    timestamp: int
    intent_type: str
    intent_confidence: float
    tool_name: str
    symbol: Optional[str]
    input_params: Dict[str, Any]
    output_result: Dict[str, Any]
    execution_time_ms: float
    chat_id: int
    outcome: OutcomeType = OutcomeType.PENDING
    outcome_value: Optional[float] = None
    outcome_timestamp: Optional[int] = None


@dataclass
class CausalSignal:
    """إشارة للتحليل السببي."""
    signal_id: str
    signal_type: str  # e.g., "rsi_oversold", "kelly_high"
    signal_value: float
    market_conditions: Dict[str, float]
    outcome_return: Optional[float] = None
    outcome_correct: Optional[bool] = None
    timestamp: int = field(default_factory=lambda: int(datetime.now().timestamp() * 1000))


@dataclass
class LearningMetrics:
    """مقاييس التعلم والتحسين."""
    total_interactions: int
    correct_predictions: int
    accuracy: float
    avg_confidence: float
    confidence_calibration: float  # How well confidence matches accuracy
    top_performing_tools: List[Dict[str, Any]]
    improvement_trend: float  # +/- percentage over time


class LearningConnector:
    """
    الموصل الرئيسي لحلقة التعلم.
    يربط أدوات AlphaMCP بمحرك الاستدلال السببي وتحسين الأوزان.
    """
    
    # Configuration
    OUTCOME_TRACKING_WINDOW_HOURS = 24
    MIN_SAMPLES_FOR_LEARNING = 50
    SIGNAL_CACHE_TTL_HOURS = 72
    
    def __init__(
        self,
        env: Any,
        causal_engine: Optional[Any] = None
    ):
        """
        تهيئة موصل التعلم.
        
        Args:
            env: بيئة Cloudflare Worker
            causal_engine: محرك الاستدلال السببي
        """
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.db = getattr(env, 'DB', None)
        self.causal_engine = causal_engine
        
        # In-memory cache for current session
        self._interaction_buffer: List[InteractionRecord] = []
        self._signal_buffer: List[CausalSignal] = []
        self._max_buffer_size = 100
    
    async def capture_interaction(
        self,
        intent: Any,
        tool_response: Dict[str, Any],
        chat_id: int
    ) -> str:
        """
        تسجيل التفاعل لتتبع النتائج والتحليل السببي.
        
        Args:
            intent: نتيجة تحليل النية
            tool_response: استجابة الأداة
            chat_id: معرف المحادثة
            
        Returns:
            str: معرف التفاعل
        """
        interaction_id = self._generate_id()
        
        record = InteractionRecord(
            id=interaction_id,
            timestamp=int(datetime.now().timestamp() * 1000),
            intent_type=intent.intent.value if hasattr(intent, 'intent') else str(intent),
            intent_confidence=getattr(intent, 'confidence', 0.5),
            tool_name=tool_response.get("tool_name", "unknown"),
            symbol=intent.extracted_params.get("symbol") if hasattr(intent, 'extracted_params') else None,
            input_params=getattr(intent, 'extracted_params', {}),
            output_result=tool_response,
            execution_time_ms=tool_response.get("execution_time_ms", 0),
            chat_id=chat_id
        )
        
        # Add to buffer
        self._interaction_buffer.append(record)
        if len(self._interaction_buffer) > self._max_buffer_size:
            await self._flush_interactions()
        
        # Extract causal signals from the result
        await self._extract_causal_signals(record, tool_response)
        
        # Store in KV for persistence
        if self.kv:
            await self._store_interaction(record)
        
        return interaction_id
    
    async def record_outcome(
        self,
        interaction_id: str,
        outcome: OutcomeType,
        outcome_value: float
    ) -> bool:
        """
        تسجيل نتيجة التفاعل (للتعلم من التجربة).
        
        Args:
            interaction_id: معرف التفاعل
            outcome: نوع النتيجة
            outcome_value: قيمة النتيجة (مثل العائد)
            
        Returns:
            bool: نجاح العملية
        """
        try:
            if self.kv:
                # Retrieve interaction
                data = await self.kv.get(f"interaction:{interaction_id}")
                if data:
                    record = json.loads(data)
                    record["outcome"] = outcome.value
                    record["outcome_value"] = outcome_value
                    record["outcome_timestamp"] = int(datetime.now().timestamp() * 1000)
                    
                    # Update storage
                    await self.kv.put(
                        f"interaction:{interaction_id}",
                        json.dumps(record),
                        {"expirationTtl": 86400 * 30}  # 30 days
                    )
                    
                    # Update causal signals
                    await self._update_causal_signals(
                        interaction_id,
                        outcome == OutcomeType.CORRECT,
                        outcome_value
                    )
                    
                    return True
            return False
        except Exception as e:
            print(f"❌ Error recording outcome: {e}")
            return False
    
    async def get_learning_metrics(self) -> LearningMetrics:
        """
        الحصول على مقاييس التعلم الحالية.
        
        Returns:
            LearningMetrics: مقاييس الأداء والتعلم
        """
        try:
            # Get recent interactions from DB
            if self.db:
                query = """
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN outcome = 'correct' THEN 1 ELSE 0 END) as correct,
                        AVG(confidence) as avg_confidence,
                        tool_name,
                        SUM(CASE WHEN outcome = 'correct' THEN 1 ELSE 0 END) * 100.0 / 
                            NULLIF(COUNT(*), 0) as tool_accuracy
                    FROM tool_interactions
                    WHERE timestamp > ?
                    GROUP BY tool_name
                    ORDER BY tool_accuracy DESC
                """
                
                thirty_days_ago = int(
                    (datetime.now() - timedelta(days=30)).timestamp() * 1000
                )
                result = await self.db.prepare(query).bind(thirty_days_ago).all()
                
                if result.results:
                    rows = result.results
                    total = sum(r.get('total', 0) for r in rows)
                    correct = sum(r.get('correct', 0) for r in rows)
                    
                    top_tools = [
                        {
                            "tool": r.get('tool_name'),
                            "accuracy": r.get('tool_accuracy', 0),
                            "samples": r.get('total', 0)
                        }
                        for r in rows[:5]
                    ]
                    
                    accuracy = correct / total if total > 0 else 0
                    avg_conf = rows[0].get('avg_confidence', 0.5) if rows else 0.5
                    
                    return LearningMetrics(
                        total_interactions=total,
                        correct_predictions=correct,
                        accuracy=accuracy,
                        avg_confidence=avg_conf,
                        confidence_calibration=abs(accuracy - avg_conf),
                        top_performing_tools=top_tools,
                        improvement_trend=0.0  # Calculate trend separately
                    )
            
            # Return default if no DB
            return LearningMetrics(
                total_interactions=len(self._interaction_buffer),
                correct_predictions=0,
                accuracy=0.0,
                avg_confidence=0.5,
                confidence_calibration=0.0,
                top_performing_tools=[],
                improvement_trend=0.0
            )
            
        except Exception as e:
            print(f"❌ Error getting metrics: {e}")
            return LearningMetrics(0, 0, 0.0, 0.5, 0.0, [], 0.0)
    
    async def feed_to_causal_engine(
        self,
        signals: List[CausalSignal]
    ) -> Dict[str, Any]:
        """
        تغذية الإشارات لمحرك الاستدلال السببي.
        
        Args:
            signals: قائمة الإشارات للتحليل
            
        Returns:
            dict: نتائج التحليل السببي
        """
        if not self.causal_engine or len(signals) < self.MIN_SAMPLES_FOR_LEARNING:
            return {
                "status": "insufficient_data",
                "samples": len(signals),
                "required": self.MIN_SAMPLES_FOR_LEARNING
            }
        
        try:
            # Convert signals to format expected by CausalInferenceEngine
            trading_data = []
            for signal in signals:
                if signal.outcome_return is not None:
                    trading_data.append({
                        "signal": 1.0 if signal.signal_value > 0.5 else 0.0,
                        "signal_value": signal.signal_value,
                        "return": signal.outcome_return,
                        "volatility": signal.market_conditions.get("volatility", 0.5),
                        "trend": signal.market_conditions.get("trend", 0.5),
                        "sentiment": signal.market_conditions.get("sentiment", 0.5),
                        "timestamp": signal.timestamp
                    })
            
            if len(trading_data) < self.MIN_SAMPLES_FOR_LEARNING:
                return {
                    "status": "insufficient_outcomes",
                    "with_outcomes": len(trading_data)
                }
            
            # Run causal analysis
            causal_result = await self.causal_engine.analyze_trading_causality(
                trading_data,
                signal_variable="signal",
                return_variable="return"
            )
            
            return {
                "status": "success",
                "causal_effect": causal_result.get("causal_effect"),
                "is_causal": causal_result.get("is_causal", False),
                "confounders": causal_result.get("confounders", []),
                "recommendation": causal_result.get("recommendation", ""),
                "samples_analyzed": len(trading_data)
            }
            
        except Exception as e:
            print(f"❌ Causal analysis error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def trigger_weight_optimization(self) -> Dict[str, Any]:
        """
        تشغيل تحسين الأوزان بناءً على البيانات المجمعة.
        
        Returns:
            dict: نتيجة التحسين
        """
        try:
            # Import weight optimizer
            from ..learning.optimizer import WeightOptimizer
            
            optimizer = WeightOptimizer(self.env)
            result = await optimizer.run()
            
            return {
                "status": result.get("status"),
                "new_version": result.get("version"),
                "expected_improvement": result.get("expected_improvement")
            }
            
        except Exception as e:
            print(f"❌ Optimization error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def analyze_tool_performance(self) -> Dict[str, Any]:
        """
        تحليل أداء الأدوات للتحسين.
        
        Returns:
            dict: تحليل أداء كل أداة
        """
        try:
            if not self.db:
                return {"status": "no_database"}
            
            query = """
                SELECT 
                    tool_name,
                    COUNT(*) as total_calls,
                    AVG(execution_time_ms) as avg_execution_time,
                    SUM(CASE WHEN outcome = 'correct' THEN 1 ELSE 0 END) as correct,
                    SUM(CASE WHEN outcome = 'incorrect' THEN 1 ELSE 0 END) as incorrect,
                    AVG(confidence) as avg_confidence,
                    AVG(outcome_value) as avg_outcome_value
                FROM tool_interactions
                WHERE timestamp > ?
                GROUP BY tool_name
                ORDER BY total_calls DESC
            """
            
            seven_days_ago = int(
                (datetime.now() - timedelta(days=7)).timestamp() * 1000
            )
            result = await self.db.prepare(query).bind(seven_days_ago).all()
            
            if not result.results:
                return {"status": "no_data"}
            
            tool_performance = {}
            for row in result.results:
                tool = row.get('tool_name', 'unknown')
                total = row.get('total_calls', 0)
                correct = row.get('correct', 0)
                
                tool_performance[tool] = {
                    "total_calls": total,
                    "accuracy": correct / total if total > 0 else 0,
                    "avg_execution_time_ms": row.get('avg_execution_time', 0),
                    "avg_confidence": row.get('avg_confidence', 0),
                    "avg_outcome_value": row.get('avg_outcome_value', 0),
                    "reliability_score": self._calculate_reliability_score(
                        correct / total if total > 0 else 0,
                        row.get('avg_confidence', 0.5),
                        total
                    )
                }
            
            # Rank tools
            ranked = sorted(
                tool_performance.items(),
                key=lambda x: x[1]['reliability_score'],
                reverse=True
            )
            
            return {
                "status": "success",
                "tools": tool_performance,
                "top_tool": ranked[0][0] if ranked else None,
                "analysis_period_days": 7
            }
            
        except Exception as e:
            print(f"❌ Performance analysis error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_improvement_recommendations(self) -> List[Dict[str, Any]]:
        """
        الحصول على توصيات للتحسين.
        
        Returns:
            list: قائمة التوصيات
        """
        recommendations = []
        
        try:
            metrics = await self.get_learning_metrics()
            tool_perf = await self.analyze_tool_performance()
            
            # Recommendation 1: Low accuracy
            if metrics.accuracy < 0.5:
                recommendations.append({
                    "priority": "high",
                    "type": "accuracy_improvement",
                    "message": f"الدقة الحالية {metrics.accuracy:.1%} أقل من 50%. "
                              "يُنصح بمراجعة خوارزميات التحليل.",
                    "action": "review_algorithms"
                })
            
            # Recommendation 2: Confidence calibration
            if metrics.confidence_calibration > 0.2:
                recommendations.append({
                    "priority": "medium",
                    "type": "calibration",
                    "message": f"الثقة غير متوازنة مع الدقة الفعلية "
                              f"(فرق {metrics.confidence_calibration:.1%}).",
                    "action": "calibrate_confidence"
                })
            
            # Recommendation 3: Tool-specific issues
            if tool_perf.get("status") == "success":
                for tool, perf in tool_perf.get("tools", {}).items():
                    if perf.get("accuracy", 0) < 0.4 and perf.get("total_calls", 0) > 10:
                        recommendations.append({
                            "priority": "medium",
                            "type": "tool_improvement",
                            "tool": tool,
                            "message": f"أداة '{tool}' لديها دقة منخفضة "
                                      f"({perf['accuracy']:.1%}). تحتاج مراجعة.",
                            "action": "improve_tool"
                        })
            
            # Recommendation 4: Need more data
            if metrics.total_interactions < self.MIN_SAMPLES_FOR_LEARNING:
                recommendations.append({
                    "priority": "low",
                    "type": "data_collection",
                    "message": f"تحتاج {self.MIN_SAMPLES_FOR_LEARNING - metrics.total_interactions} "
                              "تفاعلات إضافية للتحليل السببي الدقيق.",
                    "action": "collect_data"
                })
            
            return sorted(recommendations, key=lambda x: {
                "high": 0, "medium": 1, "low": 2
            }.get(x.get("priority", "low"), 2))
            
        except Exception as e:
            print(f"❌ Recommendations error: {e}")
            return []
    
    # ============ Private Methods ============
    
    def _generate_id(self) -> str:
        """توليد معرف فريد."""
        import random
        import string
        timestamp = int(datetime.now().timestamp() * 1000)
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"int_{timestamp}_{random_part}"
    
    async def _store_interaction(self, record: InteractionRecord) -> None:
        """تخزين التفاعل في KV."""
        try:
            if self.kv:
                await self.kv.put(
                    f"interaction:{record.id}",
                    json.dumps(asdict(record)),
                    {"expirationTtl": 86400 * 30}  # 30 days
                )
        except Exception as e:
            print(f"⚠️ Store interaction error: {e}")
    
    async def _flush_interactions(self) -> None:
        """تفريغ buffer التفاعلات إلى D1."""
        if not self.db or not self._interaction_buffer:
            return
        
        try:
            # Batch insert to D1
            query = """
                INSERT INTO tool_interactions 
                (id, timestamp, intent_type, confidence, tool_name, 
                 symbol, input_params, output_result, execution_time_ms, 
                 chat_id, outcome, outcome_value)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for record in self._interaction_buffer[:50]:  # Process 50 at a time
                await self.db.prepare(query).bind(
                    record.id,
                    record.timestamp,
                    record.intent_type,
                    record.intent_confidence,
                    record.tool_name,
                    record.symbol,
                    json.dumps(record.input_params),
                    json.dumps(record.output_result),
                    record.execution_time_ms,
                    record.chat_id,
                    record.outcome.value,
                    record.outcome_value
                ).run()
            
            self._interaction_buffer = self._interaction_buffer[50:]
            
        except Exception as e:
            print(f"⚠️ Flush interactions error: {e}")
    
    async def _extract_causal_signals(
        self,
        record: InteractionRecord,
        tool_response: Dict[str, Any]
    ) -> None:
        """استخراج الإشارات للتحليل السببي."""
        try:
            result = tool_response.get("result", {})
            
            # Extract signal based on tool type
            signal_type = None
            signal_value = 0.5
            
            if "rsi" in record.tool_name.lower():
                rsi = result.get("current_rsi", 50)
                signal_type = "rsi_signal"
                signal_value = 1.0 if rsi < 30 else (0.0 if rsi > 70 else 0.5)
                
            elif "kelly" in record.tool_name.lower():
                kelly = result.get("adjusted_kelly", 0)
                signal_type = "kelly_signal"
                signal_value = min(1.0, max(0.0, kelly * 2))
                
            elif "market" in record.tool_name.lower():
                confidence = result.get("signal", {}).get("confidence", 0.5)
                signal_type = "market_signal"
                signal_value = confidence
            
            if signal_type:
                signal = CausalSignal(
                    signal_id=f"sig_{record.id}",
                    signal_type=signal_type,
                    signal_value=signal_value,
                    market_conditions={
                        "volatility": result.get("market_conditions", {}).get("volatility", 0.5),
                        "trend": result.get("market_conditions", {}).get("trend", 0.5),
                        "sentiment": result.get("market_conditions", {}).get("sentiment", 0.5)
                    }
                )
                
                self._signal_buffer.append(signal)
                
                if len(self._signal_buffer) > self._max_buffer_size:
                    self._signal_buffer = self._signal_buffer[-self._max_buffer_size:]
                    
        except Exception as e:
            print(f"⚠️ Extract signals error: {e}")
    
    async def _update_causal_signals(
        self,
        interaction_id: str,
        was_correct: bool,
        outcome_value: float
    ) -> None:
        """تحديث الإشارات السببية بالنتائج."""
        try:
            signal_id = f"sig_{interaction_id}"
            
            for signal in self._signal_buffer:
                if signal.signal_id == signal_id:
                    signal.outcome_correct = was_correct
                    signal.outcome_return = outcome_value
                    break
                    
        except Exception as e:
            print(f"⚠️ Update signals error: {e}")
    
    def _calculate_reliability_score(
        self,
        accuracy: float,
        avg_confidence: float,
        sample_size: int
    ) -> float:
        """حساب درجة الموثوقية."""
        # Weight accuracy heavily, penalize overconfidence, reward sample size
        accuracy_weight = 0.6
        calibration_weight = 0.2
        sample_weight = 0.2
        
        # Calibration: how close is confidence to accuracy
        calibration_score = 1.0 - abs(accuracy - avg_confidence)
        
        # Sample size score (logarithmic)
        sample_score = min(1.0, math.log10(sample_size + 1) / 2)
        
        reliability = (
            accuracy_weight * accuracy +
            calibration_weight * calibration_score +
            sample_weight * sample_score
        )
        
        return round(reliability, 4)


class OutcomeTracker:
    """
    متتبع النتائج - يتابع نتائج الإشارات تلقائياً.
    يعمل كـ cron job لتحديث نتائج الصفقات.
    """
    
    def __init__(self, env: Any, learning_connector: LearningConnector):
        """تهيئة متتبع النتائج."""
        self.env = env
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.db = getattr(env, 'DB', None)
        self.connector = learning_connector
    
    async def run(self) -> Dict[str, Any]:
        """
        تشغيل دورة تتبع النتائج.
        يُستدعى بشكل دوري (كل ساعة مثلاً).
        
        Returns:
            dict: ملخص التحديثات
        """
        try:
            updated = 0
            errors = 0
            
            # Get pending interactions
            if self.db:
                query = """
                    SELECT id, symbol, output_result, timestamp
                    FROM tool_interactions
                    WHERE outcome = 'pending'
                      AND timestamp > ?
                    LIMIT 100
                """
                
                cutoff = int(
                    (datetime.now() - timedelta(hours=24)).timestamp() * 1000
                )
                result = await self.db.prepare(query).bind(cutoff).all()
                
                for row in result.results:
                    try:
                        # Check if we can determine outcome
                        outcome = await self._determine_outcome(row)
                        
                        if outcome["determined"]:
                            await self.connector.record_outcome(
                                row.get('id'),
                                outcome["type"],
                                outcome["value"]
                            )
                            updated += 1
                            
                    except Exception as e:
                        errors += 1
                        print(f"⚠️ Outcome tracking error: {e}")
            
            return {
                "status": "success",
                "updated": updated,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Outcome tracker error: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _determine_outcome(self, interaction: Dict) -> Dict[str, Any]:
        """
        تحديد نتيجة التفاعل بناءً على بيانات السوق.
        """
        # This would integrate with price feeds to determine if signal was correct
        # For now, return undetermined
        
        result = interaction.get("output_result", {})
        if isinstance(result, str):
            result = json.loads(result)
        
        signal = result.get("signal", {})
        action = signal.get("action", "HOLD")
        
        # Placeholder - would check actual market movement
        # In production, this would:
        # 1. Get entry price from signal
        # 2. Get current price from price feed
        # 3. Compare with predicted direction
        # 4. Determine if stop_loss or take_profit hit
        
        return {
            "determined": False,
            "type": OutcomeType.PENDING,
            "value": 0.0
        }
