"""
📊 Alpha Vantage Connector for AXIOM Trading System
Technical Indicators API Integration (RSI, MACD, ADX, ATR, etc.)

FREE TIER: 25 requests/day, 5 requests/minute
INDICATORS: 50+ technical indicators available

API Documentation: https://www.alphavantage.co/documentation/
"""

import json
from typing import Optional, Dict, List


class AlphaVantageConnector:
    """
    Alpha Vantage Technical Indicators Integration.
    
    Free Tier Limits:
    - 25 API requests/day
    - 5 API requests/minute
    
    Available Indicators:
    - RSI, MACD, ADX, ATR, EMA, SMA
    - Bollinger Bands, Stochastic
    - VWAP, OBV, MFI, CCI, Williams %R
    """
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self, api_key: str):
        """
        Initialize with Alpha Vantage API key.
        Get free key at: https://www.alphavantage.co/support/#api-key
        """
        self.api_key = api_key
        self.requests_today = 0
        self.max_daily_requests = 25
    
    def _can_request(self) -> bool:
        """Check if we have remaining daily quota."""
        return self.requests_today < self.max_daily_requests
    
    async def _fetch(self, params: dict) -> dict:
        """Make API request to Alpha Vantage."""
        from js import fetch
        
        if not self._can_request():
            return {"error": "Daily limit reached (25 requests)"}
        
        params["apikey"] = self.api_key
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{self.BASE_URL}?{query_string}"
        
        response = await fetch(url)
        self.requests_today += 1
        
        data = await response.json()
        
        # Check for API errors
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        if "Note" in data:
            return {"error": "Rate limit exceeded", "note": data["Note"]}
        
        return data
    
    # ==========================================
    # 📈 MOMENTUM INDICATORS
    # ==========================================
    
    async def get_rsi(
        self, 
        symbol: str, 
        interval: str = "5min",
        time_period: int = 14,
        series_type: str = "close"
    ) -> dict:
        """
        Get RSI (Relative Strength Index).
        
        Args:
            symbol: Stock/Forex symbol (e.g., "EURUSD", "AAPL")
            interval: 1min, 5min, 15min, 30min, 60min, daily
            time_period: RSI period (default 14)
            series_type: close, open, high, low
        
        Returns:
            dict: {symbol, interval, values: [{time, rsi}]}
        """
        data = await self._fetch({
            "function": "RSI",
            "symbol": symbol,
            "interval": interval,
            "time_period": str(time_period),
            "series_type": series_type
        })
        
        if "error" in data:
            return data
        
        # Parse response
        key = f"Technical Analysis: RSI"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:  # Last 50 values
            values.append({
                "time": time,
                "rsi": float(val["RSI"])
            })
        
        return {
            "symbol": symbol,
            "interval": interval,
            "indicator": "RSI",
            "period": time_period,
            "values": values,
            "latest": values[0] if values else None
        }
    
    async def get_macd(
        self,
        symbol: str,
        interval: str = "5min",
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> dict:
        """
        Get MACD (Moving Average Convergence Divergence).
        
        Returns:
            dict: {values: [{time, macd, signal, histogram}]}
        """
        data = await self._fetch({
            "function": "MACD",
            "symbol": symbol,
            "interval": interval,
            "series_type": "close",
            "fastperiod": str(fast_period),
            "slowperiod": str(slow_period),
            "signalperiod": str(signal_period)
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: MACD"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "macd": float(val["MACD"]),
                "signal": float(val["MACD_Signal"]),
                "histogram": float(val["MACD_Hist"])
            })
        
        return {
            "symbol": symbol,
            "interval": interval,
            "indicator": "MACD",
            "values": values,
            "latest": values[0] if values else None
        }
    
    async def get_stochastic(
        self,
        symbol: str,
        interval: str = "5min",
        fastkperiod: int = 5,
        slowkperiod: int = 3,
        slowdperiod: int = 3
    ) -> dict:
        """Get Stochastic Oscillator (K & D lines)."""
        data = await self._fetch({
            "function": "STOCH",
            "symbol": symbol,
            "interval": interval,
            "fastkperiod": str(fastkperiod),
            "slowkperiod": str(slowkperiod),
            "slowdperiod": str(slowdperiod)
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: STOCH"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "k": float(val["SlowK"]),
                "d": float(val["SlowD"])
            })
        
        return {
            "symbol": symbol,
            "indicator": "STOCH",
            "values": values,
            "latest": values[0] if values else None
        }
    
    # ==========================================
    # 📊 TREND INDICATORS
    # ==========================================
    
    async def get_adx(
        self,
        symbol: str,
        interval: str = "5min",
        time_period: int = 14
    ) -> dict:
        """
        Get ADX (Average Directional Index).
        Measures trend strength (>25 = strong trend).
        """
        data = await self._fetch({
            "function": "ADX",
            "symbol": symbol,
            "interval": interval,
            "time_period": str(time_period)
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: ADX"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "adx": float(val["ADX"])
            })
        
        return {
            "symbol": symbol,
            "indicator": "ADX",
            "period": time_period,
            "values": values,
            "latest": values[0] if values else None,
            "trend_strength": "STRONG" if values and values[0]["adx"] > 25 else "WEAK"
        }
    
    async def get_ema(
        self,
        symbol: str,
        interval: str = "5min",
        time_period: int = 21
    ) -> dict:
        """Get EMA (Exponential Moving Average)."""
        data = await self._fetch({
            "function": "EMA",
            "symbol": symbol,
            "interval": interval,
            "time_period": str(time_period),
            "series_type": "close"
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: EMA"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "ema": float(val["EMA"])
            })
        
        return {
            "symbol": symbol,
            "indicator": f"EMA{time_period}",
            "values": values,
            "latest": values[0] if values else None
        }
    
    # ==========================================
    # 📉 VOLATILITY INDICATORS
    # ==========================================
    
    async def get_atr(
        self,
        symbol: str,
        interval: str = "5min",
        time_period: int = 14
    ) -> dict:
        """
        Get ATR (Average True Range).
        Used for stop-loss and take-profit calculations.
        """
        data = await self._fetch({
            "function": "ATR",
            "symbol": symbol,
            "interval": interval,
            "time_period": str(time_period)
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: ATR"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "atr": float(val["ATR"])
            })
        
        return {
            "symbol": symbol,
            "indicator": "ATR",
            "period": time_period,
            "values": values,
            "latest": values[0] if values else None
        }
    
    async def get_bbands(
        self,
        symbol: str,
        interval: str = "5min",
        time_period: int = 20,
        nbdevup: int = 2,
        nbdevdn: int = 2
    ) -> dict:
        """
        Get Bollinger Bands.
        Returns upper, middle, lower bands.
        """
        data = await self._fetch({
            "function": "BBANDS",
            "symbol": symbol,
            "interval": interval,
            "time_period": str(time_period),
            "series_type": "close",
            "nbdevup": str(nbdevup),
            "nbdevdn": str(nbdevdn)
        })
        
        if "error" in data:
            return data
        
        key = "Technical Analysis: BBANDS"
        if key not in data:
            return {"error": "Invalid response format"}
        
        values = []
        for time, val in list(data[key].items())[:50]:
            values.append({
                "time": time,
                "upper": float(val["Real Upper Band"]),
                "middle": float(val["Real Middle Band"]),
                "lower": float(val["Real Lower Band"])
            })
        
        return {
            "symbol": symbol,
            "indicator": "BBANDS",
            "values": values,
            "latest": values[0] if values else None
        }
    
    # ==========================================
    # 🎯 COMPOSITE ANALYSIS
    # ==========================================
    
    async def get_scalping_signals(
        self,
        symbol: str,
        interval: str = "5min"
    ) -> dict:
        """
        Get all indicators needed for scalping in one call.
        Uses 2 API calls from daily quota.
        
        Returns:
            dict: Combined RSI + MACD analysis with signal recommendation
        """
        # Fetch RSI and MACD (uses 2 of 25 daily calls)
        rsi_data = await self.get_rsi(symbol, interval, 7)  # Fast RSI
        macd_data = await self.get_macd(symbol, interval)
        
        if "error" in rsi_data or "error" in macd_data:
            return {"error": "Failed to fetch indicators"}
        
        # Analyze signals
        rsi = rsi_data["latest"]["rsi"] if rsi_data.get("latest") else 50
        macd_hist = macd_data["latest"]["histogram"] if macd_data.get("latest") else 0
        
        signal = "NEUTRAL"
        confidence = 50
        
        # RSI oversold + MACD bullish = BUY
        if rsi < 30 and macd_hist > 0:
            signal = "STRONG_BUY"
            confidence = 85
        elif rsi < 40 and macd_hist > 0:
            signal = "BUY"
            confidence = 70
        # RSI overbought + MACD bearish = SELL
        elif rsi > 70 and macd_hist < 0:
            signal = "STRONG_SELL"
            confidence = 85
        elif rsi > 60 and macd_hist < 0:
            signal = "SELL"
            confidence = 70
        
        return {
            "symbol": symbol,
            "interval": interval,
            "signal": signal,
            "confidence": confidence,
            "indicators": {
                "rsi": rsi,
                "macd_histogram": macd_hist,
                "macd_line": macd_data["latest"]["macd"] if macd_data.get("latest") else 0,
                "macd_signal": macd_data["latest"]["signal"] if macd_data.get("latest") else 0
            },
            "requests_remaining": self.max_daily_requests - self.requests_today
        }
    
    def reset_daily_counter(self):
        """Reset daily request counter (call at midnight)."""
        self.requests_today = 0
    
    def get_status(self) -> dict:
        """Get current API usage status."""
        return {
            "requests_today": self.requests_today,
            "requests_remaining": self.max_daily_requests - self.requests_today,
            "max_daily": self.max_daily_requests
        }
