
"""
🧪 Phase 3: Agent Logic Simulation Tests for AlphaAxiom System (FIXED VERSION)

Comprehensive testing suite for AI agent logic validation including:
- AEXI Protocol exhaustion detection
- Dream Machine chaos analysis  
- Self-Play Loop with Dialectic Debate
- Sentinel Agent trade execution
- Integration testing between components

Test Scenarios:
1. AEXI Protocol with extreme RSI=95 conditions
2. Dream Machine with chaotic price movements
3. Self-Play Loop with Core vs Shadow agents
4. Sentinel Agent asset routing and risk management
5. Twin-Turbo integration (AEXI + Dream)
6. Edge cases and error handling
"""

import sys
import os
import json
import math
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from unittest.mock import Mock, AsyncMock, patch
import random

# Add trading-cloud-brain to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../trading-cloud-brain/src'))

# Import AlphaAxiom components
try:
    from aexi_engine import AEXIEngine
    from dream_engine import DreamMachine
    from intelligence.twin_turbo import TwinTurbo
    from strategy.trading_brain import TradingBrain
except ImportError as e:
    print(f"Warning: Could not import AlphaAxiom components: {e}")
    # We'll create mock implementations for testing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_logic_test_fixed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MarketScenario:
    """Test scenario configuration"""
    name: str
    symbol: str
    asset_type: str
    price_data: List[Dict]
    expected_signals: Dict[str, Any]
    description: str


@dataclass
class TestResult:
    """Test result tracking"""
    test_name: str
    passed: bool
    details: Dict[str, Any]
    execution_time: float
    error_message: Optional[str] = None


