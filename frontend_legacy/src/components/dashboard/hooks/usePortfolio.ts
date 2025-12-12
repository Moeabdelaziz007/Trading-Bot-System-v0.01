'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'https://trading-brain-v1.amrikyy1.workers.dev';

export interface Position {
  symbol: string;
  side: 'LONG' | 'SHORT';
  quantity: number;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
}

export interface PortfolioData {
  balance: number;
  equity: number;
  pnl: number;
  pnlPercent: number;
  positions: Position[];
  todayPnL: number;
  winRate: number;
}

export const usePortfolio = () => {
  const [portfolio, setPortfolio] = useState<PortfolioData>({
    balance: 10000,
    equity: 10250,
    pnl: 250,
    pnlPercent: 2.5,
    positions: [],
    todayPnL: 125,
    winRate: 68.5
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API_BASE}/api/portfolio`);
        
        if (response.data) {
          setPortfolio(response.data);
        }
      } catch (error) {
        console.error('Failed to fetch portfolio:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
    const interval = setInterval(fetchPortfolio, 5000); // Update every 5s

    return () => clearInterval(interval);
  }, []);

  return { portfolio, loading };
};