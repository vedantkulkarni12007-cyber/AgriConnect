from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Market

router = APIRouter(prefix="/markets", tags=["markets"])

@router.get("", response_model=dict)
def list_markets(request: Request, db: Session = Depends(get_db), district: str | None = None, near_lat: float | None = None, near_lng: float | None = None, radius_km: float | None = 50, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    q = db.query(Market).filter(Market.is_active == True)
    if district:
        q = q.filter(Market.district == district)
    if near_lat is not None and near_lng is not None:
        q = q.filter(text("ST_DWithin(location_geog, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :rad)").bindparams(lng=near_lng, lat=near_lat, rad=radius_km*1000))
    total = q.count()
    items = q.offset((page-1)*limit).limit(limit).all()
    data = [{"id": str(m.id), "name": m.name, "district": m.district, "state": m.state, "latitude": float(m.latitude) if m.latitude else None, "longitude": float(m.longitude) if m.longitude else None, "market_type": m.market_type} for m in items]
    return {"success": True, "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total+limit-1)//limit}, "message": f"{len(data)} markets", "request_id": getattr(request.state, "request_id", None)}
