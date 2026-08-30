# KrishiLink Security

## Principles (§58-59)

Secure-by-default; deny-by-default RBAC; never trust client `user_id/role/price/status`.

## Auth (§13)

- Argon2id (or bcrypt 12) hashing, never plaintext
- JWT access 15m + refresh 7d with rotation, revocation list in Redis, `jti`
- Secure cookies `HttpOnly, Secure, SameSite=Lax`, CSRF where cookie-based (double-submit)
- Password reset + email verification architecture (token via outbox, expiry 1h)
- No localStorage as source of truth

## RBAC (§14)

Roles: `FARMER, FPO, BUYER, ADMIN, OPERATOR`. Decorator `require_role(...)` on every protected route. Ownership checks: farmer can only mutate own lots (`lot.owner_id == current_user.id`). Tests cover 401/403.

## Validation & Injection

- Pydantic v2 (backend) + Zod (frontend) on every endpoint; `extra=forbid`, `strip_whitespace`, regex for phone/email
- SQLAlchemy ORM parameterized — no raw string interpolation; SAST via Semgrep
- XSS: CSP, `X-Content-Type-Options: nosniff`, sanitize rich text

## Headers & CORS

- `Strict-Transport-Security`, `X-Frame-Options: DENY`, `Content-Security-Policy`, `Referrer-Policy`, `Permissions-Policy`
- CORS allowlist from env `CORS_ORIGINS`, credentials only for same-site, no `*`

## Rate Limiting

- Redis sliding window: login 5/min, ingestion 10/min, general 100/min per IP+user

## Secrets

- Never commit `.env`; `.env.example` only; config via `pydantic-settings` validated at startup; secret scanning (gitleaks, GitHub secret scanning); dependency/container scanning (Dependabot, Trivy)

## Data Minimization (§11)

- No Aadhaar unless legal requirement; if needed, encrypted at rest (pgcrypto `pgp_sym_encrypt`, key in vault), never in API responses; audit access to sensitive fields

## Audit Logging (§59)

- Every login/logout, profile change, lot publish, offer accept/counter, transaction transition, payment, dispute, admin action → `audit_logs(actor, action, entity, entity_id, before, after, request_id, timestamp)` — immutable, append-only.

## Observability Safety

- Never log passwords, tokens, financial PAN, PII; structured logs redacted; request_id correlation.

## Feature Flags (§60)

`system_configurations` guards `VOICE_INPUT, QR_TRACEABILITY, LIVE_PRICE_INGESTION, DEMAND_HEATMAP, REAL_PAYMENT, WHATSAPP_ALERTS, NEW_MATCHING_RULES` — disabled by default, admin-toggle with audit.
