import React from 'react';
import { DialecticWarRoom } from './DialecticWarRoom';
import { EvolutionaryOptimization } from './EvolutionaryOptimization';
import { ResilienceMonitor } from './ResilienceMonitor';

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0A0A1A] text-gray-200 p-4 md:p-8 font-sans selection:bg-cyan-500/30 selection:text-white">

      {/* Top Navigation / Breadcrumb Placeholder (matching existing app style) */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <div className="w-2 h-8 bg-[#00FFFF] shadow-[0_0_10px_#00FFFF]"></div>
            SELF_PLAY_LEARNING_LOOP
          </h1>
          <p className="text-gray-500 text-sm font-mono mt-1 ml-5">
            {/* ALPHA_AXIOM // V.2.4.0 // ACTIVE */}
            ALPHA_AXIOM // V.2.4.0 // ACTIVE
          </p>
        </div>
        <div className="flex gap-3">
          <button className="px-4 py-2 bg-gray-900 border border-gray-700 rounded hover:border-[#00FFFF] text-xs font-mono transition-colors">
            VIEW_LOGS
          </button>
          <button className="px-4 py-2 bg-[#00FFFF]/10 border border-[#00FFFF]/50 text-[#00FFFF] rounded hover:bg-[#00FFFF]/20 text-xs font-mono transition-all shadow-[0_0_10px_rgba(0,255,255,0.2)]">
            PAUSE_TRAINING
          </button>
        </div>
      </header>

      {/* Main Content Grid */}
      <main className="max-w-8xl mx-auto space-y-6">

        {/* Section 1: The Minds */}
        <section>
          <DialecticWarRoom />
        </section>

        {/* Section 2: The Evolution */}
        <section>
          <EvolutionaryOptimization />
        </section>

        {/* Section 3: The System */}
        <section>
          <ResilienceMonitor />
        </section>

      </main>
    </div>
  );
};