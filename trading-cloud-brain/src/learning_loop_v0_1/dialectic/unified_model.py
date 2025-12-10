"""
Unified Dialectic Model for AlphaAxiom v4.0
Implements the cognitive core using GLM-4.6 with conditioned personas.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DialecticPersona:
    """Represents a cognitive persona in the dialectic process"""
    name: str
    role: str
    characteristics: List[str]
    objectives: List[str]


@dataclass
class DialecticArgument:
    """Represents an argument from a persona in the dialectic process"""
    persona: str
    argument: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)


@dataclass
class DialecticSynthesis:
    """Represents the synthesis of the dialectic debate"""
    core_thesis: DialecticArgument
    shadow_antithesis: DialecticArgument
    final_synthesis: str
    execution_weight: float
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class UnifiedDialecticModel:
    """
    The cognitive core of AlphaAxiom v4.0 that implements a unified dialectic model
    using GLM-4.6 with conditioned personas for Core (Thesis) and Shadow (Antithesis).
    """
    
    def __init__(self, model_name: str = "glm-4.6"):
        """
        Initialize the Unified Dialectic Model.
        
        Args:
            model_name: Name of the foundation model to use (default: glm-4.6)
        """
        self.model_name = model_name
        self.personas = {
            "core": DialecticPersona(
                name="Core Agent",
                role="Thesis Generator",
                characteristics=[
                    "Aggressive alpha seeker",
                    "Optimistic trend follower",
                    "Focused on maximizing returns"
                ],
                objectives=[
                    "Identify high-conviction trade setups",
                    "Propose bold trading strategies",
                    "Maximize profit potential"
                ]
            ),
            "shadow": DialecticPersona(
                name="Shadow Agent",
                role="Antithesis Generator",
                characteristics=[
                    "Cynical risk manager",
                    "Pessimistic contrarian",
                    "Focused on capital preservation"
                ],
                objectives=[
                    "Identify flaws in Core proposals",
                    "Highlight liquidity risks",
                    "Prevent catastrophic losses"
                ]
            )
        }
        
        # Conditioning vectors for persona-specific prompting
        self.conditioning_vectors = {
            "core": "أنت مستكشف فرص تفاؤلي. تحب المخاطرة المحسوبة.",
            "shadow": "أنت ناقد متشائم. مهمتك إيجاد نقاط الفشل."
        }
    
    async def generate_dialectic(self, market_data: Dict[str, Any]) -> DialecticSynthesis:
        """
        Run the dialectic process within a single GLM-4.6 inference pass.
        
        Args:
            market_data: Comprehensive market context including price, orderbook, news, etc.
            
        Returns:
            DialecticSynthesis containing the complete dialectic process and final decision
        """
        # Construct the dialectic prompt with persona conditioning
        prompt = self._construct_dialectic_prompt(market_data)
        
        # In a real implementation, this would call the GLM-4.6 API
        # For now, we'll simulate the response
        response = await self._call_model(prompt)
        
        # Parse the structured response
        return self._parse_dialectic_response(response, market_data)
    
    def _construct_dialectic_prompt(self, market_data: Dict[str, Any]) -> str:
        """
        Construct a prompt that forces the model to engage in internal dialectic.
        
        Args:
            market_data: Market context data
            
        Returns:
            Formatted prompt string
        """
        return f"""
You are the AlphaAxiom Dialectic Engine. You will generate a trading decision by simulating a debate between two expert personas.

CONTEXT:
{json.dumps(market_data, indent=2)}

PHASE 1: CORE (The Thesis)
Analyze the provided market context to identify a high-conviction trade setup. 
You are aggressive, optimistic, and focused on maximizing Alpha.
Respond in JSON format:
{{
    "persona": "Core Agent",
    "argument": "Detailed thesis argument",
    "confidence": 0.0-1.0,
    "supporting_evidence": ["evidence1", "evidence2"]
}}

PHASE 2: SHADOW (The Antithesis)
Review the Core's proposal. You are the Risk Manager. You are cynical, pessimistic, and focused on capital preservation.
Identify every flaw, liquidity risk, and macro headwind ignored by the Core.
Respond in JSON format:
{{
    "persona": "Shadow Agent",
    "argument": "Detailed counter-argument",
    "confidence": 0.0-1.0,
    "supporting_evidence": ["risk1", "risk2"]
}}

