"use client";
import { useState, useEffect } from 'react';
import { FlaskConical, Circle } from 'lucide-react';

type TradingMode = 'testing' | 'live';

export default function ModeToggle() {
    const [mode, setMode] = useState<TradingMode>('testing');
    const [showConfirm, setShowConfirm] = useState(false);

    useEffect(() => {
        // Load saved mode from localStorage
        const saved = localStorage.getItem('trading_mode') as TradingMode | null;
        if (saved) setMode(saved);
    }, []);

    const handleModeChange = (newMode: TradingMode) => {
        if (newMode === 'live' && mode === 'testing') {
            setShowConfirm(true);
        } else {
            setMode(newMode);
            localStorage.setItem('trading_mode', newMode);
        }
    };

    const confirmLiveMode = () => {
        setMode('live');
        localStorage.setItem('trading_mode', 'live');
        setShowConfirm(false);
    };

    return (
        <>
            <div className="mode-toggle">
                <button
                    onClick={() => handleModeChange('testing')}
                    className={`mode-toggle-btn testing ${mode === 'testing' ? 'active' : ''}`}
                >
                    <FlaskConical className="w-3 h-3 inline mr-1" />
                    Testing
                </button>
                <button
                    onClick={() => handleModeChange('live')}
                    className={`mode-toggle-btn live ${mode === 'live' ? 'active' : ''}`}
                >
                    <Circle className="w-2 h-2 inline mr-1 fill-current" />
                    Live
                </button>
            </div>

            {/* Confirmation Modal */}
            {showConfirm && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                    <div className="bento-card max-w-md p-6 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--neon-red)]/20 flex items-center justify-center">
                            <Circle className="w-8 h-8 text-[var(--neon-red)] fill-current animate-pulse" />
                        </div>
                        <h2 className="text-xl font-bold text-white mb-2">Switch to Live Mode?</h2>
                        <p className="text-[var(--text-muted)] text-sm mb-6">
                            You are about to enable <strong className="text-[var(--neon-red)]">real money trading</strong>.
                            All trades will be executed on your connected OANDA account.
                        </p>
                        <div className="flex gap-3 justify-center">
                            <button
                                onClick={() => setShowConfirm(false)}
                                className="px-4 py-2 rounded-xl bg-[var(--surface)] text-white hover:bg-[var(--surface-hover)] transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmLiveMode}
                                className="px-4 py-2 rounded-xl bg-[var(--neon-red)] text-white font-bold hover:bg-[var(--neon-red)]/80 transition-colors"
                            >
                                Confirm Live Mode
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
