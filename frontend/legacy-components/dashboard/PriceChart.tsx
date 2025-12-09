import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { CHART_DATA } from '@/lib/constants';

export const PriceChart: React.FC = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl flex flex-col h-full relative group hover:border-axiom-secondary/30 transition-colors duration-300">
      <div className="flex justify-between items-start mb-6">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="text-2xl font-bold flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-[#F7931A] flex items-center justify-center text-xs font-bold text-white">₿</span>
              BTC/USDT
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-axiom-primary/20 text-axiom-primary border border-axiom-primary/20">BULLISH</span>
          </div>
          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-mono font-bold text-white neon-text-secondary">$98,425.51</span>
            <span className="text-axiom-primary font-mono text-sm">+2.45%</span>
          </div>
        </div>
        
        <div className="flex bg-axiom-bg/50 rounded-lg p-1 border border-white/5">
          {['1H', '4H', '1D', '1W'].map((tf, i) => (
            <button 
              key={tf} 
              className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${i === 0 ? 'bg-axiom-surface text-white shadow-sm' : 'text-gray-500 hover:text-gray-300'}`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 w-full min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={CHART_DATA}>
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00D9FF" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00D9FF" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              dataKey="time" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#6B7280', fontSize: 10 }}
              dy={10}
            />
            <YAxis 
              domain={['auto', 'auto']} 
              orientation="right" 
              axisLine={false} 
              tickLine={false} 
              tick={{ fill: '#6B7280', fontSize: 10, fontFamily: 'JetBrains Mono' }}
              tickFormatter={(value) => `$${(value/1000).toFixed(1)}k`}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: 'rgba(13, 13, 13, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
              itemStyle={{ color: '#00D9FF' }}
              labelStyle={{ color: '#9CA3AF', marginBottom: '4px' }}
              formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
            />
            <Area 
              type="monotone" 
              dataKey="value" 
              stroke="#00D9FF" 
              strokeWidth={2}
              fillOpacity={1} 
              fill="url(#colorValue)" 
              animationDuration={1500}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
