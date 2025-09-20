export interface ForexPrice {
  symbol: string;
  price: number;
  change24h: number;
  changePercent24h: number;
  timestamp: string;
  source: string;
}

export interface TradingSignal {
  symbol: string;
  direction: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  strategy: string;
  price: number;
  reason: string;
  timestamp: string;
  targetPrice?: number;
  stopLoss?: number;
}

export interface NewsItem {
  title: string;
  description: string;
  url: string;
  publishedAt: string;
  impact: 'high' | 'medium' | 'low';
  currency?: string;
}

export interface UserSession {
  userId: number;
  username?: string;
  firstName?: string;
  lastActivity: Date;
  preferredPairs: string[];
  currentState?: 'waiting_for_pair_input' | 'idle';
}

export interface BotConfig {
  token: string;
  forexApiUrl: string;
  newsApiUrl?: string;
  updateInterval: number;
}