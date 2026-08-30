# KrishiLink Architecture Audit — Phase 0

**Date:** 2026-08-28  
**Auditor:** Principal Architect (AI)  
**Prototype Version:** 1.0.0 (Flask + Vite)  
**Target Version:** 2.0 Production-Grade

---

## 1. Executive Summary

Current prototype is a functional **Hackathon MVP** that demonstrates product concepts well but is architecturally unsuitable for production. It uses Flask with in-memory Python dicts, no persistent DB in runtime, no auth, no validation, demo-data bypass in frontend, and duplicated business logic. The target 2.0 requires full migration to FastAPI + PostgreSQL + PostGIS + Redis + Next.js while preserving all valuable product ideas.

**Verdict:** Reuse product concepts & UX flows; rewrite architecture, persistence, auth, and API contracts.

---

## 2. Current Architecture

```
Vite React (JS)  --->  Flask (Python dicts)  --->  demo_data.py
      |                        |
   demoData.js           Supabase schema.sql (unused at runtime)
      |
   localStorage "auth"
```

- **Frontend:** Vite 6 + React 19 + Tailwind 4 + React Router 7, JS (not TS), no Typed Client
- **Backend:** Flask 3.0 + flask-cors, Blueprint routes, services (price_service, matching_service, trend_service, transaction_service), config via python-dotenv, gunicorn entry but no Docker
- **Database:** `database/schema.sql` (Supabase/Postgres) — **not used at runtime**. Runtime uses `backend/data/demo_data.py` + frontend `src/data/demoData.js` as source of truth.
- **Auth:** `useAuth.jsx` — localStorage `krishilink_user` + `DEMO_USERS` dict, no password hashing, no JWT, no RBAC enforcement
- **Maps:** React-Leaflet + Leaflet (client only), no PostGIS
- **i18n:** `translations.js` object, 7 languages, not next-intl
- **Deployment:** none (no Dockerfile, no compose, no CI)

---

## 3. Inventory — What Exists

| Area | Files | Status |
|------|-------|--------|
| Landing / Auth UI | `LoginPage.jsx`, `RegisterPage.jsx`, `LandingPage.jsx` | Implemented (mock) |
| Farmer flows | `FarmerDashboard.jsx`, `SellPage.jsx`, `MatchesPage.jsx`, `OffersPage.jsx` | Implemented (mock) |
| Buyer flows | `BuyerDashboard.jsx` | Partial |
| FPO flows | `FPODashboard.jsx` | Skeleton |
| Prices | `PricesPage.jsx` + `/api/prices` + `price_service.py` | Implemented (demo) |
| Trends | `/api/trends/*` + `trend_service.py` (3% threshold) | Implemented (demo) |
| Lots | `/api/lots` GET/POST + `routes/lots.py` | Implemented (in-memory) |
| Matching | `/api/match` POST + `matching_service.py` (40/25/20/15 =100) | Implemented (demo, deterministic) |
| Offers | `/api/offers` GET/POST/PUT | Implemented (in-memory) |
| Transactions | `/api/transactions` GET + service | Implemented (in-memory) |
| Grievances | `/api/grievances` | Implemented (in-memory) |
| Health | `/api/health` | Implemented |
| Config | `config.py` (FLASK_ENV, DEMO_MODE) | Implemented |
| DB Schema | `schema.sql`, `seed.sql` | Designed but not wired |
| Docs | `BEGINNER_GUIDE.md`, `TEAM_GUIDE.md` | Exists |

---

## 4. Audit Findings

### A. Already Implemented (Preserve)
- Product concepts: price discovery, market comparison, trend badge (RISING/STABLE/FALLING), net realization idea, lot creation, buyer matching, offer accept/reject, transaction timeline, grievance filing, map view, multilingual keys
- UX patterns: Dashboard cards, PriceCard, MatchCard, OfferCard, map markers, demo mode banner
- Agricultural terminology: mandi/APMC, quintal, grade A/B/C, modal/min/max prices
- Demo scenarios: Maharashtra markets (Nashik, Lasalgaon, Pune etc.), 8 crops, 15-day histories

