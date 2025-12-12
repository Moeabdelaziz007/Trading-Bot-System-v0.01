'use client';

import { useState, useEffect } from 'react';
import Ably from 'ably';

interface Signal {
    id: number;
    symbol: string;
    asset_type: string;
    direction: string;
    confidence: number;
    price: number;
    source: string;
    factors: string;
    time: string;
}

interface SignalDashboardProps {
    apiUrl?: string;
    limit?: number;
}

export default function SignalDashboard({
    apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev'}/api/mcp/signals`,
    limit = 20
}: SignalDashboardProps) {    const [signals, setSignals] = useState<Signal[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState('');
    const [isLive, setIsLive] = useState(false);

    const fetchSignals = async () => {
        setLoading(true);
        try {
            const url = filter
                ? `${apiUrl}?limit=${limit}&symbol=${filter}`
                : `${apiUrl}?limit=${limit}`;

            const res = await fetch(url);
            const data = await res.json();

            if (data.status === 'success') {
                setSignals(data.signals);
                setError(null);
            } else {
                setError(data.message || 'Failed to fetch signals');
            }
        } catch (err) {
            setError('Connection error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSignals();

        // 📡 ABLY REAL-TIME SUBSCRIPTION
        let channel: Ably.RealtimeChannel | null = null;

        try {
            const ably = new Ably.Realtime({
                authUrl: `${process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev'}/api/ably/auth`
            });            channel = ably.channels.get('axiom:signals');

            channel.subscribe('signal', (message) => {
                const newSignal = JSON.parse(message.data);

                // Add to top of signals list
                setSignals(prev => [{
                    id: Date.now(),
                    symbol: newSignal.symbol,
                    asset_type: newSignal.asset_type || 'crypto',
                    direction: newSignal.direction,
                    confidence: newSignal.confidence,
                    price: newSignal.price,
                    source: 'live',
                    factors: newSignal.factors?.join(', ') || '',
                    time: newSignal.timestamp || new Date().toISOString()
                }, ...prev.slice(0, limit - 1)]);

                setIsLive(true);
            });

        } catch (e) {
            console.error('Ably connection failed:', e);
        }

        // Fallback: Auto-refresh every 30 seconds if Ably fails
        const interval = setInterval(fetchSignals, 30000);

        return () => {
            clearInterval(interval);
            if (channel) channel.unsubscribe();
        };
    }, [filter]);

    const getDirectionColor = (direction: string) => {
        if (direction.includes('BUY')) return 'text-green-400';
        if (direction.includes('SELL')) return 'text-red-400';
        return 'text-gray-400';
    };

    const getDirectionEmoji = (direction: string) => {
        if (direction === 'STRONG_BUY') return '🚀';
        if (direction === 'BUY') return '📈';
        if (direction === 'STRONG_SELL') return '💥';
        if (direction === 'SELL') return '📉';
        return '➖';
    };

    return (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                        <span className="text-xl">📊</span>
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">Signal History</h2>
                        <p className="text-sm text-gray-500">Data Learning Loop Active</p>
                    </div>
                </div>

                {/* Filter */}
                <div className="flex gap-2">
                    <input
                        type="text"
                        placeholder="Filter by symbol..."
                        value={filter}
                        onChange={(e) => setFilter(e.target.value.toUpperCase())}
                        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-purple-500"
                    />
                    <button
                        onClick={fetchSignals}
                        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
                    >
                        Refresh
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-gray-800/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Total Signals</p>
                    <p className="text-2xl font-bold text-white">{signals.length}</p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Buy Signals</p>
                    <p className="text-2xl font-bold text-green-400">
                        {signals.filter(s => s.direction.includes('BUY')).length}
                    </p>
                </div>
                <div className="bg-gray-800/50 rounded-lg p-4">
                    <p className="text-gray-400 text-sm">Sell Signals</p>
                    <p className="text-2xl font-bold text-red-400">
                        {signals.filter(s => s.direction.includes('SELL')).length}
                    </p>
                </div>
            </div>

            {/* Table */}
            {loading ? (
                <div className="flex items-center justify-center h-40">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple-500"></div>
                </div>
            ) : error ? (
                <div className="text-center py-8 text-red-400">{error}</div>
            ) : signals.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No signals recorded yet</div>
            ) : (
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="border-b border-gray-800">
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Time</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Symbol</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Direction</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Price</th>
                                <th className="text-right py-3 px-4 text-gray-400 font-medium text-sm">Confidence</th>
                                <th className="text-left py-3 px-4 text-gray-400 font-medium text-sm">Source</th>
                            </tr>
                        </thead>
                        <tbody>
                            {signals.map((signal) => (
                                <tr key={signal.id} className="border-b border-gray-800/50 hover:bg-gray-800/30 transition-colors">
                                    <td className="py-3 px-4 text-gray-300 text-sm">{signal.time}</td>
                                    <td className="py-3 px-4">
                                        <span className="font-mono font-bold text-white">{signal.symbol}</span>
                                        <span className="ml-2 text-xs text-gray-500">{signal.asset_type}</span>
                                    </td>
                                    <td className="py-3 px-4">
                                        <span className={`font-medium ${getDirectionColor(signal.direction)}`}>
                                            {getDirectionEmoji(signal.direction)} {signal.direction.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-right font-mono text-white">
                                        ${signal.price.toLocaleString()}
                                    </td>
                                    <td className="py-3 px-4 text-right">
                                        <span className={`
                      px-2 py-1 rounded text-xs font-medium
                      ${signal.confidence >= 0.7 ? 'bg-green-500/20 text-green-400' :
                                                signal.confidence >= 0.5 ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-gray-500/20 text-gray-400'}
                    `}>
                                            {Math.round(signal.confidence * 100)}%
                                        </span>
                                    </td>
                                    <td className="py-3 px-4 text-gray-400 text-sm">{signal.source}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Footer */}
            <div className="mt-4 flex items-center justify-between text-xs text-gray-500">
                <span>💎 Data = Gold | Learning Loop Active</span>
                <span>Auto-refresh: 30s</span>
            </div>
        </div>
    );
}
