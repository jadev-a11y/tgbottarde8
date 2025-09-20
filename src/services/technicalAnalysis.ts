import { ForexPrice, TradingSignal } from '../types';

export interface PriceData {
  close: number;
  high: number;
  low: number;
  volume?: number;
  timestamp: string;
}

export interface IndicatorValues {
  rsi: number;
  macd: {
    macd: number;
    signal: number;
    histogram: number;
  };
  bollingerBands: {
    upper: number;
    middle: number;
    lower: number;
  };
  sma20: number;
  ema12: number;
  ema26: number;
}

export class TechnicalAnalysisService {
  private readonly RSI_PERIOD = 14;
  private readonly MACD_FAST = 12;
  private readonly MACD_SLOW = 26;
  private readonly MACD_SIGNAL = 9;
  private readonly BB_PERIOD = 20;
  private readonly BB_MULTIPLIER = 2;

  // Calculate RSI (Relative Strength Index)
  calculateRSI(prices: number[], period: number = this.RSI_PERIOD): number {
    if (prices.length < period + 1) {
      throw new Error('Недостаточно данных для расчета RSI');
    }

    const gains: number[] = [];
    const losses: number[] = [];

    // Calculate price changes
    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }

    // Calculate initial averages (SMA for first calculation)
    let avgGain = gains.slice(0, period).reduce((sum, gain) => sum + gain, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((sum, loss) => sum + loss, 0) / period;

    // Use Wilder's smoothing method for subsequent calculations
    for (let i = period; i < gains.length; i++) {
      avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
      avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;
    }

    if (avgLoss === 0) return 100;

    const rs = avgGain / avgLoss;
    const rsi = 100 - (100 / (1 + rs));

    return Number(rsi.toFixed(2));
  }

  // Calculate EMA (Exponential Moving Average)
  calculateEMA(prices: number[], period: number): number {
    if (prices.length < period) {
      throw new Error('Недостаточно данных для расчета EMA');
    }

    // Calculate initial SMA
    const sma = prices.slice(0, period).reduce((sum, price) => sum + price, 0) / period;

    // Calculate multiplier
    const multiplier = 2 / (period + 1);

    let ema = sma;

    // Calculate EMA for remaining prices
    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
    }

