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
        this.fcsUrl = 'https://fcsapi.com/api-v3/forex/latest';
        this.alphavantageUrl = 'https://www.alphavantage.co/query';
        this.financialModelingUrl = 'https://financialmodelingprep.com/api/v3';
        this.cache = new Map();
        this.cacheTimeout = 30000;
    }
    async getPrice(symbol) {
        const cached = this.cache.get(symbol);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        try {
            let price = await this.getPriceFromFCS(symbol);
            if (!price) {
                price = await this.getPriceFromYahoo(symbol);
            }
            if (!price) {
                price = await this.getPriceFromExchangeRate(symbol);
            }
            if (!price) {
                price = await this.getPriceFromFinancialModeling(symbol);
            }
            if (!price) {
                console.warn(`Using mock price for ${symbol} - all APIs failed`);
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
            const fcsSymbol = this.convertToFCSSymbol(symbol);
            const response = await axios_1.default.get(this.fcsUrl, {
                params: {
                    symbol: fcsSymbol,
                    access_key: process.env.FCSAPI_KEY || 'demo'
                },
                timeout: 8000
            });
            console.log(`FCS API response for ${symbol}:`, response.data);
            if (response.data && response.data.status && response.data.response) {
                const data = response.data.response[0];
                return {
                    symbol: symbol.toUpperCase(),
                    price: parseFloat(data.price || data.c),
                    change24h: parseFloat(data.change || data.ch) || 0,
                    changePercent24h: parseFloat(data.changePct || data.cp) || 0,
                    timestamp: new Date().toISOString(),
                    source: 'FCS-API'
                };
            }
            return null;
        }
        catch (error) {
            console.error(`FCS API error for ${symbol}:`, error);
            return null;
        }
    }
    async getPriceFromYahoo(symbol) {
        try {
            const yahooSymbol = this.convertToYahooSymbol(symbol);
            const url = `https://query1.finance.yahoo.com/v8/finance/chart/${yahooSymbol}`;
            const response = await axios_1.default.get(url, {
                timeout: 5000,
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            });
            const data = response.data?.chart?.result?.[0];
            if (data && data.meta) {
                const price = data.meta.regularMarketPrice || data.meta.previousClose;
                const previousClose = data.meta.previousClose;
                const change = price - previousClose;
                const changePercent = (change / previousClose) * 100;
                return {
                    symbol: symbol.toUpperCase(),
                    price: parseFloat(price.toFixed(5)),
                    change24h: parseFloat(change.toFixed(5)),
                    changePercent24h: parseFloat(changePercent.toFixed(2)),
                    timestamp: new Date().toISOString(),
                    source: 'Yahoo Finance'
                };
            }
            return null;
        }
        catch (error) {
            console.error(`Yahoo Finance API error for ${symbol}:`, error);
            return null;
        }
    }
    async getPriceFromFinancialModeling(symbol) {
        try {
            const pair = symbol.toUpperCase();
            const url = `${this.financialModelingUrl}/fx/${pair}?apikey=demo`;
            const response = await axios_1.default.get(url, {
                timeout: 5000
            });
            if (response.data && response.data.length > 0) {
                const data = response.data[0];
                return {
                    symbol: symbol.toUpperCase(),
                    price: parseFloat(data.price),
                    change24h: parseFloat(data.change) || 0,
                    changePercent24h: parseFloat(data.changesPercentage) || 0,
                    timestamp: new Date().toISOString(),
                    source: 'Financial Modeling Prep'
                };
            }
            return null;
        }
        catch (error) {
            return null;
        }
    }
    convertToYahooSymbol(symbol) {
        const symbolMap = {
            'EURUSD': 'EURUSD=X',
            'GBPUSD': 'GBPUSD=X',
            'USDJPY': 'USDJPY=X',
            'USDCHF': 'USDCHF=X',
            'AUDUSD': 'AUDUSD=X',
            'NZDUSD': 'NZDUSD=X',
            'USDCAD': 'USDCAD=X',
            'EURGBP': 'EURGBP=X',
            'EURJPY': 'EURJPY=X',
            'XAUUSD': 'GC=F',
            'XTIUSD': 'CL=F',
            'BTCUSD': 'BTC-USD',
            'ETHUSD': 'ETH-USD'
        };
        return symbolMap[symbol.toUpperCase()] || `${symbol}=X`;
    }
    convertToFCSSymbol(symbol) {
        const symbolMap = {
            'EURUSD': 'EUR/USD',
            'GBPUSD': 'GBP/USD',
            'USDJPY': 'USD/JPY',
            'USDCHF': 'USD/CHF',
            'AUDUSD': 'AUD/USD',
            'NZDUSD': 'NZD/USD',
            'USDCAD': 'USD/CAD',
            'EURGBP': 'EUR/GBP',
            'EURJPY': 'EUR/JPY',
            'XAUUSD': 'XAU/USD',
            'XTIUSD': 'CL/USD',
            'BTCUSD': 'BTC/USD',
            'ETHUSD': 'ETH/USD'
        };
        return symbolMap[symbol.toUpperCase()] || symbol.toUpperCase();
    }
    getMockPrice(symbol) {
        const basePrices = {
            'EURUSD': 1.0892,
            'GBPUSD': 1.2703,
            'USDJPY': 148.95,
            'USDCHF': 0.8724,
            'AUDUSD': 0.6592,
            'NZDUSD': 0.6187,
            'USDCAD': 1.3521,
            'EURGBP': 0.8574,
            'EURJPY': 162.34,
            'XAUUSD': 2055.80,
            'XTIUSD': 76.45,
            'BTCUSD': 43127.50,
            'ETHUSD': 2634.28
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
