'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Position {
    symbol: string;
    qty: string;
    side: string;
    current_price: string;
    avg_entry_price: string;
    unrealized_pl: string;
    unrealized_plpc: string;
}

export default function LivePositions() {
    const [positions, setPositions] = useState<Position[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchPositions = async () => {
        try {
            const res = await fetch('/api/positions');
            if (res.ok) {
                const json = await res.json();
                setPositions(Array.isArray(json) ? json : []);
            }
        } catch (error) {
            console.error('Failed to fetch positions', error);
            setPositions([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPositions();
        const interval = setInterval(fetchPositions, 5000); // 5s refresh
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="text-white/30 text-sm font-mono p-4">Loading positions...</div>;

    return (
        <div className="w-full mt-6">
            <div className="flex justify-between items-center mb-4 px-2">
                <h2 className="text-xl font-orbitron text-white">Live Positions</h2>
                {positions.length > 0 && (
                    <span className="text-xs font-mono text-neon-green bg-neon-green/10 px-2 py-1 rounded">
                        {positions.length} ACTIVE
                    </span>
                )}
            </div>

            <div className="space-y-3">
                <AnimatePresence>
                    {positions.length === 0 ? (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="text-center py-10 border border-dashed border-white/10 rounded-xl"
                        >
                            <p className="text-gray-500 font-mono text-sm">No active positions</p>
                        </motion.div>
                    ) : (
                        positions.map((pos) => {
                            const isProfit = parseFloat(pos.unrealized_pl) >= 0;
                            const plPercent = (parseFloat(pos.unrealized_plpc) * 100).toFixed(2);

                            return (
                                <motion.div
                                    key={pos.symbol}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="bg-[#0A0A0A] border border-white/5 rounded-xl p-4 flex justify-between items-center hover:border-white/20 transition-all"
                                >
                                    {/* Left: Symbol & Size */}
                                    <div className="flex items-center gap-4">
                                        <div className={`w-1 h-12 rounded-full ${isProfit ? 'bg-neon-green' : 'bg-red-500'}`} />
                                        <div>
                                            <h3 className="text-lg font-bold text-white">{pos.symbol}</h3>
                                            <div className="flex gap-2 text-xs text-gray-400 font-mono">
                                                <span className="uppercase text-white/60">{pos.side}</span>
                                                <span>{pos.qty} units</span>
                                                <span>@ ${parseFloat(pos.avg_entry_price).toFixed(2)}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Right: P/L */}
                                    <div className="text-right">
                                        <div className={`text-lg font-bold font-mono ${isProfit ? 'text-neon-green' : 'text-red-500'}`}>
                                            {isProfit ? '+' : ''}{parseFloat(pos.unrealized_pl).toFixed(2)}
                                        </div>
                                        <div className={`text-xs font-mono ${isProfit ? 'text-neon-green/70' : 'text-red-500/70'}`}>
                                            {isProfit ? '+' : ''}{plPercent}%
                                        </div>
                                    </div>
                                </motion.div>
                            );
                        })
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
