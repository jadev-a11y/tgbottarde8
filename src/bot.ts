import TelegramBot from 'node-telegram-bot-api';
import dotenv from 'dotenv';
import { TradingService } from './services/tradingService';
import { NewsService } from './services/newsService';
import { UserSession } from './types';

dotenv.config();

class TradingBot {
  private bot: TelegramBot;
  private tradingService: TradingService;
  private newsService: NewsService;
  private userSessions: Map<number, UserSession>;

  constructor() {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    if (!token) {
      throw new Error('TELEGRAM_BOT_TOKEN muhit o\'zgaruvchisi mavjud emas!');
    }

    this.bot = new TelegramBot(token, { polling: true });
    this.tradingService = new TradingService();
    this.newsService = new NewsService();
    this.userSessions = new Map();

    this.setupEventHandlers();
    console.log('🤖 Professional Trading Bot ishga tushdi...');
  }

  private setupEventHandlers(): void {
    // Start command
    this.bot.onText(/\/start/, (msg) => this.handleStart(msg));

    // Signal button
    this.bot.onText(/Signal Olish|📊 Signal Olish/, (msg) => this.handleSignalRequest(msg));

    // News button
    this.bot.onText(/Yangiliklar|📰 Yangiliklar/, (msg) => this.handleNewsRequest(msg));

    // Handle callback queries
    this.bot.on('callback_query', (query) => this.handleCallbackQuery(query));

    // Handle regular messages
    this.bot.on('message', (msg) => this.handleMessage(msg));

    // Error handling
    this.bot.on('error', (error) => {
      console.error('Bot xatosi:', error);
    });

    this.bot.on('polling_error', (error) => {
      console.error('Polling xatosi:', error);
    });
  }

  private async handleStart(msg: TelegramBot.Message): Promise<void> {
    const chatId = msg.chat.id;
    const user = msg.from;

    if (!user) return;

    // Create or update user session
    this.userSessions.set(user.id, {
      userId: user.id,
      username: user.username,
      firstName: user.first_name,
      lastActivity: new Date(),
      preferredPairs: []
    });

    const welcomeMessage = `Assalomu alaykum, hurmatli ${user.first_name || 'Foydalanuvchi'}! 👋\n\n` +
      `🤖 *Professional Trading Bot*ga xush kelibsiz!\n\n` +
      `Men sizga professional forex signallari va dolzarb moliyaviy yangiliklar bilan yordam beraman.\n\n` +
      `📊 *Xizmatlarimiz:*\n` +
      `• Real vaqt forex signallari\n` +
      `• Professional texnik tahlil\n` +
      `• Dolzarb moliyaviy yangiliklar\n` +
      `• Bepul va ishonchli ma'lumotlar\n\n` +
      `Boshlash uchun quyidagi tugmalardan birini tanlang:`;

    const keyboard = {
      keyboard: [
        [{ text: '📊 Signal Olish' }, { text: '📰 Yangiliklar' }]
      ],
      resize_keyboard: true,
      one_time_keyboard: false
    };

    await this.bot.sendMessage(chatId, welcomeMessage, {
      parse_mode: 'Markdown',
      reply_markup: keyboard
    });
  }

