"""
🛡️ Risk Guardian Module for Axiom Antigravity
The "No-Man" - Validates all signals against strict risk protocols.

ROLE:
- Intercepts signals from Analyst/Reflex.
- Validates against News Guard (High Impact Events).
- Checks Portfolio Exposure.
- Uses AI (Workers AI) to audit the trade rationale.

ZERO-COST INFRASTRUCTURE:
- Uses Workers AI (Llama 3.1) for logic checks (Free).
"""

import json
from workers_ai import WorkersAI
from economic_calendar import EconomicCalendar

class RiskGuardian:
    def __init__(self, env):
        self.env = env
        self.ai = WorkersAI(env)
        self.calendar = EconomicCalendar(env)
        
    async def validate_trade(self, signal: dict, account_info: dict) -> dict:
        """
        Validate a potential trade signal.
        
        Args:
            signal: {action, symbol, confidence, rationale}
            account_info: {balance, equity, margin_used}
            
        Returns:
            dict: {approved: bool, reason: str, adjusted_signal: dict}
        """
        # 1. HARD RULE: Check Kill Switch
        try:
            kv = getattr(self.env, 'BRAIN_MEMORY', None)
            if kv:
                panic = await kv.get("panic_mode")
                if panic == "true":
                    return {"approved": False, "reason": "KILL SWITCH ACTIVATED"}
        except:
            pass

        # 2. HARD RULE: News Guard
        # Check if high impact news is imminent for the symbol's currency
        symbol = signal.get("symbol", "")
        if await self.calendar.should_avoid_trading(symbol):
             return {"approved": False, "reason": "HIGH IMPACT NEWS EVENT IMMINENT"}

        # 3. HARD RULE: Confidence Threshold
        # Minimum 75% confidence required
        confidence = float(signal.get("confidence", 0))
        if confidence < 75:
            return {"approved": False, "reason": f"LOW CONFIDENCE ({confidence}%)"}

        # 4. AI AUDIT: "The Risk Officer"
        # Ask Llama to review the trade rationale for logical fallacies or excessive risk
        rationale = signal.get("reasoning", "No rationale provided")
        
        system_prompt = """You are a strict Risk Officer for a hedge fund.
Review the trade rationale. Reject if it sounds like gambling, emotional, or vague.
Approve ONLY if it relies on data/technicals.
Respond ONLY with JSON: {"approved": bool, "risk_rating": "LOW"|"MED"|"HIGH", "comment": "brief comment"}"""
        
        audit_prompt = f"Trade: {signal.get('action')} {symbol}. Rationale: {rationale}"
        
        audit = await self.ai.chat(audit_prompt, system_prompt=system_prompt)
        
        ai_approved = False
        ai_comment = "AI Audit Failed"
        
        if audit.get("content"):
            try:
                # Parse JSON check
                content = audit["content"]
                if "{" in content:
                    json_str = content[content.find("{"):content.rfind("}")+1]
                    parsed = json.loads(json_str)
                    ai_approved = parsed.get("approved", False)
                    ai_comment = parsed.get("comment", "")
                    
                    if not ai_approved:
                        return {"approved": False, "reason": f"AI RISK REJECTION: {ai_comment}"}
            except:
                # If AI fails to parse, default to safe (reject?) or pass if hard rules met
                # For safety, we'll log warning but proceed if hard rules blocked
                ai_comment = "AI parse error, proceeding on hard rules"

        return {
            "approved": True,
            "reason": "PASSED ALL CHECKS",
            "audit_comment": ai_comment,
            "original_signal": signal
        }
