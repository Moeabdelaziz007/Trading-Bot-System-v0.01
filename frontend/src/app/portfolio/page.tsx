"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { Wallet, TrendingUp, TrendingDown, DollarSign, PieChart, RefreshCw } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface Position {
    symbol: string;
    qty: string;
    avg_entry_price: string;
    current_price: string;
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
                fetch(`${API_BASE}/api/account`),
                fetch(`${API_BASE}/api/positions`)
            ]);
            if (accountRes.ok) setPortfolio(await accountRes.json());
            if (positionsRes.ok) {
                const data = await positionsRes.json();
                setPositions(data.positions || []);
            }
        } catch (e) { console.error(e); }
        setLoading(false);
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const totalPL = positions.reduce((acc, p) => acc + parseFloat(p.unrealized_pl || '0'), 0);

    return (
        <div className="p-8 h-full overflow-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white">Portfolio</h1>
                    <p className="text-gray-500 text-sm">Your holdings and performance</p>
                </div>
                <button onClick={fetchData} className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg text-gray-400 hover:text-white transition-colors">
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <Wallet size={16} /> Portfolio Value
                    </div>
                    <p className="text-3xl font-bold text-white">
                        ${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100,000'}
                    </p>
                </div>

                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <DollarSign size={16} /> Buying Power
                    </div>
                    <p className="text-3xl font-bold text-green-400">
                        ${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200,000'}
                    </p>
                </div>

                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        <PieChart size={16} /> Positions
                    </div>
                    <p className="text-3xl font-bold text-cyan-400">{positions.length}</p>
                </div>

                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
                        {totalPL >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />} Unrealized P&L
                    </div>
                    <p className={`text-3xl font-bold ${totalPL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {totalPL >= 0 ? '+' : ''}${totalPL.toFixed(2)}
                    </p>
                </div>
            </div>

            {/* Positions Table */}
            <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-gray-800">
                    <h2 className="font-bold text-white">Open Positions</h2>
                </div>

                {positions.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No open positions. Start trading to see your holdings here.
                    </div>
                ) : (
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-900/50 text-gray-400 uppercase text-xs">
                            <tr>
                                <th className="p-4">Symbol</th>
                                <th className="p-4">Qty</th>
                                <th className="p-4">Entry Price</th>
                                <th className="p-4">Current Price</th>
                                <th className="p-4">P&L</th>
                                <th className="p-4">P&L %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {positions.map((pos, i) => {
                                const pl = parseFloat(pos.unrealized_pl || '0');
                                const plpc = parseFloat(pos.unrealized_plpc || '0') * 100;
                                return (
                                    <tr key={i} className="border-b border-gray-800 hover:bg-gray-900/50">
                                        <td className="p-4 font-bold text-white">{pos.symbol}</td>
                                        <td className="p-4 text-gray-300">{pos.qty}</td>
                                        <td className="p-4 text-gray-300">${parseFloat(pos.avg_entry_price).toFixed(2)}</td>
                                        <td className="p-4 text-gray-300">${parseFloat(pos.current_price).toFixed(2)}</td>
                                        <td className={`p-4 font-bold ${pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {pl >= 0 ? '+' : ''}${pl.toFixed(2)}
                                        </td>
                                        <td className={`p-4 ${plpc >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                            {plpc >= 0 ? '+' : ''}{plpc.toFixed(2)}%
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
