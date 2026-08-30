# KrishiLink Observability (§55-56)

## Logs

Structured JSON via `structlog`/`loguru`, fields `timestamp, level, request_id, user_id, action, entity, latency_ms, status`. Request ID via `X-Request-ID` middleware (uuid4, echo). Never log secrets/PII. Sample: `{"level":"info","request_id":"...","method":"POST","path":"/api/v1/offers","user_id":"...","status":201,"latency_ms":123}`.

## Metrics (Prometheus)

`prometheus_client` exposes `/metrics`: `http_requests_total{method,path,status}`, `http_request_duration_seconds`, `db_pool_in_use`, `celery_tasks_total{status}`, `ingestion_records_total{source,quality}`, `reservation_expiry_total`. Dashboard in `grafana/dashboards/krishilink.json`.

## Tracing

OpenTelemetry SDK → OTLP collector → Tempo/Jaeger. Trace each request through FastAPI → SQLAlchemy → Redis → Celery. `trace_id` in logs.

## Error Tracking

Sentry SDK (backend + frontend), release + environment, beforeSend redacts PII. Alerts on 5xx >1% or ingestion failure >3 retries.

## Health (§55)

`GET /api/v1/health` returns `{api, database, redis, worker, storage}` each HEALTHY/DEGRADED/DOWN + `last_ingestion`, `records_processed/rejected`, `failed_jobs`. Used by Docker HEALTHCHECK, load balancer, admin `/admin/system-health`.

## Admin Visibility

Operator can inspect failed `ingestion_runs`, `outbox_events` with retry, `audit_logs` filter by actor/entity, `celery` flower at `/admin/ops/flower` (admin only).
