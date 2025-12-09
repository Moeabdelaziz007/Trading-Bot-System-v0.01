# Learning Loop v2.0 Module Initialization
# Provides the AlphaAxiom Enhanced Learning Loop components
# Author: Axiom AI Partner | Mohamed Hossameldin Abdelaziz

__version__ = "2.1.0"
__author__ = "Axiom AI Partner"

# Import core components
from .core import (
    IntelligentCollaborationEngine,
    AgentInsight,
    CollaborationDecision,
    BayesianRiskEngine,
    RiskAssessment,
    RiskDecision,
    WeightedConsensusEngine,
    AgentOpinion,
    ConsensusResult
)

# Import Data Flow Pipeline (NEW in v2.1)
try:
    from .data_flow_pipeline import (
        DataFlowPipeline,
        SignalCollector,
        OutcomeTracker,
        PerformanceFeed,
        WeightUpdater,
        AgentSignal,
        TradeResult,
        AgentMetrics,
        get_pipeline
    )
    _DATA_FLOW_AVAILABLE = True
except ImportError:
    _DATA_FLOW_AVAILABLE = False

# Import Safety Mechanisms (NEW in v2.1)
try:
    from .safety_mechanisms import (
        SafetyOrchestrator,
        TradingModeGuard,
        DriftGuardIntegration,
        CircuitBreaker,
        DataFreshnessChecker,
        SafetyCheckResult,
        TradingMode,
        SafetyStatus,
        BlockReason,
        get_safety_orchestrator
    )
    _SAFETY_AVAILABLE = True
except ImportError:
    _SAFETY_AVAILABLE = False

__all__ = [
    # Core v2.0
    'IntelligentCollaborationEngine',
    'AgentInsight',
    'CollaborationDecision',
    'BayesianRiskEngine',
    'RiskAssessment',
    'RiskDecision',
    'WeightedConsensusEngine',
    'AgentOpinion',
    'ConsensusResult',
    # Data Flow Pipeline v2.1
    'DataFlowPipeline',
    'SignalCollector',
    'OutcomeTracker',
    'PerformanceFeed',
    'WeightUpdater',
    'AgentSignal',
    'TradeResult',
    'AgentMetrics',
    'get_pipeline',
    # Safety Mechanisms v2.1
    'SafetyOrchestrator',
    'TradingModeGuard',
    'DriftGuardIntegration',
    'CircuitBreaker',
    'DataFreshnessChecker',
    'SafetyCheckResult',
    'TradingMode',
    'SafetyStatus',
    'BlockReason',
    'get_safety_orchestrator',
]