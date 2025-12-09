import { BotScore, Transaction, TrendingTopic, Pattern, ChartPoint } from './types';

export const BOT_SCORES: BotScore[] = [
  { name: 'Alpha Bot', score: 84, color: '#00FF88' }, // Green
  { name: 'Quantum Core', score: 95, color: '#00D9FF' }, // Cyan
  { name: 'Sniper', score: 65, color: '#FFD700' }, // Gold
];

export const TRANSACTIONS: Transaction[] = [
  { asset: 'SOL', type: 'LONG', price: 648.16, status: 'Pending' },
  { asset: 'BTC', type: 'LONG', price: 98526.34, status: 'Pending' },
  { asset: 'DOT', type: 'SHORT', price: 484.64, status: 'Pending' },
  { asset: 'AVAX', type: 'LONG', price: 66.90, status: 'Pending' },
];

export const TRENDING_TOPICS: TrendingTopic[] = [
  { tag: '#AI_Regulation', mentions: '24.5k', sentiment: 'High Sentiment', score: 85, trend: 'up' },
  { tag: '#ETH_ETF', mentions: '12.1k', sentiment: 'Neutral', score: 60, trend: 'flat' },
  { tag: '#SolanaSaga', mentions: '8.2k', sentiment: 'Volatile', score: 50, trend: 'volatile' },
];

export const PATTERNS: Pattern[] = [
  { asset: 'LTC', name: 'Litecoin Reversal', timeframe: '4H', confidence: 92, type: 'Reversal', action: 'Execute Bot' },
  { asset: 'XRP', name: 'Triangle Breakout', timeframe: '1D', confidence: 88, type: 'Breakout', action: 'Execute Bot' },
];

// Generate some realistic looking price data for BTC
export const CHART_DATA: ChartPoint[] = Array.from({ length: 40 }, (_, i) => {
  const base = 98000;
  const random = Math.random() * 800 - 400;
  // Make it look like a trend
  const trend = i * 20; 
  return {
    time: `${14 + Math.floor(i/4)}:${(i%4)*15}`,
    value: base + trend + random
  };
});
