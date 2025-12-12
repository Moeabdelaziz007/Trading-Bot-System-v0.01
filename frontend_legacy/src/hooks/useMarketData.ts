"use client";
import { useState, useEffect } from 'react';
import * as Ably from 'ably';

// 🔗 Backend API Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

export interface MarketData {
    symbol: string;
    price: number;
    change_percent: number;
    volume?: number;
    is_closed?: boolean;
}

export function useMarketData(initialSymbols: string[] = ['SPY', 'BTC/USD', 'ETH/USD', 'GLD']) {
    const [data, setData] = useState<Record<string, MarketData>>({});
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState<string | null>(null);

    // 1. Initial Fetch (Polling Fallback)
    const fetchSnapshot = async () => {
        try {
            const symbolsParam = initialSymbols.join(',');
            const res = await fetch(`${API_BASE}/api/market?symbols=${symbolsParam}`, {
                headers: { 'X-System-Key': SYSTEM_KEY }
            });
            const json = await res.json();

            // Handle both array and object formats (backend might return {symbols: [...]})
            const list = Array.isArray(json) ? json : (json.symbols || []);

            const newData: Record<string, MarketData> = {};
            list.forEach((item: MarketData) => {
                newData[item.symbol] = item;
            });
            setData(prev => ({ ...prev, ...newData }));
        } catch (e) {
            console.error("Snapshot error:", e);
        }
    };

    // 2. Ably Realtime Connection
    useEffect(() => {
        // Initial fetch
        fetchSnapshot();

        // Connect to Ably using Auth URL (secure token request from backend)
        const realtime = new Ably.Realtime({
            authUrl: `${API_BASE}/api/ably/auth`,
            authHeaders: { 'X-System-Key': SYSTEM_KEY },
            autoConnect: true
        });

        realtime.connection.on('connected', () => {
            console.log("⚡ Ably Connected");
            setIsConnected(true);
            setConnectionError(null);
        });

        realtime.connection.on('failed', (stateChange) => {
            console.error("⚡ Ably Connection Failed:", stateChange);
            setIsConnected(false);
            setConnectionError(stateChange.reason?.message || 'Connection failed');
        });

        // Subscribe to market-data channel
        const channel = realtime.channels.get('market-data');
        channel.subscribe('update', (message) => {
            const updates = message.data; // Expecting list of MarketData
            if (Array.isArray(updates)) {
                setData(prev => {
                    const next = { ...prev };
                    updates.forEach((item: MarketData) => {
                        next[item.symbol] = item;
                    });
                    console.log("⚡ WebSocket Update:", updates.length, "symbols");
                    return next;
                });
            }
        });

        return () => {
            channel.unsubscribe();
            realtime.close();
        };
    }, []);

    return {
        data,
        isConnected,
        connectionError,
        refetch: fetchSnapshot
    };
}
