'use client';

/**
 * Smart MCP Card Component
 * 
 * Displays real-time market intelligence with signal indicators.
 * Shows price, change percentage, signal direction, and confidence.
 */

import { useSmartMCP, MarketIntelligence } from '@/lib/hooks/useSmartMCP';

interface SmartMCPCardProps {
    symbol: string;
    showDetails?: boolean;
}

// Signal color mapping
const SIGNAL_COLORS: Record<string, { bg: string; text: string; border: string }> = {
    STRONG_BUY: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500' },
    BUY: { bg: 'bg-green-400/10', text: 'text-green-300', border: 'border-green-400' },
    NEUTRAL: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500' },
    SELL: { bg: 'bg-red-400/10', text: 'text-red-300', border: 'border-red-400' },
    STRONG_SELL: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500' },
};

// Signal emoji
const SIGNAL_EMOJI: Record<string, string> = {
    STRONG_BUY: '🚀',
    BUY: '📈',
    NEUTRAL: '➡️',
    SELL: '📉',
    STRONG_SELL: '💥',
};

export function SmartMCPCard({ symbol, showDetails = true }: SmartMCPCardProps) {
    const { data, error, isLoading, refresh } = useSmartMCP(symbol);

    if (isLoading) {
        return (
            <div className="bg-carbon-800/50 border border-white/10 rounded-xl p-4 animate-pulse">
                <div className="h-6 bg-gray-700 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-700 rounded w-32"></div>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="bg-carbon-800/50 border border-red-500/30 rounded-xl p-4">
                <div className="text-red-400 text-sm">{symbol}: Error loading</div>
                <button
                    onClick={() => refresh()}
                    className="text-xs text-cyan-400 hover:underline mt-2"
                >
                    Retry
                </button>
            </div>
        );
    }

    const signal = data.composite_signal;
    const colors = SIGNAL_COLORS[signal.direction] || SIGNAL_COLORS.NEUTRAL;
    const emoji = SIGNAL_EMOJI[signal.direction] || '➡️';
    const priceChange = data.price.change_pct * 100;
    const isPositive = priceChange >= 0;

    return (
        <div
            className={`bg-carbon-900/60 backdrop-blur-md border ${colors.border}/30 rounded-xl p-4 
                  hover:border-cyan-500/50 transition-all duration-300 cursor-pointer`}
            onClick={() => refresh()}
        >
            {/* Header */}
            <div className="flex justify-between items-start mb-3">
                <div>
                    <div className="flex items-center gap-2">
                        <span className="text-white font-bold text-lg">{data.symbol}</span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${data.asset_type === 'crypto' ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'}`}>
                            {data.asset_type}
                        </span>
                    </div>
                    <div className="text-gray-500 text-xs mt-0.5">
                        Source: {data.price.source}
                    </div>
                </div>

                {/* Signal Badge */}
                <div className={`${colors.bg} ${colors.text} px-3 py-1 rounded-full text-sm font-medium flex items-center gap-1`}>
                    {emoji} {signal.direction.replace('_', ' ')}
                </div>
            </div>

            {/* Price */}
            <div className="mb-3">
                <div className="text-2xl font-bold text-white">
                    ${data.price.current.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={`text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
                </div>
            </div>

            {/* Details */}
            {showDetails && (
                <div className="border-t border-white/10 pt-3 space-y-2">
                    {/* Confidence Bar */}
                    <div>
                        <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Confidence</span>
                            <span>{Math.round(signal.confidence * 100)}%</span>
                        </div>
                        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                            <div
                                className={`h-full ${colors.bg.replace('/20', '')} transition-all duration-500`}
                                style={{ width: `${signal.confidence * 100}%` }}
                            />
                        </div>
                    </div>

                    {/* Factors */}
                    {signal.factors && signal.factors.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                            {signal.factors.map((factor, idx) => (
                                <span key={idx} className="text-xs bg-white/5 text-gray-300 px-2 py-0.5 rounded">
                                    {factor}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* Stale Warning */}
                    {data.is_stale && (
                        <div className="text-xs text-yellow-400 flex items-center gap-1">
                            ⚠️ Data may be stale
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// Mini version for compact displays
export function SmartMCPMini({ symbol }: { symbol: string }) {
    const { data, isLoading } = useSmartMCP(symbol);

    if (isLoading || !data) {
        return <span className="text-gray-500">...</span>;
    }

    const priceChange = data.price.change_pct * 100;
    const isPositive = priceChange >= 0;
    const emoji = SIGNAL_EMOJI[data.composite_signal.direction] || '➡️';

    return (
        <span className="inline-flex items-center gap-2">
            <span className="font-medium">{data.symbol}</span>
            <span className="text-white">${data.price.current.toLocaleString()}</span>
            <span className={isPositive ? 'text-green-400' : 'text-red-400'}>
                {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
            </span>
            <span>{emoji}</span>
        </span>
    );
}
