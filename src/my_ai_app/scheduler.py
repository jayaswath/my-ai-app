import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from my_ai_app.pipeline import run

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Run the market trip every morning at 6am, forever.

    The alarm clock. It does not do the shopping - it just decides when.
    """
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        run,
        trigger=CronTrigger(hour=6, minute=0),
        id="daily_ingest",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "Scheduler running. Next trip: %s", scheduler.get_jobs()[0].next_run_time
    )

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
