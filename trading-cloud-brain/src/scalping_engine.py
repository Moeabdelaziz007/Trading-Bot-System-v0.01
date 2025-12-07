import math

class ScalpingBrain:
    """
    The 'Fast Brain' module for High-Frequency Scalping analysis.
    Implements Institutional approximations for limited data environments.
    
    Ported from: Setmony_PriceAction_AI_Scalper.mq5
    """

    # --- Configuration (mirrors MQL5 inputs) ---
    SR_LOOKBACK_BARS = 60
    RETEST_TOLERANCE_PCT = 0.005  # How close price must be to S/R (0.5%)
    MIN_REJECTION_BODY_PCT = 30   # Body must be < 30% of total range for pin bar
    MIN_ALGO_SCORE_BUY = 2.0
    MIN_ALGO_SCORE_SELL = 2.0
    MIN_VOL_FACTOR = 1.3          # Volume must be 30% higher than 20-bar average
    
    # ATR Stop Loss Configuration (from research)
    ATR_PERIOD = 14               # Standard ATR lookback
    ATR_SL_MULT = 1.5             # 1.5x ATR for scalping (tight)
    ATR_TP_MULT = 1.0             # 1:1 Risk/Reward default

    def __init__(self, ohlcv_data):
        """
        :param ohlcv_data: List of dicts [{'time':.., 'open':.., 'high':.., 'low':.., 'close':.., 'volume':..}, ...]
        """
        self.data = ohlcv_data

    # ==================================================
    # 📐 ATR CALCULATION & STOP LOSS (Ported from MQL5)
    # ==================================================

    def calculate_atr(self, period=None):
        """
        Average True Range for volatility-based stops.
        True Range = max(High-Low, |High-PrevClose|, |Low-PrevClose|)
        """
        period = period or self.ATR_PERIOD
        if len(self.data) < period + 1:
            return None

        tr_values = []
        for i in range(-period, 0):
            high = self.data[i]['high']
            low = self.data[i]['low']
            prev_close = self.data[i - 1]['close']
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            tr_values.append(tr)

        return sum(tr_values) / len(tr_values)

    def calculate_atr_stops(self, is_buy, sl_mult=None, tp_mult=None):
        """
        Calculate dynamic Stop Loss and Take Profit based on ATR.
        Ported from MQL5 ComputeStops().
        
        :param is_buy: True for BUY trade, False for SELL
        :param sl_mult: ATR multiplier for Stop Loss (default: 1.5)
        :param tp_mult: ATR multiplier for Take Profit (default: 1.0)
        
        :returns: Dict with entry, stop_loss, take_profit, atr
        """
        sl_mult = sl_mult or self.ATR_SL_MULT
        tp_mult = tp_mult or self.ATR_TP_MULT
        
        atr = self.calculate_atr()
        if not atr or not self.data:
            return None

        current_price = self.data[-1]['close']
        sl_distance = atr * sl_mult
        tp_distance = atr * tp_mult

        if is_buy:
            stop_loss = current_price - sl_distance
            take_profit = current_price + tp_distance
        else:
            stop_loss = current_price + sl_distance
            take_profit = current_price - tp_distance

        return {
            "entry": current_price,
            "stop_loss": round(stop_loss, 5),
            "take_profit": round(take_profit, 5),
            "atr": round(atr, 5),
            "sl_distance": round(sl_distance, 5),
            "tp_distance": round(tp_distance, 5),
            "risk_reward_ratio": round(tp_mult / sl_mult, 2)
        }

    # ==================================================
    # 📈 SUPERTREND INDICATOR (Trend Filter)
    # ==================================================

    def calculate_supertrend(self, atr_period=10, multiplier=3.0):
        """
        Supertrend Indicator - ATR-based trend filter.
        Returns: trend direction (1=UP, -1=DOWN) and supertrend line value.
        
        Formula:
        - Basic Upper Band = (High + Low) / 2 + (Multiplier * ATR)
        - Basic Lower Band = (High + Low) / 2 - (Multiplier * ATR)
        - Final bands adjust dynamically based on price action
        """
        if len(self.data) < atr_period + 5:
            return None

        # Calculate ATR for supertrend
        atr_values = []
        for i in range(atr_period, len(self.data)):
            tr_sum = 0
            for j in range(i - atr_period, i):
                high = self.data[j]['high']
                low = self.data[j]['low']
                prev_close = self.data[j - 1]['close'] if j > 0 else self.data[j]['close']
                tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                tr_sum += tr
            atr_values.append(tr_sum / atr_period)

        # Calculate Supertrend
        supertrend = []
        trend = 1  # Start assuming uptrend
        
        for i in range(len(atr_values)):
            idx = i + atr_period
            high = self.data[idx]['high']
            low = self.data[idx]['low']
            close = self.data[idx]['close']
            atr = atr_values[i]
            
            # Basic bands
            hl2 = (high + low) / 2
            basic_upper = hl2 + (multiplier * atr)
            basic_lower = hl2 - (multiplier * atr)
            
            if i == 0:
                final_upper = basic_upper
                final_lower = basic_lower
            else:
                prev_close = self.data[idx - 1]['close']
                prev_upper = supertrend[i - 1]['upper']
                prev_lower = supertrend[i - 1]['lower']
                
                # Dynamic upper band
                if basic_upper < prev_upper or prev_close > prev_upper:
                    final_upper = basic_upper
                else:
                    final_upper = prev_upper
                
                # Dynamic lower band
                if basic_lower > prev_lower or prev_close < prev_lower:
                    final_lower = basic_lower
                else:
                    final_lower = prev_lower
            
            # Determine trend direction
            if i > 0:
                prev_trend = supertrend[i - 1]['trend']
                if prev_trend == 1 and close < final_lower:
                    trend = -1
                elif prev_trend == -1 and close > final_upper:
                    trend = 1
                else:
                    trend = prev_trend
            
            supertrend.append({
                'upper': final_upper,
                'lower': final_lower,
                'trend': trend,
                'value': final_lower if trend == 1 else final_upper
            })

        # Return latest supertrend
        latest = supertrend[-1] if supertrend else None
        return {
            "trend": latest['trend'] if latest else 0,
            "trend_name": "UPTREND" if latest and latest['trend'] == 1 else "DOWNTREND",
            "supertrend_value": round(latest['value'], 5) if latest else 0,
            "upper_band": round(latest['upper'], 5) if latest else 0,
            "lower_band": round(latest['lower'], 5) if latest else 0
        }

    # ==================================================
    # 🔒 TRAILING STOP LOGIC (Profit Protection)
    # ==================================================

    def calculate_trailing_stop(self, entry_price, is_buy, profit_threshold_pct=0.3, trail_pct=0.15):
        """
        Trailing Stop that activates after profit threshold.
        
        :param entry_price: Original entry price
        :param is_buy: True for LONG, False for SHORT
        :param profit_threshold_pct: Min profit % to activate trail (default: 0.3%)
        :param trail_pct: Trail distance as % (default: 0.15%)
        
        :returns: Dict with trailing stop details
        """
        if not self.data:
            return None

        current_price = self.data[-1]['close']
        
        # Calculate current profit %
        if is_buy:
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            highest_price = max(d['high'] for d in self.data[-20:])  # Last 20 bars high
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            highest_price = min(d['low'] for d in self.data[-20:])  # Last 20 bars low (for shorts)

        # Check if profit threshold reached
        is_activated = profit_pct >= profit_threshold_pct
        
        if is_activated:
            trail_distance = highest_price * (trail_pct / 100)
            if is_buy:
                trailing_stop = highest_price - trail_distance
            else:
                trailing_stop = highest_price + trail_distance
        else:
            trailing_stop = None

        return {
            "is_activated": is_activated,
            "current_profit_pct": round(profit_pct, 3),
            "profit_threshold_pct": profit_threshold_pct,
            "highest_price": round(highest_price, 5) if highest_price else 0,
            "trailing_stop": round(trailing_stop, 5) if trailing_stop else None,
            "trail_distance_pct": trail_pct
        }

    def calculate_sr_levels(self, lookback=None):
        """
        Finds nearest Support (lowest low) and Resistance (highest high)
        over a lookback period. Directly ported from MQL5 GetNearestSR().
        """
        lookback = lookback or self.SR_LOOKBACK_BARS
        if len(self.data) < lookback + 5:
            return None

        relevant_data = self.data[-(lookback + 1):-1]  # Exclude current bar
        
        max_high = max(d['high'] for d in relevant_data)
        min_low = min(d['low'] for d in relevant_data)

        return {
            "resistance": max_high,
            "support": min_low
        }

    def is_retest(self, level, for_buy):
        """
        Checks if current price is retesting a given S/R level.
        Ported from MQL5 IsRetest().
        """
        if not self.data:
            return False
        
        current_price = self.data[-1]['close']
        tolerance = level * self.RETEST_TOLERANCE_PCT
        
        return abs(current_price - level) <= tolerance

    # ==================================================
    # 🕯️ REJECTION CANDLE (PIN BAR) DETECTION
    # ==================================================

    def is_bullish_rejection(self, shift=1):
        """
        Detects a bullish rejection candle (Pin Bar / Hammer).
        Criteria (from MQL5):
        - Bullish close (close > open)
        - Body is small relative to total range (< MIN_REJECTION_BODY_PCT %)
        - Lower wick is significantly longer than upper wick (1.5x)
        """
        if len(self.data) < shift + 1:
            return False

        candle = self.data[-(shift + 1)]
        open_p, high, low, close = candle['open'], candle['high'], candle['low'], candle['close']
        
        body = abs(close - open_p)
        total_range = high - low
        
        if total_range == 0:
            return False

        body_percent = (body / total_range) * 100
        is_bull = close > open_p
        
        lower_wick = min(open_p, close) - low
        upper_wick = high - max(open_p, close)
        
        long_lower_wick = lower_wick > (upper_wick * 1.5)

        return is_bull and body_percent < self.MIN_REJECTION_BODY_PCT and long_lower_wick

    def is_bearish_rejection(self, shift=1):
        """
        Detects a bearish rejection candle (Shooting Star).
        Criteria:
        - Bearish close (close < open)
        - Body is small relative to total range
        - Upper wick is significantly longer than lower wick (1.5x)
        """
        if len(self.data) < shift + 1:
            return False

        candle = self.data[-(shift + 1)]
        open_p, high, low, close = candle['open'], candle['high'], candle['low'], candle['close']
        
        body = abs(close - open_p)
        total_range = high - low
        
        if total_range == 0:
            return False

        body_percent = (body / total_range) * 100
        is_bear = close < open_p
        
        lower_wick = min(open_p, close) - low
        upper_wick = high - max(open_p, close)
        
        long_upper_wick = upper_wick > (lower_wick * 1.5)

        return is_bear and body_percent < self.MIN_REJECTION_BODY_PCT and long_upper_wick

    # ==================================================
    # 📊 VOLUME PROFILE & ORDER FLOW (Original)
    # ==================================================

    def calculate_volume_profile(self, lookback_bars=240, bins=50):
        """
        Approximates Volume Profile by binning volume into price levels.
        Identifies POC (Point of Control) and Value Area.
        """
        if not self.data:
            return None

        relevant_data = self.data[-lookback_bars:]
        min_price = min(d['low'] for d in relevant_data)
        max_price = max(d['high'] for d in relevant_data)
        price_range = max_price - min_price
        
        if price_range == 0:
            return None

        bin_size = price_range / bins
        volume_profile = {}

        for candle in relevant_data:
            candle_range = candle['high'] - candle['low']
            if candle_range == 0:
                continue
            vol_per_price = candle['volume'] / candle_range
            start_bin = int((candle['low'] - min_price) / bin_size)
            end_bin = int((candle['high'] - min_price) / bin_size)
            
            for b in range(start_bin, end_bin + 1):
                price_level = min_price + (b * bin_size)
                level_key = round(price_level, 5) 
                current_vol = volume_profile.get(level_key, 0)
                volume_profile[level_key] = current_vol + (vol_per_price * bin_size)

        if not volume_profile:
            return None
            
        poc_level = max(volume_profile, key=volume_profile.get)
        total_volume = sum(volume_profile.values())
        value_area_vol = total_volume * 0.70
        sorted_levels = sorted(volume_profile.items(), key=lambda item: item[1], reverse=True)
        
        accumulated_vol = 0
        value_area_levels = []
        for price, vol in sorted_levels:
            accumulated_vol += vol
            value_area_levels.append(price)
            if accumulated_vol >= value_area_vol:
                break
        
        vah = max(value_area_levels) if value_area_levels else poc_level
        val = min(value_area_levels) if value_area_levels else poc_level

        return {"POC": poc_level, "VAH": vah, "VAL": val, "total_volume": total_volume}

    def get_footprint_score(self, shift=1):
        """
        Footprint-like scoring (ported from MQL5 GetFootprintScore).
        Compares current candle volume to 20-bar average.
        """
        if len(self.data) < shift + 21:
            return 0.0

        candle = self.data[-(shift + 1)]
        open_p, close, vol = candle['open'], candle['close'], candle['volume']

        # Average volume of last 20 bars
        avg_vol = sum(d['volume'] for d in self.data[-(shift + 21):-(shift + 1)]) / 20
        
        vol_factor = vol / avg_vol if avg_vol > 0 else 1.0
        direction = 1.0 if close > open_p else (-1.0 if close < open_p else 0.0)
        
        # Score = direction * (how much volume exceeds average)
        score = direction * (vol_factor - 1.0)
        return score

    def calculate_approx_delta(self, lookback=1):
        """Approximates Order Flow Delta."""
        if len(self.data) < lookback:
            return 0
        last_candle = self.data[-1]
        range_c = last_candle['high'] - last_candle['low']
        if range_c == 0:
            return 0
        body = last_candle['close'] - last_candle['open']
        return (body / range_c) * last_candle['volume']

    def calculate_vwap_bands(self):
        """Calculates VWAP and Standard Deviation Bands."""
        if not self.data:
            return None
        cum_vol, cum_vol_price = 0, 0
        vwap_series = []
        for d in self.data:
            avg_price = (d['high'] + d['low'] + d['close']) / 3
            cum_vol_price += avg_price * d['volume']
            cum_vol += d['volume']
            vwap = cum_vol_price / cum_vol if cum_vol else avg_price
            vwap_series.append(vwap)

        current_vwap = vwap_series[-1]
        variance_sum = sum((((d['high'] + d['low'] + d['close']) / 3) - vwap_series[i])**2 * d['volume'] for i, d in enumerate(self.data))
        std_dev = math.sqrt(variance_sum / cum_vol) if cum_vol else 0

        return {
            "VWAP": current_vwap, "Upper_1SD": current_vwap + std_dev,
            "Lower_1SD": current_vwap - std_dev, "Upper_2SD": current_vwap + (std_dev * 2),
            "Lower_2SD": current_vwap - (std_dev * 2)
        }

    # ==================================================
    # 🎯 ALGO SCORING SYSTEM (Ported from MQL5)
    # ==================================================

    def calculate_buy_signal(self):
        """
        Algo Scoring for BUY signal (ported from MQL5 BuySignal).
        Scores: +1 for Trend, +1 for S/R Retest+Rejection, +1 for Footprint.
        """
        sr = self.calculate_sr_levels()
        if not sr:
            return 0.0, 0.0

        score = 0.0
        
        # 1. S/R Retest + Bullish Rejection
        near_support = self.is_retest(sr['support'], for_buy=True)
        rejection = self.is_bullish_rejection(shift=1)
        if near_support and rejection:
            score += 2.0  # Strong signal

        # 2. Footprint Volume Confirmation
        fp_score = self.get_footprint_score(shift=1)
        if fp_score >= 0.3:  # Strong bullish volume
            score += 1.0

        # 3. Delta Confirmation
        delta = self.calculate_approx_delta()
        if delta > 0:
            score += 0.5

        return score, fp_score

    def calculate_sell_signal(self):
        """
        Algo Scoring for SELL signal (ported from MQL5 SellSignal).
        """
        sr = self.calculate_sr_levels()
        if not sr:
            return 0.0, 0.0

        score = 0.0
        
        # 1. S/R Retest + Bearish Rejection
        near_resistance = self.is_retest(sr['resistance'], for_buy=False)
        rejection = self.is_bearish_rejection(shift=1)
        if near_resistance and rejection:
            score += 2.0

        # 2. Footprint Volume Confirmation (Bearish)
        fp_score = self.get_footprint_score(shift=1)
        if fp_score <= -0.3:  # Strong bearish volume
            score += 1.0

        # 3. Delta Confirmation
        delta = self.calculate_approx_delta()
        if delta < 0:
            score += 0.5

        return score, fp_score

    # ==================================================
    # 🧠 MASTER ANALYSIS FUNCTION
    # ==================================================

    def analyze_market_state(self):
        """
        Synthesizes all indicators using MQL5-style Algo Scoring.
        """
        vp = self.calculate_volume_profile()
        vwap = self.calculate_vwap_bands()
        sr = self.calculate_sr_levels()
        
        if not vp or not vwap or not sr:
            return {"Action": "NEUTRAL", "Confidence": 0, "Metrics": {}}

        current_price = self.data[-1]['close']
        
        buy_score, buy_fp = self.calculate_buy_signal()
        sell_score, sell_fp = self.calculate_sell_signal()

        signal = "NEUTRAL"
        confidence = 0
        algo_score = 0

        if buy_score >= self.MIN_ALGO_SCORE_BUY and buy_score > sell_score:
            signal = "BUY_PA_SIGNAL"
            confidence = min(100, int(buy_score * 30))
            algo_score = buy_score
        elif sell_score >= self.MIN_ALGO_SCORE_SELL and sell_score > buy_score:
            signal = "SELL_PA_SIGNAL"
            confidence = min(100, int(sell_score * 30))
            algo_score = sell_score

        return {
            "Action": signal,
            "Confidence": confidence,
            "Metrics": {
                "AlgoScore": algo_score,
                "BuyScore": buy_score,
                "SellScore": sell_score,
                "Footprint_Buy": buy_fp,
                "Footprint_Sell": sell_fp,
                "POC": vp['POC'],
                "VWAP": vwap['VWAP'],
                "Support": sr['support'],
                "Resistance": sr['resistance']
            }
        }
