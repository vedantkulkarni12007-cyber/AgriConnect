# Legacy Schema

This file (`schema_legacy_supabase.sql`) contains the original Supabase/Flask schema from the prototype.

## Status: DEPRECATED

**Do not use this schema for production.** It is retained for reference only.

### Key differences from current schema:

| Aspect | Legacy (this file) | Current (Alembic) |
|--------|-------------------|-------------------|
| Geo type | `geometry(Point, 4326)` | `geography(Point, 4326)` via PostGIS |
| Owner field | `seller_id` | `owner_id` |
| Audit/Outbox | Not present | `audit_logs`, `outbox_events` tables |
| Migrations | Manual SQL | Alembic-managed |
| CHECK constraints | Few | Comprehensive |

### Authoritative schema source

The authoritative schema is defined by:
1. **SQLAlchemy models** in `backend/app/models.py`
2. **Alembic migrations** in `backend/alembic/versions/`

Use `alembic upgrade head` to apply the current schema to a database.