### B. Partially Implemented
- Auth: UI exists but no real registration/login, no persistent user
- Price intelligence: only 7-day MA + 3% threshold, missing 14/30-day, volatility, arrival context, anomaly detection, explanation provenance
- Matching: 4 factors only, missing price/time-window/verification, no versioned rules, no distance via PostGIS
- Transactions: simple status, no state machine, no reservations, no payments, no logistics
- FPO/Buyer requirement: buyer_requirements table exists in SQL but no API for CRUD

### C. Mocked
- All persistence: `LOTS.append(new_lot)` in-memory, resets on restart
- Auth: localStorage, no backend verification
- Payments: none
- Maps: static demo coordinates, no GIS queries
- Notifications: none

### D. In-Memory Demo Data (Critical)
- `backend/data/demo_data.py` — `PRICES`, `MARKETS`, `BUYERS`, `LOTS`, `OFFERS`, `TRANSACTIONS` as dicts/lists
- `frontend/src/data/demoData.js` — duplicate of backend data + `DEMO_PRICES`, `DEMO_BUYERS` with slightly different shapes
- Both bypass DB entirely when `DEMO_MODE=true` (default)

### E. Bypasses Backend APIs
- `frontend/src/services/api.js`: if `DEMO_MODE` then returns `DEMO_PRICES` etc. directly **without calling Flask**. Even in LIVE mode, it falls back to demo data on any error (`catch -> return DEMO_PRICES`). This violates "database-first" and "API-first" principles. Frontend can operate fully offline from backend.

### F. Direct DB Access (Not Applicable)
- No direct DB access from frontend, but also no DB access from backend (unused Supabase). So neither layer uses DB in production path.

### G. Insecure
- No authentication, no password hashing, no JWT, no session rotation
- No RBAC enforcement (frontend `isFarmer` hide is not authorization)
- No rate limiting, no secure headers, no CORS restriction beyond `FRONTEND_URL`
- Aadhaar `aadhaar_number TEXT` in schema without encryption consideration (violates §11)
- No input sanitization beyond basic required-fields check; no Zod/Pydantic validation
- No audit logs, no request_id, no secret scanning
- `allow_headers: ["Content-Type","Authorization"]` but no Authorization logic

### H. Duplicated Logic (DRY Violation)
- Matching: `backend/services/matching_service.py` (40/25/20/15) vs `frontend/services/api.js getMatches()` re-implements similar scoring with different thresholds (40/25/20/15 but different grade/distance logic)
- Price: `demo_data.py` generates 15-day series per market per crop; `demoData.js` generates random `DEMO_PRICE_HISTORY` via `Math.random()` — inconsistent
- Trend: `trend_service.py` vs frontend `getTrend()` in `api.js` — duplicated explanation strings
- Types: no shared types; frontend and backend define own shapes for Lot, Buyer, Price

### I. Reusable (Keep & Evolve)
- Matching scoring concept (crop/grade/quantity/distance) — refine to 100-pt spec with price/time/verification
- Trend 3% threshold — evolve to configurable versioned rules + 14/30-day + volatility
- Market/district adjacency idea — replace with PostGIS ST_DWithin
- Translation keys structure — migrate to next-intl JSON
- Price min/modal/max/volume shape — add provenance fields
- Lot fields (crop, quantity, grade, expected_price) — extend to full Lot model (§23)
- Offer fields (lot_id, buyer_id, price, quantity, status) — extend to negotiation + reservations

### J. Must Be Rewritten
- Backend framework: Flask → FastAPI (for Pydantic v2, OpenAPI, async)
- Frontend framework: Vite JS → Next.js App Router + TypeScript + strict mode
- Persistence: dicts → PostgreSQL + PostGIS + Alembic
- Auth: localStorage → JWT/refresh + Argon2id + RBAC
- API contract: unversioned `/api/*` → `/api/v1/*` with typed schemas + OpenAPI generation
- Validation: manual `if missing` → Pydantic/Zod
- Frontend data layer: `DEMO_MODE` bypass → TanStack Query + typed API client against DB-seeded demo data
- State machines: status strings → explicit versioned transitions with constraints

