# KRISHILINK 2.0 — MASTER PROGRESS TRACKER & REOPENING CONTEXT

> **CRITICAL INSTRUCTIONS FOR ANTIGRAVITY AGENT UPON REOPENING THIS PROJECT:**
> 1. **DO NOT REWRITE OR REDESIGN**: The architecture, UI design, database models, authentication, and directory structures are frozen for production hardening. Never rebuild from scratch.
> 2. **PRODUCTION BACKEND SCOPE**: `backend/app/` is the sole production application (FastAPI + SQLAlchemy 2.0 + PostGIS + Redis + Celery). Ignore legacy Flask reference files (`backend/routes/`, `backend/services/`, `flask_app_legacy.py`).
> 3. **DATA INTEGRITY & PROVENANCE**: Never introduce fake fallback demo data returning `success: true` on failed API requests. All API failures must return explicit error states.
> 4. **GIT & CI DISCIPLINE**: Always work on `feature/production-rebuild-2.0`. Never push directly to `main`. After every push, execute the mandatory Post-Push Checklist and ensure GitHub Actions CI is 100% green before notifying the user.
> 5. **TEST COVERAGE**: Backend tests in `backend/tests/` (60 passing tests) must always remain at 100% pass rate (`python -m pytest -v`).

---

## 📌 Repository State

| Attribute | Current Value |
| :--- | :--- |
| **Active Branch** | `feature/production-rebuild-2.0` |
| **Latest Commit** | `f60ada5` |
| **GitHub Actions CI Status** | **ALL GREEN (✓ Backend, ✓ Frontend)** |
| **Backend Test Suite** | **67 Passed, 0 Failed, 1 Skipped** (`pytest -v`) |
| **Frontend Production Build** | **Built in 22.3s (0 Errors)** (`npm run build`) |
| **Linter Status** | **0 Errors** (`ruff check app`, `npm run lint`) |

---

## 📊 Phase-by-Phase Roadmap & Hardening Tracker

| Phase | Description | Status | Key Deliverables & Files |
| :--- | :--- | :--- | :--- |
| **Phase 0** | **Baseline & Audit** | ✅ Complete | Full codebase audit, baseline metrics, test suites, and Docker stack recorded. |
| **Phase 1** | **P0 Security & Truthful Provenance** | ✅ Complete | • Eliminated silent fake data fallbacks in `frontend/src/services/api.js`.<br>• Enforced server-side Admin RBAC on `GET /notifications/outbox/pending` (`403 Forbidden`).<br>• Cleaned up `DemoModeBanner.jsx` to only display on explicit `?demo=1` or preview. |
| **Phase 2** | **Auth Hardening & Rate Limiting** | ✅ Complete | • Added `POST /api/v1/auth/forgot-password` and `POST /api/v1/auth/reset-password` with JWT tokens.<br>• Sliding-window rate limiter (`backend/app/core/rate_limit.py`) with Redis + in-memory fallback.<br>• Synchronous route handlers with threadpool execution for DB sessions. |
| **Phase 3** | **DB Concurrency & Idempotency** | ✅ Complete | • SQLite & PostGIS dual-compatibility UUID bind processor in `backend/app/core/database.py`.<br>• `Idempotency-Key` headers on `/lots`, `/offers`, `/transactions`.<br>• Row-locking (`with_for_update`) during offer acceptance and lot allocations. |
| **Phase 4** | **Customer Support & Disputes** | ✅ Complete | • Unified support ticket & dispute lifecycle (`OPEN` → `UNDER_REVIEW` → `RESOLVED` → `CLOSED`).<br>• Category and priority selection, resolution notes, and S3 evidence upload.<br>• Enhanced `frontend/src/pages/GrievancesPage.jsx` with real ticket numbers and tracking. |
| **Phase 5** | **Event-Driven Notifications** | ✅ Complete | • Centralized `NotificationService` (`backend/app/modules/notifications/service.py`).<br>• Outbox event emission on offers, transactions, dispute updates.<br>• Live notification polling and unread counter badges in `DashboardLayout.jsx`. |
| **Phase 6** | **Performance & Search Optimization** | ✅ Complete | • Memoized price and marketplace filters (`useMemo`).<br>• Server-side pagination on `/lots`, `/offers`, `/transactions`, `/prices`.<br>• Parameterized PostGIS distance queries. |
| **Phase 7** | **UX Polish & Warning Cleanup** | ✅ Complete | • Fixed React hook dependencies and initialization order in `OffersPage.jsx`, `PricesPage.jsx`, `MatchesPage.jsx`.<br>• Removed unused imports across `LandingPage.jsx`, `BuyerDashboard.jsx`, `TransactionsPage.jsx`. |
| **Phase 8** | **Full Test Suite & Hardened CI** | ✅ Complete | • Fixed all fixtures in `backend/conftest.py` with multi-role seed data (farmer, buyer, fpo, admin).<br>• Removed all `|| true` / `|| echo` bypasses from `.github/workflows/ci.yml`.<br>• CI executes PostGIS, Redis, Alembic up/down, Ruff linting, Pytest, Docker build, and Vite bundle. |
| **Phase 9** | **Multi-Role E2E Journeys** | ✅ Complete | • Created `backend/tests/test_e2e_journeys.py` covering:<br>  - Farmer Journey: Register → Produce Listing → Match Discovery → Dispute Filing → Alerts.<br>  - Buyer Journey: Discovery → Filters → Offer Creation → Negotiation → Escrow Transition.<br>  - FPO Journey: Login → Aggregated Lot Listing → Storage Discovery.<br>  - Admin Journey: Moderation → Health Metrics → Dispute Arbitration → Outbox. |
| **Phase 10**| **Final Production Freeze & Audit** | ✅ Complete | • Updated `README.md`, `ARCHITECTURE.md`, `AGENTS.md`, and `PROGRESS_TRACKER.md`.<br>• 100% Green CI on `feature/production-rebuild-2.0`. |