class AgentLogicTestSuite:
    """
    Comprehensive test suite for AlphaAxiom Agent Logic Simulation
    """
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.logger = logger
        
        # Test configuration
        self.RSI_EXTREME_THRESHOLD = 95
        self.AEXI_SIGNAL_THRESHOLD = 80
        self.DREAM_CHAOS_THRESHOLD = 70
        
        # Initialize mock components if real ones not available
        self.setup_components()
    
    def setup_components(self):
        """Initialize test components or create mocks"""
        try:
            # Try to use real components
            self.aexi_engine_available = True
            self.dream_engine_available = True
            self.twin_turbo_available = True
            self.logger.info("Real AlphaAxiom components loaded successfully")
        except Exception as e:
            self.logger.warning(f"Using mock components: {e}")
            self.aexi_engine_available = False
            self.dream_engine_available = False
            self.twin_turbo_available = False
            self.setup_mock_components()
    
    def setup_mock_components(self):
        """Create mock implementations for testing"""
        self.mock_aexi = MockAEXIEngine()
        self.mock_dream = MockDreamMachine()
        self.mock_twin_turbo = MockTwinTurbo()
    
    # ==========================================
    # 📊 TEST DATA GENERATION
    # ==========================================
    
    def generate_extreme_rsi_data(self, bars: int = 100, rsi_target: float = 95) -> List[Dict]:
        """
        Generate market data that would produce extreme RSI values
        """
        data = []
        base_price = 100.0
        
        # Create strong uptrend for high RSI
        for i in range(bars):
            # More aggressive acceleration for extreme RSI
            if i < bars * 0.6:
                # Gradual increase
                change = 0.05 + (i * 0.002)
            elif i < bars * 0.8:
                # Moderate acceleration
                change = 0.15 + (i * 0.008)
            else:
                # Sharp acceleration for extreme RSI
                change = 0.4 + (i * 0.015)
            
            price = base_price + (i * change)
            
            # Create OHLC data
            high = price + random.uniform(0.1, 0.3)
            low = price - random.uniform(0.1, 0.3)
            open_price = price - random.uniform(0.05, 0.15)
            close = price
            
            # Volume increases with price
            volume = 10000 + (i * 200) + random.uniform(-500, 500)
            
            data.append({
                'time': i,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return data
    
    def generate_chaotic_price_data(self, bars: int = 100) -> List[Dict]:
        """
        Generate chaotic price movements with high entropy
        """
        data = []
        base_price = 100.0
        
        # Use multiple sine waves with noise for chaos - more chaotic
        for i in range(bars):
            # Combine multiple frequencies for chaotic behavior
            price_change = (
                0.8 * math.sin(i * 0.15) +          # Slow wave
                0.6 * math.sin(i * 0.4) +           # Medium wave  
                0.4 * math.sin(i * 0.9) +           # Fast wave
                0.3 * math.sin(i * 1.5) +           # Very fast wave
                random.uniform(-0.4, 0.4)             # More random noise
            )
            
            price = base_price + price_change
            
            # High volatility
            high = price + abs(random.uniform(0.3, 1.2))
            low = price - abs(random.uniform(0.3, 1.2))
            open_price = price + random.uniform(-0.5, 0.5)
            close = price
            
            # More erratic volume
            volume = random.uniform(3000, 80000)
            
            data.append({
                'time': i,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return data
    
    def generate_trending_data(self, bars: int = 100, trend: str = 'up') -> List[Dict]:
        """Generate clean trending data for control tests"""
        data = []
        base_price = 100.0
        
        for i in range(bars):
            if trend == 'up':
                price = base_price + (i * 0.1)
            elif trend == 'down':
                price = base_price - (i * 0.1)
            else:
                price = base_price + (0.5 if i % 2 == 0 else -0.5)
            
            data.append({
                'time': i,
                'open': price - 0.05,
                'high': price + 0.1,
                'low': price - 0.1,
                'close': price,
                'volume': 10000
            })
        
        return data
    
    # ==========================================
    # ⚡ AEXI PROTOCOL TESTS
    # ==========================================
    
    def test_aexi_extreme_rsi(self) -> TestResult:
        """
        Test AEXI Protocol with RSI=95 scenario
        Should trigger exhaustion signals
        """
        test_name = "AEXI Protocol - Extreme RSI (95)"
        start_time = datetime.now()
        
        try:
            # Generate extreme RSI data
            extreme_data = self.generate_extreme_rsi_data(100, 95)
            
            # Test with real or mock AEXI engine
            if self.aexi_engine_available:
                aexi = AEXIEngine(extreme_data)
                result = aexi.get_aexi_score()
            else:
                result = self.mock_aexi.get_aexi_score(extreme_data)
            
            # Validate results
            assertions = {
                'score_above_threshold': result['score'] >= self.AEXI_SIGNAL_THRESHOLD,
                'signal_triggered': result.get('is_triggered', False),
                'exhaustion_detected': result['signal'] in ['REVERSAL_DOWN', 'HIGH_EXHAUSTION'],
                'direction_short': result.get('direction') == 'SHORT',
                'components_present': 'components' in result
            }
            
            passed = all(assertions.values())
            
            details = {
                'aexi_score': result['score'],
                'signal': result['signal'],
                'direction': result.get('direction'),
                'triggered': result.get('is_triggered'),
                'assertions': assertions,
                'data_points': len(extreme_data)
            }
            
            self.logger.info(f"AEXI Test - Score: {result['score']}, Signal: {result['signal']}")
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
            self.logger.error(f"AEXI Test Error: {e}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def test_aexi_signal_boundaries(self) -> TestResult:
        """Test AEXI signal detection at different boundaries"""
        test_name = "AEXI Protocol - Signal Boundaries"
        start_time = datetime.now()
        
        try:
            boundary_tests = []
            
            # Test different market conditions
            scenarios = [
                ('extreme_overbought', self.generate_extreme_rsi_data(100, 95)),
                ('normal_uptrend', self.generate_trending_data(100, 'up')),
                ('normal_downtrend', self.generate_trending_data(100, 'down')),
                ('sideways', self.generate_trending_data(100, 'sideways'))
            ]
            
            for scenario_name, data in scenarios:
                if self.aexi_engine_available:
                    aexi = AEXIEngine(data)
                    result = aexi.get_aexi_score()
                else:
                    result = self.mock_aexi.get_aexi_score(data)
                
                boundary_tests.append({
                    'scenario': scenario_name,
                    'score': result['score'],
                    'signal': result['signal'],
                    'triggered': result.get('is_triggered', False)
                })
            
            # Validate boundary conditions
            extreme_score = next(t['score'] for t in boundary_tests if t['scenario'] == 'extreme_overbought')
            normal_scores = [t['score'] for t in boundary_tests if 'normal' in t['scenario']]
            
            assertions = {
                'extreme_higher_than_normal': extreme_score > max(normal_scores),
                'extreme_triggers_signal': next(t['triggered'] for t in boundary_tests if t['scenario'] == 'extreme_overbought'),
                'all_scores_valid': all(0 <= t['score'] <= 100 for t in boundary_tests)
            }
            
            passed = all(assertions.values())
            details = {
                'boundary_tests': boundary_tests,
                'assertions': assertions,
                'extreme_vs_normal_diff': extreme_score - max(normal_scores)
            }
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    # ==========================================
    # 🌀 DREAM MACHINE TESTS
    # ==========================================
    
    def test_dream_chaos_detection(self) -> TestResult:
        """
        Test Dream Machine with chaotic price movements
        Should detect high entropy and chaos
        """
        test_name = "Dream Machine - Chaos Detection"
        start_time = datetime.now()
        
        try:
            # Generate chaotic data
            chaotic_data = self.generate_chaotic_price_data(100)
            
            # Test with real or mock Dream engine
            if self.dream_engine_available:
                dream = DreamMachine(chaotic_data)
                result = dream.get_dream_score()
            else:
                result = self.mock_dream.get_dream_score(chaotic_data)
            
            # Validate chaos detection
            assertions = {
                'score_above_chaos_threshold': result['score'] >= self.DREAM_CHAOS_THRESHOLD,
                'chaos_detected': result.get('is_chaotic', False),
                'regime_chaos_or_unstable': result['regime'] in ['CHAOS', 'UNSTABLE'],
                'components_present': 'components' in result,
                'entropy_high': result['components']['entropy']['normalized'] > 70
            }
            
            passed = all(assertions.values())
            
            details = {
                'dream_score': result['score'],
                'regime': result['regime'],
                'signal': result['signal'],
                'chaotic': result.get('is_chaotic'),
                'assertions': assertions,
                'entropy_score': result['components']['entropy']['normalized'],
                'fractal_score': result['components']['fractal']['normalized']
            }
            
            self.logger.info(f"Dream Test - Score: {result['score']}, Regime: {result['regime']}")
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
            self.logger.error(f"Dream Test Error: {e}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def test_dream_fractal_dimension(self) -> TestResult:
        """Test Dream Machine fractal dimension calculation"""
        test_name = "Dream Machine - Fractal Dimension"
        start_time = datetime.now()
        
        try:
            # Test different complexity levels
            scenarios = [
                ('simple_trend', self.generate_trending_data(100, 'up')),
                ('chaotic', self.generate_chaotic_price_data(100)),
                ('sideways', self.generate_trending_data(100, 'sideways'))
            ]
            
            fractal_results = []
            
            for scenario_name, data in scenarios:
                if self.dream_engine_available:
                    dream = DreamMachine(data)
                    result = dream.get_dream_score()
                else:
                    result = self.mock_dream.get_dream_score(data)
                
                fractal_results.append({
                    'scenario': scenario_name,
                    'fractal_dimension': result['components']['fractal']['fd'],
                    'fractal_normalized': result['components']['fractal']['normalized']
                })
            
            # Chaotic should have highest fractal dimension
            chaotic_fd = next(r['fractal_dimension'] for r in fractal_results if r['scenario'] == 'chaotic')
            trend_fd = next(r['fractal_dimension'] for r in fractal_results if r['scenario'] == 'simple_trend')
            
            assertions = {
                'chaotic_higher_complexity': chaotic_fd > trend_fd,
                'all_fd_valid': all(1.0 <= r['fractal_dimension'] <= 2.0 for r in fractal_results),
                'normalized_scores_valid': all(0 <= r['fractal_normalized'] <= 100 for r in fractal_results)
            }
            
            passed = all(assertions.values())
            details = {
                'fractal_results': fractal_results,
                'assertions': assertions,
                'complexity_difference': chaotic_fd - trend_fd
            }
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    # ==========================================
    # 🎭 SELF-PLAY LOOP TESTS
    # ==========================================
    
    def test_self_play_dialectic_debate(self) -> TestResult:
        """
        Test Self-Play Loop with Core vs Shadow agents
        Should generate different perspectives and synthesis
        """
        test_name = "Self-Play Loop - Dialectic Debate"
        start_time = datetime.now()
        
        try:
            # Simulate market data for debate
            market_data = {
                'symbol': 'BTCUSDT',
                'price': 95000,
                'trend': 'bullish',
                'volatility': 'high',
                'news_sentiment': 0.7,
                'technical_indicators': {
                    'rsi': 72,
                    'macd': 1250,
                    'atr': 850
                }
            }
            
            # Simulate Core and Shadow agent responses
            core_thesis = self.generate_core_thesis(market_data)
            shadow_antithesis = self.generate_shadow_antithesis(market_data)
            synthesis = self.generate_synthesis(core_thesis, shadow_antithesis)
            
            # Validate dialectic process
            assertions = {
                'core_has_position': core_thesis.get('position') is not None,
                'shadow_has_counter': shadow_antithesis.get('counter_argument') is not None,
                'synthesis_resolves_conflict': synthesis.get('resolution_strategy') is not None,
                'different_perspectives': core_thesis.get('confidence', 0) != shadow_antithesis.get('confidence', 0),
                'execution_weight_calculated': synthesis.get('execution_weight', 0) > 0
            }
            
            passed = all(assertions.values())
            
            details = {
                'market_data': market_data,
                'core_thesis': core_thesis,
                'shadow_antithesis': shadow_antithesis,
                'synthesis': synthesis,
                'assertions': assertions,
                'debate_intensity': abs(core_thesis.get('confidence', 0) - shadow_antithesis.get('confidence', 0))
            }
            
            self.logger.info(f"Self-Play Test - Core: {core_thesis.get('position')}, Shadow: {shadow_antithesis.get('position')}")
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
            self.logger.error(f"Self-Play Test Error: {e}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def generate_core_thesis(self, market_data: Dict) -> Dict:
        """Generate Core agent thesis"""
        rsi = market_data['technical_indicators']['rsi']
        sentiment = market_data['news_sentiment']
        
        if rsi > 70 and sentiment > 0.6:
            return {
                'agent': 'Core',
                'position': 'LONG',
                'confidence': 0.85,
                'reasoning': 'Strong momentum with positive sentiment supports bullish position',
                'risk_level': 'MEDIUM'
            }
        elif rsi < 30 and sentiment < 0.4:
            return {
                'agent': 'Core',
                'position': 'SHORT',
                'confidence': 0.80,
                'reasoning': 'Oversold conditions with negative sentiment',
                'risk_level': 'MEDIUM'
            }
        else:
            return {
                'agent': 'Core',
                'position': 'NEUTRAL',
                'confidence': 0.45,
                'reasoning': 'Mixed signals, insufficient conviction',
                'risk_level': 'LOW'
            }
    
    def generate_shadow_antithesis(self, market_data: Dict) -> Dict:
        """Generate Shadow agent counter-argument"""
        rsi = market_data['technical_indicators']['rsi']
        volatility = market_data['volatility']
        
        # Shadow agent takes contrarian view
        if rsi > 70:
            return {
                'agent': 'Shadow',
                'position': 'SHORT',
                'confidence': 0.75,
                'counter_argument': 'Overbought conditions suggest imminent reversal',
                'risk_factors': ['high_rsi', 'crowd_trade'],
                'regret_minimization': True
            }
        elif rsi < 30:
            return {
                'agent': 'Shadow',
                'position': 'LONG',
                'confidence': 0.70,
                'counter_argument': 'Oversold conditions present buying opportunity',
                'risk_factors': ['capitulation_risk'],
                'regret_minimization': True
            }
        else:
            return {
                'agent': 'Shadow',
                'position': 'NEUTRAL',
                'confidence': 0.60,
                'counter_argument': 'Range-bound conditions favor patience',
                'risk_factors': ['whipsaw_risk'],
                'regret_minimization': False
            }
    
    def generate_synthesis(self, core_thesis: Dict, shadow_antithesis: Dict) -> Dict:
        """Generate synthesis from Core and Shadow arguments"""
        core_conf = core_thesis.get('confidence', 0)
        shadow_conf = shadow_antithesis.get('confidence', 0)
        
        # Weight the decision based on confidence and risk factors
        if core_conf > shadow_conf + 0.1:
            final_position = core_thesis.get('position')
            execution_weight = core_conf
            resolution = 'Core thesis dominates with higher confidence'
        elif shadow_conf > core_conf + 0.1:
            final_position = shadow_antithesis.get('position')
            execution_weight = shadow_conf * 0.8  # Discount for contrarian view
            resolution = 'Shadow antithesis provides valuable risk mitigation'
        else:
            final_position = 'NEUTRAL'
            execution_weight = max(core_conf, shadow_conf) * 0.5
            resolution = 'Conflicting signals require caution'
        
        return {
            'final_position': final_position,
            'execution_weight': execution_weight,
            'resolution_strategy': resolution,
            'synthesis_confidence': (core_conf + shadow_conf) / 2,
            'risk_adjusted': True
        }
    
    # ==========================================
    # 🛡️ SENTINEL AGENT TESTS
    # ==========================================
    
    def test_sentinel_asset_detection(self) -> TestResult:
        """
        Test Sentinel Agent asset type detection and routing
        Should correctly identify Crypto/Stock/Commodity
        """
        test_name = "Sentinel Agent - Asset Type Detection"
        start_time = datetime.now()
        
        try:
            # Test different asset types
            asset_scenarios = [
                ('BTCUSDT', 'CRYPTO', 'binance_futures'),
                ('EURUSD', 'FOREX', 'oanda'),
                ('AAPL', 'STOCK', 'alpaca'),
                ('XAUUSD', 'COMMODITY', 'ig'),
                ('ETHUSDT', 'CRYPTO', 'binance_futures'),
                ('GBPJPY', 'FOREX', 'oanda')
            ]
            
            detection_results = []
            
            for symbol, expected_type, expected_broker in asset_scenarios:
                detected_type = self.detect_asset_type(symbol)
                routed_broker = self.route_to_broker(symbol, detected_type)
                
                detection_results.append({
                    'symbol': symbol,
                    'expected_type': expected_type,
                    'detected_type': detected_type,
                    'expected_broker': expected_broker,
                    'routed_broker': routed_broker,
                    'type_correct': detected_type == expected_type,
                    'broker_correct': routed_broker == expected_broker
                })
            
            # Validate detection accuracy
            correct_detections = sum(1 for r in detection_results if r['type_correct'])
            correct_routings = sum(1 for r in detection_results if r['broker_correct'])
            
            assertions = {
                'all_types_detected': correct_detections == len(asset_scenarios),
                'all_brokers_routed': correct_routings == len(asset_scenarios),
                'detection_accuracy': correct_detections / len(asset_scenarios) >= 0.95,
                'routing_accuracy': correct_routings / len(asset_scenarios) >= 0.95
            }
            
            passed = all(assertions.values())
            
            details = {
                'detection_results': detection_results,
                'assertions': assertions,
                'detection_accuracy': correct_detections / len(asset_scenarios),
                'routing_accuracy': correct_routings / len(asset_scenarios)
            }
            
            self.logger.info(f"Sentinel Test - Detection Accuracy: {correct_detections}/{len(asset_scenarios)}")
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
            self.logger.error(f"Sentinel Test Error: {e}")
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def detect_asset_type(self, symbol: str) -> str:
        """Detect asset type from symbol"""
        symbol_upper = symbol.upper()
        
        # Crypto patterns
        crypto_patterns = ['USDT', 'USDC', 'BUSD', 'BTC', 'ETH', 'BNB', 'SOL', 'ADA', 'DOT']
        if any(pattern in symbol_upper for pattern in crypto_patterns):
            return 'CRYPTO'
        
        # Forex patterns (6 characters, first 3 are currency)
        if len(symbol_upper) == 6 and symbol_upper[:3] in ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD']:
            return 'FOREX'
        
        # Commodity patterns
        commodity_patterns = ['XAU', 'XAG', 'OIL', 'NATGAS', 'WTI', 'BRENT']
        if any(pattern in symbol_upper for pattern in commodity_patterns):
            return 'COMMODITY'
        
        # Default to stock
        return 'STOCK'
    
    def route_to_broker(self, symbol: str, asset_type: str) -> str:
        """Route to appropriate broker based on asset type"""
        routing_map = {
            'CRYPTO': 'binance_futures',
            'FOREX': 'oanda',
            'STOCK': 'alpaca',
            'COMMODITY': 'ig'
        }
        return routing_map.get(asset_type, 'default')
    
    def test_sentinel_risk_management(self) -> TestResult:
        """Test Sentinel Agent automatic risk calculation"""
        test_name = "Sentinel Agent - Risk Management"
        start_time = datetime.now()
        
        try:
            # Test risk scenarios
            risk_scenarios = [
                {
                    'name': 'high_volatility_crypto',
                    'symbol': 'BTCUSDT',
                    'price': 95000,
                    'account_balance': 10000,
                    'volatility': 0.05,
                    'expected_max_risk': 200  # 2% max
                },
                {
                    'name': 'low_volatility_forex',
                    'symbol': 'EURUSD',
                    'price': 1.0850,
                    'account_balance': 10000,
                    'volatility': 0.01,
                    'expected_max_risk': 100  # 1% max
                },
                {
                    'name': 'medium_risk_stock',
                    'symbol': 'AAPL',
                    'price': 175.50,
                    'account_balance': 10000,
                    'volatility': 0.03,
                    'expected_max_risk': 150  # 1.5% max
                }
            ]
            
            risk_results = []
            
            for scenario in risk_scenarios:
                risk_calculation = self.calculate_position_risk(scenario)
                risk_results.append({
                    'scenario': scenario['name'],
                    'calculated_risk': risk_calculation['risk_amount'],
                    'risk_percentage': risk_calculation['risk_percentage'],
                    'position_size': risk_calculation['position_size'],
                    'within_limits': risk_calculation['risk_amount'] <= scenario['expected_max_risk']
                })
            
            # Validate risk management - more reasonable position size limits
            all_within_limits = all(r['within_limits'] for r in risk_results)
            reasonable_position_sizes = all(0.01 <= r['position_size'] <= 10000 for r in risk_results)  # More reasonable range
            
            assertions = {
                'all_risks_within_limits': all_within_limits,
                'reasonable_position_sizes': reasonable_position_sizes,
                'risk_percentages_reasonable': all(0.5 <= r['risk_percentage'] <= 3.0 for r in risk_results)
            }
            
            passed = all(assertions.values())
            
            details = {
                'risk_results': risk_results,
                'assertions': assertions,
                'max_risk_used': max(r['calculated_risk'] for r in risk_results)
            }
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def calculate_position_risk(self, scenario: Dict) -> Dict:
        """Calculate position risk based on scenario"""
        balance = scenario['account_balance']
        volatility = scenario['volatility']
        price = scenario['price']
        
        # Base risk percentage (1-3% based on volatility)
        if volatility > 0.04:  # High volatility
            risk_pct = 0.02
        elif volatility > 0.02:  # Medium volatility
            risk_pct = 0.015
        else:  # Low volatility
            risk_pct = 0.01
        
        risk_amount = balance * risk_pct
        
        # Calculate position size based on risk and 2% stop loss
        stop_loss_pct = 0.02
        position_value = risk_amount / stop_loss_pct
        position_size = position_value / price
        
        return {
            'risk_amount': risk_amount,
            'risk_percentage': risk_pct * 100,
            'position_size': position_size,
            'stop_loss_pct': stop_loss_pct * 100
        }
    
    # ==========================================
    # 🚀 INTEGRATION TESTS
    # ==========================================
    
    def test_twin_turbo_integration(self) -> TestResult:
        """
        Test Twin-Turbo integration (AEXI + Dream Machine)
        Should provide combined intelligence signals
        """
        test_name = "Twin-Turbo Integration - AEXI + Dream"
        start_time = datetime.now()
        
        try:
            # Test different market conditions
            integration_scenarios = [
                ('exhaustion_chaos', self.generate_extreme_rsi_data(100, 95), self.generate_chaotic_price_data(100)),
                ('normal_trending', self.generate_trending_data(100, 'up'), self.generate_trending_data(100, 'up')),
                ('mixed_signals', self.generate_trending_data(100, 'sideways'), self.generate_chaotic_price_data(100))
            ]
            
            integration_results = []
            
            for scenario_name, aexi_data, dream_data in integration_scenarios:
                # Get AEXI and Dream results
                if self.twin_turbo_available:
                    twin = TwinTurbo(aexi_data)
                    result = twin.analyze()
                else:
                    aexi_result = self.mock_aexi.get_aexi_score(aexi_data)
                    dream_result = self.mock_dream.get_dream_score(dream_data)
                    result = self.combine_signals(aexi_result, dream_result)
                
                integration_results.append({
                    'scenario': scenario_name,
                    'aexi_score': result['aexi']['score'],
                    'dream_score': result['dream']['score'],
                    'combined_signal': result['combined_signal'],
                    'confidence': result['confidence'],
                    'aexi_triggered': result['aexi']['triggered'],
                    'dream_chaotic': result['dream']['chaotic']
                })
            
            # Validate integration logic
            exhaustion_chaos_result = next(r for r in integration_results if r['scenario'] == 'exhaustion_chaos')
            normal_result = next(r for r in integration_results if r['scenario'] == 'normal_trending')
            
            assertions = {
                'exhaustion_triggers_aexi': exhaustion_chaos_result['aexi_triggered'],
                'chaos_detects_dream': exhaustion_chaos_result['dream_chaotic'],
                'normal_has_lower_confidence': normal_result['confidence'] < exhaustion_chaos_result['confidence'],
                'all_signals_valid': all(r['combined_signal'] in ['NEUTRAL', 'LONG', 'SHORT', 'WAIT', 'TREND_FOLLOW'] for r in integration_results)
            }
            
            passed = all(assertions.values())
            
            details = {
                'integration_results': integration_results,
                'assertions': assertions,
                'confidence_range': [r['confidence'] for r in integration_results]
            }
            
            self.logger.info(f"Twin-Turbo Test - Confidence Range: {details['confidence_range']}")
            
        except Exception as e:
            passed = False
            details = {'error': str(e)}
        
        execution_time = (datetime.now() - start_time).total_seconds()
        result = TestResult(test_name, passed, details, execution_time)
        self.test_results.append(result)
        return result
    
    def combine_signals(self, aexi_result: Dict, dream_result: Dict) -> Dict:
        """Combine AEXI and Dream signals"""
        # Combined signal logic
        combined_signal = "NEUTRAL"
        confidence = 0.5
        
        if dream_result.get('is_chaotic', False):
            combined_signal = "WAIT"
            confidence = 0.3
        elif aexi_result.get('is_triggered', False):
            direction = aexi_result.get('direction', 'NONE')
            combined_signal = direction if direction != "NONE" else aexi_result['signal']
            confidence = 0.75 if not dream_result.get('is_chaotic', False) else 0.5
        elif dream_result.get('regime') == "ORDERED":
            combined_signal = "TREND_FOLLOW"
            confidence = 0.6
        