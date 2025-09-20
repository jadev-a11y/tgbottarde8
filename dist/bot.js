"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TradingBot = void 0;
const node_telegram_bot_api_1 = __importDefault(require("node-telegram-bot-api"));
const dotenv_1 = __importDefault(require("dotenv"));
const tradingService_1 = require("./services/tradingService");
const newsService_1 = require("./services/newsService");
dotenv_1.default.config();
class TradingBot {
    constructor() {
        const token = process.env.TELEGRAM_BOT_TOKEN;
        if (!token) {
            throw new Error('TELEGRAM_BOT_TOKEN muhit o\'zgaruvchisi mavjud emas!');
        }
        this.bot = new node_telegram_bot_api_1.default(token, { polling: true });
        this.tradingService = new tradingService_1.TradingService();
        this.newsService = new newsService_1.NewsService();
        this.userSessions = new Map();
        this.setupEventHandlers();
        console.log('🤖 Professional Trading Bot ishga tushdi...');
    }
    setupEventHandlers() {
        this.bot.onText(/\/start/, (msg) => this.handleStart(msg));
        this.bot.onText(/Signal Olish|📊 Signal Olish/, (msg) => this.handleSignalRequest(msg));
        this.bot.onText(/Yangiliklar|📰 Yangiliklar/, (msg) => this.handleNewsRequest(msg));
        this.bot.on('callback_query', (query) => this.handleCallbackQuery(query));
        this.bot.on('message', (msg) => this.handleMessage(msg));
        this.bot.on('error', (error) => {
            console.error('Bot xatosi:', error);
        });
        this.bot.on('polling_error', (error) => {
            console.error('Polling xatosi:', error);
        });
    }
    async handleStart(msg) {
        const chatId = msg.chat.id;
        const user = msg.from;
        if (!user)
            return;
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
    async handleSignalRequest(msg) {
        const chatId = msg.chat.id;
        try {
            const pairSelectionMessage = '💱 Qaysi valyuta juftligidan signal olishni xohlaysiz?\n\nIltimos, quyidagi variantlardan birini tanlang:';
            const pairKeyboard = {
                inline_keyboard: [
                    [
                        { text: '💵 EUR/USD', callback_data: 'signal_EURUSD' },
                        { text: '💷 GBP/USD', callback_data: 'signal_GBPUSD' },
                        { text: '💴 USD/JPY', callback_data: 'signal_USDJPY' }
                    ],
                    [
                        { text: '🥇 XAU/USD (Oltin)', callback_data: 'signal_XAUUSD' },
                        { text: '🛢️ XTI/USD (Neft)', callback_data: 'signal_XTIUSD' },
                        { text: '₿ BTC/USD', callback_data: 'signal_BTCUSD' }
                    ],
                    [
                        { text: '🇦🇺 AUD/USD', callback_data: 'signal_AUDUSD' },
                        { text: '🇨🇦 USD/CAD', callback_data: 'signal_USDCAD' },
                        { text: '🇨🇭 USD/CHF', callback_data: 'signal_USDCHF' }
                    ],
                    [
                        { text: '🎲 Tasodifiy Signal', callback_data: 'signal_random' }
                    ]
                ]
            };
            await this.bot.sendMessage(chatId, pairSelectionMessage, {
                reply_markup: pairKeyboard
            });
            this.updateUserActivity(msg.from?.id);
        }
        catch (error) {
            console.error('Signal olishda xato:', error);
            await this.bot.sendMessage(chatId, '❌ Signal olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
        }
    }
    async handleNewsRequest(msg) {
        const chatId = msg.chat.id;
        try {
            const loadingMsg = await this.bot.sendMessage(chatId, '📰 Yangiliklar yuklanmoqda...');
            const news = await this.newsService.getTopNews(5);
            const newsMessage = this.newsService.formatNewsMessage(news);
            await this.bot.deleteMessage(chatId, loadingMsg.message_id);
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
            this.updateUserActivity(msg.from?.id);
        }
        catch (error) {
            console.error('Yangiliklar olishda xato:', error);
            await this.bot.sendMessage(chatId, '❌ Yangiliklar olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
        }
    }
    async handleCallbackQuery(query) {
        const chatId = query.message?.chat.id;
        const callbackData = query.data;
        if (!chatId)
            return;
        try {
            await this.bot.answerCallbackQuery(query.id);
            if (callbackData?.startsWith('signal_')) {
                await this.handleSignalGeneration(chatId, callbackData);
            }
            else {
                switch (callbackData) {
                    case 'new_signal':
                        const pairKeyboard = {
                            inline_keyboard: [
                                [
                                    { text: '💵 EUR/USD', callback_data: 'signal_EURUSD' },
                                    { text: '💷 GBP/USD', callback_data: 'signal_GBPUSD' },
                                    { text: '💴 USD/JPY', callback_data: 'signal_USDJPY' }
                                ],
                                [
                                    { text: '🥇 XAU/USD (Oltin)', callback_data: 'signal_XAUUSD' },
                                    { text: '🛢️ XTI/USD (Neft)', callback_data: 'signal_XTIUSD' },
                                    { text: '₿ BTC/USD', callback_data: 'signal_BTCUSD' }
                                ],
                                [
                                    { text: '🇦🇺 AUD/USD', callback_data: 'signal_AUDUSD' },
                                    { text: '🇨🇦 USD/CAD', callback_data: 'signal_USDCAD' },
                                    { text: '🇨🇭 USD/CHF', callback_data: 'signal_USDCHF' }
                                ],
                                [
                                    { text: '🎲 Tasodifiy Signal', callback_data: 'signal_random' }
                                ]
                            ]
                        };
                        await this.bot.sendMessage(chatId, '💱 Qaysi valyuta juftligidan signal olishni xohlaysiz?', {
                            reply_markup: pairKeyboard
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
            }
            this.updateUserActivity(query.from?.id);
        }
        catch (error) {
            console.error('Callback query xatosi:', error);
            await this.bot.sendMessage(chatId, '❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
        }
    }
    async handleMessage(msg) {
        const chatId = msg.chat.id;
        const text = msg.text;
        if (!text || text.startsWith('/') ||
            text.includes('Signal Olish') ||
            text.includes('Yangiliklar')) {
            return;
        }
        const helpMessage = `Hurmatli foydalanuvchi! 🙂\n\n` +
            `Men faqat quyidagi xizmatlarni taqdim eta olaman:\n\n` +
            `📊 *Signal Olish* - Professional forex signallari\n` +
            `📰 *Yangiliklar* - Dolzarb moliyaviy yangiliklar\n\n` +
            `Iltimos, yuqoridagi tugmalardan foydalaning.`;
        await this.bot.sendMessage(chatId, helpMessage, {
            parse_mode: 'Markdown'
        });
    }
    async handleSignalGeneration(chatId, callbackData) {
        try {
            const loadingMsg = await this.bot.sendMessage(chatId, '🔄 Signal tayyorlanmoqda, iltimos kutib turing...');
            let signal;
            if (callbackData === 'signal_random') {
                signal = await this.tradingService.getRandomSignal();
            }
            else {
                const symbol = callbackData.replace('signal_', '');
                signal = await this.tradingService.generateSignal(symbol);
            }
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
        }
        catch (error) {
            console.error('Signal generatsiya xatosi:', error);
            await this.bot.sendMessage(chatId, '❌ Signal olishda xatolik yuz berdi. Iltimos, qaytadan urinib ko\'ring.');
        }
    }
    updateUserActivity(userId) {
        if (!userId)
            return;
        const session = this.userSessions.get(userId);
        if (session) {
            session.lastActivity = new Date();
            this.userSessions.set(userId, session);
        }
    }
    async start() {
        console.log('✅ Bot muvaffaqiyatli ishga tushdi!');
        console.log('📊 Signal xizmati faol');
        console.log('📰 Yangiliklar xizmati faol');
        console.log('🔄 Barcha xizmatlar ishlayapti...');
    }
    stop() {
        this.bot.stopPolling();
        console.log('🛑 Bot to\'xtatildi');
    }
}
exports.TradingBot = TradingBot;
const bot = new TradingBot();
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
bot.start().catch((error) => {
    console.error('Bot ishga tushirishda xato:', error);
    process.exit(1);
});
