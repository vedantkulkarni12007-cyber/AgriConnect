# KRISHILINK 2.0 — FINAL PRODUCTION ENGINEERING, HARDENING & SHIP-READINESS SPECIFICATION

## Role & Mandate
You are taking over an existing, substantially developed application as a:
- Principal Full-Stack Engineer
- Software Architect
- Backend Engineer
- Frontend Engineer
- Security Engineer
- Database Engineer
- Performance Engineer
- QA Engineer
- DevOps/CI Engineer
- Reliability Engineer
- Product Engineer

Your responsibility is to take the current KrishiLink 2.0 codebase through its final engineering hardening phase before deployment and real-world testing.

**Core Directives**:
- **NOT a rewrite / NOT a redesign**: Preserve existing FastAPI (`backend/app`), React/Vite (`frontend`), PostgreSQL/PostGIS / SQLite database models, auth, routes, and UI.
- **Legacy Context**: `backend/app/` is the live FastAPI 2.0 production application. `backend/routes/`, `backend/services/`, `flask_app_legacy.py` are legacy Flask migration reference files. Do not spend engineering time on legacy Flask code or duplicate functionality.
- **Default Strategy**: `MODIFY + IMPROVE + EXTEND`.

---

## Phased Execution Roadmap

### Phase 0: Baseline & Audit
- Run and record baseline metrics:
  - Backend tests: `python -m pytest -v`
  - Frontend build: `npm run build`
  - Linting: `ruff check backend` and `npm run lint`
- Inspect current branch, test counts, failing tests, and runtime logs.

### Phase 1: P0 Security & Eliminating Fabricated Data
- **Eliminate Fabricated Data Fallback**: In `frontend/src/services/api.js`, remove silent fallback to fake demo data returning `success: true` on failed API calls. Real API failures must show clear error states with retry options. Demo data only when explicitly requested (`?demo=1` or dev mode). Update `DemoModeBanner.jsx` to reflect true data provenance.
- **Outbox Authorization**: Restrict `GET /outbox/pending` in `backend/app/modules/notifications/router.py` to admin/operator roles only (return 403 for unauthorized users).

### Phase 2: Authentication, Server-Side RBAC & Rate Limiting (P0/P1)
- **Server-Side RBAC**: Verify every protected endpoint validates authentication, role authorization, resource ownership (farmers only edit their lots; buyers only edit their offers), and state transition permissions.
- **Auth Hardening**: Password hashing, secure JWT access/refresh token handling, safe logout, token invalidation, no sensitive credential leakage in responses or logs.
- **Rate Limiting**: Wire sliding-window rate limiting into `/auth/login`, `/auth/register`, and critical mutation endpoints to protect against brute force and request storms.
- **Password Reset & Account Recovery**: Implement secure single-use token generation with expiration and rate limiting.

### Phase 3: Database Integrity, Concurrency & Idempotency (P1)
- **Concurrency**: Verify and preserve existing `with_for_update()` row-locking for lot reservations and offer negotiations.
- **Transactions & Idempotency**: Verify `Transaction.idempotency_key` on mutating transaction endpoints to prevent duplicate charges or double state transitions on retries.
- **Status Machine Cleanup**: Audit status fields (`Lot.status`, `Offer.status`, `Transaction.status`) and remove obsolete legacy lowercase check constraints via safe migration.

### Phase 4: Canonical Customer Support & Dispute Architecture (P2)
- Unified support & dispute lifecycle: `OPEN` → `ASSIGNED` → `IN_PROGRESS` → `WAITING_USER` → `RESOLVED` → `CLOSED`.
- Support categories, priority levels, threaded messages/replies, audit history, and role-based data isolation (customers see only their tickets; internal admin notes protected).

### Phase 5: Complete End-to-End Notification System (P2)
- Event-driven persistence into `notifications` table on critical domain events (offers received/accepted, transaction updates, support replies, reservation expiries).
- Frontend dashboard bell wired to live DB notification endpoints with unread badges, mark-as-read, and deep links.

### Phase 6: Performance, Latency & Search Optimization (P2)
- Optimize slow queries, database indexes, and response payloads.
- Debounce and paginate marketplace/price searches server-side.
- Audit dashboard loading to eliminate sequential N+1 network requests.

### Phase 7: Mobile, Accessibility & UX Polish (P2/P3)
- Responsive audit across Mobile, Tablet, Laptop, and Desktop.
- Zero dead/fake buttons — every button must either perform its real action or be clearly disabled with an explanation.
- Truthful, friendly user error messages with clear next steps.

### Phase 8: Full Test Suite, Hardened CI/CD & Observability (P1)
- Fix all broken test fixtures in `tests/test_integration_*.py`.
- Remove any `|| true` or `|| echo` bypasses in CI workflows so failures genuinely turn CI red.
- Structured logging for critical mutations, auth failures, and error diagnostics without logging secrets.

### Phase 9: Multi-Role End-to-End Journey Verification
- **Farmer Journey**: Register/Login → Dashboard → Listing → Match Discovery → Offer Negotiation → Transaction → Grievance.
- **Buyer Journey**: Register/Login → Discovery & Filters → Offer Submission → Payment State → Delivery → Review.
- **FPO Journey**: Login → Member Produce Aggregation → Bulk Lot Listing → Collective Negotiation.
- **Admin Journey**: Admin Login → User Moderation → Disputes Arbitration → Support Management → Audit Logs.

### Phase 10: Final Production Audit & Code Freeze
- Comprehensive security test matrix (401, 403, 404, rate limit, idempotency, upload validation).
- Update canonical documentation: `README.md`, `ARCHITECTURE.md`, `API.md`, `TESTING.md`, `SECURITY.md`.
- Code Freeze for handoff to the separate real-world deployment and credential provisioning phase.
