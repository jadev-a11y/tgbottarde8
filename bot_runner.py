#!/usr/bin/env python3
"""
Bot Runner - Ensures only one instance runs and clears Telegram session
"""
import os
import signal
import psutil
import logging
import asyncio
import aiohttp
from simple_bot import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clear_telegram_session():
    """Clear any existing Telegram getUpdates session"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.warning("No TELEGRAM_BOT_TOKEN found, skipping session clear")
        return

    try:
        # Быстрая очистка с таймаутом
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Delete webhook быстро
            webhook_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            try:
                async with session.post(webhook_url) as response:
                    logger.info(f"🗑️ Webhook clear: {response.status}")
            except:
                logger.info("🗑️ Webhook clear: skipped")

            # Агрессивная очистка updates
            clear_url = f"https://api.telegram.org/bot{token}/getUpdates"
            for attempt in range(5):  # Больше попыток
                try:
                    params = {"timeout": 0, "limit": 100, "offset": -1}  # Очистить все
                    async with session.post(clear_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            if data.get('result') and len(data['result']) > 0:
                                # Offset к последнему update + много
                                last_id = max([u['update_id'] for u in data['result']])
                                offset_params = {"offset": last_id + 100, "timeout": 0}
                                async with session.post(clear_url, params=offset_params):
                                    pass
                                logger.info(f"✅ Force cleared {len(data['result'])} updates")
                            else:
                                logger.info("✅ No pending updates")
                            break
                        else:
                            logger.warning(f"⚠️ Attempt {attempt + 1}: {response.status}")
                except Exception as e:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed: {e}")
                    await asyncio.sleep(1)  # Пауза между попытками

    except Exception as e:
        logger.warning(f"⚠️ Session clear warning (continuing): {e}")

def kill_existing_bots():
    """Kill any existing bot processes - безопасно для хостинга"""
    current_pid = os.getpid()
    killed_count = 0

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['pid'] == current_pid:
                    continue

                cmdline = ' '.join(proc.info['cmdline'] or [])
                # Более точная фильтрация для хостинга
                if any(keyword in cmdline.lower() for keyword in ['simple_bot.py', 'precise_signal_bot.py', 'telegram_bot']):
                    # Проверяем что это наш проект
                    if 'tradingbot' in cmdline or 'telegram_bot' in cmdline:
                        logger.info(f"Killing existing bot process: {proc.info['pid']} - {cmdline[:100]}")
                        proc.terminate()  # Используем terminate вместо kill
                        killed_count += 1

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Ждем завершения процессов
        if killed_count > 0:
            import time
            time.sleep(3)
            logger.info(f"Terminated {killed_count} existing bot processes")
        else:
            logger.info("No existing bot processes found")

    except Exception as e:
        logger.warning(f"Ошибка при завершении процессов: {e}")
        # Продолжаем работу даже если не смогли убить процессы

if __name__ == '__main__':
    logger.info("🔄 Ensuring single bot instance...")
    kill_existing_bots()

    logger.info("🧹 Clearing Telegram session...")
    asyncio.run(clear_telegram_session())

    # Minimal wait for Telegram session clearing
    import time
    time.sleep(0.5)

    logger.info("🚀 Starting simple trading bot...")
    asyncio.run(main())