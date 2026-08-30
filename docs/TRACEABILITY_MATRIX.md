# Requirement Traceability Matrix (§80)

| Requirement | DB | Service | API | Frontend | Test |
|-------------|----|---------|-----|----------|------|
| §1.1 Farmer price discovery | price_observations, markets | PriceService, TrendService | GET /prices, /trends | /prices, /farmer/prices PriceCard+TrendBadge | pytest trend + Playwright price flow |
| §1.5 List produce | lots | LotService.create/publish | POST /lots, /lots/{id}/publish | /farmer/sell (RHF+Zod) | integration lots, E2E sell |
| §26 Matching 100pt | match_rulesets, matches | MatchingService (7 scores) | GET /matches?lot_id, /matches/{id}/explanation | /farmer/matches MatchCard+Replay | unit matching, contract |
| §23-24 Lot splitting | lot_allocations | LotService allocation with FOR UPDATE | GET /lots/{id}/allocations | Lot detail remaining qty | integration quantity guard |
| §30-32 Offers/reservations | offers, reservations | OfferService, ReservationService | POST /offers, /offers/{id}/accept | /offers, negotiation timeline | unit FSM + integration lock |
| §34 Transactions FSM | transactions, transaction_items | TransactionService | POST /transactions, /transactions/{id}/transition | /transactions Timeline | FSM tests |
| §41 QR | lots.public_id | LotService.generate_public_id | GET /lot/{publicId} | public QR page | E2E QR |
| §42 Traceability | audit_logs, deliveries | AuditService, TraceabilityService | GET /audit + lineage | Transaction timeline | audit tests |
| §59 Audit | audit_logs, outbox_events | Audit + Outbox | all mutating routes | admin/audit | integration outbox |

*Full matrix expands per §81 in `AGENTS.md` — auto-generated from OpenAPI + DB schema in CI.*
