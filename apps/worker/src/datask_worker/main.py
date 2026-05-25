"""
RQ worker entrypoint.
Usage:
  uv run --package datask-worker python -m datask_worker.main
  or:
  rq worker datask --url $REDIS_URL
"""

import sys

import redis
import structlog
from datask_core.config import get_settings
from rq import Queue, Worker
from rq.worker import SimpleWorker

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)

logger = structlog.get_logger()


def run() -> None:
    settings = get_settings()
    conn = redis.from_url(settings.redis_url)

    queues = [Queue("datask", connection=conn)]

    # Windows does not support os.fork() — use SimpleWorker which runs jobs
    # in the same process (no forking). On Linux/macOS the standard Worker
    # is used so jobs get proper process isolation.
    WorkerClass = SimpleWorker if sys.platform == "win32" else Worker
    worker = WorkerClass(queues, connection=conn)

    logger.info("worker_starting", redis_url=settings.redis_url, concurrency=settings.worker_concurrency)
    worker.work(burst=False)


if __name__ == "__main__":
    run()
