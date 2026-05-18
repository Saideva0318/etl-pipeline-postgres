"""
Scheduler Module
APScheduler cron job — runs the full ETL pipeline on a schedule.
"""

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

from pipeline import run_sales_etl, run_api_etl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("scheduler")


def run_all_pipelines():
    """Entry point for scheduled ETL run."""
    logger.info(f"Scheduled ETL triggered at {datetime.utcnow().isoformat()}")
    sales_result = run_sales_etl()
    api_result = run_api_etl()
    logger.info(f"Scheduled run complete — Sales: {sales_result['status']} | API: {api_result['status']}")


def start_scheduler(
    hour: int = 6,
    minute: int = 0,
    timezone: str = "America/New_York"
):
    """
    Start the cron scheduler.
    
    Default: Runs every day at 6:00 AM Eastern.
    
    Args:
        hour: Hour of day (24h format)
        minute: Minute of hour
        timezone: Timezone string
    """
    scheduler = BlockingScheduler(timezone=timezone)
    
    scheduler.add_job(
        run_all_pipelines,
        trigger=CronTrigger(hour=hour, minute=minute, timezone=timezone),
        id="daily_etl",
        name="Daily ETL Pipeline Run",
        replace_existing=True
    )
    
    logger.info(f"Scheduler started — ETL will run daily at {hour:02d}:{minute:02d} {timezone}")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    start_scheduler(hour=6, minute=0)
