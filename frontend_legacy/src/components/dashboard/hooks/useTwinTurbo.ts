'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

export interface TwinTurboStatus {
    aexi: number;
    dream: number;
    lastSignal: {
        final_verdict: string;
        chaos: number;
        timestamp: string;
    } | null;
    timestamp: string;
}

export const useTwinTurbo = () => {
    const [status, setStatus] = useState<TwinTurboStatus>({
        aexi: 50.0,
        dream: 50.0,
        lastSignal: null,
        timestamp: new Date().toISOString()
    });

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                setLoading(true);
                // Using the unified dashboard endpoint which reads from KV
                const response = await axios.get(`${API_BASE}/api/dashboard`);

                if (response.data.engines) {
                    setStatus({
                        aexi: response.data.engines.aexi ?? 50,
                        dream: response.data.engines.dream ?? 50,
                        lastSignal: response.data.engines.last_signal,
                        timestamp: new Date().toISOString()
                    });
                }
            } catch (error) {
                console.error('Failed to fetch Twin-Turbo status:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();
        const interval = setInterval(fetchStatus, 3000); // Fast 3s updates for Engines

        return () => clearInterval(interval);
    }, []);

    return { status, loading };
};
