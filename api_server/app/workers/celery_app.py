import os
from celery import Celery
from app.config import settings

# Use Redis as broker (from env var set in docker-compose.yml)
_broker = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "talkflow_worker",
    broker=_broker,
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    broker_url=_broker,
    result_backend=_broker,
    task_always_eager=False,
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)
