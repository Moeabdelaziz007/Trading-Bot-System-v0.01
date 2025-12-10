'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { GitBranch, Plus } from 'lucide-react';
import { StrategyBlock, AddStrategyBlock, StrategyRule } from './StrategyBlock';

const presetRules: StrategyRule[] = [
  {
    id: '1',
    condition: 'RSI > 70 AND MACD Crosses Down',
    action: 'SELL 50%',
    color: 'red'
  },
  {
    id: '2',
    condition: 'News Sentiment < -0.5',
    action: 'CLOSE ALL POSITIONS',
    color: 'purple'
  },
  {
    id: '3',
    condition: 'EMA(9) Crosses Above EMA(21)',
    action: 'BUY 1.5x',
    color: 'green'
  },
  {
    id: '4',
    condition: 'AEXI Score > 80',
    action: 'LONG with 2x Leverage',
    color: 'cyan'
  },
];

interface StrategyEditorProps {
  rules: StrategyRule[];
  onChange: (rules: StrategyRule[]) => void;
}

export const StrategyEditor: React.FC<StrategyEditorProps> = ({ rules, onChange }) => {
  const [showPresets, setShowPresets] = useState(false);

  const handleAddRule = () => {
    setShowPresets(true);
  };

  const handleSelectPreset = (preset: StrategyRule) => {
    const newRule = {
      ...preset,
      id: `${Date.now()}-${Math.random()}`
    };
    onChange([...rules, newRule]);
    setShowPresets(false);
  };

  const handleRemoveRule = (id: string) => {
    onChange(rules.filter(rule => rule.id !== id));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-glass-border">
        <div className="flex items-center gap-3">
          <GitBranch className="w-6 h-6 text-axiom-neon-purple" />
          <h2 className="text-xl font-mono font-bold text-white tracking-tight">
            STRATEGY_GENE_EDITOR
          </h2>
        </div>
        <div className="px-3 py-1 bg-axiom-neon-cyan/10 border border-axiom-neon-cyan/30 rounded-lg">
          <span className="text-xs font-mono text-axiom-neon-cyan font-bold">
            {rules.length} RULES
          </span>
        </div>
      </div>

      {/* Info */}
      <div className="bg-axiom-neon-blue/5 border border-axiom-neon-blue/30 rounded-lg p-4">
        <p className="text-xs font-mono text-axiom-neon-blue">
          💡 Build your agent's decision logic by adding conditional rules. Each rule defines when and how your agent should act.
        </p>
      </div>

      {/* Rules List */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
        <AnimatePresence>
          {rules.map((rule, index) => (
            <StrategyBlock
              key={rule.id}
              rule={rule}
              onRemove={handleRemoveRule}
              index={index}
            />
          ))}
        </AnimatePresence>

        {/* Add Button */}
        <AddStrategyBlock onAdd={handleAddRule} />
      </div>

      {/* Preset Selection Modal */}
      <AnimatePresence>
        {showPresets && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowPresets(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-axiom-surface border border-glass-border rounded-xl p-6 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
            >
              <h3 className="text-lg font-mono font-bold text-white mb-4">
                SELECT_PRESET_RULE
              </h3>

              <div className="space-y-3">
                {presetRules.map((preset) => (
                  <motion.button
                    key={preset.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleSelectPreset(preset)}
                    className="w-full text-left"
                  >
                    <StrategyBlock
                      rule={preset}
                      onRemove={() => {}}
                      index={0}
                    />
                  </motion.button>
                ))}
              </div>

              <button
                onClick={() => setShowPresets(false)}
                className="mt-4 w-full py-3 bg-axiom-bg border border-glass-border rounded-lg text-text-muted font-mono hover:border-axiom-neon-cyan transition-colors"
              >
                CANCEL
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(255, 255, 255, 0.05);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 255, 255, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 255, 255, 0.5);
        }
      `}</style>
    </div>
  );
};