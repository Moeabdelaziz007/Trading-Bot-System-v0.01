import React, { useState } from 'react';
import { Server, Database, ShieldCheck, Activity } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { MOCK_CIRCUIT_BREAKERS } from '../constants';

export const ResilienceMonitor: React.FC = () => {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  return (
    <div className="border-t border-gray-800 pt-6">
      <h3 className="text-sm font-mono text-gray-500 mb-4 flex items-center gap-2">
        <ShieldCheck className="w-4 h-4" />
        SYSTEM_RESILIENCE_&_HEALTH
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Circuit Breakers */}
        <div className="lg:col-span-2 bg-[#050510] border border-gray-800 rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <span className="text-xs font-mono text-gray-400">CIRCUIT_BREAKERS</span>
            <span className="text-[10px] text-gray-600 font-mono">AUTO-RESET ENABLED</span>
          </div>
          <div className="space-y-2">
            {MOCK_CIRCUIT_BREAKERS.map((cb) => (
              <div 
                key={cb.id} 
                className="relative flex items-center justify-between bg-white/5 p-2 rounded border border-white/5 hover:border-gray-600 hover:bg-white/10 transition-all cursor-help"
                onMouseEnter={() => setHoveredId(cb.id)}
                onMouseLeave={() => setHoveredId(null)}
              >
                <div className="flex items-center gap-2">
                  <div className={`w-1.5 h-1.5 rounded-full ${cb.status === 'CLOSED' ? 'bg-green-500 shadow-[0_0_5px_#10B981]' : 'bg-red-500 animate-pulse'}`}></div>
                  <span className="text-xs font-mono text-gray-300">{cb.name}</span>
                </div>
                <div className="flex items-center gap-4">
                   <span className="text-[10px] font-mono text-gray-500">{cb.latency}</span>
                   <span className={`text-[10px] font-bold font-mono px-1.5 py-0.5 rounded ${
                     cb.status === 'CLOSED' 
                       ? 'bg-green-900/30 text-green-400' 
                       : 'bg-red-900/30 text-red-400'
                   }`}>
                     {cb.status}
                   </span>
                </div>

                {/* Sci-Fi Glassmorphism Tooltip */}
                <AnimatePresence>
                  {hoveredId === cb.id && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 5, scale: 0.95 }}
                      transition={{ duration: 0.2 }}
                      className="absolute left-0 bottom-full mb-2 w-64 bg-[#0A0A1A]/95 border border-gray-700 backdrop-blur-md rounded-lg p-3 shadow-[0_4px_20px_rgba(0,0,0,0.5)] z-50 pointer-events-none"
                    >
                      <div className="flex items-center gap-2 mb-2 border-b border-gray-800 pb-2">
                        <Activity className="w-3 h-3 text-cyan-400" />
                        <span className="text-[10px] font-mono font-bold text-gray-300 tracking-wider">BREAKER_STATS</span>
                      </div>
                      <div className="space-y-1.5 text-[10px] font-mono text-gray-400">
                        <div className="flex justify-between items-center">
                          <span>LAST_RESET:</span>
                          <span className="text-gray-200">{cb.lastReset}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>TOTAL_CYCLES:</span>
                          <span className="text-gray-200">{cb.totalCycles}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>AVG_LATENCY:</span>
                          <span className={cb.status === 'CLOSED' ? "text-green-400" : "text-red-400"}>
                            {cb.avgLatency}
                          </span>
                        </div>
                      </div>
                      {/* Decorative corner accent */}
                      <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-500/50 rounded-tr-sm"></div>
                      <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-500/50 rounded-bl-sm"></div>
                    </motion.div>
                  )}
                </AnimatePresence>

              </div>
            ))}
          </div>
        </div>

        {/* System Health */}
        <div className="bg-[#050510] border border-gray-800 rounded-lg p-4 flex flex-col justify-between">
           <div className="flex items-center gap-2 text-xs font-mono text-gray-400 mb-2">
             <Server className="w-3 h-3" /> NODE_HEALTH (US-EAST)
           </div>
           
           <div className="space-y-3 mt-1">
             <div>
               <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                 <span>CPU_LOAD</span>
                 <span className="text-cyan-400">42%</span>
               </div>
               <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                 <div className="h-full bg-cyan-500 w-[42%]"></div>
               </div>
             </div>
             <div>
               <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                 <span>MEMORY_HEAP</span>
                 <span className="text-purple-400">68%</span>
               </div>
               <div className="w-full h-1 bg-gray-800 rounded-full overflow-hidden">
                 <div className="h-full bg-purple-500 w-[68%]"></div>
               </div>
             </div>
             <div>
               <div className="flex justify-between text-[10px] text-gray-500 mb-1">
                 <span>UPTIME</span>
                 <span className="text-white">14d 02h 12m</span>
               </div>
             </div>
           </div>
        </div>

        {/* Storage / DB */}
        <div className="bg-[#050510] border border-gray-800 rounded-lg p-4 flex flex-col justify-between">
           <div className="flex items-center gap-2 text-xs font-mono text-gray-400 mb-2">
             <Database className="w-3 h-3" /> DATA_PERSISTENCE
           </div>
           
           <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="bg-gray-900/50 p-2 rounded text-center border border-gray-800">
                <div className="text-[10px] text-gray-500 mb-1">D1 SQL</div>
                <div className="text-xs text-white font-mono">240MB</div>
                <div className="text-[9px] text-green-500 mt-1">OPTIMAL</div>
              </div>
              <div className="bg-gray-900/50 p-2 rounded text-center border border-gray-800">
                <div className="text-[10px] text-gray-500 mb-1">R2 STORE</div>
                <div className="text-xs text-white font-mono">1.2GB</div>
                <div className="text-[9px] text-green-500 mt-1">SYNCED</div>
              </div>
           </div>
           
           <div className="mt-2 text-[10px] text-gray-600 font-mono text-center pt-2 border-t border-gray-800">
             LAST SNAPSHOT: 04:00 UTC
           </div>
        </div>

      </div>
    </div>
  );
};