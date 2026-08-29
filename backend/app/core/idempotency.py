from fastapi import Request
from sqlalchemy.orm import Session

from app.models import IdempotencyKey


def check_idempotency(request: Request, db: Session):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return None
    existing = db.get(IdempotencyKey, key)
    if existing and existing.response_body is not None:
        return existing
    return None

def save_idempotency(request: Request, db: Session, status: int, body: dict):
    key = request.headers.get("Idempotency-Key")
    if not key:
        return
    existing = db.get(IdempotencyKey, key)
    if existing:
        existing.response_status = status
        existing.response_body = body
    else:
        db.add(IdempotencyKey(key=key, response_status=status, response_body=body))
    db.commit()
