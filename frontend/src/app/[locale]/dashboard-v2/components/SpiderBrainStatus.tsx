'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Zap, Microscope, Shield, Radio, Newspaper, Briefcase } from 'lucide-react';
import { useSpiderBrain } from '../hooks/useSpiderBrain';

const iconMap: Record<string, any> = {
  Brain,
  Zap,
  Microscope,
  Shield,
  Radio,
  Newspaper,
  Briefcase
};

const colorMap: Record<string, string> = {
  cyan: 'text-axiom-neon-cyan border-axiom-neon-cyan/30 shadow-glow-cyan',
  yellow: 'text-yellow-400 border-yellow-400/30',
  purple: 'text-axiom-neon-purple border-axiom-neon-purple/30 shadow-glow-purple',
  red: 'text-axiom-neon-red border-axiom-neon-red/30 shadow-glow-red',
  green: 'text-axiom-neon-green border-axiom-neon-green/30 shadow-glow-green',
  blue: 'text-axiom-neon-blue border-axiom-neon-blue/30',
  gold: 'text-axiom-neon-gold border-axiom-neon-gold/30 shadow-glow-gold',
};

export const SpiderBrainStatus: React.FC = () => {
  const { status, loading } = useSpiderBrain();

  return (
    <div
      data-testid="spider-brain-status"
      className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6 mb-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Brain className="w-6 h-6 text-axiom-neon-cyan" />
          <h2 className="text-xl font-mono font-bold text-white tracking-tight">
            SPIDER_WEB_BRAIN
          </h2>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-axiom-neon-green/10 border border-axiom-neon-green/30 rounded-lg">
          <div className="w-2 h-2 rounded-full bg-axiom-neon-green animate-pulse shadow-glow-green"></div>
          <span className="text-xs font-mono text-axiom-neon-green font-bold">
            MAINNET: {status.totalOnline}/7 AGENTS ONLINE
          </span>
        </div>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {status.agents.map((agent, index) => {
          const Icon = iconMap[agent.icon];
          const colorClass = colorMap[agent.color];

          return (
            <motion.div
              key={agent.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="relative group"
            >
              {/* Hexagonal Container */}
              <div className={`relative bg-axiom-bg/80 border ${colorClass} rounded-lg p-4 hover:scale-105 transition-all duration-300 cursor-pointer`}>
                {/* Status Indicator */}
                <div className="absolute top-2 right-2">
                  <div className={`w-2 h-2 rounded-full ${agent.status === 'online'
                      ? 'bg-axiom-neon-green animate-pulse'
                      : agent.status === 'degraded'
                        ? 'bg-yellow-500'
                        : 'bg-axiom-neon-red'
                    }`}></div>
                </div>

                {/* Icon */}
                <div className="flex justify-center mb-3">
                  <Icon className={`w-8 h-8 ${colorClass.split(' ')[0]}`} />
                </div>

                {/* Agent Name */}
                <div className="text-center">
                  <h3 className="text-xs font-mono font-bold text-white mb-1">
                    {agent.name.toUpperCase()}
                  </h3>
                  <p className="text-[10px] text-text-muted font-mono">
                    {agent.latency}ms
                  </p>
                </div>

                {/* Hover Tooltip */}
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
                  <div className="bg-axiom-surface/95 border border-glass-border backdrop-blur-glass rounded-lg p-3 shadow-xl min-w-[200px]">
                    <div className="text-[10px] font-mono space-y-1">
                      <div className="flex justify-between">
                        <span className="text-text-muted">Purpose:</span>
                        <span className="text-white">{agent.purpose}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-muted">Model:</span>
                        <span className="text-white">{agent.model}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-text-muted">Status:</span>
                        <span className={`${agent.status === 'online' ? 'text-axiom-neon-green' : 'text-axiom-neon-red'
                          }`}>
                          {agent.status.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Neural Connection Lines (for adjacent agents) */}
              {index < status.agents.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 left-full w-4 h-px border-t border-dashed border-gray-600 -translate-y-1/2"></div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Average Latency */}
      <div className="mt-6 flex items-center justify-center gap-2 text-xs font-mono text-text-muted">
        <span>AVG_LATENCY:</span>
        <span className="text-axiom-neon-cyan font-bold">{status.averageLatency}ms</span>
      </div>
    </div>
  );
};