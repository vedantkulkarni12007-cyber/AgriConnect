# ADR-002: Vite JS → Next.js + TypeScript

**Date:** 2026-08-28
**Status:** Accepted

**Context:** Vite React 19 JS prototype, no SSR/SSG, no PWA, no typed API client.

**Decision:** Next.js 15 App Router + TypeScript strict + Tailwind + shadcn/ui + TanStack Query + next-intl + PWA (next-pwa). Required by §3 and §44-50.

**Consequences:** File-based routing, `src/features/*`, generated OpenAPI types, React Hook Form + Zod. Vite dev stays until cutover.

**Alternatives Rejected:** Keep Vite + add TS (misses App Router, PWA, i18n routing benefits).
