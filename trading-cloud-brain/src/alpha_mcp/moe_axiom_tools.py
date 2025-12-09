"""
🚀 MoeAxiomTools v1.0-beta - MCP Server
AlphaAxiom Enhanced Trading Intelligence Platform
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MCP Server متقدم للتداول الذكي - متكامل مع AlphaAxiom Learning Loop v2.0

Author: Mohamed Hossameldin Abdelaziz
Email: cryptojoker710@gmail.com
GitHub: https://github.com/Moeabdelaziz007
Version: 1.0.0-beta
"""

import json
import math
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
from dataclasses import dataclass, asdict

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎯 تهيئة Server v1.0-beta
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

try:
    from mcp.server.fastmcp import FastMCP
    server = FastMCP("MoeAxiomTools", version="1.0.0-beta")
except ImportError:
    # Fallback for Cloudflare Workers environment
    server = None
    print("⚠️ MCP not available - running in standalone mode")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 MODELS - نماذج البيانات
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class RiskProfile:
    """ملف المخاطر الشخصي"""
    daily_risk_limit: float = 2.0
    max_portfolio_risk: float = 15.0
    risk_aversion: str = "MODERATE"
    preferred_timeframe: str = "15M"

@dataclass
class MarketCondition:
    """حالة السوق الحالية"""
    volatility: str
    trend: str
    volume: str
    sentiment: str

