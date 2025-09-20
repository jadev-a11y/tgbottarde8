import axios from 'axios';
import { ForexPrice } from '../types';

export class ForexService {
  private readonly baseUrl = 'https://api.exchangerate-api.com/v4';
  private readonly fcsUrl = 'https://fcsapi.com/api-v3/forex';
  private readonly cache = new Map<string, { data: ForexPrice; timestamp: number }>();
  private readonly cacheTimeout = 60000; // 1 minute

  async getPrice(symbol: string): Promise<ForexPrice> {
    const cached = this.cache.get(symbol);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    try {
      // Try multiple sources for reliability
      let price = await this.getPriceFromExchangeRate(symbol);

      if (!price) {
        price = await this.getPriceFromFCS(symbol);
      }

      if (!price) {
        price = this.getMockPrice(symbol);
      }

      this.cache.set(symbol, { data: price, timestamp: Date.now() });
      return price;
    } catch (error) {
      console.error(`Error fetching price for ${symbol}:`, error);
      return this.getMockPrice(symbol);
    }
  }

  private async getPriceFromExchangeRate(symbol: string): Promise<ForexPrice | null> {
    try {
      // Convert EURUSD format to EUR/USD for this API
      const [base, quote] = this.parsePair(symbol);

      const response = await axios.get(`${this.baseUrl}/latest/${base}`, {
        timeout: 5000
      });

      if (response.data && response.data.rates && response.data.rates[quote]) {
        const rate = response.data.rates[quote];

        return {
          symbol: symbol.toUpperCase(),
          price: rate,
          change24h: 0, // This API doesn't provide change data
          changePercent24h: 0,
          timestamp: new Date().toISOString(),
          source: 'ExchangeRate-API'
        };
      }

      return null;
    } catch (error) {
      return null;
    }
  }

  private async getPriceFromFCS(symbol: string): Promise<ForexPrice | null> {
    try {
      // FCS API format
      const response = await axios.get(`${this.fcsUrl}/latest`, {
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
    } catch (error) {
      return null;
    }
  }

  private getMockPrice(symbol: string): ForexPrice {
    const basePrices: { [key: string]: number } = {
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
    const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
    const currentPrice = basePrice * (1 + variation);

    const change24h = (Math.random() - 0.5) * 0.05; // ±2.5% daily change

    return {
      symbol: symbol.toUpperCase(),
      price: parseFloat(currentPrice.toFixed(5)),
      change24h: parseFloat((currentPrice * change24h).toFixed(5)),
      changePercent24h: parseFloat((change24h * 100).toFixed(2)),
      timestamp: new Date().toISOString(),
      source: 'Mock Data'
    };
  }

  private parsePair(symbol: string): [string, string] {
    // Parse currency pairs like EURUSD -> EUR, USD
    const pair = symbol.toUpperCase();

    if (pair === 'XAUUSD') return ['XAU', 'USD'];
    if (pair === 'BTCUSD') return ['BTC', 'USD'];
    if (pair === 'ETHUSD') return ['ETH', 'USD'];

    // Standard forex pairs
    const major = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY'];

    for (const currency of major) {
      if (pair.startsWith(currency)) {
        const base = currency;
        const quote = pair.substring(currency.length);
        return [base, quote];
      }
    }

    // Default fallback
    return [pair.substring(0, 3), pair.substring(3)];
  }

  async getMultiplePrices(symbols: string[]): Promise<ForexPrice[]> {
    const promises = symbols.map(symbol => this.getPrice(symbol));
    return Promise.all(promises);
  }

  // Popular forex pairs
  getPopularPairs(): string[] {
    return [
      'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
      'AUDUSD', 'NZDUSD', 'USDCAD', 'EURGBP',
      'EURJPY', 'XAUUSD', 'BTCUSD', 'ETHUSD'
    ];
  }
}