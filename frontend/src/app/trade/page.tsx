"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { TradingChart } from '@/components/TradingChart';
import { ArrowUp, ArrowDown, DollarSign } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

export default function TradePage() {
    const [symbol, setSymbol] = useState('SPY');
    const [side, setSide] = useState<'buy' | 'sell'>('buy');
    const [qty, setQty] = useState('10');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<string | null>(null);
    const [portfolio, setPortfolio] = useState<{ buying_power: string } | null>(null);

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
        { symbol: 'SPY', name: 'S&P 500', type: 'Stock' },
        { symbol: 'AAPL', name: 'Apple', type: 'Stock' },
        { symbol: 'TSLA', name: 'Tesla', type: 'Stock' },
        { symbol: 'GOOGL', name: 'Alphabet', type: 'Stock' },
        { symbol: 'GLD', name: 'Gold ETF', type: 'Commodity' },
        { symbol: 'BTC', name: 'Bitcoin', type: 'Crypto' },
    ];

    return (
        <div className="flex flex-col h-full overflow-hidden">
            <header className="h-16 bg-[#0a0a0a] border-b border-gray-800/50 flex items-center px-6 shrink-0">
                <h1 className="text-lg font-bold">Trading Terminal</h1>
            </header>

            <div className="flex-1 flex overflow-hidden">
                {/* Chart Area */}
                <div className="flex-1 p-6 flex flex-col gap-4 overflow-hidden">
                    <div className="flex gap-2 overflow-x-auto shrink-0">
                        {assets.map((asset) => (
                            <button key={asset.symbol} onClick={() => setSymbol(asset.symbol)}
                                className={`px-4 py-2 rounded-lg transition-all ${symbol === asset.symbol ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400' : 'bg-gray-900/50 border border-gray-800/50 text-gray-400'
                                    }`}
                            >
                                <div className="font-bold text-sm">{asset.symbol}</div>
                                <div className="text-xs text-gray-500">{asset.type}</div>
                            </button>
                        ))}
                    </div>

                    <div className="flex-1 min-h-[350px]">
                        <TradingChart symbol={symbol} timeframe="1H" />
                    </div>
                </div>

                {/* Order Panel */}
                <div className="w-[320px] bg-[#0a0a0a] border-l border-gray-800/50 p-6 flex flex-col gap-4 shrink-0">
                    <h2 className="font-bold text-lg">Place Order</h2>

                    <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800/50">
                        <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
                            <DollarSign size={14} /> Buying Power
                        </div>
                        <div className="text-2xl font-bold text-green-400">
                            ${portfolio ? parseFloat(portfolio.buying_power).toLocaleString() : '200,000'}
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Symbol</label>
                        <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 outline-none text-sm" />
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Side</label>
                        <div className="grid grid-cols-2 gap-2">
                            <button onClick={() => setSide('buy')}
                                className={`py-2 rounded-lg font-bold flex items-center justify-center gap-2 text-sm ${side === 'buy' ? 'bg-green-500/20 border border-green-500/50 text-green-400' : 'bg-gray-800/50 border border-gray-700/50 text-gray-400'
                                    }`}
                            ><ArrowUp size={14} /> BUY</button>
                            <button onClick={() => setSide('sell')}
                                className={`py-2 rounded-lg font-bold flex items-center justify-center gap-2 text-sm ${side === 'sell' ? 'bg-red-500/20 border border-red-500/50 text-red-400' : 'bg-gray-800/50 border border-gray-700/50 text-gray-400'
                                    }`}
                            ><ArrowDown size={14} /> SELL</button>
                        </div>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Quantity</label>
                        <input type="number" value={qty} onChange={(e) => setQty(e.target.value)}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 outline-none text-sm" />
                    </div>

                    <button onClick={executeTrade} disabled={loading}
                        className={`w-full py-3 rounded-lg font-bold text-sm ${side === 'buy' ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gradient-to-r from-red-500 to-rose-600'
                            } disabled:opacity-50`}
                    >
                        {loading ? 'Executing...' : `${side.toUpperCase()} ${qty} ${symbol}`}
                    </button>

                    {result && (
                        <div className={`p-3 rounded-lg border text-sm ${result.includes('✅') ? 'bg-green-500/10 border-green-500/30 text-green-400' : 'bg-gray-800/50 border-gray-700/50 text-gray-300'
                            }`}>
                            {result}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
