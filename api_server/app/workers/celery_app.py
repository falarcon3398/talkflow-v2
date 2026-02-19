from celery import Celery
from app.config import settings

celery_app = Celery(
    "talkflow_worker",
    include=["app.workers.tasks"]
)

celery_app.conf.update(
    broker_url="memory://",
    result_backend=None,
    task_always_eager=True,
    task_eager_propagates=True,
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
