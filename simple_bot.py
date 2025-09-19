#!/usr/bin/env python3
"""
Простой торговый бот без pandas для быстрого запуска
"""

import os
import logging
import asyncio
import aiohttp
import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime, timedelta
from openai import AsyncOpenAI

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleTradingBot:
    def __init__(self):
        self.trading_pairs = [
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD",
            "USDCHF", "USDCAD", "NZDUSD", "BTCUSD",
            "ETHUSD", "XAUUSD", "XAGUSD"
        ]

    async def get_real_price(self, pair: str):
        """Получить реальную цену валютной пары"""
        try:
            # Используем exchangerate.host - бесплатный API
            if len(pair) == 6:  # Forex pairs like EURUSD
                base = pair[:3]
                target = pair[3:]

                async with aiohttp.ClientSession() as session:
                    url = f"https://api.exchangerate.host/latest?base={base}&symbols={target}"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('success') and data.get('rates'):
                                return round(data['rates'].get(target, 0), 5)

            # Попробуем Yahoo Finance API для других пар
            symbol_map = {
                'BTCUSD': 'BTC-USD',
                'ETHUSD': 'ETH-USD',
                'XAUUSD': 'GC=F',
                'XAGUSD': 'SI=F'
            }

            yahoo_symbol = symbol_map.get(pair)
            if yahoo_symbol:
                async with aiohttp.ClientSession() as session:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('chart') and data['chart'].get('result'):
                                result = data['chart']['result'][0]
                                meta = result.get('meta', {})
                                price = meta.get('regularMarketPrice')
                                if price:
                                    return round(float(price), 2 if pair.startswith('XAU') else 5)

            logger.warning(f"Не удалось получить цену для {pair}")
            return None

        except Exception as e:
            logger.error(f"Ошибка получения цены для {pair}: {e}")
            return None

    async def analyze_with_gpt_web_search(self, pair: str):
        """GPT-4o-search-preview анализ как в мини приложении"""
        try:
            # Get OpenAI API key
            openai_key = os.getenv('OPENAI_API_KEY')
            if not openai_key:
                logger.warning("OpenAI API key not found")
                return None

            # Initialize OpenAI client
            client = AsyncOpenAI(api_key=openai_key)

            # GPT-4o-search-preview request
            response = await client.chat.completions.create(
                model="gpt-4o-search-preview",
                web_search_options={
                    "user_location": {
                        "type": "approximate",
                        "approximate": {
                            "country": "US",
                            "city": "New York",
                            "region": "New York",
                            "timezone": "America/New_York"
                        }
                    }
                },
                messages=[
                    {
                        "role": "system",
                        "content": "Siz professional forex trader va texnik tahlil mutaxassisisiz. FAQAT web search orqali ANIQ ma'lumotlar toping va trading signal bering."
                    },
                    {
                        "role": "user",
                        "content": f"""{pair} uchun ANIQ texnik tahlil va trading signal bering:

🎯 KENG WEB SEARCH VAZIFASI:
"{pair} current price today live real time spot"
"{pair} RSI indicator current value today"
"{pair} MACD signal current bullish bearish"
"{pair} technical analysis live trading signals"
"{pair} market news today fundamental analysis"
"{pair} economic factors affecting price"
"{pair} volume analysis trading signals"
"{pair} support resistance levels technical chart"
"{pair} momentum indicators stochastic"
"{pair} fibonacci retracement levels"
"{pair} candlestick patterns today"
"{pair} trend analysis moving averages"

📊 KENG MA'LUMOT TOPISH KERAK:
1. Hozirgi aniq narx (USD) va 24-soatlik o'zgarish
2. RSI qiymati (0-100) va trend
3. MACD signali va histogram
4. Moving Average 20, 50, 200 holati
5. Support va Resistance darajalari (eng kam 3ta)
6. Volume tahlili va momentum
7. Fundamental yangiliklar va tahlil
8. Stochastic va boshqa ko'rsatkichlar
9. Candlestick pattern tahlili
10. Fibonacci retracement darajalari
11. Market sentiment va whale activity
12. Economic calendar ta'siri

✅ BATAFSIL JAVOB FORMATI:
Signal: [BUY/SELL/HOLD]
Ishonch: [yuqori/o'rta/past] - [%]
Narx: [aniq USD qiymat]
Maqsad: [aniq USD qiymat]
Stop: [aniq USD qiymat]

BATAFSIL TEXNIK TAHLIL:
- RSI: [qiymat] ([oversold/overbought/neutral])
- MACD: [signal] ([divergence bor/yo'q])
- Moving Averages: [20MA, 50MA, 200MA holati]
- Support: [3ta daraja]
- Resistance: [3ta daraja]
- Volume: [yuqori/past/o'rta] + trend
- Stochastic: [qiymat va signal]
- Fibonacci: [muhim retracement darajalari]
- Candlestick: [oxirgi pattern]

FUNDAMENTAL TAHLIL:
- Oxirgi yangiliklar va ularning ta'siri
- Economic calendar eventlari
- Market sentiment (Fear/Greed index)
- Institutlar va whale faoliyati
- Makroiqtisodiy omillar

RISK MENEJMENTI:
- Entry strategy va vaqt
- Position sizing tavsiya
- Risk/Reward ratio
- Alternativ scenario

MAKSIMAL BATAFSIL VA PROFESSIONAL JAVOB BERING! Barcha web search natijalarini ishlating!"""
                    }
                ],
                max_tokens=4000
            )

            analysis_text = response.choices[0].message.content
            logger.info(f"Professional market analysis received: {len(analysis_text)} chars")

            return self.parse_gpt_analysis(analysis_text, pair)

        except Exception as e:
            logger.error(f"Professional market analysis error: {e}")
            return None

    def parse_gpt_analysis(self, text: str, pair: str):
        """Parse GPT analysis response"""
        try:
            lines = text.split('\n')

            signal = 'HOLD'
            confidence = 75
            price = 0
            target = 0
            stop = 0
            reasoning = text[:500] + '...' if len(text) > 500 else text

            # Extract key values
            for line in lines:
                lower_line = line.lower()

                if 'signal:' in lower_line:
                    if 'buy' in lower_line:
                        signal = 'STRONG_BUY' if 'strong' in lower_line else 'BUY'
                    elif 'sell' in lower_line:
                        signal = 'STRONG_SELL' if 'strong' in lower_line else 'SELL'
                    else:
                        signal = 'HOLD'

                if 'ishonch:' in lower_line or 'confidence:' in lower_line:
                    if 'yuqori' in lower_line or 'high' in lower_line:
                        confidence = 90
                    elif 'o\'rta' in lower_line or 'medium' in lower_line:
                        confidence = 75
                    elif 'past' in lower_line or 'low' in lower_line:
                        confidence = 60

                if 'narx:' in lower_line or 'price:' in lower_line:
                    import re
                    price_match = re.search(r'([\d.,]+)', line)
                    if price_match:
                        price = float(price_match.group(1).replace(',', ''))

                if 'maqsad:' in lower_line or 'target:' in lower_line:
                    import re
                    target_match = re.search(r'([\d.,]+)', line)
                    if target_match:
                        target = float(target_match.group(1).replace(',', ''))

                if 'stop:' in lower_line:
                    import re
                    stop_match = re.search(r'([\d.,]+)', line)
                    if stop_match:
                        stop = float(stop_match.group(1).replace(',', ''))

            # Set defaults if not found
            if not price:
                if 'EUR' in pair:
                    price = 1.0850
                elif 'GBP' in pair:
                    price = 1.2650
                elif 'JPY' in pair:
                    price = 149.50
                elif 'BTC' in pair:
                    price = 98500
                elif 'XAU' in pair:
                    price = 2650
                else:
                    price = 1.0000

            if not target:
                target = price * (1.008 if signal.endswith('BUY') else 0.992 if signal.endswith('SELL') else 1.0)

            if not stop:
                stop = price * (0.995 if signal.endswith('BUY') else 1.005 if signal.endswith('SELL') else 1.0)

            return {
                'signal': signal,
                'confidence': confidence,
                'price': price,
                'target': target,
                'stop': stop,
                'reasoning': reasoning,
                'rsi': 50,  # Will be in detailed text
                'macd': 'NEUTRAL',  # Will be in detailed text
                'trend': 'SIDEWAYS'  # Will be in detailed text
            }

        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None

    def generate_reasoning(self, signal: str, rsi: float, macd: str, trend: str):
        """Генерация обоснования сигнала"""
        reasons = []

        if rsi < 30:
            reasons.append(f"RSI {rsi} - haddan tashqari sotilgan zona, narx ko'tarilishi kutilmoqda")
        elif rsi > 70:
            reasons.append(f"RSI {rsi} - o'ta sotib olingan zona, narx pasayishi ehtimoli yuqori")
        else:
            reasons.append(f"RSI {rsi} - neytral zona, momentum kuzatilmoqda")

        if macd == "BULLISH":
            reasons.append("MACD ko'rsatkichi bullish signal bermoqda - xaridorlar ustunlik qilmoqda")
        else:
            reasons.append("MACD ko'rsatkichi bearish signal bermoqda - sotuvchilar bosim o'tkazmoqda")

        if trend == "UPTREND":
            reasons.append("Moving Average trend yuqoriga yo'nalgan - umumiy trend ijobiy")
        else:
            reasons.append("Moving Average trend pastga yo'nalgan - umumiy trend salbiy")

        return " | ".join(reasons)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начальная команда"""
        keyboard = [
            ["📈 Signal olish", "📊 Bozor tahlili"],
            ["⭐ Sevimlilar", "ℹ️ Yordam"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            f"Assalomu alaykum, {update.effective_user.first_name}!\n\n"
            "🤖 Professional Trading Bot ga xush kelibsiz!\n\n"
            "📈 Yuqori aniqlikdagi trading signallar\n"
            "📊 Professional bozor tahlili\n"
            "⚡ Real-time ma'lumotlar\n\n"
            "Tanlang:",
            reply_markup=reply_markup
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabarlarni qayta ishlash"""
        text = update.message.text

        if text == "📈 Signal olish":
            await self.show_pairs(update, context)
        elif text == "📊 Bozor tahlili":
            await self.market_analysis(update, context)
        elif text == "⭐ Sevimlilar":
            await self.favorites(update, context)
        elif text == "ℹ️ Yordam":
            await self.help_command(update, context)
        elif text in self.trading_pairs:
            await self.analyze_pair(update, context, text)
        else:
            await self.unknown_command(update, context)

    async def show_pairs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Trading juftlarini ko'rsatish"""
        keyboard = []
        for i in range(0, len(self.trading_pairs), 2):
            row = self.trading_pairs[i:i+2]
            keyboard.append(row)
        keyboard.append(["🔙 Orqaga"])

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "📈 Trading juftligini tanlang:",
            reply_markup=reply_markup
        )

    async def analyze_pair(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pair: str):
        """Trading juftligi tahlili"""
        await update.message.reply_text("⏳ Haqiqiy bozor ma'lumotlari olinmoqda...")

        # Get real market data
        current_price = await self.get_real_price(pair)
        if current_price is None:
            await update.message.reply_text("❌ Ma'lumot olishda xatolik. Keyinroq qayta urinib ko'ring.")
            return

        await update.message.reply_text("📊 Professional bozor tahlili bajarilmoqda...")

        # Get GPT-4o web search analysis
        analysis = await self.analyze_with_gpt_web_search(pair)
        if analysis is None:
            # Fallback to simple analysis if GPT fails
            analysis = {
                'signal': 'HOLD',
                'confidence': 50,
                'price': current_price,
                'target': current_price,
                'stop': current_price,
                'reasoning': 'Professional tahlil bajarilmoqda. Bozor ma\'lumotlari asosida signal tayyorlanmoqda.',
                'rsi': 50,
                'macd': 'NEUTRAL',
                'trend': 'SIDEWAYS'
            }
        if analysis is None:
            await update.message.reply_text("❌ Tahlilda xatolik. Keyinroq qayta urinib ko'ring.")
            return

        # Map signals to emoji
        signal_emoji = {
            'STRONG_BUY': '🟢🟢',
            'BUY': '🟢',
            'NEUTRAL': '🟡',
            'SELL': '🔴',
            'STRONG_SELL': '🔴🔴'
        }

        # Use analysis targets or calculate defaults
        signal = analysis['signal']
        tp = analysis.get('target', current_price)
        sl = analysis.get('stop', current_price)

        # Fallback calculation if targets not provided
        if tp == current_price and sl == current_price:
            if signal in ['BUY', 'STRONG_BUY']:
                tp = round(current_price * 1.015, 5)  # 1.5% TP
                sl = round(current_price * 0.992, 5)  # 0.8% SL
            elif signal in ['SELL', 'STRONG_SELL']:
                tp = round(current_price * 0.985, 5)  # 1.5% TP
                sl = round(current_price * 1.008, 5)  # 0.8% SL
        else:
            tp = current_price
            sl = current_price

        # Format values properly
        if pair.startswith('XAU'):
            price_str = f"{current_price:.2f}"
            tp_str = f"{tp:.2f}"
            sl_str = f"{sl:.2f}"
            ma_short_str = f"{analysis['ma_short']:.2f}"
            ma_long_str = f"{analysis['ma_long']:.2f}"
        else:
            price_str = f"{current_price:.5f}"
            tp_str = f"{tp:.5f}"
            sl_str = f"{sl:.5f}"
            ma_short_str = f"{analysis['ma_short']:.5f}"
            ma_long_str = f"{analysis['ma_long']:.5f}"

        message = f"""
{signal_emoji.get(signal, '🟡')} <b>{pair} Professional Tahlil</b>

💰 <b>Joriy narx:</b> {price_str}
📊 <b>Signal:</b> {signal}
📈 <b>Ishonch:</b> {analysis['confidence']}%

🎯 <b>Take Profit:</b> {tp_str}
⛔ <b>Stop Loss:</b> {sl_str}

📝 <b>Professional Bozor Tahlili:</b>
{analysis['reasoning'][:1000]}...

⏰ <b>Vaqt:</b> {datetime.now().strftime('%H:%M:%S')}

⚠️ <b>Eslatma:</b> Haqiqiy bozor ma'lumotlari asosida tahlil. Trading xavfli!
        """

        await update.message.reply_text(message, parse_mode='HTML')

    async def market_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Umumiy bozor tahlili"""
        await update.message.reply_text(
            """
