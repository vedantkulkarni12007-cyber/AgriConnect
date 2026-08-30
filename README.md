# 🌿 KrishiLink 2.0 — Production-Ready Agricultural Marketplace

[![CI Pipeline](https://github.com/vedantkulkarni12007-cyber/KrishiLink/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/vedantkulkarni12007-cyber/KrishiLink/actions/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/Tests-73%20Passed-brightgreen)](file:///backend/tests)
[![Python](https://img.shields.io/badge/FastAPI-0.115-blue)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React%2FVite-18-blue)](https://vitejs.dev)
[![PostGIS](https://img.shields.io/badge/PostgreSQL-PostGIS%20GEOGRAPHY-informational)](https://postgis.net)

**"Better Prices. Better Buyers. Better Decisions."**

KrishiLink 2.0 is a hardened, production-grade agricultural digital marketplace built for the Smart India Hackathon 2026, connecting Indian farmers, Farmer Producer Organizations (FPOs), and commercial buyers. It offers real-time mandi modal pricing, 7-factor explainable matchmaking, escrow transaction state machines, verified cold-storage discovery, persistent event-driven notifications, and a transparent grievance arbitration system.

---

## 🏗️ Architecture & Technology Stack

- **Backend Application**: FastAPI (`backend/app/main.py`) + SQLAlchemy 2.0 + Pydantic v2
- **Database & Spatial**: PostgreSQL 15 + PostGIS (`GEOGRAPHY(POINT, 4326)`) with SQLite dual-compatibility for tests
- **Caching & Rate Limiting**: Redis 7 sliding-window rate limiting with in-memory fallback
- **Asynchronous Outbox & Tasks**: Celery worker & beat for transactional outbox dispatch and reservation expirations
- **Object Storage**: S3 adapter with presigned upload and download URLs (`backend/app/core/s3.py`)
- **Frontend SPA**: React 18 + Vite + Tailwind CSS + Lucide Icons + Recharts + Leaflet
- **Observability**: Prometheus metrics (`/metrics`), OpenTelemetry tracing, and Audit Logging on all state mutations

---

## 🚀 Quick Start (Local Development)

### 1. Start Full Stack with Docker Compose
```bash
docker compose up --build
```
- **FastAPI API Server**: `http://localhost:8001/api/v1` (OpenAPI docs: `http://localhost:8001/api/v1/docs`)
- **React Frontend**: `http://localhost:5173`
- **PostgreSQL / PostGIS**: `localhost:5435`
- **Redis**: `localhost:6380`

### 2. Manual Dev Setup

#### Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000
```

#### Frontend:
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing & Verification

The test suite covers unit tests, integration tests, concurrency & row-locking validations, cryptographic auth, rate limiting, and multi-role end-to-end user journeys.

```bash
# Run backend test suite (73 tests)
cd backend
python -m pytest -v

# Run linting
python -m ruff check app

# Run frontend build & lint
cd frontend
npm run lint
npm run build
```

---

## 👥 Demo User Credentials

| Role | Email | Password | Primary Capabilities |
| :--- | :--- | :--- | :--- |
| **Farmer** | `ramesh@demo.com` | `demo123!` | List produce lots, receive buyer offers, accept/counter, file disputes |
| **Buyer** | `buyer@demo.com` | `demo123!` | Browse marketplace, filter mandis, submit price offers, track escrow orders |
| **Buyer** | `mehta@demo.com` | `demo123!` | Bulk procurement, contract negotiation |
| **FPO** | `fpo@demo.com` | `demo123!` | Aggregate collective lots, warehouse & cold-storage booking |
| **Admin** | `admin@demo.com` | `demo123!` | Moderate users, arbitrate disputes, monitor system metrics & outbox |

---

## 📁 Repository Structure

```
KrishiLink/
├── .github/workflows/ci.yml       # GitHub Actions CI workflow
├── backend/
│   ├── app/
│   │   ├── core/                  # Database, security, config, rate limiting, S3, OTel
│   │   ├── modules/
│   │   │   ├── admin/             # System health, metrics, user moderation
│   │   │   ├── auth/              # JWT, Argon2, password reset
│   │   │   ├── crops/             # Commodity catalog & varieties
│   │   │   ├── disputes/          # Customer support & grievance arbitration
│   │   │   ├── lots/              # Produce listing, QR codes, idempotency
│   │   │   ├── markets/           # APMC Mandi coordinates & distance queries
│   │   │   ├── matching/          # 7-factor 100pt explainable matchmaking
│   │   │   ├── notifications/     # Persistent alerts & transactional outbox
│   │   │   ├── offers/            # Buyer negotiation FSM & row locking
│   │   │   ├── prices/            # Modal price trends & historical analytics
│   │   │   ├── storage/           # Warehouse & cold storage discovery
│   │   │   └── transactions/      # Escrow milestone state machine
│   │   └── seed.py                # Database seeder with realistic Maharashtra mandis
│   ├── alembic/                   # Database schema migrations
│   └── tests/                     # 73 automated unit & E2E integration tests
├── frontend/
│   ├── src/
│   │   ├── components/            # Design system badges, states, banners
│   │   ├── layouts/               # DashboardLayout with live notification bell
│   │   ├── pages/                 # Role dashboards, marketplace, orders, support
│   │   └── services/api.js        # Truthful API client with provenance tagging
│   └── vite.config.js
└── docs/                          # Architecture ADRs, deployment guides, and specs
```
