# 🌿 KrishiLink 2.0 — Production Deployment & Cloud Integration Checklist

> **Target Audience**: Senior DevOps, Cloud Engineers, and Release Maintainers  
> **Core Objective**: Deploy KrishiLink 2.0 to run 100% independently over the public internet without dependencies on developer machines, Docker Compose, or local database files.

---

## 🏗️ Target Cloud Architecture

| Component | Target Cloud Provider | Role in KrishiLink 2.0 |
| :--- | :--- | :--- |
| **Frontend SPA** | **Vercel** | React 18 + Vite static application hosting with custom domain and edge routing. |
| **Backend API** | **Render (Web Service)** | Containerized FastAPI ASGI server running multi-worker Uvicorn. |
| **Async Task Worker** | **Render (Background Worker)** | Celery worker executing transactional outbox dispatch and reservation TTL sweeps. |
| **Primary Database** | **Supabase (PostgreSQL 15)** | Relational database with PostGIS (`GEOGRAPHY(POINT, 4326)`) extension. |
| **Cache & Message Broker** | **Upstash Redis / Managed Redis** | Native Redis (`rediss://...`) for Celery queues and sliding-window rate limiting. |
| **Evidence Storage** | **AWS S3 / Cloudflare R2** | Private object bucket storing dispute images/PDFs with presigned URLs. |
| **Authentication** | **Google Cloud Console** | Google Identity Services OAuth 2.0 Client ID for one-tap sign-in. |
| **Transactional Email** | **Resend / SMTP** | Outbox-driven transactional emails for registration and password resets. |

---

## 📋 Phase 1: Supabase (Managed PostgreSQL + PostGIS)

### 1. Database Provisioning
1. Sign in to [supabase.com](https://supabase.com) and create a project in the closest region (e.g. `ap-south-1` Mumbai).
2. Open **Database** → **Extensions**, search for `postgis` and enable **PostGIS**.
3. Go to **Project Settings** → **Database** → **Connection string** → **URI**.
4. Select the **Session** connection pool (Direct port `5432` or pooled port `6543`).

### 2. Required Driver Format for SQLAlchemy & Alembic
FastAPI and Alembic use `psycopg` (v3). Ensure your URI starts with `postgresql+psycopg://`:
```text
postgresql+psycopg://postgres.[project-ref]:[YOUR-PASSWORD]@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
```

### 3. Running Database Migrations
Run Alembic against your Supabase connection string from your CI runner or local environment:
```bash
cd backend
export DATABASE_URL="postgresql+psycopg://postgres.[ref]:[pass]@[host]:6543/postgres?sslmode=require"
alembic upgrade head
```

---

## 📋 Phase 2: Managed Redis (Upstash / Redis Cloud)

### 1. Redis Provisioning
1. Create a Redis database on [upstash.com](https://upstash.com) or [redis.io/cloud](https://redis.io/cloud).
2. Copy the **Native Redis Connection URL** (e.g. `rediss://default:password@host.upstash.io:6379`).
   > ⚠️ **Important**: Do NOT use the Upstash REST URL (`https://...`) or REST Token. KrishiLink requires the standard TCP connection string.

### 2. Environment Variable
```env
REDIS_URL=rediss://default:[YOUR_PASSWORD]@[HOST]:6379/0
```

---

## 📋 Phase 3: S3-Compatible Object Storage (AWS S3 / Cloudflare R2)

### 1. Bucket Configuration
1. Create a private bucket (e.g. `krishilink-evidence-prod`).
2. Keep **Block Public Access** ENABLED. KrishiLink generates secure, time-limited presigned URLs (`generate_presigned_url`) for client downloads.
3. Configure CORS on the bucket to permit `GET` / `PUT` from your production frontend domain:
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT"],
    "AllowedOrigins": ["https://krishilink.vercel.app"],
    "ExposeHeaders": ["ETag"]
  }
]
```

### 2. Environment Variables
```env
S3_ENDPOINT=https://[account-id].r2.cloudflarestorage.com  # Or leave empty for AWS standard
S3_BUCKET=krishilink-evidence-prod
S3_ACCESS_KEY=[YOUR_ACCESS_KEY]
S3_SECRET_KEY=[YOUR_SECRET_KEY]
```

---

## 📋 Phase 4: Render Backend & Background Worker Deployment

### 1. Web Service (FastAPI API Server)
- **Repository**: Connect `vedantkulkarni12007-cyber/KrishiLink`
- **Root Directory**: `backend`
- **Runtime**: `Docker`
- **Instance Type**: Starter / Standard (512MB+ RAM)
- **Health Check Path**: `/api/v1/health`
- **Docker Command**: Default from `backend/Dockerfile` (`uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`)
- **Environment Variables**:
  ```env
  ENV=production
  DEBUG=false
  DATABASE_URL=postgresql+psycopg://...
  REDIS_URL=rediss://...
  JWT_SECRET=[generate-64-character-random-secret]
  CORS_ORIGINS=https://krishilink.vercel.app,https://yourcustomdomain.com
  GOOGLE_CLIENT_ID=[your-google-client-id].apps.googleusercontent.com
  RESEND_API_KEY=re_123456789
  EMAIL_FROM=KrishiLink <noreply@krishilink.in>
  S3_ENDPOINT=...
  S3_BUCKET=...
  S3_ACCESS_KEY=...
  S3_SECRET_KEY=...
  ```

### 2. Background Worker (Celery Worker & Beat)
- **Type**: Background Worker
- **Root Directory**: `backend`
- **Runtime**: `Docker`
- **Docker Command**:
  ```bash
  celery -A app.workers.celery_app.celery_app worker --beat --loglevel=info
  ```
- **Environment Variables**: Same `DATABASE_URL`, `REDIS_URL`, `RESEND_API_KEY`, `S3_*` as the web service.

---

## 📋 Phase 5: Vercel Frontend Deployment

### 1. Vercel Configuration
1. Connect GitHub repository to [vercel.com](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Framework Preset: `Vite`.
4. Build Command: `npm run build`.
5. Output Directory: `dist`.

### 2. Frontend Environment Variables
| Variable | Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `https://krishilink-api.onrender.com` | Deployed FastAPI URL (NO trailing slash). |
| `VITE_DEMO_MODE` | `false` | Disables client mock fallback in production. |
| `VITE_GOOGLE_CLIENT_ID` | `[id].apps.googleusercontent.com` | Google Identity Services Client ID. |

