"use client";
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
    Settings,
    ShieldAlert,
    Zap,
    Key,
    Save,
    Power,
    Activity,
    Lock,
    User,
    Mail,
    Phone
} from 'lucide-react';
import { useUser } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';

export default function SettingsPage() {
    const { user, isLoaded } = useUser();
    const router = useRouter();
    const [settings, setSettings] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [userDetails, setUserDetails] = useState({
        firstName: '',
        lastName: '',
        email: '',
        phone: ''
    });

    useEffect(() => {
        // Initialize mock settings
        setSettings({
            risk: {
                killSwitch: false,
                riskPerTrade: 1.0,
                level: 'Medium'
            },
            strategy: {
                aexiThreshold: 75,
                dreamThreshold: 80,
                activeTimeframes: ['M5', 'H1', 'D1']
            },
            apiKeys: {
                capital: '••••••••••••CAPITAL',
                zai_glm: '••••••••••••GLM45'
            }
        });

        // Initialize user details
        if (isLoaded && user) {
            setUserDetails({
                firstName: user.firstName || '',
                lastName: user.lastName || '',
                email: user.emailAddresses[0]?.emailAddress || '',
                phone: user.phoneNumbers[0]?.phoneNumber || ''
            });
        }

        setLoading(false);
    }, [isLoaded, user]);

    const handleSave = async () => {
        setSaving(true);
        try {
            // In a real app, you would save to your backend here
            await new Promise(resolve => setTimeout(resolve, 1000)); // Fake delay for UX
            setSaving(false);
        } catch (e) {
            setSaving(false);
        }
    };

    const handleUpdateUser = async () => {
        if (!user) return;

        setSaving(true);
        try {
            // Update user details through Clerk
            await user.update({
                firstName: userDetails.firstName,
                lastName: userDetails.lastName,
            });
            setSaving(false);
        } catch (e) {
            setSaving(false);
        }
    };

    const updateRisk = (key: string, val: any) => {
        setSettings({ ...settings, risk: { ...settings.risk, [key]: val } });
    };

    const updateStrategy = (key: string, val: any) => {
        setSettings({ ...settings, strategy: { ...settings.strategy, [key]: val } });
    };

    const handleSignOut = async () => {
        try {
            // Sign out through Clerk
            await fetch('/api/auth/signout', { method: 'POST' });
            router.push('/');
        } catch (error) {
            console.error('Sign out error:', error);
        }
    };

    if (!isLoaded || loading) {
        return <div className="p-8 text-[var(--neon-cyan)] animate-pulse">Loading Configurations...</div>;
    }

    return (
        <div className="min-h-screen space-y-6 animate-fade-in p-2 md:p-0 pb-20">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-[var(--neon-green)] to-[var(--neon-cyan)] flex items-center gap-3">
                        <Settings className="w-8 h-8 text-[var(--neon-green)]" />
                        Expert Configuration
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-1 font-mono">
                        System Level Controls • Risk Management • API Keys
                    </p>
                </div>

                <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleSave}
                    disabled={saving}
                    className="px-6 py-2 rounded-lg bg-[var(--neon-cyan)] text-black font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(0,240,255,0.4)]"
                >
                    <Save className="w-4 h-4" />
                    {saving ? 'Saving...' : 'Save Changes'}
                </motion.button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* User Profile Section */}
                <div className="bento-card p-6 border-l-4 border-l-[var(--neon-blue)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <User className="w-6 h-6 text-[var(--neon-blue)]" />
                        User Profile
                    </h2>

                    <div className="space-y-4">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-[var(--neon-purple)] to-[var(--neon-cyan)] p-1">
                                <div className="w-full h-full bg-[var(--void)] rounded-lg flex items-center justify-center">
                                    {user?.imageUrl ? (
                                        <img
                                            src={user.imageUrl}
                                            alt="Profile"
                                            className="w-full h-full rounded-lg object-cover"
                                        />
                                    ) : (
                                        <span className="text-xl font-bold text-white">
                                            {userDetails.firstName?.charAt(0)}{userDetails.lastName?.charAt(0)}
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div>
                                <h3 className="font-bold text-white">{userDetails.firstName} {userDetails.lastName}</h3>
                                <p className="text-xs text-[var(--text-muted)]">{userDetails.email}</p>
                            </div>
                        </div>

                        <div>
                            <label className="text-sm font-bold mb-2 block">First Name</label>
                            <input
                                type="text"
                                value={userDetails.firstName}
                                onChange={(e) => setUserDetails({ ...userDetails, firstName: e.target.value })}
                                className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-2 text-sm focus:border-[var(--neon-blue)] focus:outline-none"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-bold mb-2 block">Last Name</label>
                            <input
                                type="text"
                                value={userDetails.lastName}
                                onChange={(e) => setUserDetails({ ...userDetails, lastName: e.target.value })}
                                className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-2 text-sm focus:border-[var(--neon-blue)] focus:outline-none"
                            />
                        </div>

                        <div>
                            <label className="text-sm font-bold mb-2 block">Email</label>
                            <div className="relative">
                                <input
                                    type="email"
                                    value={userDetails.email}
                                    readOnly
                                    className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-2 text-sm opacity-70"
                                />
                                <Mail className="absolute right-3 top-2.5 w-4 h-4 text-[var(--text-dim)]" />
                            </div>
                        </div>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={handleUpdateUser}
                            disabled={saving}
                            className="w-full py-2 rounded-lg bg-[var(--neon-blue)] text-black font-bold flex items-center justify-center gap-2"
                        >
                            Update Profile
                        </motion.button>

                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={handleSignOut}
                            className="w-full py-2 rounded-lg bg-red-500/20 border border-red-500/50 text-red-400 font-bold flex items-center justify-center gap-2"
                        >
                            <Power className="w-4 h-4" />
                            Sign Out
                        </motion.button>
                    </div>
                </div>

                {/* 1. Risk Management Section */}
                <div className="bento-card p-6 border-l-4 border-l-[var(--neon-green)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <ShieldAlert className="w-6 h-6 text-[var(--neon-green)]" />
                        Risk Management
                    </h2>

                    <div className="space-y-6">
                        {/* Kill Switch */}
                        <div className="flex items-center justify-between p-4 bg-[var(--void)] border border-[var(--glass-border)] rounded-xl">
                            <div>
                                <h3 className="font-bold text-red-500 flex items-center gap-2">
                                    <Power className="w-4 h-4" /> EMERGENCY KILL SWITCH
                                </h3>
                                <p className="text-xs text-[var(--text-muted)]">Instantly stop all trading and cancel orders</p>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={settings?.risk?.killSwitch}
                                    onChange={(e) => updateRisk('killSwitch', e.target.checked)}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-red-600 shadow-[0_0_10px_rgba(255,0,0,0.5)]"></div>
                            </label>
                        </div>

                        {/* Risk Per Trade */}
                        <div>
                            <div className="flex justify-between mb-2">
                                <label className="text-sm font-bold">Risk Per Trade (%)</label>
                                <span className="text-[var(--neon-green)] font-mono">{settings?.risk?.riskPerTrade}%</span>
                            </div>
                            <input
                                type="range"
                                min="0.1"
                                max="5.0"
                                step="0.1"
                                value={settings?.risk?.riskPerTrade}
                                onChange={(e) => updateRisk('riskPerTrade', parseFloat(e.target.value))}
                                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-[var(--neon-green)]"
                            />
                        </div>

                        {/* Risk Level Selector */}
                        <div>
                            <label className="text-sm font-bold mb-2 block">Risk Profile</label>
                            <div className="grid grid-cols-3 gap-2">
                                {['Low', 'Medium', 'High'].map((level) => (
                                    <button
                                        key={level}
                                        onClick={() => updateRisk('level', level)}
                                        className={`py-2 rounded-lg text-sm border transition-all ${settings?.risk?.level === level
                                            ? 'border-[var(--neon-green)] bg-[var(--neon-green)]/10 text-[var(--neon-green)] shadow-[0_0_10px_rgba(0,255,0,0.2)]'
                                            : 'border-[var(--glass-border)] text-[var(--text-dim)] hover:border-[var(--neon-green)]/50'
                                            }`}
                                    >
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Note: Strategy Engine has been moved to Dashboard > Self-Play Learning Loop */}

                {/* 3. API Keys (Full Width) */}
                <div className="md:col-span-2 bento-card p-6 border-l-4 border-l-[var(--neon-cyan)]">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Key className="w-6 h-6 text-[var(--neon-cyan)]" />
                        API Connections
                    </h2>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-mono text-[var(--neon-cyan)]">Capital.com API Key</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={settings?.apiKeys?.capital}
                                    readOnly
                                    className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-3 text-sm focus:border-[var(--neon-cyan)] focus:outline-none"
                                />
                                <Lock className="absolute right-3 top-3 w-4 h-4 text-[var(--text-dim)]" />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-mono text-[var(--neon-purple)]">Z.ai GLM-4.5 API Key</label>
                            <div className="relative">
                                <input
                                    type="password"
                                    value={settings?.apiKeys?.zai_glm}
                                    readOnly
                                    className="w-full bg-[var(--void)] border border-[var(--glass-border)] rounded-lg p-3 text-sm focus:border-[var(--neon-purple)] focus:outline-none"
                                />
                                <Lock className="absolute right-3 top-3 w-4 h-4 text-[var(--text-dim)]" />
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}