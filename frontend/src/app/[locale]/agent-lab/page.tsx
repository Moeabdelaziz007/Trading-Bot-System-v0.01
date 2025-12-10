'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { AgentBuilder } from './components/AgentBuilder';
import { StrategyEditor } from './components/StrategyEditor';
import { SimulationSandbox } from './components/SimulationSandbox';
import { StrategyRule } from './components/StrategyBlock';

interface AgentConfig {
  name: string;
  description: string;
  avatar: string | null;
  dna: {
    riskTolerance: number;
    tradeFrequency: number;
    intelligenceLevel: number;
  };
  broker: 'capital' | 'alpaca' | 'bybit';
}

export default function AgentLabPage() {
  const [agentConfig, setAgentConfig] = useState<AgentConfig>({
    name: '',
    description: '',
    avatar: null,
    dna: {
      riskTolerance: 50,
      tradeFrequency: 50,
      intelligenceLevel: 50,
    },
    broker: 'capital'
  });

  const [strategyRules, setStrategyRules] = useState<StrategyRule[]>([]);

  const handleDeploy = () => {
    // TODO: Implement actual deployment
    console.log('Deploying agent:', { ...agentConfig, rules: strategyRules });
    alert(`🚀 Agent "${agentConfig.name}" is being deployed to ${agentConfig.broker}!`);
  };

  return (
    <div className="min-h-screen bg-axiom-bg">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-axiom-surface/80 backdrop-blur-glass border-b border-glass-border">
        <div className="max-w-[1920px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link 
                href="/dashboard-v2"
                className="p-2 hover:bg-axiom-bg rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-text-muted hover:text-white" />
              </Link>
              <div className="flex items-center gap-3">
                <Sparkles className="w-8 h-8 text-axiom-neon-purple" />
                <div>
                  <h1 className="text-xl font-mono font-bold text-white tracking-tight">
                    AGENT_FOUNDRY
                  </h1>
                  <p className="text-xs text-text-muted font-mono">
                    Create & Simulate Trading Agents
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 px-4 py-2 bg-axiom-neon-purple/10 border border-axiom-neon-purple/30 rounded-lg">
              <div className="w-2 h-2 rounded-full bg-axiom-neon-purple animate-pulse"></div>
              <span className="text-sm font-mono text-axiom-neon-purple font-bold">
                LAB_MODE
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - 3 Column Layout */}
      <main className="max-w-[1920px] mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Panel - Agent Builder */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:col-span-3"
          >
            <div className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 sticky top-24">
              <AgentBuilder 
                config={agentConfig}
                onChange={setAgentConfig}
              />
            </div>
          </motion.div>

          {/* Center Panel - Strategy Editor */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="lg:col-span-5"
          >
            <div className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6">
              <StrategyEditor 
                rules={strategyRules}
                onChange={setStrategyRules}
              />
            </div>
          </motion.div>

          {/* Right Panel - Simulation Sandbox */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-4"
          >
            <div className="bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 sticky top-24">
              <SimulationSandbox 
                agentConfig={{ ...agentConfig, rules: strategyRules }}
                onDeploy={handleDeploy}
              />
            </div>
          </motion.div>
        </div>

        {/* DNA Visualization Background */}
        <div className="fixed inset-0 pointer-events-none overflow-hidden -z-10 opacity-10">
          <svg className="w-full h-full" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="dna-pattern" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                <motion.path
                  d="M 10 50 Q 30 30, 50 50 T 90 50"
                  stroke="#00FFFF"
                  strokeWidth="2"
                  fill="none"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                />
                <motion.path
                  d="M 10 50 Q 30 70, 50 50 T 90 50"
                  stroke="#A855F7"
                  strokeWidth="2"
                  fill="none"
                  initial={{ pathLength: 0 }}
                  animate={{ pathLength: 1 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear", delay: 1 }}
                />
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#dna-pattern)" />
          </svg>
        </div>
      </main>
    </div>
  );
}