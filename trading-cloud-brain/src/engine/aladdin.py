"""
🛡️ Aladdin Risk Engine - Correlation-Aware Risk Management
============================================================
Inspired by BlackRock's Aladdin system. 

Features:
    - Real-time Correlation Matrix calculation
    - Dynamic risk adjustment based on portfolio exposure
    - Hard limits enforcement (max drawdown, max exposure)
    - Correlated asset detection and risk reduction

Principle: "Never double down on correlated risk."
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Result of risk evaluation for a trade."""
    approved: bool
    original_size: float
    adjusted_size: float
    risk_score: float  # 0-1, higher = more risky
    reason: str
    correlations: Dict[str, float]  # Symbol -> correlation coefficient


class AladdinRiskEngine:
    """
    Portfolio Risk Engine with Correlation Management.
    
    Monitors portfolio exposure and prevents concentrated risk
    in correlated assets (e.g., Gold & BTC during USD strengthening).
    
    Core Rules:
        1. Max risk per trade: configurable (default 2%)
        2. Max portfolio risk: configurable (default 10%)
        3. Correlation threshold: if two assets are >80% correlated,
           reduce exposure on the newer position by 50%
    """
    
    # Known correlation groups (pre-calculated for speed)
    CORRELATION_GROUPS = {
        'safe_haven': ['XAUUSD', 'XAGUSD', 'BTCUSD', 'BTCUSDT'],
        'risk_on': ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD'],
        'usd_strength': ['USDJPY', 'USDCHF', 'USDCAD'],
        'crypto': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT'],
    }
    
    def __init__(
        self,
        max_risk_per_trade: float = 0.02,  # 2%
        max_portfolio_risk: float = 0.10,   # 10%
        correlation_threshold: float = 0.80,
        correlation_lookback: int = 30  # Days for correlation calc
    ):
        """
        Initialize Aladdin Risk Engine.
        
        Args:
            max_risk_per_trade: Maximum risk per single trade (fraction)
            max_portfolio_risk: Maximum total portfolio risk (fraction)
            correlation_threshold: Threshold above which to reduce exposure
            correlation_lookback: Number of periods for correlation calculation
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_portfolio_risk = max_portfolio_risk
        self.correlation_threshold = correlation_threshold
        self.correlation_lookback = correlation_lookback
        
        # Cache for price history (symbol -> list of closes)
        self._price_cache: Dict[str, List[float]] = {}
        self._correlation_matrix: Dict[Tuple[str, str], float] = {}
        
        logger.info(f"🛡️ Aladdin Risk Engine initialized (max_risk={max_risk_per_trade*100}%)")
    
    def update_price(self, symbol: str, price: float) -> None:
        """
        Update price cache for correlation calculation.
        
        Should be called periodically (e.g., every candle close).
        """
        if symbol not in self._price_cache:
            self._price_cache[symbol] = []
        
        self._price_cache[symbol].append(price)
        
        # Keep only lookback period
        if len(self._price_cache[symbol]) > self.correlation_lookback * 2:
            self._price_cache[symbol] = self._price_cache[symbol][-self.correlation_lookback:]
    
    def calculate_correlation(
        self,
        symbol_a: str,
        symbol_b: str
    ) -> float:
        """
        Calculate Pearson correlation between two assets.
        
        Returns:
            Correlation coefficient (-1 to 1)
            Returns 0 if insufficient data
        """
        if symbol_a not in self._price_cache or symbol_b not in self._price_cache:
            return 0.0
        
        prices_a = np.array(self._price_cache[symbol_a])
        prices_b = np.array(self._price_cache[symbol_b])
        
        # Align lengths
        min_len = min(len(prices_a), len(prices_b), self.correlation_lookback)
        if min_len < 5:  # Need at least 5 data points
            return 0.0
        
        prices_a = prices_a[-min_len:]
        prices_b = prices_b[-min_len:]
        
        # Calculate returns
        returns_a = np.diff(prices_a) / prices_a[:-1]
        returns_b = np.diff(prices_b) / prices_b[:-1]
        
        # Pearson correlation
        if len(returns_a) < 2:
            return 0.0
        
        correlation = np.corrcoef(returns_a, returns_b)[0, 1]
        
        # Handle NaN
        if np.isnan(correlation):
            return 0.0
        
        # Cache result
        self._correlation_matrix[(symbol_a, symbol_b)] = correlation
        
        return correlation
    
    def get_correlation_matrix(self) -> Dict[Tuple[str, str], float]:
        """Get the current correlation matrix."""
        return self._correlation_matrix.copy()
    
    def find_correlated_assets(
        self,
        symbol: str,
        current_positions: List[str]
    ) -> Dict[str, float]:
        """
        Find which current positions are correlated with a new symbol.
        
        Args:
            symbol: New symbol to trade
            current_positions: List of symbols currently held
        
        Returns:
            Dict of {position_symbol: correlation_coefficient}
        """
        correlations = {}
        
        for pos_symbol in current_positions:
            if pos_symbol == symbol:
                continue
            
            corr = self.calculate_correlation(symbol, pos_symbol)
            
            # Also check known groups (fast path)
            if abs(corr) < self.correlation_threshold:
                corr = self._check_group_correlation(symbol, pos_symbol)
            
            if abs(corr) >= self.correlation_threshold:
                correlations[pos_symbol] = corr
        
        return correlations
    
    def _check_group_correlation(
        self,
        symbol_a: str,
        symbol_b: str
    ) -> float:
        """
        Check if two symbols belong to the same correlation group.
        Returns 0.85 if same group, 0.0 otherwise.
        """
        for group_name, symbols in self.CORRELATION_GROUPS.items():
            # Normalize symbols
            norm_a = symbol_a.upper().replace('.', '')
            norm_b = symbol_b.upper().replace('.', '')
            
            in_group_a = any(norm_a.startswith(s) or s.startswith(norm_a) for s in symbols)
            in_group_b = any(norm_b.startswith(s) or s.startswith(norm_b) for s in symbols)
            
            if in_group_a and in_group_b:
                logger.debug(f"🔗 {symbol_a} & {symbol_b} in same group: {group_name}")
                return 0.85
        
        return 0.0
    
    def evaluate_trade(
        self,
        symbol: str,
        proposed_size: float,
        side: str,
        account_balance: float,
        current_positions: Dict[str, dict]  # {symbol: {side, size, pnl}}
    ) -> RiskAssessment:
        """
        Evaluate a proposed trade and adjust if necessary.
        
        Args:
            symbol: Symbol to trade
            proposed_size: Proposed position size
            side: 'buy' or 'sell'
            account_balance: Current account balance
            current_positions: Dict of current positions
        
        Returns:
            RiskAssessment with approval and adjusted size
        """
        # 1. Check basic risk limit
        risk_amount = proposed_size * 0.02  # Assume 2% SL
        risk_percent = risk_amount / account_balance if account_balance > 0 else 1.0
        
        if risk_percent > self.max_risk_per_trade:
            # Reduce size to fit within limits
            max_size = (self.max_risk_per_trade * account_balance) / 0.02
            return RiskAssessment(
                approved=True,
                original_size=proposed_size,
                adjusted_size=max_size,
                risk_score=0.8,
                reason=f"Size reduced to fit {self.max_risk_per_trade*100}% risk limit",
                correlations={}
            )
        
        # 2. Check correlation with existing positions
        position_symbols = list(current_positions.keys())
        correlations = self.find_correlated_assets(symbol, position_symbols)
        
        if correlations:
            # Find maximum correlation
            max_corr_symbol = max(correlations, key=lambda x: abs(correlations[x]))
            max_corr = abs(correlations[max_corr_symbol])
            
            # Check if same direction (amplifying risk)
            existing_pos = current_positions.get(max_corr_symbol, {})
            existing_side = existing_pos.get('side', '').lower()
            
            same_direction = (
                (side.lower() == 'buy' and existing_side == 'buy') or
                (side.lower() == 'sell' and existing_side == 'sell')
            )
            
            if same_direction and max_corr >= self.correlation_threshold:
                # REDUCE RISK: Cut position by 50%
                adjusted_size = proposed_size * 0.5
                
                logger.warning(
                    f"⚠️ ALADDIN: {symbol} correlated ({max_corr:.0%}) with {max_corr_symbol}. "
                    f"Reducing size from {proposed_size} to {adjusted_size}"
                )
                
                return RiskAssessment(
                    approved=True,
                    original_size=proposed_size,
                    adjusted_size=adjusted_size,
                    risk_score=max_corr,
                    reason=f"Correlated with {max_corr_symbol} ({max_corr:.0%}). Size halved.",
                    correlations=correlations
                )
        
        # 3. Check total portfolio risk
        total_exposure = sum(
            pos.get('size', 0) for pos in current_positions.values()
        )
        total_exposure += proposed_size
        
        portfolio_risk = total_exposure / account_balance if account_balance > 0 else 1.0
        
        if portfolio_risk > self.max_portfolio_risk:
            # Reject or reduce
            available_exposure = (self.max_portfolio_risk * account_balance) - (total_exposure - proposed_size)
            
            if available_exposure <= 0:
                return RiskAssessment(
                    approved=False,
                    original_size=proposed_size,
                    adjusted_size=0,
                    risk_score=1.0,
                    reason=f"Portfolio risk limit ({self.max_portfolio_risk*100}%) exceeded",
                    correlations=correlations
                )
            
            return RiskAssessment(
                approved=True,
                original_size=proposed_size,
                adjusted_size=available_exposure,
                risk_score=0.9,
                reason=f"Size reduced to stay within portfolio limit",
                correlations=correlations
            )
        
        # 4. Trade approved as-is
        return RiskAssessment(
            approved=True,
            original_size=proposed_size,
            adjusted_size=proposed_size,
            risk_score=risk_percent / self.max_risk_per_trade,
            reason="Trade approved",
            correlations=correlations
        )
    
    def emergency_check(
        self,
        current_drawdown: float,
        max_drawdown_limit: float = 0.05
    ) -> bool:
        """
        Emergency circuit breaker check.
        
        Args:
            current_drawdown: Current drawdown as fraction (e.g., 0.03 = 3%)
            max_drawdown_limit: Maximum allowed drawdown before shutdown
        
        Returns:
            True if trading should HALT
        """
        if abs(current_drawdown) >= max_drawdown_limit:
            logger.critical(
                f"🚨 ALADDIN EMERGENCY: Drawdown {current_drawdown*100:.1f}% "
                f"exceeds limit {max_drawdown_limit*100}%. HALT TRADING!"
            )
            return True
        
        return False
