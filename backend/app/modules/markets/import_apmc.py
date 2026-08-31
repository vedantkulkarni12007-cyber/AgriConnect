import logging
import os
import time
from typing import Any

import requests
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Market

logger = logging.getLogger(__name__)

# Nominatim Geocoding Cache file to prevent repetitive external queries
CACHE_FILE = os.path.join(os.path.dirname(__file__), "geocode_cache.json")


def load_geocode_cache() -> dict[str, Any]:
    if os.path.exists(CACHE_FILE):
        try:
            import json

            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_geocode_cache(cache: dict[str, Any]) -> None:
    try:
        import json

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.warning("Could not save geocode cache: %s", e)


def geocode_address(query: str, cache: dict[str, Any]) -> tuple[float, float] | None:
    """
    Perform geocoding query against Nominatim / OpenStreetMap.
    Respects rate limits (1 request per second) and caches coordinates.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return None

    if cleaned_query in cache:
        cached = cache[cleaned_query]
        if cached:
            return (float(cached["lat"]), float(cached["lon"]))
        return None

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": cleaned_query,
        "format": "json",
        "limit": 1,
        "countrycodes": "in",
    }
    headers = {
        "User-Agent": "KrishiLink-AgriPlatform/2.0 (contact@krishilink.org)",
        "Accept-Language": "en",
    }

    try:
        time.sleep(1.0)  # Respect OpenStreetMap 1 req/sec policy
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                cache[cleaned_query] = {"lat": lat, "lon": lon}
                save_geocode_cache(cache)
                return (lat, lon)
    except Exception as exc:
        logger.warning("Geocoding failed for '%s': %s", cleaned_query, exc)

    cache[cleaned_query] = None
    save_geocode_cache(cache)
    return None


# Well-known district and APMC coordinates across key agricultural centers
STANDARD_MANDI_COORDINATES: dict[str, tuple[float, float, str, str]] = {
    # Maharashtra Mandis
    "Lasalgaon APMC": (20.1224, 73.9698, "Nashik", "Maharashtra"),
    "Nashik APMC": (19.9975, 73.7898, "Nashik", "Maharashtra"),
    "Pune APMC": (18.5204, 73.8567, "Pune", "Maharashtra"),
    "Ahmednagar APMC": (19.0948, 74.7480, "Ahmednagar", "Maharashtra"),
    "Solapur APMC": (17.6868, 75.9064, "Solapur", "Maharashtra"),
    "Chhatrapati Sambhaji Nagar (Aurangabad) APMC": (19.8762, 75.3433, "Chhatrapati Sambhaji Nagar", "Maharashtra"),
    "Nagpur APMC": (21.1458, 79.0882, "Nagpur", "Maharashtra"),
    "Vashi APMC (Mumbai)": (19.0760, 72.8777, "Mumbai", "Maharashtra"),
    "Kolhapur APMC": (16.7050, 74.2433, "Kolhapur", "Maharashtra"),
    "Sangli APMC": (16.8524, 74.5815, "Sangli", "Maharashtra"),
    "Satara APMC": (17.6805, 74.0183, "Satara", "Maharashtra"),
    "Jalgaon APMC": (21.0077, 75.5626, "Jalgaon", "Maharashtra"),
    "Amravati APMC": (20.9374, 77.7796, "Amravati", "Maharashtra"),
    "Akola APMC": (20.7002, 77.0082, "Akola", "Maharashtra"),
    "Latur APMC": (18.4088, 76.5604, "Latur", "Maharashtra"),
    "Nanded APMC": (19.1383, 77.3210, "Nanded", "Maharashtra"),
    # Karnataka Mandis
    "Bengaluru (Yeshwanthpur) APMC": (13.0163, 77.5557, "Bengaluru Urban", "Karnataka"),
    "Mysuru APMC (Bandipalya)": (12.2818, 76.6667, "Mysuru", "Karnataka"),
    "Belagavi APMC": (15.8497, 74.4977, "Belagavi", "Karnataka"),
    "Hubballi APMC (Amargol)": (15.3949, 75.1017, "Dharwad", "Karnataka"),
    "Kalaburagi APMC": (17.3297, 76.8343, "Kalaburagi", "Karnataka"),
    "Shivamogga APMC": (13.9299, 75.5681, "Shivamogga", "Karnataka"),
    "Davanagere APMC": (14.4644, 75.9218, "Davanagere", "Karnataka"),
    "Ballari APMC": (15.1394, 76.9214, "Ballari", "Karnataka"),
    "Kolar APMC": (13.1367, 78.1291, "Kolar", "Karnataka"),
    "Chikkaballapura APMC": (13.4325, 77.7275, "Chikkaballapura", "Karnataka"),
    "Hassan APMC": (13.0072, 76.1032, "Hassan", "Karnataka"),
    "Mandya APMC": (12.5218, 76.8951, "Mandya", "Karnataka"),
    "Tumakuru APMC": (13.3409, 77.1010, "Tumakuru", "Karnataka"),
    "Chitradurga APMC": (14.2251, 76.3980, "Chitradurga", "Karnataka"),
    "Bagalkote APMC": (16.1817, 75.6958, "Bagalkote", "Karnataka"),
    "Vijayapura APMC": (16.8302, 75.7100, "Vijayapura", "Karnataka"),
    "Raichur APMC": (16.2076, 77.3463, "Raichur", "Karnataka"),
    "Bidar APMC": (17.9104, 77.5199, "Bidar", "Karnataka"),
    "Gadag APMC": (15.4298, 75.6329, "Gadag", "Karnataka"),
    "Haveri APMC": (14.7958, 75.3991, "Haveri", "Karnataka"),
    "Udupi APMC": (13.3409, 74.7421, "Udupi", "Karnataka"),
    "Mangaluru APMC (Baikampady)": (12.9352, 74.8118, "Dakshina Kannada", "Karnataka"),
}


def geog(lat: float, lng: float) -> WKTElement:
    return WKTElement(f"POINT({lng} {lat})", srid=4326, extended=True)


def import_standard_mandis(db: Session) -> int:
    """Import and update core APMC mandis with coordinates."""
    count = 0
    for mandi_name, (lat, lng, district, state) in STANDARD_MANDI_COORDINATES.items():
        m = db.query(Market).filter(Market.name == mandi_name).first()
        if not m:
            m = Market(
                name=mandi_name,
                district=district,
                state=state,
                latitude=lat,
                longitude=lng,
                location_geog=geog(lat, lng),
                market_type="APMC",
                is_active=True,
            )
            db.add(m)
        else:
            m.latitude = lat
            m.longitude = lng
            m.district = district
            m.state = state
            m.location_geog = geog(lat, lng)
        count += 1
    db.commit()
    logger.info("Imported %d standard APMC mandis with verified coordinates.", count)
    return count


if __name__ == "__main__":
    db = SessionLocal()
    try:
        c = import_standard_mandis(db)
        print(f"Successfully processed {c} APMC mandis with PostGIS coordinates.")
    finally:
        db.close()
