# routes/offers.py
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints for managing buyer offers on farmer lots.
# An offer is a buyer's bid to purchase a lot at a specified price/quantity.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from data.demo_data import OFFERS, LOTS, TRANSACTIONS

offers_bp = Blueprint("offers", __name__)

# Valid offer statuses that can be set via PUT
VALID_STATUSES = {"pending", "accepted", "rejected", "expired"}


@offers_bp.route("/api/offers", methods=["GET"])
def list_offers():
    """
    GET /api/offers?farmer_id=F001&buyer_id=B002&status=pending

    Returns a list of offers filtered by optional query parameters.

    Query parameters:
      farmer_id (optional) – show offers for this farmer's lots
      buyer_id  (optional) – show offers made by this buyer
      status    (optional) – filter by offer status

    Response example:
    {
      "success": true,
      "data": [
        {
          "id": "O001",
          "lot_id": "L001",
          "buyer_id": "B002",
          "price": 1280,
          "quantity": 80,
          "status": "pending",
          ...
        }
      ],
      "message": "2 offer(s) found"
    }
    """
    farmer_id     = request.args.get("farmer_id", None)
    buyer_id      = request.args.get("buyer_id",  None)
    status_filter = request.args.get("status",    None)

    results = OFFERS

    if farmer_id:
        results = [o for o in results if o.get("farmer_id") == farmer_id]

    if buyer_id:
        results = [o for o in results if o.get("buyer_id") == buyer_id]

    if status_filter:
        results = [o for o in results if o.get("status") == status_filter]

    return jsonify({
        "success": True,
        "data":    results,
        "message": f"{len(results)} offer(s) found",
    }), 200


@offers_bp.route("/api/offers", methods=["POST"])
def create_offer():
    """
    POST /api/offers

    Creates a new offer from a buyer on a specific lot.

    Request body (JSON):
    {
      "lot_id":   "L001",
      "buyer_id": "B002",
      "price":    1280,
      "quantity": 80,
      "message":  "Interested in export quality onion"
    }

    All four fields (lot_id, buyer_id, price, quantity) are required.

    Response:
    {
      "success": true,
      "data": { <new offer object> },
      "message": "Offer created successfully"
    }
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must be valid JSON",
        }), 400

    # Validate required fields
    required = ["lot_id", "buyer_id", "price", "quantity"]
    missing  = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Missing required fields: {', '.join(missing)}",
        }), 400

    lot_id   = body["lot_id"]
    buyer_id = body["buyer_id"]

    # Verify the lot exists and is still open for offers
    lot = next((l for l in LOTS if l["id"] == lot_id), None)
    if not lot:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Lot '{lot_id}' not found",
        }), 404

    if lot.get("status") not in ("active", "matched"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Lot '{lot_id}' is not open for offers (status: {lot.get('status')})",
        }), 400

    # Build the new offer
    next_id   = f"O{len(OFFERS) + 1:03d}"
    today     = date.today()
    new_offer = {
        "id":         next_id,
        "lot_id":     lot_id,
        "buyer_id":   buyer_id,
        "farmer_id":  lot.get("farmer_id", "unknown"),
        "price":      float(body["price"]),
        "quantity":   float(body["quantity"]),
        "status":     "pending",
        "message":    body.get("message", ""),
        "created_at": today.isoformat(),
        "expires_at": (today + timedelta(days=7)).isoformat(),
    }

    OFFERS.append(new_offer)

    return jsonify({
        "success": True,
        "data":    new_offer,
        "message": "Offer created successfully",
    }), 201


@offers_bp.route("/api/offers/<string:offer_id>", methods=["PUT"])
def update_offer_status(offer_id: str):
    """
    PUT /api/offers/<offer_id>

    Update the status of an existing offer.
    Typically used by the farmer to accept or reject a buyer's offer.

    Path parameter:
      offer_id – e.g. 'O001'

    Request body (JSON):
    {
      "status": "accepted"   or   "rejected"
    }

    When an offer is accepted:
    - A new TRANSACTION record is automatically created.
    - The lot status is updated to 'matched'.

    Response:
    {
      "success": true,
      "data": { <updated offer> },
      "message": "Offer O001 updated to accepted"
    }
    """
    body = request.get_json(silent=True)

    if not body or not body.get("status"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must include 'status' field",
        }), 400

    new_status = body["status"].lower()
    if new_status not in VALID_STATUSES:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Invalid status '{new_status}'. Must be one of: {', '.join(VALID_STATUSES)}",
        }), 400

    # Find the offer
    offer = next((o for o in OFFERS if o["id"] == offer_id), None)
    if not offer:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Offer '{offer_id}' not found",
        }), 404

    # Don't allow changing a finalized offer
    if offer["status"] in ("accepted", "rejected"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Offer '{offer_id}' is already {offer['status']} and cannot be changed",
        }), 400

    # Update the offer status
    offer["status"] = new_status

    # If accepted: create a transaction and update the lot status
    if new_status == "accepted":
        # Mark the lot as matched
        for lot in LOTS:
            if lot["id"] == offer["lot_id"]:
                lot["status"] = "matched"
                break

        # Create a new transaction record
        next_txn_id = f"T{len(TRANSACTIONS) + 1:03d}"
        lot = next((l for l in LOTS if l["id"] == offer["lot_id"]), {})

        new_txn = {
            "id":                next_txn_id,
            "offer_id":          offer_id,
            "lot_id":            offer["lot_id"],
            "farmer_id":         offer["farmer_id"],
            "buyer_id":          offer["buyer_id"],
            "crop":              lot.get("crop", ""),
            "quantity":          offer["quantity"],
            "price_per_quintal": offer["price"],
            # Total: price per quintal × quantity in tonnes × 10 quintals/tonne
            "total_amount":      offer["price"] * offer["quantity"] * 10,
            "current_stage":     "offer_accepted",
            "stage_history": [
                {"stage": "offer_created",  "timestamp": offer["created_at"]},
                {"stage": "offer_accepted", "timestamp": date.today().isoformat()},
            ],
            "created_at": date.today().isoformat(),
        }

        TRANSACTIONS.append(new_txn)

    return jsonify({
        "success": True,
        "data":    offer,
        "message": f"Offer {offer_id} updated to '{new_status}'",
    }), 200
