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
