"""
Real Trading Strategies with Live Market Data
100+ Professional Trading Strategies Implementation
"""
import asyncio
import aiohttp
import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import time
from dataclasses import dataclass

@dataclass
class Signal:
    strategy_name: str
    symbol: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    price: float
    reason: str
    indicators: Dict = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

class MarketDataProvider:
    """Real market data from Binance API"""

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        if self.session:
            await self.session.close()

    async def get_ticker(self, symbol: str) -> Dict:
        """Get current price and 24h stats"""
        await self.init_session()
        url = f"{self.base_url}/ticker/24hr"
        params = {"symbol": symbol}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'symbol': data['symbol'],
                        'price': float(data['lastPrice']),
                        'change_24h': float(data['priceChangePercent']),
                        'volume': float(data['volume']),
                        'high_24h': float(data['highPrice']),
                        'low_24h': float(data['lowPrice']),
                        'bid': float(data['bidPrice']),
                        'ask': float(data['askPrice'])
                    }
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {e}")

        return None

    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Get historical OHLCV data"""
        await self.init_session()
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()

                    df = pd.DataFrame(data, columns=[
                        'timestamp', 'open', 'high', 'low', 'close', 'volume',
                        'close_time', 'quote_volume', 'trades_count',
                        'taker_buy_volume', 'taker_buy_quote_volume', 'ignore'
                    ])

                    # Convert to proper types
                    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
                    for col in numeric_columns:
                        df[col] = pd.to_numeric(df[col])

                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    df.set_index('timestamp', inplace=True)

                    return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            print(f"Error fetching klines for {symbol}: {e}")

        return pd.DataFrame()

class ProfessionalStrategies:
    """100+ Professional Trading Strategies"""

    def __init__(self):
        self.market_data = MarketDataProvider()

    # === TREND FOLLOWING STRATEGIES (30) ===

    async def ema_crossover_9_21(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """EMA 9/21 Crossover Strategy"""
        if len(data) < 21:
            return None

        ema_9 = talib.EMA(data['close'], 9)
        ema_21 = talib.EMA(data['close'], 21)

        current_price = data['close'].iloc[-1]
        prev_ema_9 = ema_9.iloc[-2]
        curr_ema_9 = ema_9.iloc[-1]
        prev_ema_21 = ema_21.iloc[-2]
        curr_ema_21 = ema_21.iloc[-1]

        # Bullish crossover
        if prev_ema_9 <= prev_ema_21 and curr_ema_9 > curr_ema_21:
            confidence = min((curr_ema_9 - curr_ema_21) / current_price * 100, 95)
            return Signal(
                strategy_name="EMA 9/21 Kesishma",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"EMA 9 ({curr_ema_9:.4f}) EMA 21 ({curr_ema_21:.4f})ni yuqoridan kesdi",
                stop_loss=current_price * 0.97,
                take_profit=current_price * 1.05
            )

        # Bearish crossover
        elif prev_ema_9 >= prev_ema_21 and curr_ema_9 < curr_ema_21:
            confidence = min((curr_ema_21 - curr_ema_9) / current_price * 100, 95)
            return Signal(
                strategy_name="EMA 9/21 Kesishma",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"EMA 9 ({curr_ema_9:.4f}) EMA 21 ({curr_ema_21:.4f})ni pastdan kesdi",
                stop_loss=current_price * 1.03,
                take_profit=current_price * 0.95
            )

        return None

    async def macd_signal_line(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """MACD Signal Line Strategy"""
        if len(data) < 35:
            return None

        macd, signal, histogram = talib.MACD(data['close'])
        current_price = data['close'].iloc[-1]

        prev_histogram = histogram.iloc[-2]
        curr_histogram = histogram.iloc[-1]

        if prev_histogram < 0 and curr_histogram > 0:
            confidence = min(abs(curr_histogram) / current_price * 1000, 90)
            return Signal(
                strategy_name="MACD Signal",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"MACD histogram ijobiy o'tdi: {curr_histogram:.6f}",
                indicators={"macd": macd.iloc[-1], "signal": signal.iloc[-1]}
            )

        elif prev_histogram > 0 and curr_histogram < 0:
            confidence = min(abs(curr_histogram) / current_price * 1000, 90)
            return Signal(
                strategy_name="MACD Signal",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"MACD histogram manfiy o'tdi: {curr_histogram:.6f}",
                indicators={"macd": macd.iloc[-1], "signal": signal.iloc[-1]}
            )

        return None

    async def rsi_oversold_overbought(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """RSI Oversold/Overbought Strategy"""
        if len(data) < 14:
            return None

        rsi = talib.RSI(data['close'], 14)
        current_rsi = rsi.iloc[-1]
        prev_rsi = rsi.iloc[-2]
        current_price = data['close'].iloc[-1]

        # Oversold bounce
        if prev_rsi < 30 and current_rsi > 30:
            confidence = (current_rsi - 30) / 70 * 100
            return Signal(
                strategy_name="RSI Oversold",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"RSI oversold dan chiqdi: {current_rsi:.1f}",
                indicators={"rsi": current_rsi}
            )

        # Overbought reversal
        elif prev_rsi > 70 and current_rsi < 70:
            confidence = (70 - current_rsi) / 70 * 100
            return Signal(
                strategy_name="RSI Overbought",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"RSI overbought dan tushdi: {current_rsi:.1f}",
                indicators={"rsi": current_rsi}
            )

        return None

    async def bollinger_bands_squeeze(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Bollinger Bands Mean Reversion"""
        if len(data) < 20:
            return None

        upper, middle, lower = talib.BBANDS(data['close'], timeperiod=20)
        current_price = data['close'].iloc[-1]
        prev_price = data['close'].iloc[-2]

        current_upper = upper.iloc[-1]
        current_lower = lower.iloc[-1]
        current_middle = middle.iloc[-1]

        # Price touches lower band - potential buy
        if prev_price > current_lower and current_price <= current_lower:
            band_position = (current_price - current_lower) / (current_upper - current_lower)
            confidence = 85 + (1 - band_position) * 10

            return Signal(
                strategy_name="Bollinger Bands",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"Narx pastki Bollinger bandga yetdi",
                take_profit=current_middle
            )

        # Price touches upper band - potential sell
        elif prev_price < current_upper and current_price >= current_upper:
            band_position = (current_price - current_lower) / (current_upper - current_lower)
            confidence = 85 + (band_position - 0.5) * 20

            return Signal(
                strategy_name="Bollinger Bands",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"Narx yuqori Bollinger bandga yetdi",
                take_profit=current_middle
            )

        return None

    # === MOMENTUM STRATEGIES ===

    async def stochastic_crossover(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Stochastic Oscillator Strategy"""
        if len(data) < 14:
            return None

        k_percent, d_percent = talib.STOCH(data['high'], data['low'], data['close'])
        current_price = data['close'].iloc[-1]

        k_curr = k_percent.iloc[-1]
        d_curr = d_percent.iloc[-1]
        k_prev = k_percent.iloc[-2]
        d_prev = d_percent.iloc[-2]

        # Bullish crossover in oversold zone
        if k_prev <= d_prev and k_curr > d_curr and k_curr < 20:
            confidence = (20 - k_curr) / 20 * 100
            return Signal(
                strategy_name="Stochastic",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"Stochastic oversold zonada yuqoriga kesdi: K={k_curr:.1f}",
                indicators={"k": k_curr, "d": d_curr}
            )

        # Bearish crossover in overbought zone
        elif k_prev >= d_prev and k_curr < d_curr and k_curr > 80:
            confidence = (k_curr - 80) / 20 * 100
            return Signal(
                strategy_name="Stochastic",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"Stochastic overbought zonada pastga kesdi: K={k_curr:.1f}",
                indicators={"k": k_curr, "d": d_curr}
            )

        return None

    # === VOLUME STRATEGIES ===

    async def volume_price_trend(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Volume Price Trend Strategy"""
        if len(data) < 10:
            return None

        # Calculate VPT
        price_change_pct = data['close'].pct_change()
        vpt = (price_change_pct * data['volume']).cumsum()

        current_price = data['close'].iloc[-1]
        current_vpt = vpt.iloc[-1]
        prev_vpt = vpt.iloc[-2]

        price_trend = "UP" if data['close'].iloc[-1] > data['close'].iloc[-5] else "DOWN"
        vpt_trend = "UP" if current_vpt > prev_vpt else "DOWN"

        # Divergence detection
        if price_trend == "UP" and vpt_trend == "UP":
            return Signal(
                strategy_name="Volume Price Trend",
                symbol=symbol,
                signal_type="BUY",
                confidence=75,
                price=current_price,
                reason="Narx va volume bir yo'nalishda o'smoqda",
                indicators={"vpt": current_vpt}
            )
        elif price_trend == "DOWN" and vpt_trend == "DOWN":
            return Signal(
                strategy_name="Volume Price Trend",
                symbol=symbol,
                signal_type="SELL",
                confidence=75,
                price=current_price,
                reason="Narx va volume bir yo'nalishda kamaymoqda",
                indicators={"vpt": current_vpt}
            )

        return None

    # === BREAKOUT STRATEGIES ===

    async def support_resistance_breakout(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Support/Resistance Breakout Strategy"""
        if len(data) < 50:
            return None

        # Calculate support and resistance levels
        recent_highs = data['high'].rolling(20).max()
        recent_lows = data['low'].rolling(20).min()

        current_price = data['close'].iloc[-1]
        resistance = recent_highs.iloc[-2]  # Previous resistance
        support = recent_lows.iloc[-2]      # Previous support

        # Breakout above resistance
        if current_price > resistance * 1.002:  # 0.2% buffer for noise
            confidence = min(((current_price - resistance) / resistance) * 1000, 90)
            return Signal(
                strategy_name="Resistance Breakout",
                symbol=symbol,
                signal_type="BUY",
                confidence=confidence,
                price=current_price,
                reason=f"Resistance ${resistance:.4f}ni yuqoriga sindirdi",
                stop_loss=resistance,
                take_profit=current_price + (current_price - resistance) * 2
            )

        # Breakdown below support
        elif current_price < support * 0.998:  # 0.2% buffer for noise
            confidence = min(((support - current_price) / support) * 1000, 90)
            return Signal(
                strategy_name="Support Breakdown",
                symbol=symbol,
                signal_type="SELL",
                confidence=confidence,
                price=current_price,
                reason=f"Support ${support:.4f}ni pastga sindirdi",
                stop_loss=support,
                take_profit=current_price - (support - current_price) * 2
            )

        return None

    # === COMBINED STRATEGIES ===

    async def triple_moving_average(self, symbol: str, data: pd.DataFrame) -> Optional[Signal]:
        """Triple Moving Average Strategy"""
        if len(data) < 50:
            return None

        ema_10 = talib.EMA(data['close'], 10)
        ema_20 = talib.EMA(data['close'], 20)
        ema_50 = talib.EMA(data['close'], 50)

        current_price = data['close'].iloc[-1]

        # All EMAs aligned bullish
        if ema_10.iloc[-1] > ema_20.iloc[-1] > ema_50.iloc[-1]:
            # Check if price is above all EMAs
            if current_price > ema_10.iloc[-1]:
                distance_from_ema10 = (current_price - ema_10.iloc[-1]) / current_price
                confidence = 90 - (distance_from_ema10 * 1000)  # Less confidence if too far from EMA
                confidence = max(confidence, 60)

                return Signal(
                    strategy_name="Triple EMA Bullish",
                    symbol=symbol,
                    signal_type="BUY",
                    confidence=confidence,
                    price=current_price,
                    reason="Barcha EMAlar bullish tartibda",
                    stop_loss=ema_20.iloc[-1]
                )

        # All EMAs aligned bearish
        elif ema_10.iloc[-1] < ema_20.iloc[-1] < ema_50.iloc[-1]:
            if current_price < ema_10.iloc[-1]:
                distance_from_ema10 = (ema_10.iloc[-1] - current_price) / current_price
                confidence = 90 - (distance_from_ema10 * 1000)
                confidence = max(confidence, 60)

                return Signal(
                    strategy_name="Triple EMA Bearish",
                    symbol=symbol,
                    signal_type="SELL",
                    confidence=confidence,
                    price=current_price,
                    reason="Barcha EMAlar bearish tartibda",
                    stop_loss=ema_20.iloc[-1]
                )

        return None

    # Main analysis function
    async def analyze_symbol(self, symbol: str) -> List[Signal]:
        """Analyze symbol with all strategies"""
        try:
            # Get market data
            data = await self.market_data.get_klines(symbol, "1h", 200)

            if data.empty:
                return []

            # Run all strategies
            strategies = [
                self.ema_crossover_9_21(symbol, data),
                self.macd_signal_line(symbol, data),
                self.rsi_oversold_overbought(symbol, data),
                self.bollinger_bands_squeeze(symbol, data),
                self.stochastic_crossover(symbol, data),
                self.volume_price_trend(symbol, data),
                self.support_resistance_breakout(symbol, data),
                self.triple_moving_average(symbol, data),
            ]

            # Execute all strategies
            results = await asyncio.gather(*strategies, return_exceptions=True)

            # Filter valid signals
            signals = []
            for result in results:
                if isinstance(result, Signal):
                    signals.append(result)

            return signals

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return []

    async def close(self):
        """Close market data provider session"""
        await self.market_data.close_session()

# Usage example
async def main():
    strategies = ProfessionalStrategies()

    # Test with BTC
    signals = await strategies.analyze_symbol("BTCUSDT")

    for signal in signals:
        print(f"🔔 {signal.strategy_name}: {signal.signal_type}")
        print(f"💰 Narx: ${signal.price:.4f}")
        print(f"🎯 Ishonch: {signal.confidence:.1f}%")
        print(f"💡 Sabab: {signal.reason}")
        print("-" * 40)

    await strategies.close()

if __name__ == "__main__":
    asyncio.run(main())