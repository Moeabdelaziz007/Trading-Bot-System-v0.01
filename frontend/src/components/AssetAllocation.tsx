"use client";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface Position {
    symbol: string;
    market_value: string | number;
}

interface AssetAllocationProps {
    positions: Position[];
    cash: number | string;
}

// Neon colors for the chart
const COLORS = ['#06b6d4', '#10b981', '#f59e0b', '#6366f1', '#ec4899', '#8b5cf6'];

// Custom Tooltip
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
        return (
            <div className="bg-[#0a0a0a] border border-gray-800 p-3 rounded-lg shadow-xl">
                <p className="text-gray-400 text-xs mb-1">{payload[0].name}</p>
                <p className="text-white font-bold font-mono">
                    ${Number(payload[0].value).toLocaleString()}
                </p>
            </div>
        );
    }
    return null;
};

export default function AssetAllocation({ positions, cash }: AssetAllocationProps) {
    // Prepare data for chart
    const data = [
        { name: 'Cash', value: parseFloat(String(cash)) || 0 },
        ...positions.map((p) => ({
            name: p.symbol,
            value: parseFloat(String(p.market_value)) || 0
        }))
    ].filter(item => item.value > 0);

    // Calculate total
    const total = data.reduce((sum, item) => sum + item.value, 0);

    if (data.length === 0 || total === 0) {
        return (
            <div className="glass-card p-6 flex flex-col h-[350px]">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></div>
                        Asset Allocation
                    </h3>
                </div>
                <div className="flex-1 flex items-center justify-center">
                    <p className="text-gray-500 text-sm">No positions to display</p>
                </div>
            </div>
        );
    }

    return (
        <div className="glass-card p-6 flex flex-col h-[350px]">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></div>
                    Asset Allocation
                </h3>
                <span className="text-[10px] text-gray-600 bg-gray-900 px-2 py-1 rounded border border-gray-800">
                    REAL-TIME
                </span>
            </div>

            {/* Center Total Value */}
            <div className="text-center mb-2">
                <p className="text-xs text-gray-500">Total Portfolio</p>
                <p className="text-2xl font-bold text-white font-mono">
                    ${total.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
            </div>

            <div className="flex-1 w-full flex items-center">
                <ResponsiveContainer width="60%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={70}
                            paddingAngle={3}
                            dataKey="value"
                            stroke="none"
                        >
                            {data.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={COLORS[index % COLORS.length]}
                                    className="hover:opacity-80 transition-opacity cursor-pointer"
                                    style={{ filter: `drop-shadow(0 0 8px ${COLORS[index % COLORS.length]}40)` }}
                                />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                    </PieChart>
                </ResponsiveContainer>

                {/* Legend */}
                <div className="flex flex-col gap-2 flex-1">
                    {data.map((item, index) => (
                        <div key={item.name} className="flex items-center gap-2 text-xs">
                            <div
                                className="w-3 h-3 rounded-sm"
                                style={{ backgroundColor: COLORS[index % COLORS.length] }}
                            ></div>
                            <span className="text-gray-400 flex-1 truncate">{item.name}</span>
                            <span className="font-mono text-white font-bold">
                                {((item.value / total) * 100).toFixed(1)}%
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
