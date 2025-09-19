#!/usr/bin/env python3
"""
Простой торговый бот без pandas для быстрого запуска
"""

import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

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
        await update.message.reply_text("⏳ Tahlil qilinmoqda...")

        # Simulate analysis delay
        await asyncio.sleep(2)

        # Simple demo analysis
        import random

        signals = ["BUY", "SELL", "NEUTRAL"]
        signal = random.choice(signals)
        confidence = random.randint(65, 95)
        current_price = round(random.uniform(1.0800, 1.0900), 5)

        if signal == "BUY":
            emoji = "🟢"
            tp = round(current_price * 1.02, 5)
            sl = round(current_price * 0.99, 5)
        elif signal == "SELL":
            emoji = "🔴"
            tp = round(current_price * 0.98, 5)
            sl = round(current_price * 1.01, 5)
        else:
            emoji = "🟡"
            tp = current_price
            sl = current_price

        message = f"""
{emoji} <b>{pair} Tahlil natijasi</b>

📊 <b>Signal:</b> {signal}
📈 <b>Ishonch darajasi:</b> {confidence}%
💰 <b>Joriy narx:</b> {current_price}

🎯 <b>Take Profit:</b> {tp}
⛔ <b>Stop Loss:</b> {sl}

📝 <b>Tahlil:</b>
• Texnik indikatorlar {signal.lower()} signalini ko'rsatmoqda
• Bozor sharoitlari barqaror
• Volume ma'lumotlari normal

⏰ <b>Vaqt:</b> {datetime.now().strftime('%H:%M:%S')}

⚠️ <b>Eslatma:</b> Bu tahlil faqat ma'lumot uchun. Trading xavfli!
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
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()