-- Migration number: 0001 ⏱️ 2025-12-14T04:45:00Z
-- Initial Schema Migration for Trading Cloud Brain D1 Database
-- This migration creates all core tables for the trading system
-- Environment: D1 (Cloudflare SQLite)

-- ========================================
-- 1. Core Trading Tables
-- ========================================

-- Trades Table (The core ledger)
CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    -- UUID
    symbol TEXT NOT NULL,
    -- e.g. EURUSD
    direction TEXT NOT NULL,
    -- BUY / SELL
    entry_price REAL NOT NULL,
    exit_price REAL,
    qty REAL NOT NULL,
    pnl REAL,
    status TEXT NOT NULL,
    -- OPEN, FILLED, CLOSED, CANCELED
    opened_at INTEGER NOT NULL,
    -- Unix Timestamp
    closed_at INTEGER,
    strategy TEXT,
    -- scalper / swing
    meta JSON -- Extra data (SL, TP, indicators)
);

-- Indexes for trades table
CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_opened_at ON trades(opened_at);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);

-- Signals Table (AI Decision Log)
CREATE TABLE IF NOT EXISTS signals (
    id TEXT PRIMARY KEY,
    symbol TEXT NOT NULL,
    engine TEXT NOT NULL,
    -- AEXI, Dream, PatternScanner
    signal_type TEXT NOT NULL,
    -- BULLISH, BEARISH
    strength REAL,
    -- 0.0 - 1.0 (Confidence)
    timestamp INTEGER NOT NULL,
    raw_data JSON -- Full indicator values at that moment
);

-- Indexes for signals table
CREATE INDEX IF NOT EXISTS idx_signals_timestamp ON signals(timestamp);
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals(symbol);
CREATE INDEX IF NOT EXISTS idx_signals_engine ON signals(engine);

-- ========================================
-- 2. Learning Loop Tables
-- ========================================

-- signal_events (The Brain's Memory)
CREATE TABLE IF NOT EXISTS signal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    -- Unix timestamp (ms)
    symbol TEXT NOT NULL,
    -- AAPL, BTCUSDT, EURUSD, etc.
    asset_type TEXT NOT NULL,
    -- stock, forex, crypto
    -- Market State at Signal Time
    price_at_signal REAL NOT NULL,
    bid REAL,
    ask REAL,
    source TEXT,
    -- finage, bybit, etc.
    -- Signal Details
    signal_direction TEXT NOT NULL,
    -- STRONG_BUY, BUY, NEUTRAL, SELL, STRONG_SELL
    signal_confidence REAL NOT NULL,
    -- 0.0 to 1.0
    factors TEXT,
    -- JSON array: ["Strong Momentum", "RSI Oversold"]
    -- Component Scores (for Learning which factors work best)
    momentum_score REAL,
    rsi_score REAL,
    sentiment_score REAL,
    volume_score REAL,
    volatility_score REAL
);

-- Indexes for signal_events
CREATE INDEX IF NOT EXISTS idx_signal_symbol_time ON signal_events(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_signal_direction ON signal_events(signal_direction);
CREATE INDEX IF NOT EXISTS idx_signal_timestamp ON signal_events(timestamp DESC);

-- signal_outcomes (The Teacher)
CREATE TABLE IF NOT EXISTS signal_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_event_id INTEGER NOT NULL,
    -- FK to signal_events
    -- Outcome Measurements
    price_1h_later REAL,
    price_4h_later REAL,
    price_24h_later REAL,
    -- Calculated Performance
    return_1h REAL,
    -- % return after 1 hour
    return_4h REAL,
    return_24h REAL,
    -- Accuracy Flags (Did we predict correctly?)
    was_correct_1h INTEGER,
    -- 1=correct, 0=wrong, NULL=unknown
    was_correct_4h INTEGER,
    was_correct_24h INTEGER,
    final_status TEXT DEFAULT 'incomplete',
    -- incomplete, complete, error, skipped
    updated_at INTEGER,
    -- When outcome was last calculated
    FOREIGN KEY (signal_event_id) REFERENCES signal_events(id)
);

-- Indexes for signal_outcomes
CREATE INDEX IF NOT EXISTS idx_outcome_signal ON signal_outcomes(signal_event_id);
CREATE INDEX IF NOT EXISTS idx_outcome_updated ON signal_outcomes(updated_at);

-- learning_metrics (The Report Card)
CREATE TABLE IF NOT EXISTS learning_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Aggregation Dimensions
    symbol TEXT,
    signal_direction TEXT,
    timeframe TEXT,
    -- 1h, 4h, 24h
    date_range TEXT,
    -- YYYY-MM (monthly aggregation)
    -- Performance Stats
    total_signals INTEGER,
    correct_signals INTEGER,
    accuracy_pct REAL,
    avg_return REAL,
    max_return REAL,
    min_return REAL,
    -- Component Analysis (Which factors contributed most?)
    momentum_contribution REAL,
    rsi_contribution REAL,
    sentiment_contribution REAL,
    last_updated INTEGER
);

