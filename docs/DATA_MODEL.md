# KrishiLink Data Model 2.0

**DB:** PostgreSQL 15 + PostGIS 3.4 · **Migrations:** Alembic · **UIDs:** `gen_random_uuid()` (pgcrypto)

## Core Tables

**users** `id PK, email UNIQUE, phone UNIQUE, password_hash, full_name, role ENUM(FARMER,FPO,BUYER,ADMIN,OPERATOR), location, district, state, is_verified, is_active, created_at, updated_at, deleted_at`
**roles, permissions, user_roles** (RBAC §14)

**farmer_profiles** `id, user_id FK, land_area_acres, primary_crops TEXT[], bank_account_encrypted, ifsc_encrypted`
**buyer_profiles** `id, user_id FK, business_name, business_type ENUM, license_number, crops_interested, min_qty, max_qty, preferred_grade, is_verified, rating, total_transactions, location GEOGRAPHY(Point,4326)` + GiST
**fpo_profiles** `id, user_id FK, organization_name, registration_number, member_count, total_land_acres`

**crops** `id, name UNIQUE, name_* i18n, category, unit, image_url` + **crop_varieties** `id, crop_id FK, name, code`

**markets** `id, name, name_marathi, district, state, location GEOGRAPHY(Point,4326), market_type, is_active`

## Prices & Provenance (§18-22)

**price_sources** `id, name, url, adapter (agmarknet/enam/demo), is_active`
**ingestion_runs** `id, source_id FK, started_at, finished_at, status, records_fetched, records_ok, records_rejected, parser_version, error`
**price_observations** `id, crop_id FK, variety_id FK, market_id FK, price_date, min_price, modal_price, max_price, volume_tonnes, source_id FK, source_record_id, source_url, published_at, retrieved_at, ingestion_run_id FK, parser_version, normalization_version, raw_payload_hash, quality_status ENUM(HIGH,MEDIUM,LOW)` UNIQUE(crop,market,date,source)
**data_provenance** (view or table) joining observation → ingestion_run → source
**market_prices** (materialized/derived latest per crop/market)

**price_intelligence cache** `derived_metrics` or computed view: 7/14/30-day avg, change, volatility, trend ENUM(RISING,STABLE,FALLING,VOLATILE,INSUFFICIENT_DATA), rule_version, inputs JSONB

## Lots & Supply

**lots** `id PK, public_id UNIQUE KL-LOT-YYYY-NNNNNN, owner_id FK users, crop_id FK, variety_id, grade ENUM(A,B,C), quantity, unit, asking_price, market_reference_price, location GEOGRAPHY, harvest_date, available_from, available_until, status ENUM(DRAFT,PUBLISHED,RESERVED,PARTIALLY_ALLOCATED,SOLD,FULFILLED,CANCELLED,EXPIRED), created_at, updated_at` + CHECK quantity>0, available_until>=available_from
**lot_allocations** `id, lot_id FK, buyer_id FK, offer_id FK, allocated_quantity, fulfilled_quantity, remaining_quantity GENERATED, status` CHECK sum allocations ≤ lots.quantity (enforced via SELECT FOR UPDATE + CHECK in service, plus deferred constraint)

**buyer_requirements** `id, buyer_id FK, crop_id FK, variety_id, grade, quantity_min/max, target_price, location GEOGRAPHY, max_distance_km, required_from/until, delivery_window, storage_requirements JSONB, quality_requirements JSONB, is_active`

## Matching

**match_rulesets** `id, version, weights JSONB {crop:30,grade:15,quantity:15,distance:15,price:10,time:5,verification:10}, is_active, created_at`
**matches** `id, lot_id FK, buyer_id FK, buyer_requirement_id, ruleset_id FK, ruleset_version, component_scores JSONB, final_score, explanation JSONB, created_at` UNIQUE(lot,buyer,ruleset_version)

## Offers/Reservations

**offers** `id, lot_id FK, buyer_id FK, owner_id FK, quantity, price_per_unit, total_value GENERATED, message, expires_at, status ENUM(PENDING,COUNTERED,ACCEPTED,REJECTED,EXPIRED,CANCELLED), parent_offer_id FK, created_at`
**negotiations** (optional as offer history via parent_offer_id)
**reservations** `id, lot_id FK, buyer_id FK, offer_id FK, quantity, status ENUM(ACTIVE,EXPIRED,CONSUMED,CANCELLED), reserved_at, expires_at`

## Transactions / Payments / Logistics (§34-37)

**transactions** `id, lot_id FK, buyer_id FK, seller_id FK, allocation_id FK, status ENUM(CREATED,PAYMENT_PENDING,PAYMENT_CONFIRMED,PROCESSING,READY_FOR_DISPATCH,IN_TRANSIT,DELIVERED,COMPLETED,DISPUTED,CANCELLED,REFUNDED), gross_value, transport_cost, storage_cost, fees, net_realization, idempotency_key UNIQUE, created_at`
**transaction_items** `id, transaction_id FK, lot_id FK, quantity, price`
**payments** `id, transaction_id FK, provider, provider_reference, amount, currency, status, timestamps` (MockPaymentProvider)
**deliveries** `id, transaction_id FK, pickup_location GEOGRAPHY, delivery_location GEOGRAPHY, distance_km, estimated_transport_cost, status, evidence_ids`

## Storage / Disputes / Evidence

**storage_facilities** `id, name, type, capacity, available_capacity, location GEOGRAPHY, cost_per_unit, services JSONB, contact, verification_status, status` CHECK available_capacity >=0
**disputes** `id, transaction_id FK, raised_by FK, reason, description, status ENUM(OPEN,UNDER_REVIEW,RESOLVED,REJECTED,ESCALATED), resolution, operator_id, created_at`
**evidence** `id, dispute_id FK nullable, transaction_id FK nullable, lot_id FK nullable, uploader_id FK, s3_key, file_hash, mime_type, metadata JSONB, created_at` (object storage)

## System

**notifications** `id, user_id FK, type, payload JSONB, is_read, created_at`
**audit_logs** `id, actor_id, action, entity, entity_id, before JSONB, after JSONB, request_id, created_at` BRIN on created_at + GIN on entity
**outbox_events** `id, aggregate, aggregate_id, event_type, payload JSONB, status ENUM(PENDING,PROCESSED,FAILED), retry_count, created_at`
**system_configurations** `key PK, value JSONB, version, updated_by, updated_at` (feature flags §60, rule versions §79)
**Idempotency:** `idempotency_keys(key PK, response_status, response_body JSONB, created_at)` or via transactions.idempotency_key

## Indexes

- `market_prices(crop, market, date)` UNIQUE + GiST on `location`
- `price_observations(price_date)` BRIN, `market_prices(modal_price)`
- `lots(status, crop_id)` partial where PUBLISHED, `lots(public_id)` UNIQUE
- `matches(lot_id, final_score DESC)`, `offers(lot_id, status)`
- PostGIS GiST on all GEOGRAPHY columns

## Constraints

All monetary `DECIMAL(12,2)` CHECK >=0; quantities `DECIMAL(12,2)` CHECK >0; state transitions enforced in service + CHECK via allowed_from/to lookup (or service-guarded with DB trigger for invalid).
