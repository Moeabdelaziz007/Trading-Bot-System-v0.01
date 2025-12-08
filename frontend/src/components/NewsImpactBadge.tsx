"use client";
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface NewsEvent {
    name: string;
    time: string;
    currency: string;
    impact: 'high' | 'medium' | 'low';
}

interface NewsImpactData {
    avoid: boolean;
    reason: string;
    events: NewsEvent[];
}

export default function NewsImpactBadge() {
    const [impact, setImpact] = useState<NewsImpactData | null>(null);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState(false);

    useEffect(() => {
        const checkImpact = async () => {
            try {
                // Mock data - replace with actual API call
                const mockImpact: NewsImpactData = {
                    avoid: Math.random() > 0.7,
                    reason: "NFP Release in 15 minutes",
                    events: [
                        { name: "Non-Farm Payrolls", time: "13:30", currency: "USD", impact: "high" },
                        { name: "Unemployment Rate", time: "13:30", currency: "USD", impact: "high" },
                    ]
                };
                setImpact(mockImpact);
            } catch (e) {
                console.error('Failed to check news impact', e);
            } finally {
                setLoading(false);
            }
        };
        checkImpact();
        const interval = setInterval(checkImpact, 60000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="animate-pulse h-12 bg-[var(--glass-border)] rounded-lg"></div>
        );
    }

    if (!impact || !impact.avoid) {
        return (
            <motion.div
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--neon-green)] bg-opacity-10 border border-[var(--neon-green)] border-opacity-30"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <span className="w-2 h-2 bg-[var(--neon-green)] rounded-full animate-pulse"></span>
                <span className="text-sm text-[var(--neon-green)] font-medium">Safe to Trade</span>
                <span className="text-xs text-[var(--text-dim)]">No high-impact news</span>
            </motion.div>
        );
    }

    return (
        <motion.div
            className="bento-card border-red-500 border-opacity-50 overflow-hidden cursor-pointer"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="flex items-center justify-between p-4 bg-red-500 bg-opacity-10">
                <div className="flex items-center gap-3">
                    <motion.span
                        className="text-2xl"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                    >
                        ⚠️
                    </motion.span>
                    <div>
                        <p className="text-sm font-semibold text-red-400">High-Impact News Alert</p>
                        <p className="text-xs text-[var(--text-dim)]">{impact.reason}</p>
                    </div>
                </div>
                <motion.span
                    className="text-[var(--text-dim)]"
                    animate={{ rotate: expanded ? 180 : 0 }}
                >
                    ▼
                </motion.span>
            </div>

            <motion.div
                className="overflow-hidden"
                initial={{ height: 0 }}
                animate={{ height: expanded ? 'auto' : 0 }}
                transition={{ duration: 0.3 }}
            >
                <div className="p-4 space-y-2 bg-[var(--glass-bg)]">
                    {impact.events.map((event, idx) => (
                        <div
                            key={idx}
                            className="flex items-center justify-between p-2 rounded bg-red-500 bg-opacity-5 border border-red-500 border-opacity-20"
                        >
                            <div className="flex items-center gap-2">
                                <span className="text-xs px-2 py-0.5 bg-red-500 bg-opacity-20 text-red-400 rounded font-semibold">
                                    🔴 HIGH
                                </span>
                                <span className="text-sm text-white">{event.name}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-xs text-[var(--text-dim)]">{event.currency}</span>
                                <span className="text-xs font-mono text-white">{event.time} UTC</span>
                            </div>
                        </div>
                    ))}
                    <p className="text-xs text-red-400 text-center mt-3">
                        ⛔ Avoid trading during high-impact news releases
                    </p>
                </div>
            </motion.div>
        </motion.div>
    );
}
