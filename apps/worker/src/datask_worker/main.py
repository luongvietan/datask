"""
RQ worker entrypoint.
Usage:
  uv run --package datask-worker python -m datask_worker.main
  or:
  rq worker datask --url $REDIS_URL
"""

import redis
import structlog
from datask_core.config import get_settings
from rq import Queue, Worker

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
    worker = Worker(queues, connection=conn)

    logger.info("worker_starting", redis_url=settings.redis_url, concurrency=settings.worker_concurrency)
    worker.work(burst=False)


if __name__ == "__main__":
    run()
