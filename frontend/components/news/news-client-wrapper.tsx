'use client';

import { useState, useEffect, useMemo, useCallback, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Newspaper, ArrowUpRight, Radio } from "lucide-react";
import dynamic from "next/dynamic";
import { performanceMonitor } from '../../lib/performance-monitor';
import { useBriefing, useNews } from '../../lib/swr-config';
import { NewsGridSkeleton, DataFetchError } from './loading-skeletons';
import DailyBriefingCard from './daily-briefing-card';

// ==========================================
// 🚀 OPTIMIZED DYNAMIC IMPORTS
// ==========================================

// Lazy load non-critical components with optimized loading states
const PulsingOrb = dynamic(() => import("./pulsing-orb"), {
    loading: () => <div className="w-4 h-4 bg-cyan-500/20 rounded-full animate-pulse" />,
    ssr: false
});

const Typewriter = dynamic(() => import("./typewriter"), {
    loading: () => <div className="h-4 w-32 bg-gray-700 rounded animate-pulse" />,
    ssr: false
});

const GlitchText = dynamic(() => import("./glitch-text"), {
    loading: () => <div className="text-cyan-400 h-6">Loading...</div>,
    ssr: false
});

const NeonTag = dynamic(() => import("./neon-tag"), {
    loading: () => <span className="inline-block w-12 h-4 bg-gray-700 rounded animate-pulse"></span>,
    ssr: false
});

const PerformanceDashboard = dynamic(() => import("../performance/performance-dashboard"), {
    ssr: false
});

// ==========================================
// 🎯 TYPE DEFINITIONS
// ==========================================

interface NewsClientWrapperProps {
    initialNews: any[];
    initialBriefing: any;
}

// ==========================================
// 🚀 OPTIMIZED CLIENT WRAPPER WITH SWR
// ==========================================

