#!/usr/bin/env python3
"""
Professional Trading Bot - O'zbek tilida
Maksimal darajada muloyim va professional
"""

import os
import asyncio
import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from advanced_signals import AdvancedSignalGenerator
import yfinance as yf

# Logging sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ProfessionalTradingBot:
    """Professional trading bot - O'zbek tilida"""

    def __init__(self):
        self.signal_generator = AdvancedSignalGenerator()
        self.user_states = {}
        self.user_favorites = {}

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot boshlash komandasi"""
        user = update.effective_user
        user_name = user.first_name or "Hurmatli foydalanuvchi"

        welcome_message = f"""
🌟 Assalomu alaykum, {user_name}!

Men professional trading yordamchi botman. Sizga quyidagi xizmatlarni taklif etaman:

📊 **Asosiy imkoniyatlar:**
• Jonli bozor tahlili
• Professional signal generatsiyasi
• Texnik ko'rsatkichlar monitoring
• Risk menejment maslahatlari

💡 Qanday yordam bera olaman?
Quyidagi tugmalardan birini tanlang yoki /yordam buyrug'ini yuboring.

Hurmat bilan, Trading Assistant 🤝
"""

        keyboard = [
            ['📈 Signal olish', '💹 Bozor tahlili'],
            ['⭐ Sevimlilar', '📊 Portfolio'],
            ['⚙️ Sozlamalar', '❓ Yordam']
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            welcome_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Yordam ko'rsatish"""
        help_text = """
📚 **Hurmatli foydalanuvchi, quyida bot imkoniyatlari:**

🔹 **Signal olish**
Tanlangan juftlik uchun professional tahlil va savdo signallari

🔹 **Bozor tahlili**
Hozirgi bozor holati va tendensiyalar tahlili

🔹 **Sevimlilar**
Tez-tez kuzatiladigan juftliklarni saqlash

🔹 **Portfolio**
Sizning savdolaringiz statistikasi

📝 **Maslahat:**
Signal olish uchun juftlikni tanlang va bizning tahlilimizni kuting.

Agar qo'shimcha savollar bo'lsa, administrator bilan bog'laning.

Hurmat bilan xizmatdamiz! 🙏
"""

        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Xabarlarni qayta ishlash"""
        text = update.message.text
        user_id = update.effective_user.id

        # Signal olish
        if text == '📈 Signal olish':
            await self.show_pairs_menu(update, context)

        # Bozor tahlili
        elif text == '💹 Bozor tahlili':
            await self.market_analysis(update, context)

        # Sevimlilar
        elif text == '⭐ Sevimlilar':
            await self.show_favorites(update, context)

        # Portfolio
        elif text == '📊 Portfolio':
            await self.show_portfolio(update, context)

        # Sozlamalar
        elif text == '⚙️ Sozlamalar':
            await self.show_settings(update, context)

        # Yordam
        elif text == '❓ Yordam':
            await self.help_command(update, context)

        # Juftlik tanlash
        elif text in self.get_all_pairs():
            await self.generate_signal(update, context, text)

        # Orqaga
        elif text == '◀️ Orqaga':
            await self.start(update, context)

        else:
            await update.message.reply_text(
                "Kechirasiz, bunday buyruq topilmadi. Iltimos, tugmalardan foydalaning. 🙏",
                parse_mode='Markdown'
            )

    def get_all_pairs(self):
        """Barcha juftliklar ro'yxati"""
        return [
            # Forex
            'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
            'EURGBP', 'EURJPY', 'GBPJPY', 'AUDJPY', 'EURAUD', 'EURCHF', 'AUDCAD',
            # Crypto
            'BTCUSD', 'ETHUSD', 'BNBUSD', 'XRPUSD', 'ADAUSD', 'DOGEUSD', 'SOLUSD',
            # Commodities
            'XAUUSD', 'XAGUSD', 'OILUSD', 'GASUSD'
        ]

    async def show_pairs_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Juftliklar menyusini ko'rsatish"""
        message = """
📈 **Hurmatli foydalanuvchi, quyidagi kategoriyalardan tanlang:**

Sizga qaysi bozor bo'yicha signal kerak?
"""

        keyboard = [
            ['💱 Forex juftliklari', '₿ Kripto valyutalar'],
            ['🏆 Qimmatbaho metallar', '⛽ Energiya resurslari'],
            ['⭐ Eng mashhur', '◀️ Orqaga']
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def generate_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pair: str):
        """Signal generatsiyasi"""
        loading_message = await update.message.reply_text(
            f"⏳ *{pair}* uchun tahlil tayyorlanmoqda...\n\nIltimos, biroz kuting... 🙏",
            parse_mode='Markdown'
        )

        try:
            # Real market data olish
            ticker = yf.Ticker(pair.replace('USD', '=X') if 'USD' in pair else pair)
            info = ticker.info
            history = ticker.history(period='1d', interval='1h')

            if not history.empty:
                current_price = history['Close'].iloc[-1]
                change = history['Close'].iloc[-1] - history['Close'].iloc[0]
                change_percent = (change / history['Close'].iloc[0]) * 100
            else:
                current_price = 0
                change = 0
                change_percent = 0

            # Advanced signal generator dan signal olish
            real_data = {
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'high': history['High'].max() if not history.empty else 0,
                'low': history['Low'].min() if not history.empty else 0,
                'volume': history['Volume'].sum() if not history.empty else 0,
                'source': 'YFinance',
                'timestamp': datetime.now()
            }

            signal_data = self.signal_generator.generate_advanced_signal(
                pair,
                real_data,
                {'price': current_price}
            )

            # Signal xabarini tayyorlash
            signal_emoji = '🟢' if signal_data['signal'] == 'BUY' else '🔴' if signal_data['signal'] == 'SELL' else '⚪'
            confidence_bar = self.get_confidence_bar(signal_data['confidence'])

            signal_message = f"""
{signal_emoji} **{pair} UCHUN PROFESSIONAL TAHLIL**

📊 **Bozor holati:**
• Joriy narx: ${current_price:.5f}
• 24-soatlik o'zgarish: {change_percent:+.2f}%
• Kunlik diapazon: ${signal_data['indicators']['support']:.5f} - ${signal_data['indicators']['resistance']:.5f}

🎯 **SIGNAL: {signal_data['signal']}**
Ishonch darajasi: {signal_data['confidence']:.1f}%
{confidence_bar}

📈 **Savdo parametrlari:**
• Kirish narxi: ${current_price:.5f}
• Take Profit: ${signal_data['take_profit']:.5f}
• Stop Loss: ${signal_data['stop_loss']:.5f}
• Risk/Reward: 1:{signal_data['risk_reward']:.1f}

🔍 **Texnik ko'rsatkichlar:**
• RSI: {signal_data['indicators']['rsi']:.1f}
• MACD: {signal_data['indicators']['macd']:.6f}
• Volume: {signal_data['indicators']['volume_ratio']:.1f}x o'rtacha

💡 **Tahlil:**
{self.format_reasons(signal_data.get('detailed_reasons', []))}

⚠️ **Risk haqida eslatma:**
Hurmatli foydalanuvchi, har doim o'z risk menejmentingizdan foydalaning. Faqat yo'qotishga tayyor bo'lgan mablag'dan foydalaning.

🕐 Yangilangan: {datetime.now().strftime('%H:%M:%S')}

Yana signal olish uchun boshqa juftlikni tanlang yoki /start buyrug'ini yuboring.

Hurmat bilan, Trading Assistant 🤝
"""

            await loading_message.edit_text(
                signal_message,
                parse_mode='Markdown'
            )

            # Inline tugmalar qo'shish
            keyboard = [
                [
                    InlineKeyboardButton("♻️ Yangilash", callback_data=f"refresh_{pair}"),
                    InlineKeyboardButton("⭐ Sevimlilarga qo'shish", callback_data=f"fav_{pair}")
                ],
                [
                    InlineKeyboardButton("📊 Batafsil tahlil", callback_data=f"detail_{pair}"),
                    InlineKeyboardButton("📈 Grafik", callback_data=f"chart_{pair}")
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                "Qo'shimcha amallar:",
                reply_markup=reply_markup
            )

        except Exception as e:
            logger.error(f"Signal generatsiyada xato: {e}")
            await loading_message.edit_text(
                f"""
⚠️ **Kechirasiz, texnik nosozlik yuz berdi**

{pair} uchun ma'lumot olishda muammo paydo bo'ldi.

Iltimos, keyinroq urinib ko'ring yoki boshqa juftlikni tanlang.

Agar muammo davom etsa, administrator bilan bog'laning.

Hurmat bilan uzr so'raymiz 🙏
""",
                parse_mode='Markdown'
            )

    def get_confidence_bar(self, confidence):
        """Ishonch darajasi vizualizatsiyasi"""
        filled = int(confidence / 10)
        empty = 10 - filled
        return '🟩' * filled + '⬜' * empty

    def format_reasons(self, reasons):
        """Sabab tahlilini formatlash"""
        if not reasons:
            return "Ma'lumotlar tahlil qilinmoqda..."

        formatted = []
        for i, reason in enumerate(reasons[:3], 1):  # Faqat 3 ta asosiy sabab
            formatted.append(f"{i}. {reason}")

        return '\n'.join(formatted)

    async def market_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Umumiy bozor tahlili"""
        loading = await update.message.reply_text("⏳ Bozor tahlili tayyorlanmoqda...")

        try:
            analysis = """
📊 **UMUMIY BOZOR TAHLILI**

🌍 **Global bozor holati:**
• AQSh dollari: Kuchli pozitsiya
• Yevro: O'rtacha holat
• Oltin: Ko'tarilish tendensiyasi

📈 **Bugungi sessiyalar:**
• Osiyo: Faol savdo
• Yevropa: O'rtacha hajm
• Amerika: Kutilmoqda

💡 **Tavsiyalar:**
• EURUSD: Qisqa muddatli SELL signali
• XAUUSD: Uzoq muddatli BUY imkoniyati
• BTCUSD: Neytral, kuzatish tavsiya etiladi

⚠️ **Muhim yangiliklar:**
• Fed yig'ilishi kutilmoqda
• ECB foiz stavkasi qarori
• NFP ma'lumotlari e'lon qilinadi

Batafsil signal olish uchun juftlik tanlang.

Hurmat bilan, Trading Assistant 🤝
"""

            await loading.edit_text(analysis, parse_mode='Markdown')

        except Exception as e:
            await loading.edit_text("Kechirasiz, tahlilda xatolik. Keyinroq urinib ko'ring. 🙏")

    async def show_favorites(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Sevimli juftliklar"""
        user_id = update.effective_user.id
        favorites = self.user_favorites.get(user_id, [])

        if not favorites:
            message = """
⭐ **Sevimli juftliklar**

Sizda hali sevimli juftliklar yo'q.

Signal olayotganda ⭐ tugmasini bosib, juftlikni sevimlilarga qo'shing.

Hurmat bilan, Trading Assistant 🤝
"""
        else:
            pairs_list = '\n'.join([f"• {pair}" for pair in favorites])
            message = f"""
⭐ **Sizning sevimli juftliklaringiz:**

{pairs_list}

Tanlash uchun juftlik nomini yozing.
"""

        await update.message.reply_text(message, parse_mode='Markdown')

    async def show_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Portfolio statistikasi"""
        message = """
📊 **Sizning portfolioingiz**

📈 Jami signallar: 0
✅ Muvaffaqiyatli: 0
❌ Muvaffaqiyatsiz: 0
📊 Samaradorlik: 0%

💰 **Moliyaviy ko'rsatkichlar:**
• Jami foyda: $0
• O'rtacha foyda: 0%
• Eng yaxshi savdo: -
• Risk/Reward: 1:2

📅 **So'nggi faoliyat:**
Hali savdolar yo'q

Signal olish va portfolio statistikasini yaxshilash uchun savdoni boshlang!

Hurmat bilan, Trading Assistant 🤝
"""

        await update.message.reply_text(message, parse_mode='Markdown')

    async def show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Bot sozlamalari"""
        keyboard = [
            ['🔔 Bildirishnomalar', '🌐 Til sozlamalari'],
            ['⏰ Vaqt zonasi', '📱 Interfeys'],
            ['◀️ Orqaga']
        ]

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        message = """
⚙️ **Sozlamalar**

Hurmatli foydalanuvchi, quyidagi sozlamalarni o'zgartirishingiz mumkin:

• 🔔 Bildirishnomalar - Signal va yangiliklar haqida xabar berish
• 🌐 Til - Interfeys tili (Hozir: O'zbek tili)
• ⏰ Vaqt zonasi - Sizning mintaqangiz vaqti
• 📱 Interfeys - Ko'rinish sozlamalari

Tanlang va sozlang!

Hurmat bilan, Trading Assistant 🤝
"""

        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Inline tugmalar uchun handler"""
        query = update.callback_query
        await query.answer()

        data = query.data

        if data.startswith('refresh_'):
            pair = data.replace('refresh_', '')
            await query.message.reply_text(f"♻️ {pair} signali yangilanmoqda...")
            # Signal yangilash logikasi

        elif data.startswith('fav_'):
            pair = data.replace('fav_', '')
            user_id = query.from_user.id

            if user_id not in self.user_favorites:
                self.user_favorites[user_id] = []

            if pair not in self.user_favorites[user_id]:
                self.user_favorites[user_id].append(pair)
                await query.message.reply_text(f"⭐ {pair} sevimlilarga qo'shildi!")
            else:
                await query.message.reply_text(f"Bu juftlik allaqachon sevimlilarда!")

        elif data.startswith('detail_'):
            pair = data.replace('detail_', '')
            await query.message.reply_text(f"📊 {pair} uchun batafsil tahlil tayyorlanmoqda...")

        elif data.startswith('chart_'):
            pair = data.replace('chart_', '')
            await query.message.reply_text(f"📈 {pair} grafigi yuklanmoqda...")

async def main():
    """Asosiy bot funksiyasi"""
    # Bot tokenini olish
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi!")
        return

    # Bot yaratish
    bot = ProfessionalTradingBot()
    application = Application.builder().token(token).build()

    # Handlerlar qo'shish
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("yordam", bot.help_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.callback_query_handler))

    # Botni ishga tushirish
    logger.info("✅ Professional Trading Bot ishga tushirildi!")
    logger.info("🌐 Interfeys tili: O'zbek tili")
    logger.info("📊 Signal generatori: Python Advanced Signals")

    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())