---

## 🛠️ Command Cheatsheet for Future Sessions

### Running the Stack
- **Full Docker Stack**: `docker compose up --build`
- **FastAPI Dev Server**: `cd backend && python -m uvicorn app.main:app --reload --port 8000`
- **React Frontend**: `cd frontend && npm run dev -- --host 0.0.0.0 --port 5173`
- **Database Migrations**: `cd backend && alembic -c alembic.ini upgrade head`

### Running Verification Tests
- **Run Backend Pytest (60 tests)**: `cd backend && python -m pytest -v`
- **Run Ruff Linter**: `cd backend && python -m ruff check app`
- **Run Frontend Linter**: `cd frontend && npm run lint`
- **Run Frontend Build**: `cd frontend && npm run build`

### Mandatory Post-Push Verification Checklist
```bash
# 1. Verify remote SHA
git -C c:\vedant ls-remote origin feature/production-rebuild-2.0

# 2. Check workflow status
gh --repo vedantkulkarni12007-cyber/KrishiLink run list --limit 3

# 3. Inspect specific workflow run (ensure both frontend & backend are green)
gh --repo vedantkulkarni12007-cyber/KrishiLink run view <RUN_ID>
```

---

## 🔑 Key Architectural Decisions

1. **FastAPI Sync Handlers with SQLAlchemy Sessions**:
   Route handlers in `backend/app/modules/` using synchronous `db: Session = Depends(get_db)` use `def` (not `async def`) so FastAPI delegates them to worker threadpools, preventing blocking of the asyncio event loop.
2. **SQLite & PostgreSQL UUID Compatibility**:
   `backend/app/core/database.py` patches `UUID.bind_processor` to transparently accept both Python `uuid.UUID` objects and UUID strings without raising `'str' object has no attribute 'hex'`.
3. **Sliding-Window Rate Limiting**:
   `backend/app/core/rate_limit.py` provides sliding-window request throttling with Redis backing and in-memory bucket fallback when Redis is offline.
4. **Idempotent Mutations & Concurrency**:
   `Idempotency-Key` headers are verified across lot listings and transactions. Database row locking (`with_for_update()`) prevents race conditions during produce allocation and offer acceptance.

---

## 👥 Demo User Logins

| Role | Email | Password |
| :--- | :--- | :--- |
| **Farmer** | `ramesh@demo.com` | `demo123!` |
| **Buyer** | `buyer@demo.com` | `demo123!` |
| **Buyer** | `mehta@demo.com` | `demo123!` |
| **FPO** | `fpo@demo.com` | `demo123!` |
| **Admin** | `admin@demo.com` | `demo123!` |
