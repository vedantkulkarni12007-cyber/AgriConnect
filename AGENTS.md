# AGENTS — KrishiLink 2.0

## Commands
- `docker compose up --build` — full stack (postgres:5435, redis:6380, backend:8001, frontend:5173 legacy Flask:5000)
- `alembic upgrade head` — run migrations (from backend/)
- `uvicorn app.main:app --reload --port 8000` — FastAPI dev (from backend/)
- `python flask_app_legacy.py` — Flask demo (legacy, 5000)
- `npm run dev -- --host 0.0.0.0 --port 5173` — Vite frontend
- Test: `pytest`, `npm run lint`, `npm run build`

## Architecture
- FastAPI `app.main` + `app/core/{config,database,security,errors}` + `app/modules/<domain>/{models,schemas,repository,service,router}`
- PostgreSQL+PostGIS (GEOGRAPHY), Redis+Celery, S3 adapter, JWT Argon2, RBAC
- API `/api/v1/*` envelope `{success,data,message,request_id}`, OpenAPI at `/api/v1/openapi.json`

## Rules
- No business logic in routes; use Service → Repository → DB
- Pydantic v2 + Zod validation, no silent failures, audit every mutation, outbox for async
- PostGIS ST_DWithin for geo, never adjacency dict
- Never bypass backend with frontend demoData — seed DB instead
- Alembic only for schema, never manual DDL
- Never push to `main`; use `feature/*` branches + PR; `main` is protected
- After every push: `git ls-remote`, `gh run list --limit 3`, `gh run view <id> --log-failed`; wait for green before notifying

## Post-Push Checklist (mandatory after `git push`)
1. `git -C <repo> ls-remote origin <branch>` — verify correct SHA on remote
2. `gh --repo <org>/<repo> run list --limit 3` — confirm workflow triggered on correct branch
3. `gh run view <id>` — wait for `✓` both jobs; if `✗`, `gh run view <id> --log-failed` and fix on same feature branch (never on main)
4. Refresh GitHub `…/commits/<branch>` with Ctrl+Shift+R — ensure no stale red commits visible
5. If red commits remain as history, squash via `git reset --soft <base> && git commit` + `push --force` on feature branch only

## Lessons Learned (2026-08-28)
- CI `alembic -c backend/alembic.ini` + `working-directory: backend` → double prefix → `No config file`; fix: `alembic -c alembic.ini` + `pytest -q`
- CI `on: push: branches: [main]` hid feature branch runs; fix: `branches: [main, "feature/**"]`
- PostGIS GiST indexes duplicated (`idx_*` + `ix_*` on same GEOGRAPHY) → `relation already exists`; fix: deduplicate + `CREATE INDEX IF NOT EXISTS` via `op.execute`
- Autogenerate drops tiger/postgis internal tables and `audit_logs`/`outbox_events` if Base misses them; fix: add SystemConfiguration/AuditLog/OutboxEvent to `app.models` + filter or clean migration
- Force-pushing to main hides history but leaves stale browser cache; always hard refresh and verify via `ls-remote`
