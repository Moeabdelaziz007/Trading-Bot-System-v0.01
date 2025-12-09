import React from 'react';
import { TRENDING_TOPICS } from '../constants';
import { TrendingUp, Minus, Zap } from 'lucide-react';

export const TrendingTopics: React.FC = () => {
  return (
    <div className="glass-panel p-6 rounded-2xl">
      <div className="flex items-center gap-2 mb-6">
        <div className="p-1.5 bg-axiom-orange/10 rounded-lg">
             <TrendingUp className="w-5 h-5 text-axiom-orange" />
        </div>
        <h2 className="text-lg font-semibold">Trending Topics</h2>
      </div>

      <div className="space-y-6">
        {TRENDING_TOPICS.map((topic) => {
          let progressColor = '';
          let Icon = Minus;
          let iconColor = '';
          
          if (topic.sentiment === 'High Sentiment') {
            progressColor = 'bg-gradient-to-r from-yellow-500 to-axiom-orange';
            Icon = TrendingUp;
            iconColor = 'text-axiom-primary';
          } else if (topic.sentiment === 'Neutral') {
            progressColor = 'bg-gradient-to-r from-blue-600 to-axiom-secondary';
            Icon = Minus;
            iconColor = 'text-gray-400';
          } else {
            progressColor = 'bg-gradient-to-r from-purple-500 to-pink-500';
            Icon = Zap;
            iconColor = 'text-axiom-tertiary';
          }

          return (
            <div key={topic.tag} className="group">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-bold text-white group-hover:text-axiom-secondary transition-colors">{topic.tag}</h3>
                  <div className="text-xs text-gray-400 flex items-center gap-1 mt-0.5">
                    <span>{topic.mentions} mentions</span>
                    <span>•</span>
                    <span className={topic.sentiment === 'High Sentiment' ? 'text-axiom-orange' : 'text-gray-300'}>{topic.sentiment}</span>
                  </div>
                </div>
                <Icon className={`w-4 h-4 ${iconColor}`} />
              </div>
              
              <div className="h-1.5 w-full bg-white/10 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${progressColor}`} 
                  style={{ width: `${topic.score}%` }}
                />
              </div>
              <div className="flex justify-end mt-1">
                 <span className="text-[10px] text-gray-500 font-mono">{topic.score}/100</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
