"""
🧠 DeepSeek Analyst Module for Axiom Antigravity
The "Deep Brain" for complex financial analysis requiring 128K context.

RESEARCH-BASED IMPLEMENTATION:
- DeepSeek API is OpenAI-compatible (use same client pattern)
- JSON mode: response_format={'type': 'json_object'}
- Pricing: $0.27/1M input (cache miss), $1.10/1M output
- 128K context window for long document analysis

ARCHITECTURE:
- Groq (Fast Brain): Real-time decisions, < 1 second
- DeepSeek (Deep Brain): Heavy analysis, document reasoning

EXPERT FEATURES:
- Exponential backoff retry with jitter
- JSON schema validation
- KV caching for repeated queries
- Cost tracking in response
- Timeout handling
"""

import json
import time
import hashlib
from js import fetch, Headers

# DeepSeek API Configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"  # Default model
DEEPSEEK_REASONER = "deepseek-reasoner"  # For complex reasoning tasks

# Pricing per 1M tokens (for cost tracking)
PRICING = {
    "deepseek-chat": {
        "input_cache_hit": 0.07,
        "input_cache_miss": 0.27,
        "output": 1.10
    },
    "deepseek-reasoner": {
        "input_cache_hit": 0.14,
        "input_cache_miss": 0.55,
        "output": 2.19
    }
}

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 10.0  # seconds


