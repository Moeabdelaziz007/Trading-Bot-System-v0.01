DROP TABLE IF EXISTS market_ohlcv;
CREATE TABLE market_ohlcv (
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    source TEXT,
    PRIMARY KEY (symbol, timestamp)
);
DROP TABLE IF EXISTS market_signals;
CREATE TABLE market_signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    type TEXT,
    data TEXT,
    -- JSON string
    confidence REAL
);
-- Index for fast signal retrieval
CREATE INDEX idx_signals_symbol_ts ON market_signals(symbol, timestamp);