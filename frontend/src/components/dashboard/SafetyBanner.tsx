'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, ShieldCheck, Info } from 'lucide-react';

interface SafetyBannerProps {
    mode: 'paper' | 'demo' | 'live';
    disclaimerText?: string;
}

/**
 * 🛡️ Safety Banner Component
 * Displays a prominent banner indicating the current trading mode.
 * Required for investor transparency and regulatory compliance.
 */
export const SafetyBanner: React.FC<SafetyBannerProps> = ({
    mode = 'paper',
    disclaimerText
}) => {
    const modeConfig = {
        paper: {
            icon: <ShieldCheck className="w-5 h-5" />,
            title: 'PAPER TRADING MODE',
            subtitle: 'No real money at risk. All trades are simulated.',
            bgColor: 'bg-axiom-neon-cyan/10',
            borderColor: 'border-axiom-neon-cyan/50',
            textColor: 'text-axiom-neon-cyan',
            glowClass: 'shadow-[0_0_15px_rgba(0,255,255,0.2)]'
        },
        demo: {
            icon: <Info className="w-5 h-5" />,
            title: 'DEMO MODE',
            subtitle: 'Connected to demo broker. Virtual balance only.',
            bgColor: 'bg-yellow-500/10',
            borderColor: 'border-yellow-500/50',
            textColor: 'text-yellow-400',
            glowClass: 'shadow-[0_0_15px_rgba(255,200,0,0.2)]'
        },
        live: {
            icon: <AlertTriangle className="w-5 h-5" />,
            title: 'LIVE TRADING',
            subtitle: 'Real capital at risk. Trade responsibly.',
            bgColor: 'bg-axiom-neon-red/10',
            borderColor: 'border-axiom-neon-red/50',
            textColor: 'text-axiom-neon-red',
            glowClass: 'shadow-[0_0_15px_rgba(255,50,50,0.3)]'
        }
    };

    const config = modeConfig[mode];

    return (
        <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`w-full ${config.bgColor} ${config.borderColor} ${config.glowClass} border rounded-lg p-3 mb-4`}
        >
            <div className="flex items-center justify-between">
                {/* Left: Icon + Title */}
                <div className="flex items-center gap-3">
                    <div className={`${config.textColor}`}>
                        {config.icon}
                    </div>
                    <div>
                        <h3 className={`text-sm font-mono font-bold ${config.textColor} tracking-wider`}>
                            {config.title}
                        </h3>
                        <p className="text-xs text-text-muted font-mono">
                            {config.subtitle}
                        </p>
                    </div>
                </div>

                {/* Right: Disclaimer */}
                {disclaimerText && (
                    <p className="text-xs text-text-muted font-mono max-w-xs text-right hidden md:block">
                        {disclaimerText}
                    </p>
                )}
            </div>

            {/* Conditions for Live (only shown in paper/demo mode) */}
            {mode !== 'live' && (
                <div className="mt-3 pt-3 border-t border-glass-border/30">
                    <p className="text-xs text-text-muted font-mono">
                        <span className="font-bold text-white">Prerequisites for Live Capital:</span>{' '}
                        ✅ 30-day paper trading history | ✅ &gt;60% win rate | ✅ Risk acknowledged
                    </p>
                </div>
            )}
        </motion.div>
    );
};

export default SafetyBanner;
