import React from 'react';
import { PATTERNS } from '../constants';
import { Target } from 'lucide-react';

export const PatternRecognition: React.FC = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl h-full">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-1.5 bg-axiom-tertiary/10 rounded-lg">
           <Target className="w-5 h-5 text-axiom-tertiary" />
        </div>
        <h2 className="text-lg font-semibold">AI Pattern Recognition</h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {PATTERNS.map((pattern) => (
          <div key={pattern.asset} className="bg-[#13131f] border border-white/5 rounded-xl p-4 hover:border-axiom-tertiary/50 transition-all duration-300 group relative overflow-hidden">
             {/* Decorative corner glow */}
             <div className="absolute top-0 right-0 w-16 h-16 bg-axiom-tertiary/5 blur-2xl rounded-full -translate-y-1/2 translate-x-1/2 group-hover:bg-axiom-tertiary/10 transition-all"></div>

            <div className="flex items-center gap-3 mb-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm ${pattern.asset === 'LTC' ? 'bg-[#345D9D]/20 text-[#345D9D] border border-[#345D9D]/30' : 'bg-white/10 text-white border border-white/20'}`}>
                {pattern.asset}
              </div>
              <div>
                 <div className="text-[10px] text-gray-400 uppercase tracking-widest">DETECTED</div>
                 <div className="font-bold text-white leading-tight">{pattern.name}</div>
              </div>
            </div>

            <div className="flex justify-between items-end mb-4">
              <div>
                <div className="text-xs text-gray-500 mb-1">Timeframe</div>
                <div className="font-mono text-sm">{pattern.timeframe}</div>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500 mb-1">Confidence</div>
                <div className="font-mono text-xl font-bold text-white">{pattern.confidence}%</div>
              </div>
            </div>

            <button className="w-full py-2 bg-axiom-surface hover:bg-axiom-tertiary hover:text-white border border-axiom-tertiary/30 text-axiom-tertiary rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-[0_0_10px_rgba(0,0,0,0.5)] group-hover:shadow-[0_0_15px_rgba(255,0,255,0.4)]">
              {pattern.action}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
