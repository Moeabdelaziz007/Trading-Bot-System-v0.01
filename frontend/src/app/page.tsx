"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, LineChart, Wallet, History, Bot, Settings, LogOut, Zap,
    Send, TrendingUp, TrendingDown, Activity, Bell, User, ChevronRight
} from 'lucide-react';
import { TradingChart } from '@/components/TradingChart';

const API_BASE = "https://trading-brain-v1.amrikyy.workers.dev";

// ==================== SIDEBAR ====================
const routes = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/trade', icon: LineChart, label: 'Terminal' },
    { path: '/portfolio', icon: Wallet, label: 'Portfolio' },
    { path: '/history', icon: History, label: 'History' },
    { path: '/automation', icon: Bot, label: 'Auto-Pilot' },
];

function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="w-64 h-screen glass-card-strong flex flex-col shrink-0 border-r border-white/5">
            {/* Logo */}
            <div className="p-5 border-b border-white/5">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl overflow-hidden glow-cyan">
                        <img src="/logo.png" alt="Antigravity" className="w-full h-full object-cover" />
                    </div>
                    <div>
                        <h1 className="font-semibold text-white tracking-tight">ANTIGRAVITY</h1>
                        <p className="text-[10px] text-gray-500 font-mono">v2.0 • MoE Brain</p>
                    </div>
                </div>
            </div>

            {/* User Profile */}
            <div className="p-4 border-b border-white/5">
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02]">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <User size={16} className="text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">Mohamed</p>
                        <p className="text-xs text-gray-500">Pro Trader</p>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-medium bg-cyan-500/20 text-cyan-400 rounded-full border border-cyan-500/30">PRO</span>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1">
                {routes.map((route) => {
                    const Icon = route.icon;
                    const isActive = pathname === route.path;
                    return (
                        <Link key={route.path} href={route.path} className={`nav-item ${isActive ? 'active' : ''}`}>
                            <Icon size={18} />
                            <span className="text-sm font-medium">{route.label}</span>
                            {isActive && <ChevronRight size={14} className="ml-auto opacity-50" />}
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Actions */}
            <div className="p-3 border-t border-white/5 space-y-1">
                <Link href="/settings" className="nav-item">
                    <Settings size={18} />
                    <span className="text-sm">Settings</span>
                </Link>
                <button className="nav-item w-full text-left hover:text-red-400">
                    <LogOut size={18} />
                    <span className="text-sm">Disconnect</span>
                </button>
            </div>

            {/* Status */}
            <div className="p-4 border-t border-white/5">
                <div className="status-online">
                    <span className="status-dot"></span>
                    <span>Sentinel AI Online</span>
                </div>
            </div>
        </div>
    );
}

// ==================== STAT CARD ====================
function StatCard({ label, value, change, icon: Icon, color = 'cyan' }: {
    label: string;
    value: string;
    change?: string;
    icon: React.ElementType;
    color?: 'cyan' | 'green' | 'red';
}) {
    const colorClasses = {
        cyan: 'text-cyan-400',
        green: 'text-emerald-400',
        red: 'text-rose-400',
    };

    return (
        <div className="stat-card">
            <div className="flex items-center justify-between mb-2">
                <span className="stat-label">{label}</span>
                <Icon size={16} className={colorClasses[color]} />
            </div>
            <div className="stat-value">{value}</div>
            {change && (
                <div className={`flex items-center gap-1 mt-1 text-sm ${change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {change.startsWith('+') ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                    <span>{change}</span>
                </div>
            )}
        </div>
    );
}

// ==================== MAIN DASHBOARD ====================
export default function Dashboard() {
    const [messages, setMessages] = useState([
        { role: 'ai', content: '🧠 Sentinel AI Online. I can analyze markets, execute trades, or provide research. Try: "Analyze AAPL" or "Buy 5 TSLA"' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [portfolio, setPortfolio] = useState({ portfolio_value: '100000', buying_power: '200000' });
    const [activeSymbol, setActiveSymbol] = useState('SPY');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const watchlist = [
        { symbol: 'SPY', name: 'S&P 500', change: '+1.24%' },
        { symbol: 'AAPL', name: 'Apple', change: '+2.15%' },
        { symbol: 'TSLA', name: 'Tesla', change: '-0.87%' },
        { symbol: 'GOOGL', name: 'Alphabet', change: '+0.56%' },
    ];

    const fetchData = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/account`);
            if (res.ok) setPortfolio(await res.json());
        } catch (e) { console.error(e); }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [fetchData]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;
        setMessages(prev => [...prev, { role: 'user', content: input }]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input })
            });
            const data = await res.json();

            if (data.type === 'SHOW_CHART' && data.symbol) setActiveSymbol(data.symbol);
            if (data.trade_executed?.status === 'success') setTimeout(fetchData, 1000);

            setMessages(prev => [...prev, { role: 'ai', content: data.reply || JSON.stringify(data) }]);
        } catch {
            setMessages(prev => [...prev, { role: 'ai', content: '⚠️ Connection error. Please try again.' }]);
        }
        setLoading(false);
    };

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="h-14 glass-card-strong border-b border-white/5 flex items-center justify-between px-6 shrink-0">
                    <div className="flex items-center gap-4">
                        <h1 className="text-lg font-semibold text-white">Dashboard</h1>
                        <div className="status-online">
                            <span className="status-dot"></span>
                            <span>Live</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-4">
                        <button className="p-2 hover:bg-white/5 rounded-lg transition-colors relative">
                            <Bell size={18} className="text-gray-400" />
                            <span className="absolute top-1 right-1 w-2 h-2 bg-rose-500 rounded-full"></span>
                        </button>
                    </div>
                </header>

                {/* Dashboard Content */}
                <div className="flex-1 p-6 overflow-auto">
                    {/* Stats Row */}
                    <div className="grid grid-cols-4 gap-4 mb-6">
                        <div className="animate-slide-up delay-100">
                            <StatCard
                                label="Total Equity"
                                value={`$${parseFloat(portfolio.portfolio_value).toLocaleString()}`}
                                change="+2.4%"
                                icon={Wallet}
                                color="cyan"
                            />
                        </div>
                        <div className="animate-slide-up delay-200">
                            <StatCard
                                label="Buying Power"
                                value={`$${parseFloat(portfolio.buying_power).toLocaleString()}`}
                                icon={Activity}
                                color="green"
                            />
                        </div>
                        <div className="animate-slide-up delay-300">
                            <StatCard
                                label="Active Trades"
                                value="3"
                                icon={LineChart}
                                color="cyan"
                            />
                        </div>
                        <div className="animate-slide-up delay-400">
                            <StatCard
                                label="Win Rate"
                                value="68%"
                                change="+5%"
                                icon={TrendingUp}
                                color="green"
                            />
                        </div>
                    </div>

                    {/* Main Grid - 70/30 Split */}
                    <div className="grid grid-cols-10 gap-6" style={{ height: 'calc(100vh - 240px)' }}>
                        {/* Left - Chart (70%) */}
                        <div className="col-span-7 glass-card p-0 overflow-hidden flex flex-col animate-slide-up delay-200 hover-glow-border">
                            {/* Chart Header */}
                            <div className="flex items-center justify-between p-4 border-b border-white/5">
                                <div className="flex items-center gap-4">
                                    {watchlist.map((item) => (
                                        <button
                                            key={item.symbol}
                                            onClick={() => setActiveSymbol(item.symbol)}
                                            className={`px-3 py-1.5 text-sm rounded-lg transition-all hover-scale ${activeSymbol === item.symbol
                                                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                                }`}
                                        >
                                            <span className="font-mono font-medium">{item.symbol}</span>
                                            <span className={`ml-2 text-xs ${item.change.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                {item.change}
                                            </span>
                                        </button>
                                    ))}
                                </div>
                            </div>
                            {/* Chart */}
                            <div className="flex-1">
                                <TradingChart symbol={activeSymbol} timeframe="1H" />
                            </div>
                        </div>

                        {/* Right - Chat (30%) */}
                        <div className="col-span-3 chat-container animate-slide-up delay-300 hover-glow-border">
                            {/* Chat Header */}
                            <div className="flex items-center gap-3 p-4 border-b border-white/5">
                                <div className="w-10 h-10 rounded-lg overflow-hidden ring-2 ring-cyan-500/30 glow-cyan">
                                    <img src="/sentinel-avatar.png" alt="Sentinel AI" className="w-full h-full object-cover" />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-sm font-semibold text-white">Sentinel AI</h3>
                                    <p className="text-xs text-cyan-400 flex items-center gap-1">
                                        <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                                        Analyzing markets...
                                    </p>
                                </div>
                            </div>

                            {/* Messages */}
                            <div className="chat-messages">
                                {messages.map((msg, i) => (
                                    <div key={i} className={`${msg.role === 'user' ? 'chat-bubble-user' : 'chat-bubble-ai'} animate-fade-in`}>
                                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                                    </div>
                                ))}
                                {loading && (
                                    <div className="chat-bubble-ai">
                                        <div className="typing-indicator">
                                            <span></span><span></span><span></span>
                                        </div>
                                    </div>
                                )}
                                <div ref={messagesEndRef} />
                            </div>

                            {/* Input */}
                            <div className="chat-input-container">
                                <div className="relative">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Ask Sentinel AI..."
                                        className="chat-input pr-12"
                                    />
                                    <button
                                        onClick={handleSend}
                                        disabled={loading}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors disabled:opacity-50"
                                    >
                                        <Send size={16} className="text-white" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
