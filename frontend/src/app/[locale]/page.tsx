"use client";
import PortfolioDonut from '@/components/PortfolioDonut';
import PLChart from '@/components/PLChart';
import ActiveBots from '@/components/ActiveBots';
import TelegramWidget from '@/components/TelegramWidget';
import LivePositions from '@/components/LivePositions';
import TwinTurboGauges from '@/components/TwinTurboGauges';
import { useEffect, useState } from 'react';

interface AccountData {
    equity: string;
    portfolio_value: string;
    source?: string;
}

export default function Dashboard() {
    const [account, setAccount] = useState<AccountData | null>(null);

    useEffect(() => {
        const fetchAccount = async () => {
            try {
                const res = await fetch('/api/account');
                if (res.ok) {
                    const data = await res.json();
                    setAccount(data);
                }
            } catch (e) {
                console.error('Failed to fetch account', e);
            }
        };
        fetchAccount();
        const interval = setInterval(fetchAccount, 10000);
        return () => clearInterval(interval);
    }, []);

    const equity = parseFloat(account?.equity || account?.portfolio_value || '100000');

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Page Title */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white">My Dashboard</h1>
                    <p className="text-sm text-[var(--text-muted)]">
                        {account?.source ? `Connected to ${account.source}` : 'Demo Mode'}
                    </p>
                </div>
            </div>

            {/* Bento Grid - Row 1 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Portfolio Overview (Donut) */}
                <PortfolioDonut equity={equity} />

                {/* Profit & Loss Chart */}
                <PLChart />

                {/* Active Bots */}
                <ActiveBots />
            </div>

            {/* Bento Grid - Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Live Positions - Takes 2 columns */}
                <div className="lg:col-span-2">
                    <LivePositions />
                </div>

                {/* Telegram Widget */}
                <TelegramWidget />
            </div>

            {/* Bento Grid - Row 3: AI Engines */}
            <div className="grid grid-cols-1 gap-6">
                <TwinTurboGauges />
            </div>

            {/* Bottom Stats Banner */}
            <div className="bento-card flex items-center justify-between p-4">
                <div className="flex items-center gap-8">
                    <div>
                        <p className="text-xs text-[var(--text-dim)] uppercase">Total Equity</p>
                        <p className="text-xl font-bold font-mono text-white">${equity.toLocaleString()}</p>
                    </div>
                    <div className="w-px h-10 bg-[var(--glass-border)]" />
                    <div>
                        <p className="text-xs text-[var(--text-dim)] uppercase">Today's P/L</p>
                        <p className="text-xl font-bold font-mono text-[var(--neon-green)]">+$1,245.00</p>
                    </div>
                    <div className="w-px h-10 bg-[var(--glass-border)]" />
                    <div>
                        <p className="text-xs text-[var(--text-dim)] uppercase">Active Trades</p>
                        <p className="text-xl font-bold font-mono text-white">3</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-[var(--neon-green)] rounded-full animate-pulse" />
                    <span className="text-sm text-[var(--neon-green)] font-medium">Market Open</span>
                </div>
            </div>
        </div>
    );
}
