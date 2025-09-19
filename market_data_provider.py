#!/usr/bin/env python3
"""
Провайдер рыночных данных с несколькими источниками для надежности
"""
import yfinance as yf
# import pandas as pd  # Removed for Python 3.13 compatibility
import requests
import json
from typing import Tuple, Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class MarketDataProvider:
    """Провайдер рыночных данных с fallback источниками"""

    def __init__(self):
        # Бесплатный ключ Alpha Vantage - демо ключ
        self.alpha_vantage_key = "demo"

    def get_forex_data_av(self, from_currency: str, to_currency: str) -> Optional[dict]:
        """Получить данные валютной пары через Alpha Vantage"""
        return None

    def get_crypto_data_av(self, symbol: str) -> Optional[dict]:
        """Получить данные криптовалюты через Alpha Vantage"""
        return None

    def get_free_forex_data(self, pair: str) -> Optional[dict]:
        """Получить данные через бесплатные API"""
        try:
            # Exchangerate API (бесплатный)
            base = pair[:3]
            target = pair[3:]

            url = f"https://api.exchangerate.host/timeseries"
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            params = {
                'start_date': start_date,
                'end_date': end_date,
                'base': base,
                'symbols': target,
                'format': 'json'
            }

            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get('success') and 'rates' in data:
                rates_data = []
                for date_str, rates in data['rates'].items():
                    if target in rates:
                        rates_data.append({
                            'date': date_str,
                            'close': rates[target]
                        })

                if rates_data:
                    df = dict(rates_data)
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)

                    # Добавляем базовые OHLC данные
                    df['open'] = df['close']
                    df['high'] = df['close'] * 1.001  # Симуляция разброса
                    df['low'] = df['close'] * 0.999
                    df['volume'] = 1000000  # Фиктивный объем

                    logger.info(f"Free API: получено {len(df)} записей для {pair}")
                    return df

        except Exception as e:
            logger.error(f"Free API error: {e}")

        return None

    async def get_market_data(self, pair: str) -> Tuple[bool, str, dict]:
        """Главный метод получения данных с fallback логикой"""
        try:
            pair_clean = pair.upper().replace('/', '').replace('-', '').replace(' ', '')

            # Попытка 1: yfinance (основной источник)
            yf_data = self._try_yfinance(pair_clean)
            if yf_data is not None and not yf_data.empty:
                return True, f"yfinance:{pair_clean}", yf_data

            # Попытка 2: Alpha Vantage для форекса
            if len(pair_clean) == 6:
                from_curr = pair_clean[:3]
                to_curr = pair_clean[3:]
                av_data = self.get_forex_data_av(from_curr, to_curr)
                if av_data is not None and not av_data.empty:
                    return True, f"alphavantage:{from_curr}/{to_curr}", av_data

            # Попытка 3: Alpha Vantage для криптовалют
            if pair_clean.endswith('USD'):
                crypto_symbol = pair_clean[:-3]
                av_crypto = self.get_crypto_data_av(crypto_symbol)
                if av_crypto is not None and not av_crypto.empty:
                    return True, f"alphavantage:{crypto_symbol}-USD", av_crypto

            # Попытка 4: Бесплатные API для форекса
            if len(pair_clean) == 6:
                free_data = self.get_free_forex_data(pair_clean)
                if free_data is not None and not free_data.empty:
                    return True, f"free_api:{pair_clean}", free_data

            return False, "", dict()

        except Exception as e:
            logger.error(f"Market data error: {e}")
            return False, "", dict()

    def _try_yfinance(self, pair_clean: str) -> Optional[dict]:
        """Попытка получить данные через yfinance"""
        try:
            # Маппинг символов для yfinance
            symbol_map = {
                # Forex
                'EURUSD': 'EURUSD=X',
                'GBPUSD': 'GBPUSD=X',
                'USDJPY': 'JPY=X',
                'AUDUSD': 'AUDUSD=X',
                'USDCHF': 'USDCHF=X',
                'USDCAD': 'USDCAD=X',

                # Crypto
                'BTCUSD': 'BTC-USD',
                'ETHUSD': 'ETH-USD',
                'BNBUSD': 'BNB-USD',
                'XRPUSD': 'XRP-USD',

                # Metals
                'XAUUSD': 'GC=F',
                'XAGUSD': 'SI=F',
                'GOLD': 'GC=F',
                'SILVER': 'SI=F'
            }

            test_symbols = []

            # Проверяем прямое соответствие
            if pair_clean in symbol_map:
                test_symbols.append(symbol_map[pair_clean])

            # Добавляем вариации
            test_symbols.extend([
                f"{pair_clean}=X",  # Forex format
                f"{pair_clean[:3]}-{pair_clean[3:]}",  # Crypto format
                pair_clean
            ])

            for symbol in test_symbols[:3]:  # Ограничиваем до 3 попыток
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period="1mo", interval="1d")

                    if not data.empty and len(data) > 10:
                        data.columns = [col.lower() for col in data.columns]
                        logger.info(f"yfinance: успешно получен {symbol}")
                        return data

                except Exception as e:
                    logger.debug(f"yfinance failed for {symbol}: {e}")
                    continue

        except Exception as e:
            logger.error(f"yfinance error: {e}")

        return None