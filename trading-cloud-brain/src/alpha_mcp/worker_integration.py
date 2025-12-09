"""
🔌 AlphaMCP Worker Integration v1.0-beta
Integrates AlphaMCP with Cloudflare Worker for Telegram Bot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Part of AlphaAxiom Learning Loop v2.0

This module provides easy integration with the existing worker.py
Handles the full flow: Telegram → AlphaMCP → Causal → Response
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional


class AlphaMCPIntegration:
    """
    Integration helper for AlphaMCP with Cloudflare Worker.
    Provides a clean interface for Telegram webhook handlers.
    """
    
    def __init__(self, env: Any):
        """
        Initialize the integration.
        
        Args:
            env: Cloudflare Worker environment bindings
        """
        self.env = env
        self._bridge = None
        self._connector = None
        self._causal_engine = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Lazy initialize all components.
        Call this once before processing messages.
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            # Import components
            from .telegram_bridge import TelegramMCPBridge
            from .learning_connector import LearningConnector
            
            # Try to import causal engine
            try:
                from ..learning_loop_v2.core.causal_inference import (
                    CausalInferenceEngine
                )
                self._causal_engine = CausalInferenceEngine(
                    kv_store=getattr(self.env, 'BRAIN_MEMORY', None),
                    d1_database=getattr(self.env, 'DB', None)
                )
            except ImportError:
                self._causal_engine = None
                print("⚠️ CausalInferenceEngine not available")
            
            # Initialize learning connector
            self._connector = LearningConnector(
                env=self.env,
                causal_engine=self._causal_engine
            )
            
            # Initialize bridge
            self._bridge = TelegramMCPBridge(
                env=self.env,
                causal_engine=self._causal_engine,
                learning_connector=self._connector
            )
            
            self._initialized = True
            print("✅ AlphaMCP Integration initialized")
            return True
            
        except Exception as e:
            print(f"❌ AlphaMCP initialization error: {e}")
            return False
    
    async def process_telegram_message(
        self,
        message: str,
        chat_id: int,
        user_name: str = "Trader"
    ) -> str:
        """
        Process a Telegram message through AlphaMCP.
        
        Args:
            message: The message text
            chat_id: Telegram chat ID
            user_name: User's display name
            
        Returns:
            str: Formatted response for Telegram (HTML)
        """
        if not await self.initialize():
            return "❌ خطأ في تهيئة النظام. يرجى المحاولة لاحقاً."
        
        try:
            # Process through bridge
            response = await self._bridge.process_message(
                message=message,
                chat_id=chat_id,
                user_name=user_name
            )
            
            # Format for Telegram
            formatted = self._bridge.format_response_for_telegram(
                response,
                user_name
            )
            
            return formatted
            
        except Exception as e:
            print(f"❌ Message processing error: {e}")
            return f"❌ خطأ: {str(e)}"
    
    async def should_handle_message(self, message: str) -> bool:
        """
        Check if AlphaMCP should handle this message.
        
        Args:
            message: The message text
            
        Returns:
            bool: True if AlphaMCP should handle it
        """
        # Keywords that trigger AlphaMCP
        triggers = [
            # English triggers
            "analyze", "analysis", "position", "risk", "rsi",
            "kelly", "backtest", "size", "market", "trade",
            "timeframe", "mtf", "portfolio", "signal",
            # Arabic triggers
            "تحليل", "حلل", "مركز", "حجم", "مخاطر",
            "كيلي", "باكتست", "سوق", "تداول", "إشارة",
            # Symbols
            "eurusd", "gbpusd", "usdjpy", "xauusd", "gold",
            "btcusd", "ethusd", "us30", "nas100",
        ]
        
        message_lower = message.lower()
        
        # Check for triggers
        for trigger in triggers:
            if trigger in message_lower:
                return True
        
        return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get AlphaMCP system status.
        
        Returns:
            dict: System status information
        """
        if not await self.initialize():
            return {"status": "not_initialized", "error": True}
        
        try:
            # Get learning metrics
            metrics = await self._connector.get_learning_metrics()
            
            # Get tool performance
            perf = await self._connector.analyze_tool_performance()
            
            # Get recommendations
            recommendations = await self._connector.get_improvement_recommendations()
            
            return {
                "status": "operational",
                "version": "1.0.0-beta",
                "components": {
                    "bridge": self._bridge is not None,
                    "connector": self._connector is not None,
                    "causal_engine": self._causal_engine is not None
                },
                "metrics": {
                    "total_interactions": metrics.total_interactions,
                    "accuracy": f"{metrics.accuracy:.1%}",
                    "avg_confidence": f"{metrics.avg_confidence:.1%}"
                },
                "top_tools": perf.get("tools", {}),
                "recommendations_count": len(recommendations),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def trigger_learning_cycle(self) -> Dict[str, Any]:
        """
        Manually trigger a learning/optimization cycle.
        
        Returns:
            dict: Result of the learning cycle
        """
        if not await self.initialize():
            return {"status": "not_initialized"}
        
        try:
            # Feed signals to causal engine
            causal_result = await self._connector.feed_to_causal_engine(
                self._connector._signal_buffer
            )
            
            # Trigger weight optimization if enough data
            if causal_result.get("status") == "success":
                opt_result = await self._connector.trigger_weight_optimization()
            else:
                opt_result = {"status": "skipped", "reason": "insufficient_data"}
            
            return {
                "causal_analysis": causal_result,
                "optimization": opt_result,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton instance for worker
_integration_instance: Optional[AlphaMCPIntegration] = None


def get_alpha_mcp_integration(env: Any) -> AlphaMCPIntegration:
    """
    Get or create the AlphaMCP integration instance.
    
    Args:
        env: Cloudflare Worker environment
        
    Returns:
        AlphaMCPIntegration: The integration instance
    """
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = AlphaMCPIntegration(env)
    
    return _integration_instance


async def handle_alpha_mcp_request(
    message: str,
    chat_id: int,
    user_name: str,
    env: Any
) -> str:
    """
    Convenience function for worker.py integration.
    
    Usage in worker.py:
        from alpha_mcp.worker_integration import handle_alpha_mcp_request
        
        # In telegram handler:
        if should_use_alpha_mcp(text):
            response = await handle_alpha_mcp_request(text, chat_id, user_name, env)
            await send_telegram_reply(env, chat_id, response)
    
    Args:
        message: The message text
        chat_id: Telegram chat ID
        user_name: User's display name
        env: Cloudflare Worker environment
        
    Returns:
        str: Formatted response for Telegram
    """
    integration = get_alpha_mcp_integration(env)
    return await integration.process_telegram_message(message, chat_id, user_name)


async def check_should_handle(message: str, env: Any) -> bool:
    """
    Check if AlphaMCP should handle this message.
    
    Args:
        message: The message text
        env: Cloudflare Worker environment
        
    Returns:
        bool: True if AlphaMCP should handle
    """
    integration = get_alpha_mcp_integration(env)
    return await integration.should_handle_message(message)
