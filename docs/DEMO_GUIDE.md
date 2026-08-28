# KrishiLink Demo Guide — WHEAT-NASHIK-DEMO-001

**Seed:** `python -m app.seed` (idempotent, 960 obs, 5 lots)
**Users:** `ramesh@demo.com/demo123!` (farmer), `mehta@demo.com/demo123!` (buyer), `admin@krishilink.demo/demo123!` (admin)

### Flow 1-24 (spec §85)
1. `POST /api/v1/auth/login` farmer
2. `GET /api/v1/prices?crop=Wheat` → today's modal
3. `GET /api/v1/markets` compare
4. `GET /api/v1/prices/{id}/provenance` → source, hash
5. `GET /api/v1/prices/Wheat/history?days=14` → trend
6. `POST /api/v1/lots` farmer 1000kg Wheat (Idempotency-Key)
7. `POST /api/v1/matches/refresh {lot_id}` → 2 matches 95/84
8. `GET /api/v1/matches/{id}/explanation` → Why 95?
9. Buyer `GET /api/v1/buyer-requirements` (via profile)
10. Buyer `POST /api/v1/offers {lot_id, quantity 400, price 2050}`
11. Farmer `POST /offers/{id}/counter {price 2100}`
12. Buyer `POST /offers/{new_id}/accept` → 400kg ACTIVE reservation 48h
13. Reserved quantity checked via `SELECT FOR UPDATE`
14. `POST /transactions {reservation_id}` → CREATED
15. `POST /transactions/{id}/transition PAYMENT_PENDING → COMPLETED` (7 steps)
16. `GET /transactions/{id}` → timeline
17. `POST /disputes` → OPEN
18. `POST /disputes/{id}/evidence {s3_key,file_hash}`
19. Transaction COMPLETED, lot remaining 600kg via `SELECT SUM(allocated)` check
20. `GET /lots/public/KL-LOT-2026-000004` QR safe
21. `GET /admin/audit` → all steps logged
22. Outbox `GET /notifications/outbox/pending` → events
23. Admin `GET /admin/system-health` → HEALTHY
24. `GET /metrics` Prometheus

### Failure Demo (§86)
- Duplicate `Idempotency-Key` → same public_id
- Expired reservation (worker `reservations.expire`)
- Invalid transition → 409
- Unauthorized → 401/403
- `GET /lots/public/KL-...` without auth → 200 (public safe only)

### URLs
- Frontend: http://localhost:5173 (Vite) / http://localhost:3000 (Next.js future)
- API: http://localhost:8001/docs (OpenAPI), http://localhost:8001/api/v1/health/detailed
- DB: `docker exec krishilink-postgres-1 psql -U krishilink -d krishilink -c '\dt'`
