# routes/transactions.py
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints for viewing and updating transaction records.
# Transactions represent confirmed deals moving through a pipeline of stages.
# ─────────────────────────────────────────────────────────────────────────────

from flask import Blueprint, request, jsonify
from services.transaction_service import (
    get_transactions,
    get_transaction_by_id,
    update_transaction_stage,
)

transactions_bp = Blueprint("transactions", __name__)


@transactions_bp.route("/api/transactions", methods=["GET"])
def list_transactions():
    """
    GET /api/transactions?farmer_id=F001&buyer_id=B002

    Returns a list of transactions, optionally filtered by farmer or buyer.

    Query parameters:
      farmer_id (optional) – e.g. 'F001'
      buyer_id  (optional) – e.g. 'B002'

    Response example:
    {
      "success": true,
      "data": [
        {
          "id": "T001",
          "crop": "Cotton",
          "quantity": 200,
          "current_stage": "produce_dispatched",
          ...
        }
      ],
      "message": "2 transaction(s) found"
    }
    """
    farmer_id = request.args.get("farmer_id", None)
    buyer_id  = request.args.get("buyer_id",  None)

    txns = get_transactions(farmer_id=farmer_id, buyer_id=buyer_id)

    return jsonify({
        "success": True,
        "data":    txns,
        "message": f"{len(txns)} transaction(s) found",
    }), 200


@transactions_bp.route("/api/transactions/<string:txn_id>", methods=["GET"])
def get_single_transaction(txn_id: str):
    """
    GET /api/transactions/<txn_id>

    Returns full details of a single transaction, including a complete
    stage-by-stage timeline (both completed and pending stages).

    Path parameter:
      txn_id – e.g. 'T001'

    Response example:
    {
      "success": true,
      "data": {
        "id": "T001",
        "crop": "Cotton",
        "current_stage": "produce_dispatched",
        "timeline": [
          { "stage": "offer_created",    "label": "Offer Created",    "completed": true,  "timestamp": "2026-08-24" },
          { "stage": "offer_accepted",   "label": "Offer Accepted",   "completed": true,  "timestamp": "2026-08-25" },
          { "stage": "produce_dispatched","label": "Produce Dispatched","completed": true, "timestamp": "2026-08-27" },
          { "stage": "payment_pending",  "label": "Payment Pending",  "completed": false, "timestamp": null },
          ...
        ]
      },
      "message": "Transaction T001 found"
    }
    """
    txn = get_transaction_by_id(txn_id)

    if txn is None:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Transaction '{txn_id}' not found",
        }), 404

    return jsonify({
        "success": True,
        "data":    txn,
        "message": f"Transaction {txn_id} found",
    }), 200


@transactions_bp.route("/api/transactions/<string:txn_id>/stage", methods=["PUT"])
def advance_stage(txn_id: str):
    """
    PUT /api/transactions/<txn_id>/stage

    Advance a transaction to the next stage in the pipeline.

    Request body (JSON):
    {
      "stage": "payment_pending"
    }

    The stage must be a valid stage name AND must come after the current stage.

    Response:
    {
      "success": true,
      "data": { <updated transaction> },
      "message": "Transaction T001 advanced to payment_pending"
    }
    """
    body = request.get_json(silent=True)

    if not body or not body.get("stage"):
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must include a 'stage' field",
        }), 400

    result = update_transaction_stage(txn_id, body["stage"])

    if "error" in result:
        return jsonify({
            "success": False,
            "data":    None,
            "message": result["error"],
        }), 400

    return jsonify({
        "success": True,
        "data":    result,
        "message": f"Transaction {txn_id} advanced to '{body['stage']}'",
    }), 200
