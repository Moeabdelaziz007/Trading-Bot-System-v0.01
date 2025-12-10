"""
⏰ CRON HANDLER - Extracted from worker.py
Handles all scheduled tasks for AlphaAxiom Trading System

Cron Schedules:
- Every 1 min:  RiskGuardian + SwarmHeartbeat (safety scan)
- Every 5 min:  MomentumScout + VolatilitySpiker (opportunity detection)
- Every 15 min: ReversionHunter + LiquidityWatcher + Journalist
- Every 1 hour: Strategist + PerformanceMonitor (weight update)
- Daily 00:00:  ContestManager + WealthReport (daily ranking)
"""

from js import Response, fetch, Headers
import json
import datetime

# Import core modules
from core import log
from state import StateManager
from patterns import PatternScanner

# Constants
MAX_TRADES_PER_DAY = 30
MAX_DAILY_LOSS_PERCENT = 5.0
STARTING_EQUITY = 100000


async def on_scheduled(event, env, ctx=None):
    """
    Unified Cron Handler for AlphaAxiom.
    
    Combines both original cron handlers into one consolidated function.
    """
    now = datetime.datetime.utcnow()
    current_minute = now.minute
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 🛡️ SAFETY CHECK FIRST | فحص الأمان أولاً
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    trading_mode = str(getattr(env, 'TRADING_MODE', 'SIMULATION'))
    
    log.info(f"⏰ Cron Triggered at {now.isoformat()} | Mode: {trading_mode}")
    
    try:
        kv = env.BRAIN_MEMORY
        panic_mode = await kv.get("panic_mode")
        if panic_mode == "true":
            log.info("🛑 Panic mode active - all trading halted")
            # Still run maintenance even in panic mode
            await _run_maintenance(env)
            return
    except Exception as e:
        log.error(f"KV check failed: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 📊 DAILY LOSS CHECK (Safety Feature)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    try:
        from capital_connector import CapitalConnector
        capital = CapitalConnector(env)
        account = await capital.get_account_info()
        current_equity = float(account.get("equity", STARTING_EQUITY))
        
        starting_equity_str = await kv.get("daily_starting_equity")
        starting_equity = float(starting_equity_str) if starting_equity_str else STARTING_EQUITY
        
        daily_pnl_percent = ((current_equity - starting_equity) / starting_equity) * 100
        
        if daily_pnl_percent <= -MAX_DAILY_LOSS_PERCENT:
            await kv.put("panic_mode", "true")
            await kv.put("panic_reason", f"Daily loss limit hit: {daily_pnl_percent:.2f}%")
            await _send_alert(env, f"🛑 AUTO KILL SWITCH: Daily loss {daily_pnl_percent:.2f}%")
            return
    except Exception as e:
        log.error(f"Daily loss check failed: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1️⃣ RISK GUARDIAN + HEARTBEAT (Every 1 min)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    try:
        from risk_manager import RiskGuardian
        from economic_calendar import EconomicCalendar
        
        risk_brain = RiskGuardian(env)
        calendar = EconomicCalendar(env)
        
        high_impact = await calendar.check_impact_alerts()
        if high_impact:
            await risk_brain.engage_news_lockdown(high_impact)
            log.info("📰 High-impact news detected - trading paused")
            return
        
        await kv.put("swarm_heartbeat", now.isoformat())
        await kv.put("swarm_mode", trading_mode)
        
    except Exception as e:
        log.error(f"Risk/Heartbeat check failed: {e}")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2️⃣ FAST AGENTS (Every 5 min)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if current_minute % 5 == 0:
        await _run_fast_agents(env, kv)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3️⃣ 15-MIN AGENTS (Reversion + Liquidity)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if current_minute % 15 == 0:
        await _run_15min_agents(env, kv)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4️⃣ HOURLY AGENTS (Strategist + Monitor)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if current_minute == 0:
        await _run_hourly_agents(env, kv, current_hour)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5️⃣ DAILY MIDNIGHT (Contest + Report)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if current_hour == 0 and current_minute == 0:
        await _run_daily_tasks(env, kv, trading_mode, now)

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 6️⃣ LEARNING LOOP CRONS
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    await _run_learning_loop(env, current_minute, current_hour, current_weekday)


# ==========================================
# 🔧 HELPER FUNCTIONS
# ==========================================

async def _run_fast_agents(env, kv):
    """5-minute Fast Agents: MomentumScout + VolatilitySpiker"""
    log.info("⚡ Dispatching Fast Agents...")
    try:
        from data_collector import DataCollector
        from strategy import TradingBrain
        
        state = StateManager(env)
        if not await state.acquire_cron_lock("scalper_5min", ttl=60):
            return
        
        try:
            collector = DataCollector(env)
            watchlist = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD"]
            
            for symbol in watchlist:
                if await state.has_open_position(symbol):
                    continue
                if not await state.acquire_lock(symbol):
                    continue
                
                try:
                    candles = await collector.fetch_candles(symbol, timeframe="1m", limit=300)
                    if candles:
                        brain = TradingBrain(candles, mode="SCALP")
                        decision = brain.analyze()
                        
                        scanner = PatternScanner(candles)
                        patterns = scanner.scan_all()
                        
                        if decision.get('signal') not in ['NEUTRAL', 'NO_DATA']:
                            pattern_info = f" | Patterns: {len(patterns)}" if patterns else ""
                            await _send_alert(env, f"🚀 SCALP: {symbol}\nSignal: {decision['signal']}{pattern_info}")
                finally:
                    await state.release_lock(symbol)
        finally:
            await state.release_cron_lock("scalper_5min")
    except Exception as e:
        log.error(f"Fast agents failed: {e}")


async def _run_15min_agents(env, kv):
    """15-minute Agents: ReversionHunter + LiquidityWatcher"""
    log.info("📊 Dispatching 15min Agents...")
    try:
        from agents.journalist import JournalistAgent
        journalist = JournalistAgent(getattr(env, 'PERPLEXITY_API_KEY', ''))
        await journalist.run_mission(env)
    except Exception as e:
        log.error(f"Journalist failed: {e}")
    
    try:
        from agents.swarm import ReversionHunter, LiquidityWatcher
        from data_collector import DataCollector
        
        collector = DataCollector(env)
        crypto_list = ["BTCUSD", "ETHUSD", "SOLUSD"]
        
        for symbol in crypto_list:
            candles = await collector.fetch_candles(symbol, timeframe="15m", limit=100)
            if candles:
                reversion = ReversionHunter()
                rev_signal = reversion.analyze(candles)
                
                liquidity = LiquidityWatcher()
                liq_signal = liquidity.analyze(candles)
                
                await kv.put(f"signal_{symbol}_reversion", json.dumps(rev_signal))
                await kv.put(f"signal_{symbol}_liquidity", json.dumps(liq_signal))
    except Exception as e:
        log.error(f"15min agents failed: {e}")


async def _run_hourly_agents(env, kv, current_hour):
    """Hourly Agents: Strategist + PerformanceMonitor"""
    log.info("🧠 Hourly Update: Strategist...")
    try:
        from agents.strategist import StrategistAgent
        strategist = StrategistAgent(env)
        await strategist.run_mission()
    except Exception as e:
        log.error(f"Strategist failed: {e}")

    if current_hour % 4 == 0:
        try:
            from agents.swarm.performance_monitor import PerformanceMonitor
            monitor = PerformanceMonitor(env)
            weights = await monitor.update_softmax_weights()
            await kv.put("swarm_agent_weights", json.dumps(weights))
            log.info(f"⚖️ Weights updated: {weights}")
        except Exception as e:
            log.error(f"PerformanceMonitor failed: {e}")


async def _run_daily_tasks(env, kv, trading_mode, now):
    """Daily Midnight: ContestManager + WealthReport"""
    log.info("🏆 Daily Midnight Tasks...")
    try:
        from agents.swarm.contest_manager import ContestManager
        contest = ContestManager(env)
        rankings = await contest.generate_daily_rankings()
        await kv.put("daily_agent_rankings", json.dumps(rankings))
        
        if rankings.get("top_agent"):
            await _send_alert(env, f"🏆 Daily Contest\n🥇 {rankings['top_agent']}")
    except Exception as e:
        log.error(f"ContestManager failed: {e}")

    try:
        from finance.manager import FinanceManager
        fm = FinanceManager(env=env)
        report = await fm.get_consolidated_wealth()
        
        await _send_alert(env, f"📊 Daily Wealth Report\n💰 ${report.total_value:,.2f}\n📈 {report.change_24h:+.2f}%")
    except Exception as e:
        log.error(f"WealthReport failed: {e}")


async def _run_learning_loop(env, current_minute, current_hour, current_weekday):
    """Learning Loop Crons: Tracker, Aggregator, Optimizer"""
    # Hourly: Outcome Tracker
    if current_minute == 0:
        try:
            from learning.tracker import OutcomeTracker
            tracker = OutcomeTracker(env)
            await tracker.run()
        except Exception as e:
            log.error(f"OutcomeTracker failed: {e}")

    # Daily: Metrics Aggregator
    if current_hour == 0 and current_minute == 0:
        try:
            from learning.aggregator import MetricsAggregator
            aggregator = MetricsAggregator(env)
            await aggregator.run()
        except Exception as e:
            log.error(f"MetricsAggregator failed: {e}")

    # Weekly: Weight Optimizer (Sunday midnight)
    if current_weekday == 6 and current_hour == 0 and current_minute == 0:
        try:
            from learning.optimizer import WeightOptimizer
            optimizer = WeightOptimizer(env)
            await optimizer.run()
        except Exception as e:
            log.error(f"WeightOptimizer failed: {e}")


async def _run_maintenance(env):
    """Database cleanup - runs even in panic mode"""
    try:
        db = env.TRADING_DB
        await db.prepare("DELETE FROM trades WHERE timestamp < datetime('now', '-30 days')").run()
    except:
        pass


async def _send_alert(env, message):
    """Send Telegram alert"""
    try:
        from routes.telegram import send_telegram_alert
        await send_telegram_alert(env, message)
    except:
        pass
