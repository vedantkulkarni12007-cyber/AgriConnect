from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Crop

router = APIRouter(prefix="/crops", tags=["crops"])

@router.get("", response_model=dict)
def list_crops(request: Request, db: Session = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    q = db.query(Crop)
    total = q.count()
    items = q.offset((page-1)*limit).limit(limit).all()
    data = [{"id": str(c.id), "name": c.name, "category": c.category, "unit": c.unit} for c in items]
    return {"success": True, "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total+limit-1)//limit}, "message": f"{len(data)} crops", "request_id": getattr(request.state, "request_id", None)}

@router.get("/{crop_id}", response_model=dict)
def get_crop(crop_id: str, request: Request, db: Session = Depends(get_db)):
    c = db.query(Crop).filter(Crop.id == crop_id).first()
    if not c:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Crop not found")
    return {"success": True, "data": {"id": str(c.id), "name": c.name, "category": c.category}, "message": "OK", "request_id": getattr(request.state, "request_id", None)}
