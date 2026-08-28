# config.py
# ─────────────────────────────────────────────────────────────────────────────
# Central configuration for the KrishiLink backend.
# All environment variables are read here using python-dotenv so the rest
# of the app just imports `Config` and uses its attributes.
# ─────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

# Load the .env file from the same directory as this file.
# If .env doesn't exist the app falls back to environment variables or defaults.
load_dotenv()


class Config:
    """
    Application configuration loaded from environment variables.

    Usage:
        from config import Config
        print(Config.DEMO_MODE)   # True / False
    """

    # ── Flask settings ────────────────────────────────────────────────────────
    FLASK_ENV: str = os.getenv("FLASK_ENV", "development")
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", 5000))

    # ── Supabase (database) settings ──────────────────────────────────────────
    # These are left empty in the .env.example so the app starts in DEMO MODE
    # without needing a real database.
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")

    # ── CORS settings ─────────────────────────────────────────────────────────
    # Which frontend origin is allowed to call this API.
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ── Demo mode flag ────────────────────────────────────────────────────────
    # DEMO_MODE is automatically True when SUPABASE_URL is not configured.
    # In demo mode all routes return data from data/demo_data.py instead of
    # making real database calls.
    DEMO_MODE: bool = SUPABASE_URL == ""

    # ── App metadata ──────────────────────────────────────────────────────────
    APP_VERSION: str = "1.0.0"
    APP_NAME: str = "KrishiLink API"
