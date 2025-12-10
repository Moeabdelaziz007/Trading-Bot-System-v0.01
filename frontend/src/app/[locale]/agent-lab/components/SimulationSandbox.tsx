'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Activity, TrendingUp, TrendingDown, Rocket, AlertCircle } from 'lucide-react';
import { SimulationChart } from './SimulationChart';

interface SimulationStats {
  winRate: number;
  maxDrawdown: number;
  profitFactor: number;
  totalTrades: number;
  projectedReturn: number;
}

interface SimulationSandboxProps {
  agentConfig: any;
  onDeploy: () => void;
}

export const SimulationSandbox: React.FC<SimulationSandboxProps> = ({ agentConfig, onDeploy }) => {
  const [stats, setStats] = useState<SimulationStats>({
    winRate: 0,
    maxDrawdown: 0,
    profitFactor: 0,
    totalTrades: 0,
    projectedReturn: 0
  });

  const [chartData, setChartData] = useState<Array<{ time: string; value: number }>>([]);
  const [isSimulating, setIsSimulating] = useState(false);

  // Simulate backtest based on agent DNA
  useEffect(() => {
    setIsSimulating(true);

    // Generate mock backtest data based on DNA
    const baseWinRate = 50 + (agentConfig.dna.intelligenceLevel * 0.2);
    const riskMultiplier = 1 + (agentConfig.dna.riskTolerance / 100);
    const tradeCount = Math.floor(50 + (agentConfig.dna.tradeFrequency * 2));

    // Generate chart data
    const data = [];
    let equity = 10000;
    const now = new Date();

    for (let i = 0; i < 30; i++) {
      const date = new Date(now);
      date.setDate(date.getDate() - (30 - i));
      
      // Random walk with bias based on DNA
      const change = (Math.random() - 0.45) * 100 * riskMultiplier;
      equity += change;
      
      data.push({
        time: date.toISOString().split('T')[0],
        value: equity
      });
    }

    setChartData(data);

    // Calculate stats
    const finalEquity = data[data.length - 1].value;
    const maxEquity = Math.max(...data.map(d => d.value));
    const minEquity = Math.min(...data.map(d => d.value));
    
    setStats({
      winRate: Math.min(95, baseWinRate),
      maxDrawdown: ((maxEquity - minEquity) / maxEquity) * 100,
      profitFactor: 1 + (agentConfig.dna.intelligenceLevel / 50),
      totalTrades: tradeCount,
      projectedReturn: ((finalEquity - 10000) / 10000) * 100
    });

    setTimeout(() => setIsSimulating(false), 1000);
  }, [agentConfig]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-glass-border">
        <div className="flex items-center gap-3">
          <Activity className="w-6 h-6 text-axiom-neon-green" />
          <h2 className="text-xl font-mono font-bold text-white tracking-tight">
            SIMULATION_SANDBOX
          </h2>
        </div>
        {isSimulating && (
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-axiom-neon-cyan animate-pulse"></div>
            <span className="text-xs font-mono text-axiom-neon-cyan">
              SIMULATING...
            </span>
          </div>
        )}
      </div>

      {/* Live Backtest Chart */}
      <div className="space-y-3">
        <h3 className="text-sm font-mono font-bold text-white">
          THEORETICAL_PERFORMANCE
        </h3>
        <SimulationChart data={chartData} height={250} />
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 gap-4">
        {/* Win Rate */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-axiom-bg/50 border border-glass-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-axiom-neon-green" />
            <span className="text-xs font-mono text-text-muted">WIN_RATE</span>
          </div>
          <p className="text-2xl font-mono font-bold text-axiom-neon-green">
            {stats.winRate.toFixed(1)}%
          </p>
        </motion.div>

        {/* Max Drawdown */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-axiom-bg/50 border border-glass-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-4 h-4 text-axiom-neon-red" />
            <span className="text-xs font-mono text-text-muted">MAX_DRAWDOWN</span>
          </div>
          <p className="text-2xl font-mono font-bold text-axiom-neon-red">
            {stats.maxDrawdown.toFixed(1)}%
          </p>
        </motion.div>

        {/* Profit Factor */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-axiom-bg/50 border border-glass-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-4 h-4 text-axiom-neon-cyan" />
            <span className="text-xs font-mono text-text-muted">PROFIT_FACTOR</span>
          </div>
          <p className="text-2xl font-mono font-bold text-axiom-neon-cyan">
            {stats.profitFactor.toFixed(2)}
          </p>
        </motion.div>

        {/* Total Trades */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-axiom-bg/50 border border-glass-border rounded-lg p-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <AlertCircle className="w-4 h-4 text-axiom-neon-purple" />
            <span className="text-xs font-mono text-text-muted">TOTAL_TRADES</span>
          </div>
          <p className="text-2xl font-mono font-bold text-white">
            {stats.totalTrades}
          </p>
        </motion.div>
      </div>

      {/* Projected Return */}
      <div className={`p-4 rounded-lg border-2 ${
        stats.projectedReturn >= 0 
          ? 'bg-axiom-neon-green/5 border-axiom-neon-green' 
          : 'bg-axiom-neon-red/5 border-axiom-neon-red'
      }`}>
        <div className="flex items-center justify-between">
          <span className="text-sm font-mono text-text-muted">
            PROJECTED_30D_RETURN
          </span>
          <span className={`text-2xl font-mono font-bold ${
            stats.projectedReturn >= 0 ? 'text-axiom-neon-green' : 'text-axiom-neon-red'
          }`}>
            {stats.projectedReturn >= 0 ? '+' : ''}{stats.projectedReturn.toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Deploy Button */}
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={onDeploy}
        disabled={!agentConfig.name || agentConfig.rules?.length === 0}
        className="w-full bg-axiom-neon-green hover:bg-axiom-neon-green/90 text-black font-mono font-bold py-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-glow-green relative overflow-hidden group"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
        <div className="relative flex items-center justify-center gap-3">
          <Rocket className="w-6 h-6" />
          <span className="text-xl">IGNITE_AGENT</span>
        </div>
      </motion.button>

      {/* Warning */}
      {(!agentConfig.name || agentConfig.rules?.length === 0) && (
        <div className="bg-axiom-neon-red/5 border border-axiom-neon-red/30 rounded-lg p-3">
          <p className="text-xs font-mono text-axiom-neon-red">
            ⚠️ Complete agent configuration and add at least one strategy rule to deploy
          </p>
        </div>
      )}
    </div>
  );
};