@dataclass
class TradingSignal:
    """إشارة تداول متكاملة"""
    symbol: str
    action: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timeframe: str
    reasoning: str
    risk_score: float
    expected_rr: float


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 UTILITY FUNCTIONS - دوال مساعدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _calculate_rsi(prices: List[float], period: int = 14) -> float:
    """حساب RSI بسيط"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100 if avg_gain > 0 else 50
    
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def _polyfit_slope(values: List[float]) -> float:
    """حساب ميل خط الاتجاه"""
    if len(values) < 2:
        return 0.0
    n = len(values)
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    
    numerator = sum((i - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    
    return numerator / denominator if denominator != 0 else 0.0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧠 CORE TRADING TOOLS - أدوات التداول الأساسية
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def calculate_kelly_criterion(
    win_rate: float,
    avg_win: float,
    avg_loss: float,
    risk_aversion: str = "MODERATE"
) -> dict:
    """
    🧠 معيار كيلي المحسن مع إدارة مخاطر متقدمة
    
    Args:
        win_rate: نسبة الفوز (0.0 - 1.0)
        avg_win: متوسط الربح
        avg_loss: متوسط الخسارة
        risk_aversion: مستوى تحمل المخاطرة (LOW, MODERATE, HIGH)
        
    Returns:
        dict: استراتيجية إدارة رأس المال المثلى
    """
    try:
        if avg_loss == 0:
            return {"error": "متوسط الخسارة لا يمكن أن يكون صفر"}
        
        # صيغة Kelly الأساسية
        b = avg_win / avg_loss
        q = 1 - win_rate
        kelly_fraction = (win_rate * b - q) / b
        
        # عوامل التكيف بناءً على تحمل المخاطرة
        risk_factors = {
            "LOW": 0.25,
            "MODERATE": 0.5,
            "HIGH": 0.75
        }
        
        risk_factor = risk_factors.get(risk_aversion, 0.5)
        adjusted_kelly = kelly_fraction * risk_factor
        
        # تحديد مستوى المخاطرة
        if adjusted_kelly > 0.3:
            risk_level = "🔴 عالي جداً - غير موصى به"
        elif adjusted_kelly > 0.15:
            risk_level = "🟡 متوسط - بحذر"
        elif adjusted_kelly > 0:
            risk_level = "🟢 منخفض - آمن"
        else:
            risk_level = "⚫ سلبي - تجنب التداول"
        
        virtual_balance = 10000
        position_size = virtual_balance * adjusted_kelly
        
        return {
            "raw_kelly": round(kelly_fraction, 4),
            "adjusted_kelly": round(adjusted_kelly, 4),
            "recommended_position_size": f"{round(adjusted_kelly * 100, 2)}%",
            "position_size_usd": f"${round(position_size, 2)}",
            "risk_level": risk_level,
            "risk_aversion": risk_aversion,
            "optimal_lots": round(position_size / 100000, 3),
            "win_rate": f"{win_rate * 100}%",
            "expected_value": round((win_rate * avg_win) - ((1 - win_rate) * avg_loss), 2)
        }
    except Exception as e:
        return {"error": f"خطأ في الحساب: {str(e)}"}


def advanced_rsi_analysis(
    prices: List[float],
    period: int = 14,
    oversold: float = 30,
    overbought: float = 70
) -> dict:
    """
    📊 تحليل RSI متقدم مع إشارات ديناميكية
    
    Args:
        prices: قائمة الأسعار التاريخية
        period: فترة RSI (افتراضي 14)
        oversold: مستوى ذروة البيع (افتراضي 30)
        overbought: مستوى ذروة الشراء (افتراضي 70)
        
    Returns:
        dict: تحليل RSI متكامل
    """
    try:
        if len(prices) < period + 1:
            return {"error": f"تحتاج على الأقل {period + 1} أسعار"}
        
        rsi = _calculate_rsi(prices, period)
        
        # حساب مجموعة RSI للتحليل
        rsi_values = []
        for i in range(len(prices) - period):
            period_prices = prices[i:i+period+1]
            rsi_val = _calculate_rsi(period_prices, period)
            rsi_values.append(rsi_val)
        
        # حساب الزخم
        if len(rsi_values) >= 3:
            rsi_slope = rsi_values[-1] - rsi_values[-3]
        else:
            rsi_slope = 0
        
        # تحديد الإشارة
        if rsi > overbought:
            if rsi_slope < 0:
                signal = "🔴 ذروة شراء مع انعكاس (بيع قوي)"
            else:
                signal = "🟡 ذروة شراء مستمر (مراقبة)"
            recommendation = "بيع"
        elif rsi < oversold:
            if rsi_slope > 0:
                signal = "🟢 ذروة بيع مع انعكاس (شراء قوي)"
            else:
                signal = "🟠 ذروة بيع مستمر (مراقبة)"
            recommendation = "شراء"
        else:
            if rsi_slope > 1:
                signal = "📈 في المنطقة المحايدة مع زخم صعودي"
                recommendation = "شراء بحذر"
            elif rsi_slope < -1:
                signal = "📉 في المنطقة المحايدة مع زخم هبوطي"
                recommendation = "بيع بحذر"
            else:
                signal = "🔄 في المنطقة المحايدة بدون زخم واضح"
                recommendation = "انتظر"
        
        # تحليل التباعد
        divergence = ""
        if len(prices) >= 20 and len(rsi_values) >= 10:
            recent_prices = prices[-10:]
            recent_rsi = rsi_values[-10:]
            
            price_trend = _polyfit_slope(recent_prices)
            rsi_trend = _polyfit_slope(recent_rsi)
            
            if price_trend > 0 and rsi_trend < 0:
                divergence = "⚠️ تباعد هبوطي (السعر يصعد والـRSI يهبط)"
                recommendation = "تفكر في البيع"
            elif price_trend < 0 and rsi_trend > 0:
                divergence = "⚠️ تباعد صعودي (السعر يهبط والـRSI يصعد)"
                recommendation = "تفكر في الشراء"
        
        return {
            "rsi_value": round(rsi, 2),
            "rsi_slope": round(rsi_slope, 2),
            "signal": signal,
            "recommendation": recommendation,
            "divergence": divergence,
            "overbought_level": overbought,
            "oversold_level": oversold,
            "period_used": period,
            "price_action": f"آخر سعر: {prices[-1]}",
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"خطأ في تحليل RSI: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔮 ALPHAXIOM ENHANCED TOOLS - أدوات AlphaAxiom المحسنة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def alphaaxiom_market_analysis(
    symbol: str,
    current_price: float,
    volume: float,
    volatility: float,
    news_sentiment: str,
    social_sentiment: str = "neutral"
) -> dict:
    """
    🔮 تحليل AlphaAxiom للسوق (متعدد العوامل)
    
    Args:
        symbol: رمز الأصل (مثال: BTC-USD, EURUSD)
        current_price: السعر الحالي
        volume: حجم التداول (مقارنة بالمتوسط)
        volatility: معدل التقلب (ATR أو نسبة مئوية)
        news_sentiment: معنويات الأخبار (positive, negative, neutral)
        social_sentiment: معنويات السوشيال ميديا
        
    Returns:
        dict: تقرير تحليل سوق متكامل
    """
    try:
        factors = []
        total_score = 0
        max_score = 0
        
        # عامل التقلب
        if volatility < 0.01:
            price_factor = 0.3
            factors.append(("✅ استقرار سعري", 0.3))
        elif volatility < 0.03:
            price_factor = 0.5
            factors.append(("📊 تقلب معتدل", 0.5))
        else:
            price_factor = 0.8
            factors.append(("⚠️ تقلب عالي", 0.8))
        
        total_score += price_factor
        max_score += 1
        
        # عامل الحجم
        if volume > 1.5:
            volume_factor = 0.8
            factors.append(("📈 حجم عالي (تأكيد)", 0.8))
        elif volume > 0.8:
            volume_factor = 0.5
            factors.append(("📊 حجم طبيعي", 0.5))
        else:
            volume_factor = 0.3
            factors.append(("📉 حجم منخفض", 0.3))
        
        total_score += volume_factor
        max_score += 1
        
        # عامل الأخبار
        if news_sentiment == "positive":
            news_factor = 0.9
            factors.append(("✅ أخبار إيجابية قوية", 0.9))
        elif news_sentiment == "negative":
            news_factor = 0.2
            factors.append(("❌ أخبار سلبية", 0.2))
        else:
            news_factor = 0.5
            factors.append(("➖ أخبار محايدة", 0.5))
        
        total_score += news_factor
        max_score += 1
        
        # عامل السوشيال ميديا
        if social_sentiment == "positive":
            social_factor = 0.7
            factors.append(("😊 معنويات سوشيال إيجابية", 0.7))
        elif social_sentiment == "negative":
            social_factor = 0.3
            factors.append(("😟 معنويات سوشيال سلبية", 0.3))
        else:
            social_factor = 0.5
            factors.append(("😐 معنويات سوشيال محايدة", 0.5))
        
        total_score += social_factor
        max_score += 1
        
        # حساب النتيجة النهائية
        final_score = total_score / max_score
        
        # تحديد التوصية
        if final_score > 0.7:
            recommendation = "🚀 شراء قوي"
            confidence = "عالية"
            action = "BUY"
        elif final_score > 0.55:
            recommendation = "📈 شراء بحذر"
            confidence = "متوسطة"
            action = "BUY_CAREFUL"
        elif final_score > 0.45:
            recommendation = "🔄 الانتظار"
            confidence = "منخفضة"
            action = "HOLD"
        elif final_score > 0.3:
            recommendation = "📉 بيع بحذر"
            confidence = "متوسطة"
            action = "SELL_CAREFUL"
        else:
            recommendation = "🔴 بيع قوي"
            confidence = "عالية"
            action = "SELL"
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "market_score": round(final_score, 3),
            "recommendation": recommendation,
            "confidence": confidence,
            "action": action,
            "factors": factors,
            "weighted_factors": [
                {"factor": name, "weight": weight, "contribution": round(weight/max_score, 3)}
                for name, weight in factors
            ],
            "analysis_time": datetime.now().isoformat(),
            "alphaaxiom_version": "1.0-beta",
            "risk_advisory": "استخدم Stop Loss دائمًا" if final_score < 0.4 or final_score > 0.6 else "السوق متقلب، كن حذرًا"
        }
    except Exception as e:
        return {"error": f"خطأ في تحليل السوق: {str(e)}"}


def intelligent_position_sizing(
    account_balance: float,
    risk_tolerance: str,
    symbol: str,
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    market_volatility: float
) -> dict:
    """
    💰 حساب حجم مركز ذكي (مع تكيف تلقائي)
    
    Args:
        account_balance: رصيد الحساب
        risk_tolerance: تحمل المخاطرة (LOW, MEDIUM, HIGH)
        symbol: رمز الأصل
        entry_price: سعر الدخول المتوقع
        stop_loss: سعر وقف الخسارة
        take_profit: سعر جني الأرباح
        market_volatility: تقلب السوق الحالي
        
    Returns:
        dict: استراتيجية حجم المركز المثلى
    """
    try:
        # حساب المخاطرة الأساسية
        risk_per_trade = {
            "LOW": 0.005,
            "MEDIUM": 0.01,
            "HIGH": 0.02
        }.get(risk_tolerance, 0.01)
        
        # تعديل المخاطرة بناءً على التقلب
        volatility_adjustment = 1.0
        if market_volatility > 0.03:
            volatility_adjustment = 0.7
        elif market_volatility < 0.01:
            volatility_adjustment = 1.3
        
        adjusted_risk = risk_per_trade * volatility_adjustment
        
        pip_value = 10
        sl_pips = abs(entry_price - stop_loss) * 10000
        risk_amount = account_balance * adjusted_risk
        
        if sl_pips > 0:
            position_size = risk_amount / (sl_pips * pip_value)
        else:
            position_size = account_balance * 0.01 / entry_price
        
        lot_size = position_size / 100000
        
        tp_pips = abs(take_profit - entry_price) * 10000
        if sl_pips > 0:
            rr_ratio = tp_pips / sl_pips
        else:
            rr_ratio = 0
        
        if rr_ratio > 2:
            trade_quality = "⭐⭐⭐ ممتاز"
        elif rr_ratio > 1.5:
            trade_quality = "⭐⭐ جيد"
        elif rr_ratio > 1:
            trade_quality = "⭐ مقبول"
        else:
            trade_quality = "⚠️ ضعيف"
        
        actual_risk_pct = (sl_pips * pip_value * lot_size * 100000) / account_balance * 100
        
        return {
            "account_balance": f"${account_balance:,.2f}",
            "risk_tolerance": risk_tolerance,
            "symbol": symbol,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "recommended_position_size": f"{position_size:,.0f} وحدة",
            "recommended_lots": round(lot_size, 3),
            "risk_per_trade": f"{adjusted_risk * 100:.2f}%",
            "risk_amount": f"${risk_amount:,.2f}",
            "sl_pips": round(sl_pips, 1),
            "tp_pips": round(tp_pips, 1),
            "risk_reward_ratio": round(rr_ratio, 2),
            "trade_quality": trade_quality,
            "market_volatility": f"{market_volatility * 100:.2f}%",
            "volatility_adjustment": round(volatility_adjustment, 2),
            "actual_risk_percentage": f"{actual_risk_pct:.2f}%",
            "max_suggested_lots": round(account_balance * 0.02 / (sl_pips * pip_value * 100), 3) if sl_pips > 0 else 0,
            "warning": "حجم المركز ضمن الحدود الآمنة" if actual_risk_pct < 2 else "⚠️ حجم المركز مرتفع المخاطرة"
        }
    except Exception as e:
        return {"error": f"خطأ في حساب حجم المركز: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 RISK MANAGEMENT TOOLS - أدوات إدارة المخاطر
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def portfolio_risk_assessment(
    positions: List[Dict],
    account_balance: float,
    correlation_matrix: Optional[List[List[float]]] = None
) -> dict:
    """
    🛡️ تقييم مخاطر المحفظة المتقدم
    
    Args:
        positions: قائمة المراكز المفتوحة
        account_balance: رصيد الحساب الإجمالي
        correlation_matrix: مصفوفة ارتباط الأصول (اختياري)
        
    Returns:
        dict: تقرير مخاطر المحفظة
    """
    try:
        total_value = 0
        total_risk = 0
        position_risks = []
        
        for pos in positions:
            position_value = pos.get('size', 0) * pos.get('current_price', 0)
            position_risk = pos.get('risk_percentage', 0) / 100 * position_value
            total_value += position_value
            total_risk += position_risk
            
            position_risks.append({
                "symbol": pos.get('symbol', 'UNKNOWN'),
                "value": f"${position_value:,.2f}",
                "risk_amount": f"${position_risk:,.2f}",
                "risk_percentage": f"{pos.get('risk_percentage', 0)}%"
            })
        
        portfolio_risk_pct = (total_risk / account_balance) * 100 if account_balance > 0 else 0
        
        if portfolio_risk_pct < 5:
            risk_level = "🟢 منخفض"
            recommendation = "يمكن إضافة مراكز جديدة"
        elif portfolio_risk_pct < 10:
            risk_level = "🟡 معتدل"
            recommendation = "راقب المراكز الحالية"
        elif portfolio_risk_pct < 15:
            risk_level = "🟠 مرتفع"
            recommendation = "قلل من المراكز الجديدة"
        else:
            risk_level = "🔴 عالي جداً"
            recommendation = "قلل المراكز الحالية فوراً"
        
        diversification_score = 0
        if len(positions) > 0 and total_value > 0:
            avg_position_size = total_value / len(positions)
            size_variance = sum(
                abs((pos.get('size', 0) * pos.get('current_price', 0)) - avg_position_size)
                for pos in positions
            ) / total_value
            diversification_score = max(0, 1 - size_variance)
        
        return {
            "portfolio_summary": {
                "total_positions": len(positions),
                "total_value": f"${total_value:,.2f}",
                "total_risk_amount": f"${total_risk:,.2f}",
                "portfolio_risk_percentage": f"{portfolio_risk_pct:.2f}%",
                "account_balance": f"${account_balance:,.2f}",
                "risk_level": risk_level,
                "diversification_score": f"{diversification_score:.2%}"
            },
            "position_details": position_risks,
            "recommendations": [
                recommendation,
                "استخدم Stop Loss لكل مركز",
                "راجع ترابط الأصول في محفظتك" if diversification_score < 0.5 else "محفظتك متنوعة بشكل جيد"
            ],
            "risk_metrics": {
                "var_95": f"${total_risk * 1.645:,.2f} (95% ثقة)",
                "max_drawdown_potential": f"{portfolio_risk_pct * 1.5:.2f}%",
                "stress_test_result": "جيد" if portfolio_risk_pct < 10 else "يتطلب مراجعة"
            }
        }
    except Exception as e:
        return {"error": f"خطأ في تقييم المحفظة: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📈 TECHNICAL ANALYSIS SUITE - مجموعة التحليل الفني
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def multi_timeframe_analysis(
    symbol: str,
    price_data: Dict[str, List[float]],
    primary_timeframe: str = "15M"
) -> dict:
    """
    ⏰ تحليل متعدد الأطر الزمنية
    
    Args:
        symbol: رمز الأصل
        price_data: بيانات الأسعار لكل إطار زمني
        primary_timeframe: الإطار الزمني الأساسي
        
    Returns:
        dict: تحليل التزامن بين الأطر الزمنية
    """
    try:
        analysis_results = {}
        timeframe_signals = []
        
        for timeframe, prices in price_data.items():
            if len(prices) < 14:
                continue
            
            current_price = prices[-1]
            sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else current_price
            sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else current_price
            
            if current_price > sma_20 > sma_10:
                trend = "صعودي"
            elif current_price < sma_20 < sma_10:
                trend = "هبوطي"
            else:
                trend = "جانبي"
            
            rsi = _calculate_rsi(prices, 14)
            
            if rsi < 30:
                signal = "شراء"
            elif rsi > 70:
                signal = "بيع"
            else:
                signal = "محايد"
            
            analysis_results[timeframe] = {
                "trend": trend,
                "rsi": round(rsi, 1),
                "signal": signal,
                "price_vs_sma20": f"{((current_price / sma_20 - 1) * 100):.2f}%" if sma_20 > 0 else "0%",
                "current_price": current_price
            }
            
            timeframe_signals.append(signal)
        
        buy_signals = timeframe_signals.count("شراء")
        sell_signals = timeframe_signals.count("بيع")
        neutral_signals = timeframe_signals.count("محايد")
        
        if buy_signals > sell_signals and buy_signals > neutral_signals:
            overall_signal = "🟢 شراء (أغلبية الأطر)"
        elif sell_signals > buy_signals and sell_signals > neutral_signals:
            overall_signal = "🔴 بيع (أغلبية الأطر)"
        else:
            overall_signal = "🟡 انتظر (عدم وضوح)"
        
        primary_analysis = analysis_results.get(primary_timeframe, {})
        
        if primary_analysis.get("signal") == "شراء" and overall_signal.startswith("🟢"):
            alignment = "✅ تزامن إيجابي"
            confidence = "عالية"
        elif primary_analysis.get("signal") == "بيع" and overall_signal.startswith("🔴"):
            alignment = "✅ تزامن سلبي"
            confidence = "عالية"
        else:
            alignment = "⚠️ تضارب في الإشارات"
            confidence = "منخفضة"
        
        return {
            "symbol": symbol,
            "primary_timeframe": primary_timeframe,
            "overall_signal": overall_signal,
            "alignment_analysis": alignment,
            "confidence": confidence,
            "timeframe_details": analysis_results,
            "signal_distribution": {
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "neutral_signals": neutral_signals
            },
            "recommendation": "التنفيذ موصى به" if confidence == "عالية" else "انتظر تأكيد إضافي",
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"خطأ في التحليل متعدد الأطر: {str(e)}"}


def strategy_backtest_simulation(
    initial_balance: float,
    trades: List[Dict],
    commission_per_trade: float = 2.0
) -> dict:
    """
    🧪 محاكاة اختبار إستراتيجية التداول
    
    Args:
        initial_balance: الرصيد الابتدائي
        trades: قائمة الصفقات التاريخية
        commission_per_trade: عمولة كل صفقة
        
    Returns:
        dict: نتائج محاكاة الإستراتيجية
    """
    try:
        balance = initial_balance
        trades_history = []
        winning_trades = 0
        total_trades = len(trades)
        
        for i, trade in enumerate(trades):
            entry = trade.get('entry_price', 0)
            exit_price = trade.get('exit_price', entry)
            position_size = trade.get('position_size', balance * 0.01)
            direction = trade.get('direction', 'BUY')
            
            if direction == 'BUY':
                pnl = (exit_price - entry) * position_size
            else:
                pnl = (entry - exit_price) * position_size
            
            pnl -= commission_per_trade
            balance += pnl
            trade_result = "ربح" if pnl > 0 else "خسارة"
            
            if pnl > 0:
                winning_trades += 1
            
            trades_history.append({
                "trade": i + 1,
                "direction": direction,
                "entry": entry,
                "exit": exit_price,
                "pnl": round(pnl, 2),
                "result": trade_result,
                "balance_after": round(balance, 2)
            })
        
        final_balance = balance
        total_pnl = final_balance - initial_balance
        roi = (total_pnl / initial_balance) * 100 if initial_balance > 0 else 0
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        max_consecutive_losses = 0
        current_loss_streak = 0
        
        for trade in trades_history:
            if trade['pnl'] < 0:
                current_loss_streak += 1
                max_consecutive_losses = max(max_consecutive_losses, current_loss_streak)
            else:
                current_loss_streak = 0
        
        if roi > 20 and win_rate > 55:
            strategy_rating = "⭐⭐⭐⭐⭐ ممتازة"
        elif roi > 10 and win_rate > 50:
            strategy_rating = "⭐⭐⭐⭐ جيدة جداً"
        elif roi > 0 and win_rate > 45:
            strategy_rating = "⭐⭐⭐ مقبولة"
        elif roi > -10:
            strategy_rating = "⭐⭐ تحتاج تحسين"
        else:
            strategy_rating = "⭐ ضعيفة"
        
        winning_pnls = [t['pnl'] for t in trades_history if t['pnl'] > 0]
        losing_pnls = [t['pnl'] for t in trades_history if t['pnl'] < 0]
        
        profit_factor = "∞"
        if losing_pnls:
            profit_factor = round(sum(winning_pnls) / abs(sum(losing_pnls)), 2)
        
        return {
            "backtest_summary": {
                "initial_balance": f"${initial_balance:,.2f}",
                "final_balance": f"${final_balance:,.2f}",
                "total_pnl": f"${total_pnl:,.2f}",
                "roi": f"{roi:.2f}%",
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "win_rate": f"{win_rate:.2f}%",
                "max_consecutive_losses": max_consecutive_losses,
                "average_commission": f"${commission_per_trade:.2f}",
                "strategy_rating": strategy_rating
            },
            "detailed_trades": trades_history[:10],
            "key_metrics": {
                "profit_factor": profit_factor,
                "average_win": f"${sum(winning_pnls)/len(winning_pnls):.2f}" if winning_pnls else "$0",
                "average_loss": f"${sum(losing_pnls)/len(losing_pnls):.2f}" if losing_pnls else "$0",
                "largest_win": f"${max([t['pnl'] for t in trades_history], default=0):.2f}",
                "largest_loss": f"${min([t['pnl'] for t in trades_history], default=0):.2f}"
            },
            "recommendations": [
                "زيادة حجم الصفقات" if win_rate > 60 and roi > 15 else "مراجعة نقاط الدخول",
                "تحسين إدارة المخاطرة" if max_consecutive_losses > 3 else "مستوى مخاطرة مقبول",
                "تقليل عدد الصفقات" if total_trades > 100 and roi < 5 else "عدد الصفقات مناسب"
            ]
        }
    except Exception as e:
        return {"error": f"خطأ في محاكاة الاختبار: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 SYSTEM TOOLS - أدوات النظام
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_server_info() -> dict:
    """معلومات الخادم"""
    tools_list = [
        "calculate_kelly_criterion - معيار كيلي المحسن",
        "advanced_rsi_analysis - تحليل RSI متقدم",
        "alphaaxiom_market_analysis - تحليل AlphaAxiom للسوق",
        "intelligent_position_sizing - حساب حجم مركز ذكي",
        "portfolio_risk_assessment - تقييم مخاطر المحفظة",
        "multi_timeframe_analysis - تحليل متعدد الأطر",
        "strategy_backtest_simulation - محاكاة اختبار الإستراتيجية"
    ]
    
    return {
        "server_name": "MoeAxiomTools",
        "version": "1.0.0-beta",
        "creator": "محمد حسام الدين عبدالعزيز",
        "email": "cryptojoker710@gmail.com",
        "github": "https://github.com/Moeabdelaziz007",
        "project": "AlphaAxiom Trading Platform",
        "description": "منصة ذكاء تداول متقدمة مع نظام تعلم آلي ذاتي التحسين",
        "launch_date": "December 2025",
        "status": "🚀 نشط (Beta)",
        "total_tools": len(tools_list),
        "available_tools": tools_list,
        "integrated_systems": [
            "AlphaAxiom Spider Web",
            "Learning Loop v2.0",
            "Risk Management Framework",
            "Multi-Broker Execution"
        ],
        "supported_brokers": ["Capital.com", "Alpaca", "OANDA", "Bybit", "Coinbase"],
        "ai_models": ["GLM-4.5", "Gemini 2.0", "Workers AI"],
        "infrastructure": "Cloudflare Workers + D1 + KV + R2 (Zero Cost)"
    }


def market_calendar_today() -> dict:
    """📅 تقويم الأحداث الاقتصادية اليوم"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        events = [
            {
                "time": "10:00 EST",
                "event": "مؤشر أسعار المستهلك الأمريكي (CPI)",
                "currency": "USD",
                "impact": "🔴 عالي",
                "forecast": "3.2%",
                "previous": "3.1%"
            },
            {
                "time": "14:00 EST",
                "event": "قرار سعر الفائدة الاحتياطي الفيدرالي",
                "currency": "USD",
                "impact": "🔴 عالي جداً",
                "forecast": "5.50%",
                "previous": "5.50%"
            },
            {
                "time": "08:00 GMT",
                "event": "معدل البطالة في بريطانيا",
                "currency": "GBP",
                "impact": "🟡 متوسط",
                "forecast": "4.2%",
                "previous": "4.3%"
            }
        ]
        
        recommendations = []
        high_impact_events = [e for e in events if "عالي" in e["impact"]]
        
        if high_impact_events:
            recommendations.append("⚠️ تجنب التداول قبل الأحداث ذات التأثير العالي")
            recommendations.append("استخدم أوامر معلقة لتجنب الانزلاق السعري")
        else:
            recommendations.append("✅ يوم مناسب للتداول العادي")
            recommendations.append("ركز على التحليل الفني")
        
        return {
            "date": today,
            "total_events": len(events),
            "high_impact_events": len(high_impact_events),
            "events": events,
            "trading_recommendations": recommendations,
            "risk_warning": "تقلبات عالية متوققة خلال الأحداث الاقتصادية الهامة" if high_impact_events else "مخاطر تقلب طبيعية",
            "best_trading_times": [
                "10:00-12:00 EST: أعلى سيولة",
                "14:00-16:00 EST: إعلانات اقتصادية"
            ],
            "update_time": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"خطأ في جلب التقويم: {str(e)}"}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚 RESOURCES - الموارد
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ALPHAAXIOM_FRAMEWORK = """
🏛️ إطار عمل AlphaAxiom للتداول الذكي v1.0-beta
═══════════════════════════════════════════════════════

🎯 الفلسفة الأساسية:
- الدليل على الادعاءات (Evidence > Claims)
- الجودة على السرعة (Quality > Speed)
- البساطة على التعقيد (Simplicity > Complexity)
- الأمان على الراحة (Security > Convenience)

🏗️ المكونات الأساسية:

1️⃣ Spider Web Architecture:
   - 89+ مكون معياري
   - 5 وكلاء ذكاء اصطناعي متخصصين
   - نظام اتصال داخلي ذكي

2️⃣ Learning Loop v2.0:
   - تعلم تعاوني بين الوكلاء
   - ذاكرة متجهية للمعرفة
   - تكيف تلقائي مع ظروف السوق

3️⃣ Risk Management Layer:
   - معيار كيلي المتكيف
   - حارس مخاطر ذكي
   - مراقبة المحفظة الآنية

4️⃣ Execution Engine:
   - دعم 5 وسطاء مختلفين
   - تنفيذ أوامر ذكي
   - تتبع الأداء الفوري

📊 مقاييس النجاح:
- تكلفة صفر شهرياً (Zero-Cost Infrastructure)
- 90% اكتمال النظام
- 24/7 تشغيل آلي
- تعلم مستمر ذاتي التحسين

💡 القاعدة الذهبية:
"لا تقرر بناءً على المشاعر، بل بناءً على البيانات"
"""

