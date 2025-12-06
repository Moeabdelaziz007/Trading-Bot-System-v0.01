'use client';

import React, { useEffect, useState, useRef } from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { useMarketData } from '@/hooks/useMarketData';

interface LivePriceProps {
    symbol: string;
    name: string;
    color: 'cyan' | 'blue' | 'gold' | 'green' | 'red';
}

const colorMap = {
    cyan: {
        bg: 'from-neon-cyan/10 to-neon-cyan/5',
        border: 'border-neon-cyan/30',
        text: 'text-neon-cyan',
        glow: 'shadow-[0_0_20px_rgba(0,242,234,0.2)]',
    },
    blue: {
        bg: 'from-blue-500/10 to-blue-500/5',
        border: 'border-blue-500/30',
        text: 'text-blue-400',
        glow: 'shadow-[0_0_20px_rgba(59,130,246,0.2)]',
    },
    gold: {
        bg: 'from-neon-gold/10 to-neon-gold/5',
        border: 'border-neon-gold/30',
        text: 'text-neon-gold',
        glow: 'shadow-[0_0_20px_rgba(255,215,0,0.2)]',
    },
    green: {
        bg: 'from-neon-green/10 to-neon-green/5',
        border: 'border-neon-green/30',
        text: 'text-neon-green',
        glow: 'shadow-[0_0_20px_rgba(0,255,157,0.2)]',
    },
    red: {
        bg: 'from-neon-red/10 to-neon-red/5',
        border: 'border-neon-red/30',
        text: 'text-neon-red',
        glow: 'shadow-[0_0_20px_rgba(255,0,85,0.2)]',
    },
};

export default function LivePrice({ symbol, name, color }: LivePriceProps) {
    const { data, isLoading, trend } = useMarketData(symbol);
    const [pulseClass, setPulseClass] = useState('');
    const prevPrice = useRef<number | null>(null);
    const colors = colorMap[color];

    // Pulse effect on price change
    useEffect(() => {
        if (data?.price && prevPrice.current !== null) {
            if (data.price > prevPrice.current) {
                setPulseClass('price-up');
            } else if (data.price < prevPrice.current) {
                setPulseClass('price-down');
            }
            const timer = setTimeout(() => setPulseClass(''), 600);
            return () => clearTimeout(timer);
        }
        if (data?.price) {
            prevPrice.current = data.price;
        }
    }, [data?.price]);

    // Skeleton loader
    if (isLoading) {
        return (
            <div className={`glass-panel rounded-xl p-4 border ${colors.border}`}>
                <div className="flex items-center justify-between">
                    <div className="space-y-2">
                        <div className="skeleton h-4 w-20"></div>
                        <div className="skeleton h-6 w-32"></div>
                    </div>
                    <div className="skeleton h-10 w-10 rounded-full"></div>
                </div>
            </div>
        );
    }

    const changePercent = data?.change_percent || 0;
    const isPositive = changePercent >= 0;

    return (
        <div
            className={`glass-panel rounded-xl p-4 border ${colors.border} ${colors.glow} 
                        transition-all duration-300 hover:scale-[1.02] ${pulseClass} fade-in`}
        >
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wider">{name}</p>
                    <p className={`text-2xl font-bold ${colors.text} font-mono`}>
                        ${data?.price?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '0.00'}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                        {isPositive ? (
                            <TrendingUp className="w-3 h-3 text-neon-green" />
                        ) : (
                            <TrendingDown className="w-3 h-3 text-neon-red" />
                        )}
                        <span className={`text-xs font-medium ${isPositive ? 'text-neon-green' : 'text-neon-red'}`}>
                            {isPositive ? '+' : ''}{changePercent.toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div className={`p-3 rounded-full bg-gradient-to-br ${colors.bg}`}>
                    <Activity className={`w-5 h-5 ${colors.text} ${trend === 'up' ? 'animate-bounce' : ''}`} />
                </div>
            </div>
        </div>
    );
}
