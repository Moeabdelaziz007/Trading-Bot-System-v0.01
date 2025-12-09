import React from 'react';
import { BOT_SCORES } from '../constants';
import { BotScore } from '../types';

const Gauge = ({ score, color, name, size = 120 }: { score: number; color: string; name: string; size?: number }) => {
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background Circle */}
        <svg className="transform -rotate-90 w-full h-full">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#16213E"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Progress Circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-1000 ease-out"
            style={{ filter: `drop-shadow(0 0 4px ${color})` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
          <span className="text-2xl font-bold font-mono">{score}%</span>
        </div>
      </div>
      <span className="mt-3 text-sm font-medium text-gray-400 uppercase tracking-wider">{name}</span>
      {/* Dots representation below */}
      <div className="mt-2 flex gap-1">
        {Array.from({ length: 6 }).map((_, i) => (
          <div
            key={i}
            className={`w-1.5 h-1.5 rounded-full ${i < (score / 100) * 6 ? '' : 'bg-gray-700'}`}
            style={{ backgroundColor: i < (score / 100) * 6 ? color : undefined }}
          />
        ))}
      </div>
    </div>
  );
};

export const BotScores: React.FC = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl relative overflow-hidden group hover:border-axiom-primary/30 transition-colors duration-300">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-axiom-primary/10 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-axiom-primary"><path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/></svg>
          </div>
          <h2 className="text-lg font-semibold tracking-tight">AI Bot Scores</h2>
        </div>
        <button className="text-xs text-axiom-secondary hover:text-white transition-colors">View All</button>
      </div>

      <div className="flex flex-wrap justify-around items-end gap-6 mb-8">
        {BOT_SCORES.map((bot, idx) => (
            // Make the middle one slightly larger for visual hierarchy as per design
           <Gauge 
             key={bot.name} 
             name={bot.name}
             score={bot.score}
             color={bot.color}
             size={idx === 1 ? 140 : 100} 
           />
        ))}
      </div>

      <div className="grid grid-cols-3 divide-x divide-white/10 border-t border-white/10 pt-4">
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">ACTIVE TRADES</div>
          <div className="text-xl font-bold font-mono text-white">12</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">WIN RATE</div>
          <div className="text-xl font-bold font-mono text-axiom-primary">78.4%</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-gray-400 mb-1">PROFIT (24H)</div>
          <div className="text-xl font-bold font-mono text-axiom-primary">+$1,240</div>
        </div>
      </div>
      
      {/* Background ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-axiom-secondary/5 blur-[80px] rounded-full pointer-events-none" />
    </div>
  );
};