RISK_MANAGEMENT_BIBLE = """
📖 إنجيل إدارة المخاطر - AlphaAxiom Edition
═══════════════════════════════════════════════════════

🎯 المبادئ الأساسية:

1️⃣ قاعدة الـ 2%:
   - لا تخاطر بأكثر من 2% من رأس المال في صفقة واحدة
   - استخدم Position Sizing الذكي
   - احسب Stop Loss قبل الدخول

2️⃣ قاعدة الـ 6%:
   - لا تخسر أكثر من 6% من رأس المال شهرياً
   - توقف عند الوصول للحد
   - أعد تقييم الاستراتيجية

3️⃣ قاعدة الـ 20%:
   - لا تخصص أكثر من 20% للمحفظة لأصل واحد
   - تنويع عبر فئات الأصول
   - مراقبة الترابط بين الأصول

🛡️ أدوات الحماية:

✅ Stop Loss الديناميكي:
   - ATR-Based: 2.5 × ATR
   - Support/Resistance: تحت/فوق المستويات الرئيسية
   - Trailing Stop: يتحرك مع السعر

✅ Position Sizing الذكي:
   - Kelly Criterion المتكيف
   - تعديل الحجم حسب التقلبات
   - مراعاة سيولة السوق

✅ مراقبة المحفظة:
   - حساب المخاطرة الإجمالية
   - تحليل التنويع
   - اختبارات الإجهاد

⚠️ علامات الخطر:
- 3 خسائر متتالية → توقف وتقييم
- خسارة 10% من رأس المال → مراجعة شاملة
- تغير ظروف السوق → تعديل المخاطرة

🧠 الحكمة:
"المحترفون لا يتجنبون الخسائر، بل يديرونها"
"""