  private async handleSignalRequest(msg: TelegramBot.Message): Promise<void> {
    const chatId = msg.chat.id;

    try {
      // Show loading message
      const loadingMsg = await this.bot.sendMessage(chatId, '🔄 Signal tayyorlanmoqda, iltimos kutib turing...');

      // Generate signal
      const signal = await this.tradingService.getRandomSignal();
      const signalMessage = this.tradingService.formatSignalMessage(signal);

      // Delete loading message
      await this.bot.deleteMessage(chatId, loadingMsg.message_id);

      // Send signal with inline keyboard
      const inlineKeyboard = {
        inline_keyboard: [
          [
            { text: '🔄 Yangi Signal', callback_data: 'new_signal' },
            { text: '📰 Yangiliklar', callback_data: 'news' }
          ]
        ]
      };

      await this.bot.sendMessage(chatId, signalMessage, {
        parse_mode: 'Markdown',
        reply_markup: inlineKeyboard
      });

      // Update user activity
      this.updateUserActivity(msg.from?.id);

    } catch (error) {
      console.error('Signal olishda xato:', error);
      await this.bot.sendMessage(chatId, '❌ Signal olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
    }
  }

  private async handleNewsRequest(msg: TelegramBot.Message): Promise<void> {
    const chatId = msg.chat.id;

    try {
      // Show loading message
      const loadingMsg = await this.bot.sendMessage(chatId, '📰 Yangiliklar yuklanmoqda...');

      // Get news
      const news = await this.newsService.getTopNews(5);
      const newsMessage = this.newsService.formatNewsMessage(news);

      // Delete loading message
      await this.bot.deleteMessage(chatId, loadingMsg.message_id);

      // Send news with inline keyboard
      const inlineKeyboard = {
        inline_keyboard: [
          [
            { text: '🔄 Yangilash', callback_data: 'refresh_news' },
            { text: '📊 Signal Olish', callback_data: 'new_signal' }
          ]
        ]
      };

      await this.bot.sendMessage(chatId, newsMessage, {
        parse_mode: 'Markdown',
        reply_markup: inlineKeyboard
      });

      // Update user activity
      this.updateUserActivity(msg.from?.id);

    } catch (error) {
      console.error('Yangiliklar olishda xato:', error);
      await this.bot.sendMessage(chatId, '❌ Yangiliklar olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
    }
  }

  private async handleCallbackQuery(query: TelegramBot.CallbackQuery): Promise<void> {
    const chatId = query.message?.chat.id;
    const callbackData = query.data;

    if (!chatId) return;

    try {
      await this.bot.answerCallbackQuery(query.id);

      switch (callbackData) {
        case 'new_signal':
          // Show loading
          const loadingMsg = await this.bot.sendMessage(chatId, '🔄 Yangi signal tayyorlanmoqda...');

          const signal = await this.tradingService.getRandomSignal();
          const signalMessage = this.tradingService.formatSignalMessage(signal);

          await this.bot.deleteMessage(chatId, loadingMsg.message_id);

          const signalKeyboard = {
            inline_keyboard: [
              [
                { text: '🔄 Yangi Signal', callback_data: 'new_signal' },
                { text: '📰 Yangiliklar', callback_data: 'news' }
              ]
            ]
          };

          await this.bot.sendMessage(chatId, signalMessage, {
            parse_mode: 'Markdown',
            reply_markup: signalKeyboard
          });
          break;

        case 'news':
        case 'refresh_news':
          const newsLoadingMsg = await this.bot.sendMessage(chatId, '📰 Yangiliklar yangilanmoqda...');

          const news = await this.newsService.getTopNews(5);
          const newsMessage = this.newsService.formatNewsMessage(news);

          await this.bot.deleteMessage(chatId, newsLoadingMsg.message_id);

          const newsKeyboard = {
            inline_keyboard: [
              [
                { text: '🔄 Yangilash', callback_data: 'refresh_news' },
                { text: '📊 Signal Olish', callback_data: 'new_signal' }
              ]
            ]
          };

          await this.bot.sendMessage(chatId, newsMessage, {
            parse_mode: 'Markdown',
            reply_markup: newsKeyboard
          });
          break;

        default:
          await this.bot.sendMessage(chatId, '❌ Noto\'g\'ri buyruq.');
      }

      this.updateUserActivity(query.from?.id);

    } catch (error) {
      console.error('Callback query xatosi:', error);
      await this.bot.sendMessage(chatId, '❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
    }
  }

  private async handleMessage(msg: TelegramBot.Message): Promise<void> {
    const chatId = msg.chat.id;
    const text = msg.text;

    // Skip if it's a command or handled message
    if (!text || text.startsWith('/') ||
        text.includes('Signal Olish') ||
        text.includes('Yangiliklar')) {
      return;
    }

    // Help message for unknown commands
    const helpMessage = `Hurmatli foydalanuvchi! 🙂\n\n` +
      `Men faqat quyidagi xizmatlarni taqdim eta olaman:\n\n` +
      `📊 *Signal Olish* - Professional forex signallari\n` +
      `📰 *Yangiliklar* - Dolzarb moliyaviy yangiliklar\n\n` +
      `Iltimos, yuqoridagi tugmalardan foydalaning.`;

    await this.bot.sendMessage(chatId, helpMessage, {
      parse_mode: 'Markdown'
    });
  }

  private updateUserActivity(userId?: number): void {
    if (!userId) return;

    const session = this.userSessions.get(userId);
    if (session) {
      session.lastActivity = new Date();
      this.userSessions.set(userId, session);
    }
  }

  public async start(): Promise<void> {
    console.log('✅ Bot muvaffaqiyatli ishga tushdi!');
    console.log('📊 Signal xizmati faol');
    console.log('📰 Yangiliklar xizmati faol');
    console.log('🔄 Barcha xizmatlar ishlayapti...');
  }

  public stop(): void {
    this.bot.stopPolling();
    console.log('🛑 Bot to\'xtatildi');
  }
}

// Bot ni ishga tushirish
const bot = new TradingBot();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Bot to\'xtatilmoqda...');
  bot.stop();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Bot to\'xtatilmoqda...');
  bot.stop();
  process.exit(0);
});

// Start the bot
bot.start().catch((error) => {
  console.error('Bot ishga tushirishda xato:', error);
  process.exit(1);
});

export { TradingBot };