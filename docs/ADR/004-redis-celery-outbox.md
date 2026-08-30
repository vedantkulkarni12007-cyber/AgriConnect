# ADR-004: Redis + Celery + Transactional Outbox

**Date:** 2026-08-28
**Status:** Accepted

**Context:** Need async for notifications, ingestion retries, reservation expiry, without losing business writes if side-effect fails (§35).

**Decision:** Redis as broker/backend + Celery (or ARQ if Python 3.14 friction, documented) + transactional outbox table `outbox_events`. Business txn writes `audit_logs` + `outbox_events` atomically; worker polls and dispatches idempotently.

**Consequences:** `redis` + `celery` + `beat` for reservation expiry; outbox worker is Prometheus-instrumented.

**Alternatives Rejected:** Direct after_commit hooks (not durable), full event sourcing (overkill).
