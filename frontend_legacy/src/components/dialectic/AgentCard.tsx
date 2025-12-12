import React from 'react';

interface AgentCardProps {
  type: 'core' | 'shadow';
  title: string;
  text: string;
  confidence?: number;
  regret?: number;
}

export const AgentCard: React.FC<AgentCardProps> = ({ 
  type, 
  title, 
  text, 
  confidence, 
  regret 
}) => {
  const isCore = type === 'core';
  const bgColor = isCore ? 'bg-blue-900/50' : 'bg-red-900/50';
  const borderColor = isCore ? 'border-blue-500' : 'border-red-500';
  const textColor = isCore ? 'text-blue-400' : 'text-red-400';
  const metricLabel = isCore ? 'CONFIDENCE' : 'REGRET';
  const metricValue = isCore ? confidence : regret;

  return (
    <div className={`rounded-xl border ${borderColor} ${bgColor} p-6 backdrop-blur-sm transition-all duration-300 hover:shadow-lg`}>
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className={`font-mono text-lg ${textColor}`}>{title}</h3>
          <p className="text-xs text-gray-500 mt-1">
            {/* // {isCore ? 'THESIS_AGENT' : 'ANTITHESIS_AGENT'} */}
          </p>
        </div>
        {metricValue !== undefined && (
          <div className="text-right">
            <p className="text-xs text-gray-500">{metricLabel}</p>
            <p className={`font-mono ${textColor}`}>{metricValue}%</p>
          </div>
        )}
      </div>
      
      <div className="min-h-[120px]">
        <p className="text-gray-300 text-sm font-mono leading-relaxed">
          {text || (isCore ? "Analyzing market conditions..." : "Challenging core assumptions...")}
        </p>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isCore ? 'bg-blue-500' : 'bg-red-500'} animate-pulse`}></div>
          <span className="text-xs text-gray-500 font-mono">ACTIVE</span>
        </div>
      </div>
    </div>
  );
};