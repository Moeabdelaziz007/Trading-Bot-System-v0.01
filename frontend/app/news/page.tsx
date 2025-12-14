'use client';

import { motion } from "framer-motion";
import ResourceHints from "@/components/performance/resource-hints";
import NewsClientWrapper from "@/components/news/news-client-wrapper";

const WORKER_API_URL = process.env.NEXT_PUBLIC_WORKER_URL || "https://trading-brain-v1.amrikyy1.workers.dev";

// ==========================================
// 🧠 CLIENT COMPONENT: Intelligence Hub v2.0
// ==========================================

export default function IntelligenceHub() {
    console.log('[PERF] Starting IntelligenceHub client component - no server blocking');

    // Return client wrapper without server-side data fetching
    return (
        <>
            <ResourceHints apiUrl={WORKER_API_URL} />
            <NewsClientWrapper initialNews={[]} initialBriefing={null} />
        </>
    );
}