"use client";
import { motion } from 'framer-motion';
import { Bot, ChevronRight, TrendingUp, Pause, Play } from 'lucide-react';

interface BotInfo {
    name: string;
    status: 'active' | 'paused' | 'testing';
    growth: number;
    profit: number;
    sparkline: number[];
}

const MOCK_BOTS: BotInfo[] = [
    {
        name: 'EUR/USD Scalper',
        status: 'active',
        growth: 14.5,
        profit: 1250,
        sparkline: [10, 15, 12, 18, 22, 20, 25, 28, 24, 30]
    },
    {
        name: 'XAU/USD Trend',
        status: 'testing',
        growth: 8.2,
        profit: 0,
        sparkline: [5, 8, 6, 10, 12, 11, 14, 16, 15, 18]
    },
    {
        name: 'GBP/JPY Swing',
        status: 'paused',
        growth: -2.1,
        profit: -180,
        sparkline: [20, 18, 22, 19, 16, 14, 12, 10, 8, 9]
    },
];

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
    const max = Math.max(...data);
    const min = Math.min(...data);
    const range = max - min || 1;

    const points = data.map((v, i) => {
        const x = (i / (data.length - 1)) * 100;
        const y = 100 - ((v - min) / range) * 100;
        return `${x},${y}`;
    }).join(' ');

    return (
        <svg viewBox="0 0 100 100" className="w-24 h-8" preserveAspectRatio="none">
            <polyline
                points={points}
                fill="none"
                stroke={color}
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
            />
        </svg>
    );
}

export default function ActiveBots() {
    return (
        <div className="bento-card h-full">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-[var(--neon-cyan)]" />
                    <h3 className="text-sm font-medium text-[var(--text-muted)]">Active Bots</h3>
                </div>
                <button className="text-xs text-[var(--neon-cyan)] hover:underline flex items-center gap-1">
                    SHOW MORE <ChevronRight className="w-3 h-3" />
                </button>
            </div>

            <div className="space-y-3">
                {MOCK_BOTS.map((bot, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="flex items-center justify-between p-3 rounded-xl bg-[var(--surface)] hover:bg-[var(--surface-hover)] transition-colors cursor-pointer group"
                    >
                        <div className="flex items-center gap-3">
                            {/* Status Indicator */}
                            <div className={`w-2 h-2 rounded-full ${bot.status === 'active' ? 'bg-[var(--neon-green)] animate-pulse' :
                                    bot.status === 'testing' ? 'bg-[var(--neon-gold)]' :
                                        'bg-[var(--text-dim)]'
                                }`} />

                            <div>
                                <p className="text-sm font-medium text-white">{bot.name}</p>
                                <span className={`text-[10px] uppercase font-bold ${bot.status === 'active' ? 'text-[var(--neon-green)]' :
                                        bot.status === 'testing' ? 'text-[var(--neon-gold)]' :
                                            'text-[var(--text-dim)]'
                                    }`}>
                                    {bot.status}
                                </span>
                            </div>
                        </div>

                        {/* Sparkline */}
                        <MiniSparkline
                            data={bot.sparkline}
                            color={bot.growth >= 0 ? 'var(--neon-green)' : 'var(--neon-red)'}
                        />

                        {/* Stats */}
                        <div className="text-right">
                            <p className={`text-sm font-mono font-bold ${bot.growth >= 0 ? 'text-[var(--neon-green)]' : 'text-[var(--neon-red)]'
                                }`}>
                                {bot.growth >= 0 ? '+' : ''}{bot.growth}%
                            </p>
                            <p className="text-[10px] text-[var(--text-dim)]">
                                ${Math.abs(bot.profit).toLocaleString()}
                            </p>
                        </div>

                        {/* Quick Action */}
                        <button className="opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-lg bg-[var(--glass-border)] hover:bg-[var(--neon-cyan)]/20">
                            {bot.status === 'active' ?
                                <Pause className="w-4 h-4 text-[var(--text-muted)]" /> :
                                <Play className="w-4 h-4 text-[var(--text-muted)]" />
                            }
                        </button>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
