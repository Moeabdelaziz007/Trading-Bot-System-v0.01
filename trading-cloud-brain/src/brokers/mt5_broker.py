from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MT5Broker:
    """
    MT5 Broker integration for AlphaAxiom
    Connects to your MT5 bridge (Windows VPS or local)
    
    Supports: XM Global, Exness, ICM Capital, FXTM, etc.
    """
    
    def __init__(self, bridge_url: str, auth_token: str, broker_name: str = "XM Global"):
        self.bridge_url = bridge_url.rstrip('/')
        self.auth_token = auth_token
        self.broker_name = broker_name
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        logger.info(f"✅ MT5Broker initialized: {broker_name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if bridge is online and MT5 connected"""
        try:
            response = await self.client.get(f"{self.bridge_url}/api/v1/health")
            return response.json()
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "offline", "error": str(e)}
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get MT5 account information"""
        try:
            response = await self.client.post(f"{self.bridge_url}/api/v1/account/info")
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            raise
    
    async def get_live_price(self, symbol: str) -> Dict[str, Any]:
        """Get real-time price for symbol"""
        try:
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/market/price",
                json={"symbol": symbol}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get price for {symbol}: {e}")
            raise
    
    async def execute_trade(
        self,
        symbol: str,
        action: str,
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "AlphaAxiom"
    ) -> Dict[str, Any]:
        """Execute a trade on MT5"""
        try:
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/trade/execute",
                json={
                    "symbol": symbol,
                    "action": action,
                    "volume": volume,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "comment": comment
                }
            )
            result = response.json()
            
            if result.get('success'):
                logger.info(f"✅ Trade executed: {symbol} {action} {volume} lots")
            else:
                logger.error(f"❌ Trade failed: {result.get('comment')}")
            
            return result
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            raise
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get open positions"""
        try:
            payload = {}
            if symbol:
                payload["symbol"] = symbol
            
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/positions/list",
                json=payload
            )
            data = response.json()
            return data.get('positions', [])
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def close_position(self, ticket: int) -> Dict[str, Any]:
        """Close a specific position"""
        try:
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/positions/close",
                json={"ticket": ticket}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to close position {ticket}: {e}")
            raise
    
    async def modify_position(
        self,
        ticket: int,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict[str, Any]:
        """Modify position SL/TP"""
        try:
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/positions/modify",
                json={
                    "ticket": ticket,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit
                }
            )
            return response.json()
        except Exception as e:
            logger.error(f"Failed to modify position {ticket}: {e}")
            raise
    
    async def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "H1",
        bars_count: int = 100
    ) -> List[Dict[str, Any]]:
        """Get historical candlestick data"""
        try:
            response = await self.client.post(
                f"{self.bridge_url}/api/v1/market/history",
                json={
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "bars_count": bars_count
                }
            )
            data = response.json()
            return data.get('candles', [])
        except Exception as e:
            logger.error(f"Failed to get history for {symbol}: {e}")
            return []
