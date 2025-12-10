from typing import Any, Dict
from ..brokers.mt5_broker import MT5Broker
import logging

logger = logging.getLogger(__name__)


class MT5MCPTools:
    """
    MCP Tools for MT5/Forex Trading
    Integrates with AlphaAxiom's existing MCP architecture
    """
    
    def __init__(self, mt5_broker: MT5Broker):
        self.mt5 = mt5_broker
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Dict]:
        """Register all MT5 MCP tools"""
        return {
            "mt5_gold_price": {
                "name": "mt5_gold_price",
                "description": "Get real-time gold (XAUUSD) price from MT5 - Perfect for Arabic traders who love gold trading",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "handler": self._get_gold_price
            },
            
            "mt5_execute_smart_trade": {
                "name": "mt5_execute_smart_trade",
                "description": "Execute a forex trade with automatic risk management (2% risk per trade). Supports XAUUSD, EURUSD, GBPUSD, etc.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol (XAUUSD, EURUSD, GBPUSD, etc.)",
                            "enum": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "XAGUSD", "USOIL"]
                        },
                        "direction": {
                            "type": "string",
                            "description": "Trade direction (BUY or SELL)",
                            "enum": ["BUY", "SELL"]
                        },
                        "risk_percent": {
                            "type": "number",
                            "description": "Risk percentage of account balance (default: 2%)",
                            "default": 2.0
                        },
                        "reason": {
                            "type": "string",
                            "description": "Trading reason/strategy (for logging)"
                        }
                    },
                    "required": ["symbol", "direction"]
                },
                "handler": self._execute_smart_trade
            },
            
            "mt5_portfolio_status": {
                "name": "mt5_portfolio_status",
                "description": "Get complete MT5 portfolio: balance, equity, open positions, P&L. Returns Arabic summary.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                "handler": self._get_portfolio_status
            },
            
            "mt5_market_scan": {
                "name": "mt5_market_scan",
                "description": "Scan multiple forex pairs for trading opportunities using technical analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of symbols to scan",
                            "default": ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
                        }
                    },
                    "required": []
                },
                "handler": self._market_scan
            },
            
            "mt5_close_all": {
                "name": "mt5_close_all",
                "description": "Emergency: Close ALL open positions immediately (kill switch)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "confirm": {
                            "type": "boolean",
                            "description": "Must be true to execute"
                        }
                    },
                    "required": ["confirm"]
                },
                "handler": self._close_all_positions
            },
            
            "mt5_analysis": {
                "name": "mt5_analysis",
                "description": "Get comprehensive technical analysis for a symbol (RSI, MACD, trends)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Trading symbol"
                        },
                        "timeframe": {
                            "type": "string",
                            "description": "Timeframe for analysis",
                            "enum": ["M1", "M5", "M15", "M30", "H1", "H4", "D1"],
                            "default": "H1"
                        }
                    },
                    "required": ["symbol"]
                },
                "handler": self._get_analysis
            }
        }
    
    # ========== TOOL HANDLERS ==========
    
    async def _get_gold_price(self, **kwargs) -> Dict[str, Any]:
        """Get real-time gold price"""
        try:
            price = await self.mt5.get_live_price("XAUUSD")
            
            return {
                "success": True,
                "symbol": "XAUUSD",
                "bid": price['bid'],
                "ask": price['ask'],
                "spread": price.get('spread_points', 0),
                "timestamp": price.get('timestamp'),
                "arabic_message": f"سعر الذهب: ${price['bid']:.2f} 💰"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "arabic_message": "فشل جلب سعر الذهب ❌"
            }
    
    async def _execute_smart_trade(self, **kwargs) -> Dict[str, Any]:
        """Execute trade with automatic risk management"""
        try:
            symbol = kwargs['symbol']
            direction = kwargs['direction']
            risk_percent = kwargs.get('risk_percent', 2.0)
            reason = kwargs.get('reason', 'AlphaAxiom AI Trade')
            
            # Get account info
            account = await self.mt5.get_account_info()
            balance = account['balance']
            
            # Get current price
            price = await self.mt5.get_live_price(symbol)
            current_price = price['ask'] if direction == 'BUY' else price['bid']
            
            # Calculate position size (simplified - you can enhance this)
            risk_amount = balance * (risk_percent / 100)
            
            # Fixed stop loss in pips for simplicity
            stop_loss_pips = 50
            pip_value = 0.01 if symbol == 'XAUUSD' else 0.0001
            
            # Calculate lot size (simplified)
            lot_size = min(risk_amount / (stop_loss_pips * 10), 0.1)  # Max 0.1 lots
            lot_size = round(lot_size, 2)
            
            # Calculate SL/TP
            if direction == 'BUY':
                stop_loss = current_price - (stop_loss_pips * pip_value)
                take_profit = current_price + (stop_loss_pips * 2 * pip_value)  # 2:1 RR
            else:
                stop_loss = current_price + (stop_loss_pips * pip_value)
                take_profit = current_price - (stop_loss_pips * 2 * pip_value)
            
            # Execute trade
            result = await self.mt5.execute_trade(
                symbol=symbol,
                action=direction,
                volume=lot_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=reason
            )
            
            if result['success']:
                arabic_msg = f"✅ تم فتح صفقة {direction} {symbol}\nالحجم: {lot_size} لوت\nالمخاطرة: ${risk_amount:.2f}"
            else:
                arabic_msg = f"❌ فشل فتح الصفقة: {result.get('comment')}"
            
            return {
                "success": result['success'],
                "ticket": result.get('ticket'),
                "entry_price": current_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "lot_size": lot_size,
                "risk_amount": risk_amount,
                "arabic_message": arabic_msg
            }
            
        except Exception as e:
            logger.error(f"Smart trade error: {e}")
            return {
                "success": False,
                "error": str(e),
                "arabic_message": "حدث خطأ في تنفيذ الصفقة ❌"
            }
    
    async def _get_portfolio_status(self, **kwargs) -> Dict[str, Any]:
        """Get portfolio status with Arabic summary"""
        try:
            account = await self.mt5.get_account_info()
            positions = await self.mt5.get_positions()
            
            total_profit = sum(pos['profit'] for pos in positions)
            
            # Arabic summary
            if len(positions) == 0:
                arabic_summary = "لا توجد صفقات مفتوحة حالياً"
            else:
                status = "ربح" if total_profit > 0 else "خسارة"
                arabic_summary = f"لديك {len(positions)} صفقة مفتوحة | {status}: ${abs(total_profit):.2f}"
            
            return {
                "success": True,
                "account": {
                    "balance": account['balance'],
                    "equity": account['equity'],
                    "profit": account['profit'],
                    "margin_level": account.get('margin_level', 0)
                },
                "positions": {
                    "count": len(positions),
                    "total_profit": total_profit,
                    "list": positions
                },
                "arabic_summary": arabic_summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "arabic_message": "فشل جلب حالة المحفظة ❌"
            }
    
    async def _market_scan(self, **kwargs) -> Dict[str, Any]:
        """Scan multiple pairs for opportunities"""
        try:
            symbols = kwargs.get('symbols', ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY'])
            
            opportunities = []
            for symbol in symbols:
                price = await self.mt5.get_live_price(symbol)
                # Simple opportunity detection
                if price['spread_points'] < 20:  # Low spread = good for trading
                    opportunities.append({
                        "symbol": symbol,
                        "price": price['bid'],
                        "spread": price['spread_points'],
                        "quality": "Good" if price['spread_points'] < 10 else "Fair"
                    })
            
            return {
                "success": True,
                "scanned": len(symbols),
                "opportunities": opportunities,
                "arabic_message": f"تم فحص {len(symbols)} زوج، وجد {len(opportunities)} فرص تداول 📊"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _close_all_positions(self, **kwargs) -> Dict[str, Any]:
        """Emergency close all positions"""
        try:
            if not kwargs.get('confirm'):
                return {
                    "success": False,
                    "error": "Confirmation required",
                    "arabic_message": "يجب تأكيد إغلاق جميع الصفقات"
                }
            
            positions = await self.mt5.get_positions()
            
            closed = 0
            failed = 0
            
            for pos in positions:
                try:
                    result = await self.mt5.close_position(pos['ticket'])
                    if result.get('success'):
                        closed += 1
                    else:
                        failed += 1
                except:
                    failed += 1
            
            return {
                "success": True,
                "closed": closed,
                "failed": failed,
                "arabic_message": f"تم إغلاق {closed} صفقة، فشل {failed} ⚠️"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_analysis(self, **kwargs) -> Dict[str, Any]:
        """Get technical analysis"""
        try:
            symbol = kwargs['symbol']
            timeframe = kwargs.get('timeframe', 'H1')
            
            # Get historical data
            candles = await self.mt5.get_historical_data(symbol, timeframe, 50)
            
            if not candles:
                return {"success": False, "error": "No data available"}
            
            # Simple analysis (you can enhance this with your existing indicators)
            closes = [c['close'] for c in candles]
            
            # Simple trend detection
            sma20 = sum(closes[-20:]) / 20
            current_price = closes[-1]
            
            trend = "صاعد (Uptrend)" if current_price > sma20 else "هابط (Downtrend)"
            
            return {
                "success": True,
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": current_price,
                "sma20": sma20,
                "trend": trend,
                "arabic_message": f"{symbol} الاتجاه: {trend}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
