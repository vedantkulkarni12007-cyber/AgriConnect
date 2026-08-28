# routes/prices.py
# ─────────────────────────────────────────────────────────────────────────────
# Price-related API endpoints.
# Delegates business logic to services/price_service.py.
# ─────────────────────────────────────────────────────────────────────────────

from flask import Blueprint, request, jsonify
from services.price_service import get_all_prices, get_price_history, get_best_price

prices_bp = Blueprint("prices", __name__)


@prices_bp.route("/api/prices", methods=["GET"])
def list_prices():
    """
    GET /api/prices?crop=Onion&market=Nashik

    Returns the latest price for every (crop, market) combination.
    Optionally filter by crop and/or market query parameters.

    Query parameters:
      crop   (optional) – e.g. 'Onion', 'Tomato'
      market (optional) – e.g. 'Nashik', 'Pune'

    Response example:
    {
      "success": true,
      "data": [
        {
          "crop": "Onion",
          "market": "Nashik",
          "modal_price": 1200,
          "min_price": 1116,
          "max_price": 1284,
          "volume": 330,
          "date": "2026-08-28"
        },
        ...
      ],
      "message": "8 price records found"
    }
    """
    # Read optional query string parameters
    crop   = request.args.get("crop",   None)
    market = request.args.get("market", None)

    prices = get_all_prices(crop=crop, market=market)

    return jsonify({
        "success": True,
        "data":    prices,
        "message": f"{len(prices)} price record(s) found",
    }), 200


@prices_bp.route("/api/prices/<string:crop>", methods=["GET"])
def prices_for_crop(crop: str):
    """
    GET /api/prices/<crop>

    Returns today's price for a specific crop across ALL markets,
    plus full 15-day price history for each market.

    Path parameter:
      crop – e.g. 'Onion', 'Tomato', 'Cotton'

    Also includes the best_price summary showing which market pays highest.

    Response example:
    {
      "success": true,
      "data": {
        "crop": "Onion",
        "best_price": { "best_market": "Mumbai", "modal_price": 1495 },
        "latest_prices": [ ... ],
        "history_by_market": { "Nashik": [...], "Pune": [...] }
      },
      "message": "Price data for Onion"
    }
    """
    from data.demo_data import MARKETS

    crop_norm = crop.strip().title()

    # Get today's price across all markets
    latest_prices = get_all_prices(crop=crop_norm)

    if not latest_prices:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"No price data found for crop: {crop_norm}",
        }), 404

    # Get 15-day history for each market
    history_by_market = {}
    for market in MARKETS:
        hist = get_price_history(crop_norm, market, days=15)
        if hist:
            history_by_market[market] = hist

    # Which market is paying the best today?
    best = get_best_price(crop_norm)

    return jsonify({
        "success": True,
        "data": {
            "crop":              crop_norm,
            "best_price":        best,
            "latest_prices":     latest_prices,
            "history_by_market": history_by_market,
        },
        "message": f"Price data for {crop_norm}",
    }), 200
