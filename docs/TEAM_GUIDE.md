# 👥 Team Git Guide for KrishiLink

This guide explains how all 6 team members can work on the project together using Git and GitHub.

---

## 🔑 First Time Setup (Do this ONCE)

### 1. Install Git
Download from: https://git-scm.com/download/win
During install, choose "Git from command line and 3rd-party software"

### 2. Configure Git (your name and email)
```bash
git config --global user.name "Your Name"
git config --global user.email "yourname@email.com"
```

### 3. Clone the repository
```bash
git clone https://github.com/your-team/krishilink.git
cd krishilink
```

---

## 📅 Daily Workflow

### Every morning before you start working:
```bash
git pull origin main
```
This downloads the latest code so you're not working on old files.

---

## 🌿 Creating a Feature Branch

Never work directly on `main`. Always create a branch for your work.

```bash
# Create a new branch
git checkout -b feature/price-dashboard

# Good branch name examples:
# feature/price-dashboard
# feature/farmer-login
# fix/map-not-loading
# feature/marathi-translations
```

---

## 💾 Saving Your Work (Committing)

```bash
# Step 1: See what files you changed
git status

# Step 2: Add files you want to save
git add .                          # Add all changed files
git add frontend/src/pages/        # Or add just a folder

# Step 3: Commit with a descriptive message
git commit -m "Add 15-day price trend chart to farmer dashboard"

# Good commit messages:
# ✓ "Add price comparison table to prices page"
# ✓ "Fix mobile layout in offers page"
# ✓ "Add Marathi translations for dashboard"
# ✗ "fixed stuff" (too vague!)
# ✗ "asdf" (meaningless!)
```

---

## ⬆️ Uploading Your Work (Pushing)

```bash
git push origin feature/price-dashboard
```

---

## 🔀 Creating a Pull Request (PR)

After pushing, go to GitHub and:
1. You'll see a green button: **"Compare & pull request"** — click it
2. Write a clear description of what you changed
3. Ask a teammate to review it
4. After approval, click **"Merge pull request"**

---

## ⬇️ Getting Other People's Changes

```bash
# Switch to main
git checkout main

# Get the latest merged code
git pull origin main

# Switch back to your branch
git checkout feature/price-dashboard

# Update your branch with latest main
git merge main
```

---

## ⚠️ Resolving Conflicts

A conflict happens when two people changed the same line of code.
Git will mark the conflict like this:

```
<<<<<<< HEAD (your changes)
const price = 1800;
=======
const price = 1750;
>>>>>>> main (their changes)
```

How to fix:
1. Open the file in VS Code
2. Choose which version is correct (or combine them)
3. Delete the `<<<<<<<`, `=======`, `>>>>>>>` lines
4. Save the file
5. `git add .` and `git commit -m "Resolve merge conflict"`

---

## 📋 Team Area Suggestions

| Team Member | Branch Naming          | Area                            |
|-------------|------------------------|---------------------------------|
| Member 1    | `feature/ui-pages`     | Frontend pages (LandingPage, etc.) |
| Member 2    | `feature/components`   | Reusable components, styling    |
| Member 3    | `feature/backend-api`  | Flask routes, services          |
| Member 4    | `feature/price-data`   | Demo data, trend calculations   |
| Member 5    | `feature/supabase`     | Database, authentication        |
| Member 6    | `feature/maps-notifs`  | Map page, notification system   |

---

## 🚫 NEVER do these:

```bash
# NEVER commit .env files (they contain secrets!)
git add .env   # ❌ NO!

# NEVER force push to main
git push --force origin main  # ❌ NO!

# NEVER commit node_modules
git add node_modules/  # ❌ NO! (covered by .gitignore)
```

---

## ✅ Quick Reference

| Command | What it does |
|---------|-------------|
| `git pull` | Download latest code |
| `git checkout -b feature/name` | Create new branch |
| `git status` | See changed files |
| `git add .` | Stage all changes |
| `git commit -m "message"` | Save checkpoint |
| `git push origin branch-name` | Upload to GitHub |
| `git checkout main` | Switch to main branch |
| `git merge main` | Update branch with latest main |

---

*Remember: Small, frequent commits are better than one massive commit!*
