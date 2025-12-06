"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { DashboardLayout, StatCard } from '@/components/DashboardLayout';
import { TradingChart } from '@/components/TradingChart';
import { ArrowUp, ArrowDown, DollarSign, LineChart, Zap, AlertTriangle } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy.workers.dev";

export default function TradePage() {
    const [symbol, setSymbol] = useState('SPY');
    const [side, setSide] = useState<'buy' | 'sell'>('buy');
    const [qty, setQty] = useState('10');
    const [orderType, setOrderType] = useState<'market' | 'limit'>('market');
    const [limitPrice, setLimitPrice] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [portfolio, setPortfolio] = useState<{ buying_power: string; portfolio_value: string } | null>(null);

    const fetchPortfolio = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/account`);
            if (res.ok) setPortfolio(await res.json());
        } catch (e) { console.error(e); }
    }, []);

    useEffect(() => { fetchPortfolio(); }, [fetchPortfolio]);

    const executeTrade = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch(`${API_BASE}/api/trade?symbol=${symbol}&side=${side}&qty=${qty}`);
            const data = await res.json();
            setResult(data.message || JSON.stringify(data));
            fetchPortfolio();
        } catch {
            setResult('Trade failed');
        }
        setLoading(false);
    };

    const assets = [
        { symbol: 'SPY', name: 'S&P 500', type: 'Index' },
        { symbol: 'AAPL', name: 'Apple', type: 'Stock' },
        { symbol: 'TSLA', name: 'Tesla', type: 'Stock' },
        { symbol: 'GOOGL', name: 'Alphabet', type: 'Stock' },
        { symbol: 'NVDA', name: 'NVIDIA', type: 'Stock' },
        { symbol: 'BTC', name: 'Bitcoin', type: 'Crypto' },
    ];

    return (
        <DashboardLayout title="Trading Terminal" subtitle="Execute trades with precision">
            <div className="flex h-full">
                {/* Chart Area */}
                <div className="flex-1 p-6 flex flex-col gap-4 overflow-hidden">
                    {/* Asset Selector */}
                    <div className="flex gap-2 overflow-x-auto pb-2 shrink-0">
                        {assets.map((asset) => (
                            <button
                                key={asset.symbol}
                                onClick={() => setSymbol(asset.symbol)}
                                className={`px-4 py-2.5 rounded-xl transition-all flex-shrink-0 ${symbol === asset.symbol
                                        ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400 glow-cyan'
                                        : 'glass-card text-gray-400 hover:text-white hover:border-white/10'
                                    }`}
                            >
                                <div className="font-mono font-semibold text-sm">{asset.symbol}</div>
                                <div className="text-xs opacity-60">{asset.type}</div>
                            </button>
                        ))}
                    </div>

                    {/* Chart */}
                    <div className="flex-1 glass-card overflow-hidden min-h-[400px]">
                        <TradingChart symbol={symbol} timeframe="1H" />
                    </div>
                </div>

                {/* Order Panel */}
                <div className="w-[340px] glass-card-strong border-l border-white/5 p-6 flex flex-col gap-5 shrink-0">
                    {/* Account Stats */}
                    <div className="grid grid-cols-2 gap-3">
                        <StatCard
                            label="Buying Power"
                            value={`$${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200K'}`}
                            icon={DollarSign}
                            color="green"
                        />
                        <StatCard
                            label="Portfolio"
                            value={`$${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100K'}`}
                            icon={LineChart}
                            color="cyan"
                        />
                    </div>

                    {/* Order Form */}
                    <div className="space-y-4">
                        <div>
                            <label className="text-xs text-gray-500 font-medium block mb-2">Symbol</label>
                            <input
                                type="text"
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                                className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 font-mono font-semibold outline-none focus:border-cyan-500/50 transition-colors"
                            />
                        </div>

                        <div>
                            <label className="text-xs text-gray-500 font-medium block mb-2">Side</label>
                            <div className="grid grid-cols-2 gap-3">
                                <button
                                    onClick={() => setSide('buy')}
                                    className={`py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${side === 'buy'
                                            ? 'bg-emerald-500/20 border border-emerald-500/50 text-emerald-400 glow-green'
                                            : 'glass-card text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <ArrowUp size={16} /> BUY
                                </button>
                                <button
                                    onClick={() => setSide('sell')}
                                    className={`py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${side === 'sell'
                                            ? 'bg-rose-500/20 border border-rose-500/50 text-rose-400 glow-red'
                                            : 'glass-card text-gray-400 hover:text-white'
                                        }`}
                                >
                                    <ArrowDown size={16} /> SELL
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="text-xs text-gray-500 font-medium block mb-2">Order Type</label>
                            <div className="grid grid-cols-2 gap-3">
                                {(['market', 'limit'] as const).map((type) => (
                                    <button
                                        key={type}
                                        onClick={() => setOrderType(type)}
                                        className={`py-2.5 rounded-xl text-sm font-medium transition-all ${orderType === type
                                                ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400'
                                                : 'glass-card text-gray-400 hover:text-white'
                                            }`}
                                    >
                                        {type.charAt(0).toUpperCase() + type.slice(1)}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3">
                            <div>
                                <label className="text-xs text-gray-500 font-medium block mb-2">Quantity</label>
                                <input
                                    type="number"
                                    value={qty}
                                    onChange={(e) => setQty(e.target.value)}
                                    className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 font-mono outline-none focus:border-cyan-500/50 transition-colors"
                                />
                            </div>
                            {orderType === 'limit' && (
                                <div>
                                    <label className="text-xs text-gray-500 font-medium block mb-2">Limit Price</label>
                                    <input
                                        type="number"
                                        value={limitPrice}
                                        onChange={(e) => setLimitPrice(e.target.value)}
                                        placeholder="0.00"
                                        className="w-full bg-black/30 border border-white/5 rounded-xl py-3 px-4 font-mono outline-none focus:border-cyan-500/50 transition-colors"
                                    />
                                </div>
                            )}
                        </div>

                        {/* AI Suggestion */}
                        <div className="glass-card p-3 flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center">
                                <Zap size={14} className="text-cyan-400" />
                            </div>
                            <div className="flex-1">
                                <p className="text-xs text-gray-400">AI suggests</p>
                                <p className="text-sm text-white font-medium">Wait for better entry</p>
                            </div>
                        </div>

                        {/* Execute Button */}
                        <button
                            onClick={executeTrade}
                            disabled={loading}
                            className={`w-full py-4 rounded-xl font-bold text-white flex items-center justify-center gap-2 transition-all ${side === 'buy'
                                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:shadow-lg hover:shadow-emerald-500/30'
                                    : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:shadow-lg hover:shadow-rose-500/30'
                                } disabled:opacity-50`}
                        >
                            {loading ? (
                                <>Executing...</>
                            ) : (
                                <>
                                    {side === 'buy' ? <ArrowUp size={18} /> : <ArrowDown size={18} />}
                                    {side.toUpperCase()} {qty} {symbol}
                                </>
                            )}
                        </button>

                        {/* Result */}
                        {result && (
                            <div className={`p-4 rounded-xl border ${result.includes('✅')
                                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                                    : 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                                }`}>
                                <div className="flex items-start gap-2">
                                    <AlertTriangle size={16} className="shrink-0 mt-0.5" />
                                    <p className="text-sm">{result}</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
