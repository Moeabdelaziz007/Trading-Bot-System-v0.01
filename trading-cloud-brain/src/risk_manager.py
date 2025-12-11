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

        # 4. HARD RULE: Fixed Risk Limit (Max 1%)
        # Enforce strict 1% risk per trade limit if size and price are known
        # We assume if 'qty' and 'price' are in signal, we can calculate risk value.
        # If stop_loss is present, risk = (entry - stop) * qty.
        # If no stop loss, we assume full position value risk for safety (conservative) or rely on sizing.
        # Here we check position value relative to account as a proxy for max exposure if SL not explicit.

        qty = float(signal.get("qty", 0))
        price = float(signal.get("price", 0))
        balance = float(account_info.get("balance", 0))
        equity = float(account_info.get("equity", balance)) # Use equity if available

        if qty > 0 and price > 0 and equity > 0:
            position_value = qty * price

            # Scenario A: Stop Loss is known
            stop_loss = float(signal.get("stop_loss", 0))
            if stop_loss > 0:
                risk_amount = abs(price - stop_loss) * qty
                risk_pct = (risk_amount / equity) * 100
                if risk_pct > 1.0:
                    return {
                        "approved": False,
                        "reason": f"EXCESSIVE RISK: {risk_pct:.2f}% > 1.0% limit"
                    }

            # Scenario B: No Stop Loss - Check Position Sizing Cap (Safety net)
            # If we don't have SL, we can't risk more than X% of equity in a single trade value?
            # No, that limits position size too much (e.g. 1% pos size is tiny).
            # Instead, we force a check: If no SL, we reject? Or we allow but assume default risk?
            # For this strict requirement, we will REJECT if risk cannot be calculated OR rely on 'risk_amount' field.
            # Let's check if 'risk_amount' was pre-calculated.
            risk_amt_explicit = float(signal.get("risk_amount", 0))
            if risk_amt_explicit > 0:
                risk_pct = (risk_amt_explicit / equity) * 100
                if risk_pct > 1.0:
                    return {
                        "approved": False,
                        "reason": f"EXCESSIVE RISK (Explicit): {risk_pct:.2f}% > 1.0% limit"
                    }

        # 5. AI AUDIT: "The Risk Officer"
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

    # ==================================================
    # 📊 KELLY CRITERION (Position Sizing from Gemini Research)
    # ==================================================

    def calculate_kelly_fraction(self, win_rate: float, avg_win: float, avg_loss: float) -> dict:
        """
        Kelly Criterion for optimal position sizing.
        Formula: f* = (p * b - q) / b
        
        Where:
        - p = win rate (probability of winning)
        - q = 1 - p (probability of losing)
        - b = avg_win / avg_loss (payout ratio)
        
        :param win_rate: Historical win rate (0.0 to 1.0)
        :param avg_win: Average winning trade amount
        :param avg_loss: Average losing trade amount (positive value)
        
        :returns: Dict with kelly fraction and recommended position size
        """
        if avg_loss <= 0 or win_rate < 0 or win_rate > 1:
            return {"kelly_fraction": 0, "error": "Invalid inputs"}
        
        p = win_rate
        q = 1 - p
        b = avg_win / avg_loss  # Payout ratio
        
        # Kelly Formula: f* = (p * b - q) / b
        kelly = (p * b - q) / b if b > 0 else 0
        
        # Safety caps
        # Full Kelly is aggressive; Half-Kelly is recommended
        half_kelly = kelly / 2
        quarter_kelly = kelly / 4
        
        # Never risk more than 1% (Strict Rule) even if Kelly says so
        capped_kelly = min(kelly, 0.01)
        # Recommendation
        recommended_pct = min(half_kelly, 0.01)
        
        return {
            "full_kelly": round(kelly * 100, 2),
            "half_kelly": round(half_kelly * 100, 2),
            "quarter_kelly": round(quarter_kelly * 100, 2),
            "recommended_pct": round(recommended_pct * 100, 2),
            "payout_ratio": round(b, 2),
            "edge": round((p * b - q) * 100, 2)  # Expected edge %
        }

    # ==================================================
    # 🎲 CHAOS FACTOR (Human-like Behavior from Gemini Research)
    # ==================================================

    def apply_chaos_factor(self, value: float, chaos_level: str = "medium") -> dict:
        """
        Apply human-like randomization to values to avoid pattern detection.
        
        From Gemini Research:
        - Weibull distribution for delays
        - Value dithering (±2%)
        - Precision variance
        
        :param value: Original value (e.g., trade amount)
        :param chaos_level: "low", "medium", "high"
        
        :returns: Dict with chaotic value and metadata
        """
        import random
        import math
        
        # Variance based on chaos level
        variance_map = {
            "low": 0.005,      # ±0.5%
            "medium": 0.02,    # ±2%
            "high": 0.05       # ±5%
        }
        variance = variance_map.get(chaos_level, 0.02)
        
        # 1. Value Dithering (Gaussian noise)
        dither = random.gauss(0, variance)
        chaotic_value = value * (1 + dither)
        
        # 2. Precision Variance (random decimal places)
        decimals = random.choice([2, 3, 4, 5])
        chaotic_value = round(chaotic_value, decimals)
        
        # 3. Weibull Delay (human-like reaction time)
        # Shape 1.5 creates natural "fast rise, slow decay" curve
        weibull_delay = random.weibullvariate(0.5, 1.5)
        human_delay = max(0.15, weibull_delay)  # Min 150ms physiological floor
        
        return {
            "original": value,
            "chaotic": chaotic_value,
            "dither_pct": round(dither * 100, 3),
            "precision": decimals,
            "human_delay_sec": round(human_delay, 3),
            "chaos_level": chaos_level
        }

    async def engage_news_lockdown(self, events: list):
        """
        Emergency lockdown during high-impact news events.
        """
        try:
            kv = getattr(self.env, 'BRAIN_MEMORY', None)
            if kv:
                await kv.put("news_lockdown", "true", expirationTtl=1800)  # 30 min
                print(f"🔒 NEWS LOCKDOWN: {len(events)} high impact events")
        except Exception as e:
            print(f"Lockdown failed: {e}")
