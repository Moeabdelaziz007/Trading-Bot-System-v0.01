export interface BotScore {
  name: string;
  score: number;
  color: string;
}

export interface Transaction {
  asset: string;
  type: 'LONG' | 'SHORT';
  price: number;
  amount?: string;
  pnl?: string;
  status: 'Pending' | 'Completed' | 'Failed';
}

export interface TrendingTopic {
  tag: string;
  mentions: string;
  sentiment: 'High Sentiment' | 'Neutral' | 'Volatile';
  score: number;
  trend: 'up' | 'down' | 'flat' | 'volatile';
}

export interface Pattern {
  asset: string;
  name: string;
  timeframe: string;
  confidence: number;
  type: 'Reversal' | 'Breakout';
  action: 'Execute Bot';
}

export interface ChartPoint {
  time: string;
  value: number;
}
