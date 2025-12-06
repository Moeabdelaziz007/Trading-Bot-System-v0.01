"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, LineChart, Wallet, History, Bot, Settings, LogOut, Zap } from 'lucide-react';

const routes = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard', color: 'text-cyan-400' },
    { path: '/trade', icon: LineChart, label: 'Terminal', color: 'text-green-400' },
    { path: '/portfolio', icon: Wallet, label: 'Portfolio', color: 'text-yellow-400' },
    { path: '/history', icon: History, label: 'History', color: 'text-purple-400' },
    { path: '/automation', icon: Bot, label: 'Auto-Pilot', color: 'text-red-400' },
    { path: '/settings', icon: Settings, label: 'Settings', color: 'text-gray-400' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="flex flex-col h-full w-64 bg-[#050505] border-r border-gray-800">
            {/* Logo */}
            <div className="p-6 flex items-center gap-3 border-b border-gray-800">
                <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-cyan-500/20">
                    <Zap size={22} className="text-white" />
                </div>
                <div>
                    <h1 className="font-bold text-white tracking-wider">ANTIGRAVITY</h1>
                    <p className="text-[10px] text-gray-500">Trading LLM v2.0</p>
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 py-6 flex flex-col gap-1 px-3">
                {routes.map((route) => {
                    const Icon = route.icon;
                    const isActive = pathname === route.path;

                    return (
                        <Link
                            key={route.path}
                            href={route.path}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${isActive
                                    ? 'bg-gray-800/80 text-white border border-gray-700/50'
                                    : 'text-gray-400 hover:bg-gray-900 hover:text-white'
                                }`}
                        >
                            <Icon size={20} className={isActive ? route.color : 'text-gray-500'} />
                            <span className="font-medium text-sm">{route.label}</span>
                        </Link>
                    );
                })}
            </div>

            {/* Status */}
            <div className="px-4 pb-4">
                <div className="bg-gray-900/50 rounded-xl p-4 border border-gray-800/50 space-y-2">
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">AI Status</span>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                            <span className="text-xs text-green-400">Online</span>
                        </div>
                    </div>
                    <div className="flex items-center justify-between">
                        <span className="text-xs text-gray-500">Broker</span>
                        <span className="text-xs text-cyan-400">Alpaca</span>
                    </div>
                </div>
            </div>

            {/* Disconnect */}
            <div className="p-4 border-t border-gray-800">
                <button className="flex items-center gap-3 px-4 py-3 w-full text-gray-400 hover:text-red-400 transition-colors rounded-xl hover:bg-gray-900/50">
                    <LogOut size={20} />
                    <span className="text-sm">Disconnect</span>
                </button>
            </div>
        </div>
    );
}
