# routes/health.py
# ─────────────────────────────────────────────────────────────────────────────
# A simple "health check" endpoint that lets the frontend (or DevOps tools)
# verify the API is alive and know what mode it's running in.
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime, timezone
from flask import Blueprint
from config import Config

# A Blueprint is Flask's way of grouping related routes.
# We create one Blueprint per feature area and register them all in app.py.
health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """
    GET /api/health

    Returns the API status, operating mode, current timestamp and version.

    Response example:
    {
      "success": true,
      "data": {
        "status": "ok",
        "mode": "demo",
        "timestamp": "2026-08-28T00:00:00Z",
        "version": "1.0.0"
      },
      "message": "KrishiLink API is running"
    }
    """
    from flask import jsonify

    mode = "demo" if Config.DEMO_MODE else "live"

    return jsonify({
        "success": True,
        "data": {
            "status":    "ok",
            "mode":      mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version":   Config.APP_VERSION,
        },
        "message": f"{Config.APP_NAME} is running in {mode.upper()} mode",
    }), 200
