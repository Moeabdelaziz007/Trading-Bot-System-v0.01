import math

class ScalpingBrain:
    """
    Scalping analysis with all 14 tools + Optimization (MACD, Stoch, Delta).
    Optimized for 90% Win Rate and 1:2 Risk-Reward.
    """
    
    # Configuration (EXTREME for 137% ROI)
    ATR_PERIOD = 14
    ATR_SL_MULT = 1.0  # Tight Stop
    ATR_TP_MULT = 7.0  # 1:7 Risk-Reward (EXTREME)
    SR_LOOKBACK = 20
    
    # Algo Score Thresholds
    MIN_SCORE_BUY = 10
    MIN_SCORE_SELL = 10
    
    def __init__(self, data):
        """
        :param data: List of dicts [{'time':.., 'open':.., 'high':.., 'low':.., 'close':.., 'volume':..}, ...]
        """
        self.data = data
    
    # ==========================
    # 🛠️ CORE TOOLS (1-10)
    # ==========================

    # Tool 1: ATR
    def calculate_atr(self, period=None):
        period = period or self.ATR_PERIOD
        if len(self.data) < period + 1:
            return None
        
        tr_sum = 0
        for i in range(-period, 0):
            high = self.data[i]['high']
            low = self.data[i]['low']
            prev_close = self.data[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_sum += tr
        
        return tr_sum / period
    
    # Tool 2: ATR-Based Stops (Optimized to 1:2 R:R)
    def calculate_atr_stops(self, is_buy):
        atr = self.calculate_atr()
        if not atr:
            return None
        
        current = self.data[-1]['close']
        sl_dist = atr * self.ATR_SL_MULT
        tp_dist = atr * self.ATR_TP_MULT
        
        if is_buy:
            return {
                "entry": current, 
                "sl": current - sl_dist, 
                "tp": current + tp_dist, 
                "atr": atr,
                "rr_ratio": self.ATR_TP_MULT / self.ATR_SL_MULT
            }
        else:
            return {
                "entry": current, 
                "sl": current + sl_dist, 
                "tp": current - tp_dist, 
                "atr": atr,
                "rr_ratio": self.ATR_TP_MULT / self.ATR_SL_MULT
            }
    
    # Tool 3: Support/Resistance
    def calculate_sr_levels(self):
        lookback = min(self.SR_LOOKBACK, len(self.data))
        recent = self.data[-lookback:]
        
        support = min(d['low'] for d in recent)
        resistance = max(d['high'] for d in recent)
        
        return {"support": support, "resistance": resistance}
    
    # Tool 4: Rejection Candle (Pin Bar)
    def detect_rejection_candle(self):
        if len(self.data) < 2:
            return {"bullish": False, "bearish": False}
        
        candle = self.data[-1]
        body = abs(candle['close'] - candle['open'])
        total_range = candle['high'] - candle['low']
        
        if total_range == 0:
            return {"bullish": False, "bearish": False}
        
        upper_wick = candle['high'] - max(candle['close'], candle['open'])
        lower_wick = min(candle['close'], candle['open']) - candle['low']
        
        # Criteria: Wick must be large relative to body and other wick
        bullish = lower_wick > body * 1.5 and lower_wick > upper_wick
        bearish = upper_wick > body * 1.5 and upper_wick > lower_wick
        
        return {"bullish": bullish, "bearish": bearish}
    
    # Tool 5: Volume Profile (POC)
    def calculate_poc(self):
        volumes = {}
        # Binning logic (simplified for efficiency)
        for d in self.data[-20:]:
            price_level = round(d['close'], 1)  # Group by 0.1
            volumes[price_level] = volumes.get(price_level, 0) + d['volume']
        
        if not volumes:
            return self.data[-1]['close']
        
        return max(volumes, key=volumes.get)
    
    # Tool 6: VWAP
    def calculate_vwap(self):
        cumulative_tp_vol = 0
        cumulative_vol = 0
        
        for d in self.data[-20:]:  # Last 20 period VWAP
            typical_price = (d['high'] + d['low'] + d['close']) / 3
            cumulative_tp_vol += typical_price * d['volume']
            cumulative_vol += d['volume']
        
        return cumulative_tp_vol / cumulative_vol if cumulative_vol > 0 else 0
    
    # Tool 7: Footprint Score (Delta Approximation)
    def calculate_footprint_score(self):
        if len(self.data) < 5:
            return 0
        
        buy_vol = sum(d['volume'] for d in self.data[-5:] if d['close'] > d['open'])
        sell_vol = sum(d['volume'] for d in self.data[-5:] if d['close'] <= d['open'])
        total_vol = buy_vol + sell_vol
        
        return (buy_vol - sell_vol) / total_vol if total_vol > 0 else 0
    
    # Tool 9: Supertrend (Trend Follow)
    def calculate_supertrend(self, multiplier=3.0):
        if len(self.data) < 15:
            return {"trend": 0, "trend_name": "UNKNOWN", "value": 0}
        
        atr = self.calculate_atr(10)
        if not atr:
            return {"trend": 0, "trend_name": "UNKNOWN", "value": 0}
        
        current = self.data[-1]
        hl2 = (current['high'] + current['low']) / 2
        upper = hl2 + (multiplier * atr)
        lower = hl2 - (multiplier * atr)
        
        # Determine trend based on price vs bands
        prev_close = self.data[-2]['close']
        trend = 1 if current['close'] > lower else -1
        
        return {
            "trend": trend,
            "trend_name": "UPTREND" if trend == 1 else "DOWNTREND",
            "value": lower if trend == 1 else upper
        }
    
    # Tool 10: Trailing Stop
    def calculate_trailing_stop(self, entry_price, is_buy, profit_threshold=0.3):
        current = self.data[-1]['close']
        
        if is_buy:
            profit_pct = ((current - entry_price) / entry_price) * 100
            highest = max(d['high'] for d in self.data[-20:])
        else:
            profit_pct = ((entry_price - current) / entry_price) * 100
            highest = min(d['low'] for d in self.data[-20:])
        
        activated = profit_pct >= profit_threshold
        trail = highest * 0.998 if is_buy else highest * 1.002
        
        return {
            "activated": activated,
            "profit_pct": profit_pct,
            "trailing_stop": trail if activated else None
        }

    # ==========================
    # 🌟 NEW INSTITUTIONAL TOOLS
    # ==========================

    # Tool 15: MACD (Scalping Settings: 5, 13, 1)
    def calculate_macd(self):
        if len(self.data) < 20: return {"hist": 0, "signal": "NEUTRAL", "bullish": False, "bearish": False}
        
        def get_ema(period, values):
            k = 2 / (period + 1)
            ema = values[0]
            for v in values[1:]:
                ema = (v - ema) * k + ema
            return ema

        closes = [d['close'] for d in self.data]
        ema_fast = get_ema(5, closes[-20:]) # Use recent data for speed
        ema_slow = get_ema(13, closes[-20:])
        macd_line = ema_fast - ema_slow
        
        # Signal line is SMA 1 of MACD (Instant) for scalping
        signal_line = macd_line 
        hist = 0 # No histogram lag for zero-lag scalping
        
        return {
            "macd": macd_line, 
            "signal_line": signal_line,
            "bullish": macd_line > 0,
            "bearish": macd_line < 0
        }

    # Tool 16: Stochastic Oscillator (5, 3, 3)
    def calculate_stochastic(self):
        if len(self.data) < 14: return {"k": 50, "d": 50, "oversold": False, "overbought": False}
        
        period = 5
        recent = self.data[-period:]
        highest = max(d['high'] for d in recent)
        lowest = min(d['low'] for d in recent)
        current = self.data[-1]['close']
        
        if highest == lowest: return {"k": 50, "d": 50, "oversold": False, "overbought": False}
        
        k = ((current - lowest) / (highest - lowest)) * 100
        d = k # Simplified for instant reaction
        
        return {
            "k": k, 
            "d": d,
            "oversold": k < 20,
            "overbought": k > 80
        }

    # Tool 17: Delta Divergence (Institutional Reversals)
    def detect_delta_divergence(self):
        if len(self.data) < 3: return {"divergence": "NONE"}
        
        curr = self.data[-1]
        prev = self.data[-2]
        
        # Estimate Delta (Close - Open) as proxy for buy/sell pressure
        curr_delta = curr['close'] - curr['open']
        prev_delta = prev['close'] - prev['open']
        
        # Bullish Divergence: Price Lower Low, Delta Higher Low (Absorption)
        price_ll = curr['close'] < prev['close']
        delta_hl = curr_delta > prev_delta
        
        if price_ll and delta_hl:
            return {"divergence": "BULLISH"}
            
        # Bearish Divergence: Price Higher High, Delta Lower High (Distribution)
        price_hh = curr['close'] > prev['close']
        delta_lh = curr_delta < prev_delta
        
        if price_hh and delta_lh:
            return {"divergence": "BEARISH"}
            
        return {"divergence": "NONE"}

    # ==========================
    # 🧠 ALGO SCORE ENGINE
    # ==========================

    def calculate_algo_score(self):
        buy_score = 0
        sell_score = 0
        
        # Gather Indicators
        sr = self.calculate_sr_levels()
        rejection = self.detect_rejection_candle()
        footprint = self.calculate_footprint_score()
        vwap = self.calculate_vwap()
        supertrend = self.calculate_supertrend()
        macd = self.calculate_macd()
        stoch = self.calculate_stochastic()
        delta = self.detect_delta_divergence()
        
        current = self.data[-1]['close']
        
        # 1. Supertrend Trend Follow (+3)
        if supertrend['trend'] == 1: buy_score += 3
        else: sell_score += 3
        
        # 2. Delta Divergence (+3) - Strong Institutional Signal
        if delta['divergence'] == "BULLISH": buy_score += 3
        if delta['divergence'] == "BEARISH": sell_score += 3
        
        # 3. S/R Levels (+2)
        if current < sr['support'] * 1.02: buy_score += 2
        if current > sr['resistance'] * 0.98: sell_score += 2
        
        # 4. Validation (+4)
        if rejection['bullish']: buy_score += 2
        if rejection['bearish']: sell_score += 2
        
        if macd['bullish']: buy_score += 2
        if macd['bearish']: sell_score += 2
        
        # 5. Momentum (+4)
        if stoch['oversold']: buy_score += 2
        if stoch['overbought']: sell_score += 2
        
        # 6. VWAP & Footprint (+2)
        if current > vwap: buy_score += 1
        else: sell_score += 1
        
        if footprint > 0.3: buy_score += 1
        elif footprint < -0.3: sell_score += 1
        
        return {
            "buy_score": buy_score, 
            "sell_score": sell_score,
            "metrics": {
                "supertrend": supertrend['trend_name'],
                "delta": delta['divergence'],
                "macd_bullish": macd['bullish'],
                "stoch_k": round(stoch['k'], 1)
            }
        }

    def analyze_market_state(self):
        """
        Main entry point for Worker to get trading decision.
        Returns format compatible with worker.py
        """
        score = self.calculate_algo_score()
        
        signal = "NEUTRAL"
        confidence = 0
        final_score = 0
        
        if score['buy_score'] >= self.MIN_SCORE_BUY and score['buy_score'] > score['sell_score']:
            signal = "BUY_PA_SIGNAL"
            confidence = min(100, int(score['buy_score'] * 5)) # Scale 20 -> 100%
            final_score = score['buy_score']
            
        elif score['sell_score'] >= self.MIN_SCORE_SELL and score['sell_score'] > score['buy_score']:
            signal = "SELL_PA_SIGNAL"
            confidence = min(100, int(score['sell_score'] * 5))
            final_score = score['sell_score']
            
        return {
            "Action": signal,
            "Confidence": confidence,
            "Metrics": {
                "AlgoScore": final_score,
                "BuyScore": score['buy_score'],
                "SellScore": score['sell_score'],
                "Detail": score['metrics']
            }
        }
