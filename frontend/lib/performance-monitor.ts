import React from 'react';
import { onCLS, onINP, onFCP, onLCP, onTTFB } from 'web-vitals';

interface PerformanceMetrics {
  cls: number;
  fid: number;
  fcp: number;
  lcp: number;
  ttfb: number;
}

class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private callbacks: ((metrics: PerformanceMetrics) => void)[] = [];

  constructor() {
    // Only initialize on client side
    if (typeof window !== 'undefined') {
      this.initializeMetrics();
    }
  }

  private initializeMetrics() {
    // Measure Core Web Vitals (only available in browser)
    if (typeof window === 'undefined') return;

    onCLS((metric) => {
      this.metrics.cls = metric.value;
      this.notifyCallbacks();
    });

    onINP((metric) => {
      this.metrics.fid = metric.value; // Using INP as replacement for FID
      this.notifyCallbacks();
    });

    onFCP((metric) => {
      this.metrics.fcp = metric.value;
      this.notifyCallbacks();
    });

    onLCP((metric) => {
      this.metrics.lcp = metric.value;
      this.notifyCallbacks();
    });

    onTTFB((metric) => {
      this.metrics.ttfb = metric.value;
      this.notifyCallbacks();
    });
  }

  private notifyCallbacks() {
    if (this.isComplete()) {
      const completeMetrics = this.metrics as PerformanceMetrics;
      this.callbacks.forEach(callback => callback(completeMetrics));
      
      // Log to console in development
      if (process.env.NODE_ENV === 'development') {
        console.log('Core Web Vitals:', completeMetrics);
      }

      // Send to analytics in production
      if (process.env.NODE_ENV === 'production') {
        this.sendToAnalytics(completeMetrics);
      }
    }
  }

  private isComplete(): boolean {
    return !!(
      this.metrics.cls !== undefined &&
      this.metrics.fid !== undefined &&
      this.metrics.fcp !== undefined &&
      this.metrics.lcp !== undefined &&
      this.metrics.ttfb !== undefined
    );
  }

  private sendToAnalytics(metrics: PerformanceMetrics) {
    // Send to your analytics service
    if (typeof window !== 'undefined' && 'gtag' in window) {
      (window as any).gtag('event', 'core_web_vitals', {
        event_category: 'Performance',
        event_label: 'Core Web Vitals',
        value: JSON.stringify(metrics),
        non_interaction: true,
      });
    }
  }

  public onMetricsCollected(callback: (metrics: PerformanceMetrics) => void) {
    this.callbacks.push(callback);
  }

  public getMetrics(): Partial<PerformanceMetrics> {
    return { ...this.metrics };
  }

  public getPerformanceGrade(): string {
    if (!this.isComplete()) return 'Loading...';

    const { cls, fid, lcp, ttfb } = this.metrics as PerformanceMetrics;
    
    // Scoring based on Web Vitals thresholds
    let score = 0;
    let total = 0;

    // CLS scoring (0-0.1 is good, 0.1-0.25 needs improvement, >0.25 is poor)
    if (cls <= 0.1) score += 1;
    else if (cls <= 0.25) score += 0.5;
    total += 1;

    // FID scoring (<100ms is good, 100-300ms needs improvement, >300ms is poor)
    if (fid <= 100) score += 1;
    else if (fid <= 300) score += 0.5;
    total += 1;

    // LCP scoring (<2.5s is good, 2.5-4s needs improvement, >4s is poor)
    if (lcp <= 2500) score += 1;
    else if (lcp <= 4000) score += 0.5;
    total += 1;

    // TTFB scoring (<800ms is good, 800-1800ms needs improvement, >1800ms is poor)
    if (ttfb <= 800) score += 1;
    else if (ttfb <= 1800) score += 0.5;
    total += 1;

    const percentage = (score / total) * 100;
    
    if (percentage >= 90) return 'A';
    if (percentage >= 80) return 'B';
    if (percentage >= 70) return 'C';
    if (percentage >= 60) return 'D';
    return 'F';
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// React hook for using performance monitor
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = React.useState<Partial<PerformanceMetrics>>({});
  const [grade, setGrade] = React.useState<string>('Loading...');

  React.useEffect(() => {
    performanceMonitor.onMetricsCollected((newMetrics) => {
      setMetrics(newMetrics);
      setGrade(performanceMonitor.getPerformanceGrade());
    });

    // Set current metrics if already available
    setMetrics(performanceMonitor.getMetrics());
    setGrade(performanceMonitor.getPerformanceGrade());
  }, []);

  return { metrics, grade };
}

// Utility to measure custom performance marks
export function measurePerformance(name: string, fn: () => void | Promise<void>) {
  if (typeof window === 'undefined') return fn;

  const startMark = `${name}-start`;
  const endMark = `${name}-end`;
  const measureName = `${name}-measure`;

  performance.mark(startMark);

  const result = fn();

  if (result instanceof Promise) {
    return result.finally(() => {
      performance.mark(endMark);
      performance.measure(measureName, startMark, endMark);
      
      const measure = performance.getEntriesByName(measureName, 'measure')[0];
      if (process.env.NODE_ENV === 'development') {
        console.log(`${name} took ${measure.duration}ms`);
      }
    });
  } else {
    performance.mark(endMark);
    performance.measure(measureName, startMark, endMark);
    
    const measure = performance.getEntriesByName(measureName, 'measure')[0];
    if (process.env.NODE_ENV === 'development') {
      console.log(`${name} took ${measure.duration}ms`);
    }
    
    return result;
  }
}