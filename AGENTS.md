# AGENTS — KrishiLink 2.0 (Master Engineering Reference)

> **CRITICAL REOPENING INSTRUCTIONS**:
> When continuing or resuming work on KrishiLink 2.0:
> 1. Read `PROGRESS_TRACKER.md` and `docs/PRODUCTION_ENGINEERING_SPEC.md` for complete historical and technical context.
> 2. **DO NOT REWRITE OR REDESIGN**: Preserve existing FastAPI backend in `backend/app/`, React/Vite frontend in `frontend/`, and PostgreSQL/PostGIS / SQLite models.
> 3. Ignore legacy Flask code (`backend/routes/`, `backend/services/`, `flask_app_legacy.py`).
> 4. Keep all 60 tests in `backend/tests/` passing at 100% (`python -m pytest -v`).
> 5. Always commit/push to `feature/production-rebuild-2.0` and verify green CI (`gh run list`).

## Commands
- `docker compose up --build` — full stack (postgres:5435, redis:6380, backend:8001, frontend:5173)
- `alembic upgrade head` — run migrations (from backend/)
- `python -m uvicorn app.main:app --reload --port 8000` — FastAPI dev (from backend/)
- `npm run dev -- --host 0.0.0.0 --port 5173` — Vite frontend
- Verification: `python -m pytest -v`, `python -m ruff check app`, `npm run lint`, `npm run build`

## Architecture & Conventions
- FastAPI `app.main` + `app/core/{config,database,security,errors,rate_limit,s3}` + `app/modules/<domain>/{models,schemas,service,router}`
- PostgreSQL+PostGIS (`GEOGRAPHY(POINT, 4326)`) with SQLite dual-compatibility for tests
- Redis sliding-window rate limiting with in-memory fallback
- API `/api/v1/*` envelope `{success,data,message,request_id}`, OpenAPI at `/api/v1/openapi.json`
- Event-driven persistent notifications + transactional outbox table

## Rules
- No business logic in routes; use Service → Repository → DB
- Pydantic v2 validation, no silent failures, audit every mutation
- Never bypass backend with frontend demoData on failed requests — return truthful error states
- Alembic only for schema changes, never manual DDL
- Never push to `main`; work exclusively on `feature/production-rebuild-2.0`
- After every push: follow the mandatory Post-Push Checklist

## Post-Push Checklist (Mandatory)
1. `git -C c:\vedant ls-remote origin feature/production-rebuild-2.0` — verify remote SHA
2. `gh --repo vedantkulkarni12007-cyber/KrishiLink run list --limit 3` — confirm workflow triggered
3. `gh --repo vedantkulkarni12007-cyber/KrishiLink run view <id>` — wait for `✓` on both jobs before notifying

## Current Status (2026-08-30)
- **Branch**: `feature/production-rebuild-2.0` (HEAD `6eb1d68`, CI 100% green)
- **Tests**: 68 passed (0 failed, 1 skipped) across unit, integration, earnings, and multi-role E2E journeys
- **Phases 0–10 Complete**: Auth, RBAC, Rate Limiting, PostGIS, Matching, Negotiations, Escrow FSM, S3 Evidence, Live Notifications, Customer Support Tickets, Farmer Earnings Endpoint, and CI/CD Automation.