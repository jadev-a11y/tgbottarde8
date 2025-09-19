#!/usr/bin/env python3
"""
Bot Runner - Ensures only one instance runs
"""
import os
import signal
import psutil
import logging
from simple_bot import main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    logger.info("🚀 Starting simple trading bot...")
    main()