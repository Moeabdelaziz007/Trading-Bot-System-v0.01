"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { History, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface TradeLog {
    id?: number;
    ticker: string;
    action: string;
    qty: number;
    order_id?: string;
    trigger_reason?: string;
    executed_at?: string;
}

export default function HistoryPage() {
    const [logs, setLogs] = useState<TradeLog[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/logs`);
            if (res.ok) {
                const data = await res.json();
                setLogs(data.logs || []);
            }
        } catch (e) { console.error(e); }
        setLoading(false);
    }, []);

    useEffect(() => { fetchLogs(); }, [fetchLogs]);

    return (
        <div className="p-8 h-full overflow-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white">Trade History</h1>
                    <p className="text-gray-500 text-sm">All executed trades and automation logs</p>
                </div>
                <button onClick={fetchLogs} className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg text-gray-400 hover:text-white">
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <History size={16} /> Total Trades
                    </div>
                    <p className="text-3xl font-bold text-white">{logs.length}</p>
                </div>

                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <CheckCircle size={16} /> Buy Orders
                    </div>
                    <p className="text-3xl font-bold text-green-400">
                        {logs.filter(l => l.action === 'buy').length}
                    </p>
                </div>

                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <XCircle size={16} /> Sell Orders
                    </div>
                    <p className="text-3xl font-bold text-red-400">
                        {logs.filter(l => l.action === 'sell').length}
                    </p>
                </div>
            </div>

            {/* Trade Logs Table */}
            <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-gray-800">
                    <h2 className="font-bold text-white">Recent Trades</h2>
                </div>

                {logs.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No trade history yet. Execute some trades to see them here.
                    </div>
                ) : (
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-900/50 text-gray-400 uppercase text-xs">
                            <tr>
                                <th className="p-4">Time</th>
                                <th className="p-4">Symbol</th>
                                <th className="p-4">Side</th>
                                <th className="p-4">Qty</th>
                                <th className="p-4">Trigger</th>
                                <th className="p-4">Order ID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {logs.map((log, i) => (
                                <tr key={i} className="border-b border-gray-800 hover:bg-gray-900/50">
                                    <td className="p-4 text-gray-400">
                                        <div className="flex items-center gap-2">
                                            <Clock size={14} />
                                            {log.executed_at ? new Date(log.executed_at).toLocaleString() : 'N/A'}
                                        </div>
                                    </td>
                                    <td className="p-4 font-bold text-white">{log.ticker}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${log.action === 'buy' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                            }`}>
                                            {log.action?.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="p-4 text-gray-300">{log.qty}</td>
                                    <td className="p-4 text-gray-500 text-xs">{log.trigger_reason || 'manual'}</td>
                                    <td className="p-4 text-gray-600 text-xs font-mono">{log.order_id?.slice(0, 8) || '-'}...</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
