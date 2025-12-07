"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
    Newspaper, Activity, ArrowUpRight, ArrowDownRight,
    Send, Zap, RefreshCw, Wallet, LayoutGrid, Maximize
} from 'lucide-react';
import { TradingChart } from '@/components/TradingChart';
import { WarRoom } from '@/components/WarRoom';

// 🔗 Backend API Configuration
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://trading-brain-v1.amrikyy.workers.dev";
const SYSTEM_KEY = process.env.NEXT_PUBLIC_SYSTEM_KEY || "";

// 🛡️ Secure Headers
const getHeaders = () => ({
    'Content-Type': 'application/json',
    ...(SYSTEM_KEY && { 'X-System-Key': SYSTEM_KEY })
});

// Market symbol type
interface MarketSymbol {
    symbol: string;
    price: number;
    change_percent: number;
    volume?: number;
}

// ==================== DASHBOARD 2.0 ====================
export default function Dashboard() {
    // State
    const [messages, setMessages] = useState<{ role: string; content: string }[]>([
        { role: 'system', content: '🦅 Antigravity System Online. Connected to Google News & Alpaca. Try: "Analyze BTC" or "Buy 1 AAPL"' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [activeSymbol, setActiveSymbol] = useState('SPY');
    const [activeTimeframe, setActiveTimeframe] = useState('1H');
    const [news, setNews] = useState<string | null>(null);
    const [portfolio, setPortfolio] = useState({ portfolio_value: '100000', buying_power: '200000', equity: '100000' });
    const [systemStatus, setSystemStatus] = useState({ status: 'offline', trades_today: 0, ai: 'Loading...' });
    const [watchlist, setWatchlist] = useState<MarketSymbol[]>([
        { symbol: 'SPY', price: 0, change_percent: 0 },
        { symbol: 'AAPL', price: 0, change_percent: 0 },
        { symbol: 'BTC', price: 0, change_percent: 0 },
        { symbol: 'ETH', price: 0, change_percent: 0 },
    ]);
    const [viewMode, setViewMode] = useState<'STANDARD' | 'WAR_ROOM'>('STANDARD');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // 📡 Fetch System Data
    const fetchSystemData = useCallback(async () => {
        try {
            // Status
            const statusRes = await fetch(`${API_BASE}/api/status`);
            if (statusRes.ok) setSystemStatus(await statusRes.json());

            // Account (protected endpoint)
            const accountRes = await fetch(`${API_BASE}/api/account`, {
                headers: getHeaders()
            });
            if (accountRes.ok) setPortfolio(await accountRes.json());
        } catch (e) {
            console.error('System fetch error:', e);
        }
    }, []);

    // 📈 Fetch Market Data (Real-time prices)
    const fetchMarketData = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/market?symbols=SPY,AAPL,BTC,ETH`, {
                headers: getHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                if (data.symbols) {
                    setWatchlist(data.symbols);
                }
            }
        } catch (e) {
            console.error('Market data error:', e);
        }
    }, []);

    // 📰 Fetch News for Symbol
    const fetchNews = useCallback(async (symbol: string) => {
        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ message: `Analyze ${symbol}` })
            });
            const data = await res.json();
            if (data.reply) {
                setNews(data.reply);
            }
        } catch {
            setNews('⚠️ Unable to fetch market intelligence.');
        }
    }, []);

    // Initial Load
    useEffect(() => {
        fetchSystemData();
        fetchMarketData();
        fetchNews(activeSymbol);
        const interval = setInterval(() => {
            fetchSystemData();
            fetchMarketData();
        }, 30000);
        return () => clearInterval(interval);
    }, [fetchSystemData, fetchMarketData, fetchNews, activeSymbol]);

    // Auto-scroll chat
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // 💬 Handle Chat Command
    const handleSend = async () => {
        if (!input.trim()) return;
        const userMsg = input;
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ message: userMsg })
            });
            const data = await res.json();

            // Update chart if SHOW_CHART
            if (data.type === 'SHOW_CHART' && data.symbol) {
                setActiveSymbol(data.symbol);
            }

            // Update news if RESEARCH
            if (data.type === 'RESEARCH') {
                setNews(data.reply);
            }

            // Refresh data if trade executed
            if (data.trade_executed?.status === 'success') {
                setTimeout(fetchSystemData, 1000);
            }

            setMessages(prev => [...prev, { role: 'ai', content: data.reply || JSON.stringify(data) }]);
        } catch {
            setMessages(prev => [...prev, { role: 'ai', content: '⚠️ Connection error. Please try again.' }]);
        }
        setLoading(false);
    };

    // Handle timeframe change
    const handleTimeframeChange = (tf: string) => {
        setActiveTimeframe(tf);
    };

    return (
        <div className="flex flex-col h-full p-6 gap-6 overflow-hidden">

            {/* 📊 Top Stats Row */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 animate-slide-up">
                <StatCard
                    title="Portfolio Value"
                    value={`$${parseFloat(portfolio.portfolio_value).toLocaleString()}`}
                    change="+2.4%"
                    positive={true}
                    icon={<Wallet className="text-cyan-400" size={20} />}
                />
                <StatCard
                    title="Buying Power"
                    value={`$${parseFloat(portfolio.buying_power).toLocaleString()}`}
                    icon={<ArrowUpRight className="text-emerald-400" size={20} />}
                />
                <StatCard
                    title="Trades Today"
                    value={`${systemStatus.trades_today} / 10`}
                    icon={<Activity className="text-purple-400" size={20} />}
                />
                <StatCard
                    title="AI Status"
                    value={systemStatus.status === 'online' ? 'ONLINE' : 'OFFLINE'}
                    icon={<Zap className={systemStatus.status === 'online' ? 'text-yellow-400' : 'text-gray-500'} size={20} />}
                    status={systemStatus.status}
                />
            </div>

            {/* 📈 Main Workspace (Split View) */}
            <div className="flex-1 flex gap-6 overflow-hidden">

                {/* LEFT: Market Data */}
                <div className="flex-[2] flex flex-col gap-4 animate-slide-up delay-200">

                    {/* 🔴 Mode Switch (Top Right) */}
                    <div className="flex justify-end gap-2 -mb-12 z-20 relative mr-2">
                        <button
                            onClick={() => setViewMode('STANDARD')}
                            className={`p-2 rounded-lg backdrop-blur border transition-all ${viewMode === 'STANDARD'
                                ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                                : 'bg-black/50 border-gray-800 text-gray-500 hover:text-white'
                                }`}
                            title="Standard View"
                        >
                            <Maximize size={16} />
                        </button>
                        <button
                            onClick={() => setViewMode('WAR_ROOM')}
                            className={`p-2 rounded-lg backdrop-blur border transition-all ${viewMode === 'WAR_ROOM'
                                ? 'bg-red-500/20 border-red-500 text-red-400 shadow-[0_0_15px_rgba(220,38,38,0.3)]'
                                : 'bg-black/50 border-gray-800 text-gray-500 hover:text-red-400'
                                }`}
                            title="Enter War Room (4 Charts)"
                        >
                            <LayoutGrid size={16} />
                        </button>
                    </div>

                    {/* Chart Container - Conditional Rendering */}
                    <div className="glass-card p-0 flex-1 relative overflow-hidden hover-glow-border">
                        {viewMode === 'STANDARD' ? (
                            <>
                                {/* Standard Mode: Single Chart */}
                                {/* Chart Header - Watchlist with Real Data */}
                                <div className="absolute top-4 left-4 z-10 flex gap-2 flex-wrap">
                                    {watchlist.map(item => (
                                        <button
                                            key={item.symbol}
                                            onClick={() => {
                                                setActiveSymbol(item.symbol);
                                                fetchNews(item.symbol);
                                            }}
                                            className={`px-3 py-1.5 rounded-lg text-sm font-mono transition-all hover-scale ${activeSymbol === item.symbol
                                                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 glow-cyan'
                                                : 'bg-black/50 text-gray-400 border border-white/10 hover:text-white'
                                                }`}
                                        >
                                            {item.symbol}
                                            <span className={`ml-2 text-xs ${item.change_percent >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                                            </span>
                                        </button>
                                    ))}
                                </div>

                                {/* Timeframe Selector */}
                                <div className="absolute top-4 right-20 z-10 flex gap-1 bg-black/50 backdrop-blur-sm rounded-lg p-1 border border-gray-800/50">
                                    {['15m', '1H', '4H', '1D'].map((tf) => (
                                        <button
                                            key={tf}
                                            onClick={() => handleTimeframeChange(tf)}
                                            className={`px-2 py-1 text-xs rounded transition-all ${tf === activeTimeframe
                                                ? 'bg-cyan-500/20 text-cyan-400'
                                                : 'text-gray-500 hover:text-gray-300'
                                                }`}
                                        >
                                            {tf}
                                        </button>
                                    ))}
                                </div>

                                <div className="absolute top-4 right-4 z-10">
                                    <span className="bg-emerald-500/20 text-emerald-400 px-2 py-1 rounded text-xs border border-emerald-500/30 flex items-center gap-1">
                                        <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
                                        LIVE
                                    </span>
                                </div>
                                <TradingChart symbol={activeSymbol} timeframe={activeTimeframe} />
                            </>
                        ) : (
                            /* War Room Mode: 4 Charts Grid */
                            <WarRoom
                                globalTimeframe={activeTimeframe}
                                onTimeframeChange={handleTimeframeChange}
                            />
                        )}
                    </div>

                    {/* 📰 News Ticker (Google News) */}
                    <div className="h-44 glass-card p-4 overflow-hidden hover-glow-border">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2 text-xs text-gray-500 uppercase tracking-wider">
                                <Newspaper size={14} className="text-cyan-400" />
                                Market Intelligence ({activeSymbol})
                            </div>
                            <button
                                onClick={() => fetchNews(activeSymbol)}
                                className="p-1 hover:bg-white/5 rounded transition-colors"
                            >
                                <RefreshCw size={14} className="text-gray-500 hover:text-cyan-400" />
                            </button>
                        </div>
                        <div className="overflow-y-auto h-28 pr-2 custom-scrollbar">
                            {news ? (
                                <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-line animate-fade-in">
                                    {news}
                                </div>
                            ) : (
                                <div className="flex flex-col gap-2">
                                    <div className="h-3 bg-white/5 rounded w-3/4 animate-pulse"></div>
                                    <div className="h-3 bg-white/5 rounded w-1/2 animate-pulse"></div>
                                    <div className="h-3 bg-white/5 rounded w-2/3 animate-pulse"></div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* RIGHT: Sentinel Chat */}
                <div className="flex-1 glass-card flex flex-col overflow-hidden animate-slide-up delay-300 hover-glow-border">
                    {/* Chat Header */}
                    <div className="p-4 border-b border-white/5 bg-black/30 flex justify-between items-center">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg overflow-hidden ring-2 ring-cyan-500/30 bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                                <Zap size={16} className="text-white" />
                            </div>
                            <div>
                                <span className="font-semibold text-white text-sm">SENTINEL AI</span>
                                <p className="text-[10px] text-cyan-400 flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                                    Analyzing {activeSymbol}...
                                </p>
                            </div>
                        </div>
                        <span className="text-[10px] text-gray-500 font-mono">v2.0 PRO</span>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.map((msg, i) => (
                            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                                <div className={`max-w-[85%] p-3 rounded-xl text-sm ${msg.role === 'user'
                                    ? 'bg-cyan-600/20 text-cyan-100 border border-cyan-500/30'
                                    : 'bg-white/[0.03] text-gray-300 border border-white/5'
                                    }`}>
                                    <p className="whitespace-pre-wrap">{msg.content}</p>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-white/[0.03] border border-white/5 p-3 rounded-xl">
                                    <div className="typing-indicator">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input */}
                    <div className="p-4 bg-black/40 border-t border-white/5">
                        <div className="relative">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Command Sentinel (e.g., 'Analyze ETH')..."
                                className="w-full bg-[#0a0a0a] border border-white/10 rounded-xl py-3 px-4 pr-12 text-sm outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/30 transition-all placeholder:text-gray-600"
                            />
                            <button
                                onClick={handleSend}
                                disabled={loading}
                                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-all disabled:opacity-50 glow-cyan"
                            >
                                <Send size={16} className="text-white" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ==================== STAT CARD COMPONENT ====================
interface StatCardProps {
    title: string;
    value: string;
    change?: string;
    positive?: boolean;
    icon?: React.ReactNode;
    status?: string;
}

function StatCard({ title, value, change, positive, icon, status }: StatCardProps) {
    return (
        <div className="glass-card p-4 flex items-center justify-between hover:border-cyan-500/30 transition-all hover-glow-border cursor-default">
            <div>
                <p className="text-[10px] text-gray-500 uppercase tracking-widest">{title}</p>
                <h3 className={`text-xl font-bold mt-1 font-mono ${status === 'online' ? 'text-emerald-400' : status === 'offline' ? 'text-rose-400' : 'text-white'}`}>
                    {value}
                </h3>
                {change && (
                    <span className={`text-xs flex items-center gap-0.5 ${positive ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {positive ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />} {change}
                    </span>
                )}
            </div>
            <div className="opacity-60">{icon}</div>
        </div>
    );
}