---

## 📋 Phase 6: Google OAuth & Identity Services Setup

1. Open [Google Cloud Console](https://console.cloud.google.com) → **APIs & Services** → **Credentials**.
2. Create **OAuth 2.0 Client ID** (Web application).
3. Under **Authorized JavaScript origins**, add:
   - `https://krishilink.vercel.app`
   - `http://localhost:5173` (for local staging)
4. Copy the Client ID and set:
   - In Render: `GOOGLE_CLIENT_ID`
   - In Vercel: `VITE_GOOGLE_CLIENT_ID`

---

## 📋 Phase 7: Post-Deployment Verification Checklist

Verify the deployed system end-to-end over the public internet:

- [ ] **1. Public Health Check**: Navigate to `https://[your-backend].onrender.com/api/v1/health` → Verify `{ "success": true, "data": { "status": "healthy" } }`.
- [ ] **2. Frontend Asset Delivery**: Open `https://[your-frontend].vercel.app` → Confirm no 404s or console errors.
- [ ] **3. Real Registration**: Register a new farmer account using a live phone number and email.
- [ ] **4. Google Sign-In**: Click "Continue with Google" and verify instant JWT issuance and profile creation.
- [ ] **5. Produce Listing**: Create a lot from the farmer dashboard → Verify database persistence in Supabase.
- [ ] **6. 100pt Matchmaking**: Check buyer candidates and verify Haversine distance calculations.
- [ ] **7. Offer & Counter-Offer Negotiation**: Submit buyer offer, accept it, and verify reservation creation.
- [ ] **8. Escrow State Machine**: Progress the transaction through `CREATED` → `PAYMENT_CONFIRMED` → `DELIVERED`.
- [ ] **9. Evidence Upload**: Upload dispute evidence image → Verify presigned URL download from S3/R2.
- [ ] **10. Transactional Email**: Request password reset → Confirm delivery via Resend/SMTP logs.

---

## 🛠️ Common Failure Symptoms & Rollback Steps

| Symptom | Probable Cause | Action / Fix |
| :--- | :--- | :--- |
| **CORS Error in Browser Console** | `CORS_ORIGINS` in Render backend does not include the Vercel domain. | Update `CORS_ORIGINS` in Render settings to include exact Vercel URL and redeploy. |
| **500 Error on Matching / Geo Query** | PostGIS extension not enabled in Supabase. | In Supabase SQL editor, run `CREATE EXTENSION IF NOT EXISTS postgis;`. |
| **Rate Limit 500 / Worker Crash** | Invalid Redis URI schema (e.g. using Upstash REST token). | Ensure `REDIS_URL` uses `rediss://...` TCP connection string. |
| **Dispute Image 403 Forbidden** | S3 bucket CORS or bucket name mismatch. | Verify `S3_BUCKET` name and add Vercel domain to S3 bucket CORS policy. |
| **Google Sign-In "Origin not allowed"** | Vercel domain missing from Google Cloud Console. | Add Vercel URL to Authorized JavaScript Origins in Google Credentials dashboard. |
