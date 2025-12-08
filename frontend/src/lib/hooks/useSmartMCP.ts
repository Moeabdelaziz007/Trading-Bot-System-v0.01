/**
 * Smart MCP Hook
 * 
 * Fetches market intelligence from the Zero-Cost MCP endpoint.
 * Supports both Crypto (Bybit) and Stocks (Finnhub).
 * 
 * @example
 * const { data, error, isLoading } = useSmartMCP("BTCUSDT");
 * const { data: appleData } = useSmartMCP("AAPL");
 */

import useSWR from 'swr';

// API Configuration
const MCP_BASE_URL = process.env.NEXT_PUBLIC_MCP_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

// Types
export interface PriceData {
    current: number;
    change_pct: number;
    high?: number;
    low?: number;
    high_24h?: number;
    low_24h?: number;
    volume_24h?: number;
    prev_close?: number;
    source: 'bybit' | 'finnhub' | 'cache' | 'unknown';
}

export interface CompositeSignal {
    direction: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL';
    confidence: number;
    factors?: string[];
}

export interface MarketIntelligence {
    symbol: string;
    asset_type: 'crypto' | 'stock';
    is_stale: boolean;
    price: PriceData;
    composite_signal: CompositeSignal;
}

export interface MCPResponse {
    status: 'success' | 'error';
    data?: MarketIntelligence;
    error?: string;
}

export interface MCPHealth {
    status: 'ok' | 'error';
    credits?: {
        finnhub: number;
        alpha_vantage: number;
        news_data: number;
    };
    message?: string;
}

// Fetcher function
const fetcher = async (url: string) => {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    return response.json();
};

/**
 * Hook to fetch market intelligence for a specific symbol
 * 
 * @param symbol - Trading symbol (e.g., "BTCUSDT", "AAPL", "TSLA")
 * @param refreshInterval - Auto-refresh interval in ms (default: 60000)
 */
export function useSmartMCP(symbol: string, refreshInterval: number = 60000) {
    const { data, error, isLoading, mutate } = useSWR<MCPResponse>(
        symbol ? `${MCP_BASE_URL}/api/mcp/intelligence?symbol=${symbol}` : null,
        fetcher,
        {
            refreshInterval,
            revalidateOnFocus: true,
            dedupingInterval: 10000, // Dedupe requests within 10s
        }
    );

    return {
        data: data?.data,
        error: error || (data?.status === 'error' ? new Error(data.error) : null),
        isLoading,
        refresh: mutate,
    };
}

/**
 * Hook to fetch MCP API health status (credits remaining)
 */
export function useMCPHealth() {
    const { data, error, isLoading } = useSWR<MCPHealth>(
        `${MCP_BASE_URL}/api/mcp/health`,
        fetcher,
        {
            refreshInterval: 300000, // Refresh every 5 minutes
        }
    );

    return {
        credits: data?.credits,
        status: data?.status,
        message: data?.message,
        error,
        isLoading,
    };
}

/**
 * Hook for multiple symbols (batch)
 */
export function useMultipleSymbols(symbols: string[], refreshInterval: number = 60000) {
    const results = symbols.map((symbol) => useSmartMCP(symbol, refreshInterval));

    return {
        data: results.map(r => r.data).filter(Boolean),
        isLoading: results.some(r => r.isLoading),
        errors: results.filter(r => r.error).map(r => r.error),
    };
}
