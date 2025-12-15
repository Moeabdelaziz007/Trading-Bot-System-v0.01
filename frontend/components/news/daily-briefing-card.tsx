"use client";

import { motion } from "framer-motion";
import { Zap, TrendingUp, TrendingDown, Minus, Globe } from "lucide-react";
import { Suspense, useMemo } from "react";
import { GlassCard } from "@/components/glass-card";
import dynamic from "next/dynamic";
import { BriefingSkeleton, DataFetchError } from "./loading-skeletons";
import { Briefing } from "@/lib/swr-config";

// Dynamic imports for performance
const Typewriter = dynamic(() => import("./typewriter"), {
    loading: () => <div className="h-4 w-32 bg-gray-700 rounded animate-pulse" />,
    ssr: false
});

const NeonTag = dynamic(() => import("./neon-tag"), {
    loading: () => <span className="inline-block w-12 h-4 bg-gray-700 rounded animate-pulse"></span>,
    ssr: false
});

interface DailyBriefingCardProps {
    briefing: Briefing | undefined;
    isLoading: boolean;
    isError: any;
    onRetry: () => void;
}

export default function DailyBriefingCard({ briefing, isLoading, isError, onRetry }: DailyBriefingCardProps) {

    // Memoized sentiment style
    const sentimentStyle = useMemo(() => {
        const sentiment = briefing?.sentiment || "Neutral";
        switch (sentiment) {
            case "Bullish": return { icon: <TrendingUp className="w-5 h-5" style={{ color: "var(--color-sentiment-bullish)" }} />, color: "var(--color-sentiment-bullish)" };
            case "Bearish": return { icon: <TrendingDown className="w-5 h-5" style={{ color: "var(--color-sentiment-bearish)" }} />, color: "var(--color-sentiment-bearish)" };
            default: return { icon: <Minus className="w-5 h-5" style={{ color: "var(--color-sentiment-neutral)" }} />, color: "var(--color-sentiment-neutral)" };
        }
    }, [briefing]);

    if (isError) {
        return (
            <DataFetchError
                message="Failed to load briefing data"
                onRetry={onRetry}
            />
        );
    }

    if (isLoading) {
        return <BriefingSkeleton />;
    }

    return (
        <GlassCard
            sentiment={
                briefing?.sentiment === "Bullish" ? "bullish" :
                    briefing?.sentiment === "Bearish" ? "bearish" :
                        "neutral"
            }
            className="relative p-6"
        >
            <div className="relative z-10">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <Zap className="w-5 h-5" style={{ color: "#facc15" }} />
                        <span className="text-xs text-gray-400 uppercase tracking-widest">Daily Executive Briefing</span>
                    </div>
                    {briefing && (
                        <motion.div
                            className="flex items-center gap-2 px-3 py-1 rounded-full shadow-lg border"
                            style={{
                                boxShadow: briefing.sentiment === "Bullish" ? "var(--glow-bullish)" :
                                    briefing.sentiment === "Bearish" ? "var(--glow-bearish)" :
                                        "var(--glow-neutral)"
                            }}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ type: "spring", stiffness: 200, damping: 15 }}
                        >
                            {sentimentStyle.icon}
                            <span
                                className="text-lg font-bold"
                                style={{ color: sentimentStyle.color }}
                            >
                                {briefing.sentiment.toUpperCase()}
                            </span>
                        </motion.div>
                    )}
                </div>

                {/* AI Summary with Optimized Typewriter */}
                <div className="min-h-[80px] text-lg md:text-xl leading-relaxed text-gray-300">
                    {briefing ? (
                        <Suspense fallback={<div className="h-4 w-32 bg-gray-800 rounded animate-pulse" />}>
                            <Typewriter text={briefing.summary} speed={30} />
                        </Suspense>
                    ) : (
                        <div className="text-gray-500 text-center py-4">
                            <Globe className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>Waiting AI Analysis...</p>
                            <p className="text-xs mt-1">Daily briefing generates at 08:00 Cairo Time</p>
                        </div>
                    )}
                </div>

                {/* Impact Tags */}
                <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/10">
                    <span className="text-xs text-gray-500 mr-2">MARKET DRIVERS:</span>
                    {['FED_RATES', 'BTC_HALVING', 'CHINA_STIMULUS', 'AI_SECTOR'].map((driver, i) => (
                        <Suspense key={i} fallback={<div className="px-2 py-1 bg-gray-800 rounded text-xs">Loading...</div>}>
                            <NeonTag type={i % 2 === 0 ? "positive" : i % 2 === 1 ? "critical" : "positive" as const}>
                                {driver.replace('_', ' ')}
                            </NeonTag>
                        </Suspense>
                    ))}
                </div>

                {briefing && (
                    <div className="mt-4 text-xs text-gray-600 flex items-center gap-2">
                        <span
                            className="w-1 h-1 rounded-full"
                            style={{ backgroundColor: "var(--color-primary-cyan)" }}
                        />
                        Generated by Perplexity Sonar • {new Date(briefing.created_at).toLocaleString()}
                    </div>
                )}
            </div>
        </GlassCard>
    );
}
