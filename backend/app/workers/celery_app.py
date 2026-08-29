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
    beat_schedule={
        "outbox.poller": {
            "task": "outbox.process_pending",
            "schedule": 5.0,
        },
        "reservations.expire": {
            "task": "reservations.expire",
            "schedule": 60.0,
        },
    },
)

celery_app.autodiscover_tasks(["app.workers"])

@celery_app.task(name="health.ping")
def ping():
    return "pong"


@celery_app.task(name="reservations.expire")
def expire_reservations():
    from datetime import datetime, timezone

    from app.core.database import SessionLocal
    from app.models import Reservation

    db = SessionLocal()
    try:
        expired = db.query(Reservation).filter(
            Reservation.status == "ACTIVE",
            Reservation.expires_at < datetime.now(timezone.utc)
        ).update({"status": "EXPIRED"})
        db.commit()
        return {"expired": expired}
    finally:
        db.close()


@celery_app.task(name="outbox.process_pending", bind=True, max_retries=3, default_retry_delay=10)
def process_outbox(self):
    from urllib.parse import urlparse

    import redis

    from app.core.database import SessionLocal
    from app.models import OutboxEvent

    db = SessionLocal()
    try:
        pending = db.query(OutboxEvent).filter(
            OutboxEvent.status == "PENDING"
        ).order_by(OutboxEvent.created_at).limit(100).all()

        if not pending:
            return {"processed": 0}

        # Get Redis client for stream publishing
        parsed = urlparse(settings.redis_url)
        r = redis.Redis(
            host=parsed.hostname or "localhost",
            port=parsed.port or 6379,
            password=parsed.password or None,
            db=int(parsed.path.lstrip("/")) if parsed.path else 0,
            decode_responses=True,
        )

        processed = 0
        for event in pending:
            try:
                stream_key = f"events:{event.aggregate}"
                r.xadd(stream_key, {
                    "event_id": str(event.id),
                    "aggregate": event.aggregate,
                    "aggregate_id": event.aggregate_id,
                    "event_type": event.event_type,
                    "payload": str(event.payload),
                })
                event.status = "COMPLETED"
                processed += 1
            except Exception:
                event.retry_count += 1
                if event.retry_count >= 3:
                    event.status = "FAILED"
                # Log error, continue with next event

        db.commit()
        return {"processed": processed, "total_pending": len(pending)}
    finally:
        db.close()
