'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Zap, Activity, Save } from 'lucide-react';

// Backend URL
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

interface StrategyConfig {
    aexiThreshold: number;
    dreamThreshold: number;
    activeTimeframes: string[];
}

export const StrategyEngine: React.FC = () => {
    const [config, setConfig] = useState<StrategyConfig>({
        aexiThreshold: 75,
        dreamThreshold: 80,
        activeTimeframes: ['M5', 'H1', 'D1']
    });
    const [saving, setSaving] = useState(false);
    const [lastSaved, setLastSaved] = useState<Date | null>(null);

    // Load config from backend on mount
    useEffect(() => {
        const loadConfig = async () => {
            try {
                const res = await fetch(`${BACKEND_URL}/api/status`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.strategy) {
                        setConfig({
                            aexiThreshold: data.strategy.aexi_threshold || 75,
                            dreamThreshold: data.strategy.dream_threshold || 80,
                            activeTimeframes: data.strategy.timeframes || ['M5', 'H1', 'D1']
                        });
                    }
                }
            } catch (e) {
                console.log('Using default strategy config');
            }
        };
        loadConfig();
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            await fetch(`${BACKEND_URL}/api/settings`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    strategy: {
                        aexi_threshold: config.aexiThreshold,
                        dream_threshold: config.dreamThreshold,
                        timeframes: config.activeTimeframes
                    }
                })
            });
            setLastSaved(new Date());
        } catch (e) {
            console.error('Failed to save config');
        } finally {
            setSaving(false);
        }
    };

    const toggleTimeframe = (tf: string) => {
        setConfig(prev => ({
            ...prev,
            activeTimeframes: prev.activeTimeframes.includes(tf)
                ? prev.activeTimeframes.filter(t => t !== tf)
                : [...prev.activeTimeframes, tf]
        }));
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-[#0A0A1A]/90 border border-purple-500/30 rounded-lg p-6"
        >
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-mono font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-purple-400" />
                    STRATEGY_ENGINE
                </h2>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className={`px-4 py-2 rounded-lg text-xs font-mono flex items-center gap-2 transition-all ${saving
                            ? 'bg-gray-600 cursor-not-allowed'
                            : 'bg-purple-600 hover:bg-purple-700'
                        }`}
                >
                    <Save className="w-4 h-4" />
                    {saving ? 'SAVING...' : 'SAVE_CONFIG'}
                </button>
            </div>

            <div className="space-y-6">
                {/* AEXI Threshold */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-sm font-bold flex items-center gap-2 text-gray-300">
                            AEXI Trigger Threshold
                            <Activity className="w-3 h-3 text-cyan-400" />
                        </label>
                        <span className="text-cyan-400 font-mono">{config.aexiThreshold}/100</span>
                    </div>
                    <input
                        type="range"
                        min="50"
                        max="95"
                        value={config.aexiThreshold}
                        onChange={(e) => setConfig(prev => ({ ...prev, aexiThreshold: parseInt(e.target.value) }))}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">Minimum score required to trigger a trade signal.</p>
                </div>

                {/* Dream Threshold */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-sm font-bold text-gray-300">Dream Machine Threshold</label>
                        <span className="text-pink-400 font-mono">{config.dreamThreshold}/100</span>
                    </div>
                    <input
                        type="range"
                        min="50"
                        max="95"
                        value={config.dreamThreshold}
                        onChange={(e) => setConfig(prev => ({ ...prev, dreamThreshold: parseInt(e.target.value) }))}
                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-pink-500"
                    />
                </div>

                {/* Active Timeframes */}
                <div>
                    <label className="text-sm font-bold mb-2 block text-gray-300">Active Timeframes</label>
                    <div className="flex gap-2 flex-wrap">
                        {['M1', 'M5', 'M15', 'H1', 'H4', 'D1'].map((tf) => (
                            <button
                                key={tf}
                                onClick={() => toggleTimeframe(tf)}
                                className={`px-4 py-2 rounded text-xs font-mono border transition-all ${config.activeTimeframes.includes(tf)
                                        ? 'border-purple-500 bg-purple-500/20 text-white'
                                        : 'border-gray-600 text-gray-400 hover:border-purple-500/50'
                                    }`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Last Saved Indicator */}
                {lastSaved && (
                    <p className="text-xs text-green-400 font-mono">
                        ✓ Last saved: {lastSaved.toLocaleTimeString()}
                    </p>
                )}
            </div>
        </motion.div>
    );
};
