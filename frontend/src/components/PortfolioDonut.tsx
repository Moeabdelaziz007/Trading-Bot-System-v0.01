"use client";
import { motion } from 'framer-motion';

interface AllocationItem {
    symbol: string;
    value: number;
    color: string;
}

const MOCK_ALLOCATION: AllocationItem[] = [
    { symbol: 'EUR/USD', value: 35, color: '#3B82F6' },
    { symbol: 'XAU/USD', value: 28, color: '#F59E0B' },
    { symbol: 'GBP/USD', value: 22, color: '#8B5CF6' },
    { symbol: 'USD/JPY', value: 15, color: '#10B981' },
];

export default function PortfolioDonut({ equity = 10000 }: { equity?: number }) {
    const total = MOCK_ALLOCATION.reduce((sum, item) => sum + item.value, 0);
    let cumulativePercent = 0;

    return (
        <div className="bento-card h-full">
            <h3 className="text-sm font-medium text-[var(--text-muted)] mb-4">Overview</h3>

            <div className="flex items-center gap-6">
                {/* Donut Chart */}
                <div className="relative w-40 h-40">
                    <svg viewBox="0 0 42 42" className="w-full h-full -rotate-90">
                        {MOCK_ALLOCATION.map((item, index) => {
                            const percent = (item.value / total) * 100;
                            const dashArray = `${percent} ${100 - percent}`;
                            const dashOffset = 100 - cumulativePercent;
                            cumulativePercent += percent;

                            return (
                                <circle
                                    key={index}
                                    cx="21"
                                    cy="21"
                                    r="15.915"
                                    fill="transparent"
                                    stroke={item.color}
                                    strokeWidth="3"
                                    strokeDasharray={dashArray}
                                    strokeDashoffset={dashOffset}
                                    className="transition-all duration-500"
                                />
                            );
                        })}
                    </svg>

                    {/* Center Text */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                        <span className="text-2xl font-bold text-white">
                            ${equity.toLocaleString()}
                        </span>
                        <span className="text-xs text-[var(--text-dim)]">Total Balance</span>
                    </div>
                </div>

                {/* Legend */}
                <div className="flex-1 space-y-2">
                    {MOCK_ALLOCATION.map((item, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, x: 10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="flex items-center justify-between"
                        >
                            <div className="flex items-center gap-2">
                                <div
                                    className="w-2 h-2 rounded-full"
                                    style={{ background: item.color }}
                                />
                                <span className="text-sm text-white">{item.symbol}</span>
                            </div>
                            <span className="text-sm font-mono text-[var(--text-muted)]">
                                ${((item.value / 100) * equity).toLocaleString()}
                            </span>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}
