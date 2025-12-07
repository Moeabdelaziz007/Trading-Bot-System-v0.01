"use client";
import { useState } from 'react';
import { motion } from 'framer-motion';

type TimeRange = '24H' | '7D' | '30D' | 'ALL';

const MOCK_DATA: Record<TimeRange, { day: string; value: number }[]> = {
    '24H': [
        { day: '9AM', value: 120 },
        { day: '12PM', value: -50 },
        { day: '3PM', value: 200 },
        { day: '6PM', value: 85 },
        { day: '9PM', value: -30 },
    ],
    '7D': [
        { day: 'Mon', value: 334 },
        { day: 'Tue', value: -180 },
        { day: 'Wed', value: 518 },
        { day: 'Thu', value: 734 },
        { day: 'Fri', value: 420 },
        { day: 'Sat', value: -120 },
        { day: 'Sun', value: 256 },
    ],
    '30D': [
        { day: 'W1', value: 1200 },
        { day: 'W2', value: 850 },
        { day: 'W3', value: -400 },
        { day: 'W4', value: 1600 },
    ],
    'ALL': [
        { day: 'Jan', value: 2400 },
        { day: 'Feb', value: 1800 },
        { day: 'Mar', value: -900 },
        { day: 'Apr', value: 3200 },
        { day: 'May', value: 2100 },
    ],
};

export default function PLChart() {
    const [range, setRange] = useState<TimeRange>('7D');
    const data = MOCK_DATA[range];
    const maxValue = Math.max(...data.map(d => Math.abs(d.value)));
    const totalPL = data.reduce((sum, d) => sum + d.value, 0);

    return (
        <div className="bento-card h-full">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-sm font-medium text-[var(--text-muted)]">Profit and Loss</h3>
                    <p className={`text-2xl font-bold ${totalPL >= 0 ? 'text-[var(--neon-green)]' : 'text-[var(--neon-red)]'}`}>
                        {totalPL >= 0 ? '+' : ''}${totalPL.toLocaleString()}
                    </p>
                </div>

                {/* Time Filter Tabs */}
                <div className="flex gap-1 bg-[var(--surface)] rounded-lg p-1">
                    {(['24H', '7D', '30D', 'ALL'] as TimeRange[]).map((t) => (
                        <button
                            key={t}
                            onClick={() => setRange(t)}
                            className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${range === t
                                    ? 'bg-[var(--neon-blue)] text-white'
                                    : 'text-[var(--text-muted)] hover:text-white'
                                }`}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            {/* Bar Chart */}
            <div className="flex items-end justify-between h-32 gap-2">
                {data.map((item, index) => {
                    const height = (Math.abs(item.value) / maxValue) * 100;
                    const isProfit = item.value >= 0;

                    return (
                        <motion.div
                            key={index}
                            initial={{ height: 0 }}
                            animate={{ height: `${height}%` }}
                            transition={{ delay: index * 0.05, duration: 0.3 }}
                            className="flex-1 flex flex-col items-center justify-end"
                        >
                            <div
                                className={`w-full rounded-t-md ${isProfit ? 'bg-[var(--chart-profit)]' : 'bg-[var(--chart-loss)]'
                                    }`}
                                style={{ height: `${height}%`, minHeight: '8px' }}
                            />
                            <span className="text-[10px] text-[var(--text-dim)] mt-2">{item.day}</span>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
