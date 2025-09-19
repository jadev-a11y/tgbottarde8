"""
Keng qamrovli signal tahlili va news integratsiyasi
Detailed signal analysis with news integration and comprehensive market data
"""
import asyncio
import aiohttp
#import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
#import talib
import logging
from bs4 import BeautifulSoup
import json
import re

class EconomicNewsProvider:
    """Economic news va calendar events provider"""

    def __init__(self):
        self.session = None
        self.news_cache = {}
        self.cache_duration = 1800  # 30 daqiqa

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )

    async def get_forex_factory_events(self) -> List[Dict]:
        """Forex Factory kalendar eventlarini olish"""
        await self.init_session()

        try:
            # Forex Factory calendar scraping
            url = "https://www.forexfactory.com/calendar"

            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    events = []
                    calendar_rows = soup.find_all('tr', class_=['calendar__row', 'calendar_row'])

                    for row in calendar_rows[:10]:  # Oxirgi 10 ta event
                        try:
                            time_elem = row.find('td', class_='calendar__time')
                            currency_elem = row.find('td', class_='calendar__currency')
                            event_elem = row.find('td', class_='calendar__event')
                            impact_elem = row.find('span', class_='calendar__impact')

                            if event_elem and currency_elem:
                                events.append({
                                    'time': time_elem.text.strip() if time_elem else 'TBA',
                                    'currency': currency_elem.text.strip() if currency_elem else '',
                                    'event': event_elem.text.strip(),
                                    'impact': self._get_impact_level(impact_elem),
                                    'source': 'ForexFactory'
                                })
                        except Exception:
                            continue

                    return events

        except Exception as e:
            logging.error(f"Forex Factory scraping xatosi: {e}")

        return []

    async def get_investing_news(self, pair: str) -> List[Dict]:
        """Investing.com dan news olish"""
        await self.init_session()

        try:
            # Currency-specific news URL
            currency = pair[:3] if len(pair) >= 3 else 'USD'
            url = f"https://www.investing.com/currencies/{currency.lower()}-news"

            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    news_items = []
                    articles = soup.find_all('div', class_=['largeTitle', 'textDiv'])[:5]

                    for article in articles:
                        try:
                            title_elem = article.find('a')
                            if title_elem:
                                news_items.append({
                                    'title': title_elem.text.strip(),
                                    'currency': currency,
                                    'source': 'Investing.com',
                                    'timestamp': datetime.now(),
                                    'relevance': self._calculate_news_relevance(title_elem.text, pair)
                                })
                        except Exception:
                            continue

                    return news_items

        except Exception as e:
            logging.error(f"Investing.com news xatosi: {e}")

        return []

    def _get_impact_level(self, impact_elem) -> str:
        """Impact darajasini aniqlash"""
        if not impact_elem:
            return 'LOW'

        impact_class = impact_elem.get('class', [])
        if 'icon--ff-impact-red' in impact_class or 'red' in str(impact_class):
            return 'HIGH'
        elif 'icon--ff-impact-ora' in impact_class or 'orange' in str(impact_class):
            return 'MEDIUM'
        else:
            return 'LOW'

    def _calculate_news_relevance(self, title: str, pair: str) -> float:
        """News relevance calculator"""
        base_currency = pair[:3]
        quote_currency = pair[3:6] if len(pair) >= 6 else 'USD'

        relevance = 0.0
        title_lower = title.lower()

        # Currency mentions
        if base_currency.lower() in title_lower:
            relevance += 0.5
        if quote_currency.lower() in title_lower:
            relevance += 0.3

        # High-impact keywords
        high_impact_words = ['fed', 'ecb', 'boe', 'boj', 'rate', 'inflation', 'gdp', 'employment', 'crisis']
        for word in high_impact_words:
            if word in title_lower:
                relevance += 0.2

        return min(relevance, 1.0)

    async def close_session(self):
        if self.session:
            await self.session.close()

