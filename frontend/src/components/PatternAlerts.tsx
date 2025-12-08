"use client";
import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface PatternData {
    symbol: string;
    pattern: string;
    category: 'candlestick' | 'chart';
    bullish: boolean;
    timestamp: number;
}

export default function PatternAlerts() {
    const [patterns, setPatterns] = useState<PatternData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPatterns = async () => {
            try {
                // Mock data - replace with actual API call
                const mockPatterns: PatternData[] = [
                    { symbol: 'EURUSD', pattern: 'BULLISH_ENGULFING', category: 'candlestick', bullish: true, timestamp: Date.now() },
                    { symbol: 'XAUUSD', pattern: 'DOJI', category: 'candlestick', bullish: false, timestamp: Date.now() - 60000 },
                    { symbol: 'GBPUSD', pattern: 'DOUBLE_BOTTOM', category: 'chart', bullish: true, timestamp: Date.now() - 120000 },
                ];
                setPatterns(mockPatterns);
            } catch (e) {
                console.error('Failed to fetch patterns', e);
            } finally {
                setLoading(false);
            }
        };
        fetchPatterns();
        const interval = setInterval(fetchPatterns, 30000);
        return () => clearInterval(interval);
    }, []);

    const getCategoryIcon = (category: string) => {
        return category === 'candlestick' ? '🕯️' : '📊';
    };

    const formatPattern = (pattern: string) => {
        return pattern.replace(/_/g, ' ').toLowerCase()
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    const getTimeAgo = (timestamp: number) => {
        const diff = Math.floor((Date.now() - timestamp) / 1000);
        if (diff < 60) return `${diff}s ago`;
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        return `${Math.floor(diff / 3600)}h ago`;
    };

    if (loading) {
        return (
            <div className="bento-card p-4 animate-pulse">
                <div className="h-4 bg-[var(--glass-border)] rounded w-1/3 mb-4"></div>
                <div className="space-y-2">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-12 bg-[var(--glass-border)] rounded"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <motion.div
            className="bento-card p-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                    <span>🔍</span> Pattern Alerts
                </h3>
                <span className="px-2 py-0.5 text-xs bg-[var(--neon-green)] bg-opacity-20 text-[var(--neon-green)] rounded-full">
                    {patterns.length} Active
                </span>
            </div>

            <AnimatePresence>
                <div className="space-y-2">
                    {patterns.length === 0 ? (
                        <p className="text-sm text-[var(--text-dim)] text-center py-4">
                            No patterns detected
                        </p>
                    ) : (
                        patterns.map((item, idx) => (
                            <motion.div
                                key={`${item.symbol}-${item.pattern}`}
                                className="flex items-center justify-between p-3 rounded-lg bg-[var(--glass-bg)] border border-[var(--glass-border)] hover:border-[var(--neon-green)] transition-colors"
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                exit={{ opacity: 0, scale: 0.95 }}
                                transition={{ delay: idx * 0.1 }}
                            >
                                <div className="flex items-center gap-3">
                                    <span className="text-xl">{getCategoryIcon(item.category)}</span>
                                    <div>
                                        <p className="text-sm font-mono text-white">{item.symbol}</p>
                                        <p className="text-xs text-[var(--text-dim)]">{formatPattern(item.pattern)}</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <span className={`text-xs font-semibold px-2 py-1 rounded ${item.bullish
                                            ? 'bg-[var(--neon-green)] bg-opacity-20 text-[var(--neon-green)]'
                                            : 'bg-red-500 bg-opacity-20 text-red-400'
                                        }`}>
                                        {item.bullish ? '↑ BULLISH' : '↓ BEARISH'}
                                    </span>
                                    <p className="text-xs text-[var(--text-dim)] mt-1">{getTimeAgo(item.timestamp)}</p>
                                </div>
                            </motion.div>
                        ))
                    )}
                </div>
            </AnimatePresence>

            <div className="mt-4 pt-3 border-t border-[var(--glass-border)]">
                <p className="text-xs text-[var(--text-dim)] text-center">
                    Powered by PatternScanner AI
                </p>
            </div>
        </motion.div>
    );
}
