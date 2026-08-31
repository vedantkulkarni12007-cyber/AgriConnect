import redis as redis_lib
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import check_db, get_db
from app.core.deps import require_role
from app.models import AuditLog, Dispute, Lot, Transaction, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=dict)
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: str | None = None,
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role.lower())
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    data = [
        {
            "id": str(u.id),
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_verified": u.is_verified,
            "is_active": u.is_active,
        }
        for u in items
    ]
    return {
        "success": True,
        "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit},
        "message": f"{len(data)} users",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/audit", response_model=dict)
def audit_logs(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    data = [
        {
            "id": str(a.id),
            "actor_id": a.actor_id,
            "action": a.action,
            "entity": a.entity,
            "entity_id": a.entity_id,
            "request_id": a.request_id,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in items
    ]
    return {
        "success": True,
        "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit},
        "message": f"{len(data)} logs",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/system-health", response_model=dict)
def system_health(request: Request, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    checks = {}
    try:
        checks["database"] = "HEALTHY" if check_db() else "DOWN"
    except:
        checks["database"] = "DOWN"
    try:
        r = redis_lib.Redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.ping()
        checks["redis"] = "HEALTHY"
    except:
        checks["redis"] = "DOWN"
    checks["api"] = "HEALTHY"
    # counts
    stats = {
        "users": db.query(User).count(),
        "lots": db.query(Lot).count(),
        "transactions": db.query(Transaction).count(),
        "disputes": db.query(Dispute).count(),
    }
    overall = "HEALTHY" if all(v == "HEALTHY" for v in checks.values()) else "DEGRADED"
    return {
        "success": True,
        "data": {"status": overall, "checks": checks, "stats": stats},
        "message": f"System {overall}",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.post("/users/{user_id}/verify", response_model=dict)
def verify_user(user_id: str, request: Request, db: Session = Depends(get_db), admin=Depends(require_role("admin"))):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.is_verified = True
    db.commit()
    return {
        "success": True,
        "data": {"id": str(u.id), "is_verified": True},
        "message": "User verified",
        "request_id": getattr(request.state, "request_id", None),
    }
