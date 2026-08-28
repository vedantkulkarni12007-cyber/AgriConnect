# ADR-001: Flask → FastAPI

**Date:** 2026-08-28  
**Status:** Accepted

**Context:** Prototype uses Flask without typing, manual validation, no OpenAPI.

**Decision:** Migrate to FastAPI + Pydantic v2. Provides typed schemas, auto OpenAPI, dependency injection for auth/RBAC, async support, better testability. Aligns with §3 required stack.

**Consequences:** Rewrite routes, add `app/core/config.py` via pydantic-settings, generate TS client. Flask app remains on :5000 during strangler migration.

**Alternatives Rejected:** Keep Flask + marshmallow (less idiomatic, no native OpenAPI generation).
