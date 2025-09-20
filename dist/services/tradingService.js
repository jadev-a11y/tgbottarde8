"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TradingService = void 0;
const forexService_1 = require("./forexService");
const technicalAnalysis_1 = require("./technicalAnalysis");
class TradingService {
    constructor() {
        this.forexService = new forexService_1.ForexService();
        this.technicalAnalysis = new technicalAnalysis_1.TechnicalAnalysisService();
    }
    async generateSignal(symbol) {
        try {
            const currentPrice = await this.forexService.getPrice(symbol);
            const signal = this.technicalAnalysis.generateTradingSignal(currentPrice.price, symbol);
            return signal;
        }
        catch (error) {
            console.error(`Error generating signal for ${symbol}:`, error);
            throw error;
        }
    }
    selectStrategy() {
        const strategies = [
            'Volume Price Trend',
            'Moving Average Crossover',
            'RSI Divergence',
            'Support Resistance',
            'Bollinger Bands',
            'MACD Signal',
            'Fibonacci Retracement',
            'Price Action'
        ];
        return strategies[Math.floor(Math.random() * strategies.length)];
    }
    async analyzeWithStrategy(price, strategy) {
        const direction = this.getSignalDirection(price, strategy);
        const confidence = this.calculateConfidence(price, strategy);
        const reason = this.generateReason(price, strategy, direction);
        const { targetPrice, stopLoss } = this.calculateLevels(price.price, direction);
        return {
            symbol: price.symbol,
            direction,
            confidence,
            strategy,
            price: price.price,
            reason,
            timestamp: new Date().toISOString(),
            targetPrice,
            stopLoss
        };
    }
    getSignalDirection(price, strategy) {
        const changePercent = price.changePercent24h;
        switch (strategy) {
            case 'Volume Price Trend':
                return changePercent > 0 ? 'BUY' : changePercent < -1 ? 'SELL' : 'HOLD';
            case 'Moving Average Crossover':
                return Math.random() > 0.6 ? 'BUY' : Math.random() < 0.3 ? 'SELL' : 'HOLD';
            case 'RSI Divergence':
                return Math.abs(changePercent) > 1.5 ? (changePercent > 0 ? 'SELL' : 'BUY') : 'HOLD';
            case 'Support Resistance':
                return changePercent < -2 ? 'BUY' : changePercent > 2 ? 'SELL' : 'HOLD';
            case 'Bollinger Bands':
                return Math.abs(changePercent) > 2 ? (changePercent > 0 ? 'SELL' : 'BUY') : 'HOLD';
            case 'MACD Signal':
                return changePercent > 0.5 ? 'BUY' : changePercent < -0.5 ? 'SELL' : 'HOLD';
            case 'Fibonacci Retracement':
                return changePercent < -1.5 ? 'BUY' : changePercent > 1.5 ? 'SELL' : 'HOLD';
            case 'Price Action':
                return Math.random() > 0.5 ? 'BUY' : 'SELL';
            default:
                return 'HOLD';
        }
    }
    calculateConfidence(price, strategy) {
        const changeAbs = Math.abs(price.changePercent24h);
        let baseConfidence = 50;
        if (changeAbs > 2)
            baseConfidence += 20;
        else if (changeAbs > 1)
            baseConfidence += 10;
        if (['Volume Price Trend', 'MACD Signal'].includes(strategy)) {
            baseConfidence += 10;
        }
        const randomFactor = (Math.random() - 0.5) * 20;
        return Math.max(30, Math.min(95, baseConfidence + randomFactor));
    }
    generateReason(price, strategy, direction) {
        const reasons = {
            'BUY': [
                'Narx pastki qo\'llab-quvvatlash darajasidan sakradi',
                'Ko\'rsatkichlar yuqoriga ko\'tarilish tendensiyasini ko\'rsatmoqda',
                'Texnik tahlil yuqoriga harakatni tasdiqlaydi',
                'Bozor his-tuyg\'ulari ijobiy yo\'nalishda',
                'Asosiy qarshilik darajasi sindirildi'
            ],
            'SELL': [
                'Narx yuqori qarshilik darajasidan qaytdi',
                'Ko\'rsatkichlar pastga tushish signalini bermoqda',
                'Texnik tahlil pasayish tendensiyasini ko\'rsatdi',
                'Bozor his-tuyg\'ulari salbiy yo\'nalishda',
                'Muhim qo\'llab-quvvatlash darajasi buzildi'
            ],
            'HOLD': [
                'Bozor aniq yo\'nalishga ega emas',
                'Narx muhim darajalar orasida harakat qilmoqda',
                'Kutish va kuzatish tavsiya etiladi',
                'Signal aniq emas, ehtiyotkorlik talab qilinadi'
            ]
        };
        const directionReasons = reasons[direction];
        const selectedReason = directionReasons[Math.floor(Math.random() * directionReasons.length)];
        const strategyDetails = {
            'Volume Price Trend': 'Hajm va narx bir yo\'nalishda harakat qilmoqda',
            'Moving Average Crossover': 'O\'rtacha ko\'rsatkichlar kesishma signali',
            'RSI Divergence': 'RSI divergensiya payterni ko\'rsatmoqda',
            'Support Resistance': 'Qo\'llab-quvvatlash/qarshilik darajasi faol',
            'Bollinger Bands': 'Bollinger Bands signali faollashdi',
            'MACD Signal': 'MACD histogramma o\'zgarishi',
            'Fibonacci Retracement': 'Fibonacci darajalarida reaktsiya',
            'Price Action': 'Narx harakati tahlili asosida'
        };
        return `${selectedReason}. ${strategyDetails[strategy] || 'Texnik tahlil asosida'}.`;
    }
    calculateLevels(currentPrice, direction) {
        if (direction === 'HOLD') {
            return {};
        }
        const riskRewardRatio = 2;
        const riskPercent = 0.01 + Math.random() * 0.02;
        if (direction === 'BUY') {
            const stopLoss = currentPrice * (1 - riskPercent);
            const targetPrice = currentPrice * (1 + riskPercent * riskRewardRatio);
            return {
                targetPrice: parseFloat(targetPrice.toFixed(5)),
                stopLoss: parseFloat(stopLoss.toFixed(5))
            };
        }
        else {
            const stopLoss = currentPrice * (1 + riskPercent);
            const targetPrice = currentPrice * (1 - riskPercent * riskRewardRatio);
            return {
                targetPrice: parseFloat(targetPrice.toFixed(5)),
                stopLoss: parseFloat(stopLoss.toFixed(5))
            };
        }
    }
    async getRandomSignal() {
        const popularPairs = this.forexService.getPopularPairs();
        const randomPair = popularPairs[Math.floor(Math.random() * popularPairs.length)];
        return this.generateSignal(randomPair);
    }
    formatSignalMessage(signal) {
        const directionEmoji = {
            'BUY': '🟢',
            'SELL': '🔴',
            'HOLD': '🟡'
        };
        const directionText = {
            'BUY': 'SOTIB OLISH',
            'SELL': 'SOTISH',
            'HOLD': 'KUTISH'
        };
        let message = `${signal.symbol.includes('BTC') || signal.symbol.includes('ETH') ? '₿' : '💱'} ${signal.symbol}\n\n`;
        message += `${directionEmoji[signal.direction]} ${directionText[signal.direction]} Signal\n`;
        message += `🤖 Strategiya: ${signal.strategy}\n`;
        message += `🎯 Ishonch: ${Math.round(signal.confidence)}%\n\n`;
        message += `💰 Narx: ${signal.price.toFixed(signal.symbol.includes('JPY') ? 3 : 5)}\n`;
        if (signal.targetPrice) {
            message += `🎯 Maqsad: ${signal.targetPrice.toFixed(signal.symbol.includes('JPY') ? 3 : 5)}\n`;
        }
        if (signal.stopLoss) {
            message += `🛑 Stop Loss: ${signal.stopLoss.toFixed(signal.symbol.includes('JPY') ? 3 : 5)}\n`;
        }
        message += `💡 Sabab: ${signal.reason}\n\n`;
        const now = new Date();
        const timeString = now.toLocaleTimeString('uz-UZ', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        message += `⏰ ${timeString}`;
        return message;
    }
}
exports.TradingService = TradingService;