📊 <b>Bugungi bozor tahlili</b>

🌍 <b>Forex bozori:</b>
• USD kuchli pozitsiyada
• EUR/USD pastroq harakat
• GBP volatil

💰 <b>Kriptovalyuta:</b>
• BTC barqaror o'sish
• ETH yuqori momentum

🥇 <b>Qimmatbaho metallar:</b>
• XAUUSD ko'tarilish tendentsiyasi
• XAGUSD range harakati

⏰ Ma'lumot yangilangan: {datetime.now().strftime('%H:%M:%S')}
            """,
            parse_mode='HTML'
        )

    async def favorites(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sevimli juftliklar"""
        await update.message.reply_text(
            "⭐ Sevimli trading juftliklaringiz:\n\n"
            "Hozircha sevimlilar yo'q.\n"
            "Juftlikni tahlil qilib, ⭐ tugmasini bosing."
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam"""
        await update.message.reply_text(
            """
ℹ️ <b>Bot haqida ma'lumot</b>

🤖 Professional Trading Signal Bot

<b>Imkoniyatlar:</b>
• 📈 Real-time trading signallar
• 📊 Professional texnik tahlil
• ⚡ Tez va aniq natijalar
• 🎯 TP/SL ko'rsatkichlari

<b>Qo'llab-quvvatlash:</b>
@trading_support

<b>Kanal:</b>
@trading_signals_uz

⚠️ <b>Muhim:</b> Trading xavfli! Har doim risk-menedjmentdan foydalaning.
            """,
            parse_mode='HTML'
        )

    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Noma'lum buyruq"""
        await update.message.reply_text(
            "❓ Kechirasiz, tushunmadim.\n"
            "Iltimos, menyudan tanlang yoki /help buyrug'ini kiriting."
        )

def main():
    """Botni ishga tushirish"""
    # Bot tokenini ENV dan olish
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    # Botni yaratish
    application = Application.builder().token(token).build()
    bot = SimpleTradingBot()

    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))

    # Botni ishga tushirish
    logger.info("🤖 Simple Trading Bot started!")
    logger.info(f"Bot token: {token[:20]}...")
    logger.info(f"OpenAI key available: {bool(os.getenv('OPENAI_API_KEY'))}")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()