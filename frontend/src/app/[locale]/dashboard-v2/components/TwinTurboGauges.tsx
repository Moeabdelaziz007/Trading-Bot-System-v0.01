'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Gauge, Zap, Brain } from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

interface EngineData {
  aexi: number;
  dream: number;
  mtfAlignment: 'full' | 'partial' | 'none';
}

const CircularGauge: React.FC<{
  value: number;
  max: number;
  color: string;
  glowColor: string;
  label: string;
  threshold: number;
}> = ({ value, max, color, glowColor, label, threshold }) => {
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 45; // radius = 45
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  const isTriggered = value >= threshold;

  return (
    <div className="relative flex flex-col items-center">
      <svg className="w-32 h-32 -rotate-90" viewBox="0 0 100 100">
        {/* Background Circle */}
        <circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth="8"
        />
        {/* Progress Circle */}
        <motion.circle
          cx="50"
          cy="50"
          r="45"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={isTriggered ? glowColor : ''}
        />
      </svg>

      {/* Center Value */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-mono font-bold ${isTriggered ? color.replace('stroke-', 'text-') : 'text-white'}`}>
          {value}
        </span>
        <span className="text-xs text-text-muted font-mono">/{max}</span>
      </div>

      {/* Label */}
      <div className="mt-2 text-center">
        <p className="text-sm font-mono font-bold text-white">{label}</p>
        {isTriggered && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className={`text-xs font-mono ${color.replace('stroke-', 'text-')} mt-1`}
          >
            ⚡ TRIGGERED
          </motion.p>
        )}
      </div>
    </div>
  );
};

export const TwinTurboGauges: React.FC = () => {
  const [engineData, setEngineData] = useState<EngineData>({
    aexi: 78,
    dream: 65,
    mtfAlignment: 'full'
  });

  useEffect(() => {
    const fetchEngineData = async () => {
      try {
        const response = await axios.get(`${API_BASE}/api/engines/status`);
        if (response.data) {
          setEngineData(response.data);
        }
      } catch (error) {
        console.log('Using mock engine data');
      }
    };

    fetchEngineData();
    const interval = setInterval(fetchEngineData, 5000);

    return () => clearInterval(interval);
  }, []);

  const mtfStatusColor = {
    full: 'bg-axiom-neon-green text-white',
    partial: 'bg-yellow-500 text-black',
    none: 'bg-axiom-neon-red text-white'
  };

  const mtfStatusIcon = {
    full: '🟢',
    partial: '🟡',
    none: '🔴'
  };

  return (
    <div
      data-testid="twin-turbo-gauges"
      className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6"
    >
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <Gauge className="w-6 h-6 text-axiom-neon-purple" />
        <h2 className="text-xl font-mono font-bold text-white tracking-tight">
          TWIN_TURBO_ENGINES
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* AEXI Protocol */}
        <div className="flex flex-col items-center">
          <CircularGauge
            value={engineData.aexi}
            max={100}
            color="stroke-axiom-neon-cyan"
            glowColor="drop-shadow-glow-cyan"
            label="AEXI PROTOCOL"
            threshold={80}
          />
          <p className="text-xs text-text-muted font-mono mt-3 text-center max-w-[200px]">
            Exhaustion Detection Engine
          </p>
        </div>

        {/* Dream Machine */}
        <div className="flex flex-col items-center">
          <CircularGauge
            value={engineData.dream}
            max={100}
            color="stroke-axiom-neon-purple"
            glowColor="drop-shadow-glow-purple"
            label="DREAM MACHINE"
            threshold={70}
          />
          <p className="text-xs text-text-muted font-mono mt-3 text-center max-w-[200px]">
            Chaos Theory Pattern Detector
          </p>
        </div>

        {/* MTF Scalper */}
        <div className="flex flex-col items-center justify-center">
          <div className="bg-axiom-bg/80 border border-glass-border rounded-lg p-6 w-full">
            <div className="flex items-center gap-2 mb-4">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h3 className="text-sm font-mono font-bold text-white">
                MTF_SCALPER
              </h3>
            </div>

            {/* Alignment Status */}
            <div className="flex items-center justify-center gap-3 mb-4">
              <span className="text-4xl">{mtfStatusIcon[engineData.mtfAlignment]}</span>
              <div>
                <p className="text-xs text-text-muted font-mono">ALIGNMENT</p>
                <p className={`text-sm font-mono font-bold ${engineData.mtfAlignment === 'full' ? 'text-axiom-neon-green' :
                    engineData.mtfAlignment === 'partial' ? 'text-yellow-400' :
                      'text-axiom-neon-red'
                  }`}>
                  {engineData.mtfAlignment.toUpperCase()}
                </p>
              </div>
            </div>

            {/* Timeframes */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-text-muted">1M</span>
                <div className={`w-2 h-2 rounded-full ${engineData.mtfAlignment !== 'none' ? 'bg-axiom-neon-green' : 'bg-gray-600'}`}></div>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-text-muted">5M</span>
                <div className={`w-2 h-2 rounded-full ${engineData.mtfAlignment !== 'none' ? 'bg-axiom-neon-green' : 'bg-gray-600'}`}></div>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-text-muted">15M</span>
                <div className={`w-2 h-2 rounded-full ${engineData.mtfAlignment === 'full' ? 'bg-axiom-neon-green' : 'bg-gray-600'}`}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};