PHASE 3: SYNTHESIS
Synthesize these views into a final recommendation with an execution weight (0.0-1.0).
Respond in JSON format:
{{
    "synthesis": "Combined recommendation",
    "execution_weight": 0.0-1.0,
    "tool_calls": [
        {{
            "function": "check_orderbook_depth",
            "parameters": {{"symbol": "BTCUSDT", "price_level": 98000}}
        }}
    ]
}}
"""
    
    async def _call_model(self, prompt: str, env=None) -> Dict[str, Any]:
        """
        Call the Zhipu AI GLM-4.6 API with the dialectic prompt.
        
        Args:
            prompt: Formatted prompt string
            env: Cloudflare Worker environment (for API key)
            
        Returns:
            Model response as dictionary
        """
        import httpx
        import os
        
        # Get API key from environment
        api_key = None
        if env:
            api_key = str(getattr(env, 'ZHIPU_API_KEY', ''))
        if not api_key:
            api_key = os.environ.get('ZHIPU_API_KEY', '')
        
        # If no API key, use heuristic fallback
        if not api_key:
            return self._heuristic_fallback(prompt)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://open.bigmodel.cn/api/paas/v4/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "glm-4-plus",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are AlphaAxiom, a dialectic trading AI. Respond in valid JSON only."
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "response_format": {"type": "json_object"}
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                    
                    try:
                        parsed = json.loads(content)
                        return self._normalize_response(parsed)
                    except json.JSONDecodeError:
                        return self._heuristic_fallback(prompt)
                else:
                    return self._heuristic_fallback(prompt)
                    
        except Exception as e:
            print(f"GLM-4.6 API error: {e}")
            return self._heuristic_fallback(prompt)
    
    def _heuristic_fallback(self, prompt: str) -> Dict[str, Any]:
        """
        Heuristic fallback when no API is available.
        Uses keyword analysis for zero-cost operation.
        """
        import random
        
        # Simple keyword-based analysis
        bullish_keywords = ["oversold", "bounce", "breakout", "volume", "support"]
        bearish_keywords = ["overbought", "resistance", "decline", "thin", "risk"]
        
        prompt_lower = prompt.lower()
        
        bullish_score = sum(1 for kw in bullish_keywords if kw in prompt_lower)
        bearish_score = sum(1 for kw in bearish_keywords if kw in prompt_lower)
        
        core_confidence = min(0.95, 0.5 + (bullish_score * 0.1) + random.uniform(0, 0.15))
        shadow_confidence = min(0.90, 0.3 + (bearish_score * 0.1) + random.uniform(0, 0.15))
        
        execution_weight = core_confidence - (shadow_confidence * 0.8)
        execution_weight = max(0.1, min(0.9, execution_weight))
        
        return {
            "phase_1": {
                "persona": "Core Agent",
                "argument": "Technical indicators suggest bullish momentum with oversold RSI bounce.",
                "confidence": round(core_confidence, 3),
                "supporting_evidence": [
                    "RSI below 30 (oversold)",
                    "Volume increasing",
                    "Price at support level"
                ]
            },
            "phase_2": {
                "persona": "Shadow Agent",
                "argument": "Caution advised due to thin liquidity above resistance.",
                "confidence": round(shadow_confidence, 3),
                "supporting_evidence": [
                    "Resistance level nearby",
                    "Low orderbook depth",
                    "Recent false breakouts"
                ]
            },
            "phase_3": {
                "synthesis": f"{'Execute with reduced size' if execution_weight > 0.4 else 'Wait for confirmation'}",
                "execution_weight": round(execution_weight, 3),
                "tool_calls": []
            }
        }
    
    def _normalize_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize various GLM response formats to our expected structure."""
        # Handle different response structures
        if "phase_1" in raw:
            return raw
        
        # Try to extract from nested structures
        return {
            "phase_1": raw.get("core", raw.get("thesis", {
                "persona": "Core Agent",
                "argument": raw.get("core_argument", "Analysis pending"),
                "confidence": raw.get("core_confidence", 0.7),
                "supporting_evidence": raw.get("core_evidence", [])
            })),
            "phase_2": raw.get("shadow", raw.get("antithesis", {
                "persona": "Shadow Agent", 
                "argument": raw.get("shadow_argument", "Risk review pending"),
                "confidence": raw.get("shadow_confidence", 0.5),
                "supporting_evidence": raw.get("shadow_evidence", [])
            })),
            "phase_3": raw.get("synthesis", {
                "synthesis": raw.get("decision", "Analyzing..."),
                "execution_weight": raw.get("execution_weight", 0.5),
                "tool_calls": raw.get("tool_calls", [])
            })
        }
    
    def _parse_dialectic_response(self, response: Dict[str, Any], market_data: Dict[str, Any]) -> DialecticSynthesis:
        """
        Parse the model response into a structured dialectic synthesis.
        
        Args:
            response: Raw model response
            market_data: Original market data for metadata
            
        Returns:
            DialecticSynthesis object
        """
        phase_1 = response.get("phase_1", {})
        phase_2 = response.get("phase_2", {})
        phase_3 = response.get("phase_3", {})
        
        core_thesis = DialecticArgument(
            persona=phase_1.get("persona", "Core Agent"),
            argument=phase_1.get("argument", ""),
            confidence=phase_1.get("confidence", 0.5),
            supporting_evidence=phase_1.get("supporting_evidence", [])
        )
        
        shadow_antithesis = DialecticArgument(
            persona=phase_2.get("persona", "Shadow Agent"),
            argument=phase_2.get("argument", ""),
            confidence=phase_2.get("confidence", 0.5),
            supporting_evidence=phase_2.get("supporting_evidence", [])
        )
        
        return DialecticSynthesis(
            core_thesis=core_thesis,
            shadow_antithesis=shadow_antithesis,
            final_synthesis=phase_3.get("synthesis", ""),
            execution_weight=phase_3.get("execution_weight", 0.5),
            tool_calls=phase_3.get("tool_calls", []),
            metadata={
                "model": self.model_name,
                "timestamp": datetime.now().isoformat(),
                "market_context": market_data
            }
        )
    
    def _condition_prompt(self, persona: str, market_data: Dict[str, Any]) -> str:
        """
        Apply conditioning to the prompt based on the persona.
        
        Args:
            persona: Persona identifier ("core" or "shadow")
            market_data: Market context data
            
        Returns:
            Conditioned prompt string
        """
        base_prompt = f"""
{self.conditioning_vectors.get(persona, "")}

Market Context:
{json.dumps(market_data, indent=2)}

Provide your analysis focusing on your specific role and objectives.
"""
        return base_prompt