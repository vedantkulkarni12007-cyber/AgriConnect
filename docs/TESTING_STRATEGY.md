# KrishiLink Testing Strategy (§65-69)

## Pyramid

**Unit (70%)** — services, calculators, validators, state machines, matching, price intelligence
- `pytest` + `pytest-asyncio` for `calculate_trend` (RISING/STABLE/FALLING), `calculate_*_score`, `idempotency`, `net_realization`, FSM transitions (valid/invalid)
- Frontend `vitest` + `React Testing Library` for components, Zod validation, translations

**Integration (20%)** — DB, repositories, API, auth, RBAC
- Testcontainers Postgres+PostGIS + Redis; Alembic upgrade/downgrade on fresh DB
- `httpx.AsyncClient` against FastAPI `app` with JWT fixtures for FARMER/BUYER/ADMIN; assert 200/201/400/401/403/404/409/422

**E2E (10%)** — `Playwright` against Docker Compose
- Flows: register → login → farmer sell 1000kg wheat → match → buyer offer 400kg → counter → accept → reservation → transaction → payment (mock) → delivery + evidence → remaining qty → QR → audit → admin inspect
- Visual regression snapshots (mobile/tablet/desktop) for PriceCard, MatchCard

## Postman (§17,66)

`docs/postman/KrishiLink.postman_collection.json` + envs `local/staging/production` with variables `base_url, access_token, refresh_token, user_id, lot_id, offer_id, transaction_id`. Automated assertions per request, covers 200/201/400/401/403/404/409/422, duplicate Idempotency-Key, invalid transitions, RBAC.

## Contract Testing (§67)

- `schemathesis` / `openapi-spec-validator` against `/api/v1/openapi.json`
- Generated TS client drift check in CI (fail if OpenAPI hash changes but frontend types not regenerated)

## Quality Gates (§70)

Every PR: `ruff check + ruff format --check + mypy --strict + eslint + prettier --check + tsc --noEmit + pytest + vitest + build + gitleaks + trivy + semgrep`
Main: adds Playwright E2E + Docker build + `alembic upgrade head && downgrade base && upgrade head`

## Accessibility (§69)

- `axe-core` via Playwright, WCAG 2.2 AA: keyboard nav, focus, labels, ARIA, contrast, screen reader, form errors — run in CI with `npx playwright test --project=a11y`.

## Performance (§57)

- `pytest-benchmark` for matching (<800ms p95), k6 for API p95 targets; indexes + pagination required; never sacrifice correctness.

## Coverage Target

- Backend services ≥85% line, integration critical paths 100% (auth, FSM, quantity locks), E2E at least one happy + 5 failure paths (§86).
