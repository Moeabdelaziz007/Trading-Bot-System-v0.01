"""
🧮 Math Sandbox MCP - Safe Calculator
Zero-Cost Computational Engine

Responsibilities:
- Execute LLM-generated math safely
- Allow: math.*, statistics.*, list operations
- Block: import, exec, eval, system calls
"""

import math
import statistics
import json

class MathEngine:
    def __init__(self):
        self.allowed_globals = {
            "math": math,
            "statistics": statistics,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum,
            "len": len,
            "sorted": sorted,
            "float": float,
            "int": int,
            "list": list,
            "dict": dict
        }

    def evaluate(self, expression: str, data: dict = None):
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Python-like expression string (e.g., "sum(prices) / len(prices)")
            data: Dictionary of variables to inject (e.g., {"prices": [1, 2, 3]})
        """
        context = self.allowed_globals.copy()
        if data:
            context.update(data)

        # Security checks
        if "__" in expression or "import" in expression or "exec" in expression or "eval" in expression:
            return {"error": "Security Violation: Unsafe expression detected"}

        try:
            # We use eval() here BUT strictly controlled globals/locals
            # Cloudflare Workers environment is already sandboxed,
            # but we restrict it further to prevent logic abuse.
            result = eval(expression, {"__builtins__": {}}, context)

            # Check result type
            if isinstance(result, (int, float, bool, str, list, dict)):
                return {"result": result, "status": "success"}
            else:
                return {"result": str(result), "status": "success"}

        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def run_script(self, script: str, inputs: dict):
        """
        Run a multi-line math script (limited functionality).
        This is a simulated execution since we can't easily use exec() safely.
        For now, we stick to single expression evaluation or strict parsing.

        NOTE: For v2.0 Zero-Cost, we focus on 'evaluate' for indicators.
        """
        return {"error": "Multi-line script execution not supported in Zero-Cost Tier. Use evaluate()"}
