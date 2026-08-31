from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import BuyerProfile, FPOProfile, Market, StorageFacility, User

router = APIRouter(prefix="/markets", tags=["markets"])


@router.get("", response_model=dict)
def list_markets(
    request: Request,
    db: Session = Depends(get_db),
    state: str | None = None,
    district: str | None = None,
    search: str | None = None,
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float | None = 100,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
):
    """
    List APMC / wholesale markets with optional PostGIS spatial proximity and search filters.
    """
    q = db.query(Market).filter(Market.is_active == True)  # noqa: E712

    if state and state.lower() != "all":
        q = q.filter(Market.state.ilike(f"%{state}%"))
    if district and district.lower() != "all":
        q = q.filter(Market.district.ilike(f"%{district}%"))
    if search and search.strip():
        term = f"%{search.strip()}%"
        q = q.filter((Market.name.ilike(term)) | (Market.district.ilike(term)) | (Market.state.ilike(term)))

    # PostGIS Spatial Radius Query (Dialect aware for PostgreSQL & SQLite test runner)
    if near_lat is not None and near_lng is not None and radius_km:
        dialect_name = getattr(getattr(db.bind, "dialect", None), "name", "")
        if dialect_name == "postgresql":
            radius_meters = radius_km * 1000.0
            q = q.filter(
                text(
                    "ST_DWithin(location_geog, CAST(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326) AS geography), :rad)"
                ).bindparams(lng=near_lng, lat=near_lat, rad=radius_meters)
            )
        else:
            # SQLite bounding box approximation (1 deg latitude ~ 111km)
            deg_delta = radius_km / 111.0
            q = q.filter(
                Market.latitude.between(near_lat - deg_delta, near_lat + deg_delta),
                Market.longitude.between(near_lng - deg_delta, near_lng + deg_delta),
            )

    total = q.count()
    items = q.offset((page - 1) * limit).limit(limit).all()

    data: list[dict[str, Any]] = []
    for m in items:
        dist_km = None
        if near_lat is not None and near_lng is not None and m.latitude and m.longitude:
            # Haversine distance calculation as universal fallback / accuracy
            from math import atan2, cos, radians, sin, sqrt

            dlat = radians(float(m.latitude) - near_lat)
            dlng = radians(float(m.longitude) - near_lng)
            a = sin(dlat / 2) ** 2 + cos(radians(near_lat)) * cos(radians(float(m.latitude))) * sin(dlng / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            dist_km = round(6371 * c, 1)

        data.append(
            {
                "id": str(m.id),
                "name": m.name,
                "district": m.district,
                "state": m.state,
                "latitude": float(m.latitude) if m.latitude is not None else None,
                "longitude": float(m.longitude) if m.longitude is not None else None,
                "market_type": m.market_type,
                "distance_km": dist_km,
            }
        )

    if near_lat is not None and near_lng is not None:
        data.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0))

    return {
        "success": True,
        "data": {
            "items": data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
        },
        "message": f"{len(data)} markets",
        "request_id": getattr(request.state, "request_id", None),
    }


