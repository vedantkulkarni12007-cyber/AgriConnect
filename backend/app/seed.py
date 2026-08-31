"""Deterministic demo seed — WHEAT-NASHIK-DEMO-001

Idempotent: safe to run multiple times (ON CONFLICT / upsert).
Uses demo_data.py as source, writes to PostgreSQL+PostGIS via SQLAlchemy.
Public IDs: KL-LOT-2026-0000X
"""

import hashlib
import uuid
from datetime import date, datetime, timedelta, timezone

from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    BuyerProfile,
    Crop,
    FarmerProfile,
    FPOProfile,
    IngestionRun,
    Lot,
    Market,
    MatchRuleSet,
    PriceObservation,
    PriceSource,
    StorageFacility,
    User,
)

MARKET_COORDS = {
    "Nashik": (19.9975, 73.7898),
    "Lasalgaon": (20.1224, 73.9698),
    "Pune": (18.5204, 73.8567),
    "Ahmednagar": (19.0948, 74.7480),
    "Solapur": (17.6868, 75.9064),
    "Aurangabad": (19.8762, 75.3433),
    "Nagpur": (21.1458, 79.0882),
    "Mumbai": (19.0760, 72.8777),
}

FIXED_UUIDS = {
    "crops": {
        "Onion": uuid.UUID("22222222-0000-0000-0000-000000000001"),
        "Tomato": uuid.UUID("22222222-0000-0000-0000-000000000002"),
        "Soybean": uuid.UUID("22222222-0000-0000-0000-000000000003"),
        "Cotton": uuid.UUID("22222222-0000-0000-0000-000000000004"),
        "Wheat": uuid.UUID("22222222-0000-0000-0000-000000000005"),
        "Potato": uuid.UUID("22222222-0000-0000-0000-000000000006"),
        "Chilli": uuid.UUID("22222222-0000-0000-0000-000000000007"),
        "Rice": uuid.UUID("22222222-0000-0000-0000-000000000008"),
    },
    "markets": {
        "Nashik": uuid.UUID("11111111-0000-0000-0000-000000000001"),
        "Lasalgaon": uuid.UUID("11111111-0000-0000-0000-000000000002"),
        "Pune": uuid.UUID("11111111-0000-0000-0000-000000000003"),
        "Ahmednagar": uuid.UUID("11111111-0000-0000-0000-000000000004"),
        "Solapur": uuid.UUID("11111111-0000-0000-0000-000000000005"),
        "Aurangabad": uuid.UUID("11111111-0000-0000-0000-000000000006"),
        "Nagpur": uuid.UUID("11111111-0000-0000-0000-000000000007"),
        "Mumbai": uuid.UUID("11111111-0000-0000-0000-000000000008"),
    },
    "users": {
        "ramesh": uuid.UUID("33333333-0000-0000-0000-000000000001"),
        "sunita": uuid.UUID("33333333-0000-0000-0000-000000000002"),
        "ganesh": uuid.UUID("33333333-0000-0000-0000-000000000003"),
        "laxmi": uuid.UUID("33333333-0000-0000-0000-000000000004"),
        "mehta": uuid.UUID("33333333-0000-0000-0000-000000000005"),
        "agro": uuid.UUID("33333333-0000-0000-0000-000000000006"),
        "fresh": uuid.UUID("33333333-0000-0000-0000-000000000007"),
        "fpo1": uuid.UUID("33333333-0000-0000-0000-000000000008"),
        "fpo2": uuid.UUID("33333333-0000-0000-0000-000000000009"),
        "admin": uuid.UUID("33333333-0000-0000-0000-000000000010"),
    },
}


def geog(lat, lng):
    return WKTElement(f"POINT({lng} {lat})", srid=4326, extended=True)


