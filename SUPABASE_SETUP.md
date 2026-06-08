# Supabase Setup — Step by Step (10 minutes)

## Step 1 — Create Free Supabase Account
1. Go to https://supabase.com
2. Click "Start your project" → Sign up with GitHub
3. Click "New Project"
   - Name: `ca-compliance-os`
   - Password: (create a strong password, save it)
   - Region: **Southeast Asia (Singapore)** ← closest to India
4. Wait 2 minutes for project to spin up

## Step 2 — Create Tables
1. In Supabase dashboard → click **SQL Editor** (left sidebar)
2. Click **New Query**
3. Paste this SQL and click **Run**:

```sql
-- Clients table
CREATE TABLE clients (
  id      BIGSERIAL PRIMARY KEY,
  name    TEXT NOT NULL,
  phone   TEXT,
  email   TEXT,
  gstin   TEXT,
  created DATE DEFAULT CURRENT_DATE
);

-- Deadlines table
CREATE TABLE deadlines (
  id              BIGSERIAL PRIMARY KEY,
  client_id       BIGINT NOT NULL REFERENCES clients(id),
  compliance_type TEXT NOT NULL,
  category        TEXT NOT NULL,
  due_date        DATE NOT NULL,
  status          TEXT DEFAULT 'upcoming',
  doc_status      TEXT DEFAULT 'pending'
);

-- Index for fast client lookups
CREATE INDEX idx_deadlines_client ON deadlines(client_id);
```

4. You should see "Success. No rows returned"

## Step 3 — Get Your API Keys
1. In Supabase dashboard → click **Settings** (gear icon, bottom left)
2. Click **API**
3. Copy these two values:
   - **Project URL** → looks like `https://xxxxxxxxxxxx.supabase.co`
   - **anon public key** → long string starting with `eyJ...`

## Step 4 — Add Keys to Streamlit Cloud
1. Go to your Streamlit Cloud app → click the **3 dots menu** → **Settings**
2. Click **Secrets**
3. Paste this (replace with your actual values):

```toml
SUPABASE_URL = "https://xxxxxxxxxxxx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

4. Click **Save** → app will restart automatically

## Step 5 — Verify It's Working
- Open your Streamlit app
- You should see "☁️ Supabase (Cloud)" in the sidebar (bottom)
- Add a test client → check Supabase dashboard → Table Editor → clients table

## That's it! Your data now persists forever. ✅

---

## How to Update a Deadline Date (When Govt Extends)
1. Go to Supabase → Table Editor → deadlines
2. Find the deadline (filter by compliance_type)
3. Click the cell → edit the due_date
4. Press Enter → saved instantly, all CAs see the update

---

## Free Tier Limits (More than enough for MVP)
| Resource | Free Limit | You'll Use |
|---|---|---|
| Rows | 500MB storage | ~1000 clients = ~35,000 rows = tiny |
| API requests | 50,000/day | Fine for 10-50 users |
| Bandwidth | 5GB/month | Fine |

