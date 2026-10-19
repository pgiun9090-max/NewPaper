"""
Scheduler Module.
Runs the newspaper pipeline every morning at 08:00 AM KST.
"""
import sys
from pathlib import Path

# Ensure Source directory is in sys.path
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import time
import schedule
import logging
from datetime import datetime, timezone, timedelta
from pipeline import run_pipeline
from config import SCHEDULE_TIME

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


def scheduled_job():
    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"[{now_str}] Starting scheduled newspaper production (08:00 AM job)...")
    try:
        output_file = run_pipeline(use_exact_8am_window=True)
        if output_file:
            logger.info(f"Daily newspaper production completed: {output_file}")
        else:
            logger.warning("Daily newspaper production finished without output.")
    except Exception as e:
        logger.error(f"Error occurred during scheduled newspaper production: {e}", exc_info=True)


def start_scheduler(schedule_time: str = SCHEDULE_TIME):
    """Starts the scheduler loop."""
    logger.info(f"Newspaper Production Scheduler started. Scheduled daily at {schedule_time} AM KST.")
    schedule.every().day.at(schedule_time).do(scheduled_job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
