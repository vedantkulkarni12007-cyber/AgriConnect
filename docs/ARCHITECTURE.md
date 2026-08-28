# KrishiLink Architecture 2.0

**Version:** 2.0.0  
**Status:** Decision Gate — Approved for Phase 2+  
**Stack:** Next.js 15 + FastAPI + PostgreSQL/PostGIS + Redis + S3

---

## 1. System Overview

```
FARMER / FPO / BUYER / ADMIN
            │
      Next.js 15 / PWA (TS, Tailwind, shadcn/ui, TanStack Query, next-intl)
            │  Typed API Client (generated from OpenAPI)
      FastAPI — /api/v1/*  (Pydantic v2, OpenAPI)
            │
   ┌────────┼────────┬──────────┐
   │        │        │          │
 Domain  RuleEng  Workflows  Observability
 Services Engines  (FSM)     (OTel, Prometheus)
   │        │        │
   └────────┼────────┘
            │
     PostgreSQL 15 + PostGIS 3.4
            ├── business data
            ├── audit_logs
            ├── provenance (price_sources, data_provenance, ingestion_runs)
            ├── outbox_events (transactional outbox)
            └── PostGIS GEOGRAPHY(Point,4326)
            │
     Redis (cache, idempotency, Celery broker)
     S3-compatible (evidence, QR)
     Celery Worker (notifications, ingestion, reservations expiry)
```

---

## 2. Backend Layering

```
Router (FastAPI) → Pydantic Validation → Auth/RBAC Dependency → Application Service → Domain Service → Repository → SQLAlchemy → PostgreSQL
                                                  │
                                          Audit + Outbox (same DB txn)
```

**Rule:** Routes are thin (<30 lines). Business logic in Services. No business logic in Repositories.

**Example:** `POST /api/v1/offers/{id}/accept` → `OfferService.accept_offer()` → checks state, quantity locks (`SELECT ... FOR UPDATE`), creates `Reservation`, writes `AuditLog`, writes `OutboxEvent`, `COMMIT`.

---

## 3. Domain Modules

Each under `backend/app/modules/<name>/` with `models.py schemas.py repository.py service.py router.py tests/`

`auth users farmers fpos buyers crops markets prices price_intelligence lots matching offers negotiations reservations transactions payments logistics storage notifications disputes evidence traceability reports admin audit provenance health`

Shared: `backend/app/core/` (config, security, db, errors, pagination, idempotency, observability) + `backend/app/workers/`.

---

## 4. Database Principles

- PostgreSQL authoritative, PostGIS for geo (`GEOGRAPHY(Point,4326)` + GiST)
- `ST_DWithin` for nearby buyers/markets/storage — never adjacency dict
- FKs, UNIQUE, CHECK, indexes, composite indexes, `created_at/updated_at`, soft-delete where appropriate
- Alembic only for schema changes
- Encrypted fields for sensitive data (if collected) + audit access
- Outbox pattern for async side-effects

---

## 5. Auth & RBAC

- Argon2id password hash, JWT access (15m) + refresh (7d, rotation, revocation list in Redis)
- Roles: FARMER, FPO, BUYER, ADMIN, OPERATOR — enforced via `Depends(require_role(...))` on every protected route. Frontend hiding ≠ auth.
- OTP architecture placeholder, not active.

---

## 6. API Contract

- Base: `/api/v1/`
- Envelope: `{ success: bool, data: T|null, message: str, request_id: str, code?: str, details?: any }`
- Errors: `code`, `message`, `details`, `request_id`
- Idempotency-Key header for `POST /lots`, `POST /offers/{id}/accept`, `POST /transactions`, etc.
- OpenAPI from FastAPI is source of truth; TS types generated via `openapi-typescript`.

---

## 7. Price Intelligence & Provenance

Every `price_observation` stores `source`, `source_record_id`, `source_url`, `published_at`, `retrieved_at`, `ingestion_run_id`, `parser_version`, `raw_payload_hash`, `quality_status`. Derived metrics store `inputs`, `calculation`, `rule_version`, `generated_at`. User can answer "Where did this number come from?" (§18).

---

## 8. Matching Engine

Versioned `MatchRuleSet` stored in `system_configurations`/`match_rulesets`. Default weights §26: crop 30, grade 15, quantity 15, distance 15, price 10, time 5, verification 10 =100. Each match stores `ruleset_id`, `ruleset_version`, component scores, final_score, explanation. PostGIS for distance.

---

## 9. Transactions

State machine §34: `CREATED → PAYMENT_PENDING → PAYMENT_CONFIRMED → PROCESSING → READY_FOR_DISPATCH → IN_TRANSIT → DELIVERED → COMPLETED` (+ DISPUTED/CANCELLED/REFUNDED). Invalid transitions rejected (check constraint + service guard). Lot splitting via `lot_allocations` with `allocated_quantity` checked in DB txn, `SELECT ... FOR UPDATE` on lots.

---

## 10. Frontend

- Next.js App Router, feature-based `src/features/*`
- Routes per §44 (public `/`, `/prices`, farmer `/farmer/*`, buyer `/buyer/*`, fpo `/fpo/*`, admin `/admin/*`, public `/lot/[publicId]`)
- Design system per §46, farmer-first UX §47, professional mode §48, i18n next-intl §49, PWA §50, map §51, share §52
- Quality: ESLint, Prettier, TS strict

---

## 11. Observability & Security

- Structured JSON logs + `X-Request-ID`, OpenTelemetry traces, Prometheus metrics, Sentry
- Security: secure headers, CORS, rate limiting (Redis), Zod/Pydantic validation, RBAC, audit_logs per §59, feature flags per §60

---

## 12. Deployment

Docker Compose for local (frontend, backend, postgres+postgis, redis, worker, nginx). GitHub Actions CI per §70. Environment config validated at startup via Pydantic Settings, never commit secrets.

---

## 13. Non-Goals for MVP

Blockchain, AI price prediction as authoritative (deterministic only, §76), real payment gateway (MockPaymentProvider with adapter), WhatsApp live (share card only unless configured).

---

*Companion docs: `ADR/`, `API_CONTRACT.md`, `DATA_MODEL.md`, `SECURITY.md`, `TESTING_STRATEGY.md`, `DEPLOYMENT.md`, `OBSERVABILITY.md`, `DATA_PROVENANCE.md`*
