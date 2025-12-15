import useSWR, { type SWRConfiguration } from 'swr';

// Mock data for development to avoid CORS issues
const mockBriefingData = {
    summary: "Global markets show mixed signals today with technology stocks leading gains while energy sector faces headwinds.",
    sentiment: "Neutral" as const,
    created_at: new Date().toISOString(),
};

const mockNewsData = {
    news: [
        {
            id: 1,
            source: "Financial Times",
            title: "Fed Signals Potential Rate Pause",
            link: "#",
            published_at: new Date().toISOString(),
        },
        {
            id: 2,
            source: "Tech News",
            title: "Tech Stocks Rally on AI Optimism",
            link: "#",
            published_at: new Date(Date.now() - 3600000).toISOString(),
        },
        {
            id: 3,
            source: "Energy Daily",
            title: "Oil Prices Stabilize Amid Supply Concerns",
            link: "#",
            published_at: new Date(Date.now() - 7200000).toISOString(),
        },
        {
            id: 4,
            source: "Crypto Watch",
            title: "Cryptocurrency Market Shows Recovery Signs",
            link: "#",
            published_at: new Date(Date.now() - 10800000).toISOString(),
        },
    ],
};

// Enhanced fetcher function for SWR with CORS handling
export const fetcher = async (url: string) => {
    try {
        // For development, use mock data to avoid CORS issues
        // For development, use mock data to avoid CORS issues
        // if (process.env.NODE_ENV === 'development') {
        //     if (url.includes('/api/briefing/latest')) {
        //         return mockBriefingData;
        //     }
        //     if (url.includes('/api/news/latest')) {
        //         return mockNewsData;
        //     }
        // }

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                // Remove Cache-Control header that's causing CORS issues
            },
        });

        if (!response.ok) {
            const error = new Error(`HTTP error! status: ${response.status}`);
            (error as any).info = await response.json();
            (error as any).status = response.status;
            throw error;
        }

        return response.json();
    } catch (error) {
        console.error('API fetch error:', error);
        // Return mock data on error for development
        // Return mock data on error for development
        // if (process.env.NODE_ENV === 'development') {
        //     if (url.includes('/api/briefing/latest')) {
        //         return mockBriefingData;
        //     }
        //     if (url.includes('/api/news/latest')) {
        //         return mockNewsData;
        //     }
        // }
        throw error;
    }
};

// SWR configuration optimized for performance
export const swrConfig: SWRConfiguration = {
    revalidateOnFocus: false,
    revalidateOnReconnect: true,
    dedupingInterval: 30000, // 30 seconds to reduce API calls
    errorRetryCount: 2, // Reduced retry attempts
    errorRetryInterval: 3000, // Faster retry
    loadingTimeout: 5000, // Shorter timeout for better UX
    onError: (error: any, key: string) => {
        console.error(`SWR Error for ${key}:`, error);
    },
};

// Custom hook for fetching briefing data
export function useBriefing() {
    const WORKER_API_URL = process.env.NEXT_PUBLIC_WORKER_URL || "https://trading-brain-v1.amrikyy1.workers.dev";
    const { data, error, isLoading, mutate } = useSWR<Briefing>(
        `${WORKER_API_URL}/api/briefing/latest`,
        fetcher,
        {
            ...swrConfig,
            refreshInterval: 300000, // 5 minutes instead of 10 minutes
        }
    );

    return {
        briefing: data,
        isLoading,
        isError: error,
        mutate,
    };
}

// Custom hook for fetching news data
export function useNews(limit: number = 8) {
    const WORKER_API_URL = process.env.NEXT_PUBLIC_WORKER_URL || "https://trading-brain-v1.amrikyy1.workers.dev";
    const { data, error, isLoading, mutate } = useSWR<NewsResponse>(
        `${WORKER_API_URL}/api/news/latest?limit=${limit}`,
        fetcher,
        {
            ...swrConfig,
            refreshInterval: 300000, // 5 minutes instead of 3 minutes
        }
    );

    return {
        news: data?.news || [],
        isLoading,
        isError: error,
        mutate,
    };
}

// Type definitions
export interface Briefing {
    summary: string;
    sentiment: "Bullish" | "Bearish" | "Neutral";
    created_at: string;
}

export interface NewsItem {
    id: number;
    source: string;
    title: string;
    link?: string;
    published_at: string;
}

export interface NewsResponse {
    news: NewsItem[];
}