class ComprehensiveSignalAnalyzer:
    """Keng qamrovli signal tahlilchisi"""

    def __init__(self):
        self.news_provider = EconomicNewsProvider()

    def calculate_support_resistance_zones(self, data: pd.DataFrame) -> Dict[str, List[float]]:
        """Professional support va resistance zonalarini hisoblash"""
        highs = data['high'].values
        lows = data['low'].values
        close = data['close'].values

        # Pivot points
        pivots = []
        for i in range(5, len(highs) - 5):
            # High pivot
            if all(highs[i] >= highs[i-j] for j in range(1, 6)) and all(highs[i] >= highs[i+j] for j in range(1, 6)):
                pivots.append(('resistance', highs[i]))
            # Low pivot
            if all(lows[i] <= lows[i-j] for j in range(1, 6)) and all(lows[i] <= lows[i+j] for j in range(1, 6)):
                pivots.append(('support', lows[i]))

        # Zonalarni guruhlash
        support_zones = []
        resistance_zones = []

        for zone_type, price in pivots:
            if zone_type == 'support':
                support_zones.append(price)
            else:
                resistance_zones.append(price)

        # Yaqin zonalarni birlashtirish
        current_price = close[-1]

        def merge_nearby_levels(levels, threshold=0.001):
            if not levels:
                return []
            levels = sorted(set(levels))
            merged = [levels[0]]

            for level in levels[1:]:
                if abs(level - merged[-1]) / current_price > threshold:
                    merged.append(level)

            return merged[:10]  # Eng muhim 10 ta zona

        return {
            'support_zones': merge_nearby_levels(support_zones),
            'resistance_zones': merge_nearby_levels(resistance_zones),
            'current_price': current_price
        }

    def calculate_fibonacci_levels(self, data: pd.DataFrame, lookback: int = 100) -> Dict[str, float]:
        """Fibonacci retracement levellarini hisoblash"""
        recent_data = data.tail(lookback)
        high_price = recent_data['high'].max()
        low_price = recent_data['low'].min()

        diff = high_price - low_price

        # Trend direction aniqlash
        sma_20 = talib.SMA(recent_data['close'], 20)
        trend_up = recent_data['close'].iloc[-1] > sma_20.iloc[-1]

        if trend_up:
            # Uptrend - retracement downward dan
            levels = {
                'fibonacci_100': high_price,
                'fibonacci_786': high_price - 0.786 * diff,
                'fibonacci_618': high_price - 0.618 * diff,
                'fibonacci_50': high_price - 0.5 * diff,
                'fibonacci_382': high_price - 0.382 * diff,
                'fibonacci_236': high_price - 0.236 * diff,
                'fibonacci_0': low_price
            }
        else:
            # Downtrend - retracement upward ga
            levels = {
                'fibonacci_0': high_price,
                'fibonacci_236': low_price + 0.236 * diff,
                'fibonacci_382': low_price + 0.382 * diff,
                'fibonacci_50': low_price + 0.5 * diff,
                'fibonacci_618': low_price + 0.618 * diff,
                'fibonacci_786': low_price + 0.786 * diff,
                'fibonacci_100': low_price
            }

        return levels

    def calculate_pips_and_targets(self, pair: str, entry_price: float,
                                 stop_loss: float, take_profit: float) -> Dict[str, float]:
        """Pips, risk/reward va boshqa hisob-kitoblar"""

        # Pip value aniqlash
        if 'JPY' in pair:
            pip_size = 0.01
        else:
            pip_size = 0.0001

        # Pips hisoblash
        if entry_price > stop_loss:  # Long position
            stop_loss_pips = (entry_price - stop_loss) / pip_size
            take_profit_pips = (take_profit - entry_price) / pip_size
        else:  # Short position
            stop_loss_pips = (stop_loss - entry_price) / pip_size
            take_profit_pips = (entry_price - take_profit) / pip_size

        risk_reward_ratio = take_profit_pips / stop_loss_pips if stop_loss_pips > 0 else 0

        # Position sizing (1% risk model)
        account_balance = 10000  # Default account
        risk_percentage = 0.01
        position_size = (account_balance * risk_percentage) / (stop_loss_pips * 10)  # 10$ per pip for standard lot

        return {
            'stop_loss_pips': round(stop_loss_pips, 1),
            'take_profit_pips': round(take_profit_pips, 1),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'position_size': round(position_size, 2),
            'pip_value': pip_size,
            'max_loss_usd': round(stop_loss_pips * 10, 2),  # Assuming $10/pip
            'max_profit_usd': round(take_profit_pips * 10, 2)
        }

    async def generate_comprehensive_signal(self, pair: str, market_data: pd.DataFrame,
                                          basic_signal: Dict) -> Dict:
        """Keng qamrovli signal yaratish"""

        if len(market_data) < 50:
            return basic_signal

        current_price = market_data['close'].iloc[-1]

        # Technical analysis
        rsi = talib.RSI(market_data['close'], 14)
        macd, signal_line, histogram = talib.MACD(market_data['close'])
        bb_upper, bb_middle, bb_lower = talib.BBANDS(market_data['close'])
        atr = talib.ATR(market_data['high'], market_data['low'], market_data['close'], 14)

        # Support/Resistance zones
        zones = self.calculate_support_resistance_zones(market_data)

        # Fibonacci levels
        fib_levels = self.calculate_fibonacci_levels(market_data)

        # News analysis
        try:
            forex_events = await self.news_provider.get_forex_factory_events()
            relevant_news = await self.news_provider.get_investing_news(pair)
        except Exception as e:
            logging.error(f"News olishda xato: {e}")
            forex_events = []
            relevant_news = []

        # Signal detalization
        signal_details = self._generate_detailed_analysis(
            pair, current_price, market_data, rsi, macd, signal_line,
            bb_upper, bb_middle, bb_lower, atr, zones, fib_levels
        )

        # Pips calculation
        entry_price = current_price
        if basic_signal.get('signal') == 'SOTIB_OLISH':
            stop_loss = current_price - (atr.iloc[-1] * 2)
            take_profit = current_price + (atr.iloc[-1] * 3)
        else:
            stop_loss = current_price + (atr.iloc[-1] * 2)
            take_profit = current_price - (atr.iloc[-1] * 3)

        pips_data = self.calculate_pips_and_targets(pair, entry_price, stop_loss, take_profit)

        # Comprehensive result
        comprehensive_signal = {
            **basic_signal,
            'detailed_analysis': signal_details,
            'technical_indicators': {
                'RSI': round(rsi.iloc[-1], 2) if len(rsi) > 0 else None,
                'MACD': round(macd.iloc[-1], 5) if len(macd) > 0 else None,
                'MACD_Signal': round(signal_line.iloc[-1], 5) if len(signal_line) > 0 else None,
                'BB_Position': self._get_bb_position(current_price, bb_upper.iloc[-1], bb_lower.iloc[-1]),
                'ATR': round(atr.iloc[-1], 5) if len(atr) > 0 else None
            },
            'support_resistance': zones,
            'fibonacci_levels': fib_levels,
            'pips_analysis': pips_data,
            'news_impact': {
                'forex_factory_events': forex_events[:3],  # Top 3 events
                'relevant_news': relevant_news[:2],  # Top 2 news
                'overall_sentiment': self._calculate_news_sentiment(forex_events, relevant_news, pair)
            },
            'trade_management': {
                'entry_price': round(entry_price, 5),
                'stop_loss': round(stop_loss, 5),
                'take_profit': round(take_profit, 5),
                'trailing_stop': round(current_price - (atr.iloc[-1] * 1.5), 5),
                'break_even_level': round(current_price + (atr.iloc[-1] * 0.5), 5) if basic_signal.get('signal') == 'SOTIB_OLISH' else round(current_price - (atr.iloc[-1] * 0.5), 5)
            },
            'market_context': self._get_market_context(pair, market_data),
            'confidence_breakdown': self._calculate_confidence_breakdown(rsi, macd, signal_line, zones, current_price)
        }

        return comprehensive_signal

    def _generate_detailed_analysis(self, pair: str, current_price: float, data: pd.DataFrame,
                                  rsi, macd, signal_line, bb_upper, bb_middle, bb_lower,
                                  atr, zones, fib_levels) -> str:
        """Batafsil tahlil matni yaratish"""

        analysis_parts = []

        # Trend analysis
        sma_20 = talib.SMA(data['close'], 20)
        sma_50 = talib.SMA(data['close'], 50)

        if len(sma_20) > 0 and len(sma_50) > 0:
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                trend = "yuqoriga yo'nalgan"
                trend_strength = "kuchli" if sma_20.iloc[-1] > sma_50.iloc[-1] * 1.005 else "o'rtacha"
            else:
                trend = "pastga yo'nalgan"
                trend_strength = "kuchli" if sma_20.iloc[-1] < sma_50.iloc[-1] * 0.995 else "o'rtacha"

            analysis_parts.append(f"🔹 Asosiy trend: {trend_strength} {trend} trend kuzatilmoqda (SMA20: {sma_20.iloc[-1]:.5f}, SMA50: {sma_50.iloc[-1]:.5f})")

        # RSI analysis
        if len(rsi) > 0:
            rsi_value = rsi.iloc[-1]
            if rsi_value > 70:
                rsi_desc = "overbought zonada - narx tuzatish ehtimoli yuqori"
            elif rsi_value < 30:
                rsi_desc = "oversold zonada - qaytish rallisi kutilmoqda"
            else:
                rsi_desc = "neytral zonada - trend davom etishi mumkin"

            analysis_parts.append(f"🔹 RSI ko'rsatkichi: {rsi_value:.1f} - {rsi_desc}")

        # MACD analysis
        if len(macd) > 1 and len(signal_line) > 1:
            if macd.iloc[-1] > signal_line.iloc[-1] and macd.iloc[-2] <= signal_line.iloc[-2]:
                macd_desc = "ijobiy crossover - bullish momentum boshlanmoqda"
            elif macd.iloc[-1] < signal_line.iloc[-1] and macd.iloc[-2] >= signal_line.iloc[-2]:
                macd_desc = "salbiy crossover - bearish momentum kuchaymoqda"
            elif macd.iloc[-1] > signal_line.iloc[-1]:
                macd_desc = "signal chizig'i ustida - bullish momentum davom etmoqda"
            else:
                macd_desc = "signal chizig'i ostida - bearish pressure saqlanmoqda"

            analysis_parts.append(f"🔹 MACD tahlili: {macd_desc}")

        # Bollinger Bands analysis
        if len(bb_upper) > 0 and len(bb_lower) > 0:
            bb_position = self._get_bb_position(current_price, bb_upper.iloc[-1], bb_lower.iloc[-1])
            if bb_position == "Yuqori chegara yaqinida":
                bb_desc = "Bollinger Bands yuqori chegarasida - qarshilik zonasi yaqin"
            elif bb_position == "Pastki chegara yaqinida":
                bb_desc = "Bollinger Bands pastki chegarasida - support zonasi yaqin"
            else:
                bb_desc = "Bollinger Bands o'rtasida - normal price action"

            analysis_parts.append(f"🔹 Volatillik tahlili: {bb_desc}")

        # Support/Resistance analysis
        nearest_support = max([s for s in zones['support_zones'] if s < current_price], default=None)
        nearest_resistance = min([r for r in zones['resistance_zones'] if r > current_price], default=None)

        if nearest_support:
            support_distance = ((current_price - nearest_support) / current_price) * 100
            analysis_parts.append(f"🔹 Eng yaqin support: {nearest_support:.5f} ({support_distance:.2f}% pastda)")

        if nearest_resistance:
            resistance_distance = ((nearest_resistance - current_price) / current_price) * 100
            analysis_parts.append(f"🔹 Eng yaqin resistance: {nearest_resistance:.5f} ({resistance_distance:.2f}% yuqorida)")

        # Volume analysis
        if 'volume' in data.columns:
            volume_ma = talib.SMA(data['volume'], 20)
            if len(volume_ma) > 0:
                current_volume = data['volume'].iloc[-1]
                avg_volume = volume_ma.iloc[-1]

                if current_volume > avg_volume * 1.5:
                    volume_desc = "o'rtachadan ancha yuqori - kuchli faollik"
                elif current_volume > avg_volume * 1.2:
                    volume_desc = "o'rtachadan yuqori - yaxshi faollik"
                elif current_volume < avg_volume * 0.8:
                    volume_desc = "o'rtachadan past - zaif faollik"
                else:
                    volume_desc = "o'rtacha darajada - normal faollik"

                analysis_parts.append(f"🔹 Savdo hajmi: {volume_desc}")

        # Fibonacci analysis
        fib_50 = fib_levels.get('fibonacci_50')
        fib_618 = fib_levels.get('fibonacci_618')

        if fib_50 and abs(current_price - fib_50) / current_price < 0.002:
            analysis_parts.append(f"🔹 Fibonacci: Narx 50% retracement darajasida ({fib_50:.5f}) - muhim qaror nuqtasi")
        elif fib_618 and abs(current_price - fib_618) / current_price < 0.002:
            analysis_parts.append(f"🔹 Fibonacci: Narx 61.8% retracement darajasida ({fib_618:.5f}) - golden ratio support/resistance")

        return "\n".join(analysis_parts)

    def _get_bb_position(self, price: float, upper: float, lower: float) -> str:
        """Bollinger Bands pozitsiyasini aniqlash"""
        middle = (upper + lower) / 2

        if price > upper * 0.98:
            return "Yuqori chegara yaqinida"
        elif price < lower * 1.02:
            return "Pastki chegara yaqinida"
        elif price > middle:
            return "O'rta va yuqori chegara orasida"
        else:
            return "Pastki va o'rta chegara orasida"

    def _calculate_news_sentiment(self, forex_events: List[Dict],
                                relevant_news: List[Dict], pair: str) -> str:
        """News sentiment hisoblash"""
        sentiment_score = 0

        # High impact events
        high_impact_count = sum(1 for event in forex_events if event.get('impact') == 'HIGH')
        sentiment_score += high_impact_count * 0.3

        # Relevant news count
        sentiment_score += len(relevant_news) * 0.1

        if sentiment_score > 0.5:
            return "YUQORI TA'SIR"
        elif sentiment_score > 0.2:
            return "O'RTACHA TA'SIR"
        else:
            return "PAST TA'SIR"

    def _get_market_context(self, pair: str, data: pd.DataFrame) -> Dict[str, str]:
        """Market context ma'lumotlari"""
        volatility = data['close'].pct_change().std() * np.sqrt(252) * 100

        if 'XAU' in pair:
            context = "Qimmatbaho metallar bozori - geopolitik xavflar va inflatsiya kutishlari ta'sir qiladi"
        elif 'USD' in pair and 'EUR' in pair:
            context = "Eng faol valyuta jufti - AQSh va Eurozone iqtisodiy ma'lumotlari asosiy ta'sir ko'rsatadi"
        elif 'OIL' in pair:
            context = "Energiya bozori - OPEC+ qarori, inventar ma'lumotlari va global iqtisod ta'sir qiladi"
        elif 'BTC' in pair or 'ETH' in pair:
            context = "Kripto valyuta bozori - institusional qabul va regulyativ yangiliklar muhim"
        else:
            context = "Forex bozori - markaziy bank siyosati va iqtisodiy ko'rsatkichlar asosiy omillar"

        session = self._get_trading_session()

        return {
            'market_type': context,
            'volatility_level': f"{volatility:.1f}% yillik",
            'trading_session': session,
            'liquidity': "Yuqori" if session in ["London", "New York"] else "O'rtacha"
        }

    def _get_trading_session(self) -> str:
        """Joriy savdo sessiyasini aniqlash"""
        utc_hour = datetime.utcnow().hour

        if 0 <= utc_hour < 7:
            return "Sydney/Tokyo"
        elif 7 <= utc_hour < 15:
            return "London"
        elif 15 <= utc_hour < 22:
            return "New York"
        else:
            return "Sydney/Tokyo"

    def _calculate_confidence_breakdown(self, rsi, macd, signal_line, zones, current_price) -> Dict[str, int]:
        """Confidence breakdown hisoblash"""
        breakdown = {
            'technical_indicators': 0,
            'support_resistance': 0,
            'trend_analysis': 0,
            'volume_confirmation': 0,
            'news_sentiment': 0
        }

        # Technical indicators
        if len(rsi) > 0:
            if 30 < rsi.iloc[-1] < 70:
                breakdown['technical_indicators'] += 10
            elif rsi.iloc[-1] < 30 or rsi.iloc[-1] > 70:
                breakdown['technical_indicators'] += 15  # Strong signal

        if len(macd) > 1 and len(signal_line) > 1:
            if macd.iloc[-1] > signal_line.iloc[-1]:
                breakdown['technical_indicators'] += 15

        # Support/Resistance
        near_level = False
        for support in zones['support_zones']:
            if abs(current_price - support) / current_price < 0.001:
                near_level = True
                break
        for resistance in zones['resistance_zones']:
            if abs(current_price - resistance) / current_price < 0.001:
                near_level = True
                break

        if near_level:
            breakdown['support_resistance'] = 20
        else:
            breakdown['support_resistance'] = 10

        # Default values for other factors
        breakdown['trend_analysis'] = 15
        breakdown['volume_confirmation'] = 10
        breakdown['news_sentiment'] = 10

        return breakdown

    async def close(self):
        """Resources yopish"""
        await self.news_provider.close_session()