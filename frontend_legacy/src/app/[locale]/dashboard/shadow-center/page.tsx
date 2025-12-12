'use client';

import { AgentCard } from '@/components/dialectic/AgentCard';
import { DecisionOrb } from '@/components/dialectic/DecisionOrb';
import { FitnessChart } from '@/components/dialectic/FitnessChart';
import { useDialecticStream } from '@/hooks/useDialecticStream';

export default function ShadowCenterPage() {
  const { coreText, shadowText, decision } = useDialecticStream();

  return (
    <div className="p-6 space-y-6 bg-black min-h-screen text-white">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-mono text-cyan-400">SELF_PLAY_LEARNING_LOOP</h1>
          <p className="text-xs text-gray-500">{/* // ALPHA_AXIOM // V.4.0 // ACTIVE */}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-xs font-mono">LIVE_INFERENCE</span>
        </div>
      </div>

      {/* Status Indicator */}
      <div className="flex items-center space-x-2 text-sm">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
          <span className="text-blue-400 font-mono">CORE_ACTIVE</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-red-500 rounded-full"></div>
          <span className="text-red-400 font-mono">SHADOW_ACTIVE</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
          <span className="text-purple-400 font-mono">SYNTHESIS_READY</span>
        </div>
      </div>

      {/* The War Room Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-center border border-gray-800 p-8 rounded-xl bg-gray-900/50 backdrop-blur-sm">
        
        {/* Thesis (Core) */}
        <AgentCard 
          type="core" 
          title="CORE_AGENT" 
          text={coreText} 
          confidence={84} 
        />

        {/* Synthesis (The Bridge) */}
        <div className="flex justify-center">
          <DecisionOrb decision={decision} status={decision ? "decided" : "thinking"} />
        </div>

        {/* Antithesis (Shadow) */}
        <AgentCard 
          type="shadow" 
          title="SHADOW_AGENT" 
          text={shadowText} 
          regret={32} 
        />
      </div>

      {/* Fitness Landscape */}
      <div className="mt-8">
        <FitnessChart />
      </div>

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-4 backdrop-blur-sm">
          <p className="text-xs text-gray-500">GENERATION</p>
          <p className="font-mono text-cyan-400 text-xl">30</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-4 backdrop-blur-sm">
          <p className="text-xs text-gray-500">POPULATION_SIZE</p>
          <p className="font-mono text-cyan-400 text-xl">128</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-4 backdrop-blur-sm">
          <p className="text-xs text-gray-500">MUTATION_RATE</p>
          <p className="font-mono text-cyan-400 text-xl">0.075</p>
        </div>
        <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-4 backdrop-blur-sm">
          <p className="text-xs text-gray-500">BEST_FITNESS</p>
          <p className="font-mono text-green-400 text-xl">95.2%</p>
        </div>
      </div>
    </div>
  );
}