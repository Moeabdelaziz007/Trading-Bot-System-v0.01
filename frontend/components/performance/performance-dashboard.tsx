'use client';

import React, { useState, useEffect } from 'react';
import { usePerformanceMetrics } from '@/lib/performance-monitor';

interface PerformanceDashboardProps {
  isVisible?: boolean;
}

export default function PerformanceDashboard({ isVisible = true }: PerformanceDashboardProps) {
  const { metrics, grade } = usePerformanceMetrics();
  const [expanded, setExpanded] = useState(false);

  // Always show in development mode, respect isVisible prop in production
  if (process.env.NODE_ENV === 'development' ? false : !isVisible) return null;

  const getScoreColor = (value: number, thresholds: { good: number; needsImprovement: number }) => {
    if (value <= thresholds.good) return 'text-green-400';
    if (value <= thresholds.needsImprovement) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-400';
      case 'B': return 'text-green-300';
      case 'C': return 'text-yellow-400';
      case 'D': return 'text-orange-400';
      case 'F': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 font-mono text-xs">
      {/* Collapsed state */}
      <div
        className={`bg-black/80 backdrop-blur-md border border-cyan-500/30 rounded-lg p-3 cursor-pointer transition-all duration-300 ${
          expanded ? 'opacity-0 pointer-events-none' : 'opacity-100'
        }`}
        onClick={() => setExpanded(true)}
      >
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
          <span className="text-cyan-400">Performance</span>
          <span className={`font-bold ${getGradeColor(grade)}`}>{grade}</span>
        </div>
      </div>

      {/* Expanded state */}
      <div
        className={`bg-black/90 backdrop-blur-md border border-cyan-500/30 rounded-lg p-4 min-w-80 transition-all duration-300 ${
          expanded ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-cyan-400 font-bold text-sm">Core Web Vitals</h3>
          <button
            onClick={() => setExpanded(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        <div className="space-y-3">
          {/* Overall Grade */}
          <div className="flex justify-between items-center p-2 bg-cyan-500/10 rounded">
            <span className="text-gray-300">Overall Grade</span>
            <span className={`font-bold text-lg ${getGradeColor(grade)}`}>{grade}</span>
          </div>

          {/* LCP */}
          <div className="flex justify-between items-center p-2 bg-black/30 rounded">
            <span className="text-gray-300">LCP</span>
            <div className="text-right">
              <span className={getScoreColor(metrics.lcp || 0, { good: 2500, needsImprovement: 4000 })}>
                {metrics.lcp ? `${(metrics.lcp / 1000).toFixed(2)}s` : 'Loading...'}
              </span>
              <div className="text-gray-500 text-xs">
                {metrics.lcp && metrics.lcp <= 2500 ? 'Good' : 
                 metrics.lcp && metrics.lcp <= 4000 ? 'Needs Improvement' : 'Poor'}
              </div>
            </div>
          </div>

          {/* FID */}
          <div className="flex justify-between items-center p-2 bg-black/30 rounded">
            <span className="text-gray-300">FID</span>
            <div className="text-right">
              <span className={getScoreColor(metrics.fid || 0, { good: 100, needsImprovement: 300 })}>
                {metrics.fid ? `${metrics.fid.toFixed(0)}ms` : 'Loading...'}
              </span>
              <div className="text-gray-500 text-xs">
                {metrics.fid && metrics.fid <= 100 ? 'Good' : 
                 metrics.fid && metrics.fid <= 300 ? 'Needs Improvement' : 'Poor'}
              </div>
            </div>
          </div>

          {/* CLS */}
          <div className="flex justify-between items-center p-2 bg-black/30 rounded">
            <span className="text-gray-300">CLS</span>
            <div className="text-right">
              <span className={getScoreColor(metrics.cls || 0, { good: 0.1, needsImprovement: 0.25 })}>
                {metrics.cls ? metrics.cls.toFixed(3) : 'Loading...'}
              </span>
              <div className="text-gray-500 text-xs">
                {metrics.cls && metrics.cls <= 0.1 ? 'Good' : 
                 metrics.cls && metrics.cls <= 0.25 ? 'Needs Improvement' : 'Poor'}
              </div>
            </div>
          </div>

          {/* FCP */}
          <div className="flex justify-between items-center p-2 bg-black/30 rounded">
            <span className="text-gray-300">FCP</span>
            <div className="text-right">
              <span className={getScoreColor(metrics.fcp || 0, { good: 1800, needsImprovement: 3000 })}>
                {metrics.fcp ? `${(metrics.fcp / 1000).toFixed(2)}s` : 'Loading...'}
              </span>
              <div className="text-gray-500 text-xs">
                {metrics.fcp && metrics.fcp <= 1800 ? 'Good' : 
                 metrics.fcp && metrics.fcp <= 3000 ? 'Needs Improvement' : 'Poor'}
              </div>
            </div>
          </div>

          {/* TTFB */}
          <div className="flex justify-between items-center p-2 bg-black/30 rounded">
            <span className="text-gray-300">TTFB</span>
            <div className="text-right">
              <span className={getScoreColor(metrics.ttfb || 0, { good: 800, needsImprovement: 1800 })}>
                {metrics.ttfb ? `${metrics.ttfb.toFixed(0)}ms` : 'Loading...'}
              </span>
              <div className="text-gray-500 text-xs">
                {metrics.ttfb && metrics.ttfb <= 800 ? 'Good' : 
                 metrics.ttfb && metrics.ttfb <= 1800 ? 'Needs Improvement' : 'Poor'}
              </div>
            </div>
          </div>
        </div>

        {/* Performance Tips */}
        <div className="mt-4 pt-3 border-t border-gray-700">
          <h4 className="text-cyan-300 text-xs font-bold mb-2">Optimization Tips</h4>
          <div className="space-y-1 text-xs text-gray-400">
            {metrics.lcp && metrics.lcp > 2500 && (
              <div>• Optimize largest content element</div>
            )}
            {metrics.fid && metrics.fid > 100 && (
              <div>• Reduce JavaScript execution time</div>
            )}
            {metrics.cls && metrics.cls > 0.1 && (
              <div>• Ensure proper image dimensions</div>
            )}
            {metrics.ttfb && metrics.ttfb > 800 && (
              <div>• Improve server response time</div>
            )}
          </div>
        </div>

        {/* Refresh Button */}
        <button
          onClick={() => window.location.reload()}
          className="mt-3 w-full bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 py-2 px-3 rounded text-xs transition-colors"
        >
          Refresh Metrics
        </button>
      </div>
    </div>
  );
}