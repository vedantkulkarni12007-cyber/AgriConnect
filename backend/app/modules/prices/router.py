from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Crop, Market, PriceObservation
from app.modules.prices.mandi_api import fetch_mandi_prices

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("", response_model=dict)
def list_prices(
    request: Request,
    db: Session = Depends(get_db),
    crop: str | None = None,
    market: str | None = None,
    district: str | None = None,
    state: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    q = (
        db.query(
            PriceObservation,
            Crop.name.label("crop_name"),
            Market.name.label("market_name"),
            Market.district.label("market_district"),
            Market.state.label("market_state"),
        )
        .join(Crop, PriceObservation.crop_id == Crop.id)
        .join(Market, PriceObservation.market_id == Market.id)
    )
    if crop and crop.lower() != "all":
        q = q.filter(Crop.name.ilike(f"%{crop}%"))
    if market and market.lower() != "all":
        q = q.filter(Market.name.ilike(f"%{market}%"))
    if district and district.lower() != "all":
        q = q.filter(Market.district.ilike(f"%{district}%"))
    if state and state.lower() != "all":
        q = q.filter(Market.state.ilike(f"%{state}%"))

    q = q.order_by(PriceObservation.price_date.desc())
    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()
    data = []
    for o, crop_name, market_name, market_dist, market_st in items:
        # Check prior observation for truthful trend comparison
        prev_obs = (
            db.query(PriceObservation.modal_price)
            .filter(
                PriceObservation.crop_id == o.crop_id,
                PriceObservation.market_id == o.market_id,
                PriceObservation.price_date < o.price_date,
            )
            .order_by(PriceObservation.price_date.desc())
            .first()
        )
        if prev_obs and prev_obs[0] and float(prev_obs[0]) > 0 and o.modal_price:
            prev_m = float(prev_obs[0])
            curr_m = float(o.modal_price)
            diff_pct = round(((curr_m - prev_m) / prev_m) * 100, 2)
            trend_val = "RISING" if diff_pct > 0 else ("FALLING" if diff_pct < 0 else "STABLE")
        else:
            diff_pct = None
            trend_val = "UNKNOWN"

        data.append(
            {
                "id": str(o.id),
                "crop_id": str(o.crop_id),
                "crop": crop_name,
                "market_id": str(o.market_id),
                "market": market_name,
                "district": market_dist,
                "state": market_st,
                "price_date": o.price_date.isoformat() if hasattr(o.price_date, "isoformat") else str(o.price_date),
                "min_price": float(o.min_price or 0),
                "modal_price": float(o.modal_price or 0),
                "max_price": float(o.max_price or 0),
                "volume_tonnes": float(o.volume_tonnes) if o.volume_tonnes else None,
                "volume": float(o.volume_tonnes) if o.volume_tonnes else 0,
                "quality_status": o.quality_status,
                "source_record_id": o.source_record_id,
                "change_pct": diff_pct,
                "trend": trend_val,
            }
        )
    return {
        "success": True,
        "data": {
            "items": data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
        },
        "message": f"{len(data)} observations",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/live", response_model=dict)
def live_mandi_prices(
    request: Request,
    db: Session = Depends(get_db),
    crop: str | None = None,
    market: str | None = None,
    district: str | None = None,
    state: str | None = None,
    date: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Fetch live/recent daily government mandi prices from data.gov.in.
    Falls back to verified database observations if external API is unreachable.
    """
    live_records = fetch_mandi_prices(
        limit=limit,
        offset=offset,
        state=state,
        district=district,
        market=market,
        commodity=crop,
        date=date,
    )

    if live_records:
        return {
            "success": True,
            "source": "data.gov.in (Agmarknet / Ministry of Agriculture)",
            "data": {
                "items": live_records,
                "total": len(live_records),
                "is_live": True,
            },
            "message": f"Retrieved {len(live_records)} live government mandi price records",
            "request_id": getattr(request.state, "request_id", None),
        }

    # Fallback to local verified observations
    db_res = list_prices(
        request=request,
        db=db,
        crop=crop,
        market=market,
        district=district,
        state=state,
        page=(offset // limit) + 1,
        limit=limit,
    )
    fallback_items = db_res.get("data", {}).get("items", [])
    normalized_fallback = [
        {
            "state": item.get("state", "Maharashtra"),
            "district": item.get("district", ""),
            "market": item.get("market", ""),
            "commodity": item.get("crop", ""),
            "variety": "Standard",
            "grade": item.get("quality_status", "FAQ"),
            "arrival_date": item.get("price_date", ""),
            "min_price": item.get("min_price"),
            "modal_price": item.get("modal_price"),
            "max_price": item.get("max_price"),
            "unit": "quintal",
            "trend": item.get("trend"),
            "change_pct": item.get("change_pct"),
        }
        for item in fallback_items
    ]

    return {
        "success": True,
        "source": "KrishiLink Verified Database",
        "data": {
            "items": normalized_fallback,
            "total": db_res.get("data", {}).get("total", len(normalized_fallback)),
            "is_live": False,
        },
        "message": f"Retrieved {len(normalized_fallback)} verified mandi price records (live API fallback)",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/trends/{crop_name}", response_model=dict)
def get_price_trend(
    crop_name: str,
    request: Request,
    db: Session = Depends(get_db),
    market: str | None = None,
):
    crop = db.query(Crop).filter(Crop.name.ilike(crop_name)).first()
    if not crop:
        return {
            "success": False,
            "message": f"Crop '{crop_name}' not found",
            "request_id": getattr(request.state, "request_id", None),
        }

    q = (
        db.query(PriceObservation)
        .filter(PriceObservation.crop_id == crop.id)
        .order_by(PriceObservation.price_date.desc())
    )
    if market and market.lower() != "all":
        m = db.query(Market).filter(Market.name.ilike(market)).first()
        if m:
            q = q.filter(PriceObservation.market_id == m.id)

    obs = q.limit(7).all()
    if not obs:
        return {
            "success": True,
            "data": {
                "crop": crop.name,
                "market": market or "All Markets",
                "current_price": 0,
                "moving_average": 0,
                "percentage_change": 0,
                "trend": "STABLE",
                "explanation": f"Insufficient 7-day observation data to compute price trend for {crop.name}.",
                "note": "Calculated from arithmetic 7-day modal prices",
            },
            "message": "Insufficient trend data",
            "request_id": getattr(request.state, "request_id", None),
        }

    prices = [float(o.modal_price) for o in obs if o.modal_price]
    current_price = prices[0] if prices else 0
    moving_avg = round(sum(prices) / len(prices), 2) if prices else 0
    pct_change = round(((current_price - moving_avg) / moving_avg) * 100, 2) if moving_avg > 0 else 0
    trend_val = "RISING" if pct_change > 1.5 else ("FALLING" if pct_change < -1.5 else "STABLE")

    explanation = f"{crop.name} modal prices are currently {trend_val.lower()} ({pct_change:+}% relative to the 7-day moving average)."

    return {
        "success": True,
        "data": {
            "crop": crop.name,
            "market": market or (obs[0].market_id and "Regional APMC"),
            "current_price": current_price,
            "moving_average": moving_avg,
            "percentage_change": pct_change,
            "trend": trend_val,
            "explanation": explanation,
            "note": "Rule-based signal calculated from 7-day arithmetic price observations",
        },
        "message": f"7-day trend signal for {crop.name}",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/{crop_name}/history", response_model=dict)
def price_history(
    crop_name: str,
    request: Request,
    db: Session = Depends(get_db),
    market: str | None = None,
    days: int = Query(15, ge=1, le=90),
):
    crop = db.query(Crop).filter(Crop.name.ilike(crop_name)).first()
    if not crop:
        # Return graceful empty history instead of 404
        return {
            "success": True,
            "data": {"crop": crop_name, "history": []},
            "message": f"No history records found for {crop_name}",
            "request_id": getattr(request.state, "request_id", None),
        }

    q = (
        db.query(PriceObservation)
        .filter(PriceObservation.crop_id == crop.id)
        .order_by(PriceObservation.price_date.desc())
    )
    if market and market.lower() != "all":
        m = db.query(Market).filter(Market.name.ilike(market)).first()
        if m:
            q = q.filter(PriceObservation.market_id == m.id)

    items = list(reversed(q.limit(days).all()))
    data = [
        {
            "date": o.price_date.isoformat() if hasattr(o.price_date, "isoformat") else str(o.price_date),
            "price": float(o.modal_price or 0),
            "modal_price": float(o.modal_price or 0),
            "min_price": float(o.min_price or 0),
            "max_price": float(o.max_price or 0),
        }
        for o in items
    ]
    return {
        "success": True,
        "data": {"crop": crop.name, "history": data},
        "message": f"{len(data)} days",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/{obs_id}/provenance", response_model=dict)
def provenance(obs_id: str, request: Request, db: Session = Depends(get_db)):
    obs = db.get(PriceObservation, obs_id)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return {
        "success": True,
        "data": {
            "id": str(obs.id),
            "source_id": str(obs.source_id) if obs.source_id else None,
            "source_record_id": obs.source_record_id,
            "source_url": obs.source_url,
            "published_at": obs.published_at.isoformat() if obs.published_at else None,
            "retrieved_at": obs.retrieved_at.isoformat() if obs.retrieved_at else None,
            "ingestion_run_id": str(obs.ingestion_run_id) if obs.ingestion_run_id else None,
            "parser_version": obs.parser_version,
            "raw_payload_hash": obs.raw_payload_hash,
            "quality_status": obs.quality_status,
        },
        "message": "Provenance",
        "request_id": getattr(request.state, "request_id", None),
    }
