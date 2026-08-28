# routes/grievances.py
# ─────────────────────────────────────────────────────────────────────────────
# Endpoints for raising and viewing farmer grievances / complaints.
# A grievance can be linked to a transaction or raised independently.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import date
from flask import Blueprint, request, jsonify
from data.demo_data import GRIEVANCES

grievances_bp = Blueprint("grievances", __name__)

# Supported issue types for classification and routing
# Keep in sync with GrievancesPage.jsx ISSUE_TYPES array
VALID_ISSUE_TYPES = [
    "Price Dispute",
    "Quality Dispute",
    "Payment Delay",
    "Delivery Issue",
    "Fraud",
    "Logistics Issue",
    "Contract Violation",
    "Other",
]


@grievances_bp.route("/api/grievances", methods=["GET"])
def list_grievances():
    """
    GET /api/grievances?farmer_id=F001

    Returns a list of grievances, optionally filtered by farmer.

    Query parameters:
      farmer_id (optional) – show only grievances for this farmer
      status    (optional) – filter by: open / under_review / resolved

    Response example:
    {
      "success": true,
      "data": [
        {
          "id": "G001",
          "farmer_id": "F003",
          "issue_type": "Price Dispute",
          "status": "open",
          "description": "...",
          ...
        }
      ],
      "message": "1 grievance(s) found"
    }
    """
    farmer_id     = request.args.get("farmer_id", None)
    status_filter = request.args.get("status",    None)

    results = GRIEVANCES

    if farmer_id:
        results = [g for g in results if g.get("farmer_id") == farmer_id]

    if status_filter:
        results = [g for g in results if g.get("status") == status_filter]

    return jsonify({
        "success": True,
        "data":    results,
        "message": f"{len(results)} grievance(s) found",
    }), 200


@grievances_bp.route("/api/grievances", methods=["POST"])
def create_grievance():
    """
    POST /api/grievances

    Raises a new grievance on behalf of a farmer.

    Request body (JSON):
    {
      "farmer_id":      "F003",
      "transaction_id": "T001",          (optional – null if not transaction-related)
      "issue_type":     "Payment Delay",
      "description":    "Payment not received within 7 days of dispatch."
    }

    Required fields: farmer_id, issue_type, description

    Response:
    {
      "success": true,
      "data": { <new grievance object> },
      "message": "Grievance raised successfully. Our team will review within 48 hours."
    }
    """
    body = request.get_json(silent=True)

    if not body:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Request body must be valid JSON",
        }), 400

    # Validate required fields — farmer_id is optional (demo mode has no real auth)
    required = ["issue_type", "description"]
    missing  = [f for f in required if not body.get(f)]
    if missing:
        return jsonify({
            "success": False,
            "data":    None,
            "message": f"Missing required fields: {', '.join(missing)}",
        }), 400

    # Validate issue type
    issue_type = body["issue_type"].strip()
    if issue_type not in VALID_ISSUE_TYPES:
        return jsonify({
            "success": False,
            "data":    None,
            "message": (
                f"Invalid issue_type '{issue_type}'. "
                f"Valid options: {', '.join(VALID_ISSUE_TYPES)}"
            ),
        }), 400

    # Description must be meaningful (at least 10 characters)
    description = body["description"].strip()
    if len(description) < 10:
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Description must be at least 20 characters long",
        }), 400

    # Build the new grievance
    next_id      = f"G{len(GRIEVANCES) + 1:03d}"
    new_grievance = {
        "id":               next_id,
        "farmer_id":        body.get("farmer_id", "demo"),
        "transaction_id":   body.get("transaction_id", None),
        "issue_type":       issue_type,
        "description":      description,
        "status":           "open",       # all new grievances start as 'open'
        "created_at":       date.today().isoformat(),
        "resolved_at":      None,
        "resolution_note":  None,
    }

    GRIEVANCES.append(new_grievance)

    return jsonify({
        "success": True,
        "data":    new_grievance,
        "message": "Grievance raised successfully. Our team will review within 48 hours.",
    }), 201
