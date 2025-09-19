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
        async with aiohttp.ClientSession() as session:
            # Delete webhook to clear any webhook-based conflicts
            webhook_url = f"https://api.telegram.org/bot{token}/deleteWebhook"
            async with session.post(webhook_url) as response:
                if response.status == 200:
                    logger.info("✅ Telegram webhook cleared")
                else:
                    logger.warning(f"⚠️ Webhook clear status: {response.status}")

            # Get updates with timeout=0 to clear any pending updates
            clear_url = f"https://api.telegram.org/bot{token}/getUpdates"
            params = {"timeout": 0, "limit": 100}
            async with session.post(clear_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('result'):
                        # Get last update_id to offset future requests
                        last_id = max([u['update_id'] for u in data['result']], default=0)
                        if last_id > 0:
                            # Confirm updates processed by offsetting
                            offset_params = {"offset": last_id + 1, "timeout": 0}
                            async with session.post(clear_url, params=offset_params) as resp:
                                logger.info(f"✅ Cleared {len(data['result'])} pending updates")
                    logger.info("✅ Telegram session cleared")
                else:
                    logger.warning(f"⚠️ Session clear status: {response.status}")

    except Exception as e:
        logger.error(f"❌ Failed to clear Telegram session: {e}")

def kill_existing_bots():
    """Kill any existing bot processes"""
    current_pid = os.getpid()
    killed_count = 0

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue

            cmdline = ' '.join(proc.info['cmdline'] or [])
            if any(keyword in cmdline for keyword in ['precise_signal_bot', 'simple_bot', 'bot_runner', 'python3 bot_runner', 'python bot_runner', 'telegram']):
                logger.info(f"Killing existing bot process: {proc.info['pid']}")
                proc.kill()
                killed_count += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed_count > 0:
        logger.info(f"Killed {killed_count} existing bot processes")
    else:
        logger.info("No existing bot processes found")

if __name__ == '__main__':
    logger.info("🔄 Ensuring single bot instance...")
    kill_existing_bots()

    logger.info("🧹 Clearing Telegram session...")
    asyncio.run(clear_telegram_session())

    # Wait a moment for Telegram to process the session clearing
    import time
    time.sleep(2)

    logger.info("🚀 Starting simple trading bot...")
    main()