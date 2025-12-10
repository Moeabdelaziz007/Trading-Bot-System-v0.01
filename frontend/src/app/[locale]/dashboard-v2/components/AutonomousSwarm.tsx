'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Shield, Zap, Newspaper, Brain, TrendingUp } from 'lucide-react';

interface CronJob {
  agent: string;
  icon: any;
  interval: string;
  watchlist: string;
  model: string;
  color: string;
  nextRun: string;
}

const cronJobs: CronJob[] = [
  {
    agent: 'RiskGuardian',
    icon: Shield,
    interval: '1 min',
    watchlist: 'All',
    model: 'Workers AI',
    color: 'text-axiom-neon-red',
    nextRun: '00:32'
  },
  {
    agent: 'Scalper',
    icon: Zap,
    interval: '5 min',
    watchlist: 'EURUSD, GBPUSD, XAUUSD, BTC',
    model: 'TradingBrain',
    color: 'text-yellow-400',
    nextRun: '00:35'
  },
  {
    agent: 'Journalist',
    icon: Newspaper,
    interval: '15 min',
    watchlist: 'Market News',
    model: 'DuckDuckGo/Perplexity',
    color: 'text-axiom-neon-blue',
    nextRun: '00:45'
  },
  {
    agent: 'Strategist',
    icon: Brain,
    interval: '1 hour',
    watchlist: 'Portfolio',
    model: 'GLM-4.5',
    color: 'text-axiom-neon-purple',
    nextRun: '01:00'
  },
  {
    agent: 'Swing',
    icon: TrendingUp,
    interval: '4 hours',
    watchlist: 'Major Pairs',
    model: 'Gemini 2.0',
    color: 'text-axiom-neon-green',
    nextRun: '04:00'
  }
];

export const AutonomousSwarm: React.FC = () => {
  return (
    <div className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Clock className="w-6 h-6 text-axiom-neon-gold" />
          <h2 className="text-xl font-mono font-bold text-white tracking-tight">
            AUTONOMOUS_SWARM_SYSTEM
          </h2>
        </div>
        <div className="px-3 py-1 bg-axiom-neon-green/10 border border-axiom-neon-green/30 rounded-lg">
          <span className="text-xs font-mono text-axiom-neon-green font-bold">
            24/7 OPERATIONS
          </span>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        {cronJobs.map((job, index) => (
          <motion.div
            key={job.agent}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="relative group"
          >
            {/* Timeline Line */}
            {index < cronJobs.length - 1 && (
              <div className="absolute left-6 top-12 w-px h-full bg-gradient-to-b from-glass-border to-transparent"></div>
            )}

            <div className="flex items-start gap-4 bg-axiom-bg/50 border border-glass-border rounded-lg p-4 hover:border-glass-border/50 hover:bg-axiom-bg/70 transition-all">
              {/* Icon Circle */}
              <div className={`flex-shrink-0 w-12 h-12 rounded-full bg-axiom-surface border-2 ${job.color.replace('text-', 'border-')} flex items-center justify-center relative z-10`}>
                <job.icon className={`w-6 h-6 ${job.color}`} />
              </div>

              {/* Job Details */}
              <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs text-text-muted font-mono mb-1">AGENT</p>
                  <p className={`text-sm font-mono font-bold ${job.color}`}>
                    {job.agent}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-text-muted font-mono mb-1">INTERVAL</p>
                  <p className="text-sm font-mono text-white">
                    {job.interval}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-text-muted font-mono mb-1">WATCHLIST</p>
                  <p className="text-sm font-mono text-white truncate">
                    {job.watchlist}
                  </p>
                </div>

                <div>
                  <p className="text-xs text-text-muted font-mono mb-1">NEXT_RUN</p>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-axiom-neon-green animate-pulse"></div>
                    <p className="text-sm font-mono text-axiom-neon-green font-bold">
                      {job.nextRun}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer Stats */}
      <div className="mt-6 grid grid-cols-3 gap-4 pt-4 border-t border-glass-border">
        <div className="text-center">
          <p className="text-2xl font-mono font-bold text-white">{cronJobs.length}</p>
          <p className="text-xs text-text-muted font-mono">ACTIVE_AGENTS</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-mono font-bold text-axiom-neon-green">100%</p>
          <p className="text-xs text-text-muted font-mono">UPTIME</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-mono font-bold text-axiom-neon-cyan">1,284</p>
          <p className="text-xs text-text-muted font-mono">EXECUTIONS_TODAY</p>
        </div>
      </div>
    </div>
  );
};