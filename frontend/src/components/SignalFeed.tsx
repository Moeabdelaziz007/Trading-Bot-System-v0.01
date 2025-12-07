'use client';

import { motion } from 'framer-motion';

const MOCK_SIGNALS = [
    { symbol: 'BTC/USD', type: 'BUY', price: '98,450.00', time: '2m ago', confidence: 94 },
    { symbol: 'XAU/USD', type: 'SELL', price: '2,045.50', time: '15m ago', confidence: 88 },
    { symbol: 'EUR/USD', type: 'HOLD', price: '1.0850', time: '1h ago', confidence: 72 },
];

export default function SignalFeed() {
    return (
        <div className="w-full">
            <h2 className="text-xl font-orbitron text-white mb-4 px-2">Market Intelligence</h2>
            <div className="grid gap-3">
                {MOCK_SIGNALS.map((signal, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="bg-[#0A0A0A] border border-white/5 rounded-xl p-4 flex justify-between items-center group hover:border-neon-cyan/30 transition-all cursor-pointer"
                    >
                        <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs ${signal.type === 'BUY' ? 'bg-neon-green/10 text-neon-green' :
                                    signal.type === 'SELL' ? 'bg-red-500/10 text-red-500' : 'bg-gray-500/10 text-gray-400'
                                }`}>
                                {signal.type}
                            </div>
                            <div>
                                <h3 className="font-bold text-white">{signal.symbol}</h3>
                                <p className="text-xs text-gray-500 font-mono">{signal.time}</p>
                            </div>
                        </div>

                        <div className="text-right">
                            <div className="font-mono text-white">${signal.price}</div>
                            <div className="text-xs text-neon-cyan/70 font-mono">
                                {signal.confidence}% Confidence
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>
        </div>
    );
}
