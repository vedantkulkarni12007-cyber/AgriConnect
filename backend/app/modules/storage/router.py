from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.s3 import generate_presigned_url, get_s3_client
from app.models import StorageFacility

router = APIRouter(prefix="/storage", tags=["storage"])


@router.get("", response_model=dict)
def list_storage(
    request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)
):
    q = db.query(StorageFacility).filter(StorageFacility.status == "ACTIVE")
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    data = [
        {
            "id": str(s.id),
            "name": s.name,
            "type": s.type,
            "capacity": float(s.capacity) if s.capacity else None,
            "available_capacity": float(s.available_capacity) if s.available_capacity else None,
            "location_text": s.location_text,
            "cost_per_unit": float(s.cost_per_unit) if s.cost_per_unit else None,
        }
        for s in items
    ]
    return {
        "success": True,
        "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total + limit - 1) // limit},
        "message": f"{len(data)} facilities",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/buckets", response_model=dict)
def list_buckets(request: Request):
    """List S3 buckets (if configured)"""
    client = get_s3_client()
    if not client:
        return {"success": True, "data": [], "message": "S3 not configured"}

    try:
        resp = client.list_buckets()
        buckets = [{"name": b["Name"], "created": b["CreationDate"].isoformat()} for b in resp.get("Buckets", [])]
        return {"success": True, "data": buckets, "message": f"{len(buckets)} buckets"}
    except Exception as e:
        return {"success": False, "data": [], "message": f"Error listing buckets: {e}"}


@router.post("/presigned-url", response_model=dict)
def create_presigned_url(key: str, expiration: int = 3600, request: Request = None):
    """Generate presigned URL for S3 object"""
    client = get_s3_client()
    if not client:
        raise HTTPException(status_code=503, detail="S3 not configured")

    url = generate_presigned_url(key, expiration)
    return {
        "success": True,
        "data": {"url": url, "expires_in": expiration},
        "message": "Presigned URL generated",
        "request_id": getattr(request.state, "request_id", None) if request else None,
    }
