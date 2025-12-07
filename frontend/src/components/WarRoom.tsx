"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { TradingChart } from '@/components/TradingChart';
import { Activity, Maximize2, Minimize2, AlertOctagon, Skull } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

const getHeaders = () => ({
    'Content-Type': 'application/json',
    ...(SYSTEM_KEY && { 'X-System-Key': SYSTEM_KEY })
});

// The Big 4 Market Drivers
const WAR_ASSETS = [
    { symbol: "SPY", name: "S&P 500", type: "Index" },
    { symbol: "BTC", name: "Bitcoin", type: "Crypto" },
    { symbol: "GLD", name: "Gold", type: "Commodity" },
    { symbol: "ETH", name: "Ethereum", type: "Crypto" }
];

interface WarRoomProps {
    globalTimeframe: string;
    onTimeframeChange: (tf: string) => void;
}

export function WarRoom({ globalTimeframe, onTimeframeChange }: WarRoomProps) {
    const [expandedCell, setExpandedCell] = useState<string | null>(null);
    const [panicConfirm, setPanicConfirm] = useState(false);
    const [marketData, setMarketData] = useState<Record<string, { price: number; change_percent: number }>>({});

    // Fetch market data for all assets
    const fetchMarketData = useCallback(async () => {
        try {
            const symbols = WAR_ASSETS.map(a => a.symbol).join(',');
            const res = await fetch(`${API_BASE}/api/market?symbols=${symbols}`, {
                headers: getHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                const dataMap: Record<string, { price: number; change_percent: number }> = {};
                data.symbols?.forEach((s: { symbol: string; price: number; change_percent: number }) => {
                    dataMap[s.symbol] = { price: s.price, change_percent: s.change_percent };
                });
                setMarketData(dataMap);
            }
        } catch (e) {
            console.error('War Room fetch error:', e);
        }
    }, []);

    useEffect(() => {
        fetchMarketData();
        const interval = setInterval(fetchMarketData, 30000);
        return () => clearInterval(interval);
    }, [fetchMarketData]);

    // Panic Button Handler - REAL LIQUIDATION
    const handlePanic = async () => {
        if (!panicConfirm) {
            setPanicConfirm(true);
            setTimeout(() => setPanicConfirm(false), 5000); // Reset after 5 seconds
            return;
        }

        // Execute panic sell via API
        try {
            const res = await fetch(`${API_BASE}/api/trade/panic`, {
                method: 'POST',
                headers: getHeaders()
            });
            const data = await res.json();

            if (data.status === 'LIQUIDATING') {
                alert(`🚨 PANIC PROTOCOL EXECUTED!\n\n${data.message}\n\nCheck Telegram for confirmation.`);
            } else {
                alert(`⚠️ Panic Protocol Status: ${data.status}\n\n${data.message || data.error || 'Unknown error'}`);
            }
        } catch (error) {
            alert('⚠️ Panic protocol failed - network error');
            console.error('Panic error:', error);
        }
        setPanicConfirm(false);
    };

    return (
        <div className="flex flex-col h-full w-full animate-fade-in bg-[#050505]">

            {/* 🔴 DEFCON Header */}
            <div className="flex justify-between items-center p-3 mb-3 bg-gradient-to-r from-red-950/30 to-transparent border border-red-900/40 rounded-xl">
                <div className="flex items-center gap-4">
                    {/* Status */}
                    <div className="flex items-center gap-2 text-red-500">
                        <Activity size={18} className="animate-pulse" />
                        <span className="font-bold text-xs tracking-[0.3em] uppercase">DEFCON 1</span>
                    </div>

                    <div className="h-5 w-px bg-red-900/50"></div>

                    {/* Global Timeframe Selector */}
                    <div className="flex gap-1 bg-black/40 p-1 rounded-lg">
                        {['15m', '1H', '4H', '1D'].map((tf) => (
                            <button
                                key={tf}
                                onClick={() => onTimeframeChange(tf)}
                                className={`px-3 py-1 text-[10px] font-bold rounded transition-all ${globalTimeframe === tf
                                    ? 'bg-red-600 text-white shadow-[0_0_15px_rgba(220,38,38,0.5)]'
                                    : 'text-gray-500 hover:text-red-400'
                                    }`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>

                {/* 🚨 PANIC BUTTON */}
                <button
                    onClick={handlePanic}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-xs tracking-widest transition-all ${panicConfirm
                        ? 'bg-red-600 text-white animate-pulse shadow-[0_0_30px_rgba(220,38,38,0.6)]'
                        : 'bg-red-950/50 border border-red-600/50 text-red-500 hover:bg-red-600 hover:text-white'
                        }`}
                >
                    {panicConfirm ? (
                        <>
                            <Skull size={16} className="animate-bounce" />
                            CONFIRM LIQUIDATION
                        </>
                    ) : (
                        <>
                            <AlertOctagon size={14} />
                            FLATTEN ALL
                        </>
                    )}
                </button>
            </div>

            {/* 📊 The 2x2 Smart Grid */}
            <div className={`flex-1 grid gap-3 overflow-hidden transition-all duration-500 ${expandedCell
                ? 'grid-cols-1 grid-rows-1'
                : 'grid-cols-1 md:grid-cols-2 grid-rows-2'
                }`}>
                {WAR_ASSETS.map((asset) => {
                    // If expanded, hide others
                    if (expandedCell && expandedCell !== asset.symbol) return null;

                    const stats = marketData[asset.symbol] || { price: 0, change_percent: 0 };

                    return (
                        <WarRoomCell
                            key={asset.symbol}
                            symbol={asset.symbol}
                            name={asset.name}
                            type={asset.type}
                            timeframe={globalTimeframe}
                            price={stats.price}
                            changePercent={stats.change_percent}
                            isExpanded={expandedCell === asset.symbol}
                            onToggleExpand={() => setExpandedCell(expandedCell === asset.symbol ? null : asset.symbol)}
                        />
                    );
                })}
            </div>
        </div>
    );
}

// ==================== WAR ROOM CELL ====================
interface WarRoomCellProps {
    symbol: string;
    name: string;
    type: string;
    timeframe: string;
    price: number;
    changePercent: number;
    isExpanded: boolean;
    onToggleExpand: () => void;
}

function WarRoomCell({ symbol, name, type, timeframe, price, changePercent, isExpanded, onToggleExpand }: WarRoomCellProps) {
    const isBullish = changePercent >= 0;

    // Dynamic Heat Map Border
    const borderColor = isBullish
        ? 'border-emerald-500/40 hover:border-emerald-500/60'
        : 'border-rose-500/40 hover:border-rose-500/60';

    const glowEffect = isBullish
        ? 'shadow-[0_0_30px_rgba(16,185,129,0.08)]'
        : 'shadow-[0_0_30px_rgba(239,68,68,0.08)]';

    return (
        <div className={`relative border-2 rounded-xl overflow-hidden bg-black/70 backdrop-blur-sm transition-all duration-300 group ${borderColor} ${glowEffect} ${isExpanded ? 'z-50' : ''}`}>

            {/* 📊 Quick Stats Overlay */}
            <div className="absolute top-3 left-3 z-20 pointer-events-none">
                <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-white text-sm tracking-wide">{symbol}</span>
                    <span className="text-[9px] text-gray-500 bg-gray-900/80 px-1.5 py-0.5 rounded">{type}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`text-xl font-mono font-bold ${isBullish ? 'text-emerald-400' : 'text-rose-400'}`}>
                        ${price > 0 ? price.toLocaleString() : '---'}
                    </span>
                    <span className={`text-xs font-bold px-2 py-0.5 rounded ${isBullish
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        }`}>
                        {changePercent > 0 ? '+' : ''}{changePercent.toFixed(2)}%
                    </span>
                </div>
                <span className="text-[10px] text-gray-600">{name}</span>
            </div>

            {/* 🔍 Expand/Collapse Button */}
            <button
                onClick={onToggleExpand}
                className="absolute top-3 right-3 z-20 p-2 text-gray-500 hover:text-white bg-black/40 hover:bg-black/80 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                title={isExpanded ? 'Minimize' : 'Maximize'}
            >
                {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>

            {/* 📈 The Chart */}
            <div className="w-full h-full opacity-70 group-hover:opacity-100 transition-opacity pt-16">
                <TradingChart
                    symbol={symbol}
                    timeframe={timeframe}
                    hideControls={true}
                />
            </div>
        </div>
    );
}
