'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Shield, AlertTriangle, Activity } from 'lucide-react';

interface RiskMetrics {
    dailyPnL: number;
    dailyPnLPercent: number;
    riskConsumed: number;
    maxDailyRisk: number;
    openPositions: number;
    maxPositions: number;
    largestPosition: number;
    maxPositionSize: number;
}

interface RiskDashboardProps {
    metrics?: RiskMetrics;
    isLoading?: boolean;
}

/**
 * 📊 Risk Dashboard Component
 * Displays real-time risk metrics aligned with RISK_MODEL.md constitution.
 */
export const RiskDashboard: React.FC<RiskDashboardProps> = ({
    metrics,
    isLoading = false
}) => {
    // Default metrics for demo/loading state
    const defaultMetrics: RiskMetrics = {
        dailyPnL: 0,
        dailyPnLPercent: 0,
        riskConsumed: 0,
        maxDailyRisk: 5.0,
        openPositions: 0,
        maxPositions: 5,
        largestPosition: 0,
        maxPositionSize: 5.0
    };

    const data = metrics || defaultMetrics;

    // Calculate risk consumption percentage
    const riskUsagePercent = (data.riskConsumed / data.maxDailyRisk) * 100;
    const positionUsagePercent = (data.openPositions / data.maxPositions) * 100;

    // Determine risk status
    const getRiskStatus = () => {
        if (riskUsagePercent >= 80) return { label: 'CRITICAL', color: 'text-axiom-neon-red', bg: 'bg-axiom-neon-red/20' };
        if (riskUsagePercent >= 50) return { label: 'ELEVATED', color: 'text-yellow-400', bg: 'bg-yellow-400/20' };
        return { label: 'NORMAL', color: 'text-axiom-neon-green', bg: 'bg-axiom-neon-green/20' };
    };

    const riskStatus = getRiskStatus();

    const ProgressBar: React.FC<{ value: number; max: number; color: string }> = ({ value, max, color }) => (
        <div className="w-full h-2 bg-axiom-bg/50 rounded-full overflow-hidden">
            <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.min((value / max) * 100, 100)}%` }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className={`h-full ${color} rounded-full`}
            />
        </div>
    );

    if (isLoading) {
        return (
            <div className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 animate-pulse">
                <div className="h-6 bg-axiom-bg/50 rounded w-1/3 mb-4"></div>
                <div className="space-y-4">
                    <div className="h-16 bg-axiom-bg/50 rounded"></div>
                    <div className="h-16 bg-axiom-bg/50 rounded"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Shield className="w-6 h-6 text-axiom-neon-purple" />
                    <h2 className="text-xl font-mono font-bold text-white tracking-tight">
                        RISK_DASHBOARD
                    </h2>
                </div>
                <div className={`px-3 py-1 rounded-full ${riskStatus.bg} ${riskStatus.color} text-xs font-mono font-bold`}>
                    {riskStatus.label}
                </div>
            </div>

            {/* Main Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Daily P&L Card */}
                <div className="bg-axiom-bg/60 rounded-lg p-4 border border-glass-border/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-text-muted font-mono">DAILY P&L</span>
                        {data.dailyPnL >= 0 ? (
                            <TrendingUp className="w-4 h-4 text-axiom-neon-green" />
                        ) : (
                            <TrendingDown className="w-4 h-4 text-axiom-neon-red" />
                        )}
                    </div>
                    <div className="flex items-baseline gap-2">
                        <span className={`text-2xl font-mono font-bold ${data.dailyPnL >= 0 ? 'text-axiom-neon-green' : 'text-axiom-neon-red'}`}>
                            {data.dailyPnL >= 0 ? '+' : ''}{data.dailyPnL.toFixed(2)}
                        </span>
                        <span className={`text-sm font-mono ${data.dailyPnLPercent >= 0 ? 'text-axiom-neon-green' : 'text-axiom-neon-red'}`}>
                            ({data.dailyPnLPercent >= 0 ? '+' : ''}{data.dailyPnLPercent.toFixed(2)}%)
                        </span>
                    </div>
                </div>

                {/* Risk Consumed Card */}
                <div className="bg-axiom-bg/60 rounded-lg p-4 border border-glass-border/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-text-muted font-mono">DAILY RISK CONSUMED</span>
                        {riskUsagePercent >= 80 && <AlertTriangle className="w-4 h-4 text-axiom-neon-red animate-pulse" />}
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                        <span className="text-2xl font-mono font-bold text-white">
                            {data.riskConsumed.toFixed(2)}%
                        </span>
                        <span className="text-sm font-mono text-text-muted">
                            / {data.maxDailyRisk}% MAX
                        </span>
                    </div>
                    <ProgressBar
                        value={data.riskConsumed}
                        max={data.maxDailyRisk}
                        color={riskUsagePercent >= 80 ? 'bg-axiom-neon-red' : riskUsagePercent >= 50 ? 'bg-yellow-400' : 'bg-axiom-neon-green'}
                    />
                </div>

                {/* Open Positions Card */}
                <div className="bg-axiom-bg/60 rounded-lg p-4 border border-glass-border/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-text-muted font-mono">OPEN POSITIONS</span>
                        <Activity className="w-4 h-4 text-axiom-neon-cyan" />
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                        <span className="text-2xl font-mono font-bold text-white">
                            {data.openPositions}
                        </span>
                        <span className="text-sm font-mono text-text-muted">
                            / {data.maxPositions} MAX
                        </span>
                    </div>
                    <ProgressBar
                        value={data.openPositions}
                        max={data.maxPositions}
                        color="bg-axiom-neon-cyan"
                    />
                </div>

                {/* Largest Position Card */}
                <div className="bg-axiom-bg/60 rounded-lg p-4 border border-glass-border/50">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-text-muted font-mono">LARGEST POSITION</span>
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                        <span className="text-2xl font-mono font-bold text-white">
                            {data.largestPosition.toFixed(2)}%
                        </span>
                        <span className="text-sm font-mono text-text-muted">
                            / {data.maxPositionSize}% LIMIT
                        </span>
                    </div>
                    <ProgressBar
                        value={data.largestPosition}
                        max={data.maxPositionSize}
                        color="bg-axiom-neon-purple"
                    />
                </div>
            </div>

            {/* Footer: Risk Constitution Reference */}
            <div className="mt-4 pt-4 border-t border-glass-border/30">
                <p className="text-xs text-text-muted font-mono text-center">
                    Governed by <span className="text-axiom-neon-cyan">RISK_MODEL.md</span> |
                    Guardian: <span className="text-axiom-neon-green">ACTIVE</span> |
                    Circuit Breaker: <span className="text-axiom-neon-green">ARMED</span>
                </p>
            </div>
        </div>
    );
};

export default RiskDashboard;
