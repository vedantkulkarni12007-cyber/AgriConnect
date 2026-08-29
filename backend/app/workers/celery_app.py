from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "krishilink",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
)

@celery_app.task(name="health.ping")
def ping():
    return "pong"


@celery_app.task(name="reservations.expire")
def expire_reservations():
    return {"expired": 0}
