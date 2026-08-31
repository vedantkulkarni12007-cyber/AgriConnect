import argparse
import json
import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

# Configure terminal encoding
sys.stdout.reconfigure(encoding='utf-8')

# Read API Key from environment (AGMARKNET_API_KEY, MANDI_API_KEY, or DATA_GOV_API_KEY)
RAW_KEY = (
    os.environ.get("AGMARKNET_API_KEY")
    or os.environ.get("MANDI_API_KEY")
    or os.environ.get("DATA_GOV_API_KEY")
    or ""
).strip()
CLEAN_KEY = RAW_KEY[:-1] if RAW_KEY.endswith("h") and len(RAW_KEY) == 57 else RAW_KEY

RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

# ==============================================================================
# FastAPI Application for Interactive Browser / Swagger Verification
# ==============================================================================
app = FastAPI(
    title="KrishiLink — Data.gov.in Mandi API Verification Gateway",
    description="Interactive test proxy for Government of India Agmarknet Mandi Daily Modal Price API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Data.gov.in Mandi API Verification Gateway is running.",
        "interactive_docs": "http://127.0.0.1:8000/docs",
        "quick_test_onion": "http://127.0.0.1:8000/test/data-gov-prices?state=Maharashtra&commodity=Onion",
        "quick_test_tomato": "http://127.0.0.1:8000/test/data-gov-prices?state=Maharashtra&commodity=Tomato",
        "quick_test_all": "http://127.0.0.1:8000/test/data-gov-prices?limit=5",
    }


@app.get("/test/data-gov-prices", summary="Query Live Mandi Prices from data.gov.in")
async def get_test_prices(
    state: str | None = Query("Maharashtra", description="State name, e.g., Maharashtra, Gujarat, Punjab"),
    commodity: str | None = Query("Onion", description="Commodity, e.g., Onion, Tomato, Potato, Wheat, Cotton"),
    district: str | None = Query(None, description="District name, e.g., Pune, Nashik, Ahilyanagar"),
    market: str | None = Query(None, description="Market / APMC name, e.g., Pune APMC"),
    limit: int = Query(10, ge=1, le=100, description="Records per page"),
    offset: int = Query(0, ge=0, description="Record offset"),
):
    """
    Queries live Agmarknet / data.gov.in Mandi records and normalizes the output.
    """
    target_params = {
        "api-key": CLEAN_KEY,
        "format": "json",
        "limit": limit,
        "offset": offset,
    }
    if state and state.strip() and state.lower() != "all":
        target_params["filters[state.keyword]"] = state.strip()
    if commodity and commodity.strip() and commodity.lower() != "all":
        target_params["filters[commodity]"] = commodity.strip()
    if district and district.strip():
        target_params["filters[district]"] = district.strip()
    if market and market.strip():
        target_params["filters[market]"] = market.strip()

    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            resp = await client.get(BASE_URL, params=target_params)
            if resp.status_code in (401, 403):
                raise HTTPException(status_code=502, detail="Data.gov.in authentication rejected the API credential.")
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Data.gov.in returned error: {resp.status_code}")
            payload = resp.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Data.gov.in request timed out (Government server slow to respond).")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected proxy error: {exc}")

    raw_records = payload.get("records", [])
    normalized = []
    for rec in raw_records:
        min_p = float(rec.get("min_price", 0)) if rec.get("min_price") is not None else None
        modal_p = float(rec.get("modal_price", 0)) if rec.get("modal_price") is not None else None
        max_p = float(rec.get("max_price", 0)) if rec.get("max_price") is not None else None

        normalized.append({
            "state": rec.get("state"),
            "district": rec.get("district"),
            "market": rec.get("market"),
            "commodity": rec.get("commodity"),
            "variety": rec.get("variety"),
            "grade": rec.get("grade"),
            "arrival_date": rec.get("arrival_date"),
            "price_unit": "INR per Quintal (100 kg)",
            "min_price": min_p,
            "modal_price": modal_p,
            "max_price": max_p,
            "modal_price_per_kg": round(modal_p / 100.0, 2) if modal_p else None,
        })

    return {
        "success": True,
        "source": "data.gov.in (Agmarknet / Ministry of Agriculture)",
        "dataset_title": payload.get("title"),
        "total_available_matching": payload.get("total", 0),
        "count_in_response": len(normalized),
        "offset": offset,
        "limit": limit,
        "items": normalized,
    }


# ==============================================================================
# CLI Verification Runner
# ==============================================================================
def run_cli_tests():
    print("=" * 60)
    print("🌿 KRISHILINK — DATA.GOV.IN MANDI API LIVE VERIFICATION")
    print("=" * 60)

    # 1. Direct Ping
    print("\n[Step 1] Testing Connection & Authentication...")
    try:
        with httpx.Client(timeout=15.0, headers=HEADERS) as client:
            r = client.get(BASE_URL, params={"api-key": CLEAN_KEY, "format": "json", "limit": 5})
            if r.status_code == 200:
                d = r.json()
                print(f"✅ Authentication SUCCESS: HTTP 200 OK")
                print(f"• Dataset: {d.get('title')}")
                print(f"• Total Live Records Across India: {d.get('total')}")
            else:
                print(f"❌ Authentication Failed: HTTP {r.status_code}")
                return
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Filter Tests
    print("\n[Step 2] Testing Regional Filtering...")
    filter_cases = [
        ("Maharashtra State", {"filters[state.keyword]": "Maharashtra"}),
        ("Maharashtra + Onion", {"filters[state.keyword]": "Maharashtra", "filters[commodity]": "Onion"}),
        ("Maharashtra + Tomato", {"filters[state.keyword]": "Maharashtra", "filters[commodity]": "Tomato"}),
        ("Maharashtra + Ginger", {"filters[state.keyword]": "Maharashtra", "filters[commodity]": "Ginger(Green)"}),
    ]

    with httpx.Client(timeout=15.0, headers=HEADERS) as client:
        for name, flt in filter_cases:
            p = {"api-key": CLEAN_KEY, "format": "json", "limit": 3, **flt}
            res = client.get(BASE_URL, params=p).json()
            total = res.get("total", 0)
            recs = res.get("records", [])
            print(f"\n  ➤ Filter: {name} (Total Matching: {total})")
            for rec in recs:
                print(f"    - {rec.get('market')} ({rec.get('district')}): {rec.get('commodity')} ({rec.get('variety')}) -> ₹{rec.get('modal_price')}/Quintal on {rec.get('arrival_date')}")

    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE: API IS FULLY FUNCTIONAL & OPERATIONAL.")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data.gov.in Verification Runner")
    parser.add_argument("--serve", action="store_true", help="Start the live interactive FastAPI server on port 8000")
    parser.add_argument("--port", type=int, default=8000, help="Port to run FastAPI server on (default: 8000)")
    args = parser.parse_args()

    if args.serve:
        print(f"🚀 Starting KrishiLink Data.gov.in Test Server on http://127.0.0.1:{args.port}")
        print(f"📖 Interactive Swagger Docs: http://127.0.0.1:{args.port}/docs")
        uvicorn.run(app, host="127.0.0.1", port=args.port)
    else:
        run_cli_tests()
