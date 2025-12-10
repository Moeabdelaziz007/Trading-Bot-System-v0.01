'use client';

import { Sidebar } from '@/components/dashboard/Sidebar';
import { Header } from '@/components/dashboard/Header';
import { BotScores } from '@/components/dashboard/BotScores';
import { PriceChart } from '@/components/dashboard/PriceChart';
import { AutomationPipeline } from '@/components/dashboard/AutomationPipeline';
import { TransactionsTable } from '@/components/dashboard/TransactionsTable';
import { TrendingTopics } from '@/components/dashboard/TrendingTopics';
import { PatternRecognition } from '@/components/dashboard/PatternRecognition';
// Self-Play Learning Loop Components
import { DialecticWarRoom } from '@/components/dialectic/DialecticWarRoom';
import { ResilienceMonitor } from '@/components/dialectic/ResilienceMonitor';
import { EvolutionaryOptimization } from '@/components/dialectic/EvolutionaryOptimization';
import { StrategyEngine } from '@/components/dialectic/StrategyEngine';
import { useState } from 'react';
import { SignedIn, SignedOut } from '@clerk/nextjs';
import { Brain } from 'lucide-react';

export default function DashboardPage() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    // Function to close the sidebar
    const closeSidebar = () => {
        setIsSidebarOpen(false);
    };

    // Function to toggle sidebar
    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="min-h-screen bg-axiom-bg text-gray-300 font-sans">
            <Sidebar isOpen={isSidebarOpen} onClose={closeSidebar} />

            <div className={`transition-all duration-300 ${isSidebarOpen ? 'lg:pl-64' : 'lg:pl-20'}`}>
                <Header toggleSidebar={toggleSidebar} />

                <main className="p-4 lg:p-6 max-w-[1600px] mx-auto space-y-6">
                    <SignedIn>
                        {/* Top Grid: Bot Scores & Price Chart */}
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                            <div className="lg:col-span-4 xl:col-span-3">
                                <BotScores />
                            </div>
                            <div className="lg:col-span-8 xl:col-span-9 h-[400px] lg:h-auto">
                                <PriceChart />
                            </div>
                        </div>

                        {/* ═══════════════════════════════════════════════════════════
                            SELF-PLAY LEARNING LOOP SECTION
                        ═══════════════════════════════════════════════════════════ */}
                        <div className="border-t border-gray-800 pt-6">
                            <div className="flex items-center gap-3 mb-6">
                                <Brain className="w-6 h-6 text-purple-400" />
                                <h2 className="text-xl font-mono font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                                    SELF_PLAY_LEARNING_LOOP
                                </h2>
                                <span className="text-xs font-mono text-gray-500 ml-2">V.2.4.0 | ACTIVE</span>
                            </div>

                            {/* Dialectic War Room - Full Width */}
                            <DialecticWarRoom />

                            {/* Resilience Monitor, Evolutionary Optimization & Strategy Engine */}
                            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
                                <ResilienceMonitor />
                                <EvolutionaryOptimization />
                                <StrategyEngine />
                            </div>
                        </div>
                        {/* ═══════════════════════════════════════════════════════════ */}

                        {/* Middle Grid: Pipeline, Trending, Patterns */}
                        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                            <div className="lg:col-span-4 xl:col-span-3">
                                <AutomationPipeline />
                            </div>
                            <div className="lg:col-span-4 xl:col-span-4">
                                <TrendingTopics />
                            </div>
                            <div className="lg:col-span-4 xl:col-span-5">
                                <PatternRecognition />
                            </div>
                        </div>

                        {/* Bottom: Transactions */}
                        <div className="grid grid-cols-1">
                            <TransactionsTable />
                        </div>
                    </SignedIn>

                    <SignedOut>
                        <div className="flex flex-col items-center justify-center h-[70vh] text-center">
                            <h1 className="text-3xl font-bold mb-4">Welcome to Axiom Antigravity</h1>
                            <p className="text-gray-400 mb-8 max-w-2xl">
                                Please sign in to access your personalized dashboard with real-time market data,
                                AI-powered trading bots, and advanced analytics.
                            </p>
                            <div className="bg-gradient-to-r from-axiom-primary to-blue-500 p-1 rounded-full">
                                <button
                                    className="bg-axiom-bg px-6 py-3 rounded-full font-semibold hover:bg-axiom-bg/90 transition-colors"
                                    onClick={() => window.location.href = '/sign-in'}
                                >
                                    Sign In to Continue
                                </button>
                            </div>
                        </div>
                    </SignedOut>
                </main>
            </div>

            {/* Overlay for sidebar - now works on all screen sizes */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30"
                    onClick={closeSidebar}
                />
            )}
        </div>
    );
}