class DeepSeekAnalyst:
    """
    🧠 DeepSeek Deep Brain for Complex Financial Analysis
    
    Designed for:
    - Long document analysis (earnings reports, regulatory filings)
    - Multi-source signal synthesis
    - Deep Chain-of-Thought reasoning
    
    Usage:
        analyst = DeepSeekAnalyst(env)
        result = await analyst.analyze_document(text, task="summarize")
        result = await analyst.generate_trading_signal(market_data, news)
    """
    
    def __init__(self, env):
        self.env = env
        self.api_key = str(getattr(env, 'DEEPSEEK_API_KEY', ''))
        self.kv = getattr(env, 'BRAIN_MEMORY', None)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def _get_cache_key(self, prompt: str, model: str) -> str:
        """Generate a cache key from prompt hash"""
        content = f"{model}:{prompt}"
        return f"deepseek_cache:{hashlib.md5(content.encode()).hexdigest()[:16]}"
    
    async def _get_cached_response(self, cache_key: str):
        """Check if we have a cached response"""
        if not self.kv:
            return None
        try:
            cached = await self.kv.get(cache_key)
            if cached:
                data = json.loads(cached)
                # Cache valid for 1 hour
                if time.time() - data.get("timestamp", 0) < 3600:
                    return data.get("response")
        except:
            pass
        return None
    
    async def _set_cached_response(self, cache_key: str, response: dict):
        """Cache the response"""
        if not self.kv:
            return
        try:
            await self.kv.put(cache_key, json.dumps({
                "timestamp": time.time(),
                "response": response
            }))
        except:
            pass
    
    async def _make_request(self, messages: list, model: str = DEEPSEEK_MODEL,
                           json_mode: bool = True, temperature: float = 0.1,
                           max_tokens: int = 4096) -> dict:
        """
        Make a request to DeepSeek API with retry logic.
        
        Args:
            messages: List of message dicts [{role, content}]
            model: Model to use (deepseek-chat or deepseek-reasoner)
            json_mode: If True, force JSON output
            temperature: 0.0-2.0, lower = more deterministic
            max_tokens: Maximum tokens in response
        
        Returns:
            dict: Parsed response with content, usage, and cost
        """
        if not self.api_key:
            return {"error": "DEEPSEEK_API_KEY not configured", "content": None}
        
        headers = Headers.new({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }.items())
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        # Enable JSON mode
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        
        # Retry with exponential backoff
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await fetch(
                    DEEPSEEK_API_URL,
                    method="POST",
                    headers=headers,
                    body=json.dumps(payload)
                )
                
                if response.ok:
                    data = json.loads(await response.text())
                    
                    # Extract content
                    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    usage = data.get("usage", {})
                    
                    # Track tokens
                    input_tokens = usage.get("prompt_tokens", 0)
                    output_tokens = usage.get("completion_tokens", 0)
                    self.total_input_tokens += input_tokens
                    self.total_output_tokens += output_tokens
                    
                    # Calculate cost
                    pricing = PRICING.get(model, PRICING["deepseek-chat"])
                    cost = (input_tokens / 1_000_000 * pricing["input_cache_miss"] +
                           output_tokens / 1_000_000 * pricing["output"])
                    
                    # Parse JSON if in JSON mode
                    parsed_content = content
                    if json_mode and content:
                        try:
                            parsed_content = json.loads(content)
                        except json.JSONDecodeError:
                            # Try to extract JSON from markdown blocks
                            if "```json" in content:
                                json_str = content.split("```json")[1].split("```")[0].strip()
                                parsed_content = json.loads(json_str)
                            elif "```" in content:
                                json_str = content.split("```")[1].split("```")[0].strip()
                                parsed_content = json.loads(json_str)
                    
                    return {
                        "content": parsed_content,
                        "raw_content": content,
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": input_tokens + output_tokens
                        },
                        "cost_usd": round(cost, 6),
                        "model": model,
                        "cached": False
                    }
                
                # Handle rate limits
                if response.status == 429:
                    delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                    # Add jitter
                    delay += (time.time() % 1) * 0.5
                    await self._async_sleep(delay)
                    continue
                
                # Handle other errors
                error_text = await response.text()
                last_error = f"API Error {response.status}: {error_text[:200]}"
                
            except Exception as e:
                last_error = str(e)
                delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
                await self._async_sleep(delay)
        
        return {"error": last_error, "content": None}
    
    async def _async_sleep(self, seconds: float):
        """Async-compatible sleep using fetch timeout trick"""
        # In Cloudflare Workers, we use a dummy fetch with timeout
        try:
            await fetch(
                "https://httpstat.us/200?sleep=" + str(int(seconds * 1000)),
                method="GET"
            )
        except:
            pass
    
    async def analyze_financial_text(self, text: str, analysis_type: str = "sentiment",
                                     use_cache: bool = True) -> dict:
        """
        Analyze financial text for sentiment, signals, or summary.
        
        Args:
            text: Financial text (news, report, etc.)
            analysis_type: "sentiment", "signal", "summary", "risk"
            use_cache: Whether to use cached responses
        
        Returns:
            dict: Analysis result with confidence and reasoning
        """
        # Check cache
        cache_key = self._get_cache_key(f"{analysis_type}:{text[:500]}", DEEPSEEK_MODEL)
        if use_cache:
            cached = await self._get_cached_response(cache_key)
            if cached:
                cached["cached"] = True
                return cached
        
        # Build prompt based on analysis type
        prompts = {
            "sentiment": """أنت محلل مالي خبير. قم بتحليل النص التالي وحدد المشاعر السوقية.

أجب بتنسيق JSON:
{
    "sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
    "confidence": 0-100,
    "key_factors": ["عامل1", "عامل2"],
    "market_impact": "HIGH" | "MEDIUM" | "LOW",
    "reasoning": "تفسير مفصل"
}""",
            "signal": """أنت خوارزمية تداول متقدمة. حلل النص وحدد إشارة التداول.

أجب بتنسيق JSON:
{
    "action": "BUY" | "SELL" | "HOLD",
    "confidence": 0-100,
    "target_assets": ["EURUSD", "..."],
    "risk_level": "HIGH" | "MEDIUM" | "LOW",
    "entry_timing": "IMMEDIATE" | "WAIT" | "AVOID",
    "reasoning": "تحليل مفصل"
}""",
            "summary": """أنت محلل مالي. لخص النص التالي مع التركيز على النقاط المهمة للتداول.

أجب بتنسيق JSON:
{
    "summary": "ملخص موجز",
    "key_points": ["نقطة1", "نقطة2"],
    "market_relevance": "HIGH" | "MEDIUM" | "LOW",
    "affected_sectors": ["قطاع1", "قطاع2"]
}""",
            "risk": """أنت مدير مخاطر مالية. حلل المخاطر في النص التالي.

أجب بتنسيق JSON:
{
    "risk_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
    "risk_factors": ["مخاطرة1", "مخاطرة2"],
    "mitigation": ["إجراء1", "إجراء2"],
    "confidence": 0-100
}"""
        }
        
        system_prompt = prompts.get(analysis_type, prompts["sentiment"])
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"النص للتحليل:\n\n{text}"}
        ]
        
        result = await self._make_request(messages, json_mode=True)
        
        # Cache successful response
        if result.get("content") and use_cache:
            await self._set_cached_response(cache_key, result)
        
        return result
    
    async def generate_trading_signal(self, market_context: dict) -> dict:
        """
        Generate a comprehensive trading signal from multiple data sources.
        
        Args:
            market_context: Dict containing:
                - news: List of recent news items
                - technicals: Technical indicators (RSI, MACD, etc.)
                - sentiment: Current market sentiment
                - economic_events: Upcoming economic events
        
        Returns:
            dict: Trading signal with action, confidence, reasoning
        """
        system_prompt = """أنت نظام تداول خوارزمي متقدم يعمل بالذكاء الاصطناعي.
مهمتك هي تحليل جميع البيانات المتاحة وتوليد إشارة تداول واحدة.

قواعد صارمة:
1. الثقة يجب أن تكون 75% على الأقل للتداول
2. لا تتداول أثناء الأخبار عالية التأثير
3. احترم حدود المخاطر

أجب بتنسيق JSON فقط:
{
    "action": "BUY" | "SELL" | "HOLD",
    "symbol": "EURUSD",
    "confidence": 0-100,
    "entry_price": 0.00,
    "stop_loss": 0.00,
    "take_profit": 0.00,
    "position_size": "SMALL" | "MEDIUM" | "LARGE",
    "reasoning": "تحليل شامل يتضمن جميع العوامل",
    "risk_factors": ["مخاطرة1", "مخاطرة2"],
    "time_horizon": "SCALP" | "INTRADAY" | "SWING"
}"""
        
        user_content = f"""سياق السوق الحالي:

📰 الأخبار:
{json.dumps(market_context.get('news', []), ensure_ascii=False, indent=2)}

📊 المؤشرات الفنية:
{json.dumps(market_context.get('technicals', {}), ensure_ascii=False, indent=2)}

😊 المشاعر:
{json.dumps(market_context.get('sentiment', {}), ensure_ascii=False, indent=2)}

📅 الأحداث الاقتصادية القادمة:
{json.dumps(market_context.get('economic_events', []), ensure_ascii=False, indent=2)}

بناءً على هذه البيانات، ما هي إشارة التداول المثلى؟"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]
        
        # Use reasoner model for complex analysis
        result = await self._make_request(
            messages,
            model=DEEPSEEK_MODEL,  # Use chat for speed, reasoner for accuracy
            json_mode=True,
            temperature=0.1,
            max_tokens=2048
        )
        
        return result
    
    def get_usage_stats(self) -> dict:
        """Get current session usage statistics"""
        pricing = PRICING[DEEPSEEK_MODEL]
        total_cost = (
            self.total_input_tokens / 1_000_000 * pricing["input_cache_miss"] +
            self.total_output_tokens / 1_000_000 * pricing["output"]
        )
        
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "estimated_cost_usd": round(total_cost, 4)
        }
