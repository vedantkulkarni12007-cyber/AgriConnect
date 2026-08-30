# app.py
# ─────────────────────────────────────────────────────────────────────────────
# KrishiLink Flask Application Factory
#
# This is the entry point for the backend server.
# It creates and configures the Flask application, registers all blueprints
# (groups of routes), and sets up CORS (cross-origin resource sharing)
# so the React frontend can talk to this API.
#
# HOW TO RUN:
#   python app.py                  (development – with auto-reload)
#   gunicorn app:app --bind 0.0.0.0:5000  (production)
# ─────────────────────────────────────────────────────────────────────────────

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config

# Import all blueprints (each file in routes/ is one blueprint)
from routes.health       import health_bp
from routes.prices       import prices_bp
from routes.trends       import trends_bp
from routes.lots         import lots_bp
from routes.matching     import matching_bp
from routes.offers       import offers_bp
from routes.transactions import transactions_bp
from routes.grievances   import grievances_bp


def create_app() -> Flask:
    """
    Application factory function.

    Using a factory pattern (instead of a global `app` object) makes the
    app easier to test and allows multiple configurations to coexist.

    Returns
    -------
    A configured Flask application instance.
    """
    app = Flask(__name__)

    # ── CORS Configuration ────────────────────────────────────────────────────
    # CORS (Cross-Origin Resource Sharing) allows the frontend running on
    # http://localhost:5173 (Vite default) to call this API on port 5000.
    # Without this, browsers block the requests for security reasons.
    CORS(
        app,
        origins=[Config.FRONTEND_URL, "http://localhost:3000"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
        supports_credentials=True,
    )

    # ── Blueprint Registration ─────────────────────────────────────────────────
    # Each blueprint handles a specific feature area of the API.
    # We register them all here so the main app knows about every route.
    blueprints = [
        health_bp,        # GET  /api/health
        prices_bp,        # GET  /api/prices
        trends_bp,        # GET  /api/trends
        lots_bp,          # GET  /api/lots,       POST /api/lots
        matching_bp,      # GET  /api/match,       POST /api/match
        offers_bp,        # GET  /api/offers,     POST /api/offers,  PUT /api/offers/<id>
        transactions_bp,  # GET  /api/transactions, GET /api/transactions/<id>
        grievances_bp,    # GET  /api/grievances, POST /api/grievances
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    # ── Consistent JSON Error Handlers ────────────────────────────────────────
    # These functions override Flask's default HTML error pages.
    # Instead, they return JSON so the frontend always gets a consistent format:
    # { "success": false, "data": null, "message": "..." }

    @app.errorhandler(400)
    def bad_request(error):
        """400 Bad Request – the client sent a malformed request."""
        return jsonify({
            "success": False,
            "data":    None,
            "message": "Bad request. Please check your input.",
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        """404 Not Found – the requested URL or resource doesn't exist."""
        return jsonify({
            "success": False,
            "data":    None,
            "message": "The requested resource was not found.",
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """405 Method Not Allowed – wrong HTTP verb for this endpoint."""
        return jsonify({
            "success": False,
            "data":    None,
            "message": "HTTP method not allowed for this endpoint.",
        }), 405

    @app.errorhandler(500)
    def internal_server_error(error):
        """500 Internal Server Error – something unexpected went wrong."""
        return jsonify({
            "success": False,
            "data":    None,
            "message": "An internal server error occurred. Please try again later.",
        }), 500

    # ── Startup banner ────────────────────────────────────────────────────────
    mode = "DEMO" if Config.DEMO_MODE else "LIVE"
    print(f"\n{'='*55}")
    print(f"  {Config.APP_NAME} v{Config.APP_VERSION}")
    print(f"  Mode      : {mode}")
    print(f"  Debug     : {Config.FLASK_DEBUG}")
    print(f"  CORS from : {Config.FRONTEND_URL}")
    print(f"{'='*55}\n")

    return app


# ── Create the app instance used by Flask / Gunicorn ─────────────────────────
# `app` is referenced by gunicorn as `app:app`
app = create_app()


# ── Development server entry point ────────────────────────────────────────────
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",           # accept connections from any network interface
        port=Config.FLASK_PORT,   # default 5000
        debug=Config.FLASK_DEBUG, # auto-reload on code changes
    )
