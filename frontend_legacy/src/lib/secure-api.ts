/**
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 🔐 SECURE API CLIENT | عميل API الآمن
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 
 * Purpose: Secure communication between Frontend and Cloudflare Worker Backend
 * Features:
 *   - X-System-Key authentication for protected endpoints
 *   - Automatic retry with exponential backoff
 *   - Request/Response validation with Zod
 *   - Error handling with user-friendly messages
 * 
 * Author: Axiom AI Partner | Mohamed Hossameldin Abdelaziz
 * Date: December 9, 2025
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

import { z } from 'zod';

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Configuration | الإعدادات
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy.workers.dev';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // ms

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Zod Schemas for Validation | مخططات التحقق
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export const HealthResponseSchema = z.object({
    status: z.string(),
    mode: z.string().optional(),
    drift_guard: z.string().optional(),
    timestamp: z.string().optional(),
});

export const MetricsResponseSchema = z.object({
    agents: z.record(z.object({
        wins: z.number(),
        losses: z.number(),
        avg_pnl: z.number(),
        weight: z.number(),
    })).optional(),
    total_trades: z.number().optional(),
    win_rate: z.number().optional(),
    total_pnl: z.number().optional(),
});

export const WealthResponseSchema = z.object({
    total_equity: z.number(),
    available_cash: z.number(),
    profit_today: z.number(),
    profit_airlock: z.number().optional(),
    positions: z.array(z.object({
        symbol: z.string(),
        qty: z.number(),
        market_value: z.number(),
        unrealized_pl: z.number(),
    })).optional(),
});

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Types | الأنواع
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type MetricsResponse = z.infer<typeof MetricsResponseSchema>;
export type WealthResponse = z.infer<typeof WealthResponseSchema>;

interface ApiError {
    message: string;
    code?: string;
    status?: number;
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// Secure Fetch with Retry | الجلب الآمن مع إعادة المحاولة
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async function secureFetch<T>(
    endpoint: string,
    options: RequestInit = {},
    schema?: z.ZodSchema<T>,
    requiresAuth = false
): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    
    const headers: HeadersInit = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
    };
    
    // Add authentication header for protected endpoints
    if (requiresAuth) {
        const systemKey = process.env.NEXT_PUBLIC_SYSTEM_KEY;
        if (systemKey) {
            (headers as Record<string, string>)['X-System-Key'] = systemKey;
        }
    }
    
    let lastError: Error | null = null;
    
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });
            
            // Handle non-OK responses
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || `HTTP ${response.status}: ${response.statusText}`
                );
            }
            
            const data = await response.json();
            
            // Validate response with Zod schema if provided
            if (schema) {
                const parsed = schema.safeParse(data);
                if (!parsed.success) {
                    console.warn('Response validation warning:', parsed.error.issues);
                    // Return data anyway, just log the warning
                }
            }
            
            return data as T;
            
        } catch (error) {
            lastError = error as Error;
            
            // Don't retry on 4xx errors (client errors)
            if (error instanceof Error && error.message.includes('HTTP 4')) {
                throw error;
            }
            
            // Wait before retrying with exponential backoff
            if (attempt < MAX_RETRIES - 1) {
                await new Promise(resolve => 
                    setTimeout(resolve, RETRY_DELAY * Math.pow(2, attempt))
                );
            }
        }
    }
    
    throw lastError || new Error('Request failed after max retries');
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// API Methods | طرق API
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

export const secureApi = {
    /**
     * Check system health (public endpoint)
     * فحص صحة النظام (نقطة نهاية عامة)
     */
    async getHealth(): Promise<HealthResponse> {
        return secureFetch('/health', {}, HealthResponseSchema, false);
    },
    
    /**
     * Get learning loop metrics (protected)
     * الحصول على مقاييس حلقة التعلم (محمية)
     */
    async getMetrics(): Promise<MetricsResponse> {
        return secureFetch('/loop/metrics', {}, MetricsResponseSchema, true);
    },
    
    /**
     * Get wealth/portfolio summary (protected)
     * الحصول على ملخص الثروة/المحفظة (محمي)
     */
    async getWealth(): Promise<WealthResponse> {
        return secureFetch('/finance/summary', {}, WealthResponseSchema, true);
    },
    
    /**
     * Get drift guard status (protected)
     * الحصول على حالة حارس الانحراف (محمي)
     */
    async getDriftStatus(): Promise<{ status: string; drift_detected: boolean }> {
        return secureFetch('/drift/status', {}, undefined, true);
    },
    
    /**
     * Get swarm agent performance (protected)
     * الحصول على أداء وكلاء السرب (محمي)
     */
    async getSwarmPerformance(): Promise<{
        agents: Record<string, { weight: number; performance: number }>;
        mode: string;
    }> {
        return secureFetch('/swarm/performance', {}, undefined, true);
    },
    
    /**
     * Execute a trade signal (protected - requires TRADING_MODE != SIMULATION)
     * تنفيذ إشارة تداول (محمي - يتطلب وضع غير المحاكاة)
     */
    async executeTrade(params: {
        symbol: string;
        side: 'BUY' | 'SELL';
        amount: number;
        stopLoss?: number;
        takeProfit?: number;
    }): Promise<{ success: boolean; orderId?: string; error?: string }> {
        return secureFetch('/trade/execute', {
            method: 'POST',
            body: JSON.stringify(params),
        }, undefined, true);
    },
    
    /**
     * Trigger panic mode - close all positions (protected)
     * تفعيل وضع الذعر - إغلاق جميع المراكز (محمي)
     */
    async triggerPanic(): Promise<{ success: boolean; message: string }> {
        return secureFetch('/panic', {
            method: 'POST',
        }, undefined, true);
    },
};

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// React Hook for API calls | خطاف React لاستدعاءات API
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import { useState, useEffect, useCallback } from 'react';

interface UseApiResult<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => void;
}

export function useSecureApi<T>(
    apiMethod: () => Promise<T>,
    dependencies: unknown[] = []
): UseApiResult<T> {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        
        try {
            const result = await apiMethod();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    }, [apiMethod]);
    
    useEffect(() => {
        fetchData();
    }, [...dependencies, fetchData]);
    
    return { data, loading, error, refetch: fetchData };
}

export default secureApi;
