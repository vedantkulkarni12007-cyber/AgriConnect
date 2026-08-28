# routes/matching.py
# ─────────────────────────────────────────────────────────────────────────────
# Buyer matching endpoints.
# Accepts lot details and returns a scored, ranked list of matching buyers.
# ─────────────────────────────────────────────────────────────────────────────

from flask import Blueprint, request, jsonify
from services.matching_service import match_buyers
from data.demo_data import LOTS

matching_bp = Blueprint("matching", __name__)


@matching_bp.route("/api/match", methods=["POST"])
def match_from_lot_details():
    """
    POST /api/match

    Accepts lot details in the request body and returns a ranked list
    of matching buyers with scores and reasons.

    Request body (JSON):
    {
      "crop":     "Onion",
      "quantity": 80,
      "grade":    "A",
      "location": "Lasalgaon",
      "district": "Nashik",
      "state":    "Maharashtra"
    }

    Response:
    {
      "success": true,
      "data": [
        {
          "buyer": { "id": "B002", "name": "Sahyadri Farms Export", ... },
          "score": 85,
          "match_label": "Excellent",
          "match_reasons": ["Buyer purchases Onion", "Grade A matches preference", ...]
        },
        ...
      ],
      "message": "3 matching buyer(s) found"
    }
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must be valid JSON with lot details",
        }), 400

    # Minimum required: crop (without it, matching makes no sense)
    if not body.get("crop"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Field 'crop' is required to find matching buyers",
        }), 400

    matches = match_buyers(body)

    return jsonify({
        "success": True,
        "data":    matches,
        "message": f"{len(matches)} matching buyer(s) found",
    }), 200


@matching_bp.route("/api/match", methods=["GET"])
def match_from_lot_id():
    """
    GET /api/match?lot_id=L001

    Looks up an existing lot by ID and returns matching buyers for it.

    Query parameters:
      lot_id (required) – e.g. 'L001'

    Response: same structure as POST /api/match
    """
    lot_id = request.args.get("lot_id", None)

    if not lot_id:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Query parameter 'lot_id' is required",
        }), 400

    # Find the lot in demo data
    lot = next((l for l in LOTS if l["id"] == lot_id), None)

    if not lot:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Lot '{lot_id}' not found",
        }), 404

    matches = match_buyers(lot)

    return jsonify({
        "success": True,
        "data":    matches,
        "message": f"{len(matches)} matching buyer(s) found for lot {lot_id}",
    }), 200
