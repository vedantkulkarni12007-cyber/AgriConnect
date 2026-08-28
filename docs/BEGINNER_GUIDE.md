# 📚 Beginner's Guide to KrishiLink

Welcome to the team! This guide explains the technology we're using in simple language.
You do NOT need to understand all of this to contribute — but reading it will help!

---

## 🤔 What is Frontend and Backend?

Think of a restaurant:
- **Frontend** = The dining room. This is what customers (users) see. Tables, menu, decor.
- **Backend** = The kitchen. This is where the actual cooking (data processing) happens.
- **API** = The waiter. It takes orders from the dining room and brings food from the kitchen.

In KrishiLink:
- **Frontend** (React) = The website you see in your browser
- **Backend** (Flask) = The Python server that processes requests
- **API** = The routes that connect them (`/api/prices`, `/api/lots`, etc.)

---

## ⚛️ What is React?

React is a JavaScript library for building user interfaces.

Instead of writing HTML directly, you write **components** — reusable pieces of UI.

Example:
```jsx
// This is a React component
function PriceCard({ crop, price }) {
  return (
    <div className="card">
      <h2>{crop}</h2>
      <p>₹{price} per quintal</p>
    </div>
  );
}

// Use it like this:
<PriceCard crop="Onion" price={1800} />
```

Every page in KrishiLink (`LandingPage.jsx`, `FarmerDashboard.jsx`, etc.) is a React component.

---

## ⚡ What is Vite?

Vite is a tool that:
- Starts a development server quickly
- Reloads the page automatically when you save a file
- Builds the final website for deployment

You run it with: `npm run dev`

---

## 🐍 What is Flask?

Flask is a Python web framework.

It lets you write API routes:
```python
@app.route('/api/prices')
def get_prices():
    return {"success": True, "data": prices}
```

When the frontend calls `/api/prices`, Flask runs this function and returns the data.

---

## 🗄️ What is a Database?

A database is where we store information permanently.
When the app restarts, the data is still there.

We use **Supabase** which gives us a **PostgreSQL** database in the cloud.

Think of it as a spreadsheet with multiple sheets (tables):
- `users` table — stores farmer/buyer/FPO accounts
- `prices` table — stores daily mandi prices
- `lots` table — stores produce listings
- `offers` table — stores buyer offers

---

## ☁️ What is Supabase?

Supabase is a platform that gives us:
1. A **PostgreSQL database** (to store all data)
2. **Authentication** (login/register users securely)
3. A **dashboard** to view and edit data visually

Website: [supabase.com](https://supabase.com)

Free tier is enough for our project!

---

## 🔑 What is an Environment Variable?

An environment variable is a setting that changes based on where you run the app.

Instead of hardcoding secrets in code:
```python
# BAD — never do this!
supabase_key = "eyJhbGciOiJIUzI1NiJ9.actual_secret_key_here"
```

We use environment variables:
```python
# GOOD — secret stays outside code
supabase_key = os.environ.get("SUPABASE_KEY")
```

We store these in a `.env` file that is NEVER committed to Git.

---

## 🌿 What is Git?

Git is a version control system. It tracks changes to your code.

Think of it like "save points" in a video game:
- **commit** = save a checkpoint
- **branch** = work on a parallel save file
- **push** = upload your save to GitHub
- **pull** = download the latest save

Basic flow:
```bash
git pull              # Get latest code from GitHub
git checkout -b my-feature  # Start working on something new
# ... make changes ...
git add .             # Select files to save
git commit -m "Added price chart"  # Save checkpoint
git push              # Upload to GitHub
```

---

## 🔗 How Does Frontend Talk to Backend?

The frontend uses `fetch` (or our `api.js` service) to send HTTP requests:

```javascript
// Frontend calls the backend
const response = await fetch('http://localhost:5000/api/prices');
const data = await response.json();
// data.data contains the list of prices
```

The backend receives the request and returns JSON:
```python
# Backend returns data
@app.route('/api/prices')
def prices():
    return jsonify({"success": True, "data": DEMO_PRICES})
```

---

## 📁 File Structure Quick Reference

```
frontend/src/
├── pages/      ← Each file = one page (LandingPage, FarmerDashboard, etc.)
├── components/ ← Reusable UI (Navbar, Footer, Badges, etc.)
├── layouts/    ← Page wrappers (sidebar, demo banner)
├── services/   ← api.js = all backend calls go here
├── hooks/      ← useAuth.jsx = login state, useLanguage.jsx = language
├── data/       ← demoData.js = sample data when backend is off
└── utils/      ← translations.js = English/Marathi/Hindi text

backend/
├── app.py      ← Entry point, starts Flask server
├── config.py   ← Reads .env variables
├── routes/     ← API endpoints (prices.py, lots.py, etc.)
├── services/   ← Business logic (trend_service.py, matching_service.py)
└── data/       ← demo_data.py = sample data for API
```

---

## 🆘 I'm Stuck — What Do I Do?

1. Read the error message carefully
2. Google the exact error message
3. Check the README.md
4. Ask a teammate
5. Ask the AI assistant (this very tool!)

---

*Happy coding! You've got this. 🌾*