export default function NewsClientWrapper({ initialNews, initialBriefing }: NewsClientWrapperProps) {
    const [visibleCount, setVisibleCount] = useState(4);
    const [mounted, setMounted] = useState(false);
    const [orbState, setOrbState] = useState<"idle" | "analyzing" | "alert">("idle");

    // Use SWR hooks for data fetching
    const { briefing, isLoading: briefingLoading, isError: briefingError, mutate: mutateBriefing } = useBriefing();
    const { news, isLoading: newsLoading, isError: newsError, mutate: mutateNews } = useNews(8);

    // Track web vitals on mount
    useEffect(() => {
        setMounted(true);
        // Performance monitoring is already initialized automatically in the constructor
        // No need to call trackWebVitals() as it doesn't exist
    }, []);

    // Manual refresh function using SWR mutate
    const fetchData = useCallback(async () => {
        setOrbState("analyzing");
        try {
            await Promise.all([
                mutateBriefing(),
                mutateNews()
            ]);
            setOrbState("idle");
        } catch (e) {
            console.error("Manual refresh failed:", e);
            setOrbState("alert");
        }
    }, [mutateBriefing, mutateNews]);

    const visibleNews = useMemo(() => news.slice(0, visibleCount), [news, visibleCount]);

    return (
        <div className="min-h-screen bg-black text-gray-200 font-mono p-4 md:p-6 lg:p-8">

            {/* Performance Dashboard - Only in development */}
            {process.env.NODE_ENV === 'development' && mounted && (
                <Suspense fallback={null}>
                    <PerformanceDashboard />
                </Suspense>
            )}

            <div className="relative z-10 max-w-7xl mx-auto space-y-6 md:space-y-8">

                {/* ==========================================
                // 🎯 OPTIMIZED HEADER
                // ========================================== */}
                <motion.div
                    className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-cyan-500/20 pb-6"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                >
                    <div className="flex items-center gap-4">
                        <Suspense fallback={<div className="w-8 h-8 bg-gray-800 rounded-full animate-pulse" />}>
                            <PulsingOrb state={orbState} />
                        </Suspense>

                        <div>
                            <Suspense fallback={<div className="h-6 w-32 bg-gray-800 rounded animate-pulse" />}>
                                <GlitchText className="text-xl md:text-2xl text-white">
                                    INTELLIGENCE_HUB
                                </GlitchText>
                            </Suspense>

                            <p className="text-xs text-gray-500 mt-1 flex items-center gap-2">
                                <Radio className="w-3 h-3" style={{ color: "var(--color-primary-cyan)" }} />
                                QUANTUM MARKET ANALYSIS SYSTEM v2.0
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <motion.button
                            onClick={fetchData}
                            className="px-4 py-2 rounded-lg text-xs flex items-center gap-2 transition-all border"
                            style={{
                                backgroundColor: "rgba(0, 240, 255, 0.1)",
                                borderColor: "rgba(0, 240, 255, 0.3)",
                                color: "var(--color-primary-cyan)"
                            }}
                            whileHover={{
                                scale: 1.05,
                                backgroundColor: "rgba(0, 240, 255, 0.2)"
                            }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <RefreshCw className="w-4 h-4" /> SYNC
                        </motion.button>

                        <div className="text-xs text-gray-600 flex items-center gap-2">
                            <div
                                className="w-2 h-2 rounded-full animate-pulse"
                                style={{ backgroundColor: "var(--color-sentiment-bullish)" }}
                            />
                            ONLINE
                        </div>
                    </div>
                </motion.div>

                {/* ==========================================
                // 🎯 OPTIMIZED AI BRIEFING CARD
                // ========================================== */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, ease: "easeOut", delay: 0.1 }}
                >
                    <DailyBriefingCard
                        briefing={briefing}
                        isLoading={briefingLoading}
                        isError={briefingError}
                        onRetry={() => mutateBriefing()}
                    />
                </motion.div>

                {/* ==========================================
                // 🎯 OPTIMIZED NEWS FEED
                // ========================================== */}
                <div>
                    <div className="flex items-center gap-3 mb-6">
                        <Newspaper className="w-5 h-5" style={{ color: "var(--color-primary-cyan)" }} />
                        <h2 className="text-lg font-bold text-white">RAW_DATA_STREAM</h2>
                        <span className="text-xs text-gray-500">({news.length} SIGNALS)</span>
                    </div>

                    {newsError ? (
                        <DataFetchError
                            message="Failed to load news data"
                            onRetry={() => mutateNews()}
                        />
                    ) : newsLoading ? (
                        <NewsGridSkeleton count={4} />
                    ) : (
                        <>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
                                <AnimatePresence mode="popLayout">
                                    {visibleNews.map((item, index) => (
                                        <motion.a
                                            key={item.id}
                                            href={item.link || "#"}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="group block p-4 md:p-6 rounded-xl border transition-all"
                                            style={{
                                                backgroundColor: "rgba(17, 24, 39, 0.3)",
                                                borderColor: "rgba(31, 41, 55, 0.5)"
                                            }}
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: index * 0.05, duration: 0.2 }}
                                            whileHover={{
                                                scale: 1.02,
                                                y: -2,
                                                backgroundColor: "rgba(17, 24, 39, 0.5)"
                                            }}
                                        >
                                            <div className="flex justify-between items-start mb-3">
                                                <span
                                                    className="text-xs font-bold px-2 py-0.5 rounded"
                                                    style={{
                                                        color: "var(--color-primary-cyan)",
                                                        backgroundColor: "rgba(0, 240, 255, 0.1)"
                                                    }}
                                                >
                                                    {item.source}
                                                </span>
                                                <span className="text-xs text-gray-600">
                                                    {new Date(item.published_at).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                                </span>
                                            </div>

                                            <h3 className="text-sm md:text-base font-medium text-gray-300 group-hover:text-white line-clamp-2 transition-colors">
                                                {item.title}
                                            </h3>

                                            <div className="mt-2 flex justify-end">
                                                <ArrowUpRight size={14} className="text-gray-600 group-hover:text-[var(--color-primary-cyan)] transition-colors" />
                                            </div>
                                        </motion.a>
                                    ))}
                                </AnimatePresence>
                            </div>

                            {/* Load More Button */}
                            {news.length > visibleCount && (
                                <motion.div
                                    className="flex justify-center mt-8"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ duration: 0.3, delay: 0.2 }}
                                >
                                    <motion.button
                                        onClick={() => setVisibleCount(prev => Math.min(prev + 4, news.length))} // Load 4 more instead of 6
                                        className="px-6 py-3 rounded-lg text-sm flex items-center gap-2 transition-all border"
                                        style={{
                                            backgroundColor: "rgba(0, 240, 255, 0.1)",
                                            borderColor: "rgba(0, 240, 255, 0.3)",
                                            color: "var(--color-primary-cyan)"
                                        }}
                                        whileHover={{
                                            scale: 1.05,
                                            backgroundColor: "rgba(0, 240, 255, 0.2)"
                                        }}
                                        whileTap={{ scale: 0.95 }}
                                    >
                                        <ArrowUpRight className="w-4 h-4" /> LOAD MORE SIGNALS
                                    </motion.button>
                                </motion.div>
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}