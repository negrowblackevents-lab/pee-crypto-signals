from __future__ import annotations

import asyncio
from dataclasses import dataclass

from apscheduler.schedulers.background import BackgroundScheduler

from .config import settings


@dataclass
class SchedulerHandle:
    scheduler: BackgroundScheduler

    def shutdown(self) -> None:
        self.scheduler.shutdown(wait=False)


def start_scheduler(job_coro) -> SchedulerHandle:
    scheduler = BackgroundScheduler()

    def _run():
        asyncio.run(job_coro())

    scheduler.add_job(_run, "interval", seconds=settings.UPDATE_INTERVAL_SECONDS, max_instances=1, coalesce=True)
    scheduler.start()
    return SchedulerHandle(scheduler=scheduler)

