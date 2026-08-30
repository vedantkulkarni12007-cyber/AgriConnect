# KrishiLink API Contract (v1)

**Base:** `/api/v1` · **Auth:** Bearer JWT (except public) · **Content-Type:** `application/json` · **Idempotency:** `Idempotency-Key: <uuid>` for mutating endpoints marked *

**Envelope**
```json
{ "success": bool, "data": T|null, "message": string, "request_id": "uuid", "code"?: string, "details"?: any }
```
Error codes: `VALIDATION_ERROR` (422), `UNAUTHORIZED` (401), `FORBIDDEN` (403), `NOT_FOUND` (404), `CONFLICT` (409), `RATE_LIMITED` (429).

**Auth**
- `POST /api/v1/auth/register` `{email,password,role,full_name,phone,location,district}` → 201
- `POST /api/v1/auth/login` → `{access_token, refresh_token}`
- `POST /api/v1/auth/refresh` `POST /api/v1/auth/logout`

**Prices / Provenance (§18-22)**
- `GET /api/v1/prices?crop=&market=&page=&limit=` → `Paginated<PriceObservation>`
- `GET /api/v1/prices/{crop}` → `{best_price, latest_prices, history_by_market}`
- `GET /api/v1/prices/{crop}/history?market=&days=` → history
- `GET /api/v1/trends/{crop}?market=` → `{current_price, moving_average, percentage_change, trend, explanation, rule_version}`
- `GET /api/v1/prices/{id}/provenance` → provenance record §18
- `GET /api/v1/prices/{id}/explanation` → §22

**Markets / Crops**
- `GET /api/v1/markets?district=&crop=&near_lat=&near_lng=&radius_km=` (PostGIS)
- `GET /api/v1/crops` `GET /api/v1/crops/{id}`

**Lots (§23-24,41)**
- `GET /api/v1/lots?status=&crop=&farmer_id=&page=` 
- `POST /api/v1/lots*` `{crop,variety,grade,quantity,unit,asking_price,market_reference_price,location,harvest_date,available_from,available_until}` → 201 `{id, public_id: KL-LOT-2026-000182, qr_url}`
- `GET /api/v1/lots/{id}` `PATCH /api/v1/lots/{id}` `POST /api/v1/lots/{id}/publish*` `POST /api/v1/lots/{id}/cancel`
- `GET /api/v1/lots/{id}/allocations` `GET /api/v1/lot/{publicId}` (public QR page)

**Buyer Requirements (§25,29)**
- `CRUD /api/v1/buyer-requirements` + `GET /api/v1/demand/heatmap?crop=&grade=&bbox=`

**Matching (§26-28)**
- `POST /api/v1/matches/refresh` (idempotent) + `GET /api/v1/matches?lot_id=` → `[{buyer, score, component_scores, explanation, ruleset_version}]`
- `GET /api/v1/matches/{id}/explanation` → why recommended

**Offers/Negotiations (§30-31)**
- `GET /api/v1/offers?lot_id=&status=` `POST /api/v1/offers*` `{lot_id, quantity, price, message, expires_at}`
- `POST /api/v1/offers/{id}/counter` `POST /api/v1/offers/{id}/accept*` `POST /api/v1/offers/{id}/reject` `POST /api/v1/offers/{id}/withdraw`
- `GET /api/v1/offers/{id}/history`

**Reservations (§32)** `GET /api/v1/reservations` (auto on offer accept, expires, DB-locked)

**Transactions/Payments/Logistics (§34-37)**
- `POST /api/v1/transactions*` `GET /api/v1/transactions/{id}` `GET /api/v1/transactions` `POST /api/v1/transactions/{id}/transition` (FSM guard)
- `POST /api/v1/payments*` (MockPaymentProvider adapter)
- `GET /api/v1/logistics/calculate?lot_id=&buyer_id=` → `{distance, transport_cost, net_realization}` (§37)

**Storage (§38)** `CRUD /api/v1/storage-facilities` with capacity guards

**Disputes/Evidence (§39-40)** `POST /api/v1/disputes*` `POST /api/v1/disputes/{id}/evidence` (S3, hash stored)

**What-if (§77)** `POST /api/v1/calculator/net-realization` `{selling_price, quantity, transport, storage, fees}` → `{gross, net, break_even}`

**Admin (§54-55)** `GET /api/v1/admin/*` (ADMIN only) users/verification/markets/ingestion/transactions/disputes/audit/system-health

**System** `GET /api/v1/health` `GET /api/v1/metrics` · Pagination `?page=1&limit=20` · All lists paginated.

OpenAPI from FastAPI at `/api/v1/openapi.json`; TS client generated via `openapi-typescript`; Postman at `docs/postman/`.
