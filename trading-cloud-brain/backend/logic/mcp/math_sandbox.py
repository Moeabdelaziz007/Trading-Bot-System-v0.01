"""
🧮 MATH SANDBOX (Safe Execution)
Allows LLMs to run generated Python math code safely.
"""

import math
import statistics

class MathSandboxMCP:
    
    ALLOWED_GLOBALS = {
        "math": math,
        "statistics": statistics,
        "sum": sum,
        "len": len,
        "max": max,
        "min": min,
        "abs": abs,
        "round": round,
        "sorted": sorted,
        "list": list,
        "dict": dict
    }
    
    def run_calculation(self, code: str, data: list):
        """
        Executes sanitized math code on a dataset.
        Use Case: "Compute the 200 EMA of this data array"
        """
        # 1. Sanitize
        blacklist = ["import", "open", "eval", "exec", "__", "sys", "os", "subprocess"]
        if any(bad in code for bad in blacklist):
            return {"error": "Security Breach: Unsafe code detected"}
        
        # 2. Prepare Context
        context = {
            "data": data,
            "result": None
        }
        context.update(self.ALLOWED_GLOBALS)
        
        # 3. Execute
        try:
            # Code should assign final value to 'result' variable
            exec(code, {"__builtins__": {}}, context)
            return {"success": True, "result": context.get("result")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_example_prompt():
        return """
        Given a list of numbers in variable 'data'.
        Write Python code to calculate the Simple Moving Average.
        Assign the final value to variable 'result'.
        Do not import any modules.
        Example:
        result = sum(data) / len(data)
        """
