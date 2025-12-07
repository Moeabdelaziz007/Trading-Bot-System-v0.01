"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { DashboardLayout, StatCard, TableSkeleton, EmptyState } from '@/components/DashboardLayout';
import AssetAllocation from '@/components/AssetAllocation';
import { Wallet, TrendingUp, TrendingDown, DollarSign, PieChart, RefreshCw, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

const getHeaders = () => ({
    'Content-Type': 'application/json',
    ...(SYSTEM_KEY && { 'X-System-Key': SYSTEM_KEY })
});

interface Position {
    symbol: string;
    qty: string;
    avg_entry_price: string;
    current_price: string;
    market_value: string;
    unrealized_pl: string;
    unrealized_plpc: string;
}

export default function PortfolioPage() {
    const [portfolio, setPortfolio] = useState<{ portfolio_value: string, buying_power: string, cash: string } | null>(null);
    const [positions, setPositions] = useState<Position[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchData = useCallback(async () => {
        setLoading(true);
        try {
            const [accountRes, positionsRes] = await Promise.all([
                fetch(`${API_BASE}/api/account`, { headers: getHeaders() }),
                fetch(`${API_BASE}/api/positions`, { headers: getHeaders() })
            ]);
            if (accountRes.ok) setPortfolio(await accountRes.json());
            if (positionsRes.ok) {
                const data = await positionsRes.json();
                setPositions(Array.isArray(data) ? data : (data.positions || []));
            }
        } catch (e) { console.error(e); }
        setLoading(false);
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const totalPL = positions.reduce((acc, p) => acc + parseFloat(p.unrealized_pl || '0'), 0);

    return (
        <DashboardLayout title="Portfolio Intelligence" subtitle="Your holdings and performance analytics">
            <div className="p-6 space-y-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <StatCard
                        label="Portfolio Value"
                        value={`$${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100,000'}`}
                        icon={Wallet}
                        color="cyan"
                    />
                    <StatCard
                        label="Buying Power"
                        value={`$${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200,000'}`}
                        icon={DollarSign}
                        color="green"
                    />
                    <StatCard
                        label="Positions"
                        value={positions.length}
                        icon={PieChart}
                        color="cyan"
                    />
                    <StatCard
                        label="Unrealized P&L"
                        value={`${totalPL >= 0 ? '+' : ''}$${totalPL.toFixed(2)}`}
                        icon={totalPL >= 0 ? TrendingUp : TrendingDown}
                        color={totalPL >= 0 ? 'green' : 'red'}
                    />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Asset Allocation Chart */}
                    <div className="lg:col-span-1">
                        <AssetAllocation
                            positions={positions.map(p => ({
                                symbol: p.symbol,
                                market_value: p.market_value || String(parseFloat(p.qty) * parseFloat(p.current_price))
                            }))}
                            cash={portfolio?.cash || '100000'}
                        />
                    </div>

                    {/* Positions Table */}
                    <div className="lg:col-span-2">
                        {loading ? (
                            <TableSkeleton rows={5} />
                        ) : positions.length === 0 ? (
                            <div className="glass-card">
                                <EmptyState
                                    icon={Wallet}
                                    title="No Open Positions"
                                    description="Start trading to see your holdings here. Use the Terminal to execute your first trade."
                                    actionLabel="Go to Terminal"
                                    action={() => window.location.href = '/trade'}
                                />
                            </div>
                        ) : (
                            <div className="glass-card overflow-hidden">
                                <div className="p-4 border-b border-white/5 flex items-center justify-between">
                                    <h2 className="font-semibold text-white flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                                        Open Positions
                                    </h2>
                                    <button onClick={fetchData} className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors">
                                        <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                                        Refresh
                                    </button>
                                </div>
                                <div className="overflow-x-auto">
                                    <table className="w-full text-left text-sm">
                                        <thead className="bg-black/30 text-gray-400 uppercase text-xs">
                                            <tr>
                                                <th className="p-4">Symbol</th>
                                                <th className="p-4">Qty</th>
                                                <th className="p-4">Entry Price</th>
                                                <th className="p-4">Current Price</th>
                                                <th className="p-4">P&L</th>
                                                <th className="p-4">P&L %</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-white/5">
                                            {positions.map((pos, i) => {
                                                const pl = parseFloat(pos.unrealized_pl || '0');
                                                const plpc = parseFloat(pos.unrealized_plpc || '0') * 100;
                                                return (
                                                    <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                                        <td className="p-4">
                                                            <div className="flex items-center gap-3">
                                                                <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${pl >= 0 ? 'bg-emerald-500/20' : 'bg-rose-500/20'}`}>
                                                                    {pl >= 0 ? <ArrowUpRight size={16} className="text-emerald-400" /> : <ArrowDownRight size={16} className="text-rose-400" />}
                                                                </div>
                                                                <span className="font-mono font-semibold text-white">{pos.symbol}</span>
                                                            </div>
                                                        </td>
                                                        <td className="p-4 font-mono text-gray-300">{pos.qty}</td>
                                                        <td className="p-4 font-mono text-gray-300">${parseFloat(pos.avg_entry_price).toFixed(2)}</td>
                                                        <td className="p-4 font-mono text-white">${parseFloat(pos.current_price).toFixed(2)}</td>
                                                        <td className={`p-4 font-mono font-semibold ${pl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                            {pl >= 0 ? '+' : ''}${pl.toFixed(2)}
                                                        </td>
                                                        <td className={`p-4 font-mono ${plpc >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                            {plpc >= 0 ? '+' : ''}{plpc.toFixed(2)}%
                                                        </td>
                                                    </tr>
                                                );
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
