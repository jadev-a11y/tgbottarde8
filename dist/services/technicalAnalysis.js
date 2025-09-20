"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TechnicalAnalysisService = void 0;
class TechnicalAnalysisService {
    constructor() {
        this.RSI_PERIOD = 14;
        this.MACD_FAST = 12;
        this.MACD_SLOW = 26;
        this.MACD_SIGNAL = 9;
        this.BB_PERIOD = 20;
        this.BB_MULTIPLIER = 2;
    }
    calculateRSI(prices, period = this.RSI_PERIOD) {
        if (prices.length < period + 1) {
            throw new Error('Недостаточно данных для расчета RSI');
        }
        const gains = [];
        const losses = [];
        for (let i = 1; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            gains.push(change > 0 ? change : 0);
            losses.push(change < 0 ? Math.abs(change) : 0);
        }
        let avgGain = gains.slice(0, period).reduce((sum, gain) => sum + gain, 0) / period;
        let avgLoss = losses.slice(0, period).reduce((sum, loss) => sum + loss, 0) / period;
        for (let i = period; i < gains.length; i++) {
            avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
            avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;
        }
        if (avgLoss === 0)
            return 100;
        const rs = avgGain / avgLoss;
        const rsi = 100 - (100 / (1 + rs));
        return Number(rsi.toFixed(2));
    }
    calculateEMA(prices, period) {
        if (prices.length < period) {
            throw new Error('Недостаточно данных для расчета EMA');
        }
        const sma = prices.slice(0, period).reduce((sum, price) => sum + price, 0) / period;
        const multiplier = 2 / (period + 1);
        let ema = sma;
        for (let i = period; i < prices.length; i++) {
            ema = (prices[i] * multiplier) + (ema * (1 - multiplier));
        }
        return Number(ema.toFixed(5));
    }
    calculateMACD(prices) {
        if (prices.length < this.MACD_SLOW) {
            throw new Error('Недостаточно данных для расчета MACD');
        }
        const ema12 = this.calculateEMA(prices, this.MACD_FAST);
        const ema26 = this.calculateEMA(prices, this.MACD_SLOW);
        const macd = ema12 - ema26;
        const macdHistory = this.generateMACDHistory(prices);
        const signal = this.calculateEMA(macdHistory, this.MACD_SIGNAL);
        const histogram = macd - signal;
        return {
            macd: Number(macd.toFixed(5)),
            signal: Number(signal.toFixed(5)),
            histogram: Number(histogram.toFixed(5))
        };
    }
    generateMACDHistory(prices) {
        const macdHistory = [];
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
    calculateBollingerBands(prices, period = this.BB_PERIOD) {
        if (prices.length < period) {
            throw new Error('Недостаточно данных для расчета Bollinger Bands');
        }
        const subset = prices.slice(-period);
        const sma = subset.reduce((sum, price) => sum + price, 0) / period;
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
    calculateSMA(prices, period) {
        if (prices.length < period) {
            throw new Error('Недостаточно данных для расчета SMA');
        }
        const subset = prices.slice(-period);
        const sma = subset.reduce((sum, price) => sum + price, 0) / period;
        return Number(sma.toFixed(5));
    }
    generateHistoricalData(currentPrice, periods = 50) {
        const prices = [];
        let price = currentPrice;
        for (let i = 0; i < periods; i++) {
            const change = (Math.random() - 0.5) * 0.02;
            const trendBias = i < periods / 2 ? -0.001 : 0.001;
            price = price * (1 + change + trendBias);
            prices.unshift(Number(price.toFixed(5)));
        }
        return prices;
    }
    analyzePrice(currentPrice, symbol) {
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
    generateTradingSignal(currentPrice, symbol) {
        const indicators = this.analyzePrice(currentPrice, symbol);
        const signals = this.evaluateIndicators(indicators, currentPrice);
        const finalSignal = this.combineSignals(signals);
        const confidence = this.calculateConfidence(signals, indicators);
        const strategy = this.determineStrategy(signals);
        const reason = this.generateReason(signals, indicators);
        const { targetPrice, stopLoss } = this.calculateTradingLevels(currentPrice, finalSignal, confidence, indicators);
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
    evaluateIndicators(indicators, currentPrice) {
        return {
            rsi: this.evaluateRSI(indicators.rsi),
            macd: this.evaluateMACD(indicators.macd),
            bollinger: this.evaluateBollingerBands(indicators.bollingerBands, currentPrice),
            trend: this.evaluateTrend(indicators, currentPrice)
        };
    }
    evaluateRSI(rsi) {
        if (rsi < 30)
            return 'BUY';
        if (rsi > 70)
            return 'SELL';
        return 'NEUTRAL';
    }
    evaluateMACD(macd) {
        if (macd.macd > macd.signal && macd.histogram > 0)
            return 'BUY';
        if (macd.macd < macd.signal && macd.histogram < 0)
            return 'SELL';
        return 'NEUTRAL';
    }
    evaluateBollingerBands(bb, price) {
        if (price < bb.lower)
            return 'BUY';
        if (price > bb.upper)
            return 'SELL';
        return 'NEUTRAL';
    }
    evaluateTrend(indicators, price) {
        if (price > indicators.sma20 && indicators.ema12 > indicators.ema26)
            return 'BUY';
        if (price < indicators.sma20 && indicators.ema12 < indicators.ema26)
            return 'SELL';
        return 'NEUTRAL';
    }
    combineSignals(signals) {
        const buySignals = Object.values(signals).filter(s => s === 'BUY').length;
        const sellSignals = Object.values(signals).filter(s => s === 'SELL').length;
        if (buySignals >= 3)
            return 'BUY';
        if (sellSignals >= 3)
            return 'SELL';
        if (buySignals > sellSignals)
            return 'BUY';
        if (sellSignals > buySignals)
            return 'SELL';
        return 'HOLD';
    }
    calculateConfidence(signals, indicators) {
        let confidence = 50;
        if (indicators.rsi < 20 || indicators.rsi > 80)
            confidence += 15;
        else if (indicators.rsi < 35 || indicators.rsi > 65)
            confidence += 10;
        if (Math.abs(indicators.macd.histogram) > 0.001)
            confidence += 10;
        const signalValues = Object.values(signals);
        const buyCount = signalValues.filter(s => s === 'BUY').length;
        const sellCount = signalValues.filter(s => s === 'SELL').length;
        if (buyCount >= 3 || sellCount >= 3)
            confidence += 20;
        else if (buyCount >= 2 || sellCount >= 2)
            confidence += 10;
        return Math.min(95, Math.max(30, confidence));
    }
    determineStrategy(signals) {
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
    generateReason(signals, indicators) {
        const reasons = [];
        if (signals.rsi === 'BUY') {
            reasons.push(`RSI ${indicators.rsi.toFixed(1)} - haddan tashqari sotilgan holat`);
        }
        else if (signals.rsi === 'SELL') {
            reasons.push(`RSI ${indicators.rsi.toFixed(1)} - haddan tashqari sotib olingan holat`);
        }
        if (signals.macd === 'BUY') {
            reasons.push('MACD ijobiy signal bermoqda');
        }
        else if (signals.macd === 'SELL') {
            reasons.push('MACD salbiy signal bermoqda');
        }
        if (signals.bollinger === 'BUY') {
            reasons.push('Narx Bollinger pastki chegarasida');
        }
        else if (signals.bollinger === 'SELL') {
            reasons.push('Narx Bollinger yuqori chegarasida');
        }
        if (signals.trend === 'BUY') {
            reasons.push('Yuqoriga yo\'nalgan trend');
        }
        else if (signals.trend === 'SELL') {
            reasons.push('Pastga yo\'nalgan trend');
        }
        return reasons.length > 0 ? reasons.join(', ') : 'Texnik ko\'rsatkichlar asosida tahlil';
    }
    calculateTradingLevels(price, direction, confidence, indicators) {
        if (direction === 'HOLD')
            return {};
        const baseRisk = 0.01 + ((100 - confidence) / 100) * 0.02;
        const riskRewardRatio = 2 + (confidence / 100);
        if (direction === 'BUY') {
            const stopLoss = indicators.bollingerBands.lower || (price * (1 - baseRisk));
            const targetPrice = price + ((price - stopLoss) * riskRewardRatio);
            return {
                targetPrice: Number(targetPrice.toFixed(5)),
                stopLoss: Number(stopLoss.toFixed(5))
            };
        }
        else {
            const stopLoss = indicators.bollingerBands.upper || (price * (1 + baseRisk));
            const targetPrice = price - ((stopLoss - price) * riskRewardRatio);
            return {
                targetPrice: Number(targetPrice.toFixed(5)),
                stopLoss: Number(stopLoss.toFixed(5))
            };
        }
    }
}
exports.TechnicalAnalysisService = TechnicalAnalysisService;
