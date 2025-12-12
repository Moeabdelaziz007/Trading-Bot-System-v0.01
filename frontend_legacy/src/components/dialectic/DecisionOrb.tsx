import React from 'react';

interface DecisionOrbProps {
  decision: string | null;
  status?: 'thinking' | 'decided';
}

export const DecisionOrb: React.FC<DecisionOrbProps> = ({ 
  decision, 
  status = 'thinking' 
}) => {
  const isDecided = status === 'decided' && decision;
  const orbColor = isDecided 
    ? decision.includes('LONG') 
      ? 'bg-gradient-to-br from-green-500 to-emerald-600' 
      : decision.includes('SHORT') 
        ? 'bg-gradient-to-br from-red-500 to-orange-600' 
        : 'bg-gradient-to-br from-yellow-500 to-amber-600'
    : 'bg-gradient-to-br from-purple-500 to-indigo-600';
  
  const pulseClass = !isDecided ? 'animate-pulse' : '';

  return (
    <div className="flex flex-col items-center">
      <div className={`w-48 h-48 rounded-full ${orbColor} ${pulseClass} flex items-center justify-center shadow-2xl transition-all duration-500 transform hover:scale-105`}>
        <div className="bg-black/20 rounded-full w-44 h-44 flex items-center justify-center">
          <div className="bg-black/30 rounded-full w-40 h-40 flex items-center justify-center">
            {isDecided ? (
              <div className="text-center p-4">
                <p className="font-mono text-white text-lg font-bold">{decision}</p>
                <p className="text-xs text-gray-300 mt-2">SYNTHESIS_LOCKED</p>
              </div>
            ) : (
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin mx-auto"></div>
                <p className="font-mono text-white text-sm mt-4">PROCESSING</p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="mt-6 text-center">
        <h3 className="font-mono text-cyan-400 text-lg">DIALECTIC_SYNTHESIS</h3>
        <p className="text-xs text-gray-500 mt-1">{/* // RESOLUTION_ENGINE */}</p>      </div>
    </div>
  );
};