'use client';

import useSWR from 'swr';

// Backend API URL
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

// Fetcher function
const fetcher = async (url: string) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch');
    return res.json();
};

// Types
export interface DashboardData {
    account: {
        balance: number;
        equity: number;
    };
    positions: Array<{
        symbol: string;
        side: string;
        pnl: number;
        status?: string;
        entry_price?: number;
        amount?: number;
    }>;
    engines: {
        aexi: number;
        dream: number;
        last_signal: string | null;
    };
    bots: Array<{
        name: string;
        win_rate: number;
        pnl: number;
        color?: string;
    }>;
    timestamp: string;
}

export interface BotScore {
    name: string;
    score: number;
    color: string;
}

export interface Transaction {
    asset: string;
    type: 'LONG' | 'SHORT';
    price: number;
    amount?: number;
    pnl?: number;
    status: string;
}

/**
 * Hook to fetch dashboard data from backend
 */
export function useDashboard() {
    const { data, error, isLoading, mutate } = useSWR<DashboardData>(
        `${API_BASE}/api/dashboard`,
        fetcher,
        {
            refreshInterval: 5000, // Refresh every 5 seconds
            revalidateOnFocus: true,
        }
    );

    // Transform bot data to BotScore format
    const botScores: BotScore[] = data?.bots?.map((bot, idx) => ({
        name: bot.name || `Bot ${idx + 1}`,
        score: bot.win_rate || 50,
        color: bot.color || ['#00FF88', '#00D9FF', '#FFD700'][idx % 3],
    })) || [
            { name: 'Alpha Bot', score: 84, color: '#00FF88' },
            { name: 'Quantum Core', score: 95, color: '#00D9FF' },
            { name: 'Sniper', score: 65, color: '#FFD700' },
        ];

    // Transform positions to transactions
    const transactions: Transaction[] = data?.positions?.map((pos) => ({
        asset: pos.symbol?.split('/')[0] || pos.symbol || 'N/A',
        type: (pos.side?.toUpperCase() === 'LONG' ? 'LONG' : 'SHORT') as 'LONG' | 'SHORT',
        price: pos.entry_price || 0,
        amount: pos.amount,
        pnl: pos.pnl,
        status: pos.status || 'Pending',
    })) || [];

    return {
        data,
        botScores,
        transactions,
        engines: data?.engines,
        account: data?.account,
        isLoading,
        isError: error,
        mutate,
    };
}

/**
 * Hook to fetch engine scores (AEXI & Dream)
 */
export function useEngines() {
    const { data, error, isLoading } = useSWR<DashboardData>(
        `${API_BASE}/api/dashboard`,
        fetcher,
        { refreshInterval: 3000 }
    );

    return {
        aexi: data?.engines?.aexi || 50,
        dream: data?.engines?.dream || 50,
        lastSignal: data?.engines?.last_signal,
        isLoading,
        isError: error,
    };
}

/**
 * Hook to get system status
 */
export function useSystemStatus() {
    const { data, error } = useSWR<{ message: string }>(
        `${API_BASE}/health`,
        fetcher,
        { refreshInterval: 10000 }
    );

    return {
        isOnline: !error && data?.message?.includes('Online'),
        message: data?.message || 'Checking...',
        isError: error,
    };
}
