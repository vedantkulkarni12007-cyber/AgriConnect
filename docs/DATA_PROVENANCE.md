# KrishiLink Data Provenance & Lineage (§18-19,78-79)

## Provenance (§18)

Every external price row stores:

`source, source_record_id, source_url, published_at, retrieved_at, ingestion_run_id, parser_version, normalization_version, raw_payload_hash (SHA256), quality_status (HIGH/MEDIUM/LOW)`

Pipeline: `FETCH → VALIDATE → NORMALIZE → DEDUPLICATE → QUALITY_CHECK → STORE → UPDATE_DERIVED` (§62). `ingestion_runs` tracks fetches; failures go to dead-letter with retry.

UI badge: "Where did this number come from?" → modal with source, market, date, modal price, `retrieved_at`, `raw_payload_hash` prefix, `ingestion_run_id`.

## Lineage (§19)

Derived metrics (7/14/30-day avg, trend, volatility, anomaly) store `inputs` (array of observation IDs), `calculation` (SQL/Python snippet ref), `rule_version` (e.g., `TrendRule v1.2`), `generated_at`. Example: `14-day average ₹2300` → 14 observations → TrendRule v1.2 → RISING. Replayable.

## Quality (§78)

Check on ingestion: missing values, duplicates (`UNIQUE crop,market,date,source`), staleness (`retrieved_at - published_at`), invalid prices (`modal between min/max`, `>0`), invalid dates, invalid locations (PostGIS). Assign HIGH/MEDIUM/LOW, store in `quality_status`, surface via `DataQualityBadge`.

## Versioned Rules (§79)

`match_rulesets`, `trend_rules`, `anomaly_rules` versioned in `system_configurations` + dedicated tables with `version, effective_from, weights/thresholds, created_by`. Every `matches`/`trends` row references `ruleset_id` + `version` for replay (`Why was this buyer recommended?` shows component scores per version).

## Demo Labeling (§75)

All demo-sourced rows have `source='demo'` and UI shows amber "DEMO DATA" badge; never claim "Live market data" when `source=demo`.

## Adapters (§61)

`PriceSource` interface → `AgmarknetAdapter`, `ENAMAdapter`, `DemoPriceAdapter`. Core price engine consumes normalized `PriceObservationCreate` Pydantic model, not raw payloads.
