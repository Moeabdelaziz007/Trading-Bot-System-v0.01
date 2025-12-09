# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 AlphaMCP - AlphaAxiom MCP Tools Package
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Version: 1.0.0-beta
# Integrated with AlphaAxiom Learning Loop v2.0
# Full Integration: Telegram ↔ MCP Tools ↔ Causal Inference ↔ Learning Loop
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from .moe_axiom_tools import server
from .moe_axiom_tools import (
    calculate_kelly_criterion,
    advanced_rsi_analysis,
    alphaaxiom_market_analysis,
    intelligent_position_sizing,
    portfolio_risk_assessment,
    multi_timeframe_analysis,
    strategy_backtest_simulation,
    get_server_info,
    market_calendar_today,
)
from .telegram_bridge import (
    TelegramMCPBridge,
    IntentDetector,
    UserIntent,
    IntentResult,
    ToolResponse,
)
from .learning_connector import (
    LearningConnector,
    OutcomeTracker,
    LearningMetrics,
    CausalSignal,
    OutcomeType,
)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌉 Causal Bridge (New Export)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from .causal_bridge import CausalLearningBridge

__version__ = "1.0.0-beta"
__author__ = "Mohamed Hossameldin Abdelaziz"
__all__ = [
    # MCP Server
    "server",
    # Tools
    "calculate_kelly_criterion",
    "advanced_rsi_analysis",
    "alphaaxiom_market_analysis",
    "intelligent_position_sizing",
    "portfolio_risk_assessment",
    "multi_timeframe_analysis",
    "strategy_backtest_simulation",
    "get_server_info",
    "market_calendar_today",
    # Telegram Bridge
    "TelegramMCPBridge",
    "IntentDetector",
    "UserIntent",
    "IntentResult",
    "ToolResponse",
    # Learning Connector
    "LearningConnector",
    "OutcomeTracker",
    "LearningMetrics",
    "CausalSignal",
    "OutcomeType",
    # Causal Bridge (NEW)
    "CausalLearningBridge",  # <--- جديد
]