---

## 5. Target Architecture

Described in §6 of master directive. Key migration:

| Current | Target |
|---------|--------|
| Flask Blueprints | FastAPI Routers + Services + Repositories |
| demo_data.py | PostgreSQL + PostGIS + Alembic seeds |
| localStorage auth | JWT + RBAC Middleware |
| Vite JS | Next.js 15 + TS + TanStack Query + shadcn/ui |
| Manual validation | Pydantic v2 + Zod |
| No audit | `audit_logs` + transactional outbox |
| No provenance | `price_sources`, `data_provenance`, `ingestion_runs` |
| Adjacency dict | PostGIS GEOGRAPHY + ST_DWithin |

---

## 6. Migration Strategy

**Phase 0 → 1:** Audit + Architecture Decision Records (this doc + `docs/ARCHITECTURE.md`, `docs/ADR/`, `DATA_MODEL.md`, etc.)  
**Phase 2:** Infrastructure — Docker Compose (frontend, backend, postgres+postgis, redis, worker), `.env.example`, Alembic init  
**Phase 3:** DB migration — port `schema.sql` to SQLAlchemy models + PostGIS + Alembic, seed from `demo_data.py` (normalize PRICES series into `market_prices` + `price_observations`)  
**Phase 4:** Auth/RBAC — users, roles, Argon2id, JWT, middleware, protect `/api/v1/*`  
**Phase 5:** API foundation — versioned routers, response envelope `{success,data,message,request_id}`, OpenAPI, generated TS client  
**Phase 6:** Frontend architecture — Next.js scaffold, design system, i18n (next-intl), PWA  
**Phases 7-18:** Domain modules iteratively (prices → lots → matching → offers → reservations → transactions → etc.), each with models/schemas/repositories/services/routes/tests  
**Phase 19-22:** Observability, hardening, demo snapshot `WHEAT-NASHIK-DEMO-001`, E2E

**Strangler pattern:** Keep Flask prototype running on `:5000` while FastAPI builds on `:8000` with `/api/v1`. Frontend proxy switches incrementally.

---

## 7. Technical Debt

1. No types (JS + untyped Flask)
2. No tests (0% coverage)
3. No migrations (raw SQL only)
4. No pagination on any list endpoint ( `get_all_prices` returns all)
5. No indexes analysis (schema has no indexes beyond PK/UNIQUE)
6. No error handling standard (some routes return 400, others silent success)
7. Hardcoded markets list in `routes/prices.py` (`from data.demo_data import MARKETS` imported inside function)
8. `gunicorn` in requirements but no config, conflicts with Flask dev server
9. `pandas` imported but never used in backend (dead dependency)
10. Frontend `package.json` type:module but `vite.config.js` is CJS-compatible only

---

## 8. Security Issues

- **P0:** No auth — any client can POST lots/offers as any farmer_id
- **P0:** No authorization — buyer can accept own offer as farmer
- **P0:** No rate limiting — ingestion/matching could be abused
- **P1:** No input validation on `expected_price` (negative? huge?)
- **P1:** CORS `origins=[FRONTEND_URL, "http://localhost:3000"]` hardcoded, no env toggle for prod
- **P1:** No secure headers (HSTS, CSP, X-Frame-Options)
- **P1:** Sensitive fields (Aadhaar, bank_account, ifsc_code) stored plaintext, no encryption plan
- **P2:** Error messages leak stack? Flask debug True by default

---

## 9. Data Issues

- No provenance: PRICES have `source: demo` only, no `retrieved_at`, `raw_payload_hash`, `ingestion_run_id`
- Derived metrics (trend) not linked to rule version — cannot replay "why RISING?"
- Quantity unit inconsistent: schema says `unit DEFAULT 'quintal'` but demo lots use `tonnes`/`quintal` interchangeably
- Price `volume_tonnes` vs demoData `volume` vs frontend `volume` — same concept different names
- No constraints: `lots.quantity` can be 0, `offers.quantity` can exceed `lots.quantity`
- No soft deletion, no `updated_at` triggers