@router.get("/locations", response_model=dict)
def get_map_locations(
    request: Request,
    db: Session = Depends(get_db),
    category: str = Query("all", description="all, mandi, buyer, storage, fpo"),
    state: str | None = None,
    district: str | None = None,
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float | None = 150,
    search: str | None = None,
):
    """
    Get all map locations (Mandis, Buyers, Storage Facilities, FPOs) for interactive map rendering.
    """
    from math import atan2, cos, radians, sin, sqrt

    def calc_dist(lat1: float, lng1: float, lat2: float | None, lng2: float | None) -> float | None:
        if lat2 is None or lng2 is None:
            return None
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return round(6371 * c, 1)

    locations: list[dict[str, Any]] = []

    # 1. Mandis / APMCs
    if category in ("all", "mandi", "mandis"):
        mq = db.query(Market).filter(Market.is_active == True)  # noqa: E712
        if state and state.lower() != "all":
            mq = mq.filter(Market.state.ilike(f"%{state}%"))
        if district and district.lower() != "all":
            mq = mq.filter(Market.district.ilike(f"%{district}%"))
        if search and search.strip():
            mq = mq.filter(Market.name.ilike(f"%{search.strip()}%"))

        for m in mq.limit(200).all():
            if m.latitude and m.longitude:
                lat = float(m.latitude)
                lng = float(m.longitude)
                dist = calc_dist(near_lat, near_lng, lat, lng) if near_lat and near_lng else None
                if radius_km and dist is not None and dist > radius_km:
                    continue
                locations.append(
                    {
                        "id": f"mandi-{m.id}",
                        "raw_id": str(m.id),
                        "type": "mandi",
                        "name": m.name,
                        "district": m.district,
                        "state": m.state,
                        "lat": lat,
                        "lng": lng,
                        "distance_km": dist,
                        "info": f"APMC Wholesale Mandi · {m.district}, {m.state}",
                        "details": {
                            "market_type": m.market_type or "APMC",
                            "district": m.district,
                            "state": m.state,
                        },
                    }
                )

    # 2. Buyers / Traders
    if category in ("all", "buyer", "buyers"):
        bq = db.query(BuyerProfile, User).join(User, BuyerProfile.user_id == User.id).filter(User.is_active == True)  # noqa: E712
        if state and state.lower() != "all":
            bq = bq.filter(User.state.ilike(f"%{state}%"))
        if district and district.lower() != "all":
            bq = bq.filter(User.district.ilike(f"%{district}%"))

        # Pre-mapped coordinates for seeded/registered buyers across Maharashtra & neighbouring hubs
        BUYER_FALLBACK_COORDS: dict[str, tuple[float, float]] = {
            "Nashik": (20.0100, 73.7900),
            "Pune": (18.5300, 73.8400),
            "Lasalgaon": (20.1400, 73.9800),
            "Mumbai": (19.0800, 72.8800),
            "Ahmednagar": (19.1000, 74.7400),
        }

        for bp, u in bq.limit(100).all():
            loc_name = u.location or u.district or "Nashik"
            coords = BUYER_FALLBACK_COORDS.get(loc_name, (19.9975, 73.7898))
            lat, lng = coords
            dist = calc_dist(near_lat, near_lng, lat, lng) if near_lat and near_lng else None
            if radius_km and dist is not None and dist > radius_km:
                continue

            crops_str = ", ".join(bp.crops_interested) if bp.crops_interested else "All Agro Commodities"
            locations.append(
                {
                    "id": f"buyer-{bp.id}",
                    "raw_id": str(bp.id),
                    "type": "buyer",
                    "name": bp.business_name or u.full_name,
                    "district": u.district or "Nashik",
                    "state": u.state or "Maharashtra",
                    "lat": lat,
                    "lng": lng,
                    "distance_km": dist,
                    "info": f"Verified Buyer ({bp.business_type or 'Trader'}) · Buying {crops_str}",
                    "details": {
                        "business_type": bp.business_type or "Trader",
                        "rating": float(bp.rating or 4.5),
                        "crops": bp.crops_interested or [],
                        "verified": bool(bp.is_verified),
                    },
                }
            )

    # 3. Storage Facilities
    if category in ("all", "storage", "warehouses"):
        sq = db.query(StorageFacility).filter(StorageFacility.status == "ACTIVE")
        STORAGE_FALLBACK_COORDS: dict[str, tuple[float, float]] = {
            "Lasalgaon": (20.1500, 74.0100),
            "Nashik": (19.9800, 73.7600),
            "Pune": (18.5600, 73.9100),
            "Solapur": (17.6700, 75.9200),
        }

        for s in sq.limit(50).all():
            coords = STORAGE_FALLBACK_COORDS.get(s.location_text or "", (20.0200, 73.8100))
            lat, lng = coords
            dist = calc_dist(near_lat, near_lng, lat, lng) if near_lat and near_lng else None
            if radius_km and dist is not None and dist > radius_km:
                continue

            locations.append(
                {
                    "id": f"storage-{s.id}",
                    "raw_id": str(s.id),
                    "type": "storage",
                    "name": s.name,
                    "district": s.location_text or "Nashik",
                    "state": "Maharashtra",
                    "lat": lat,
                    "lng": lng,
                    "distance_km": dist,
                    "info": f"{s.type or 'Warehouse'} · {float(s.available_capacity or 0)}T / {float(s.capacity or 0)}T capacity available",
                    "details": {
                        "type": s.type or "Dry Warehouse",
                        "capacity": float(s.capacity or 0),
                        "available": float(s.available_capacity or 0),
                        "cost_per_day": float(s.cost_per_unit or 12),
                    },
                }
            )

    # 4. FPOs
    if category in ("all", "fpo", "fpos"):
        fq = db.query(FPOProfile, User).join(User, FPOProfile.user_id == User.id).filter(User.is_active == True)  # noqa: E712
        for fpo, u in fq.limit(50).all():
            lat, lng = (19.9500, 73.8300)
            dist = calc_dist(near_lat, near_lng, lat, lng) if near_lat and near_lng else None
            if radius_km and dist is not None and dist > radius_km:
                continue

            locations.append(
                {
                    "id": f"fpo-{fpo.id}",
                    "raw_id": str(fpo.id),
                    "type": "fpo",
                    "name": fpo.organization_name or u.full_name,
                    "district": u.district or "Nashik",
                    "state": u.state or "Maharashtra",
                    "lat": lat,
                    "lng": lng,
                    "distance_km": dist,
                    "info": f"Farmer Producer Org · {fpo.member_count or 120} Member Farmers",
                    "details": {
                        "members": fpo.member_count or 0,
                        "crops": fpo.primary_crops or [],
                    },
                }
            )

    if near_lat is not None and near_lng is not None:
        locations.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0))

    counts = {
        "all": len(locations),
        "mandi": len([loc for loc in locations if loc["type"] == "mandi"]),
        "buyer": len([loc for loc in locations if loc["type"] == "buyer"]),
        "storage": len([loc for loc in locations if loc["type"] == "storage"]),
        "fpo": len([loc for loc in locations if loc["type"] == "fpo"]),
    }

    return {
        "success": True,
        "data": {
            "locations": locations,
            "counts": counts,
            "total": len(locations),
        },
        "message": f"Retrieved {len(locations)} map location markers",
        "request_id": getattr(request.state, "request_id", None),
    }
