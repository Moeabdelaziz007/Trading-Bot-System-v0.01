'use client';

import { useRouter } from 'next/navigation';
import { useDialecticStream } from '@/hooks/useDialecticStream';

export const ActiveDialecticStatus = () => {
  const router = useRouter();
  const { coreText, shadowText, decision } = useDialecticStream();

  const handleOpenWarRoom = () => {
    router.push('/dashboard/self-play');
  };

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-6 backdrop-blur-sm transition-all duration-300 hover:shadow-lg">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-mono text-lg text-cyan-400">ACTIVE_DIALECTIC_STATUS</h3>
          <p className="text-xs text-gray-500 mt-1">{/* // REAL_TIME_CONFLICT_MONITOR */}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-xs font-mono text-green-400">LIVE</span>
        </div>
      </div>

      <div className="space-y-4 mt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span className="text-sm font-mono text-blue-400">CORE_AGENT</span>
          </div>
          <span className="text-xs text-gray-500">CONFIDENCE: 84%</span>
        </div>
        
        <div className="pl-5">
          <p className="text-gray-300 text-sm font-mono">
            {coreText || "Analyzing market conditions..."}
          </p>
        </div>
        
        <div className="flex items-center justify-between mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-500"></div>
            <span className="text-sm font-mono text-red-400">SHADOW_AGENT</span>
          </div>
          <span className="text-xs text-gray-500">REGRET: 32%</span>
        </div>
        
        <div className="pl-5">
          <p className="text-gray-300 text-sm font-mono">
            {shadowText || "Challenging core assumptions..."}
          </p>
        </div>
        
        {decision && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <p className="font-mono text-cyan-400">{decision}</p>
          </div>
        )}
      </div>

      <div className="mt-6">
        <button
          onClick={handleOpenWarRoom}
          className="w-full py-2 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg font-mono text-sm hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 transform hover:scale-[1.02]"
        >
          OPEN_WAR_ROOM
        </button>
      </div>
    </div>
  );
};