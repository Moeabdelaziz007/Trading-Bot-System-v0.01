"use client";
import PortfolioDonut from '@/components/PortfolioDonut';
import PLChart from '@/components/PLChart';
import ActiveBots from '@/components/ActiveBots';
import TelegramWidget from '@/components/TelegramWidget';
import LivePositions from '@/components/LivePositions';
import TwinTurboGauges from '@/components/TwinTurboGauges';
import SentimentPanel from '@/components/SentimentPanel';
import PatternAlerts from '@/components/PatternAlerts';
import NewsImpactBadge from '@/components/NewsImpactBadge';
import SignalFeed from '@/components/SignalFeed';
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
            {/* Page Title + News Impact */}
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">My Dashboard</h1>
                    <p className="text-sm text-[var(--text-muted)]">
                        {account?.source ? `Connected to ${account.source}` : 'Demo Mode'}
                    </p>
                </div>
                <NewsImpactBadge />
            </div>

            {/* Bento Grid - Row 1 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <PortfolioDonut equity={equity} />
                <PLChart />
                <ActiveBots />
            </div>

            {/* Bento Grid - Row 2: AI Intelligence */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <SentimentPanel />
                <PatternAlerts />
                <SignalFeed />
            </div>

            {/* Bento Grid - Row 3: Positions */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <LivePositions />
                </div>
                <TelegramWidget />
            </div>

            {/* Bento Grid - Row 4: AI Engines */}
            <div className="grid grid-cols-1 gap-6">
                <TwinTurboGauges />
            </div>

            {/* Bottom Stats Banner */}
            <div className="bento-card flex flex-col md:flex-row items-center justify-between p-4 gap-4">
                <div className="flex items-center gap-8">
                    <div>
                        <p className="text-xs text-[var(--text-dim)] uppercase">Total Equity</p>
                        <p className="text-xl font-bold font-mono text-white">${equity.toLocaleString()}</p>
                    </div>
                    <div className="w-px h-10 bg-[var(--glass-border)]" />
                    <div>
                        <p className="text-xs text-[var(--text-dim)] uppercase">Today&apos;s P/L</p>
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

