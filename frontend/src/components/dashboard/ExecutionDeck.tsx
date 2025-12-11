'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertTriangle, DollarSign } from 'lucide-react';
import { useTradeExecution } from '../hooks/useTradeExecution';

export const ExecutionDeck: React.FC = () => {
  const { executeTrade, killSwitch, executing, error } = useTradeExecution();
  const [symbol, setSymbol] = useState('EURUSD');
  const [amount, setAmount] = useState(1000);
  const [showKillConfirm, setShowKillConfirm] = useState(false);

  const handleBuy = async () => {
    try {
      await executeTrade({
        symbol,
        side: 'BUY',
        amount
      });
    } catch (err) {
      console.error('Buy failed:', err);
    }
  };

  const handleSell = async () => {
    try {
      await executeTrade({
        symbol,
        side: 'SELL',
        amount
      });
    } catch (err) {
      console.error('Sell failed:', err);
    }
  };

  const handleKillSwitch = async () => {
    if (!showKillConfirm) {
      setShowKillConfirm(true);
      setTimeout(() => setShowKillConfirm(false), 5000);
      return;
    }

    try {
      await killSwitch();
      setShowKillConfirm(false);
    } catch (err) {
      console.error('Kill switch failed:', err);
    }
  };

  return (
    <div className="w-full bg-axiom-surface/50 backdrop-blur-glass border border-glass-border rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <DollarSign className="w-6 h-6 text-axiom-neon-gold" />
        <h2 className="text-xl font-mono font-bold text-white tracking-tight">
          EXECUTION_DECK
        </h2>
      </div>

      {/* Symbol & Amount Input */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-xs text-text-muted font-mono mb-2">
            SYMBOL
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            className="w-full bg-axiom-bg border border-glass-border rounded-lg px-4 py-2 text-white font-mono focus:outline-none focus:border-axiom-neon-cyan transition-colors"
            placeholder="EURUSD"
            data-testid="symbol-input"
          />
        </div>

        <div>
          <label className="block text-xs text-text-muted font-mono mb-2">
            AMOUNT ($)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(Number(e.target.value))}
            className="w-full bg-axiom-bg border border-glass-border rounded-lg px-4 py-2 text-white font-mono focus:outline-none focus:border-axiom-neon-cyan transition-colors"
            placeholder="1000"
            data-testid="amount-input"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* BUY Button */}
        <motion.button
          data-testid="buy-button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleBuy}
          disabled={executing}
          className="relative group bg-axiom-neon-green/10 border-2 border-axiom-neon-green hover:bg-axiom-neon-green/20 rounded-lg p-6 transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
        >
          <div className="absolute inset-0 bg-axiom-neon-green/0 group-hover:bg-axiom-neon-green/10 transition-all"></div>
          <div className="relative flex flex-col items-center gap-2">
            <TrendingUp className="w-8 h-8 text-axiom-neon-green" />
            <span className="text-xl font-mono font-bold text-axiom-neon-green">
              BUY
            </span>
            <span className="text-xs text-text-muted font-mono">
              LONG POSITION
            </span>
          </div>
        </motion.button>

        {/* SELL Button */}
        <motion.button
          data-testid="sell-button"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleSell}
          disabled={executing}
          className="relative group bg-axiom-neon-red/10 border-2 border-axiom-neon-red hover:bg-axiom-neon-red/20 rounded-lg p-6 transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
        >
          <div className="absolute inset-0 bg-axiom-neon-red/0 group-hover:bg-axiom-neon-red/10 transition-all"></div>
          <div className="relative flex flex-col items-center gap-2">
            <TrendingDown className="w-8 h-8 text-axiom-neon-red" />
            <span className="text-xl font-mono font-bold text-axiom-neon-red">
              SELL
            </span>
            <span className="text-xs text-text-muted font-mono">
              SHORT POSITION
            </span>
          </div>
        </motion.button>
      </div>

      {/* Kill Switch */}
      <motion.button
        data-testid="kill-switch-button"
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
        onClick={handleKillSwitch}
        disabled={executing}
        className={`w-full border-2 rounded-lg p-4 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${showKillConfirm
            ? 'bg-axiom-neon-red/20 border-axiom-neon-red animate-pulse'
            : 'bg-axiom-bg border-gray-600 hover:border-axiom-neon-red'
          }`}
      >
        <div className="flex items-center justify-center gap-3">
          <AlertTriangle className={`w-5 h-5 ${showKillConfirm ? 'text-axiom-neon-red' : 'text-gray-400'}`} />
          <span className={`font-mono font-bold ${showKillConfirm ? 'text-axiom-neon-red' : 'text-gray-400'}`}>
            {showKillConfirm ? 'CONFIRM: FLATTEN ALL POSITIONS' : 'KILL SWITCH'}
          </span>
        </div>
      </motion.button>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 bg-axiom-neon-red/10 border border-axiom-neon-red rounded-lg p-3"
        >
          <p className="text-xs font-mono text-axiom-neon-red">
            ⚠️ {error}
          </p>
        </motion.div>
      )}

      {/* Executing Indicator */}
      {executing && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center gap-2 text-axiom-neon-cyan"
        >
          <div className="w-2 h-2 rounded-full bg-axiom-neon-cyan animate-pulse"></div>
          <span className="text-xs font-mono">EXECUTING...</span>
        </motion.div>
      )}
    </div>
  );
};