    return Number(ema.toFixed(5));
  }

  // Calculate MACD (Moving Average Convergence Divergence)
  calculateMACD(prices: number[]): { macd: number; signal: number; histogram: number } {
    if (prices.length < this.MACD_SLOW) {
      throw new Error('Недостаточно данных для расчета MACD');
    }

    const ema12 = this.calculateEMA(prices, this.MACD_FAST);
    const ema26 = this.calculateEMA(prices, this.MACD_SLOW);

    const macd = ema12 - ema26;

    // For signal line, we need to calculate EMA of MACD values
    // Since we only have current MACD, we'll simulate previous values
    const macdHistory = this.generateMACDHistory(prices);
    const signal = this.calculateEMA(macdHistory, this.MACD_SIGNAL);

    const histogram = macd - signal;

    return {
      macd: Number(macd.toFixed(5)),
      signal: Number(signal.toFixed(5)),
      histogram: Number(histogram.toFixed(5))
    };
  }

  private generateMACDHistory(prices: number[]): number[] {
    const macdHistory: number[] = [];

    for (let i = this.MACD_SLOW; i <= prices.length; i++) {
      const subset = prices.slice(0, i);
      if (subset.length >= this.MACD_SLOW) {
        const ema12 = this.calculateEMA(subset, this.MACD_FAST);
        const ema26 = this.calculateEMA(subset, this.MACD_SLOW);
        macdHistory.push(ema12 - ema26);
      }
    }

    return macdHistory;
  }

  // Calculate Bollinger Bands
  calculateBollingerBands(prices: number[], period: number = this.BB_PERIOD):
    { upper: number; middle: number; lower: number } {

    if (prices.length < period) {
      throw new Error('Недостаточно данных для расчета Bollinger Bands');
    }

    const subset = prices.slice(-period);

    // Calculate SMA (middle band)
    const sma = subset.reduce((sum, price) => sum + price, 0) / period;

    // Calculate standard deviation
    const variance = subset.reduce((sum, price) => sum + Math.pow(price - sma, 2), 0) / period;
    const stdDev = Math.sqrt(variance);

    const upper = sma + (stdDev * this.BB_MULTIPLIER);
    const lower = sma - (stdDev * this.BB_MULTIPLIER);

    return {
      upper: Number(upper.toFixed(5)),
      middle: Number(sma.toFixed(5)),
      lower: Number(lower.toFixed(5))
    };
  }

  // Calculate SMA (Simple Moving Average)
  calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) {
      throw new Error('Недостаточно данных для расчета SMA');
    }

    const subset = prices.slice(-period);
    const sma = subset.reduce((sum, price) => sum + price, 0) / period;

    return Number(sma.toFixed(5));
  }

  // Generate historical price data (mock for demonstration)
  generateHistoricalData(currentPrice: number, periods: number = 50): number[] {
    const prices: number[] = [];
    let price = currentPrice;

    // Generate realistic price movements
    for (let i = 0; i < periods; i++) {
      // Random walk with slight trend bias
      const change = (Math.random() - 0.5) * 0.02; // ±1% change
      const trendBias = i < periods / 2 ? -0.001 : 0.001; // Slight trend reversal

      price = price * (1 + change + trendBias);
      prices.unshift(Number(price.toFixed(5))); // Add to beginning
    }

    return prices;
  }

  // Main analysis function
  analyzePrice(currentPrice: number, symbol: string): IndicatorValues {
    const historicalPrices = this.generateHistoricalData(currentPrice, 50);

    const rsi = this.calculateRSI(historicalPrices);
    const macd = this.calculateMACD(historicalPrices);
    const bollingerBands = this.calculateBollingerBands(historicalPrices);
    const sma20 = this.calculateSMA(historicalPrices, 20);
    const ema12 = this.calculateEMA(historicalPrices, 12);
    const ema26 = this.calculateEMA(historicalPrices, 26);

    return {
      rsi,
      macd,
      bollingerBands,
      sma20,
      ema12,
      ema26
    };
  }

  // Generate trading signal based on multiple indicators
  generateTradingSignal(currentPrice: number, symbol: string): TradingSignal {
    const indicators = this.analyzePrice(currentPrice, symbol);

    // Multi-indicator signal generation
    const signals = this.evaluateIndicators(indicators, currentPrice);
    const finalSignal = this.combineSignals(signals);
    const confidence = this.calculateConfidence(signals, indicators);
    const strategy = this.determineStrategy(signals);
    const reason = this.generateReason(signals, indicators);

    // Calculate target and stop loss
    const { targetPrice, stopLoss } = this.calculateTradingLevels(
      currentPrice,
      finalSignal,
      confidence,
      indicators
    );

    return {
      symbol,
      direction: finalSignal,
      confidence: Math.round(confidence),
      strategy,
      price: currentPrice,
      reason,
      timestamp: new Date().toISOString(),
      targetPrice,
      stopLoss
    };
  }

  private evaluateIndicators(indicators: IndicatorValues, currentPrice: number) {
    return {
      rsi: this.evaluateRSI(indicators.rsi),
      macd: this.evaluateMACD(indicators.macd),
      bollinger: this.evaluateBollingerBands(indicators.bollingerBands, currentPrice),
      trend: this.evaluateTrend(indicators, currentPrice)
    };
  }

  private evaluateRSI(rsi: number): 'BUY' | 'SELL' | 'NEUTRAL' {
    if (rsi < 30) return 'BUY';      // Oversold
    if (rsi > 70) return 'SELL';     // Overbought
    return 'NEUTRAL';
  }

  private evaluateMACD(macd: { macd: number; signal: number; histogram: number }): 'BUY' | 'SELL' | 'NEUTRAL' {
    if (macd.macd > macd.signal && macd.histogram > 0) return 'BUY';
    if (macd.macd < macd.signal && macd.histogram < 0) return 'SELL';
    return 'NEUTRAL';
  }

  private evaluateBollingerBands(bb: { upper: number; middle: number; lower: number }, price: number): 'BUY' | 'SELL' | 'NEUTRAL' {
    if (price < bb.lower) return 'BUY';      // Price below lower band
    if (price > bb.upper) return 'SELL';     // Price above upper band
    return 'NEUTRAL';
  }

  private evaluateTrend(indicators: IndicatorValues, price: number): 'BUY' | 'SELL' | 'NEUTRAL' {
    if (price > indicators.sma20 && indicators.ema12 > indicators.ema26) return 'BUY';
    if (price < indicators.sma20 && indicators.ema12 < indicators.ema26) return 'SELL';
    return 'NEUTRAL';
  }

  private combineSignals(signals: any): 'BUY' | 'SELL' | 'HOLD' {
    const buySignals = Object.values(signals).filter(s => s === 'BUY').length;
    const sellSignals = Object.values(signals).filter(s => s === 'SELL').length;

    if (buySignals >= 3) return 'BUY';
    if (sellSignals >= 3) return 'SELL';
    if (buySignals > sellSignals) return 'BUY';
    if (sellSignals > buySignals) return 'SELL';

    return 'HOLD';
  }

  private calculateConfidence(signals: any, indicators: IndicatorValues): number {
    let confidence = 50;

    // RSI confidence
    if (indicators.rsi < 20 || indicators.rsi > 80) confidence += 15;
    else if (indicators.rsi < 35 || indicators.rsi > 65) confidence += 10;

    // MACD confidence
    if (Math.abs(indicators.macd.histogram) > 0.001) confidence += 10;

    // Signal agreement
    const signalValues = Object.values(signals);
    const buyCount = signalValues.filter(s => s === 'BUY').length;
    const sellCount = signalValues.filter(s => s === 'SELL').length;

    if (buyCount >= 3 || sellCount >= 3) confidence += 20;
    else if (buyCount >= 2 || sellCount >= 2) confidence += 10;

    return Math.min(95, Math.max(30, confidence));
  }

  private determineStrategy(signals: any): string {
    if (signals.rsi !== 'NEUTRAL' && signals.macd !== 'NEUTRAL') {
      return 'RSI + MACD Kombinatsiyasi';
    }
    if (signals.bollinger !== 'NEUTRAL') {
      return 'Bollinger Bands Strategiyasi';
    }
    if (signals.trend !== 'NEUTRAL') {
      return 'Trend Following';
    }
    return 'Multi-Indikator Tahlil';
  }

  private generateReason(signals: any, indicators: IndicatorValues): string {
    const reasons: string[] = [];

    if (signals.rsi === 'BUY') {
      reasons.push(`RSI ${indicators.rsi.toFixed(1)} - haddan tashqari sotilgan holat`);
    } else if (signals.rsi === 'SELL') {
      reasons.push(`RSI ${indicators.rsi.toFixed(1)} - haddan tashqari sotib olingan holat`);
    }

    if (signals.macd === 'BUY') {
      reasons.push('MACD ijobiy signal bermoqda');
    } else if (signals.macd === 'SELL') {
      reasons.push('MACD salbiy signal bermoqda');
    }

    if (signals.bollinger === 'BUY') {
      reasons.push('Narx Bollinger pastki chegarasida');
    } else if (signals.bollinger === 'SELL') {
      reasons.push('Narx Bollinger yuqori chegarasida');
    }

    if (signals.trend === 'BUY') {
      reasons.push('Yuqoriga yo\'nalgan trend');
    } else if (signals.trend === 'SELL') {
      reasons.push('Pastga yo\'nalgan trend');
    }

    return reasons.length > 0 ? reasons.join(', ') : 'Texnik ko\'rsatkichlar asosida tahlil';
  }

  private calculateTradingLevels(
    price: number,
    direction: 'BUY' | 'SELL' | 'HOLD',
    confidence: number,
    indicators: IndicatorValues
  ): { targetPrice?: number; stopLoss?: number } {

    if (direction === 'HOLD') return {};

    // Risk based on confidence (lower confidence = lower risk)
    const baseRisk = 0.01 + ((100 - confidence) / 100) * 0.02; // 1-3% risk
    const riskRewardRatio = 2 + (confidence / 100); // 2-3 reward ratio

    if (direction === 'BUY') {
      const stopLoss = indicators.bollingerBands.lower || (price * (1 - baseRisk));
      const targetPrice = price + ((price - stopLoss) * riskRewardRatio);

      return {
        targetPrice: Number(targetPrice.toFixed(5)),
        stopLoss: Number(stopLoss.toFixed(5))
      };
    } else {
      const stopLoss = indicators.bollingerBands.upper || (price * (1 + baseRisk));
      const targetPrice = price - ((stopLoss - price) * riskRewardRatio);

      return {
        targetPrice: Number(targetPrice.toFixed(5)),
        stopLoss: Number(stopLoss.toFixed(5))
      };
    }
  }
}