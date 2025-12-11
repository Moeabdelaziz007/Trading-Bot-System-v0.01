-- ============================================
-- AXIOM LEARNING LOOP - D1 Database Schema
-- ============================================

-- ============================================
-- 1. signal_events - Main Signal Storage
-- ============================================
CREATE TABLE IF NOT EXISTS signal_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_id TEXT NOT NULL UNIQUE,
    symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('crypto', 'stock', 'forex')), 
    signal_direction TEXT NOT NULL CHECK(signal_direction IN ('BUY', 'STRONG_BUY', 'SELL', 'STRONG_SELL', 'NEUTRAL')),
    price_at_signal REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    confidence_score REAL NOT NULL,
    
    -- Factor Scores (0-100)
    momentum_score REAL,
    rsi_score REAL,
    sentiment_score REAL,
    volume_score REAL,
    volatility_score REAL,
    
    -- Context
    market_cap REAL,
    volume_24h REAL,
    
    -- Status
    status TEXT NOT NULL DEFAULT 'pending',
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_signal_events_timestamp ON signal_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_signal_events_symbol ON signal_events(symbol);
CREATE INDEX IF NOT EXISTS idx_signal_events_status ON signal_events(status);

-- ============================================
-- 2. signal_outcomes - Track Signal Results
-- ============================================
CREATE TABLE IF NOT EXISTS signal_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    signal_event_id INTEGER NOT NULL UNIQUE,
    
    -- 1 Hour Later
    price_1h_later REAL,
    return_1h REAL,
    was_correct_1h INTEGER CHECK(was_correct_1h IN (0, 1)),
    
    -- 4 Hours Later
    price_4h_later REAL,
    return_4h REAL,
    was_correct_4h INTEGER CHECK(was_correct_4h IN (0, 1)),
    
    -- 24 Hours Later
    price_24h_later REAL,
    return_24h REAL,
    was_correct_24h INTEGER CHECK(was_correct_24h IN (0, 1)),
    
    -- Final Status
    final_status TEXT NOT NULL DEFAULT 'incomplete' CHECK(final_status IN ('incomplete', 'complete', 'error', 'skipped')),
    
    -- Metadata
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    
    FOREIGN KEY(signal_event_id) REFERENCES signal_events(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_signal_outcomes_signal_id ON signal_outcomes(signal_event_id);
CREATE INDEX IF NOT EXISTS idx_signal_outcomes_final_status ON signal_outcomes(final_status);

-- ============================================
-- 3. learning_metrics - Daily Performance Stats
-- ============================================
CREATE TABLE IF NOT EXISTS learning_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_date TEXT NOT NULL,  -- YYYY-MM-DD
    symbol TEXT NOT NULL,
    signal_direction TEXT NOT NULL,
    timeframe TEXT NOT NULL CHECK(timeframe IN ('1h', '4h', '24h')),
    
    total_signals INTEGER NOT NULL,
    correct_signals INTEGER NOT NULL,
    avg_return REAL NOT NULL,
    max_return REAL NOT NULL,
    min_return REAL NOT NULL,
    
    -- Accuracy %
    accuracy REAL NOT NULL,
    
    -- Timestamps
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Composite index for daily queries
CREATE INDEX IF NOT EXISTS idx_learning_metrics_date_symbol ON learning_metrics(metric_date, symbol, signal_direction, timeframe);

-- ============================================
-- 4. weight_history - Track Weight Changes
-- ============================================
CREATE TABLE IF NOT EXISTS weight_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL UNIQUE,
    weights TEXT NOT NULL,  -- JSON: {"momentum": 0.4, "rsi": 0.2, ...}
    total_signals_analyzed INTEGER NOT NULL,
    accuracy_improvement REAL,  -- Expected improvement %
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Index for latest version
CREATE INDEX IF NOT EXISTS idx_weight_history_version ON weight_history(version DESC);

-- ============================================
-- 5. system_monitoring - System Health & Alerts
-- ============================================
CREATE TABLE IF NOT EXISTS system_monitoring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    metadata TEXT,  -- JSON metadata
    
    -- Timestamps
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Index for monitoring queries
CREATE INDEX IF NOT EXISTS idx_system_monitoring_name ON system_monitoring(metric_name);

-- ============================================
-- 6. telegram_reports - Store Telegram Reports
-- ============================================
CREATE TABLE IF NOT EXISTS telegram_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL CHECK(report_type IN ('daily', 'weekly', 'monthly')),
    report_date TEXT NOT NULL,  -- YYYY-MM-DD
    report_content TEXT NOT NULL,  -- JSON or Markdown
    sent_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    
    -- Metadata
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Index for report queries
CREATE INDEX IF NOT EXISTS idx_telegram_reports_date_type ON telegram_reports(report_date, report_type);

-- ============================================
-- 7. api_audit_log - API Access Logging
-- ============================================
CREATE TABLE IF NOT EXISTS api_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    endpoint TEXT NOT NULL,
    method TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    
    -- Timestamps
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

-- Index for audit queries
CREATE INDEX IF NOT EXISTS idx_api_audit_log_endpoint ON api_audit_log(endpoint);
