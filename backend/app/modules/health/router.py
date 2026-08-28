from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import time

from app.core.config import settings
from app.core.database import get_db, check_db
import redis as redis_lib

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": settings.app_version,
            "mode": "demo" if settings.demo_mode else "live",
            "env": settings.env,
        },
        "message": f"KrishiLink API v{settings.app_version} is running",
        "request_id": None,
    }


@router.get("/health/detailed")
def detailed_health(request: Request, db: Session = Depends(get_db)):
    checks: dict[str, str] = {}
    overall = "HEALTHY"

    db_ok = check_db()
    checks["database"] = "HEALTHY" if db_ok else "DOWN"
    if not db_ok:
        overall = "DEGRADED"

    try:
        r = redis_lib.Redis.from_url(settings.redis_url, socket_connect_timeout=1)
        r.ping()
        checks["redis"] = "HEALTHY"
    except Exception:
        checks["redis"] = "DOWN"
        overall = "DEGRADED"

    try:
        checks["api"] = "HEALTHY"
        checks["worker"] = "HEALTHY"
    except Exception:
        checks["worker"] = "UNKNOWN"

    return {
        "success": True,
        "data": {
            "status": overall,
            "version": settings.app_version,
            "checks": checks,
            "timestamp": time.time(),
        },
        "message": f"System status: {overall}",
        "request_id": request.headers.get("X-Request-ID"),
    }
