#!/usr/bin/env python3
"""
Xavfsiz Bot Runner - Faqat bitta instansiya ishlashini ta'minlaydi
"""
import os
import sys
import signal
import psutil
import logging
import asyncio
import time
import fcntl
import atexit
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SingleInstanceBot:
    """Faqat bitta bot instansiyasini ishlatish"""

    def __init__(self):
        self.lock_file = Path("/tmp/trading_bot.lock")
        self.pid_file = Path("/tmp/trading_bot.pid")
        self.lock_handle = None

    def acquire_lock(self):
        """Lock olish - faqat bitta instansiya"""
        try:
            # Lock fayl ochish
            self.lock_handle = open(self.lock_file, 'w')

            # Non-blocking lock urinish
            fcntl.lockf(self.lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # PID yozish
            self.lock_handle.write(str(os.getpid()))
            self.lock_handle.flush()

            logger.info(f"✅ Lock muvaffaqiyatli olindi (PID: {os.getpid()})")
            return True

        except IOError:
            logger.warning("⚠️ Bot allaqachon ishlab turibdi!")

            # Eski PIDni o'qish va tekshirish
            if self.pid_file.exists():
                try:
                    old_pid = int(self.pid_file.read_text())
                    if not psutil.pid_exists(old_pid):
                        logger.info(f"🔧 Eski bot (PID: {old_pid}) topilmadi, tozalash...")
                        self.cleanup_old_instance()
                        return self.acquire_lock()  # Qayta urinish
                    else:
                        logger.error(f"❌ Bot haqiqatan ishlab turibdi (PID: {old_pid})")
                except:
                    pass

            return False

    def cleanup_old_instance(self):
        """Eski instansiyalarni tozalash"""
        try:
            # Lock faylni o'chirish
            if self.lock_file.exists():
                self.lock_file.unlink()

            # PID faylni o'chirish
            if self.pid_file.exists():
                self.pid_file.unlink()

            logger.info("✅ Eski fayllar tozalandi")

        except Exception as e:
            logger.error(f"Tozalashda xato: {e}")

    def release_lock(self):
        """Lockni bo'shatish"""
        try:
            if self.lock_handle:
                fcntl.lockf(self.lock_handle, fcntl.LOCK_UN)
                self.lock_handle.close()

            if self.lock_file.exists():
                self.lock_file.unlink()

            if self.pid_file.exists():
                self.pid_file.unlink()

            logger.info("✅ Lock bo'shatildi")

        except Exception as e:
            logger.error(f"Lock bo'shatishda xato: {e}")

def kill_zombie_bots():
    """Zombie bot processlarini topish va o'chirish"""
    current_pid = os.getpid()
    killed_count = 0

    bot_keywords = [
        'simple_bot.py',
        'simple_trading_bot.py',
        'bot_runner.py',
        'precise_signal_bot.py',
        'telegram_bot'
    ]

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['pid'] == current_pid:
                    continue

                cmdline = ' '.join(proc.info.get('cmdline', []))

                # Bot processmi tekshirish
                is_bot = any(keyword in cmdline for keyword in bot_keywords)

                if is_bot:
                    # Process yoshi tekshirish (5 daqiqadan eski)
                    age = time.time() - proc.info['create_time']

                    if age > 300:  # 5 daqiqa
                        logger.warning(f"🧟 Zombie bot topildi (PID: {proc.info['pid']}, yoshi: {age:.0f}s)")
                        proc.terminate()
                        killed_count += 1
                        time.sleep(0.5)

                        if proc.is_running():
                            proc.kill()  # Force kill

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    except Exception as e:
        logger.error(f"Process tekshirishda xato: {e}")

    if killed_count > 0:
        logger.info(f"✅ {killed_count} ta zombie bot o'chirildi")
        time.sleep(2)

    return killed_count

def clear_telegram_updates():
    """Telegram update queueni tozalash"""
    import aiohttp
    import asyncio

    async def clear():
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            return

        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Webhook o'chirish
                webhook_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
                await session.post(webhook_url)

                # Updates tozalash
                clear_url = f"https://api.telegram.org/bot{token}/getUpdates"
                params = {"timeout": 0, "limit": 100, "offset": -1}

                async with session.post(clear_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('result'):
                            last_id = max([u['update_id'] for u in data['result']], default=0)
                            if last_id > 0:
                                # Skip all old updates
                                params = {"offset": last_id + 1, "timeout": 0}
                                await session.post(clear_url, params=params)
                                logger.info(f"✅ {len(data['result'])} ta eski update tozalandi")

        except Exception as e:
            logger.warning(f"Update tozalashda xato: {e}")

    asyncio.run(clear())

def signal_handler(signum, frame):
    """Signal handler"""
    logger.info(f"\n⚠️ Signal qabul qilindi: {signum}")
    sys.exit(0)

def main():
    """Asosiy funksiya"""
    logger.info("=" * 60)
    logger.info("🚀 Professional Trading Bot ishga tushirilmoqda...")
    logger.info("=" * 60)

    # Single instance tekshirish
    bot_lock = SingleInstanceBot()

    if not bot_lock.acquire_lock():
        logger.error("❌ Bot allaqachon ishlab turibdi! Chiqish...")
        sys.exit(1)

    # Cleanup on exit
    atexit.register(bot_lock.release_lock)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # Zombie botlarni o'chirish
    logger.info("🔍 Zombie botlar tekshirilmoqda...")
    kill_zombie_bots()

    # Telegram queue tozalash
    logger.info("🧹 Telegram update queue tozalanmoqda...")
    clear_telegram_updates()

    # PID faylga yozish
    bot_lock.pid_file.write_text(str(os.getpid()))

    # Biroz kutish
    time.sleep(1)

    # Asosiy botni ishga tushirish
    logger.info("✅ Barcha tekshiruvlar muvaffaqiyatli!")
    logger.info("🤖 Bot ishga tushirilmoqda...")
    logger.info("=" * 60)

    try:
        # Import qilish
        from simple_trading_bot import main as bot_main

        # Botni ishga tushirish
        asyncio.run(bot_main())

    except KeyboardInterrupt:
        logger.info("\n👋 Bot to'xtatildi (Ctrl+C)")
    except Exception as e:
        logger.error(f"❌ Botda xatolik: {e}")
        import traceback
        traceback.print_exc()
    finally:
        bot_lock.release_lock()
        logger.info("=" * 60)
        logger.info("🛑 Bot to'xtatildi")
        logger.info("=" * 60)

if __name__ == '__main__':
    main()