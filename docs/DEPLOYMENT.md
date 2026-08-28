# KrishiLink Deployment

## Local (Docker Compose) — §72

```yaml
services:
  postgres: image: postgis/postgis:15-3.4, healthcheck pg_isready, volume pgdata, ports 5432
  redis: image: redis:7-alpine, healthcheck
  backend: build: ./backend (python:3.13-slim, FastAPI+Uvicorn), depends_on postgres+redis healthy, env_file .env, alembic upgrade head on start, ports 8000
  worker: backend image, command: celery -A app.workers.celery worker -B, depends_on redis healthy
  frontend: build: ./frontend (node:20, Next.js), args VITE_API_BASE_URL, ports 3000
  nginx: proxy /api/v1 → backend, / → frontend, TLS optional
```

`docker compose up --build` → `http://localhost:3000` (frontend), `http://localhost:8000/docs` (OpenAPI), health at `/api/v1/health`.

## Env

See `backend/.env.example` + `frontend/.env.example`. Required: `DATABASE_URL, REDIS_URL, JWT_SECRET, S3_* , CORS_ORIGINS, PAYMENT_PROVIDER=mock`. Validated at startup (`pydantic-settings` raises if missing). Never commit secrets.

## CI/CD (§70)

GitHub Actions `ci.yml`: install → lint/format → typecheck → unit+integration → build → security scan (Trivy, gitleaks, Semgrep). `main` adds E2E + Docker push + `alembic check` + production build verification. Protected branch, required checks.

## Migrations (§71)

Alembic only. Never manual DDL on prod. Test in CI: `alembic upgrade head`, `downgrade base`, `upgrade head` on fresh DB.

## Prod Topology

Managed Postgres (PostGIS), managed Redis, object storage (S3), container runtime (Cloud Run / ECS / Fly), CDN for frontend static + evidence signed URLs. `LIVE_PRICE_INGESTION` flag off until source credentials provisioned.

## Demo Mode (§63-64)

Single toggle `DEMO_MODE` but **same APIs + DB**. Seeds `WHEAT-NASHIK-DEMO-001` deterministic snapshot (prices, farmer, lot, buyers, matches, offers, transaction) via `alembic seed`. Frontend never imports `demoData.js`; it queries `/api/v1/*`. Label demo badges clearly (§75).
