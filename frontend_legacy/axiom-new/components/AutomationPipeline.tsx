import React from 'react';
import { Database, BrainCircuit, ShoppingCart } from 'lucide-react';

export const AutomationPipeline: React.FC = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl relative">
      <div className="flex items-center gap-2 mb-8">
         <div className="p-1.5 bg-white/5 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
         </div>
        <h2 className="text-lg font-semibold">Automation Pipeline</h2>
      </div>

      <div className="relative pl-4">
        {/* Connecting Line */}
        <div className="absolute left-[27px] top-4 bottom-8 w-[2px] bg-gradient-to-b from-axiom-secondary via-axiom-purple to-gray-800 opacity-30"></div>

        {/* Step 1 */}
        <div className="relative mb-8 group">
          <div className="flex items-start gap-4">
            <div className="z-10 w-14 h-14 rounded-full bg-[#1A1A2E] border border-axiom-secondary flex items-center justify-center shadow-[0_0_15px_rgba(0,217,255,0.3)]">
              <Database className="w-6 h-6 text-axiom-secondary" />
            </div>
            <div className="flex-1 bg-white/5 border border-axiom-secondary/30 rounded-lg p-4 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-2">
                 <span className="text-[10px] uppercase tracking-wider text-axiom-secondary animate-pulse">Running</span>
               </div>
               <div className="absolute bottom-0 left-0 h-[2px] bg-axiom-secondary w-full animate-progress-indeterminate"></div>
              <h3 className="font-bold text-white mb-1">Data Ingestion</h3>
              <p className="text-sm text-gray-400">Processing websocket streams...</p>
            </div>
          </div>
        </div>

        {/* Step 2 */}
        <div className="relative mb-8 group">
          <div className="flex items-start gap-4">
            <div className="z-10 w-14 h-14 rounded-full bg-[#1A1A2E] border border-axiom-purple flex items-center justify-center shadow-[0_0_15px_rgba(139,92,246,0.3)]">
              <BrainCircuit className="w-6 h-6 text-axiom-purple" />
            </div>
            <div className="flex-1 bg-white/5 border border-axiom-purple/30 rounded-lg p-4 relative overflow-hidden">
                <div className="absolute top-0 right-0 p-2">
                 <span className="text-[10px] uppercase tracking-wider text-axiom-purple">Processing</span>
               </div>
               <div className="absolute bottom-0 left-0 h-[2px] bg-axiom-purple w-3/4"></div>
              <h3 className="font-bold text-white mb-1">AI Analysis</h3>
              <p className="text-sm text-gray-400">Calculating probability matrices...</p>
            </div>
          </div>
        </div>

        {/* Step 3 */}
        <div className="relative group">
          <div className="flex items-start gap-4">
            <div className="z-10 w-14 h-14 rounded-full bg-[#1A1A2E] border border-gray-700 flex items-center justify-center">
              <ShoppingCart className="w-6 h-6 text-gray-500" />
            </div>
            <div className="flex-1 bg-white/5 border border-white/5 rounded-lg p-4">
              <div className="absolute top-0 right-0 p-2">
                 <span className="text-[10px] uppercase tracking-wider text-gray-500">Waiting</span>
               </div>
              <h3 className="font-bold text-gray-400 mb-1">Execution</h3>
              <p className="text-sm text-gray-600">Waiting for signal trigger...</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
