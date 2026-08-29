
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Crop, Market, PriceObservation

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("", response_model=dict)
def list_prices(request: Request, db: Session = Depends(get_db), crop: str | None = None, market: str | None = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    q = db.query(PriceObservation).join(Crop, PriceObservation.crop_id == Crop.id).join(Market, PriceObservation.market_id == Market.id)
    if crop:
        q = q.filter(Crop.name.ilike(crop))
    if market:
        q = q.filter(Market.name.ilike(market))
    q = q.order_by(PriceObservation.price_date.desc())
    total = q.count()
    items = q.offset((page-1)*limit).limit(limit).all()
    data = [{"id": str(o.id), "crop_id": str(o.crop_id), "market_id": str(o.market_id), "price_date": o.price_date.isoformat(), "min_price": float(o.min_price), "modal_price": float(o.modal_price), "max_price": float(o.max_price), "volume_tonnes": float(o.volume_tonnes) if o.volume_tonnes else None, "quality_status": o.quality_status, "source_record_id": o.source_record_id} for o in items]
    return {"success": True, "data": {"items": data, "total": total, "page": page, "limit": limit, "pages": (total+limit-1)//limit}, "message": f"{len(data)} observations", "request_id": getattr(request.state, "request_id", None)}

@router.get("/{crop_name}/history", response_model=dict)
def price_history(crop_name: str, request: Request, db: Session = Depends(get_db), market: str | None = None, days: int = Query(15, ge=1, le=90)):
    crop = db.query(Crop).filter(Crop.name.ilike(crop_name)).first()
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found")
    q = db.query(PriceObservation).filter(PriceObservation.crop_id == crop.id).order_by(PriceObservation.price_date.desc()).limit(days)
    if market:
        m = db.query(Market).filter(Market.name.ilike(market)).first()
        if m:
            q = q.filter(PriceObservation.market_id == m.id)
    items = list(reversed(q.all()))
    data = [{"date": o.price_date.isoformat(), "modal_price": float(o.modal_price), "min_price": float(o.min_price), "max_price": float(o.max_price)} for o in items]
    return {"success": True, "data": {"crop": crop.name, "history": data}, "message": f"{len(data)} days", "request_id": getattr(request.state, "request_id", None)}

@router.get("/{obs_id}/provenance", response_model=dict)
def provenance(obs_id: str, request: Request, db: Session = Depends(get_db)):
    obs = db.get(PriceObservation, obs_id)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {"success": True, "data": {"id": str(obs.id), "source_id": str(obs.source_id) if obs.source_id else None, "source_record_id": obs.source_record_id, "source_url": obs.source_url, "published_at": obs.published_at.isoformat() if obs.published_at else None, "retrieved_at": obs.retrieved_at.isoformat() if obs.retrieved_at else None, "ingestion_run_id": str(obs.ingestion_run_id) if obs.ingestion_run_id else None, "parser_version": obs.parser_version, "raw_payload_hash": obs.raw_payload_hash, "quality_status": obs.quality_status}, "message": "Provenance", "request_id": getattr(request.state, "request_id", None)}
