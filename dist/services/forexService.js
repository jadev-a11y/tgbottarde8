"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ForexService = void 0;
const axios_1 = __importDefault(require("axios"));
class ForexService {
    constructor() {
        this.baseUrl = 'https://api.exchangerate-api.com/v4';
        this.fcsUrl = 'https://fcsapi.com/api-v3/forex';
        this.cache = new Map();
        this.cacheTimeout = 60000;
    }
    async getPrice(symbol) {
        const cached = this.cache.get(symbol);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        try {
            let price = await this.getPriceFromExchangeRate(symbol);
            if (!price) {
                price = await this.getPriceFromFCS(symbol);
            }
            if (!price) {
                price = this.getMockPrice(symbol);
            }
            this.cache.set(symbol, { data: price, timestamp: Date.now() });
            return price;
        }
        catch (error) {
            console.error(`Error fetching price for ${symbol}:`, error);
            return this.getMockPrice(symbol);
        }
    }
    async getPriceFromExchangeRate(symbol) {
        try {
            const [base, quote] = this.parsePair(symbol);
            const response = await axios_1.default.get(`${this.baseUrl}/latest/${base}`, {
                timeout: 5000
            });
            if (response.data && response.data.rates && response.data.rates[quote]) {
                const rate = response.data.rates[quote];
                return {
                    symbol: symbol.toUpperCase(),
                    price: rate,
                    change24h: 0,
                    changePercent24h: 0,
                    timestamp: new Date().toISOString(),
                    source: 'ExchangeRate-API'
                };
            }
            return null;
        }
        catch (error) {
            return null;
        }
    }
    async getPriceFromFCS(symbol) {
        try {
            const response = await axios_1.default.get(`${this.fcsUrl}/latest`, {
                params: {
                    symbol: symbol.toUpperCase(),
                    access_key: process.env.FCSAPI_KEY || 'demo'
                },
                timeout: 5000
            });
            if (response.data && response.data.response && response.data.response.length > 0) {
                const data = response.data.response[0];
                return {
                    symbol: symbol.toUpperCase(),
                    price: parseFloat(data.price),
                    change24h: parseFloat(data.change) || 0,
                    changePercent24h: parseFloat(data.changePct) || 0,
                    timestamp: new Date().toISOString(),
                    source: 'FCS-API'
                };
            }
            return null;
        }
        catch (error) {
            return null;
        }
    }
    getMockPrice(symbol) {
        const basePrices = {
            'EURUSD': 1.0950,
            'GBPUSD': 1.2650,
            'USDJPY': 149.50,
            'USDCHF': 0.8750,
            'AUDUSD': 0.6550,
            'NZDUSD': 0.6150,
            'USDCAD': 1.3550,
            'EURGBP': 0.8650,
            'EURJPY': 163.50,
            'XAUUSD': 2045.50,
            'BTCUSD': 43500.00,
            'ETHUSD': 2650.00
        };
        const basePrice = basePrices[symbol.toUpperCase()] || 1.0000;
        const variation = (Math.random() - 0.5) * 0.02;
        const currentPrice = basePrice * (1 + variation);
        const change24h = (Math.random() - 0.5) * 0.05;
        return {
            symbol: symbol.toUpperCase(),
            price: parseFloat(currentPrice.toFixed(5)),
            change24h: parseFloat((currentPrice * change24h).toFixed(5)),
            changePercent24h: parseFloat((change24h * 100).toFixed(2)),
            timestamp: new Date().toISOString(),
            source: 'Mock Data'
        };
    }
    parsePair(symbol) {
        const pair = symbol.toUpperCase();
        if (pair === 'XAUUSD')
            return ['XAU', 'USD'];
        if (pair === 'BTCUSD')
            return ['BTC', 'USD'];
        if (pair === 'ETHUSD')
            return ['ETH', 'USD'];
        const major = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY'];
        for (const currency of major) {
            if (pair.startsWith(currency)) {
                const base = currency;
                const quote = pair.substring(currency.length);
                return [base, quote];
            }
        }
        return [pair.substring(0, 3), pair.substring(3)];
    }
    async getMultiplePrices(symbols) {
        const promises = symbols.map(symbol => this.getPrice(symbol));
        return Promise.all(promises);
    }
    getPopularPairs() {
        return [
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
            'AUDUSD', 'NZDUSD', 'USDCAD', 'EURGBP',
            'EURJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD'
        ];
    }
}
exports.ForexService = ForexService;
