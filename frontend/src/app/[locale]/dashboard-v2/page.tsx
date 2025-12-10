'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Bell, Menu, Crown, Brain, TrendingUp } from 'lucide-react';
import { SpiderBrainStatus } from './components/SpiderBrainStatus';
import { TwinTurboGauges } from './components/TwinTurboGauges';
import { AutonomousSwarm } from './components/AutonomousSwarm';
import { ExecutionDeck } from './components/ExecutionDeck';
import { PaymentModal } from './components/PaymentModal';
import { usePortfolio } from './hooks/usePortfolio';

// Import existing dialectic components
import { DialecticWarRoom } from '@/components/dialectic/DialecticWarRoom';
import { EvolutionaryOptimization } from '@/components/dialectic/EvolutionaryOptimization';
import { ResilienceMonitor } from '@/components/dialectic/ResilienceMonitor';
import { StrategyEngine } from '@/components/dialectic/StrategyEngine';

export default function DashboardV2Page() {
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const { portfolio, loading } = usePortfolio();

  return (
    <div className="min-h-screen bg-axiom-bg">
      {/* Top Navigation */}
      <nav className="sticky top-0 z-40 bg-axiom-surface/80 backdrop-blur-glass border-b border-glass-border">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Brain className="w-8 h-8 text-axiom-neon-cyan" />
                <div>
                  <h1 className="text-xl font-mono font-bold text-white tracking-tight">
                    AXIOM ANTIGRAVITY
                  </h1>
                  <p className="text-xs text-text-muted font-mono">
                    v1.0 Citadel Edition
                  </p>
                </div>
              </div>
            </div>

            {/* Center - Status */}
            <div className="hidden lg:flex items-center gap-2 px-4 py-2 bg-axiom-neon-green/10 border border-axiom-neon-green/30 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-axiom-neon-green animate-pulse"></div>
              <span className="text-sm font-mono text-axiom-neon-green font-bold">
                MAINNET: 7/7 Agents Online
              </span>
            </div>

            {/* Right - Actions */}
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-axiom-surface rounded-lg transition-colors">
                <Search className="w-5 h-5 text-text-muted" />
              </button>
              <button className="p-2 hover:bg-axiom-surface rounded-lg transition-colors relative">
                <Bell className="w-5 h-5 text-text-muted" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-axiom-neon-red rounded-full"></span>
              </button>
              <button
                onClick={() => setShowPaymentModal(true)}
                className="flex items-center gap-2 px-4 py-2 bg-axiom-neon-gold/10 border border-axiom-neon-gold/30 rounded-lg hover:bg-axiom-neon-gold/20 transition-all"
              >
                <Crown className="w-4 h-4 text-axiom-neon-gold" />
                <span className="text-sm font-mono text-axiom-neon-gold font-bold">
                  UPGRADE
                </span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-[1920px] mx-auto px-6 py-6 space-y-6">
        {/* Spider Web Brain Status */}
        <SpiderBrainStatus />

        {/* Top Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Bot Scores */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6"
          >
            <h3 className="text-sm font-mono text-text-muted mb-4">BOT_SCORES</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono text-text-muted">PnL Today</span>
                <span className={`text-lg font-mono font-bold ${portfolio.todayPnL >= 0 ? 'text-axiom-neon-green' : 'text-axiom-neon-red'}`}>
                  {portfolio.todayPnL >= 0 ? '+' : ''}{portfolio.todayPnL.toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono text-text-muted">Win Rate</span>
                <span className="text-lg font-mono font-bold text-axiom-neon-cyan">
                  {portfolio.winRate}%
                </span>
              </div>
            </div>
          </motion.div>

          {/* Main Chart Placeholder */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 flex items-center justify-center"
          >
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-axiom-neon-cyan mx-auto mb-2" />
              <p className="text-sm font-mono text-text-muted">
                MAIN_CHART
              </p>
              <p className="text-xs font-mono text-text-dim mt-1">
                TradingView Integration
              </p>
            </div>
          </motion.div>

          {/* Portfolio */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6"
          >
            <h3 className="text-sm font-mono text-text-muted mb-4">PORTFOLIO</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono text-text-muted">Balance</span>
                <span className="text-lg font-mono font-bold text-white">
                  ${portfolio.balance.toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-mono text-text-muted">Positions</span>
                <span className="text-lg font-mono font-bold text-axiom-neon-cyan">
                  {portfolio.positions.length}
                </span>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Self-Play Learning Loop */}
        <div className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6">
          <div className="flex items-center gap-3 mb-6">
            <Brain className="w-6 h-6 text-axiom-neon-purple" />
            <h2 className="text-xl font-mono font-bold text-white tracking-tight">
              SELF_PLAY_LEARNING_LOOP
            </h2>
          </div>

          <div className="space-y-6">
            <DialecticWarRoom />
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ResilienceMonitor />
              <EvolutionaryOptimization />
            </div>

            <StrategyEngine />
          </div>
        </div>

        {/* Twin-Turbo Engines */}
        <TwinTurboGauges />

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* AI Chat Placeholder */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 flex items-center justify-center"
          >
            <div className="text-center">
              <Brain className="w-12 h-12 text-axiom-neon-purple mx-auto mb-2" />
              <p className="text-sm font-mono text-text-muted">
                AI_CHAT
              </p>
              <p className="text-xs font-mono text-text-dim mt-1">
                GLM-4.5 Integration
              </p>
            </div>
          </motion.div>

          {/* Execution Deck */}
          <ExecutionDeck />

          {/* Autonomous Swarm */}
          <div className="lg:col-span-1">
            <AutonomousSwarm />
          </div>
        </div>
      </main>

      {/* Payment Modal */}
      <PaymentModal isOpen={showPaymentModal} onClose={() => setShowPaymentModal(false)} />
    </div>
  );
}