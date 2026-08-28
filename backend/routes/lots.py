# routes/lots.py
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints for managing produce lots.
# A "lot" is a batch of produce a farmer wants to sell.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import date
from flask import Blueprint, request, jsonify
from data.demo_data import LOTS

lots_bp = Blueprint("lots", __name__)

# Fields that MUST be present when creating a new lot
REQUIRED_LOT_FIELDS = [
    "crop",
    "quantity",
    "unit",
    "grade",
    "location",
    "expected_price",
]


@lots_bp.route("/api/lots", methods=["GET"])
def list_lots():
    """
    GET /api/lots?farmer_id=F001&status=active

    Returns a list of produce lots.

    Query parameters:
      farmer_id (optional) – filter to lots belonging to this farmer
      status    (optional) – filter by status: active / matched / sold / cancelled

    Response example:
    {
      "success": true,
      "data": [
        {
          "id": "L001",
          "farmer_id": "F001",
          "crop": "Onion",
          "quantity": 80,
          "grade": "A",
          ...
        }
      ],
      "message": "3 lot(s) found"
    }
    """
    farmer_id     = request.args.get("farmer_id", None)
    status_filter = request.args.get("status",    None)

    results = LOTS

    if farmer_id:
        results = [lot for lot in results if lot.get("farmer_id") == farmer_id]

    if status_filter:
        results = [lot for lot in results if lot.get("status") == status_filter]

    return jsonify({
        "success": True,
        "data":    results,
        "message": f"{len(results)} lot(s) found",
    }), 200


@lots_bp.route("/api/lots", methods=["POST"])
def create_lot():
    """
    POST /api/lots

    Creates a new produce lot listing.

    Request body (JSON):
    {
      "farmer_id":      "F001",
      "crop":           "Onion",
      "quantity":       80,
      "unit":           "tonnes",
      "grade":          "A",
      "location":       "Lasalgaon",
      "district":       "Nashik",
      "state":          "Maharashtra",
      "expected_price": 1300,
      "description":    "..."
    }

    Required fields: crop, quantity, unit, grade, location, expected_price

    Response:
    {
      "success": true,
      "data": { <new lot object> },
      "message": "Lot created successfully"
    }
    """
    body = request.get_json(silent=True)

    # Ensure request has a JSON body
    if not body:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must be valid JSON",
        }), 400

    # Validate required fields
    missing = [f for f in REQUIRED_LOT_FIELDS if not body.get(f)]
    if missing:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Missing required fields: {', '.join(missing)}",
        }), 400

    # Validate quantity is a positive number
    try:
        qty = float(body["quantity"])
        if qty <= 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Field 'quantity' must be a positive number",
        }), 400

    # Validate grade is one of A, B, C
    if body.get("grade", "").upper() not in ("A", "B", "C"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Field 'grade' must be one of: A, B, C",
        }), 400

    # Generate a new lot ID (simple increment for demo mode)
    next_id = f"L{len(LOTS) + 1:03d}"

    new_lot = {
        "id":             next_id,
        "farmer_id":      body.get("farmer_id", "unknown"),
        "crop":           body["crop"].strip().title(),
        "quantity":       qty,
        "unit":           body.get("unit", "tonnes"),
        "grade":          body["grade"].upper(),
        "location":       body.get("location", ""),
        "district":       body.get("district", body.get("location", "")),
        "state":          body.get("state", "Maharashtra"),
        "expected_price": float(body.get("expected_price", 0)),
        "status":         "active",   # all new lots start as active
        "description":    body.get("description", ""),
        "images":         [],
        "created_at":     date.today().isoformat(),
    }

    # Append to the in-memory demo list (persists for the session)
    LOTS.append(new_lot)

    return jsonify({
        "success": True,
        "data":    new_lot,
        "message": "Lot created successfully",
    }), 201
