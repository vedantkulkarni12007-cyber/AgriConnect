# 🌿 KrishiLink

**"Better Prices. Better Buyers. Better Decisions."**

KrishiLink is a full-stack agricultural market platform built for the Smart India Hackathon 2026. It helps farmers discover crop prices, find verified buyers, list produce, track sales, and maintain transparent transaction records.

---

## 🚀 Quick Start (Demo Mode — No accounts needed!)

### 1. Start the Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs at: **http://localhost:5000**

Test it: Open http://localhost:5000/api/health in your browser

### 2. Start the Frontend (React)

Open a NEW terminal window:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: **http://localhost:5173**

### 3. Open the app

Go to **http://localhost:5173** in your browser.

Click **"Continue as Farmer"** on the login page — no account needed!

---

## 📁 Project Structure

```
KrishiLink/
├── frontend/          React + Vite + Tailwind CSS
│   └── src/
│       ├── pages/     All page components
│       ├── components/ Reusable UI pieces
│       ├── layouts/   Page wrappers (nav, sidebar)
│       ├── services/  API calls to backend
│       ├── hooks/     Auth, Language contexts
│       ├── data/      Demo data (no backend needed)
│       └── utils/     Translations, helpers
│
├── backend/           Python Flask REST API
│   ├── app.py         Main application entry
│   ├── config.py      Environment config
│   ├── routes/        API endpoints
│   ├── services/      Business logic
│   └── data/          Demo data for API
│
├── database/          Supabase SQL
│   ├── schema.sql     Create all tables
│   └── seed.sql       Sample data
│
├── docs/              Documentation
│   ├── BEGINNER_GUIDE.md
│   ├── TEAM_GUIDE.md
│   └── API_GUIDE.md
│
└── README.md          This file
```

---

## 🛠️ Technology Stack

| Layer    | Technology                    | Purpose               |
|----------|-------------------------------|-----------------------|
| Frontend | React 18 + Vite               | UI framework          |
| Styling  | Tailwind CSS                  | Design system         |
| Icons    | Lucide React                  | Icon library          |
| Charts   | Recharts                      | Price trend charts    |
| Maps     | React Leaflet + OpenStreetMap | Interactive maps      |
| Backend  | Python 3.13 + Flask           | REST API server       |
| Database | Supabase (PostgreSQL)         | Data storage          |
| CORS     | flask-cors                    | Frontend ↔ Backend    |

---

## 🎭 Demo vs Live Mode

### Demo Mode (default)
- Works immediately — no accounts, no API keys
- Uses realistic sample data for Maharashtra
- All features work: prices, matching, offers, transactions

### Live Mode (future)
- Connect Supabase for real authentication and database
- Replace demo data with real mandi API data
- See `docs/ARCHITECTURE.md` for integration points

---

## 🌐 API Endpoints

| Method | Endpoint                | Description               |
|--------|-------------------------|---------------------------|
| GET    | /api/health             | Server status check       |
| GET    | /api/prices             | All current crop prices   |
| GET    | /api/prices/<crop>      | Prices for specific crop  |
| GET    | /api/trends/<crop>      | 7-day trend analysis      |
| GET    | /api/lots               | All produce listings      |
| POST   | /api/lots               | Create new listing        |
| POST   | /api/match              | Find matching buyers      |
| GET    | /api/offers             | All offers                |
| POST   | /api/offers             | Make an offer             |
| PUT    | /api/offers/<id>        | Accept/reject offer       |
| GET    | /api/transactions       | All transactions          |
| GET    | /api/transactions/<id>  | Single transaction        |
| GET    | /api/grievances         | All grievances            |
| POST   | /api/grievances         | File a grievance          |

---

## 🗄️ Database Setup (Supabase)

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to **SQL Editor** in the left sidebar
4. Paste contents of `database/schema.sql` → click **Run**
5. Paste contents of `database/seed.sql` → click **Run**
6. Get your project URL and anon key from **Settings > API**
7. Add to `backend/.env` and `frontend/.env`

---

## 🔐 Environment Variables

### backend/.env
```
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_service_key_here
FRONTEND_URL=http://localhost:5173
```

### frontend/.env
```
VITE_API_BASE_URL=http://localhost:5000
VITE_DEMO_MODE=true
VITE_SUPABASE_URL=your_supabase_url_here
VITE_SUPABASE_ANON_KEY=your_anon_key_here
```

> ⚠️ **Never commit .env files to Git!** They are in .gitignore.

---

## 📱 Pages & Routes

| Route                | Description                        | Login Required |
|----------------------|------------------------------------|----------------|
| /                    | Landing page                       | No             |
| /login               | Login with demo buttons            | No             |
| /register            | Create account (farmer/buyer/fpo)  | No             |
| /prices              | Market price comparison + charts   | No             |
| /map                 | Interactive mandi/buyer/storage map| No             |
| /farmer/dashboard    | Farmer overview + trend chart      | Yes (Farmer)   |
| /sell                | Create produce listing             | Yes (Farmer)   |
| /matches             | Rule-based buyer matching          | Yes (Farmer)   |
| /offers              | Manage buyer offers                | Yes (Farmer)   |
| /transactions        | Transaction timeline               | Yes            |
| /grievances          | File and track disputes            | Yes            |
| /buyer/dashboard     | Browse lots, make offers           | Yes (Buyer)    |
| /fpo/dashboard       | Aggregated lots, FPO overview      | Yes (FPO)      |

---

## 👥 Team Collaboration Guide

Each team member can own one area:

| Area           | Files to work on                          |
|----------------|-------------------------------------------|
| Frontend UI    | `frontend/src/pages/`, `components/`      |
| Backend APIs   | `backend/routes/`, `services/`            |
| Price Data     | `backend/data/demo_data.py`               |
| Supabase/Auth  | `database/`, `frontend/src/hooks/useAuth` |
| Maps/Notifs    | `MapPage.jsx`, notifications              |
| QA/Deployment  | Testing, GitHub PRs                       |

---

## 🔮 Future Integrations

Prepared integration points (no implementation needed for MVP):

- **Agmarknet/eNAM**: Replace `price_service.py` demo data provider
- **Supabase Auth**: Uncomment in `useAuth.jsx`
- **WhatsApp/SMS**: Add to notification service
- **Payment Gateway**: Integrate in transaction flow
- **AI/ML Price Forecast**: Add as optional module in `trend_service.py`

---

## 📚 Documentation

- [`docs/BEGINNER_GUIDE.md`](docs/BEGINNER_GUIDE.md) — What is React? What is Flask? etc.
- [`docs/TEAM_GUIDE.md`](docs/TEAM_GUIDE.md) — Git workflow for teammates
- [`docs/API_GUIDE.md`](docs/API_GUIDE.md) — Full API documentation
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — System architecture

---

## 🏆 Built For

**Smart India Hackathon 2024**
Problem Statement: Strengthening Market Linkages & Price Discovery for Farmers

---

*KrishiLink — Empowering farmers with transparent market information.*