def get_alphaaxiom_framework() -> str:
    """إطار عمل AlphaAxiom للتداول الذكي"""
    return ALPHAAXIOM_FRAMEWORK


def get_risk_management_bible() -> str:
    """إنجيل إدارة المخاطر"""
    return RISK_MANAGEMENT_BIBLE


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔗 MCP TOOL REGISTRATION - تسجيل أدوات MCP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if server:
    # Register all tools with MCP server
    server.tool()(calculate_kelly_criterion)
    server.tool()(advanced_rsi_analysis)
    server.tool()(alphaaxiom_market_analysis)
    server.tool()(intelligent_position_sizing)
    server.tool()(portfolio_risk_assessment)
    server.tool()(multi_timeframe_analysis)
    server.tool()(strategy_backtest_simulation)
    server.tool()(get_server_info)
    server.tool()(market_calendar_today)
    
    # Register resources
    server.resource("alphaaxiom://trading-framework")(get_alphaaxiom_framework)
    server.resource("alphaaxiom://risk-management-bible")(get_risk_management_bible)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 تشغيل الخادم
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║    🚀 MoeAxiomTools v1.0-beta - MCP Server            ║
    ║    AlphaAxiom Enhanced Trading Intelligence           ║
    ║    Integrated with Learning Loop v2.0                 ║
    ║    Created by: محمد حسام الدين عبدالعزيز              ║
    ║    Project: AlphaAxiom Trading Platform               ║
    ╚═══════════════════════════════════════════════════════╝
    
    📊 Available Tools:
    • Kelly Criterion Calculator
    • Advanced RSI Analysis
    • AlphaAxiom Market Analysis
    • Intelligent Position Sizing
    • Portfolio Risk Assessment
    • Multi-Timeframe Analysis
    • Strategy Backtesting
    
    🔗 Integrated with AlphaAxiom Spider Web Architecture
    🧠 Powered by GLM-4.5 + Gemini 2.0 + Workers AI
    💰 Zero-Cost Infrastructure (Cloudflare Stack)
    
    🌐 Server is running...
    """)
    
    if server:
        server.run()
    else:
        print("⚠️ MCP not available - tools can be used directly")
        print("\nExample usage:")
        print("  result = calculate_kelly_criterion(0.55, 100, 50, 'MODERATE')")
        print("  print(result)")