-- Indexes for learning_metrics
CREATE INDEX IF NOT EXISTS idx_metrics_symbol_dir ON learning_metrics(symbol, signal_direction);
CREATE INDEX IF NOT EXISTS idx_metrics_accuracy ON learning_metrics(accuracy_pct DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_timeframe ON learning_metrics(timeframe);

-- weight_history (The Evolution Log)
CREATE TABLE IF NOT EXISTS weight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL,
    weights TEXT NOT NULL,
    -- JSON: {"momentum": 0.4, "rsi": 0.2, ...}
    based_on_signals INTEGER DEFAULT 0,
    previous_accuracy REAL DEFAULT 0.0,
    expected_improvement REAL DEFAULT 0.0,
    factor_accuracies TEXT,
    -- JSON: per-factor accuracy
    created_at INTEGER NOT NULL,
    status TEXT DEFAULT 'ACTIVE',
    -- ACTIVE, SUPERSEDED, ROLLED_BACK
    notes TEXT
);

-- Indexes for weight_history
CREATE INDEX IF NOT EXISTS idx_weight_version ON weight_history(version DESC);
CREATE INDEX IF NOT EXISTS idx_weight_status ON weight_history(status);

-- ========================================
-- 3. News and Briefings Tables
-- ========================================

-- News Table
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT UNIQUE NOT NULL,
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sentiment TEXT DEFAULT 'neutral',
    raw_data TEXT
);

-- Indexes for news
CREATE INDEX IF NOT EXISTS idx_news_published ON news(published_at DESC);

-- Daily AI Briefings
CREATE TABLE IF NOT EXISTS briefings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    summary TEXT,
    sentiment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for briefings
CREATE INDEX IF NOT EXISTS idx_briefings_created ON briefings(created_at DESC);

-- ========================================
-- 4. Payments Tables
-- ========================================

-- User OAuth connections (encrypted tokens)
CREATE TABLE IF NOT EXISTS user_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    -- 'coinbase', 'stripe'
    access_token TEXT NOT NULL,
    -- ENCRYPTED
    refresh_token TEXT,
    -- ENCRYPTED
    token_expires_at INTEGER,
    -- Unix timestamp (ms)
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    UNIQUE(user_id, provider)
);

-- Trade orders executed via platform
CREATE TABLE IF NOT EXISTS trade_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    -- 'coinbase'
    client_order_id TEXT NOT NULL,
    -- Our internal ID
    external_order_id TEXT,
    -- Coinbase order ID
    product_id TEXT NOT NULL,
    -- 'BTC-USD'
    side TEXT NOT NULL,
    -- 'BUY', 'SELL'
    order_type TEXT NOT NULL,
    -- 'MARKET', 'LIMIT'
    size TEXT,
    -- Base amount
    quote_size TEXT,
    -- Quote amount
    price TEXT,
    -- Limit price
    status TEXT DEFAULT 'PENDING',
    -- 'PENDING', 'FILLED', 'CANCELLED', 'FAILED'
    filled_size TEXT,
    filled_value TEXT,
    fee TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER
);

-- Indexes for payments tables
CREATE INDEX IF NOT EXISTS idx_user_connections_user ON user_connections(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_orders_user ON trade_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_trade_orders_client_id ON trade_orders(client_order_id);

-- ========================================
-- 5. System Monitoring Tables
-- ========================================

-- system_alerts (The Immune System)
CREATE TABLE IF NOT EXISTS system_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id TEXT UNIQUE,
    severity TEXT NOT NULL,
    -- INFO, WARNING, ERROR, CRITICAL
    category TEXT NOT NULL,
    -- ACCURACY_DROP, DATA_QUALITY, ROLLBACK, etc.
    title TEXT NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'OPEN',
    -- OPEN, ACKNOWLEDGED, RESOLVED
    created_at INTEGER NOT NULL,
    resolved_at INTEGER
);

-- Indexes for system_alerts
CREATE INDEX IF NOT EXISTS idx_alert_severity ON system_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alert_status ON system_alerts(status);

-- system_monitoring table for observability
CREATE TABLE IF NOT EXISTS system_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metadata TEXT,
    -- JSON metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Indexes for system_monitoring
CREATE INDEX IF NOT EXISTS idx_system_monitoring_name ON system_monitoring(metric_name);
CREATE INDEX IF NOT EXISTS idx_system_monitoring_created ON system_monitoring(created_at DESC);

-- telegram_reports table for audit trail
CREATE TABLE IF NOT EXISTS telegram_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    -- daily, weekly, optimization
    report_date TEXT NOT NULL,
    -- YYYY-MM-DD
    report_content TEXT NOT NULL,
    -- Full message text
    sent_at INTEGER NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Indexes for telegram_reports
CREATE INDEX IF NOT EXISTS idx_telegram_reports_date ON telegram_reports(report_date);
CREATE INDEX IF NOT EXISTS idx_telegram_reports_type ON telegram_reports(report_type);

-- ========================================
-- 6. Views for Dashboard Analytics
-- ========================================

-- View: Current overall accuracy
CREATE VIEW IF NOT EXISTS v_current_accuracy AS
SELECT ROUND(
        SUM(
            CASE
                WHEN was_correct_1h = 1 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) as accuracy_1h,
    ROUND(
        SUM(
            CASE
                WHEN was_correct_4h = 1 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) as accuracy_4h,
    ROUND(
        SUM(
            CASE
                WHEN was_correct_24h = 1 THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) as accuracy_24h,
    COUNT(*) as total_tracked
FROM signal_outcomes
WHERE was_correct_1h IS NOT NULL;

-- ========================================
-- 7. Migration Tracking Table
-- ========================================

-- This table will be managed by the migration script
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at INTEGER NOT NULL,
    checksum TEXT NOT NULL
);

-- Index for schema_migrations
CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at ON schema_migrations(applied_at DESC);