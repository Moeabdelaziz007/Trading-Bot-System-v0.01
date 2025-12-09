/**
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 🔌 MIDDLEWARE TYPES | أنواع البرمجيات الوسيطة
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * 
 * Shared types for middleware pipeline and API integration
 * Author: Axiom AI Partner | December 9, 2025
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 */

import { z } from 'zod';

/**
 * Middleware context passed through the pipeline
 * يتم تمرير السياق عبر خط أنابيب البرمجيات الوسيطة
 */
export interface ApiContext {
  request: {
    url: string;
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';
    headers: Record<string, string>;
    body?: unknown;
    timestamp: number;
  };
  response: {
    status?: number;
    headers?: Record<string, string>;
    body?: unknown;
  };
  metadata: {
    requestId: string;
    retryCount: number;
    startTime: number;
    endTime?: number;
  };
}

/**
 * Middleware plugin interface
 * واجهة البرمجية الوسيطة
 */
export interface Middleware {
  name: string;
  priority: number; // 0-100, higher = earlier execution
  execute: (context: ApiContext) => Promise<ApiContext | null>;
  onError?: (error: Error, context: ApiContext) => Promise<ApiContext>;
}

/**
 * API Error with structured format
 * خطأ API بصيغة منظمة
 */
export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
    timestamp: string;
    requestId: string;
  };
}

/**
 * Retry configuration
 * إعدادات إعادة المحاولة
 */
export interface RetryConfig {
  maxAttempts: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  jitterFactor: number; // 0-1
}

/**
 * Circuit breaker state
 * حالة قاطع الدارة
 */
export type CircuitBreakerState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

/**
 * Circuit breaker metrics
 * مقاييس قاطع الدارة
 */
export interface CircuitBreakerMetrics {
  state: CircuitBreakerState;
  failureCount: number;
  successCount: number;
  lastFailure?: Error;
  lastFailureTime?: number;
  nextRetryTime?: number;
}

/**
 * Logger interface
 * واجهة المسجل
 */
export interface Logger {
  debug: (message: string, context?: Record<string, unknown>) => void;
  info: (message: string, context?: Record<string, unknown>) => void;
  warn: (message: string, context?: Record<string, unknown>) => void;
  error: (message: string, error?: Error, context?: Record<string, unknown>) => void;
}

/**
 * API Configuration
 * إعدادات API
 */
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryConfig: RetryConfig;
  circuitBreaker: {
    enabled: boolean;
    failureThreshold: number;
    successThreshold: number;
    resetTimeoutMs: number;
  };
  logger: Logger;
  enableLogging: boolean;
}

/**
 * Validation schema for API responses
 * مخطط التحقق من استجابات API
 */
export const ApiErrorSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.unknown()).optional(),
    timestamp: z.string(),
    requestId: z.string(),
  }),
});

/**
 * HTTP status codes with semantic meaning
 */
export const HTTP_STATUS = {
  OK: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  UNPROCESSABLE_ENTITY: 422,
  TOO_MANY_REQUESTS: 429,
  INTERNAL_SERVER_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
  GATEWAY_TIMEOUT: 504,
} as const;

/**
 * Error codes for consistent error handling
 */
export const ERROR_CODES = {
  // Client errors
  INVALID_REQUEST: 'INVALID_REQUEST',
  UNAUTHORIZED: 'UNAUTHORIZED',
  FORBIDDEN: 'FORBIDDEN',
  NOT_FOUND: 'NOT_FOUND',
  CONFLICT: 'CONFLICT',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  
  // Server errors
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  SERVICE_UNAVAILABLE: 'SERVICE_UNAVAILABLE',
  GATEWAY_TIMEOUT: 'GATEWAY_TIMEOUT',
  
  // Network errors
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT: 'TIMEOUT',
  CIRCUIT_BREAKER_OPEN: 'CIRCUIT_BREAKER_OPEN',
  
  // Unknown
  UNKNOWN_ERROR: 'UNKNOWN_ERROR',
} as const;
