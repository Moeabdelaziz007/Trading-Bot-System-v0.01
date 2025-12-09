# ========================================
# 🤖 AXIOM AGENTS - Intelligence Layer
# ========================================
# Ported from Mini-Aladdin Architecture
# ========================================

try:
    # These require Cloudflare Workers environment (Pyodide)
    from .math import MathAgent, get_math_agent
    from .money import MoneyAgent, get_money_agent
    from .journalist import JournalistAgent, get_journalist_agent, news_filter_gate
    from .strategist import StrategistAgent, get_strategist_agent
    
    __all__ = [
        'MathAgent', 'get_math_agent',
        'MoneyAgent', 'get_money_agent',
        'JournalistAgent', 'get_journalist_agent', 'news_filter_gate',
        'StrategistAgent', 'get_strategist_agent'
    ]
except ImportError:
    # Running outside Cloudflare Workers - agents not available
    __all__ = []
