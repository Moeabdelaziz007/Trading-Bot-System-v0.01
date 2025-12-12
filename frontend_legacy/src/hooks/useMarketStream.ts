"use client";

import { useState, useEffect, useCallback } from 'react';

// API Base URL - Production Cloudflare Worker
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev';

// Dashboard Response Type
export interface DashboardSnapshot {
    account: {
        balance: number;
        equity: number;
        buying_power?: number;
        day_trades?: number;
    };
    positions: Array<{
        symbol: string;
        qty: number;
        side: string;
        market_value: number;
        unrealized_pl: number;
    }>;
    engines: {
        aexi: number;
        dream: number;
        last_signal: any | null;
    };
    bots: Array<{
        id: string;
        name: string;
        strategy: string;
        active: boolean;
        pnl: number;
    }>;
    timestamp: string;
}

// Default empty state
const DEFAULT_SNAPSHOT: DashboardSnapshot = {
    account: { balance: 0, equity: 0 },
    positions: [],
    engines: { aexi: 50, dream: 50, last_signal: null },
    bots: [],
    timestamp: new Date().toISOString()
};

/**
 * 🎯 useMarketStream - Expert Level Data Hook
 * 
 * Implements SWR (Stale-While-Revalidate) pattern:
 * - Returns cached data immediately
 * - Fetches fresh data in background
 * - Auto-refreshes every 5 seconds
 * 
 * @param pollInterval - Refresh interval in ms (default: 5000)
 */
export function useMarketStream(pollInterval: number = 5000) {
    const [data, setData] = useState<DashboardSnapshot>(DEFAULT_SNAPSHOT);
    const [isLoading, setIsLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

    const fetchSnapshot = useCallback(async () => {
        try {
            const response = await fetch(`${API_BASE}/api/dashboard`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                cache: 'no-store'
            });

            if (!response.ok) {
                throw new Error(`API Error: ${response.status}`);
            }

            const snapshot: DashboardSnapshot = await response.json();
            setData(snapshot);
            setLastUpdate(new Date());
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
            // Don't clear data on error - keep stale data
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Initial fetch + polling
    useEffect(() => {
        fetchSnapshot();

        const intervalId = setInterval(fetchSnapshot, pollInterval);

        return () => clearInterval(intervalId);
    }, [fetchSnapshot, pollInterval]);

    // Manual refresh function
    const refresh = useCallback(() => {
        setIsLoading(true);
        fetchSnapshot();
    }, [fetchSnapshot]);

    return {
        data,
        isLoading,
        error,
        lastUpdate,
        refresh
    };
}

// Convenience hooks for specific data slices
export function useAccount() {
    const { data, ...rest } = useMarketStream();
    return { account: data.account, ...rest };
}

export function useEngines() {
    const { data, ...rest } = useMarketStream();
    return { engines: data.engines, ...rest };
}

export function usePositions() {
    const { data, ...rest } = useMarketStream();
    return { positions: data.positions, ...rest };
}

export function useBots() {
    const { data, ...rest } = useMarketStream();
    return { bots: data.bots, ...rest };
}
