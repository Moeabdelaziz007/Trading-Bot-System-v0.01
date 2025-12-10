'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { GripVertical, X, Plus } from 'lucide-react';

export interface StrategyRule {
  id: string;
  condition: string;
  action: string;
  color: string;
}

interface StrategyBlockProps {
  rule: StrategyRule;
  onRemove: (id: string) => void;
  onEdit?: (id: string) => void;
  index: number;
}

export const StrategyBlock: React.FC<StrategyBlockProps> = ({
  rule,
  onRemove,
  onEdit,
  index
}) => {
  const colorMap: Record<string, string> = {
    cyan: 'border-axiom-neon-cyan bg-axiom-neon-cyan/5',
    purple: 'border-axiom-neon-purple bg-axiom-neon-purple/5',
    green: 'border-axiom-neon-green bg-axiom-neon-green/5',
    red: 'border-axiom-neon-red bg-axiom-neon-red/5',
    gold: 'border-axiom-neon-gold bg-axiom-neon-gold/5',
    blue: 'border-axiom-neon-blue bg-axiom-neon-blue/5',
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ delay: index * 0.05 }}
      className={`group relative border-2 ${colorMap[rule.color] || colorMap.cyan} rounded-lg p-4 hover:shadow-lg transition-all cursor-move`}
    >
      {/* Drag Handle */}
      <div className="absolute left-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
        <GripVertical className="w-4 h-4 text-text-muted" />
      </div>

      {/* Remove Button */}
      <button
        onClick={() => onRemove(rule.id)}
        className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:bg-axiom-neon-red/20 rounded"
      >
        <X className="w-4 h-4 text-axiom-neon-red" />
      </button>

      {/* Content */}
      <div className="pl-6 pr-8">
        <div className="space-y-2">
          {/* Condition */}
          <div>
            <span className="text-xs font-mono text-text-muted uppercase">IF</span>
            <p className="text-sm font-mono text-white mt-1">
              {rule.condition}
            </p>
          </div>

          {/* Arrow */}
          <div className="flex items-center gap-2">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-glass-border to-transparent"></div>
            <span className="text-xs font-mono text-text-muted">THEN</span>
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-glass-border to-transparent"></div>
          </div>

          {/* Action */}
          <div>
            <span className="text-xs font-mono text-text-muted uppercase">ACTION</span>
            <p className={`text-sm font-mono font-bold mt-1 ${
              rule.action.includes('BUY') || rule.action.includes('LONG') 
                ? 'text-axiom-neon-green'
                : rule.action.includes('SELL') || rule.action.includes('SHORT')
                ? 'text-axiom-neon-red'
                : 'text-axiom-neon-cyan'
            }`}>
              {rule.action}
            </p>
          </div>
        </div>
      </div>

      {/* Glow Effect */}
      <div className={`absolute inset-0 rounded-lg opacity-0 group-hover:opacity-20 transition-opacity pointer-events-none`}
        style={{
          boxShadow: `0 0 20px ${rule.color === 'cyan' ? '#00FFFF' : rule.color === 'purple' ? '#A855F7' : rule.color === 'green' ? '#22C55E' : '#3B82F6'}`
        }}
      ></div>
    </motion.div>
  );
};

interface AddStrategyBlockProps {
  onAdd: () => void;
}

export const AddStrategyBlock: React.FC<AddStrategyBlockProps> = ({ onAdd }) => {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onAdd}
      className="w-full border-2 border-dashed border-glass-border hover:border-axiom-neon-cyan rounded-lg p-6 transition-all group"
    >
      <div className="flex flex-col items-center gap-2">
        <div className="w-12 h-12 rounded-full bg-axiom-neon-cyan/10 flex items-center justify-center group-hover:bg-axiom-neon-cyan/20 transition-all">
          <Plus className="w-6 h-6 text-axiom-neon-cyan" />
        </div>
        <span className="text-sm font-mono text-text-muted group-hover:text-axiom-neon-cyan transition-colors">
          ADD_LOGIC_BLOCK
        </span>
      </div>
    </motion.button>
  );
};