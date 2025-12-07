import math

class LongTermBrain:
    """
    The 'Slow Brain' module for Swing/Position Trading.
    Focuses on Trend Confirmation, Macro Cycles, and Institutional Crosses.
    
    Upgraded with: RSI filter, ADX trend strength, Conservative Retest Entry.
    """

    # --- Configuration (Institutional Grade) ---
    VOLUME_SURGE_MULT = 1.2    # Volume must be 20% higher than 20-day avg
    RSI_PERIOD = 14
    ADX_PERIOD = 14
    ADX_THRESHOLD = 25         # ADX > 25 confirms strong trend
    RSI_OVERSOLD = 30
    RSI_NEUTRAL = 50
    RSI_OVERBOUGHT = 70

    def __init__(self, daily_data):
        """
        :param daily_data: List of dicts (OHLCV) on Daily/H4 timeframe.
        """
        self.data = daily_data

    # ==================================================
    # 📊 MOVING AVERAGE CALCULATIONS
    # ==================================================

    def calculate_sma(self, period):
        if len(self.data) < period:
            return None
        closes = [d['close'] for d in self.data[-period:]]
        return sum(closes) / period

    def calculate_ema(self, period):
        if len(self.data) < period:
            return None
        closes = [d['close'] for d in self.data]
        multiplier = 2 / (period + 1)
        ema = closes[0]
        for close in closes[1:]:
            ema = (close - ema) * multiplier + ema
        return ema

    # ==================================================
    # 📈 RSI CALCULATION (Momentum Filter)
    # ==================================================

    def calculate_rsi(self, period=None):
        """
        Relative Strength Index for momentum confirmation.
        RSI rising from <30 or above 50 confirms bullish signal.
        """
        period = period or self.RSI_PERIOD
        if len(self.data) < period + 1:
            return 50.0  # Neutral if insufficient data

        gains, losses = [], []
        for i in range(-period, 0):
            change = self.data[i]['close'] - self.data[i - 1]['close']
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    # ==================================================
    # 📐 ADX CALCULATION (Trend Strength)
    # ==================================================

    def calculate_adx(self, period=None):
        """
        Average Directional Index. ADX > 25 = Strong Trend.
        Returns: ADX value, +DI, -DI
        """
        period = period or self.ADX_PERIOD
        if len(self.data) < period * 2:
            return 0, 0, 0  # Insufficient data

        tr_list, plus_dm_list, minus_dm_list = [], [], []

        for i in range(-period * 2 + 1, 0):
            high = self.data[i]['high']
            low = self.data[i]['low']
            prev_high = self.data[i - 1]['high']
            prev_low = self.data[i - 1]['low']
            prev_close = self.data[i - 1]['close']

            # True Range
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_list.append(tr)

            # Directional Movement
            plus_dm = max(high - prev_high, 0) if (high - prev_high) > (prev_low - low) else 0
            minus_dm = max(prev_low - low, 0) if (prev_low - low) > (high - prev_high) else 0
            plus_dm_list.append(plus_dm)
            minus_dm_list.append(minus_dm)

        # Smoothed averages
        atr = sum(tr_list[-period:]) / period
        plus_di = (sum(plus_dm_list[-period:]) / atr) * 100 if atr > 0 else 0
        minus_di = (sum(minus_dm_list[-period:]) / atr) * 100 if atr > 0 else 0

        # DX and ADX
        di_sum = plus_di + minus_di
        dx = (abs(plus_di - minus_di) / di_sum) * 100 if di_sum > 0 else 0
        adx = dx  # Simplified (would normally smooth DX over period)

        return adx, plus_di, minus_di

    # ==================================================
    # 🎯 INSTITUTIONAL GOLDEN CROSS (Upgraded)
    # ==================================================

    def assess_golden_cross(self):
        """
        Institutional Golden Cross with Multi-Filter Confirmation:
        1. 50 EMA > 200 SMA (Trend Direction)
        2. Volume Surge > 1.2x average (Conviction)
        3. RSI > 50 or rising from oversold (Momentum)
        4. ADX > 25 (Trend Strength)
        """
        if len(self.data) < 200:
            return {"status": "insufficient_data", "signal": "NO_DATA"}

        ema50 = self.calculate_ema(50)
        sma200 = self.calculate_sma(200)
        rsi = self.calculate_rsi()
        adx, plus_di, minus_di = self.calculate_adx()

        is_golden = ema50 > sma200
        is_death = ema50 < sma200

        # Volume Filter
        last_vol = self.data[-1]['volume']
        avg_vol = sum(d['volume'] for d in self.data[-20:]) / 20
        vol_surge = last_vol > (avg_vol * self.VOLUME_SURGE_MULT)

        # RSI Filter
        rsi_bullish = rsi > self.RSI_NEUTRAL or rsi < self.RSI_OVERSOLD
        rsi_bearish = rsi < self.RSI_NEUTRAL or rsi > self.RSI_OVERBOUGHT

        # ADX Filter (Trend strength)
        strong_trend = adx > self.ADX_THRESHOLD

        # Algo Scoring for Signal Strength
        buy_score = 0
        sell_score = 0

        if is_golden:
            buy_score += 1
            if vol_surge:
                buy_score += 1
            if rsi_bullish:
                buy_score += 1
            if strong_trend and plus_di > minus_di:
                buy_score += 1

        if is_death:
            sell_score += 1
            if vol_surge:
                sell_score += 1
            if rsi_bearish:
                sell_score += 1
            if strong_trend and minus_di > plus_di:
                sell_score += 1

        # Determine Signal
        signal = "NEUTRAL"
        if buy_score >= 3:
            signal = "STRONG_GOLDEN_CROSS"
        elif buy_score >= 2:
            signal = "WEAK_GOLDEN_CROSS"
        elif sell_score >= 3:
            signal = "STRONG_DEATH_CROSS"
        elif sell_score >= 2:
            signal = "WEAK_DEATH_CROSS"

        return {
            "signal": signal,
            "ema50": ema50,
            "sma200": sma200,
            "rsi": rsi,
            "adx": adx,
            "plus_di": plus_di,
            "minus_di": minus_di,
            "vol_surge": vol_surge,
            "buy_score": buy_score,
            "sell_score": sell_score
        }

    # ==================================================
    # 🏦 CONSERVATIVE RETEST ENTRY
    # ==================================================

    def check_ema_retest(self):
        """
        Conservative Entry: Wait for price to retest 50 EMA after cross.
        Reduces drawdown by entering on pullback.
        """
        if len(self.data) < 55:
            return False

        ema50 = self.calculate_ema(50)
        current_close = self.data[-1]['close']

        # Check if price is within 1% of EMA50 (retest zone)
        retest_tolerance = ema50 * 0.01
        is_near_ema = abs(current_close - ema50) <= retest_tolerance

        return is_near_ema

    # ==================================================
    # 🧠 MASTER ANALYSIS FUNCTION
    # ==================================================

    def evaluate_market_health(self):
        """
        Synthesizes Long-Term view with all institutional filters.
        """
        cross_data = self.assess_golden_cross()
        ema_retest = self.check_ema_retest()

        recommendation = "HOLD"
        confidence = 50
        entry_type = "IMMEDIATE"

        signal = cross_data.get("signal", "NEUTRAL")

        if "STRONG_GOLDEN" in signal:
            if ema_retest:
                recommendation = "BUY_RETEST_ENTRY"
                confidence = 95
                entry_type = "CONSERVATIVE"
            else:
                recommendation = "BUY_LONG_TERM"
                confidence = 85
        elif "WEAK_GOLDEN" in signal:
            recommendation = "ACCUMULATE"
            confidence = 70
        elif "STRONG_DEATH" in signal:
            if ema_retest:
                recommendation = "SELL_RETEST_ENTRY"
                confidence = 95
                entry_type = "CONSERVATIVE"
            else:
                recommendation = "SELL_LONG_TERM"
                confidence = 85
        elif "WEAK_DEATH" in signal:
            recommendation = "REDUCE_EXPOSURE"
            confidence = 70

        return {
            "Action": recommendation,
            "Confidence": confidence,
            "EntryType": entry_type,
            "Technical": cross_data,
            "EMA_Retest": ema_retest
        }
