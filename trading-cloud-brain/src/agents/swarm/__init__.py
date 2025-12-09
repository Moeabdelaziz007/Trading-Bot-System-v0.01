"""
🐝 Mini-Agent Swarm - 24/7 Hypothesis Testing System
نظام سرب الوكلاء المصغرين لاختبار الفرضيات

AlphaAxiom Learning Loop v2.0
Status: ACTIVE as of December 9, 2025

This module implements specialized trading agents that:
- Execute high-frequency paper trades 24/7
- Test distinct market hypotheses
- Generate labeled performance data for Learning Loop
- Feed the Weighted Consensus Engine for self-improvement

Agents:
- MomentumScout: Breakout continuation hypothesis
- ReversionHunter: Mean reversion hypothesis  
- LiquidityWatcher: Volume precedes price hypothesis
- VolatilitySpiker: ATR expansion regime change hypothesis

Monitoring:
- PerformanceMonitor: Meta-learning agent for evaluation
- ContestManager: Internal ranking and weight adjustment
"""

from .base_mini_agent import BaseMiniAgent, AgentSignal, SignalType
from .momentum_scout import MomentumScout
from .reversion_hunter import ReversionHunter
from .liquidity_watcher import LiquidityWatcher
from .volatility_spiker import VolatilitySpiker
from .performance_monitor import PerformanceMonitor
from .contest_manager import ContestManager

__all__ = [
    'BaseMiniAgent',
    'AgentSignal',
    'SignalType',
    'MomentumScout',
    'ReversionHunter',
    'LiquidityWatcher',
    'VolatilitySpiker',
    'PerformanceMonitor',
    'ContestManager',
]

__version__ = "1.0.0"
