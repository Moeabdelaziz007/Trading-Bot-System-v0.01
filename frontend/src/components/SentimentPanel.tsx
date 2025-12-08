"use client";
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface SentimentData {
    symbol: string;
    score: number;
    label: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
    sources: number;
}

const WATCHLIST = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD'];

export default function SentimentPanel() {
    const [sentiments, setSentiments] = useState<SentimentData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchSentiment = async () => {
            try {
                // Mock data - replace with actual API call
                const mockData: SentimentData[] = WATCHLIST.map(symbol => ({
                    symbol,
                    score: Math.random() * 2 - 1, // -1 to 1
                    label: Math.random() > 0.6 ? 'BULLISH' : Math.random() > 0.3 ? 'NEUTRAL' : 'BEARISH',
                    sources: Math.floor(Math.random() * 5) + 1
                }));
                setSentiments(mockData);
            } catch (e) {
                console.error('Failed to fetch sentiment', e);
            } finally {
                setLoading(false);
            }
        };
        fetchSentiment();
        const interval = setInterval(fetchSentiment, 60000); // Every minute
        return () => clearInterval(interval);
    }, []);

    const getSentimentColor = (label: string) => {
        switch (label) {
            case 'BULLISH': return 'text-[var(--neon-green)]';
            case 'BEARISH': return 'text-red-400';
            default: return 'text-yellow-400';
        }
    };

    const getSentimentIcon = (label: string) => {
        switch (label) {
            case 'BULLISH': return '📈';
            case 'BEARISH': return '📉';
            default: return '➡️';
        }
    };

    if (loading) {
        return (
            <div className="bento-card p-4 animate-pulse">
                <div className="h-4 bg-[var(--glass-border)] rounded w-1/3 mb-4"></div>
                <div className="space-y-3">
                    {[1, 2, 3, 4].map(i => (
                        <div key={i} className="h-8 bg-[var(--glass-border)] rounded"></div>
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
                    <span>💬</span> Market Sentiment
                </h3>
                <span className="text-xs text-[var(--text-dim)]">Live</span>
            </div>

            <div className="space-y-3">
                {sentiments.map((item, idx) => (
                    <motion.div
                        key={item.symbol}
                        className="flex items-center justify-between p-2 rounded-lg bg-[var(--glass-bg)] border border-[var(--glass-border)]"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                    >
                        <div className="flex items-center gap-3">
                            <span className="text-sm font-mono text-white">{item.symbol}</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-lg">{getSentimentIcon(item.label)}</span>
                            <span className={`text-sm font-semibold ${getSentimentColor(item.label)}`}>
                                {item.label}
                            </span>
                            <span className="text-xs text-[var(--text-dim)]">
                                ({item.sources} sources)
                            </span>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div className="mt-4 pt-3 border-t border-[var(--glass-border)]">
                <p className="text-xs text-[var(--text-dim)] text-center">
                    Powered by MarketFeed AI Analysis
                </p>
            </div>
        </motion.div>
    );
}
