"use client";
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Settings,
    ShieldAlert,
    Zap,
    Key,
    Save,
    Power,
    Activity,
    Lock
} from 'lucide-react';

export default function SettingsPage() {
    const [settings, setSettings] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        fetch('/api/settings')
            .then(res => res.json())
            .then(data => {
                setSettings(data);
                setLoading(false);
            });
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            setTimeout(() => setSaving(false), 1000); // Fake delay for UX
        } catch (e) {
            setSaving(false);
        }
    };

    const updateRisk = (key: string, val: any) => {
        setSettings({ ...settings, risk: { ...settings.risk, [key]: val } });
    };

    const updateStrategy = (key: string, val: any) => {
        setSettings({ ...settings, strategy: { ...settings.strategy, [key]: val } });
    };

    if (loading) return <div className="p-8 text-[var(--neon-cyan)] animate-pulse">Loading Configurations...</div>;

    return (
        <div className="min-h-screen space-y-6 animate-fade-in p-2 md:p-0 pb-20">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[var(--neon-green)] to-[var(--neon-cyan)] flex items-center gap-3">
                        <Settings className="w-8 h-8 text-[var(--neon-green)]" />
                        Expert Configuration
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-1 font-mono">
                        System Level Controls • Risk Management • API Keys
                    </p>
                </div>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSave}
                    disabled={saving}
                    className="px-6 py-2 rounded-lg bg-[var(--neon-cyan)] text-black font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
                >
                    <Save className="w-4 h-4" />
                    {saving ? 'Saving...' : 'Save Changes'}
                </motion.button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* 1. Risk Management Section */}
                <div className="bento-card p-6 border-l-4 border-l-[var(--neon-green)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <ShieldAlert className="w-6 h-6 text-[var(--neon-green)]" />
                        Risk Management
                    </h2>

                    <div className="space-y-6">
                        {/* Kill Switch */}
                        <div className="flex items-center justify-between p-4 bg-[var(--void)] border border-[var(--glass-border)] rounded-xl">
                            <div>
                                <h3 className="font-bold text-red-500 flex items-center gap-2">
                                    <Power className="w-4 h-4" /> EMERGENCY KILL SWITCH
                                </h3>
                                <p className="text-xs text-[var(--text-muted)]">Instantly stop all trading and cancel orders</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={settings.risk.killSwitch}
                                    onChange={(e) => updateRisk('killSwitch', e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600 shadow-[0_0_10px_rgba(255,0,0,0.5)]"></div>
                            </label>
                        </div>

                        {/* Risk Per Trade */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-bold">Risk Per Trade (%)</label>
                                <span className="text-[var(--neon-green)] font-mono">{settings.risk.riskPerTrade}%</span>
                            </div>
                            <input
                                type="range"
                                min="0.1"
                                max="5.0"
                                step="0.1"
                                value={settings.risk.riskPerTrade}
                                onChange={(e) => updateRisk('riskPerTrade', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[var(--neon-green)]"
                            />
                        </div>

                        {/* Risk Level Selector */}
                        <div>
                            <label className="text-sm font-bold mb-2 block">Risk Profile</label>
                            <div className="grid grid-cols-3 gap-2">
                                {['Low', 'Medium', 'High'].map((level) => (
                                    <button
                                        key={level}
                                        onClick={() => updateRisk('level', level)}
                                        className={`py-2 rounded-lg text-sm border transition-all ${settings.risk.level === level
                                                ? 'border-[var(--neon-green)] bg-[var(--neon-green)]/10 text-[var(--neon-green)] shadow-[0_0_10px_rgba(0,255,0,0.2)]'
                                                : 'border-[var(--glass-border)] text-[var(--text-dim)] hover:border-[var(--neon-green)]/50'
                                            }`}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 2. Strategy Configuration */}
                <div className="bento-card p-6 border-l-4 border-l-[var(--neon-purple)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Zap className="w-6 h-6 text-[var(--neon-purple)]" />
                        Strategy Engine
                    </h2>

                    <div className="space-y-6">
                        {/* AEXI Threshold */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-bold flex items-center gap-2">
                                    AEXI Trigger Threshold <Activity className="w-3 h-3 text-[var(--neon-cyan)]" />
                                </label>
                                <span className="text-[var(--neon-purple)] font-mono">{settings.strategy.aexiThreshold}/100</span>
                            </div>
                            <input
                                type="range"
                                min="50"
                                max="95"
                                value={settings.strategy.aexiThreshold}
                                onChange={(e) => updateStrategy('aexiThreshold', parseInt(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[var(--neon-purple)]"
                            />
                            <p className="text-xs text-[var(--text-muted)] mt-1">Minimum score required to trigger a trade signal.</p>
                        </div>

                        {/* Dream Threshold */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-bold">Dream Machine Threshold</label>
                                <span className="text-[var(--neon-magenta)] font-mono">{settings.strategy.dreamThreshold}/100</span>
                            </div>
                            <input
                                type="range"
                                min="50"
                                max="95"
                                value={settings.strategy.dreamThreshold}
                                onChange={(e) => updateStrategy('dreamThreshold', parseInt(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[var(--neon-magenta)]"
                            />
                        </div>

                        {/* Active Timeframes */}
                        <div>
                            <label className="text-sm font-bold mb-2 block">Active Timeframes</label>
                            <div className="flex gap-2 flex-wrap">
                                {['M5', 'M15', 'H1', 'H4', 'D1'].map((tf) => (
                                    <button
                                        key={tf}
                                        onClick={() => {
                                            const current = settings.strategy.activeTimeframes;
                                            const updated = current.includes(tf)
                                                ? current.filter((t: string) => t !== tf)
                                                : [...current, tf];
                                            updateStrategy('activeTimeframes', updated);
                                        }}
                                        className={`px-3 py-1 rounded text-xs font-mono border transition-all ${settings.strategy.activeTimeframes.includes(tf)
                                                ? 'border-[var(--neon-purple)] bg-[var(--neon-purple)]/20 text-white'
                                                : 'border-[var(--glass-border)] text-[var(--text-dim)]'
                                            }`}
                                    >
                                        {tf}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 3. API Keys (Full Width) */}
                <div className="md:col-span-2 bento-card p-6 border-l-4 border-l-[var(--neon-cyan)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Key className="w-6 h-6 text-[var(--neon-cyan)]" />
                        API Connections
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-mono text-[var(--neon-cyan)]">Capital.com API Key</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={settings.apiKeys.capital}
                                    readOnly
                                    className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-3 text-sm focus:border-[var(--neon-cyan)] focus:outline-none"
                                />
                                <Lock className="absolute right-3 top-3 w-4 h-4 text-[var(--text-dim)]" />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-mono text-[var(--neon-purple)]">DeepSeek API Key</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={settings.apiKeys.deepseek}
                                    readOnly
                                    className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-3 text-sm focus:border-[var(--neon-purple)] focus:outline-none"
                                />
                                <Lock className="absolute right-3 top-3 w-4 h-4 text-[var(--text-dim)]" />
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}
