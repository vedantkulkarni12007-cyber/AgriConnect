from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Notification, OutboxEvent

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/outbox/pending", response_model=dict)
def outbox_pending(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # Restrict to admin or operator roles only — strictly enforced server-side
    if getattr(user, "role", None) not in ("admin", "operator"):
        raise HTTPException(status_code=403, detail="Forbidden: Admin or operator privileges required")

    items = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.status == "PENDING")
        .order_by(OutboxEvent.created_at.desc())
        .limit(20)
        .all()
    )
    data = [{"id": str(o.id), "aggregate": o.aggregate, "event_type": o.event_type, "status": o.status} for o in items]
    return {
        "success": True,
        "data": data,
        "message": f"{len(data)} pending outbox",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("", response_model=dict)
def list_notifications(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    total = q.count()
    items = q.order_by(Notification.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    data = [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "related_id": str(n.related_id) if n.related_id else None,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in items
    ]
    return {
        "success": True,
        "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit},
        "message": f"{len(data)} notifications",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.post("/{notif_id}/read", response_model=dict)
def mark_read(notif_id: str, request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.get(Notification, notif_id)
    if not n or n.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return {
        "success": True,
        "data": {"id": str(n.id), "is_read": True},
        "message": "Marked read",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.post("/read-all", response_model=dict)
def mark_all_read(request: Request, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read == False).update(
        {"is_read": True}
    )
    db.commit()
    return {
        "success": True,
        "data": {"updated": True},
        "message": "All notifications marked as read",
        "request_id": getattr(request.state, "request_id", None),
    }
