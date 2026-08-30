import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")
MANDI_API_URL = os.getenv(
    "MANDI_API_URL",
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
)


def fetch_mandi_prices(limit: int = 100) -> list[dict[str, Any]]:
    """
    Fetch mandi price records from data.gov.in.

    Returns the first `limit` records from the API.
    """

    if not MANDI_API_KEY:
        raise RuntimeError(
            "MANDI_API_KEY is not configured in backend/.env"
        )

    params = {
        "api-key": MANDI_API_KEY,
        "format": "json",
        "limit": limit,
    }

    response = requests.get(
        MANDI_API_URL,
        params=params,
        timeout=15,
    )

    response.raise_for_status()

    payload = response.json()

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise RuntimeError(
            "Unexpected response format from data.gov.in"
        )

    return records[:limit]