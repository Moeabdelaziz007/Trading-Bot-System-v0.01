-- Migration number: 0002 ⏱️ 2025-12-14T05:40:00Z
-- Add example tables and indexes to demonstrate migration system
-- Environment: D1 (Cloudflare SQLite)

-- Example: Add a new table for strategy performance tracking
CREATE TABLE IF NOT EXISTS strategy_performance (
    id TEXT PRIMARY KEY,
    strategy_name TEXT NOT NULL,
    symbol TEXT NOT NULL,
    win_rate REAL NOT NULL,
    total_trades INTEGER NOT NULL,
    profitable_trades INTEGER NOT NULL,
    avg_win REAL,
    avg_loss REAL,
    profit_factor REAL,
    max_drawdown REAL,
    sharpe_ratio REAL,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

-- Indexes for strategy_performance
CREATE INDEX IF NOT EXISTS idx_strategy_performance_name ON strategy_performance(strategy_name);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_symbol ON strategy_performance(symbol);
CREATE INDEX IF NOT EXISTS idx_strategy_performance_created ON strategy_performance(created_at DESC);

-- Example: Add a new column to existing trades table
ALTER TABLE trades ADD COLUMN strategy_version TEXT DEFAULT '1.0';

-- Example: Create a view for recent performance
CREATE VIEW IF NOT EXISTS v_recent_strategy_performance AS
SELECT 
    strategy_name,
    symbol,
    win_rate,
    total_trades,
    profit_factor,
    sharpe_ratio,
    updated_at
FROM strategy_performance 
WHERE updated_at > (strftime('%s', 'now') - 86400) * 1000
ORDER BY updated_at DESC;