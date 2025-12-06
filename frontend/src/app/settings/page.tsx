"use client";
import React, { useState } from 'react';
import { Settings, Key, Bell, Shield, Globe, Palette, Save, Check } from 'lucide-react';

export default function SettingsPage() {
    const [saved, setSaved] = useState(false);
    const [settings, setSettings] = useState({
        apiConnected: true,
        notifications: true,
        darkMode: true,
        autoTrade: false,
        maxTradesPerDay: 10,
        defaultQty: 10,
    });

    const handleSave = () => {
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    return (
        <div className="p-8 h-full overflow-auto">
            <div className="max-w-3xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold text-white">Settings</h1>
                    <p className="text-gray-500 text-sm">Configure your trading terminal</p>
                </div>

                {/* API Connections */}
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6 mb-6">
                    <h2 className="font-bold text-white mb-4 flex items-center gap-2">
                        <Key size={18} className="text-cyan-400" /> API Connections
                    </h2>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                                    <Check size={18} className="text-green-400" />
                                </div>
                                <div>
                                    <p className="text-white font-medium">Alpaca (Paper Trading)</p>
                                    <p className="text-xs text-gray-500">Connected • Real-time data</p>
                                </div>
                            </div>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Active</span>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                                    <Check size={18} className="text-green-400" />
                                </div>
                                <div>
                                    <p className="text-white font-medium">Groq LLM</p>
                                    <p className="text-xs text-gray-500">Connected • Llama 3.3 70B</p>
                                </div>
                            </div>
                            <span className="px-3 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Active</span>
                        </div>

                        <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-yellow-500/20 rounded-lg flex items-center justify-center">
                                    <Globe size={18} className="text-yellow-400" />
                                </div>
                                <div>
                                    <p className="text-white font-medium">Gemini (Analysis)</p>
                                    <p className="text-xs text-gray-500">Optional • News summarization</p>
                                </div>
                            </div>
                            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">Optional</span>
                        </div>
                    </div>
                </div>

                {/* Trading Settings */}
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6 mb-6">
                    <h2 className="font-bold text-white mb-4 flex items-center gap-2">
                        <Shield size={18} className="text-red-400" /> Risk Management
                    </h2>

                    <div className="space-y-4">
                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Max Trades Per Day</label>
                            <input
                                type="number"
                                value={settings.maxTradesPerDay}
                                onChange={(e) => setSettings({ ...settings, maxTradesPerDay: parseInt(e.target.value) })}
                                className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-3 px-4 outline-none focus:border-cyan-500/50"
                            />
                            <p className="text-xs text-gray-600 mt-1">Circuit breaker: stops trading after this limit</p>
                        </div>

                        <div>
                            <label className="text-sm text-gray-400 block mb-2">Default Order Quantity</label>
                            <input
                                type="number"
                                value={settings.defaultQty}
                                onChange={(e) => setSettings({ ...settings, defaultQty: parseInt(e.target.value) })}
                                className="w-full bg-gray-800/50 border border-gray-700/50 rounded-lg py-3 px-4 outline-none focus:border-cyan-500/50"
                            />
                        </div>

                        <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                            <div>
                                <p className="text-white font-medium">Auto-Execute Trades</p>
                                <p className="text-xs text-gray-500">Allow AI to execute trades from chat</p>
                            </div>
                            <button
                                onClick={() => setSettings({ ...settings, autoTrade: !settings.autoTrade })}
                                className={`w-12 h-6 rounded-full transition-colors ${settings.autoTrade ? 'bg-green-500' : 'bg-gray-700'}`}
                            >
                                <div className={`w-5 h-5 bg-white rounded-full transition-transform ${settings.autoTrade ? 'translate-x-6' : 'translate-x-0.5'}`} />
                            </button>
                        </div>
                    </div>
                </div>

                {/* Appearance */}
                <div className="bg-[#0a0a0a] border border-gray-800 rounded-xl p-6 mb-6">
                    <h2 className="font-bold text-white mb-4 flex items-center gap-2">
                        <Palette size={18} className="text-purple-400" /> Appearance
                    </h2>

                    <div className="flex items-center justify-between p-4 bg-gray-900/50 rounded-lg">
                        <div>
                            <p className="text-white font-medium">Dark Mode</p>
                            <p className="text-xs text-gray-500">Optimized for trading</p>
                        </div>
                        <button
                            onClick={() => setSettings({ ...settings, darkMode: !settings.darkMode })}
                            className={`w-12 h-6 rounded-full transition-colors ${settings.darkMode ? 'bg-cyan-500' : 'bg-gray-700'}`}
                        >
                            <div className={`w-5 h-5 bg-white rounded-full transition-transform ${settings.darkMode ? 'translate-x-6' : 'translate-x-0.5'}`} />
                        </button>
                    </div>
                </div>

                {/* Save Button */}
                <button
                    onClick={handleSave}
                    className="w-full bg-gradient-to-r from-cyan-500 to-blue-600 text-white py-4 rounded-xl font-bold flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-cyan-500/20 transition-all"
                >
                    {saved ? <><Check size={18} /> Saved!</> : <><Save size={18} /> Save Settings</>}
                </button>
            </div>
        </div>
    );
}
