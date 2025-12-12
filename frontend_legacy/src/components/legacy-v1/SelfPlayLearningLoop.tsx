'use client';

import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Zap, 
  Shield, 
  Activity, 
  Database, 
  Server, 
  Cpu, 
  BarChart3,
  Play,
  Pause,
  Radio
} from 'lucide-react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock data for the dashboard
const dashboardData = {
  dialectic: {
    core: {
      name: "Core Agent",
      analysis: "Analyzing market conditions for bullish breakout pattern. BTCUSD showing strong momentum with RSI oversold bounce at $94,500 support level. Volume profile indicates accumulation phase. Risk-reward ratio favorable at 1:3.",
      confidence: 78
    },
    shadow: {
      name: "Shadow Agent",
      analysis: "Warning: High volatility detected in BTCUSD support zone. Recent history shows 3 consecutive false breakouts with sharp reversals. Funding rates elevated indicating long liquidation risk. Recommend tightening stop-loss parameters.",
      regret: 65
    },
    synthesis: {
      decision: "Enter long position with tight stop-loss below $94,000 and take-profit at $96,000. Execution weight: 0.65",
      timestamp: "2025-12-10T10:30:45Z"
    }
  },
  evolution: {
    population: {
      generations: 127,
      popSize: 50,
      bestFitness: 0.87,
      avgFitness: 0.64
    },
    bestStrategy: {
      fitness: 0.87,
      sharpe: 2.3,
      maxDrawdown: 0.12,
      age: "24h"
    },
    fitnessHistory: [
      { generation: 0, fitness: 0.45 },
      { generation: 20, fitness: 0.52 },
      { generation: 40, fitness: 0.61 },
      { generation: 60, fitness: 0.68 },
      { generation: 80, fitness: 0.74 },
      { generation: 100, fitness: 0.81 },
      { generation: 120, fitness: 0.85 },
      { generation: 127, fitness: 0.87 }
    ]
  },
  resilience: {
    circuitBreakers: [
      { name: "API", status: "CLOSED" },
      { name: "RISK", status: "CLOSED" },
      { name: "LATENCY", status: "CLOSED" }
    ],
    systemHealth: {
      cpu: 24,
      memory: 128,
      uptime: "14d 6h"
    },
    memoryUtilization: {
      d1: "4.2GB / 10GB",
      r2: "245GB",
      snapshots: 12487
    }
  }
};

// Custom hook for typewriter effect
const useTypewriter = (text: string, speed: number = 50) => {
  const [displayedText, setDisplayedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText((prev) => prev + text.charAt(index));
        setIndex((prev) => prev + 1);
      }, speed);
      
      return () => clearTimeout(timeout);
    }
  }, [index, text, speed]);

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('');
    setIndex(0);
  }, [text]);

  return displayedText;
};

// Progress bar component
const ProgressBar = ({ 
  value, 
  max = 100, 
  color, 
  label 
}: { 
  value: number; 
  max?: number; 
  color: string; 
  label: string;
}) => {
  const percentage = (value / max) * 100;
  
  return (
    <div className="mb-2">
      <div className="flex justify-between text-xs text-gray-400 mb-1">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
        <motion.div 
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
      </div>
    </div>
  );
};

// Status indicator component
const StatusIndicator = ({ status }: { status: string }) => {
  const isClosed = status === "CLOSED";
  
  return (
    <div className="flex items-center">
      <div className={`w-2 h-2 rounded-full mr-2 ${isClosed ? 'bg-green-500' : 'bg-red-500'}`} />
      <span className={isClosed ? 'text-green-400' : 'text-red-400'}>{status}</span>
    </div>
  );
};

