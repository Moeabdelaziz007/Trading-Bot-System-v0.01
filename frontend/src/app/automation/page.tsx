"use client";
import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, LineChart, Wallet, History, Bot, Settings, LogOut, Zap,
    Plus, Power, TrendingUp, Activity, Clock, AlertTriangle, ChevronRight, User,
    ArrowUpRight, ArrowDownRight, Pause, Play, Trash2, Edit
} from 'lucide-react';

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
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-cyan-600 flex items-center justify-center glow-cyan">
                        <Zap size={20} className="text-white" />
                    </div>
                    <div>
                        <h1 className="font-semibold text-white tracking-tight">ANTIGRAVITY</h1>
                        <p className="text-[10px] text-gray-500 font-mono">v2.0 • Auto-Pilot</p>
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
                        <p className="text-xs text-gray-500">Algo Trader</p>
                    </div>
                    <span className="px-2 py-0.5 text-[10px] font-medium bg-emerald-500/20 text-emerald-400 rounded-full border border-emerald-500/30">HFT</span>
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
        </div>
    );
}

// ==================== TYPES ====================
interface Rule {
    id: number;
    ticker: string;
    condition: string;
    trigger_value: number;
    action: string;
    qty: number;
    active: number;
    winRate?: number;
    profit?: number;
}

interface LogEntry {
    id: number;
    time: string;
    rule: string;
    status: 'success' | 'pending' | 'failed';
    message: string;
}