---

## 10. API Issues

- Unversioned (`/api/prices` vs required `/api/v1/prices`)
- Inconsistent envelopes: `success`, `data`, `message` present but no `request_id`, no `code`, no `details`
- No OpenAPI (Flask doesn't generate)
- No idempotency keys
- No pagination, no filtering standardization (some use query, some use path)
- Duplicate routes: `/api/prices?crop=X&market=Y` and `/api/prices/<crop>` do overlapping work

---

## 11. Frontend Issues

- JS not TS, no strict mode, no types for API responses
- `DEMO_MODE` bypass violates §63
- No TanStack Query (no caching, no retry, no background refetch)
- No React Hook Form + Zod (forms use uncontrolled inputs)
- No shadcn/ui (custom ad-hoc components, not reusable design system)
- No PWA (no manifest, no service worker)
- No accessibility audit (missing labels, focus, contrast checks)
- Translations: object in JS, not JSON per locale, not ICU, not next-intl

---

## 12. Database Issues

- Schema is Supabase-flavored but lacks: PostGIS, indexes, check constraints on prices, soft delete, outbox, audit_logs, provenance
- Missing entities: `price_observations`, `price_sources`, `ingestion_runs`, `lot_allocations`, `reservations`, `payments`, `deliveries`, `storage_facilities`, `evidence`, `notifications`, `audit_logs`, `outbox_events`, `system_configurations`, `crop_varieties`
- UUID default uses `uuid-ossp` (legacy) vs `pgcrypto` gen_random_uuid()
- No Alembic, no migrations versioning
- `seed.sql` not inspected but likely inserts demo users/prices without provenance

---

## 13. Testing Gaps

- 0 test files in entire repo (`glob **/*.test.*` → 0, `**/test_*` → 0)
- No pytest, no vitest, no Playwright, no Postman collection
- No contract testing, no visual regression
- No CI (no `.github/workflows`)

---

## 14. Deployment Gaps

- No Docker, no Compose
- No environment-based config validation
- No health checks beyond `/api/health`
- No observability (no structured logs, no metrics, no tracing)
- No secret management (`.env.example` exists but no validation at startup)

---

## 15. Reuse Matrix

| Concept | Reuse? | Action |
|---------|--------|--------|
| Crop/market lists | ✅ | Migrate to DB seed, add PostGIS coords |
| Price min/modal/max | ✅ | Add provenance columns |
| Trend RISING/STABLE/FALLING | ✅ | Version as TrendRule v1 → v2 |
| Matching 100-pt idea | ✅ | Expand to 7-factor spec §26 |
| Lot creation flow | ✅ | Add statuses, splitting, QR |
| Offer accept/reject | ✅ | Add negotiation, reservations, idempotency |
| Transaction timeline | ✅ | Add state machine §34 |
| Grievance/dispute | ✅ | Add evidence, outbox |
| Map experience | ✅ | PostGIS backend |
| i18n keys | ✅ | Port to next-intl JSON |

---

## 16. Decisions Required (ADR Candidates)

- ADR-001: Flask → FastAPI
- ADR-002: Vite JS → Next.js + TS
- ADR-003: Supabase Auth vs self-hosted JWT (choose JWT for §13)
- ADR-004: Celery vs ARQ vs SAQ for async (choose Redis + Celery or alternative documented)
- ADR-005: Matching weights storage (DB `system_configurations` vs config file)
- ADR-006: Payment provider abstraction (Mock vs real adapter)

---

## 17. Next Phase Gate

Do NOT start coding until `docs/ARCHITECTURE.md`, `docs/ADR/`, `docs/API_CONTRACT.md`, `docs/DATA_MODEL.md`, `docs/SECURITY.md`, `docs/TESTING_STRATEGY.md`, `docs/DEPLOYMENT.md`, `docs/OBSERVABILITY.md`, `docs/DATA_PROVENANCE.md` are drafted and internally consistent.

---

*End of Audit — Phase 0 complete.*
