import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


# backend/app/modules/prices/mandi_api.py
# backend/.env is three parents above this file
BACKEND_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = BACKEND_DIR / ".env"

load_dotenv(ENV_FILE)


MANDI_API_KEY = os.getenv("MANDI_API_KEY", "")

MANDI_API_URL = os.getenv(
    "MANDI_API_URL",
    "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070",
)


def fetch_mandi_prices(limit: int = 100) -> list[dict[str, Any]]:
    """
    Fetch ONLY the first 100 mandi records
    from data.gov.in.
    """

    if not MANDI_API_KEY:
        raise RuntimeError(
            f"MANDI_API_KEY is missing. Expected it in: {ENV_FILE}"
        )

    # Hard cap: we NEVER request more than 100.
    limit = min(limit, 100)

    params = {
        "api-key": MANDI_API_KEY,
        "format": "json",
        "limit": limit,
        "offset": 0,
    }

    print("Fetching FIRST 100 mandi records...")

    response = requests.get(
        MANDI_API_URL,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    payload = response.json()

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise RuntimeError(
            "Unexpected response format from data.gov.in"
        )

    # Extra safety: never return more than 100.
    records = records[:100]

    print(f"API returned {len(records)} records.")

    return records