'use client';

import { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

export interface TradeRequest {
  symbol: string;
  side: 'BUY' | 'SELL';
  amount: number;
  stopLoss?: number;
  takeProfit?: number;
}

export const useTradeExecution = () => {
  const [executing, setExecuting] = useState(false);
  const [lastTrade, setLastTrade] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const executeTrade = async (trade: TradeRequest) => {
    try {
      setExecuting(true);
      setError(null);

      const response = await axios.post(`${API_BASE}/api/trade`, {
        symbol: trade.symbol,
        side: trade.side,
        amount: trade.amount,
        stop_loss: trade.stopLoss,
        take_profit: trade.takeProfit,
      });

      setLastTrade(response.data);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Trade execution failed';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setExecuting(false);
    }
  };

  const killSwitch = async () => {
    try {
      setExecuting(true);
      const response = await axios.post(`${API_BASE}/api/flatten`);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || 'Kill switch failed';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setExecuting(false);
    }
  };

  return {
    executeTrade,
    killSwitch,
    executing,
    lastTrade,
    error
  };
};