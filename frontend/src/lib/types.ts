// Types for Dashboard Components

export interface BotScore {
  name: string;
  score: number;
  color: string;
}

export interface Transaction {
  asset: string;
  type: 'LONG' | 'SHORT';
  price: number;
  amount?: number;
  pnl?: number;
  status: string;
}

export interface TrendingTopic {
  tag: string;
  mentions: string;
  sentiment: string;
  score: number;
  trend: 'up' | 'flat' | 'volatile' | 'down';
}

export interface Pattern {
  asset: string;
  name: string;
  timeframe: string;
  confidence: number;
  type: string;
  action: string;
}

export interface ChartPoint {
  time: string;
  value: number;
}

export interface PipelineStep {
  id: string;
  name: string;
  description: string;
  status: 'running' | 'processing' | 'waiting' | 'complete';
  progress?: number;
}

export interface DashboardData {
  account: {
    balance: number;
    equity: number;
  };
  positions: Transaction[];
  engines: {
    aexi: number;
    dream: number;
    last_signal: string | null;
  };
  bots: BotScore[];
  timestamp: string;
}
