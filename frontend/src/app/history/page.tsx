"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { DashboardLayout, StatCard, TableSkeleton, EmptyState } from '@/components/DashboardLayout';
import { History, RefreshCw, CheckCircle, XCircle, Clock, Filter, Download, Search } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy.workers.dev";

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
    const [filter, setFilter] = useState<'all' | 'buy' | 'sell'>('all');
    const [searchTerm, setSearchTerm] = useState('');

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

    const filteredLogs = logs.filter(log => {
        const matchesFilter = filter === 'all' || log.action === filter;
        const matchesSearch = !searchTerm || log.ticker.toLowerCase().includes(searchTerm.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    const buyCount = logs.filter(l => l.action === 'buy').length;
    const sellCount = logs.filter(l => l.action === 'sell').length;

    return (
        <DashboardLayout title="Trade History" subtitle="All executed trades and automation logs">
            <div className="p-6">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <StatCard label="Total Trades" value={logs.length} icon={History} color="cyan" />
                    <StatCard label="Buy Orders" value={buyCount} icon={CheckCircle} color="green" />
                    <StatCard label="Sell Orders" value={sellCount} icon={XCircle} color="red" />
                </div>

                {/* Filters */}
                <div className="glass-card p-4 mb-6">
                    <div className="flex flex-wrap items-center gap-4">
                        {/* Search */}
                        <div className="relative flex-1 min-w-[200px]">
                            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                            <input
                                type="text"
                                placeholder="Search by symbol..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full bg-black/30 border border-white/5 rounded-lg py-2 pl-10 pr-4 text-sm outline-none focus:border-cyan-500/50"
                            />
                        </div>

                        {/* Filter Buttons */}
                        <div className="flex items-center gap-2">
                            <Filter size={16} className="text-gray-500" />
                            {(['all', 'buy', 'sell'] as const).map((f) => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`px-3 py-1.5 text-sm rounded-lg transition-all ${filter === f
                                            ? f === 'buy' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                                : f === 'sell' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                                    : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                            : 'text-gray-400 hover:bg-white/5'
                                        }`}
                                >
                                    {f.charAt(0).toUpperCase() + f.slice(1)}
                                </button>
                            ))}
                        </div>

                        {/* Export */}
                        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                            <Download size={14} />
                            Export
                        </button>

                        {/* Refresh */}
                        <button
                            onClick={fetchLogs}
                            className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors"
                        >
                            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                            Refresh
                        </button>
                    </div>
                </div>

                {/* Trade Logs Table */}
                {loading ? (
                    <TableSkeleton rows={5} />
                ) : filteredLogs.length === 0 ? (
                    <div className="glass-card">
                        <EmptyState
                            icon={History}
                            title="No Trade History"
                            description="Execute some trades to see them here. Your trading activity will be logged automatically."
                            actionLabel="Go to Terminal"
                            action={() => window.location.href = '/trade'}
                        />
                    </div>
                ) : (
                    <div className="glass-card overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-black/30 text-gray-400 uppercase text-xs">
                                    <tr>
                                        <th className="p-4">Time</th>
                                        <th className="p-4">Symbol</th>
                                        <th className="p-4">Side</th>
                                        <th className="p-4">Qty</th>
                                        <th className="p-4">Trigger</th>
                                        <th className="p-4">Order ID</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {filteredLogs.map((log, i) => (
                                        <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                            <td className="p-4">
                                                <div className="flex items-center gap-2 text-gray-400">
                                                    <Clock size={14} />
                                                    <span className="font-mono text-xs">
                                                        {log.executed_at ? new Date(log.executed_at).toLocaleString() : 'N/A'}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="p-4 font-mono font-semibold text-white">{log.ticker}</td>
                                            <td className="p-4">
                                                <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${log.action === 'buy'
                                                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                                    }`}>
                                                    {log.action?.toUpperCase()}
                                                </span>
                                            </td>
                                            <td className="p-4 font-mono text-gray-300">{log.qty}</td>
                                            <td className="p-4">
                                                <span className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded">
                                                    {log.trigger_reason || 'manual'}
                                                </span>
                                            </td>
                                            <td className="p-4 font-mono text-gray-600 text-xs">{log.order_id?.slice(0, 8) || '-'}...</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    );
}
