import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, ShieldAlert, Terminal, Zap } from 'lucide-react';
import { COLORS, CORE_MONOLOGUE, SHADOW_MONOLOGUE } from '../constants';
import { TypewriterEffect } from './ui/TypewriterEffect';

export const DialecticWarRoom: React.FC = () => {
  const [coreIndex, setCoreIndex] = useState(0);
  const [shadowIndex, setShadowIndex] = useState(0);

  // Rotate through monologues
  useEffect(() => {
    const coreInterval = setInterval(() => {
      setCoreIndex((prev) => (prev + 1) % CORE_MONOLOGUE.length);
    }, 5000);
    
    // Offset shadow slightly so they don't switch exactly at the same time
    const shadowInterval = setInterval(() => {
      setShadowIndex((prev) => (prev + 1) % SHADOW_MONOLOGUE.length);
    }, 5500);

    return () => {
      clearInterval(coreInterval);
      clearInterval(shadowInterval);
    };
  }, []);

  return (
    <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 mb-6">
      {/* Header / Title Area for the Section */}
      <div className="lg:col-span-12 flex items-center justify-between border-b border-gray-800 pb-2 mb-2">
        <h2 className="text-xl font-mono text-white flex items-center gap-2">
          <Brain className="w-5 h-5 text-purple-400" />
          DIALECTIC_WAR_ROOM
        </h2>
        <div className="flex items-center gap-2 text-xs font-mono text-gray-400">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
          LIVE_INFERENCE
        </div>
      </div>

      {/* CORE AGENT (Thesis) */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-5 relative group"
      >
        <div className="absolute -inset-0.5 bg-cyan-500/20 rounded-lg blur opacity-30 group-hover:opacity-60 transition duration-1000"></div>
        <div className="relative h-full bg-[#0A0A1A]/90 border border-[#00FFFF]/30 rounded-lg p-6 flex flex-col justify-between overflow-hidden">
           {/* Top Decorator */}
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#00FFFF] to-transparent opacity-50"></div>
           
           <div className="flex justify-between items-start mb-4">
             <div className="flex items-center gap-2 text-[#00FFFF]">
               <Zap className="w-5 h-5" />
               <span className="font-mono font-bold tracking-wider">CORE_AGENT</span>
             </div>
             <span className="text-xs font-mono text-[#00FFFF]/70 border border-[#00FFFF]/30 px-2 py-1 rounded">THESIS</span>
           </div>

           <div className="h-24 font-mono text-sm text-cyan-100/90 leading-relaxed mb-4">
             <span className="text-[#00FFFF] mr-2">{'>'}</span>
             <TypewriterEffect 
               key={`core-${coreIndex}`} 
               text={CORE_MONOLOGUE[coreIndex]} 
               cursorColor="#00FFFF"
             />
           </div>

           {/* Metrics */}
           <div className="mt-auto">
             <div className="flex justify-between text-xs font-mono text-gray-400 mb-1">
               <span>CONFIDENCE_SCORE</span>
               <span className="text-[#00FFFF]">84%</span>
             </div>
             <div className="w-full bg-gray-900 rounded-full h-1.5 overflow-hidden">
               <motion.div 
                 initial={{ width: 0 }}
                 animate={{ width: '84%' }}
                 transition={{ duration: 1.5, ease: "easeOut" }}
                 className="h-full bg-[#00FFFF] shadow-[0_0_10px_#00FFFF]"
               />
             </div>
           </div>
        </div>
      </motion.div>

      {/* SYNTHESIS (Middle) */}
      <div className="lg:col-span-2 flex flex-col items-center justify-center gap-4 relative">
         <div className="absolute inset-0 flex items-center justify-center -z-10">
            <div className="w-px h-full bg-gradient-to-b from-transparent via-purple-500/30 to-transparent"></div>
         </div>
         
         <div className="bg-black border border-gray-700 rounded-full p-3 shadow-[0_0_20px_rgba(168,85,247,0.2)]">
            <div className="w-3 h-3 bg-purple-500 rounded-full animate-ping absolute"></div>
            <div className="w-3 h-3 bg-purple-500 rounded-full relative z-10"></div>
         </div>
         
         <div className="bg-[#0f0f25] border border-gray-700 w-full rounded-md p-3 font-mono text-xs text-center">
            <div className="text-gray-500 mb-1">DECISION</div>
            <div className="text-purple-400 font-bold">LONG 1.5x</div>
            <div className="text-[10px] text-gray-600 mt-1">TS: {new Date().toLocaleTimeString()}</div>
         </div>
      </div>

      {/* SHADOW AGENT (Antithesis) */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        className="lg:col-span-5 relative group"
      >
        <div className="absolute -inset-0.5 bg-[#FF0055]/20 rounded-lg blur opacity-30 group-hover:opacity-60 transition duration-1000"></div>
        <div className="relative h-full bg-[#0A0A1A]/90 border border-[#FF0055]/30 rounded-lg p-6 flex flex-col justify-between overflow-hidden">
           {/* Top Decorator */}
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[#FF0055] to-transparent opacity-50"></div>

           <div className="flex justify-between items-start mb-4">
             <div className="flex items-center gap-2 text-[#FF0055]">
               <ShieldAlert className="w-5 h-5" />
               <span className="font-mono font-bold tracking-wider">SHADOW_AGENT</span>
             </div>
             <span className="text-xs font-mono text-[#FF0055]/70 border border-[#FF0055]/30 px-2 py-1 rounded">ANTITHESIS</span>
           </div>

           <div className="h-24 font-mono text-sm text-rose-100/90 leading-relaxed mb-4">
             <span className="text-[#FF0055] mr-2">{'>'}</span>
             <TypewriterEffect 
               key={`shadow-${shadowIndex}`} 
               text={SHADOW_MONOLOGUE[shadowIndex]} 
               cursorColor="#FF0055"
             />
           </div>

           {/* Metrics */}
           <div className="mt-auto">
             <div className="flex justify-between text-xs font-mono text-gray-400 mb-1">
               <span>REGRET_ANALYSIS</span>
               <span className="text-[#FF0055]">32%</span>
             </div>
             <div className="w-full bg-gray-900 rounded-full h-1.5 overflow-hidden flex justify-end">
               <motion.div 
                 initial={{ width: 0 }}
                 animate={{ width: '32%' }}
                 transition={{ duration: 1.5, ease: "easeOut" }}
                 className="h-full bg-[#FF0055] shadow-[0_0_10px_#FF0055]"
               />
             </div>
           </div>
        </div>
      </motion.div>

      {/* Terminal / Synthesis Output */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="lg:col-span-12"
      >
        <div className="w-full bg-black/60 border-t border-b border-gray-800 backdrop-blur-sm p-4 font-mono text-sm flex flex-col md:flex-row gap-4 items-center">
          <Terminal className="w-4 h-4 text-gray-500" />
          <div className="flex-1 flex items-center gap-3 overflow-hidden whitespace-nowrap">
            <span className="text-purple-400">SYNTHESIS_ENGINE:</span>
            <span className="text-gray-300">Reconciling vectors... Hedged position approved. Order routed via dark pool.</span>
          </div>
          <div className="hidden md:flex gap-4 text-xs text-gray-500">
             <span>LATENCY: 12ms</span>
             <span>EXECUTION: OPTIMAL</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};