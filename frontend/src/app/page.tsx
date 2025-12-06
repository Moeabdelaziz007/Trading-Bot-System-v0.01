"use client";
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Bot, User, TrendingUp, AlertCircle, Newspaper, Wallet, Activity } from 'lucide-react';
import { TradingChart } from '@/components/TradingChart';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface Message {
    role: 'user' | 'system';
    type: 'text' | 'trade_card' | 'error';
    content: string;
    details?: { symbol?: string; side?: string; qty?: number; order_id?: string; };
}

interface Portfolio {
    portfolio_value: string;
    buying_power: string;
    cash: string;
}

export default function Dashboard() {
    const [messages, setMessages] = useState<Message[]>([
        { role: 'system', type: 'text', content: '🧠 AntigravityTradingLLM Online. Try: "Analyze SPY", "Buy 5 AAPL", or "Check news on TSLA"' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
    const [activeSymbol, setActiveSymbol] = useState('SPY');
    const [systemStatus, setSystemStatus] = useState<{ trades_today: number, max_trades: number }>({ trades_today: 0, max_trades: 10 });
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const fetchPortfolio = useCallback(async () => {
        try {
            const [accountRes, statusRes] = await Promise.all([
                fetch(`${API_BASE}/api/account`),
                fetch(`${API_BASE}/api/status`)
            ]);
            if (accountRes.ok) setPortfolio(await accountRes.json());
            if (statusRes.ok) setSystemStatus(await statusRes.json());
        } catch (e) { console.error(e); }
    }, []);

    useEffect(() => {
        fetchPortfolio();
        const interval = setInterval(fetchPortfolio, 30000);
        return () => clearInterval(interval);
    }, [fetchPortfolio]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMsg: Message = { role: 'user', type: 'text', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.content })
            });
            const data = await res.json();

            if (data.type === 'SHOW_CHART' && data.symbol) setActiveSymbol(data.symbol);

            let aiMsg: Message;
            if (data.trade_executed?.status === 'success') {
                aiMsg = { role: 'system', type: 'trade_card', content: data.trade_executed.message, details: data.trade_executed };
                setTimeout(fetchPortfolio, 1000);
            } else {
                aiMsg = { role: 'system', type: 'text', content: data.reply || JSON.stringify(data) };
            }
            setMessages(prev => [...prev, aiMsg]);
        } catch {
            setMessages(prev => [...prev, { role: 'system', type: 'error', content: "⚠️ Connection failed." }]);
        } finally {
            setLoading(false);
        }
    };

    const watchlist = ['SPY', 'AAPL', 'TSLA', 'GOOGL', 'GLD', 'BTC'];

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Top Bar */}
            <header className="h-16 bg-[#0a0a0a] border-b border-gray-800/50 flex items-center justify-between px-6 shrink-0">
                <div className="flex items-center gap-4">
                    <h1 className="text-lg font-bold">Dashboard</h1>
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/10 border border-green-500/30">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-green-400 text-xs">Live</span>
                    </div>
                </div>
                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <Wallet size={16} className="text-gray-500" />
                        <span className="text-sm">${portfolio ? parseFloat(portfolio.portfolio_value).toLocaleString() : '100,000'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Activity size={16} className="text-gray-500" />
                        <span className="text-sm text-gray-400">{systemStatus.trades_today}/{systemStatus.max_trades}</span>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left: Chart */}
                <div className="flex-1 flex flex-col p-6 gap-4 overflow-hidden">
                    {/* Watchlist */}
                    <div className="flex gap-2 overflow-x-auto shrink-0">
                        {watchlist.map((s) => (
                            <button key={s} onClick={() => setActiveSymbol(s)}
                                className={`px-4 py-2 rounded-lg transition-all whitespace-nowrap ${activeSymbol === s ? 'bg-cyan-500/20 border border-cyan-500/30 text-cyan-400' : 'bg-gray-900/50 border border-gray-800/50 text-gray-400'
                                    }`}
                            >{s}</button>
                        ))}
                    </div>

                    {/* Chart */}
                    <div className="flex-1 min-h-[350px]">
                        <TradingChart symbol={activeSymbol} timeframe="1H" />
                    </div>

                    {/* News */}
                    <div className="h-28 bg-[#0a0a0a] border border-gray-800/50 rounded-xl p-4 shrink-0">
                        <div className="flex items-center gap-2 mb-2">
                            <Newspaper size={14} className="text-cyan-400" />
                            <span className="text-xs font-bold text-gray-400 uppercase">Market Intel</span>
                        </div>
                        <p className="text-sm text-gray-500">Ask AI: &quot;Check news on {activeSymbol}&quot;</p>
                    </div>
                </div>

                {/* Right: Chat */}
                <div className="w-[360px] bg-[#0a0a0a]/80 border-l border-gray-800/50 flex flex-col shrink-0">
                    <div className="p-4 border-b border-gray-800/50 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                            <Bot size={20} className="text-white" />
                        </div>
                        <div>
                            <h2 className="font-bold">Sentinel AI</h2>
                            <p className="text-xs text-green-400">Ready</p>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3">
                        {messages.map((msg, i) => (
                            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`flex gap-2 max-w-[90%] ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                    <div className={`w-6 h-6 rounded-lg flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-cyan-500/20' : 'bg-green-500/20'}`}>
                                        {msg.role === 'user' ? <User size={12} className="text-cyan-400" /> : <Bot size={12} className="text-green-400" />}
                                    </div>
                                    <div className={`p-3 rounded-xl text-sm ${msg.role === 'user' ? 'bg-cyan-500/10 border border-cyan-500/20 text-cyan-100' : 'bg-gray-800/50 border border-gray-700/50 text-gray-300'}`}>
                                        {msg.type === 'text' && <p className="whitespace-pre-wrap">{msg.content}</p>}
                                        {msg.type === 'trade_card' && msg.details && (
                                            <div className="space-y-2">
                                                <div className="flex items-center gap-2 text-green-400 font-bold text-xs"><TrendingUp size={14} /> EXECUTED</div>
                                                <div className="grid grid-cols-2 gap-2 text-xs">
                                                    <div><span className="text-gray-500">Symbol</span><br /><span className="font-bold">{msg.details.symbol}</span></div>
                                                    <div><span className="text-gray-500">Side</span><br /><span className={msg.details.side === 'buy' ? 'text-green-400' : 'text-red-400'}>{msg.details.side?.toUpperCase()}</span></div>
                                                </div>
                                            </div>
                                        )}
                                        {msg.type === 'error' && <div className="flex items-center gap-2 text-red-400"><AlertCircle size={14} />{msg.content}</div>}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex gap-2">
                                <div className="w-6 h-6 rounded-lg bg-green-500/20 flex items-center justify-center"><Bot size={12} className="text-green-400" /></div>
                                <div className="flex items-center gap-1 h-6 px-3 bg-gray-800/50 rounded-xl">
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" />
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '75ms' }} />
                                    <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="p-4 border-t border-gray-800/50">
                        <div className="relative">
                            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Ask Sentinel..." className="w-full bg-gray-800/50 border border-gray-700/50 rounded-xl py-3 pl-4 pr-12 outline-none text-sm focus:border-cyan-500/50" />
                            <button onClick={handleSend} disabled={loading} className="absolute right-2 top-2 p-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg disabled:opacity-50">
                                <Send size={14} className="text-white" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
