"""
Weighted Consensus Engine for AlphaAxiom Learning Loop v2.0

This module implements improved decision-making algorithms with weighted consensus 
mechanisms for the AlphaAxiom trading system. It applies concepts from 
DeepMind's Alpha series frameworks to achieve consensus among multiple agents.
"""

import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class AgentOpinion:
    """Represents an opinion from an agent"""
    agent_id: str
    opinion_type: str  # 'trade', 'risk', 'strategy', 'signal'
    recommendation: str  # 'BUY', 'SELL', 'HOLD', etc.
    confidence: float  # 0.0 to 1.0
    reasoning: str
    timestamp: datetime
    supporting_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class ConsensusResult:
    """Represents a consensus result from multiple agent opinions"""
    consensus_id: str
    topic: str
    final_decision: str
    confidence: float
    consensus_strength: float  # Measure of agreement among agents
    reasoning: str
    timestamp: datetime
    participant_opinions: List[Dict]
    weight_distribution: Dict[str, float]
    metadata: Optional[Dict[str, Any]] = None

class WeightedConsensusEngine:
    """
    Improved decision-making algorithms with weighted consensus mechanisms.
    
    This engine applies concepts from DeepMind's Alpha series frameworks to achieve
    consensus among multiple agents. It uses weighted voting based on agent 
    performance, expertise, and confidence, similar to how AlphaZero combines
    multiple neural network evaluations to make decisions.
    """
    
    def __init__(self, d1_db, kv_store):
        """
        Initialize the Weighted Consensus Engine.
        
        Args:
            d1_db: D1 database connection for persistent storage
            kv_store: KV store for fast access to consensus data
        """
        self.d1 = d1_db
        self.kv = kv_store
        self.consensus_history = []
        self.agent_weights = {}
        self.consensus_models = {}
        
        # Default consensus parameters
        self.consensus_params = {
            'min_participants': 3,
            'confidence_threshold': 0.6,
            'consensus_threshold': 0.7,
            'diversity_weight': 0.3,
            'recency_weight': 0.2
        }
    
    async def gather_agent_opinions(
            self, topic: str, agents: List[str], context: Dict
    ) -> List[AgentOpinion]:
        """
        Gather opinions from multiple agents on a specific topic.
        
        Args:
            topic: Topic to gather opinions on
            agents: List of agent IDs to query
            context: Context information for the agents
            
        Returns:
            List of AgentOpinion objects
        """
        opinions = []
        
        for agent_id in agents:
            opinion = await self._get_agent_opinion(agent_id, topic, context)
            if opinion:
                opinions.append(opinion)
        
        return opinions
    
    async def reach_weighted_consensus(
            self, topic: str, opinions: List[AgentOpinion]
    ) -> ConsensusResult:
        """
        Reach weighted consensus among agent opinions.
        
        Args:
            topic: Topic for consensus
            opinions: List of AgentOpinion objects
            
        Returns:
            ConsensusResult object with the consensus decision
        """
        # 1. Validate minimum participants
        if len(opinions) < self.consensus_params['min_participants']:
            return await self._create_default_consensus(topic, opinions)
        
        # 2. Calculate weights for each opinion
        weights = await self._calculate_opinion_weights(opinions)
        
        # 3. Apply weighted voting
        voting_results = self._apply_weighted_voting(opinions, weights)
        
        # 4. Determine consensus strength
        consensus_strength = self._calculate_consensus_strength(voting_results)
        
        # 5. Select final decision
        final_decision, confidence = self._select_final_decision(voting_results)
        
        # 6. Generate collective reasoning
        reasoning = await self._generate_collective_reasoning(
            opinions, weights, voting_results, final_decision)
        
        # 7. Create consensus result
        result = ConsensusResult(
            consensus_id=f"consensus_{topic}_{int(datetime.now().timestamp())}",
            topic=topic,
            final_decision=final_decision,
            confidence=confidence,
            consensus_strength=consensus_strength,
            reasoning=reasoning,
            timestamp=datetime.now(),
            participant_opinions=[asdict(opinion) for opinion in opinions],
            weight_distribution=weights
        )
        
        # 8. Store consensus result
        await self._store_consensus_result(result)
        
        # 9. Update agent weights based on consensus outcome
        await self._update_agent_weights(opinions, result)
        
        return result
    
    async def _get_agent_opinion(
            self, agent_id: str, topic: str, context: Dict
    ) -> Optional[AgentOpinion]:
        """
        Get an opinion from a specific agent.
        
        Args:
            agent_id: ID of the agent
            topic: Topic for the opinion
            context: Context information
            
        Returns:
            AgentOpinion object or None
        """
        # In a full implementation, this would query the actual agent
        # For now, we'll return a mock opinion based on agent type
        
        # Determine opinion based on agent type (simplified)
        agent_type = agent_id.split('_')[0] if '_' in agent_id else 'general'
        
        opinion_map = {
            'analyst': ('BUY', 0.75, 'Technical analysis indicates bullish pattern'),
            'strategist': ('HOLD', 0.8, 'Portfolio rebalancing suggests neutral stance'),
            'risk': ('SELL', 0.7, 'Risk metrics indicate overexposure'),
            'general': ('HOLD', 0.6, 'Market conditions appear stable')
        }
        
        recommendation, confidence, reasoning = opinion_map.get(
            agent_type, ('HOLD', 0.5, 'Default recommendation'))
        
        return AgentOpinion(
            agent_id=agent_id,
            opinion_type='trade',
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            timestamp=datetime.now(),
            supporting_data=context
        )
    
    async def _calculate_opinion_weights(
            self, opinions: List[AgentOpinion]
    ) -> Dict[str, float]:
        """
        Calculate weights for each opinion based on agent performance and confidence.
        
        Args:
            opinions: List of AgentOpinion objects
            
        Returns:
            Dictionary mapping agent IDs to weights
        """
        weights = {}
        total_weight = 0.0
        
        for opinion in opinions:
            agent_id = opinion.agent_id
            
            # Base weight from agent performance
            base_weight = await self._get_agent_performance_weight(agent_id)
            
            # Confidence weight
            confidence_weight = opinion.confidence
            
            # Recency weight (more recent opinions weighted slightly higher)
            recency_weight = 1.0  # Simplified - would calculate based on timestamp
            
            # Diversity weight (encourage different types of agents)
            diversity_weight = await self._calculate_diversity_weight(
                agent_id, opinions)
            
            # Combined weight
            final_weight = (
                base_weight * 0.4 +
                confidence_weight * 0.3 +
                recency_weight * 0.2 +
                diversity_weight * 0.1
            )
            
            weights[agent_id] = final_weight
            total_weight += final_weight
        
        # Normalize weights
        if total_weight > 0:
            for agent_id in weights:
                weights[agent_id] /= total_weight
        
        return weights
    
    async def _get_agent_performance_weight(self, agent_id: str) -> float:
        """
        Get performance-based weight for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Float representing performance weight (0.0 to 1.0)
        """
        # Check cache first
        if agent_id in self.agent_weights:
            return self.agent_weights[agent_id]
        
        # Check KV store
        cached = await self.kv.get(f"agent_weight_{agent_id}")
        if cached:
            weight = float(cached)
            self.agent_weights[agent_id] = weight
            return weight
        
        # Check database
        result = await self.d1.execute(
            "SELECT avg_accuracy FROM agent_performance WHERE agent_id = ?",
            agent_id
        )
        
        if result and result[0]['avg_accuracy'] is not None:
            weight = float(result[0]['avg_accuracy']) / 100.0
            # Cache for future use
            self.agent_weights[agent_id] = weight
            await self.kv.put(f"agent_weight_{agent_id}", str(weight))
            return weight
        
        # Default weight if no history
        return 0.5
    
    async def _calculate_diversity_weight(
            self, agent_id: str, opinions: List[AgentOpinion]
    ) -> float:
        """
        Calculate diversity weight to encourage different types of agents.
        
        Args:
            agent_id: ID of the agent
            opinions: List of all opinions
            
        Returns:
            Float representing diversity weight (0.0 to 1.0)
        """
        # Count how many agents of the same type we already have
        agent_type = agent_id.split('_')[0] if '_' in agent_id else 'general'
        
        same_type_count = 0
        for opinion in opinions:
            op_agent_type = (opinion.agent_id.split('_')[0] 
                           if '_' in opinion.agent_id else 'general')
            if op_agent_type == agent_type:
                same_type_count += 1
        
        # Lower weight if we already have many of the same type
        diversity_weight = max(0.1, 1.0 - (same_type_count * 0.1))
        return diversity_weight
    
    def _apply_weighted_voting(
            self, opinions: List[AgentOpinion], weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Apply weighted voting to agent opinions.
        
        Args:
            opinions: List of AgentOpinion objects
            weights: Dictionary of agent weights
            
        Returns:
            Dictionary mapping recommendations to weighted votes
        """
        votes = {}
        total_votes = 0.0
        
        for opinion in opinions:
            agent_id = opinion.agent_id
            recommendation = opinion.recommendation
            weight = weights.get(agent_id, 0.0)
            
            # Apply confidence adjustment
            adjusted_weight = weight * opinion.confidence
            
            votes[recommendation] = votes.get(recommendation, 0.0) + adjusted_weight
            total_votes += adjusted_weight
        
        # Normalize votes
        if total_votes > 0:
            for recommendation in votes:
                votes[recommendation] /= total_votes
        
        return votes
    
    def _calculate_consensus_strength(self, voting_results: Dict[str, float]) -> float:
        """
        Calculate the strength of consensus from voting results.
        
        Args:
            voting_results: Dictionary of voting results
            
        Returns:
            Float representing consensus strength (0.0 to 1.0)
        """
        if not voting_results:
            return 0.0
        
        # Consensus strength is the proportion of votes for the top choice
        top_vote = max(voting_results.values())
        return top_vote
    
    def _select_final_decision(
            self, voting_results: Dict[str, float]
    ) -> tuple[str, float]:
        """
        Select the final decision from voting results.
        
        Args:
            voting_results: Dictionary of voting results
            
        Returns:
            Tuple of (decision, confidence)
        """
        if not voting_results:
            return ('HOLD', 0.0)
        
        # Select the option with the highest votes
        final_decision = max(voting_results.items(), key=lambda x: x[1])
        return (final_decision[0], final_decision[1])
    
    async def _generate_collective_reasoning(
            self, opinions: List[AgentOpinion], weights: Dict[str, float],
            voting_results: Dict[str, float], final_decision: str
    ) -> str:
        """
        Generate collective reasoning for the consensus decision.
        
        Args:
            opinions: List of AgentOpinion objects
            weights: Dictionary of agent weights
            voting_results: Voting results
            final_decision: Final decision
            
        Returns:
            String with collective reasoning
        """
        reasoning_parts = [f"Consensus decision: {final_decision}"]
        
        # Add consensus strength
        strength = self._calculate_consensus_strength(voting_results)
        reasoning_parts.append(f"Consensus strength: {strength:.2f}")
        
        # Add top contributing opinions
        top_opinions = sorted(opinions, key=lambda x: weights.get(x.agent_id, 0.0), 
                             reverse=True)[:3]
        
        reasoning_parts.append("Top contributing opinions:")
        for i, opinion in enumerate(top_opinions, 1):
            weight = weights.get(opinion.agent_id, 0.0)
            reasoning_parts.append(
                f"{i}. {opinion.agent_id}: {opinion.recommendation} "
                f"(weight: {weight:.2f}, confidence: {opinion.confidence:.2f}) - "
                f"{opinion.reasoning[:50]}..."
            )
        
        # Add dissenting opinions if any
        dissenting = [op for op in opinions if op.recommendation != final_decision]
        if dissenting:
            reasoning_parts.append(f"Dissenting opinions: {len(dissenting)}")
        
        return " ".join(reasoning_parts)
    
    async def _create_default_consensus(
            self, topic: str, opinions: List[AgentOpinion]
    ) -> ConsensusResult:
        """
        Create a default consensus when insufficient opinions are available.
        
        Args:
            topic: Topic for consensus
            opinions: Available opinions
            
        Returns:
            ConsensusResult object
        """
        return ConsensusResult(
            consensus_id=f"consensus_{topic}_{int(datetime.now().timestamp())}",
            topic=topic,
            final_decision='HOLD',
            confidence=0.0,
            consensus_strength=0.0,
            reasoning='Insufficient opinions for consensus',
            timestamp=datetime.now(),
            participant_opinions=[asdict(opinion) for opinion in opinions],
            weight_distribution={}
        )
    
    async def _store_consensus_result(self, result: ConsensusResult) -> None:
        """
        Store a consensus result in the database.
        
        Args:
            result: ConsensusResult to store
        """
        await self.d1.execute(
            """
            INSERT INTO consensus_results 
            (consensus_id, topic, final_decision, confidence, consensus_strength,
             reasoning, timestamp, participant_opinions, weight_distribution)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            result.consensus_id, result.topic, result.final_decision,
            result.confidence, result.consensus_strength, result.reasoning,
            result.timestamp.isoformat(),
            json.dumps(result.participant_opinions),
            json.dumps(result.weight_distribution)
        )
    
    async def _update_agent_weights(
            self, opinions: List[AgentOpinion], result: ConsensusResult
    ) -> None:
        """
        Update agent weights based on consensus outcome.
        
        Args:
            opinions: List of AgentOpinion objects
            result: ConsensusResult
        """
        # In a full implementation, this would update agent weights based on
        # how well their opinions aligned with the eventual outcome
        # For now, we'll just cache the current weights
        
        for opinion in opinions:
            agent_id = opinion.agent_id
            weight = result.weight_distribution.get(agent_id, 0.5)
            self.agent_weights[agent_id] = weight
            await self.kv.put(f"agent_weight_{agent_id}", str(weight))