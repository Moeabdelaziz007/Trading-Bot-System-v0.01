'use client';

import { Sidebar } from '@/components/dashboard/Sidebar';
import { Header } from '@/components/dashboard/Header';
import { BotScores } from '@/components/dashboard/BotScores';
import { PriceChart } from '@/components/dashboard/PriceChart';
import { AutomationPipeline } from '@/components/dashboard/AutomationPipeline';
import { TransactionsTable } from '@/components/dashboard/TransactionsTable';
import { TrendingTopics } from '@/components/dashboard/TrendingTopics';
import { PatternRecognition } from '@/components/dashboard/PatternRecognition';
import ConnectWallet from '@/components/dashboard/ConnectWallet';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function DashboardPage() {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [oauthMessage, setOauthMessage] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
    const searchParams = useSearchParams();

    // Handle OAuth success/error messages from URL parameters
    useEffect(() => {
        const oauthSuccess = searchParams.get('oauth_success');
        const oauthError = searchParams.get('oauth_error');
        
        if (oauthSuccess === 'true') {
            setOauthMessage({
                type: 'success',
                message: 'تم ربط حساب Coinbase بنجاح!'
            });
        } else if (oauthError) {
            let errorMessage = 'فشل في ربط حساب Coinbase. ';
            switch (oauthError) {
                case 'access_denied':
                    errorMessage += 'تم إلغاء العملية من قبل المستخدم.';
                    break;
                case 'missing_code':
                    errorMessage += 'رمز التفويض مفقود.';
                    break;
                case 'token_exchange_failed':
                    errorMessage += 'فشل في تبادل الرمز للوصول.';
                    break;
                default:
                    errorMessage += 'حدث خطأ غير معروف.';
            }
            setOauthMessage({
                type: 'error',
                message: errorMessage
            });
        }
        
        // Clear URL parameters after handling
        if (oauthSuccess || oauthError) {
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }, [searchParams]);

    // Auto-hide OAuth messages after 5 seconds
    useEffect(() => {
        if (oauthMessage) {
            const timer = setTimeout(() => {
                setOauthMessage(null);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [oauthMessage]);

    return (
        <div className="min-h-screen bg-axiom-bg text-gray-300 font-sans">
            <Sidebar isOpen={isSidebarOpen} />

            <div className={`transition-all duration-300 ${isSidebarOpen ? 'lg:pl-64' : 'lg:pl-20'}`}>
                <Header toggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />

                {/* OAuth Success/Error Messages */}
                {oauthMessage && (
                    <div className={`mx-4 lg:mx-6 mt-4 p-4 rounded-lg ${
                        oauthMessage.type === 'success' 
                            ? 'bg-green-900/30 border border-green-800 text-green-300' 
                            : 'bg-red-900/30 border border-red-800 text-red-300'
                    }`}>
                        <div className="flex justify-between items-center">
                            <span>{oauthMessage.message}</span>
                            <button 
                                onClick={() => setOauthMessage(null)}
                                className="text-current hover:text-white"
                                aria-label="إغلاق الرسالة"
                            >
                                ✕
                            </button>
                        </div>
                    </div>
                )}

                <main className="p-4 lg:p-6 max-w-[1600px] mx-auto space-y-6">
                    {/* Top Grid: Bot Scores & Price Chart */}
                    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                        <div className="lg:col-span-4 xl:col-span-3">
                            <BotScores />
                        </div>
                        <div className="lg:col-span-8 xl:col-span-9 h-[400px] lg:h-auto">
                            <PriceChart />
                        </div>
                    </div>

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
                </main>
            </div>

            {/* Mobile overlay for sidebar */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
                    onClick={() => setIsSidebarOpen(false)}
                />
            )}
        </div>
    );
}