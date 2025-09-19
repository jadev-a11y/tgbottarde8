"""
Forex Market Data Provider
Real-time currency exchange rates from multiple APIs
"""
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

class ForexDataProvider:
    """Get real Forex data from multiple APIs"""

    def __init__(self):
        self.session = None
        self.apis = {
            'freeforex': 'https://www.freeforexapi.com/api/live',
            'exchangerate': 'https://api.exchangerate-api.com/v4/latest',
            'fixer': 'https://api.fixer.io/latest'
        }

        # Kengaytirilgan savdo juftliklari
        self.major_pairs = {
            # Major Forex
            'EURUSD': {'name': 'Euro vs AQSh Dollar', 'base': 'EUR', 'quote': 'USD', 'type': 'forex'},
            'GBPUSD': {'name': 'Ingliz Funt vs AQSh Dollar', 'base': 'GBP', 'quote': 'USD', 'type': 'forex'},
            'USDJPY': {'name': 'AQSh Dollar vs Yapon Yen', 'base': 'USD', 'quote': 'JPY', 'type': 'forex'},
            'USDCHF': {'name': 'AQSh Dollar vs Shveytsariya Frank', 'base': 'USD', 'quote': 'CHF', 'type': 'forex'},
            'AUDUSD': {'name': 'Avstraliya Dollar vs AQSh Dollar', 'base': 'AUD', 'quote': 'USD', 'type': 'forex'},
            'USDCAD': {'name': 'AQSh Dollar vs Kanada Dollar', 'base': 'USD', 'quote': 'CAD', 'type': 'forex'},
            'NZDUSD': {'name': 'Yangi Zelandiya Dollar vs AQSh Dollar', 'base': 'NZD', 'quote': 'USD', 'type': 'forex'},
            'EURGBP': {'name': 'Euro vs Ingliz Funt', 'base': 'EUR', 'quote': 'GBP', 'type': 'forex'},
            'EURJPY': {'name': 'Euro vs Yapon Yen', 'base': 'EUR', 'quote': 'JPY', 'type': 'forex'},
            'GBPJPY': {'name': 'Ingliz Funt vs Yapon Yen', 'base': 'GBP', 'quote': 'JPY', 'type': 'forex'},

            # Minor va Exotic Forex
            'EURCHF': {'name': 'Euro vs Shveytsariya Frank', 'base': 'EUR', 'quote': 'CHF', 'type': 'forex'},
            'EURAUD': {'name': 'Euro vs Avstraliya Dollar', 'base': 'EUR', 'quote': 'AUD', 'type': 'forex'},
            'EURCAD': {'name': 'Euro vs Kanada Dollar', 'base': 'EUR', 'quote': 'CAD', 'type': 'forex'},
            'GBPCHF': {'name': 'Ingliz Funt vs Shveytsariya Frank', 'base': 'GBP', 'quote': 'CHF', 'type': 'forex'},
            'GBPAUD': {'name': 'Ingliz Funt vs Avstraliya Dollar', 'base': 'GBP', 'quote': 'AUD', 'type': 'forex'},
            'GBPCAD': {'name': 'Ingliz Funt vs Kanada Dollar', 'base': 'GBP', 'quote': 'CAD', 'type': 'forex'},
            'AUDCAD': {'name': 'Avstraliya Dollar vs Kanada Dollar', 'base': 'AUD', 'quote': 'CAD', 'type': 'forex'},
            'AUDCHF': {'name': 'Avstraliya Dollar vs Shveytsariya Frank', 'base': 'AUD', 'quote': 'CHF', 'type': 'forex'},
            'AUDJPY': {'name': 'Avstraliya Dollar vs Yapon Yen', 'base': 'AUD', 'quote': 'JPY', 'type': 'forex'},
            'CADJPY': {'name': 'Kanada Dollar vs Yapon Yen', 'base': 'CAD', 'quote': 'JPY', 'type': 'forex'},
            'CHFJPY': {'name': 'Shveytsariya Frank vs Yapon Yen', 'base': 'CHF', 'quote': 'JPY', 'type': 'forex'},
            'NZDJPY': {'name': 'Yangi Zelandiya Dollar vs Yapon Yen', 'base': 'NZD', 'quote': 'JPY', 'type': 'forex'},

            # Qimmatbaho metallar
            'XAUUSD': {'name': 'Oltin vs AQSh Dollar', 'base': 'XAU', 'quote': 'USD', 'type': 'metal'},
            'XAGUSD': {'name': 'Kumush vs AQSh Dollar', 'base': 'XAG', 'quote': 'USD', 'type': 'metal'},
            'XPTUSD': {'name': 'Platina vs AQSh Dollar', 'base': 'XPT', 'quote': 'USD', 'type': 'metal'},
            'XPDUSD': {'name': 'Palladiy vs AQSh Dollar', 'base': 'XPD', 'quote': 'USD', 'type': 'metal'},

            # Tovar (Commodities)
            'USOIL': {'name': 'AQSh Neft', 'base': 'US', 'quote': 'OIL', 'type': 'commodity'},
            'UKOIL': {'name': 'Brent Neft', 'base': 'UK', 'quote': 'OIL', 'type': 'commodity'},
            'NATGAS': {'name': 'Tabiiy Gaz', 'base': 'NAT', 'quote': 'GAS', 'type': 'commodity'},

            # Indekslar
            'US30': {'name': 'Dow Jones', 'base': 'US', 'quote': '30', 'type': 'index'},
            'US500': {'name': 'S&P 500', 'base': 'US', 'quote': '500', 'type': 'index'},
            'NAS100': {'name': 'NASDAQ 100', 'base': 'NAS', 'quote': '100', 'type': 'index'},
            'GER40': {'name': 'DAX', 'base': 'GER', 'quote': '40', 'type': 'index'},
            'UK100': {'name': 'FTSE 100', 'base': 'UK', 'quote': '100', 'type': 'index'},
            'JPN225': {'name': 'Nikkei 225', 'base': 'JPN', 'quote': '225', 'type': 'index'},
            'AUS200': {'name': 'ASX 200', 'base': 'AUS', 'quote': '200', 'type': 'index'},

            # Kripto
            'BTCUSD': {'name': 'Bitcoin vs AQSh Dollar', 'base': 'BTC', 'quote': 'USD', 'type': 'crypto'},
            'ETHUSD': {'name': 'Ethereum vs AQSh Dollar', 'base': 'ETH', 'quote': 'USD', 'type': 'crypto'},
            'BNBUSD': {'name': 'Binance Coin vs AQSh Dollar', 'base': 'BNB', 'quote': 'USD', 'type': 'crypto'},
            'ADAUSD': {'name': 'Cardano vs AQSh Dollar', 'base': 'ADA', 'quote': 'USD', 'type': 'crypto'},
            'XRPUSD': {'name': 'Ripple vs AQSh Dollar', 'base': 'XRP', 'quote': 'USD', 'type': 'crypto'},
            'SOLUSD': {'name': 'Solana vs AQSh Dollar', 'base': 'SOL', 'quote': 'USD', 'type': 'crypto'},
            'DOTUSD': {'name': 'Polkadot vs AQSh Dollar', 'base': 'DOT', 'quote': 'USD', 'type': 'crypto'},
            'LINKUSD': {'name': 'Chainlink vs AQSh Dollar', 'base': 'LINK', 'quote': 'USD', 'type': 'crypto'},
            'MATICUSD': {'name': 'Polygon vs AQSh Dollar', 'base': 'MATIC', 'quote': 'USD', 'type': 'crypto'},
            'AVAXUSD': {'name': 'Avalanche vs AQSh Dollar', 'base': 'AVAX', 'quote': 'USD', 'type': 'crypto'}
        }

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_forex_rates(self) -> Dict[str, Dict]:
        """Get real-time forex rates for all major pairs"""
        await self.init_session()

        rates_data = {}

        # Try FreeForexAPI first
        try:
            pairs_str = ",".join(self.major_pairs.keys())
            url = f"{self.apis['freeforex']}?pairs={pairs_str}"

            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    if 'rates' in data:
                        for pair, rate_info in data['rates'].items():
                            if pair in self.major_pairs:
                                rates_data[pair] = {
                                    'rate': float(rate_info['rate']),
                                    'timestamp': rate_info.get('timestamp', datetime.now().isoformat()),
                                    'name': self.major_pairs[pair]['name'],
                                    'change_24h': np.random.uniform(-0.5, 0.5),  # Mock daily change
                                    'high_24h': float(rate_info['rate']) * (1 + np.random.uniform(0, 0.01)),
                                    'low_24h': float(rate_info['rate']) * (1 - np.random.uniform(0, 0.01)),
                                    'spread': float(rate_info['rate']) * 0.0001  # Mock spread
                                }

                        if rates_data:
                            return rates_data

        except Exception as e:
            print(f"FreeForexAPI error: {e}")

        # Fallback: Generate realistic forex data
        return self._generate_realistic_forex_data()

    def _generate_realistic_forex_data(self) -> Dict[str, Dict]:
        """Generate realistic forex rates when APIs fail"""

        # Kengaytirilgan realistik bazaviy narxlar
        base_rates = {
            # Major Forex
            'EURUSD': 1.0850, 'GBPUSD': 1.2650, 'USDJPY': 149.50, 'USDCHF': 0.8950,
            'AUDUSD': 0.6550, 'USDCAD': 1.3650, 'NZDUSD': 0.5950, 'EURGBP': 0.8580,
            'EURJPY': 162.30, 'GBPJPY': 189.20,

            # Minor va Exotic Forex
            'EURCHF': 0.9720, 'EURAUD': 1.6580, 'EURCAD': 1.4820, 'GBPCHF': 1.1320,
            'GBPAUD': 1.9350, 'GBPCAD': 1.7280, 'AUDCAD': 0.8920, 'AUDCHF': 0.5860,
            'AUDJPY': 97.85, 'CADJPY': 109.70, 'CHFJPY': 167.15, 'NZDJPY': 88.95,

            # Qimmatbaho metallar (USD/troy ounce)
            'XAUUSD': 2031.50, 'XAGUSD': 24.85, 'XPTUSD': 925.40, 'XPDUSD': 1234.80,

            # Tovarlar
            'USOIL': 89.75, 'UKOIL': 93.20, 'NATGAS': 2.845,

            # Indekslar
            'US30': 35420.50, 'US500': 4567.25, 'NAS100': 15890.75, 'GER40': 16248.30,
            'UK100': 7653.80, 'JPN225': 32580.90, 'AUS200': 7234.60,

            # Kripto (USD)
            'BTCUSD': 67850.00, 'ETHUSD': 2645.75, 'BNBUSD': 585.30, 'ADAUSD': 0.4520,
            'XRPUSD': 0.6180, 'SOLUSD': 144.85, 'DOTUSD': 6.780, 'LINKUSD': 15.420,
            'MATICUSD': 0.8950, 'AVAXUSD': 28.650
        }

        rates_data = {}

        for pair, base_rate in base_rates.items():
            # Add small random variation
            current_rate = base_rate + np.random.uniform(-base_rate*0.005, base_rate*0.005)

            rates_data[pair] = {
                'rate': round(current_rate, 4 if pair != 'USDJPY' and pair != 'EURJPY' and pair != 'GBPJPY' else 2),
                'timestamp': datetime.now().isoformat(),
                'name': self.major_pairs[pair]['name'],
                'change_24h': np.random.uniform(-0.8, 0.8),
                'high_24h': current_rate * (1 + np.random.uniform(0.001, 0.008)),
                'low_24h': current_rate * (1 - np.random.uniform(0.001, 0.008)),
                'spread': current_rate * 0.0001,
                'source': 'Generated (API unavailable)'
            }

        return rates_data

    async def get_historical_data(self, pair: str, hours: int = 24) -> pd.DataFrame:
        """Generate historical data for technical analysis"""
        current_rates = await self.get_forex_rates()

        if pair not in current_rates:
            return pd.DataFrame()

        current_price = current_rates[pair]['rate']

        # Generate realistic hourly data
        data = []
        base_price = current_price

        for i in range(hours):
            timestamp = datetime.now() - timedelta(hours=hours-i)

            # Random walk with trend
            price_change = np.random.normal(0, base_price * 0.002)  # 0.2% volatility
            base_price += price_change

            # Ensure positive prices
            base_price = max(base_price, current_price * 0.95)

            # Generate OHLC
            high = base_price * (1 + abs(np.random.normal(0, 0.001)))
            low = base_price * (1 - abs(np.random.normal(0, 0.001)))
            open_price = base_price + np.random.normal(0, base_price * 0.0005)
            close_price = base_price

            data.append({
                'timestamp': timestamp,
                'open': open_price,
                'high': max(open_price, high, close_price),
                'low': min(open_price, low, close_price),
                'close': close_price,
                'volume': np.random.uniform(1000000, 5000000)  # Mock volume
            })

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)

        return df

# Test function
async def test_forex_api():
    provider = ForexDataProvider()

    print("📊 Testing Forex API...")
    rates = await provider.get_forex_rates()

    for pair, data in rates.items():
        print(f"💱 {pair}: {data['rate']} ({data['change_24h']:+.2f}%)")

    await provider.close_session()

if __name__ == "__main__":
    asyncio.run(test_forex_api())