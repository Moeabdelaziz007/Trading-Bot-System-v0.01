"""
Causal Learning Bridge v1.0
AlphaAxiom Learning Loop v2.0

The Integration Layer that connects:
- Telegram Bot Commands to AlphaMCP Tools
- Causal Inference Engine to Decision Analysis
- Learning Loop to Self-Improvement
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
from enum import Enum
import json


class ToolCategory(Enum):
    RISK = "risk"
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    INFO = "info"


class DecisionType(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    ADJUST = "adjust"


@dataclass
class ToolCall:
    tool_name: str
    category: ToolCategory
    parameters: dict
    result: dict
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0


@dataclass
class CausalDecision:
    decision_id: str
    decision_type: DecisionType
    symbol: str
    confidence: float
    tool_calls: list
    causal_factors: dict
    counterfactual_analysis: dict
    expected_outcome: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DecisionOutcome:
    decision_id: str
    actual_outcome: float
    expected_outcome: float
    prediction_error: float
    was_correct: bool
    outcome_time: datetime = field(default_factory=datetime.now)


class CausalLearningBridge:
    """
    Main integration layer connecting:
    - Telegram commands to AlphaMCP tools
    - Decisions to Causal Inference analysis
    - Outcomes to Learning Loop for self-improvement
    """
    
    TOOL_CATEGORIES = {
        "calculate_kelly_criterion": ToolCategory.RISK,
        "advanced_rsi_analysis": ToolCategory.ANALYSIS,
        "alphaaxiom_market_analysis": ToolCategory.ANALYSIS,
        "intelligent_position_sizing": ToolCategory.RISK,
        "portfolio_risk_assessment": ToolCategory.RISK,
        "multi_timeframe_analysis": ToolCategory.ANALYSIS,
        "strategy_backtest_simulation": ToolCategory.STRATEGY,
        "get_server_info": ToolCategory.INFO,
        "market_calendar_today": ToolCategory.INFO,
    }
    
    def __init__(
        self,
        kv_store: Optional[Any] = None,
        d1_database: Optional[Any] = None,
        telegram_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self.kv = kv_store
        self.d1 = d1_database
        self.telegram_token = telegram_token
        self.chat_id = chat_id
        self._causal_engine = None
        self._mcp_tools = None
        self._pending_decisions = {}
        self._decision_history = []
        self._accuracy_by_tool = {}
        self._tool_usage_count = {}
    
    @property
    def causal_engine(self):
        if self._causal_engine is None:
            from learning_loop_v2.core.causal_inference import CausalInferenceEngine
            self._causal_engine = CausalInferenceEngine(
                kv_store=self.kv, d1_database=self.d1
            )
        return self._causal_engine
    
    @property
    def mcp_tools(self):
        if self._mcp_tools is None:
            try:
                from alpha_mcp import moe_axiom_tools
                self._mcp_tools = moe_axiom_tools
            except ImportError:
                self._mcp_tools = None
        return self._mcp_tools
    
    async def execute_tool(self, tool_name: str, parameters: dict) -> ToolCall:
        """Execute an AlphaMCP tool and record the call."""
        start_time = datetime.now()
        
        if self.mcp_tools is None:
            return ToolCall(
                tool_name=tool_name, category=ToolCategory.INFO,
                parameters=parameters,
                result={"error": "MCP tools not available"},
                execution_time_ms=0
            )
        
        tool_func = getattr(self.mcp_tools, tool_name, None)
        if tool_func is None:
            return ToolCall(
                tool_name=tool_name, category=ToolCategory.INFO,
                parameters=parameters,
                result={"error": f"Tool {tool_name} not found"},
                execution_time_ms=0
            )
        
        try:
            result = tool_func(**parameters)
        except Exception as e:
            result = {"error": str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        self._tool_usage_count[tool_name] = self._tool_usage_count.get(tool_name, 0) + 1
        
        return ToolCall(
            tool_name=tool_name,
            category=self.TOOL_CATEGORIES.get(tool_name, ToolCategory.INFO),
            parameters=parameters, result=result,
            execution_time_ms=execution_time
        )

    async def make_causal_decision(self, symbol: str, context: dict) -> CausalDecision:
        """Make a trading decision using causal analysis."""
        import uuid
        decision_id = str(uuid.uuid4())[:8]
        tool_calls = []
        
        # Gather data from tools
        if "prices" in context:
            tool_calls.append(await self.execute_tool(
                "advanced_rsi_analysis", {"prices": context["prices"]}
            ))
        
        if all(k in context for k in ["current_price", "volume", "volatility"]):
            tool_calls.append(await self.execute_tool(
                "alphaaxiom_market_analysis", {
                    "symbol": symbol,
                    "current_price": context.get("current_price", 0),
                    "volume": context.get("volume", 1.0),
                    "volatility": context.get("volatility", 0.02),
                    "news_sentiment": context.get("news_sentiment", "neutral"),
                    "social_sentiment": context.get("social_sentiment", "neutral")
                }
            ))
        
        # Causal analysis
        observations = self._tools_to_observations(tool_calls, context)
        causal_analysis = await self.causal_engine.analyze_trading_causality(
            trading_data=observations,
            signal_variable="signal", return_variable="return"
        )
        
        decision_type, confidence = self._synthesize_decision(tool_calls, causal_analysis)
        
        # Counterfactual
        counterfactual = {}
        if observations:
            cf = await self.causal_engine.compute_counterfactual(
                observation=observations[-1],
                intervention={"signal": 1.0 if decision_type == DecisionType.BUY else 0.0},
                outcome_variable="return"
            )
            counterfactual = {
                "factual_outcome": cf.factual_outcome,
                "counterfactual_outcome": cf.counterfactual_outcome,
                "causal_effect": cf.causal_effect
            }
        
        expected = self._calculate_expected_outcome(tool_calls, causal_analysis, counterfactual)
        reasoning = self._generate_reasoning(symbol, tool_calls, causal_analysis, decision_type)
        
        decision = CausalDecision(
            decision_id=decision_id, decision_type=decision_type,
            symbol=symbol, confidence=confidence, tool_calls=tool_calls,
            causal_factors={
                "causal_effect": causal_analysis.get("causal_effect"),
                "confounders": causal_analysis.get("confounders", []),
                "is_causal": causal_analysis.get("is_causal", False)
            },
            counterfactual_analysis=counterfactual,
            expected_outcome=expected, reasoning=reasoning
        )
        
        self._pending_decisions[decision_id] = decision
        self._decision_history.append(decision)
        return decision
    
    def _tools_to_observations(self, tool_calls, context):
        observations = []
        for tc in tool_calls:
            if tc.result.get("error"):
                continue
            obs = {"tool": tc.tool_name}
            if tc.tool_name == "advanced_rsi_analysis":
                rsi = tc.result.get("rsi_value", 50)
                obs["signal"] = 1.0 if rsi < 30 else (0.0 if rsi > 70 else 0.5)
            elif tc.tool_name == "alphaaxiom_market_analysis":
                obs["signal"] = tc.result.get("market_score", 0.5)
            obs["return"] = context.get("expected_return", 0.0)
            observations.append(obs)
        return observations
    
    def _synthesize_decision(self, tool_calls, causal_analysis):
        buy, sell = 0, 0
        for tc in tool_calls:
            if tc.result.get("error"):
                continue
            if tc.tool_name == "alphaaxiom_market_analysis":
                action = tc.result.get("action", "HOLD")
                if "BUY" in action: buy += 1
                elif "SELL" in action: sell += 1
        
        effect = causal_analysis.get("causal_effect")
        if effect and hasattr(effect, "ate") and effect.is_significant:
            if effect.ate > 0: buy += 1
            else: sell += 1
        
        total = buy + sell
        if total == 0:
            return DecisionType.HOLD, 0.5
        conf = max(buy, sell) / total
        if buy > sell: return DecisionType.BUY, conf
        if sell > buy: return DecisionType.SELL, conf
        return DecisionType.HOLD, 0.5
    
    def _calculate_expected_outcome(self, tool_calls, causal_analysis, counterfactual):
        effect = causal_analysis.get("causal_effect")
        if effect and hasattr(effect, "ate"):
            return effect.ate
        if counterfactual.get("causal_effect"):
            return counterfactual["causal_effect"]
        return 0.0
    
    def _generate_reasoning(self, symbol, tool_calls, causal_analysis, decision_type):
        emoji = {"buy": "BUY", "sell": "SELL", "hold": "HOLD", "adjust": "ADJUST"}
        return f"{emoji.get(decision_type.value, '?')} {symbol}"

    async def record_outcome(self, decision_id: str, actual_outcome: float) -> DecisionOutcome:
        """Record outcome for learning."""
        decision = self._pending_decisions.get(decision_id)
        if not decision:
            raise ValueError(f"Decision {decision_id} not found")
        
        error = actual_outcome - decision.expected_outcome
        correct = (
            (decision.decision_type == DecisionType.BUY and actual_outcome > 0) or
            (decision.decision_type == DecisionType.SELL and actual_outcome < 0) or
            (decision.decision_type == DecisionType.HOLD and abs(actual_outcome) < 0.01)
        )
        
        outcome = DecisionOutcome(
            decision_id=decision_id, actual_outcome=actual_outcome,
            expected_outcome=decision.expected_outcome,
            prediction_error=error, was_correct=correct
        )
        
        for tc in decision.tool_calls:
            self._update_tool_accuracy(tc.tool_name, correct)
        
        del self._pending_decisions[decision_id]
        return outcome
    
    def _update_tool_accuracy(self, tool_name, was_correct):
        current = self._accuracy_by_tool.get(tool_name, 0.5)
        count = self._tool_usage_count.get(tool_name, 1)
        alpha = 2 / (count + 1)
        self._accuracy_by_tool[tool_name] = alpha * (1.0 if was_correct else 0.0) + (1 - alpha) * current
    
    async def get_learning_metrics(self):
        return {
            "total_decisions": len(self._decision_history),
            "pending_decisions": len(self._pending_decisions),
            "tool_accuracy": self._accuracy_by_tool,
            "tool_usage": self._tool_usage_count,
            "top_tools": sorted(self._accuracy_by_tool.items(), key=lambda x: x[1], reverse=True)[:3]
        }

    async def handle_telegram_command(self, command: str, args: list) -> str:
        """Handle /mcp commands from Telegram."""
        if not command:
            return self._get_help()
        
        cmd = command.lower()
        if cmd == "status":
            info = self.mcp_tools.get_server_info() if self.mcp_tools else {}
            return f"Server: {info.get('server_name', 'N/A')}, Tools: {info.get('total_tools', 0)}"
        elif cmd == "metrics":
            m = await self.get_learning_metrics()
            return f"Decisions: {m['total_decisions']}, Pending: {m['pending_decisions']}"
        elif cmd == "kelly" and len(args) >= 3:
            result = await self.execute_tool("calculate_kelly_criterion", {
                "win_rate": float(args[0]), "avg_win": float(args[1]),
                "avg_loss": float(args[2]),
                "risk_aversion": args[3] if len(args) > 3 else "MODERATE"
            })
            return str(result.result)
        elif cmd == "decision" and args:
            d = await self.make_causal_decision(args[0].upper(), {
                "current_price": 1.0, "volume": 1.0, "volatility": 0.02,
                "news_sentiment": "neutral"
            })
            return f"{d.decision_type.value.upper()} {d.symbol} (conf: {d.confidence:.1%})"
        return self._get_help()
    
    def _get_help(self):
        return "Commands: /mcp status | metrics | kelly [wr] [win] [loss] | decision [symbol]"
