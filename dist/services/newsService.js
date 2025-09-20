"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.NewsService = void 0;
const axios_1 = __importDefault(require("axios"));
class NewsService {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 600000;
    }
    async getForexNews() {
        const cacheKey = 'forex_news';
        const cached = this.cache.get(cacheKey);
        if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
            return cached.data;
        }
        try {
            let news = await this.getNewsFromForexFactory();
            if (!news || news.length === 0) {
                news = await this.getNewsFromFinnhub();
            }
            if (!news || news.length === 0) {
                news = this.getMockNews();
            }
            this.cache.set(cacheKey, { data: news, timestamp: Date.now() });
            return news;
        }
        catch (error) {
            console.error('Error fetching forex news:', error);
            return this.getMockNews();
        }
    }
    async getNewsFromForexFactory() {
        try {
            return [];
        }
        catch (error) {
            return [];
        }
    }
    async getNewsFromFinnhub() {
        try {
            const response = await axios_1.default.get('https://finnhub.io/api/v1/news', {
                params: {
                    category: 'forex',
                    token: 'demo'
                },
                timeout: 10000
            });
            if (response.data && Array.isArray(response.data)) {
                return response.data.slice(0, 5).map((item) => ({
                    title: item.headline || 'News Title',
                    description: item.summary || 'News description...',
                    url: item.url || '#',
                    publishedAt: new Date(item.datetime * 1000).toISOString(),
                    impact: this.determineImpact(item.headline || ''),
                    currency: this.extractCurrency(item.headline || '')
                }));
            }
            return [];
        }
        catch (error) {
            return [];
        }
    }
    getMockNews() {
        const mockNews = [
            {
                title: 'Federal Reserve faiz stavkalarini o\'zgartirish haqida bayonot berdi',
                description: 'Amerika Markaziy banki pul siyosati bo\'yicha yangi qaror e\'lon qildi. Bu forex bozoriga katta ta\'sir ko\'rsatishi mumkin.',
                url: 'https://example.com/news1',
                publishedAt: new Date(Date.now() - 3600000).toISOString(),
                impact: 'high',
                currency: 'USD'
            },
            {
                title: 'Yevropa Markaziy Banki inflyatsiya prognozlarini yangiladi',
                description: 'YeMB yangi iqtisodiy prognozlarni e\'lon qildi. Euro kursiga ta\'sir ko\'rsatishi kutilmoqda.',
                url: 'https://example.com/news2',
                publishedAt: new Date(Date.now() - 7200000).toISOString(),
                impact: 'medium',
                currency: 'EUR'
            },
            {
                title: 'Oltin narxlari rekord darajaga yetdi',
                description: 'Xalqaro bozorlarda oltin narxi yangi yuqori ko\'rsatkichga erishdi. Investorlar xavfsiz aktivlarga murojaat qilmoqda.',
                url: 'https://example.com/news3',
                publishedAt: new Date(Date.now() - 10800000).toISOString(),
                impact: 'high',
                currency: 'XAU'
            },
            {
                title: 'Yaponiya banki yen kursini mustahkamlash uchun interventsiya qildi',
                description: 'Yaponiya Markaziy banki milliy valyutani qo\'llab-quvvatlash uchun bozorga aralashdi.',
                url: 'https://example.com/news4',
                publishedAt: new Date(Date.now() - 14400000).toISOString(),
                impact: 'medium',
                currency: 'JPY'
            },
            {
                title: 'Bitcoin yangi yuqori ko\'rsatkichga erishdi',
                description: 'Kriptovalyuta bozorida Bitcoin narxi kutilmagan o\'sish ko\'rsatdi.',
                url: 'https://example.com/news5',
                publishedAt: new Date(Date.now() - 18000000).toISOString(),
                impact: 'medium',
                currency: 'BTC'
            }
        ];
        return mockNews;
    }
    determineImpact(headline) {
        const highImpactWords = ['federal reserve', 'interest rate', 'central bank', 'inflation', 'gdp'];
        const mediumImpactWords = ['employment', 'trade', 'economic', 'policy'];
        const lowerHeadline = headline.toLowerCase();
        if (highImpactWords.some(word => lowerHeadline.includes(word))) {
            return 'high';
        }
        else if (mediumImpactWords.some(word => lowerHeadline.includes(word))) {
            return 'medium';
        }
        return 'low';
    }
    extractCurrency(headline) {
        const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'NZD', 'XAU', 'BTC'];
        const lowerHeadline = headline.toLowerCase();
        for (const currency of currencies) {
            if (lowerHeadline.includes(currency.toLowerCase()) ||
                lowerHeadline.includes(this.getCurrencyName(currency).toLowerCase())) {
                return currency;
            }
        }
        return undefined;
    }
    getCurrencyName(code) {
        const names = {
            'USD': 'dollar',
            'EUR': 'euro',
            'GBP': 'pound',
            'JPY': 'yen',
            'AUD': 'australian',
            'CAD': 'canadian',
            'CHF': 'swiss',
            'NZD': 'zealand',
            'XAU': 'gold',
            'BTC': 'bitcoin'
        };
        return names[code] || '';
    }
    formatNewsMessage(news) {
        if (news.length === 0) {
            return '📰 Hozircha yangiliklar mavjud emas.';
        }
        let message = '📰 *FOREX VA MOLIYAVIY YANGILIKLAR*\n\n';
        news.forEach((item, index) => {
            const impactEmoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            };
            const timeAgo = this.getTimeAgo(new Date(item.publishedAt));
            message += `${impactEmoji[item.impact]} *${item.title}*\n`;
            message += `📝 ${item.description}\n`;
            if (item.currency) {
                message += `💱 Valyuta: ${item.currency}\n`;
            }
            message += `⏰ ${timeAgo}\n\n`;
        });
        message += '_Yangiliklar har 10 daqiqada yangilanadi_';
        return message;
    }
    getTimeAgo(date) {
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        if (diffMins < 1) {
            return 'Hozir';
        }
        else if (diffMins < 60) {
            return `${diffMins} daqiqa oldin`;
        }
        else if (diffHours < 24) {
            return `${diffHours} soat oldin`;
        }
        else {
            const diffDays = Math.floor(diffHours / 24);
            return `${diffDays} kun oldin`;
        }
    }
    async getTopNews(limit = 3) {
        const allNews = await this.getForexNews();
        return allNews.slice(0, limit);
    }
}
exports.NewsService = NewsService;