// Pulse animation component
const PulseIndicator = () => (
  <motion.div
    className="w-3 h-3 rounded-full bg-green-500 ml-2"
    animate={{
      scale: [1, 1.2, 1],
      opacity: [0.7, 1, 0.7]
    }}
    transition={{
      duration: 1.5,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  />
);

export const SelfPlayLearningLoop: React.FC = () => {
  const [isRunning, setIsRunning] = useState(true);
  const coreText = useTypewriter(dashboardData.dialectic.core.analysis, 30);
  const shadowText = useTypewriter(dashboardData.dialectic.shadow.analysis, 30);

  return (
    <div className="min-h-screen bg-[#0A0A1A] text-gray-100 font-sans p-4 md:p-6">
      {/* Header Section - Dialectic War Room */}
      <div className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-4">
          <div className="flex items-center mb-2 md:mb-0">
            <Brain className="text-cyan-400 mr-2" size={24} />
            <h1 className="text-xl md:text-2xl font-mono font-bold">DIALECTIC WAR ROOM</h1>
          </div>
          <div className="flex items-center">
            <div className="flex items-center bg-gray-900 px-3 py-1 rounded-full">
              <Radio className="text-green-500 mr-2" size={16} />
              <span className="text-sm font-mono">LIVE</span>
              <PulseIndicator />
            </div>
            <button 
              className="ml-3 bg-gray-800 hover:bg-gray-700 px-3 py-1 rounded-full flex items-center transition-colors"
              onClick={() => setIsRunning(!isRunning)}
            >
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
              <span className="ml-1 text-sm font-mono">{isRunning ? 'PAUSE' : 'RESUME'}</span>
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
          {/* Core Agent Panel */}
          <motion.div 
            className="border border-cyan-500 rounded-xl p-4 relative overflow-hidden"
            style={{
              boxShadow: '0 0 15px rgba(0, 255, 255, 0.3)',
              background: 'rgba(17, 24, 39, 0.7)'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="absolute inset-0 bg-cyan-500 opacity-5 pointer-events-none"></div>
            <div className="flex items-center mb-3">
              <Zap className="text-cyan-400 mr-2" size={20} />
              <h2 className="font-mono font-bold text-cyan-400">{dashboardData.dialectic.core.name} (Thesis)</h2>
            </div>
            <div className="font-mono text-sm text-gray-300 min-h-[100px]">
              {coreText}
              <span className="inline-block w-2 h-4 bg-cyan-400 ml-1 animate-pulse"></span>
            </div>
          </motion.div>
          
          {/* Shadow Agent Panel */}
          <motion.div 
            className="border border-rose-500 rounded-xl p-4 relative overflow-hidden"
            style={{
              boxShadow: '0 0 15px rgba(255, 0, 85, 0.3)',
              background: 'rgba(17, 24, 39, 0.7)'
            }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <div className="absolute inset-0 bg-rose-500 opacity-5 pointer-events-none"></div>
            <div className="flex items-center mb-3">
              <Shield className="text-rose-500 mr-2" size={20} />
              <h2 className="font-mono font-bold text-rose-500">{dashboardData.dialectic.shadow.name} (Antithesis)</h2>
            </div>
            <div className="font-mono text-sm text-gray-300 min-h-[100px]">
              {shadowText}
              <span className="inline-block w-2 h-4 bg-rose-500 ml-1 animate-pulse"></span>
            </div>
          </motion.div>
        </div>
        
        {/* Synthesis Terminal */}
        <motion.div 
          className="border border-gray-700 rounded-xl p-4 mb-4 relative overflow-hidden"
          style={{ background: 'rgba(17, 24, 39, 0.7)' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="absolute inset-0 bg-green-500 opacity-5 pointer-events-none"></div>
          <div className="flex items-center mb-3">
            <Activity className="text-green-500 mr-2" size={20} />
            <h2 className="font-mono font-bold text-green-500">SYNTHESIS</h2>
          </div>
          <div className="font-mono text-sm bg-black bg-opacity-30 p-3 rounded-lg">
            <div className="text-green-400">{dashboardData.dialectic.synthesis.decision}</div>
            <div className="text-gray-500 text-xs mt-2">
              Timestamp: {new Date(dashboardData.dialectic.synthesis.timestamp).toLocaleString()}
            </div>
          </div>
          
          {/* Confidence vs Regret Metrics */}
          <div className="mt-4">
            <ProgressBar 
              value={dashboardData.dialectic.core.confidence} 
              color="#00FFFF" 
              label="Core Confidence" 
            />
            <ProgressBar 
              value={dashboardData.dialectic.shadow.regret} 
              color="#FF0055" 
              label="Shadow Regret" 
            />
          </div>
        </motion.div>
      </div>
      
      {/* Middle Section - Evolutionary Optimization */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Population Stats */}
        <motion.div 
          className="rounded-xl p-5 relative overflow-hidden"
          style={{ background: 'rgba(17, 24, 39, 0.7)' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <div className="absolute inset-0 bg-purple-500 opacity-5 pointer-events-none"></div>
          <div className="flex justify-between items-start mb-4">
            <div className="flex items-center">
              <BarChart3 className="text-purple-500 mr-2" size={20} />
              <h2 className="font-mono font-bold text-purple-500">EVOLUTIONARY OPTIMIZATION</h2>
            </div>
            <div className="flex items-center bg-gray-900 px-3 py-1 rounded-full">
              <span className="text-sm font-mono text-green-400">RUNNING</span>
              <PulseIndicator />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
              <div className="text-gray-400 text-sm font-mono mb-1">GENERATIONS</div>
              <div className="text-2xl font-mono font-bold text-white">{dashboardData.evolution.population.generations}</div>
            </div>
            <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
              <div className="text-gray-400 text-sm font-mono mb-1">POP SIZE</div>
              <div className="text-2xl font-mono font-bold text-white">{dashboardData.evolution.population.popSize}</div>
            </div>
            <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
              <div className="text-gray-400 text-sm font-mono mb-1">BEST</div>
              <div className="text-2xl font-mono font-bold text-green-400">
                {(dashboardData.evolution.population.bestFitness * 100).toFixed(0)}%
              </div>
            </div>
            <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
              <div className="text-gray-400 text-sm font-mono mb-1">AVG</div>
              <div className="text-2xl font-mono font-bold text-cyan-400">
                {(dashboardData.evolution.population.avgFitness * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </motion.div>
        
        {/* Best Strategy */}
        <motion.div 
          className="rounded-xl p-5 relative overflow-hidden"
          style={{ background: 'rgba(17, 24, 39, 0.7)' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
        >
          <div className="absolute inset-0 bg-cyan-500 opacity-5 pointer-events-none"></div>
          <h2 className="font-mono font-bold text-cyan-400 mb-4">BEST STRATEGY</h2>
          
          <div className="space-y-4">
            <div>
              <div className="text-gray-400 text-sm font-mono mb-1">FITNESS SCORE</div>
              <div className="text-3xl font-mono font-bold text-white">
                {(dashboardData.evolution.bestStrategy.fitness * 100).toFixed(0)}%
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-gray-400 text-sm font-mono mb-1">SHARPE RATIO</div>
                <div className="text-xl font-mono font-bold text-green-400">
                  {dashboardData.evolution.bestStrategy.sharpe.toFixed(2)}
                </div>
              </div>
              <div>
                <div className="text-gray-400 text-sm font-mono mb-1">MAX DD</div>
                <div className="text-xl font-mono font-bold text-rose-500">
                  {(dashboardData.evolution.bestStrategy.maxDrawdown * 100).toFixed(0)}%
                </div>
              </div>
            </div>
            
            <div>
              <div className="text-gray-400 text-sm font-mono mb-1">AGE</div>
              <div className="text-lg font-mono font-bold text-purple-400">
                {dashboardData.evolution.bestStrategy.age}
              </div>
            </div>
          </div>
        </motion.div>
      </div>
      
      {/* Fitness Trend Chart */}
      <motion.div 
        className="rounded-xl p-5 mb-6 relative overflow-hidden"
        style={{ background: 'rgba(17, 24, 39, 0.7)' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
      >
        <div className="absolute inset-0 bg-green-500 opacity-5 pointer-events-none"></div>
        <h2 className="font-mono font-bold text-green-400 mb-4">FITNESS TREND</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dashboardData.evolution.fitnessHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis 
                dataKey="generation" 
                stroke="#9CA3AF" 
                tick={{ fontSize: 12, fontFamily: 'monospace' }}
              />
              <YAxis 
                stroke="#9CA3AF" 
                tick={{ fontSize: 12, fontFamily: 'monospace' }}
                domain={[0, 1]}
                tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'rgba(17, 24, 39, 0.9)', 
                  borderColor: '#374151',
                  fontFamily: 'monospace'
                }}
                formatter={(value) => [`${(Number(value) * 100).toFixed(1)}%`, 'Fitness']}
                labelFormatter={(label) => `Generation ${label}`}
              />
              <Area 
                type="monotone" 
                dataKey="fitness" 
                stroke="#00FFFF" 
                fill="url(#fitnessGradient)" 
                strokeWidth={2}
              />
              <defs>
                <linearGradient id="fitnessGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00FFFF" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00FFFF" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </motion.div>
      
      {/* Bottom Section - Resilience & Circuit Breakers */}
      <motion.div 
        className="rounded-xl p-5 relative overflow-hidden"
        style={{ background: 'rgba(17, 24, 39, 0.7)' }}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <div className="absolute inset-0 bg-amber-500 opacity-5 pointer-events-none"></div>
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center">
            <Shield className="text-amber-500 mr-2" size={20} />
            <h2 className="font-mono font-bold text-amber-500">RESILIENCE & CIRCUIT BREAKERS</h2>
          </div>
          <div className="text-sm font-mono text-green-400">ALL SYSTEMS NOMINAL</div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Circuit Breakers */}
          <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
            <h3 className="font-mono font-bold text-gray-300 mb-3">CIRCUIT BREAKERS</h3>
            <div className="space-y-3">
              {dashboardData.resilience.circuitBreakers.map((breaker, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="font-mono text-sm">{breaker.name}</span>
                  <StatusIndicator status={breaker.status} />
                </div>
              ))}
            </div>
          </div>
          
          {/* System Health */}
          <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
            <h3 className="font-mono font-bold text-gray-300 mb-3">SYSTEM HEALTH</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <span className="text-gray-400">CPU</span>
                  <span className="text-cyan-400">{dashboardData.resilience.systemHealth.cpu}%</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
                  <div 
                    className="bg-cyan-500 h-1.5 rounded-full" 
                    style={{ width: `${dashboardData.resilience.systemHealth.cpu}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <span className="text-gray-400">MEMORY</span>
                  <span className="text-purple-400">{dashboardData.resilience.systemHealth.memory}MB</span>
                </div>
                <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
                  <div 
                    className="bg-purple-500 h-1.5 rounded-full" 
                    style={{ width: '64%' }} // Assuming 200MB max
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <span className="text-gray-400">UPTIME</span>
                  <span className="text-green-400">{dashboardData.resilience.systemHealth.uptime}</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Memory Utilization */}
          <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg">
            <h3 className="font-mono font-bold text-gray-300 mb-3">MEMORY UTILIZATION</h3>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <div className="flex items-center">
                    <Database className="mr-1" size={14} />
                    <span className="text-gray-400">D1</span>
                  </div>
                  <span className="text-cyan-400">{dashboardData.resilience.memoryUtilization.d1}</span>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <div className="flex items-center">
                    <Server className="mr-1" size={14} />
                    <span className="text-gray-400">R2</span>
                  </div>
                  <span className="text-purple-400">{dashboardData.resilience.memoryUtilization.r2}</span>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm font-mono">
                  <span className="text-gray-400">SNAPSHOTS</span>
                  <span className="text-green-400">{dashboardData.resilience.memoryUtilization.snapshots.toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default SelfPlayLearningLoop;