"use client";
import { motion } from 'framer-motion';
import {
    User,
    CreditCard,
    TrendingUp,
    Trophy,
    Activity,
    Clock,
    Shield
} from 'lucide-react';
import { useUser } from '@clerk/nextjs';

export default function ProfilePage() {
    const { user, isLoaded } = useUser();
    
    // Mock Data (will be connected to API later)
    const userData = {
        name: isLoaded && user ? `${user.firstName} ${user.lastName}` : "Loading...",
        email: isLoaded && user ? user.emailAddresses[0]?.emailAddress : "",
        tier: "Diamond Pro",
        balance: 102540.50,
        pnl: 2540.50,
        winRate: 68.5,
        trades: 142,
        joinDate: "Dec 2024"
    };

    if (!isLoaded) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse">Loading profile...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen space-y-6 animate-fade-in p-2 md:p-0 pb-20">
            {/* Header: Cyberpunk ID Card */}
            <div className="bento-card p-8 bg-carbon-fiber relative overflow-hidden group">
                <div className="absolute top-0 right-0 p-8 opacity-20">
                    <User className="w-48 h-48 text-[var(--neon-cyan)] rotate-12" />
                </div>

                <div className="flex flex-col md:flex-row items-start md:items-center gap-6 relative z-10">
                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-[var(--neon-purple)] to-[var(--neon-cyan)] p-1">
                        <div className="w-full h-full bg-[var(--void)] rounded-xl flex items-center justify-center">
                            {user?.imageUrl ? (
                                <img 
                                    src={user.imageUrl} 
                                    alt="Profile" 
                                    className="w-full h-full rounded-xl object-cover"
                                />
                            ) : (
                                <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[var(--neon-purple)] to-[var(--neon-cyan)] animate-pulse">
                                    {userData.name.charAt(0)}
                                </span>
                            )}
                        </div>
                    </div>

                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <h1 className="text-3xl font-bold text-white tracking-tight">{userData.name}</h1>
                            <span className="px-3 py-1 rounded-full bg-[var(--neon-gold)]/20 text-[var(--neon-gold)] text-xs font-bold border border-[var(--neon-gold)]/50 flex items-center gap-1">
                                <Trophy className="w-3 h-3" /> {userData.tier}
                            </span>
                        </div>
                        <p className="text-[var(--text-muted)] font-mono text-sm flex items-center gap-4">
                            <span className="flex items-center gap-1"><Shield className="w-4 h-4" /> Email: {userData.email}</span>
                            <span className="flex items-center gap-1"><Clock className="w-4 h-4" /> Member since {userData.joinDate}</span>
                        </p>
                    </div>
                </div>
            </div>

            {/* Performance Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div
                    whileHover={{ y: -5 }}
                    className="bento-card p-6 border-l-4 border-l-[var(--neon-green)]"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <p className="text-sm text-[var(--text-muted)] uppercase mb-1">Total Balance</p>
                            <h3 className="text-3xl font-bold text-white font-mono">${userData.balance.toLocaleString()}</h3>
                        </div>
                        <div className="p-3 rounded-xl bg-[var(--neon-green)]/10 text-[var(--neon-green)]">
                            <CreditCard className="w-6 h-6" />
                        </div>
                    </div>
                    <div className="text-xs text-[var(--neon-green)] font-bold flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" /> +2.4% this week
                    </div>
                </motion.div>

                <motion.div
                    whileHover={{ y: -5 }}
                    className="bento-card p-6 border-l-4 border-l-[var(--neon-cyan)]"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <p className="text-sm text-[var(--text-muted)] uppercase mb-1">Net P/L</p>
                            <h3 className="text-3xl font-bold text-[var(--neon-cyan)] font-mono">+${userData.pnl.toLocaleString()}</h3>
                        </div>
                        <div className="p-3 rounded-xl bg-[var(--neon-cyan)]/10 text-[var(--neon-cyan)]">
                            <Activity className="w-6 h-6" />
                        </div>
                    </div>
                    <div className="w-full bg-[var(--surface)] h-1 rounded-full overflow-hidden mt-2">
                        <div className="w-[70%] h-full bg-[var(--neon-cyan)] shadow-[0_0_10px_var(--neon-cyan)]" />
                    </div>
                </motion.div>

                <motion.div
                    whileHover={{ y: -5 }}
                    className="bento-card p-6 border-l-4 border-l-[var(--neon-purple)]"
                >
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <p className="text-sm text-[var(--text-muted)] uppercase mb-1">Win Rate</p>
                            <h3 className="text-3xl font-bold text-[var(--neon-purple)] font-mono">{userData.winRate}%</h3>
                        </div>
                        <div className="p-3 rounded-xl bg-[var(--neon-purple)]/10 text-[var(--neon-purple)]">
                            <Trophy className="w-6 h-6" />
                        </div>
                    </div>
                    <p className="text-xs text-[var(--text-muted)]">Based on {userData.trades} total trades</p>
                </motion.div>
            </div>

            {/* Trade History Mock Table */}
            <div className="bento-card p-6">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-[var(--neon-blue)]" />
                    Recent Activity
                </h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs uppercase text-[var(--text-dim)] border-b border-[var(--glass-border)]">
                            <tr>
                                <th className="px-4 py-3">Symbol</th>
                                <th className="px-4 py-3">Type</th>
                                <th className="px-4 py-3">Entry</th>
                                <th className="px-4 py-3">P/L</th>
                                <th className="px-4 py-3">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--glass-border)]">
                            {[1, 2, 3].map((i) => (
                                <tr key={i} className="hover:bg-[var(--surface)] transition-colors">
                                    <td className="px-4 py-3 font-bold text-white">EURUSD</td>
                                    <td className="px-4 py-3 text-[var(--neon-green)]">LONG</td>
                                    <td className="px-4 py-3 font-mono">1.0845</td>
                                    <td className="px-4 py-3 font-mono text-[var(--neon-green)]">+$125.00</td>
                                    <td className="px-4 py-3"><span className="status-online">Closed</span></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}