// ==================== MAIN PAGE ====================
export default function AutomationPage() {
    const [rules, setRules] = useState<Rule[]>([
        { id: 1, ticker: 'BTC/USD', condition: 'PRICE_BELOW', trigger_value: 90000, action: 'BUY', qty: 0.1, active: 1, winRate: 72, profit: 1250 },
        { id: 2, ticker: 'TSLA', condition: 'PRICE_ABOVE', trigger_value: 400, action: 'SELL', qty: 10, active: 1, winRate: 65, profit: 890 },
        { id: 3, ticker: 'SPY', condition: 'PRICE_BELOW', trigger_value: 580, action: 'BUY', qty: 5, active: 0, winRate: 58, profit: -120 },
    ]);

    const [logs] = useState<LogEntry[]>([
        { id: 1, time: '22:05:32', rule: 'BTC < $90k → BUY', status: 'success', message: 'Triggered: Bought 0.1 BTC @ $89,432' },
        { id: 2, time: '21:45:18', rule: 'TSLA > $400 → SELL', status: 'pending', message: 'Condition monitoring...' },
        { id: 3, time: '21:30:00', rule: 'SPY < $580 → BUY', status: 'failed', message: 'Insufficient buying power' },
        { id: 4, time: '21:15:42', rule: 'BTC < $90k → BUY', status: 'success', message: 'Triggered: Bought 0.1 BTC @ $88,950' },
    ]);

    const [showNewRule, setShowNewRule] = useState(false);

    const toggleRule = (id: number) => {
        setRules(prev => prev.map(r => r.id === id ? { ...r, active: r.active ? 0 : 1 } : r));
    };

    const activeRules = rules.filter(r => r.active).length;
    const triggersToday = logs.filter(l => l.status === 'success').length;
    const totalProfit = rules.reduce((acc, r) => acc + (r.profit || 0), 0);

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar />

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Top Bar */}
                <header className="h-14 glass-card-strong border-b border-white/5 flex items-center justify-between px-6 shrink-0">
                    <div className="flex items-center gap-4">
                        <Bot size={20} className="text-cyan-400" />
                        <h1 className="text-lg font-semibold text-white">Auto-Pilot • Algorithm Manager</h1>
                    </div>
                    <button
                        onClick={() => setShowNewRule(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Plus size={18} />
                        <span>New Algorithm</span>
                    </button>
                </header>

                {/* Content */}
                <div className="flex-1 p-6 overflow-auto">
                    {/* Stats Header */}
                    <div className="grid grid-cols-3 gap-4 mb-6">
                        <div className="stat-card">
                            <div className="flex items-center justify-between mb-2">
                                <span className="stat-label">Active Rules</span>
                                <Power size={16} className="text-cyan-400" />
                            </div>
                            <div className="stat-value text-cyan-400">{activeRules}</div>
                            <p className="text-xs text-gray-500 mt-1">{rules.length} total configured</p>
                        </div>

                        <div className="stat-card">
                            <div className="flex items-center justify-between mb-2">
                                <span className="stat-label">Triggers Today</span>
                                <Activity size={16} className="text-emerald-400" />
                            </div>
                            <div className="stat-value text-emerald-400">{triggersToday}</div>
                            <p className="text-xs text-gray-500 mt-1">Last 24 hours</p>
                        </div>

                        <div className="stat-card">
                            <div className="flex items-center justify-between mb-2">
                                <span className="stat-label">Est. Alpha</span>
                                {totalProfit >= 0 ?
                                    <ArrowUpRight size={16} className="text-emerald-400" /> :
                                    <ArrowDownRight size={16} className="text-rose-400" />
                                }
                            </div>
                            <div className={`stat-value ${totalProfit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {totalProfit >= 0 ? '+' : ''}${totalProfit.toLocaleString()}
                            </div>
                            <p className="text-xs text-gray-500 mt-1">This month</p>
                        </div>
                    </div>

                    {/* Rule Cards Grid */}
                    <div className="mb-6">
                        <h2 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                            <Zap size={14} />
                            TRADING ALGORITHMS
                        </h2>
                        <div className="grid grid-cols-2 gap-4">
                            {rules.map((rule) => (
                                <RuleCard key={rule.id} rule={rule} onToggle={toggleRule} />
                            ))}

                            {/* Add New Card */}
                            <button
                                onClick={() => setShowNewRule(true)}
                                className="glass-card border border-dashed border-white/10 hover:border-cyan-500/30 p-6 flex flex-col items-center justify-center gap-3 transition-all group min-h-[180px]"
                            >
                                <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center group-hover:bg-cyan-500/10 transition-colors">
                                    <Plus size={24} className="text-gray-500 group-hover:text-cyan-400" />
                                </div>
                                <span className="text-sm text-gray-500 group-hover:text-gray-300">Create New Algorithm</span>
                            </button>
                        </div>
                    </div>

                    {/* Activity Log */}
                    <div>
                        <h2 className="text-sm font-medium text-gray-400 mb-4 flex items-center gap-2">
                            <Clock size={14} />
                            RECENT ACTIVITY
                        </h2>
                        <div className="glass-card overflow-hidden">
                            <div className="bg-black/30 border-b border-white/5 px-4 py-2 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                <span className="text-xs text-gray-400 font-mono">system.log — live</span>
                            </div>
                            <div className="p-4 font-mono text-sm space-y-2 max-h-[200px] overflow-y-auto">
                                {logs.map((log) => (
                                    <div key={log.id} className="flex items-start gap-3">
                                        <span className="text-gray-600 text-xs">[{log.time}]</span>
                                        <span className={`text-xs px-1.5 py-0.5 rounded ${log.status === 'success' ? 'bg-emerald-500/20 text-emerald-400' :
                                                log.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-rose-500/20 text-rose-400'
                                            }`}>
                                            {log.status.toUpperCase()}
                                        </span>
                                        <div className="flex-1">
                                            <span className="text-cyan-400">{log.rule}</span>
                                            <span className="text-gray-400 ml-2">— {log.message}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* New Rule Modal */}
            {showNewRule && <NewRuleModal onClose={() => setShowNewRule(false)} />}
        </div>
    );
}

// ==================== RULE CARD ====================
function RuleCard({ rule, onToggle }: { rule: Rule; onToggle: (id: number) => void }) {
    const conditionText = rule.condition === 'PRICE_BELOW' ? '<' : '>';
    const isProfit = (rule.profit || 0) >= 0;

    return (
        <div className={`glass-card p-5 transition-all ${rule.active ? 'border-emerald-500/20' : 'opacity-60'}`}>
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${rule.action === 'BUY' ? 'bg-emerald-500/20' : 'bg-rose-500/20'
                        }`}>
                        {rule.action === 'BUY' ?
                            <ArrowUpRight className="text-emerald-400" size={20} /> :
                            <ArrowDownRight className="text-rose-400" size={20} />
                        }
                    </div>
                    <div>
                        <h3 className="font-mono font-semibold text-white">{rule.ticker}</h3>
                        <p className="text-xs text-gray-500">{rule.action} {rule.qty} units</p>
                    </div>
                </div>

                {/* Toggle */}
                <button
                    onClick={() => onToggle(rule.id)}
                    className={`relative w-12 h-6 rounded-full transition-all ${rule.active ? 'bg-emerald-500/30' : 'bg-gray-700'
                        }`}
                >
                    <span className={`absolute top-1 w-4 h-4 rounded-full transition-all ${rule.active ? 'left-7 bg-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.5)]' : 'left-1 bg-gray-500'
                        }`}></span>
                </button>
            </div>

            {/* Logic Display */}
            <div className="bg-black/30 rounded-lg p-3 mb-4 font-mono text-sm">
                <span className="text-purple-400">IF</span>
                <span className="text-white mx-2">{rule.ticker}</span>
                <span className={`px-1.5 py-0.5 rounded text-xs ${conditionText === '<' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'
                    }`}>{conditionText}</span>
                <span className="text-cyan-400 mx-2">${rule.trigger_value.toLocaleString()}</span>
                <span className="text-yellow-400">THEN</span>
                <span className={`ml-2 px-2 py-0.5 rounded text-xs ${rule.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                    }`}>{rule.action}</span>
            </div>

            {/* Stats */}
            <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-4">
                    <div>
                        <span className="text-gray-500">Win Rate</span>
                        <span className="ml-2 text-white font-mono">{rule.winRate}%</span>
                    </div>
                    <div>
                        <span className="text-gray-500">P&L</span>
                        <span className={`ml-2 font-mono ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isProfit ? '+' : ''}${rule.profit}
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
                        <Edit size={14} className="text-gray-500 hover:text-white" />
                    </button>
                    <button className="p-1.5 hover:bg-white/5 rounded-lg transition-colors">
                        <Trash2 size={14} className="text-gray-500 hover:text-rose-400" />
                    </button>
                </div>
            </div>
        </div>
    );
}

// ==================== NEW RULE MODAL ====================
function NewRuleModal({ onClose }: { onClose: () => void }) {
    return (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50" onClick={onClose}>
            <div className="glass-card-strong w-full max-w-lg p-6" onClick={e => e.stopPropagation()}>
                <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
                    <Zap size={20} className="text-cyan-400" />
                    Create New Algorithm
                </h2>

                <div className="space-y-4">
                    <div>
                        <label className="text-sm text-gray-400 block mb-2">Asset Symbol</label>
                        <input type="text" placeholder="e.g., AAPL, BTC/USD" className="chat-input" />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Condition</label>
                            <select className="chat-input">
                                <option>Price Below</option>
                                <option>Price Above</option>
                                <option>RSI Below</option>
                                <option>RSI Above</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Trigger Value</label>
                            <input type="number" placeholder="100.00" className="chat-input" />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Action</label>
                            <select className="chat-input">
                                <option>BUY</option>
                                <option>SELL</option>
                            </select>
                        </div>
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Quantity</label>
                            <input type="number" placeholder="10" className="chat-input" />
                        </div>
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <button onClick={onClose} className="flex-1 py-3 rounded-xl border border-white/10 text-gray-400 hover:bg-white/5 transition-colors">
                        Cancel
                    </button>
                    <button className="flex-1 btn-primary">
                        Create Algorithm
                    </button>
                </div>
            </div>
        </div>
    );
}
