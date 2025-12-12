import React from 'react';

export const FitnessChart: React.FC = () => {
  // Mock data for the fitness landscape
  const fitnessData = [
    { generation: 1, fitness: 65 },
    { generation: 5, fitness: 72 },
    { generation: 10, fitness: 78 },
    { generation: 15, fitness: 84 },
    { generation: 20, fitness: 89 },
    { generation: 25, fitness: 92 },
    { generation: 30, fitness: 95 },
  ];

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-900/50 p-6 backdrop-blur-sm">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="font-mono text-lg text-cyan-400">FITNESS_LANDSCAPE</h3>
          <p className="text-xs text-gray-500 mt-1">{/* // EVOLUTIONARY_PERFORMANCE */}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">GENERATION</p>
          <p className="font-mono text-cyan-400">30</p>
        </div>
      </div>
      
      <div className="h-64 flex items-end space-x-2 mt-8">
        {fitnessData.map((point, index) => (
          <div key={index} className="flex flex-col items-center flex-1">
            <div 
              className="w-full bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t transition-all duration-500 hover:opacity-75"
              style={{ height: `${point.fitness}%` }}
            ></div>
            <p className="text-xs text-gray-500 mt-2 font-mono">{point.generation}</p>
          </div>
        ))}
      </div>
      
      <div className="mt-8 pt-6 border-t border-gray-700">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-xs text-gray-500">CURRENT_BEST</p>
            <p className="font-mono text-green-400">95.2%</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500">AVG_POPULATION</p>
            <p className="font-mono text-cyan-400">82.7%</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-500">DIVERGENCE</p>
            <p className="font-mono text-yellow-400">12.5%</p>
          </div>
        </div>
      </div>
    </div>
  );
};