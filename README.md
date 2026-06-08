# CA Compliance OS — Streamlit App

A multi-client compliance deadline dashboard for CA firms.
Built with Streamlit + SQLite. Deploy once → share link → any CA opens it in browser.

---

## ✅ FEATURES

| Feature | What it does |
|---|---|
| Multi-client dashboard | All clients, all deadlines on one screen with traffic light status |
| FY 2025-26 deadlines | 34 real deadlines auto-loaded per client (GST, TDS, ROC, ITR, Advance Tax) |
| Document status toggle | Mark each deadline: Pending / Docs Received / Filed |
| WhatsApp reminder | One-click draft message with deep link to open WhatsApp chat |
| CSV export | Download all deadlines as a spreadsheet |
| Add / delete clients | Full client management with GSTIN, phone, email |

---

## 🚀 DEPLOY ON STREAMLIT CLOUD (Recommended — Share a link)

### Step 1 — Push code to GitHub

1. Create a free account at https://github.com
2. Create a new **public** repository, e.g. `ca-compliance-os`
3. Upload these files to the repo:
   ```
   app.py
   requirements.txt
   .streamlit/config.toml
   ```
   You can drag-and-drop files on the GitHub website.

### Step 2 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository**: `your-username/ca-compliance-os`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. Click **"Deploy"**
6. Wait ~2 minutes for the build to finish.
7. You get a URL like: `https://your-username-ca-compliance-os.streamlit.app`

### Step 3 — Share the link

Send the URL to any CA. They open it in their browser — no installation needed.

> ⚠️ **Important note on data**: Streamlit Cloud uses an ephemeral filesystem.
> The SQLite database (`compliance.db`) resets when the app redeploys or restarts.
> For permanent storage, see the "Production Data Persistence" section below.

---

## 💻 RUN LOCALLY (Windows — VS Code)

### Step 1 — Install Python 3.11
Download from https://python.org — make sure to check "Add to PATH"

### Step 2 — Open the project folder in VS Code
```
File → Open Folder → select ca_compliance_streamlit
```

### Step 3 — Open terminal in VS Code (Ctrl + `)

### Step 4 — Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 5 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 6 — Run the app
```bash
streamlit run app.py
```

Browser opens automatically at http://localhost:8501

---

## 🗄️ PRODUCTION DATA PERSISTENCE

For a real CA firm where data must survive restarts, use one of these:

### Option A — Supabase (Free PostgreSQL, easiest)
1. Create free account at https://supabase.com
2. Create a project → go to Settings → Database → copy the connection string
3. Add `psycopg2-binary` and `sqlalchemy` to requirements.txt
4. Replace SQLite connections in app.py with SQLAlchemy + PostgreSQL URL
5. Store the DB URL in Streamlit Cloud Secrets (Settings → Secrets)

### Option B — PlanetScale / Railway
Same approach — free hosted MySQL/Postgres with a connection URL.

### Option C — Keep SQLite, use GitHub as backup
Add a "Export DB" button that lets the CA download the `.db` file daily.

---

## 📁 PROJECT STRUCTURE

```
ca_compliance_streamlit/
├── app.py                  ← Main Streamlit application
├── requirements.txt        ← Python dependencies
├── .streamlit/
│   └── config.toml         ← Theme and server settings
└── README.md               ← This file
```

---

## 📅 PRE-LOADED DEADLINES PER CLIENT (FY 2025-26)

| Type | Filings |
|---|---|
| GST GSTR-3B | Monthly (Apr 25 – Mar 26) — 12 deadlines |
| GST GSTR-1  | Monthly (Apr 25 – Mar 26) — 12 deadlines |
| TDS          | Quarterly — 4 deadlines |
| Advance Tax  | Quarterly — 4 deadlines |
| ITR          | Annual — 1 deadline |
| ROC          | Annual — 1 deadline |
| **Total**    | **34 deadlines per client** |

---

## 🆘 TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` again |
| App shows blank page | Check terminal for errors; try `streamlit run app.py --server.port 8502` |
| WhatsApp link not opening | Ensure phone number is 10 digits (no +91 prefix) |
| Data lost after redeploy | Expected on free Streamlit Cloud — upgrade to persistent DB (see above) |
