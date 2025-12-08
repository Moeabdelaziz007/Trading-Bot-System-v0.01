-- ========================================
-- 💎 AXIOM DATA LEARNING LOOP - Schema
-- ========================================
-- Purpose: Capture every signal, track outcomes, enable self-learning
-- "Data = Gold" - The Moat
-- ========================================
-- Table 1: signal_events (The Brain's Memory)
-- ========================================
-- Records EVERY signal generated with full context
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
    volume_score REAL
);
-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_signal_symbol_time ON signal_events(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_signal_direction ON signal_events(signal_direction);
CREATE INDEX IF NOT EXISTS idx_signal_timestamp ON signal_events(timestamp DESC);
-- ========================================
-- Table 2: signal_outcomes (The Teacher)
-- ========================================
-- Records what ACTUALLY happened after each signal
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
    updated_at INTEGER,
    -- When outcome was last calculated
    FOREIGN KEY (signal_event_id) REFERENCES signal_events(id)
);
-- Indexes for tracking
CREATE INDEX IF NOT EXISTS idx_outcome_signal ON signal_outcomes(signal_event_id);
CREATE INDEX IF NOT EXISTS idx_outcome_updated ON signal_outcomes(updated_at);
-- ========================================
-- Table 3: learning_metrics (The Report Card)
-- ========================================
-- Aggregated performance by symbol, timeframe, conditions
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
-- Indexes for analysis
CREATE INDEX IF NOT EXISTS idx_metrics_symbol_dir ON learning_metrics(symbol, signal_direction);
CREATE INDEX IF NOT EXISTS idx_metrics_accuracy ON learning_metrics(accuracy_pct DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_timeframe ON learning_metrics(timeframe);