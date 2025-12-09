# Core Components Module
# Contains the fundamental engines of the AlphaAxiom Learning Loop v2.0

# Import core classes from intelligent collaboration module
from .intelligent_collaboration import (
    IntelligentCollaborationEngine,
    AgentInsight,
    CollaborationDecision
)

# Import core classes from bayesian risk engine module
from .bayesian_risk_engine import (
    BayesianRiskEngine,
    RiskAssessment,
    RiskDecision
)

# Import core classes from weighted consensus module
from .weighted_consensus import (
    WeightedConsensusEngine,
    AgentOpinion,
    ConsensusResult
)

# Import core classes from causal inference module
from .causal_inference import (
    CausalInferenceEngine,
    CausalGraph,
    CausalVariable,
    CausalEdge,
    CausalEffect,
    CounterfactualResult
)

# Import core classes from causal bridge module (Telegram + MCP integration)
from .causal_bridge import (
    CausalLearningBridge,
    ToolCall,
    CausalDecision,
    DecisionOutcome,
    ToolCategory,
    DecisionType
)

__all__ = [
    'IntelligentCollaborationEngine',
    'AgentInsight',
    'CollaborationDecision',
    'BayesianRiskEngine',
    'RiskAssessment',
    'RiskDecision',
    'WeightedConsensusEngine',
    'AgentOpinion',
    'ConsensusResult',
    'CausalInferenceEngine',
    'CausalGraph',
    'CausalVariable',
    'CausalEdge',
    'CausalEffect',
    'CounterfactualResult',
    # Causal Bridge (Telegram + MCP + Learning Loop)
    'CausalLearningBridge',
    'ToolCall',
    'CausalDecision',
    'DecisionOutcome',
    'ToolCategory',
    'DecisionType'
]