def run():
    db: Session = SessionLocal()
    try:
        for name, uid in FIXED_UUIDS["crops"].items():
            db.merge(
                Crop(
                    id=uid,
                    name=name,
                    category="vegetable"
                    if name in ("Onion", "Tomato", "Potato", "Chilli")
                    else "grain"
                    if name in ("Wheat", "Rice")
                    else "cash_crop",
                    unit="quintal",
                )
            )
        db.flush()

        for name, uid in FIXED_UUIDS["markets"].items():
            lat, lng = MARKET_COORDS[name]
            m = db.get(Market, uid)
            if not m:
                db.add(
                    Market(
                        id=uid,
                        name=name,
                        district="Nashik" if name == "Lasalgaon" else name if name in MARKET_COORDS else "Nashik",
                        state="Maharashtra",
                        latitude=lat,
                        longitude=lng,
                        location_geog=geog(lat, lng),
                        market_type="APMC",
                        is_active=True,
                    )
                )
            else:
                m.latitude = lat
                m.longitude = lng
                m.location_geog = geog(lat, lng)
        db.flush()

        src_id = uuid.UUID("99999999-0000-0000-0000-000000000001")
        db.merge(PriceSource(id=src_id, name="demo", url="demo://local", adapter="DemoPriceAdapter", is_active=True))
        db.flush()
        run_id = uuid.UUID("99999999-0000-0000-0000-000000000002")
        db.merge(
            IngestionRun(
                id=run_id,
                source_id=src_id,
                status="completed",
                records_fetched=120,
                records_ok=120,
                records_rejected=0,
                parser_version="1.0",
                finished_at=datetime.now(timezone.utc),
            )
        )
        db.flush()

        from data.demo_data import PRICES

        for crop_name, markets in PRICES.items():
            crop_id = FIXED_UUIDS["crops"].get(crop_name)
            if not crop_id:
                continue
            for market_name, series in markets.items():
                market_id = FIXED_UUIDS["markets"].get(market_name)
                if not market_id:
                    continue
                for rec in series:
                    d = date.fromisoformat(rec["date"])
                    h = hashlib.sha256(f"{crop_name}{market_name}{d}{rec['modal_price']}".encode()).hexdigest()[:16]
                    existing = (
                        db.query(PriceObservation)
                        .filter_by(crop_id=crop_id, market_id=market_id, price_date=d, source_id=src_id)
                        .first()
                    )
                    if not existing:
                        db.add(
                            PriceObservation(
                                crop_id=crop_id,
                                market_id=market_id,
                                price_date=d,
                                min_price=rec["min_price"],
                                modal_price=rec["modal_price"],
                                max_price=rec["max_price"],
                                volume_tonnes=rec["volume"],
                                source_id=src_id,
                                source_record_id=h,
                                source_url="demo://local",
                                published_at=datetime.combine(d, datetime.min.time(), tzinfo=timezone.utc),
                                retrieved_at=datetime.now(timezone.utc),
                                ingestion_run_id=run_id,
                                parser_version="1.0",
                                normalization_version="1.0",
                                raw_payload_hash=h,
                                quality_status="MEDIUM",
                            )
                        )
        db.flush()

        pw = hash_password("demo123!")
        users = [
            (
                FIXED_UUIDS["users"]["ramesh"],
                "ramesh@demo.com",
                "9876543210",
                "Ramesh Patil",
                "farmer",
                "Lasalgaon",
                "Nashik",
            ),
            (
                FIXED_UUIDS["users"]["sunita"],
                "sunita@demo.com",
                "9876543211",
                "Sunita Deshpande",
                "farmer",
                "Pune",
                "Pune",
            ),
            (
                FIXED_UUIDS["users"]["ganesh"],
                "ganesh@demo.com",
                "9876543212",
                "Ganesh Shinde",
                "farmer",
                "Solapur",
                "Solapur",
            ),
            (
                FIXED_UUIDS["users"]["laxmi"],
                "laxmi@demo.com",
                "9876543213",
                "Laxmi Jadhav",
                "farmer",
                "Nashik",
                "Nashik",
            ),
            (
                FIXED_UUIDS["users"]["mehta"],
                "mehta@demo.com",
                "9987654321",
                "Mehta Traders Pvt Ltd",
                "buyer",
                "Nashik",
                "Nashik",
            ),
            (FIXED_UUIDS["users"]["agro"], "agro@demo.com", "9987654322", "Pune Agro Exports", "buyer", "Pune", "Pune"),
            (
                FIXED_UUIDS["users"]["fresh"],
                "fresh@demo.com",
                "9987654323",
                "FreshMart Retail",
                "buyer",
                "Mumbai",
                "Mumbai",
            ),
            (FIXED_UUIDS["users"]["fpo1"], "fpo1@demo.com", "9900112233", "Nashik FPO", "fpo", "Nashik", "Nashik"),
            (
                FIXED_UUIDS["users"]["fpo2"],
                "fpo2@demo.com",
                "9900112234",
                "Marathwada FPO",
                "fpo",
                "Aurangabad",
                "Aurangabad",
            ),
            (
                FIXED_UUIDS["users"]["admin"],
                "admin@krishilink.demo",
                "9999999999",
                "KrishiLink Admin",
                "admin",
                "Pune",
                "Pune",
            ),
        ]
        for uid, email, phone, name, role, loc, dist in users:
            lat, lng = MARKET_COORDS.get(dist, MARKET_COORDS["Pune"])
            u = db.get(User, uid)
            if not u:
                db.add(
                    User(
                        id=uid,
                        email=email,
                        phone=phone,
                        full_name=name,
                        password_hash=pw,
                        role=role,
                        location=loc,
                        district=dist,
                        state="Maharashtra",
                        location_geog=geog(lat, lng),
                        is_verified=True,
                        is_active=True,
                    )
                )
            else:
                u.password_hash = pw
                u.is_verified = True
        db.flush()
        for uid in [
            FIXED_UUIDS["users"]["ramesh"],
            FIXED_UUIDS["users"]["sunita"],
            FIXED_UUIDS["users"]["ganesh"],
            FIXED_UUIDS["users"]["laxmi"],
        ]:
            if not db.query(FarmerProfile).filter_by(user_id=uid).first():
                db.add(FarmerProfile(user_id=uid, land_area_acres=5.5, primary_crops=["Onion", "Tomato"]))
        mp = {
            FIXED_UUIDS["users"]["mehta"]: ("Mehta Traders Pvt Ltd", "trader", ["Onion", "Tomato"], 50, 500),
            FIXED_UUIDS["users"]["agro"]: ("Pune Agro Exports", "exporter", ["Onion", "Soybean"], 200, 2000),
            FIXED_UUIDS["users"]["fresh"]: ("FreshMart Retail", "retailer", ["Tomato", "Potato"], 10, 100),
        }
        for uid, (bname, btype, crops, mn, mx) in mp.items():
            if not db.query(BuyerProfile).filter_by(user_id=uid).first():
                lat, lng = MARKET_COORDS.get("Pune", MARKET_COORDS["Pune"])
                db.add(
                    BuyerProfile(
                        user_id=uid,
                        business_name=bname,
                        business_type=btype,
                        crops_interested=crops,
                        min_quantity_quintals=mn,
                        max_quantity_quintals=mx,
                        is_verified=True,
                        rating=4.5,
                        location_geog=geog(lat, lng),
                    )
                )
        if not db.query(FPOProfile).filter_by(user_id=FIXED_UUIDS["users"]["fpo1"]).first():
            db.add(
                FPOProfile(
                    user_id=FIXED_UUIDS["users"]["fpo1"],
                    organization_name="Nashik Farmer Collective FPO",
                    member_count=120,
                    primary_crops=["Onion", "Tomato"],
                )
            )
        if not db.query(FPOProfile).filter_by(user_id=FIXED_UUIDS["users"]["fpo2"]).first():
            db.add(
                FPOProfile(
                    user_id=FIXED_UUIDS["users"]["fpo2"],
                    organization_name="Marathwada Agri FPO",
                    member_count=85,
                    primary_crops=["Soybean", "Cotton"],
                )
            )

        if not db.query(MatchRuleSet).filter_by(version="v1.0").first():
            db.add(
                MatchRuleSet(
                    version="v1.0",
                    weights={
                        "crop": 30,
                        "grade": 15,
                        "quantity": 15,
                        "distance": 15,
                        "price": 10,
                        "time": 5,
                        "verification": 10,
                    },
                    is_active=True,
                )
            )
        if not db.query(MatchRuleSet).filter_by(version="v1.2").first():
            db.add(
                MatchRuleSet(
                    version="v1.2",
                    weights={
                        "crop": 30,
                        "grade": 15,
                        "quantity": 15,
                        "distance": 15,
                        "price": 10,
                        "time": 5,
                        "verification": 10,
                    },
                    is_active=False,
                )
            )

        lots = [
            (
                "44444444-0000-0000-0000-000000000001",
                FIXED_UUIDS["users"]["ramesh"],
                "Onion",
                "KL-LOT-2026-000001",
                500,
                "A",
                1800,
                "Lasalgaon",
                "Nashik",
            ),
            (
                "44444444-0000-0000-0000-000000000002",
                FIXED_UUIDS["users"]["sunita"],
                "Tomato",
                "KL-LOT-2026-000002",
                200,
                "A",
                1200,
                "Pune",
                "Pune",
            ),
            (
                "44444444-0000-0000-0000-000000000003",
                FIXED_UUIDS["users"]["ganesh"],
                "Soybean",
                "KL-LOT-2026-000003",
                300,
                "B",
                4500,
                "Solapur",
                "Solapur",
            ),
            (
                "44444444-0000-0000-0000-000000000004",
                FIXED_UUIDS["users"]["laxmi"],
                "Wheat",
                "KL-LOT-2026-000004",
                1000,
                "A",
                2150,
                "Nashik",
                "Nashik",
            ),
            (
                "44444444-0000-0000-0000-000000000005",
                FIXED_UUIDS["users"]["ramesh"],
                "Tomato",
                "KL-LOT-2026-000005",
                80,
                "B",
                900,
                "Lasalgaon",
                "Nashik",
            ),
        ]
        for lid, owner, crop, pub, qty, grade, price, loc, dist in lots:
            if not db.get(Lot, uuid.UUID(lid)):
                lat, lng = MARKET_COORDS.get(dist, MARKET_COORDS["Pune"])
                cid = FIXED_UUIDS["crops"].get(crop)
                db.add(
                    Lot(
                        id=uuid.UUID(lid),
                        public_id=pub,
                        owner_id=owner,
                        crop_id=cid,
                        crop_name=crop,
                        grade=grade,
                        quantity=qty,
                        unit="quintal",
                        asking_price=price,
                        location_text=loc,
                        district=dist,
                        location_geog=geog(lat, lng),
                        status="PUBLISHED",
                        available_from=date.today(),
                        available_until=date.today() + timedelta(days=14),
                    )
                )

        for name, dist, cap in [("Nashik ColdStore", "Nashik", 5000), ("Pune Warehouse", "Pune", 10000)]:
            if not db.query(StorageFacility).filter_by(name=name).first():
                lat, lng = MARKET_COORDS[dist]
                db.add(
                    StorageFacility(
                        name=name,
                        type="cold_storage" if "Cold" in name else "warehouse",
                        capacity=cap,
                        available_capacity=cap * 0.8,
                        location_text=dist,
                        location_geog=geog(lat, lng),
                        cost_per_unit=2.5,
                        status="ACTIVE",
                        verification_status="VERIFIED",
                    )
                )

        db.commit()
        print("Seed WHEAT-NASHIK-DEMO-001 applied")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
