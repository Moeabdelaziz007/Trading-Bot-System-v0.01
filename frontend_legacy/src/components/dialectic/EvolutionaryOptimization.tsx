import React from 'react';
import { 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';
import { Activity, Dna, Trophy, TrendingUp } from 'lucide-react';
import { MOCK_FITNESS_DATA, COLORS } from '../constants';
import { motion } from 'framer-motion';

export const EvolutionaryOptimization: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      
      {/* Chart Section */}
      <div className="lg:col-span-2 bg-[#0A0A1A]/50 border border-gray-800 rounded-xl p-5 relative overflow-hidden backdrop-blur-sm">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-2">
            <Dna className="text-green-400 w-5 h-5" />
            <h3 className="text-gray-200 font-mono font-semibold">EVOLUTIONARY_FITNESS_LANDSCAPE</h3>
          </div>
          <div className="flex items-center gap-2">
            <motion.span 
              animate={{ opacity: [1, 0.4, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-green-500"
            />
            <span className="text-xs font-mono text-green-400 tracking-wider">[RUNNING]</span>
          </div>
        </div>

        <div className="h-[250px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={MOCK_FITNESS_DATA}>
              <defs>
                <linearGradient id="colorFitness" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.core} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={COLORS.core} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis 
                dataKey="generation" 
                stroke="#64748b" 
                tick={{fontSize: 12, fontFamily: 'JetBrains Mono'}}
                tickLine={false}
                axisLine={false}
              />
              <YAxis 
                stroke="#64748b" 
                tick={{fontSize: 12, fontFamily: 'JetBrains Mono'}}
                tickLine={false}
                axisLine={false}
                domain={['auto', 'auto']}
              />
              <Tooltip 
                contentStyle={{ backgroundColor: '#0A0A1A', borderColor: '#334155', borderRadius: '8px' }}
                itemStyle={{ fontFamily: 'JetBrains Mono', fontSize: '12px' }}
                labelStyle={{ fontFamily: 'JetBrains Mono', color: '#94A3B8', marginBottom: '4px' }}
              />
              <Area 
                type="monotone" 
                dataKey="fitness" 
                stroke={COLORS.core} 
                strokeWidth={2}
                fillOpacity={1} 
                fill="url(#colorFitness)" 
              />
              <Area 
                type="monotone" 
                dataKey="avgFitness" 
                stroke="#475569" 
                strokeDasharray="4 4"
                fill="none" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Stats Column */}
      <div className="lg:col-span-1 flex flex-col gap-4">
        
        {/* Current Gen Stats */}
        <div className="bg-[#0A0A1A]/80 border border-gray-800 p-4 rounded-xl flex-1 flex flex-col justify-center">
            <div className="flex items-center gap-2 mb-3 text-gray-400 font-mono text-xs uppercase tracking-wider">
                <Activity className="w-3 h-3" /> Population Stats
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <div className="text-2xl font-mono text-white">4,281</div>
                    <div className="text-[10px] text-gray-500">GENERATION #</div>
                </div>
                <div>
                    <div className="text-2xl font-mono text-white">128</div>
                    <div className="text-[10px] text-gray-500">POPULATION SIZE</div>
                </div>
            </div>
        </div>

        {/* Best Strategy Card */}
        <div className="bg-gradient-to-br from-gray-900 to-black border border-gray-700 p-5 rounded-xl flex-1 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-2 opacity-10">
                <Trophy size={64} color={COLORS.core} />
            </div>
            <h4 className="text-sm font-mono text-gray-400 mb-4 flex items-center gap-2">
                <Trophy className="w-4 h-4 text-yellow-500" />
                ALPHA_GENOME_ID: #8X92
            </h4>
            
            <div className="space-y-3">
                <div className="flex justify-between items-end border-b border-gray-800 pb-2">
                    <span className="text-xs text-gray-500 font-mono">FITNESS_SCORE</span>
                    <span className="text-xl font-bold text-[#00FFFF] font-mono">98.42</span>
                </div>
                <div className="flex justify-between items-end border-b border-gray-800 pb-2">
                    <span className="text-xs text-gray-500 font-mono">SHARPE_RATIO</span>
                    <span className="text-md font-bold text-white font-mono">3.14</span>
                </div>
                <div className="flex justify-between items-end">
                    <span className="text-xs text-gray-500 font-mono">MAX_DRAWDOWN</span>
                    <span className="text-md font-bold text-[#FF0055] font-mono">-2.4%</span>
                </div>
            </div>
        </div>

      </div>
    </div>
  );
};