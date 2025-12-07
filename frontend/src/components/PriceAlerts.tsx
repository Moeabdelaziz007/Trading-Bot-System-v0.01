"use client";
import React, { useState } from 'react';
import { Bell, Plus, Trash2, ArrowUp, ArrowDown, BellRing } from 'lucide-react';

interface PriceAlert {
    id: number;
    symbol: string;
    condition: '>' | '<';
    price: number;
    active: boolean;
}

export default function PriceAlerts() {
    const [alerts, setAlerts] = useState<PriceAlert[]>([
        { id: 1, symbol: 'BTC', condition: '>', price: 100000, active: true },
        { id: 2, symbol: 'ETH', condition: '>', price: 4000, active: true },
        { id: 3, symbol: 'AAPL', condition: '<', price: 200, active: false },
    ]);
    const [newSymbol, setNewSymbol] = useState('');
    const [newPrice, setNewPrice] = useState('');
    const [newCondition, setNewCondition] = useState<'>' | '<'>('>');

    const addAlert = () => {
        if (!newSymbol || !newPrice) return;
        const newAlert: PriceAlert = {
            id: Date.now(),
            symbol: newSymbol.toUpperCase(),
            condition: newCondition,
            price: parseFloat(newPrice),
            active: true
        };
        setAlerts([...alerts, newAlert]);
        setNewSymbol('');
        setNewPrice('');
        // TODO: Persist to Backend D1 database
    };

    const toggleAlert = (id: number) => {
        setAlerts(alerts.map(a => a.id === id ? { ...a, active: !a.active } : a));
    };

    const deleteAlert = (id: number) => {
        setAlerts(alerts.filter(a => a.id !== id));
    };

    return (
        <div className="glass-card p-5 h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between mb-5 pb-4 border-b border-gray-800">
                <div className="flex items-center gap-2 text-cyan-400">
                    <BellRing size={18} className="animate-pulse" />
                    <h3 className="font-bold text-sm tracking-widest uppercase">Price Sentinels</h3>
                </div>
                <span className="text-[10px] text-gray-600 bg-gray-900 px-2 py-1 rounded border border-gray-800">
                    {alerts.filter(a => a.active).length} Active
                </span>
            </div>

            {/* Input Form */}
            <div className="flex gap-2 mb-5">
                <input
                    className="w-20 bg-[#111] border border-gray-700 rounded-lg px-3 py-2 text-xs text-white uppercase placeholder:text-gray-600 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all"
                    placeholder="SYM"
                    value={newSymbol}
                    onChange={e => setNewSymbol(e.target.value)}
                    maxLength={6}
                />
                <select
                    value={newCondition}
                    onChange={e => setNewCondition(e.target.value as '>' | '<')}
                    className="bg-[#111] border border-gray-700 rounded-lg px-2 py-2 text-xs text-white outline-none focus:border-cyan-500 transition-all"
                >
                    <option value=">">Above ↑</option>
                    <option value="<">Below ↓</option>
                </select>
                <input
                    className="flex-1 bg-[#111] border border-gray-700 rounded-lg px-3 py-2 text-xs text-white placeholder:text-gray-600 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/50 outline-none transition-all font-mono"
                    placeholder="PRICE"
                    type="number"
                    value={newPrice}
                    onChange={e => setNewPrice(e.target.value)}
                />
                <button
                    onClick={addAlert}
                    className="bg-cyan-600 hover:bg-cyan-500 text-white px-3 py-2 rounded-lg transition-all hover:shadow-lg hover:shadow-cyan-500/30"
                >
                    <Plus size={16} />
                </button>
            </div>

            {/* Alerts List */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar">
                {alerts.length === 0 ? (
                    <div className="text-center py-8 text-gray-600">
                        <Bell size={32} className="mx-auto mb-2 opacity-50" />
                        <p className="text-xs">No alerts set</p>
                    </div>
                ) : (
                    alerts.map(alert => (
                        <div
                            key={alert.id}
                            className={`flex justify-between items-center p-3 rounded-xl border transition-all group cursor-pointer ${alert.active
                                ? 'bg-gray-900/50 border-gray-800 hover:border-gray-700'
                                : 'bg-gray-900/20 border-gray-800/50 opacity-50'
                                }`}
                            onClick={() => toggleAlert(alert.id)}
                        >
                            <div className="flex items-center gap-3">
                                {/* Status Indicator */}
                                <div className={`w-2 h-2 rounded-full transition-all ${alert.active
                                    ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]'
                                    : 'bg-gray-600'
                                    }`}></div>

                                {/* Symbol */}
                                <span className="font-bold text-sm text-white font-mono">{alert.symbol}</span>

                                {/* Condition Icon */}
                                <div className={`p-1 rounded ${alert.condition === '>' ? 'bg-emerald-500/20' : 'bg-rose-500/20'}`}>
                                    {alert.condition === '>' ? (
                                        <ArrowUp size={12} className="text-emerald-400" />
                                    ) : (
                                        <ArrowDown size={12} className="text-rose-400" />
                                    )}
                                </div>
                            </div>

                            {/* Price */}
                            <div className="font-mono text-sm">
                                <span className="text-gray-400">{alert.condition === '>' ? 'Above' : 'Below'} </span>
                                <span className="text-white font-bold">${alert.price.toLocaleString()}</span>
                            </div>

                            {/* Delete Button */}
                            <button
                                onClick={(e) => { e.stopPropagation(); deleteAlert(alert.id); }}
                                className="text-gray-600 hover:text-rose-500 opacity-0 group-hover:opacity-100 transition-all p-1 hover:bg-rose-500/10 rounded"
                            >
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))
                )}
            </div>

            {/* Footer Tip */}
            <div className="mt-4 pt-4 border-t border-gray-800 text-center">
                <p className="text-[10px] text-gray-600">
                    Click an alert to toggle • Powered by Telegram
                </p>
            </div>
        </div>
    );
}
