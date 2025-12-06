"use client";
import React, { useState, useEffect, useCallback } from 'react';
import { Bot, Plus, Trash2, Power, RefreshCw, Zap, Clock } from 'lucide-react';

const API_BASE = "https://trading-brain-v1.amrikyy1.workers.dev";

interface TradingRule {
    rule_id: string;
    ticker: string;
    logic_json: string;
    status: string;
    created_at?: string;
}

export default function AutomationPage() {
    const [rules, setRules] = useState<TradingRule[]>([]);
    const [loading, setLoading] = useState(true);
    const [newRule, setNewRule] = useState({ ticker: 'SPY', condition: 'PRICE_BELOW', trigger: '590', action: 'BUY', qty: '5' });

    const fetchRules = useCallback(async () => {
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/rules`);
            if (res.ok) {
                const data = await res.json();
                setRules(data.rules || []);
            }
        } catch (e) { console.error(e); }
        setLoading(false);
    }, []);

    useEffect(() => { fetchRules(); }, [fetchRules]);

    const createRule = async () => {
        const ruleText = `If ${newRule.ticker} ${newRule.condition.replace('_', ' ').toLowerCase()} ${newRule.trigger}, ${newRule.action} ${newRule.qty} shares`;

        try {
            const res = await fetch(`${API_BASE}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: ruleText })
            });
            const data = await res.json();
            if (data.rule_saved) {
                fetchRules();
            }
        } catch (e) { console.error(e); }
    };

    return (
        <div className="p-8 h-full overflow-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-white">Auto-Pilot</h1>
                    <p className="text-gray-500 text-sm">Automated trading rules executed every minute</p>
                </div>
                <button onClick={fetchRules} className="flex items-center gap-2 px-4 py-2 bg-gray-800 rounded-lg text-gray-400 hover:text-white">
                    <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Status */}
            <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-cyan-500/30 rounded-xl p-6 mb-8">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-cyan-500/20 rounded-xl flex items-center justify-center">
                            <Zap size={24} className="text-cyan-400" />
                        </div>
                        <div>
                            <h3 className="font-bold text-white">Cron Job Active</h3>
                            <p className="text-sm text-gray-400">Rules evaluated every minute (24/7)</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
                        <span className="text-green-400 font-bold">Running</span>
                    </div>
                </div>
            </div>

            {/* Create Rule */}
            <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6 mb-8">
                <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                    <Plus size={18} /> Create New Rule
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Symbol</label>
                        <input type="text" value={newRule.ticker} onChange={(e) => setNewRule({ ...newRule, ticker: e.target.value.toUpperCase() })}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 text-sm outline-none focus:border-cyan-500/50" />
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Condition</label>
                        <select value={newRule.condition} onChange={(e) => setNewRule({ ...newRule, condition: e.target.value })}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 text-sm outline-none">
                            <option value="PRICE_BELOW">Price Below</option>
                            <option value="PRICE_ABOVE">Price Above</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Trigger</label>
                        <input type="number" value={newRule.trigger} onChange={(e) => setNewRule({ ...newRule, trigger: e.target.value })}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 text-sm outline-none focus:border-cyan-500/50" />
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Action</label>
                        <select value={newRule.action} onChange={(e) => setNewRule({ ...newRule, action: e.target.value })}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 text-sm outline-none">
                            <option value="BUY">Buy</option>
                            <option value="SELL">Sell</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 block mb-1">Qty</label>
                        <input type="number" value={newRule.qty} onChange={(e) => setNewRule({ ...newRule, qty: e.target.value })}
                            className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-2 px-3 text-sm outline-none focus:border-cyan-500/50" />
                    </div>

                    <div className="flex items-end">
                        <button onClick={createRule}
                            className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-2 px-4 rounded-lg font-bold hover:shadow-lg hover:shadow-cyan-500/20 transition-all">
                            Create
                        </button>
                    </div>
                </div>
            </div>

            {/* Active Rules */}
            <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl overflow-hidden">
                <div className="p-4 border-b border-gray-800">
                    <h2 className="font-bold text-white">Active Rules ({rules.length})</h2>
                </div>

                {rules.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No active rules. Create one above or use natural language: &quot;Buy 5 SPY if price drops below 590&quot;
                    </div>
                ) : (
                    <div className="divide-y divide-gray-800">
                        {rules.map((rule, i) => {
                            let logic = {};
                            try { logic = JSON.parse(rule.logic_json); } catch { }

                            return (
                                <div key={i} className="p-4 flex items-center justify-between hover:bg-gray-900/50">
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                                            <Bot size={18} className="text-green-400" />
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">
                                                {rule.ticker}: {(logic as { condition?: string }).condition?.replace('_', ' ')} {(logic as { trigger?: number }).trigger} → {(logic as { action?: string }).action} {(logic as { qty?: number }).qty}
                                            </p>
                                            <p className="text-xs text-gray-500 flex items-center gap-1">
                                                <Clock size={12} /> ID: {rule.rule_id}
                                            </p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${rule.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                                            }`}>
                                            {rule.status?.toUpperCase()}
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}
