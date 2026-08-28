# routes/trends.py
# ─────────────────────────────────────────────────────────────────────────────
# Trend analysis endpoints.
# Returns whether a crop price is RISING, FALLING, or STABLE.
# ─────────────────────────────────────────────────────────────────────────────

from flask import Blueprint, request, jsonify
from services.trend_service import get_trend_for_crop
from data.demo_data import CROPS

trends_bp = Blueprint("trends", __name__)


@trends_bp.route("/api/trends/<string:crop>", methods=["GET"])
def trend_for_crop(crop: str):
    """
    GET /api/trends/<crop>?market=Nashik

    Returns trend analysis for a specific crop.
    Optionally scoped to a specific market via query param.

    Path parameter:
      crop – e.g. 'Onion', 'Wheat'

    Query parameters:
      market (optional) – e.g. 'Nashik'. If omitted, averages all markets.

    Response example:
    {
      "success": true,
      "data": {
        "crop": "Onion",
        "market": "Nashik",
        "current_price": 1200,
        "moving_average": 1311.43,
        "percentage_change": -8.49,
        "trend": "FALLING",
        "explanation": "Price is ₹1200/quintal, which is 8.5% below..."
      },
      "message": "Trend analysis for Onion"
    }
    """
    crop_norm = crop.strip().title()
    market    = request.args.get("market", None)

    result = get_trend_for_crop(crop_norm, market=market)

    if "error" in result:
        return jsonify({
            "success": False,
            "data":    None,
            "message": result["error"],
        }), 404

    return jsonify({
        "success": True,
        "data":    result,
        "message": f"Trend analysis for {crop_norm}",
    }), 200


@trends_bp.route("/api/trends", methods=["GET"])
def all_trends():
    """
    GET /api/trends

    Returns trend analysis for ALL crops (averaged across all markets).
    Useful for a dashboard overview card.

    Response example:
    {
      "success": true,
      "data": [
        { "crop": "Onion",  "trend": "RISING",  ... },
        { "crop": "Tomato", "trend": "STABLE",  ... },
        ...
      ],
      "message": "Trend data for 8 crops"
    }
    """
    trends = []

    for crop in CROPS:
        result = get_trend_for_crop(crop)
        # Only include successful results (skip any errors silently)
        if "error" not in result:
            trends.append(result)

    return jsonify({
        "success": True,
        "data":    trends,
        "message": f"Trend data for {len(trends)} crops",
    }), 200
