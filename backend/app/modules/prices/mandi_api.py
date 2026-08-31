import logging
import os
import time
from typing import Any

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory cache: { cache_key: (timestamp, normalized_records) }
_PRICE_CACHE: dict[str, tuple[float, list[dict[str, Any]]]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes cache to avoid rate limits


def get_api_key() -> str:
    """Retrieve government mandi API key from settings or environment."""
    key = (
        settings.agmarknet_api_key
        or settings.mandi_api_key
        or os.getenv("AGMARKNET_API_KEY")
        or os.getenv("MANDI_API_KEY")
        or ""
    )
    key = key.strip()
    if key.endswith("h") and len(key) == 57:
        key = key[:-1]
    return key


def normalize_record(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw record from data.gov.in into a consistent KrishiLink structure."""
    min_p = None
    modal_p = None
    max_p = None

    try:
        if raw.get("min_price") is not None and str(raw.get("min_price")).strip():
            min_p = float(raw.get("min_price"))
    except (ValueError, TypeError):
        pass

    try:
        if raw.get("modal_price") is not None and str(raw.get("modal_price")).strip():
            modal_p = float(raw.get("modal_price"))
    except (ValueError, TypeError):
        pass

    try:
        if raw.get("max_price") is not None and str(raw.get("max_price")).strip():
            max_p = float(raw.get("max_price"))
    except (ValueError, TypeError):
        pass

    commodity = str(raw.get("commodity", "")).strip()
    market = str(raw.get("market", "")).strip()
    district = str(raw.get("district", "")).strip()
    state = str(raw.get("state", "")).strip()
    variety = str(raw.get("variety", "Standard")).strip()
    grade = str(raw.get("grade", "FAQ")).strip()
    arrival_date = str(raw.get("arrival_date", "")).strip()

    return {
        "state": state,
        "district": district,
        "market": market,
        "commodity": commodity,
        "variety": variety,
        "grade": grade,
        "arrival_date": arrival_date,
        "min_price": min_p,
        "modal_price": modal_p,
        "max_price": max_p,
        "unit": "quintal",
    }


def fetch_mandi_prices(
    limit: int = 50,
    offset: int = 0,
    state: str | None = None,
    district: str | None = None,
    market: str | None = None,
    commodity: str | None = None,
    date: str | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch and normalize mandi price records from Government of India data.gov.in.
    Applies server-side caching to prevent API rate limiting.
    """
    api_key = get_api_key()
    if not api_key:
        logger.warning("AGMARKNET_API_KEY/MANDI_API_KEY is not configured in backend environment.")
        return []

    cache_key = f"{limit}:{offset}:{state}:{district}:{market}:{commodity}:{date}"
    now = time.time()
    if cache_key in _PRICE_CACHE:
        cached_time, cached_data = _PRICE_CACHE[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            return cached_data

    params: dict[str, Any] = {
        "api-key": api_key,
        "format": "json",
        "limit": min(limit, 100),
        "offset": max(0, offset),
    }

    if state and state.strip() and state.lower() != "all":
        params["filters[state.keyword]"] = state.strip()
    if district and district.strip() and district.lower() != "all":
        params["filters[district]"] = district.strip()
    if market and market.strip() and market.lower() != "all":
        params["filters[market]"] = market.strip()
    if commodity and commodity.strip() and commodity.lower() != "all":
        params["filters[commodity]"] = commodity.strip()
    if date and date.strip():
        params["filters[arrival_date]"] = date.strip()

    api_url = getattr(
        settings, "mandi_api_url", "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
    )

    try:
        response = requests.get(
            api_url,
            params=params,
            timeout=15,
            headers={
                "User-Agent": "KrishiLink-Platform/2.0",
                "Accept": "application/json",
            },
        )
        if response.status_code != 200:
            logger.error("data.gov.in API returned HTTP status %s: %s", response.status_code, response.text[:200])
            return []

        payload = response.json()
        raw_records = payload.get("records", [])
        if not isinstance(raw_records, list):
            return []

        normalized = [normalize_record(r) for r in raw_records if r.get("commodity") and r.get("market")]
        _PRICE_CACHE[cache_key] = (now, normalized)
        return normalized

    except Exception as exc:
        logger.error("Failed to query data.gov.in mandi prices: %s", exc)
        return []
