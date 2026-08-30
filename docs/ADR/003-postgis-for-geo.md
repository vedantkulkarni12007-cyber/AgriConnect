# ADR-003: PostGIS for Geographic Operations

**Date:** 2026-08-28
**Status:** Accepted

**Context:** Prototype uses `ADJACENT_DISTRICTS` dict for proximity scoring — inaccurate, not scalable, not heatmap-capable.

**Decision:** Use PostgreSQL + PostGIS `GEOGRAPHY(Point,4326)` + GiST indexes + `ST_DWithin`/`ST_Distance`. Markets, buyers, storage, lots all geocoded. Required by §12.

**Consequences:** Add `postgis` to Docker, Alembic `CREATE EXTENSION postgis`, seed lat/lng for 8 markets (already in demo_data). Replace adjacency logic in MatchingService with SQL distance.

**Alternatives Rejected:** Keep adjacency + supplement (keeps technical debt, fails §12).
