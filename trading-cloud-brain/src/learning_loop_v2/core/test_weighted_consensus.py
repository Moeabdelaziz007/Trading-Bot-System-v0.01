"""
Test module for the Weighted Consensus Engine
"""

import asyncio
from datetime import datetime
from .weighted_consensus import WeightedConsensusEngine, AgentOpinion


# Mock database and KV store for testing
class MockDB:
    async def execute(self, query, *args):
        print(f"DB Query: {query}")
        print(f"Args: {args}")
        return []


class MockKV:
    def __init__(self):
        self.data = {}
    
    async def get(self, key):
        return self.data.get(key)
    
    async def put(self, key, value):
        self.data[key] = value


async def test_weighted_consensus_engine():
    """Test the Weighted Consensus Engine implementation"""
    print("Testing Weighted Consensus Engine...")
    
    # Create mock dependencies
    mock_db = MockDB()
    mock_kv = MockKV()
    
    # Create engine instance
    engine = WeightedConsensusEngine(mock_db, mock_kv)
    
    # Create test opinions
    opinions = [
        AgentOpinion(
            agent_id="analyst_1",
            opinion_type="trade",
            recommendation="BUY",
            confidence=0.8,
            reasoning="Strong bullish pattern detected",
            timestamp=datetime.now(),
            supporting_data={"symbol": "BTC/USD"}
        ),
        AgentOpinion(
            agent_id="strategist_1",
            opinion_type="trade",
            recommendation="HOLD",
            confidence=0.7,
            reasoning="Portfolio already balanced",
            timestamp=datetime.now(),
            supporting_data={"symbol": "BTC/USD"}
        ),
        AgentOpinion(
            agent_id="risk_1",
            opinion_type="trade",
            recommendation="SELL",
            confidence=0.9,
            reasoning="High volatility detected",
            timestamp=datetime.now(),
            supporting_data={"symbol": "BTC/USD"}
        )
    ]
    
    # Test weighted consensus
    print("\n1. Testing weighted consensus...")
    consensus = await engine.reach_weighted_consensus(
        "BTC/USD_trade", opinions)
    print(f"Consensus Result: {consensus}")
    
    print("\nTest completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_weighted_consensus_engine())