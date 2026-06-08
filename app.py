import streamlit as st
import os, hashlib, hmac, csv, io
from datetime import datetime, date, timedelta
import urllib.parse

# ── Supabase ──────────────────────────────────────────────────────────────────
try:
    from supabase import create_client
    _url = os.environ.get("SUPABASE_URL") or st.secrets.get("SUPABASE_URL","")
    _key = os.environ.get("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY","")
    USE_SUPABASE = bool(_url and _key)
    if USE_SUPABASE:
        supabase = create_client(_url, _key)
except Exception:
    USE_SUPABASE = False

if not USE_SUPABASE:
    import sqlite3

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="CA Compliance OS", page_icon="📋",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f4f6fb; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1b6e 0%, #1a3a8f 50%, #1565c0 100%) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #fff !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    transition: background 0.2s !important;
    display: block !important;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.1) !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: rgba(255,255,255,0.7) !important; font-size: 12px !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 16px;
    padding: 22px 24px;
    border: 1px solid rgba(26,35,126,0.06);
    box-shadow: 0 4px 20px rgba(26,35,126,0.08);
    transition: transform 0.2s, box-shadow 0.2s;
    position: relative;
    overflow: hidden;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 30px rgba(26,35,126,0.14);
}
[data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #1a237e, #1565c0);
}
[data-testid="stMetricLabel"] { font-size: 12px !important; font-weight: 600 !important; color: #888 !important; text-transform: uppercase; letter-spacing: 0.5px; }
[data-testid="stMetricValue"] { font-size: 36px !important; font-weight: 800 !important; color: #1a237e !important; }

/* ── Client cards ── */
.ca-card {
    background: #fff;
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 12px;
    border: 1px solid rgba(0,0,0,0.06);
    border-left: 5px solid #1a237e;
    box-shadow: 0 2px 16px rgba(26,35,126,0.06);
    transition: transform 0.18s ease, box-shadow 0.18s ease;
    animation: fadeSlideIn 0.4s ease both;
}
.ca-card:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(26,35,126,0.13); }
.ca-card.red   { border-left-color: #e53935; }
.ca-card.amber { border-left-color: #fb8c00; }
.ca-card.green { border-left-color: #43a047; }
.ca-card-name  { font-size: 16px; font-weight: 700; color: #1a237e; margin-bottom: 5px; }
.ca-card-meta  { font-size: 12px; color: #888; }

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 3px 11px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.2px;
}
.badge.red    { background: #fdecea; color: #c62828; }
.badge.amber  { background: #fff8e1; color: #e65100; }
.badge.green  { background: #e8f5e9; color: #2e7d32; }
.badge.blue   { background: #e3f2fd; color: #1565c0; }

/* ── Section headers ── */
.page-header {
    background: linear-gradient(135deg, #1a237e 0%, #1565c0 100%);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    color: #fff;
    position: relative;
    overflow: hidden;
}
.page-header::after {
    content: '';
    position: absolute;
    right: -20px; top: -20px;
    width: 120px; height: 120px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.page-header::before {
    content: '';
    position: absolute;
    right: 60px; top: 30px;
    width: 60px; height: 60px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.page-title { font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.page-sub   { font-size: 13px; color: rgba(255,255,255,0.75); }

/* ── WhatsApp box ── */
.wa-box {
    background: linear-gradient(135deg, #f1f8e9, #e8f5e9);
    border-left: 4px solid #43a047;
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 13px;
    white-space: pre-wrap;
    line-height: 1.9;
    color: #1b5e20;
    font-family: 'Courier New', monospace;
    margin-top: 10px;
    box-shadow: 0 2px 12px rgba(67,160,71,0.1);
}

/* ── Log rows ── */
.log-row {
    background: #fff;
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 6px;
    border-left: 4px solid #1a237e;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
    animation: fadeSlideIn 0.3s ease both;
    transition: transform 0.15s;
}
.log-row:hover { transform: translateX(3px); }
.log-row.login  { border-left-color: #43a047; }
.log-row.wa     { border-left-color: #25d366; }
.log-row.update { border-left-color: #fb8c00; }
.log-row.add    { border-left-color: #1565c0; }

/* ── Info banner ── */
.info-banner {
    background: linear-gradient(135deg, #e8eaf6, #e3f2fd);
    border-radius: 12px;
    padding: 12px 18px;
    color: #283593;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 16px;
    border: 1px solid rgba(26,35,126,0.1);
}

/* ── Alert ── */
.alert-box {
    background: linear-gradient(135deg, #fff8e1, #fff3e0);
    border: 1px solid #ffcc02;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 12px;
    color: #e65100;
    margin-bottom: 16px;
    font-weight: 500;
}

/* ── Admin stat cards ── */
.stat-card {
    background: #fff;
    border-radius: 14px;
    padding: 18px 20px;
    text-align: center;
    box-shadow: 0 3px 16px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.2s;
}
.stat-card:hover { transform: translateY(-2px); }
.stat-val   { font-size: 28px; font-weight: 800; color: #1a237e; }
.stat-label { font-size: 11px; color: #888; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; margin-top: 2px; }

/* ── Forms ── */
div[data-testid="stForm"] {
    background: #fff;
    padding: 28px;
    border-radius: 18px;
    border: 1px solid rgba(26,35,126,0.08);
    box-shadow: 0 4px 24px rgba(26,35,126,0.07);
}
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e0e4f0 !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1a237e !important;
    box-shadow: 0 0 0 3px rgba(26,35,126,0.1) !important;
}
.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #e0e4f0 !important;
}

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    transition: all 0.2s !important;
    border: none !important;
}
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(26,35,126,0.25) !important; }
.stButton > button[kind="primary"] { background: linear-gradient(135deg, #1a237e, #1565c0) !important; }
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #1a237e, #1565c0) !important;
    color: #fff !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    width: 100% !important;
    padding: 12px !important;
    font-size: 15px !important;
    transition: all 0.2s !important;
}
.stFormSubmitButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(26,35,126,0.35) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"] {
    background: #fff !important;
    border-radius: 14px !important;
    border: 1px solid rgba(26,35,126,0.08) !important;
    box-shadow: 0 2px 12px rgba(26,35,126,0.05) !important;
    margin-bottom: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 14px 18px !important;
    background: linear-gradient(135deg, #f8f9ff, #f0f4ff) !important;
}
[data-testid="stExpander"] summary:hover { background: linear-gradient(135deg, #eef1ff, #e8edff) !important; }

/* ── Deadline table rows ── */
.dl-row {
    background: #fff;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 5px;
    border: 1px solid rgba(0,0,0,0.05);
    display: grid;
    grid-template-columns: 3fr 1.5fr 1.5fr 2fr;
    align-items: center;
    font-size: 13px;
    transition: background 0.15s;
}
.dl-row:hover { background: #f8f9ff; }
.dl-row.overdue  { border-left: 3px solid #e53935; }
.dl-row.upcoming { border-left: 3px solid #fb8c00; }
.dl-row.filed    { border-left: 3px solid #43a047; }

/* ── Animations ── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.6; }
}
.animate-in { animation: fadeSlideIn 0.4s ease both; }

/* ── Login page ── */
.login-hero {
    text-align: center;
    padding: 40px 20px 20px;
    animation: fadeSlideIn 0.5s ease;
}
.login-logo {
    font-size: 52px;
    margin-bottom: 12px;
    animation: fadeSlideIn 0.5s ease 0.1s both;
}
.login-title {
    font-size: 28px;
    font-weight: 800;
    color: #1a237e;
    margin-bottom: 6px;
    animation: fadeSlideIn 0.5s ease 0.2s both;
}
.login-sub {
    font-size: 14px;
    color: #888;
    animation: fadeSlideIn 0.5s ease 0.3s both;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #f0f2f6; }
::-webkit-scrollbar-thumb { background: #c5cae9; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #9fa8da; }

/* ── Divider ── */
hr { border: none; border-top: 1px solid #eef0f8; margin: 16px 0; }

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    border-radius: 8px !important;
    border: 1.5px solid #1a237e !important;
    color: #1a237e !important;
    background: #fff !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #1a237e !important;
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATABASE LAYER — SQLite fallback
# ══════════════════════════════════════════════════════════════════════════════
DB_PATH = "compliance.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role     TEXT DEFAULT 'ca',
            firm     TEXT,
            phone    TEXT,
            active   INTEGER DEFAULT 1,
            created  TEXT
        );
        CREATE TABLE IF NOT EXISTS clients (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            name      TEXT NOT NULL,
            phone     TEXT, email TEXT, gstin TEXT, created TEXT
        );
        CREATE TABLE IF NOT EXISTS deadlines (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id       INTEGER NOT NULL,
            compliance_type TEXT NOT NULL,
            category        TEXT NOT NULL,
            due_date        TEXT NOT NULL,
            status          TEXT DEFAULT 'upcoming',
            doc_status      TEXT DEFAULT 'pending'
        );
        CREATE TABLE IF NOT EXISTS usage_logs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER,
            username   TEXT,
            action     TEXT,
            detail     TEXT,
            logged_at  TEXT
        );
    """)
    # seed admin if not exists
    cur = conn.execute("SELECT id FROM users WHERE username='admin'")
    if not cur.fetchone():
        conn.execute("""INSERT INTO users(username,password,role,firm,active,created)
            VALUES('admin',?,'admin','CA Compliance OS',1,date('now'))""",
            (hash_pw("admin123"),))
    conn.commit(); conn.close()

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

if not USE_SUPABASE:
    init_db()

# ══════════════════════════════════════════════════════════════════════════════
# DEADLINE MASTER DATA — FY 2025-26 + FY 2026-27
# Source: GSTN, CBIC, Income Tax India, MCA
# To update a date: change the date string below and redeploy
# ══════════════════════════════════════════════════════════════════════════════

ALL_DEADLINES = [
    # ── FY 2025-26 ────────────────────────────────────────────────────────────
    ("GST GSTR-3B (Apr 25)","GST","2025-05-20","2025-26"),
    ("GST GSTR-3B (May 25)","GST","2025-06-20","2025-26"),
    ("GST GSTR-3B (Jun 25)","GST","2025-07-20","2025-26"),
    ("GST GSTR-3B (Jul 25)","GST","2025-08-20","2025-26"),
    ("GST GSTR-3B (Aug 25)","GST","2025-09-20","2025-26"),
    ("GST GSTR-3B (Sep 25)","GST","2025-10-20","2025-26"),
    ("GST GSTR-3B (Oct 25)","GST","2025-11-20","2025-26"),
    ("GST GSTR-3B (Nov 25)","GST","2025-12-20","2025-26"),
    ("GST GSTR-3B (Dec 25)","GST","2026-01-20","2025-26"),
    ("GST GSTR-3B (Jan 26)","GST","2026-02-20","2025-26"),
    ("GST GSTR-3B (Feb 26)","GST","2026-03-20","2025-26"),
    ("GST GSTR-3B (Mar 26)","GST","2026-04-20","2025-26"),
    ("GSTR-1 (Apr 25)","GST","2025-05-11","2025-26"),
    ("GSTR-1 (May 25)","GST","2025-06-11","2025-26"),
    ("GSTR-1 (Jun 25)","GST","2025-07-11","2025-26"),
    ("GSTR-1 (Jul 25)","GST","2025-08-11","2025-26"),
    ("GSTR-1 (Aug 25)","GST","2025-09-11","2025-26"),
    ("GSTR-1 (Sep 25)","GST","2025-10-11","2025-26"),
    ("GSTR-1 (Oct 25)","GST","2025-11-11","2025-26"),
    ("GSTR-1 (Nov 25)","GST","2025-12-11","2025-26"),
    ("GSTR-1 (Dec 25)","GST","2026-01-11","2025-26"),
    ("GSTR-1 (Jan 26)","GST","2026-02-11","2025-26"),
    ("GSTR-1 (Feb 26)","GST","2026-03-11","2025-26"),
    ("GSTR-1 (Mar 26)","GST","2026-04-11","2025-26"),
    ("TDS Q1 (Apr-Jun 25)","TDS","2025-07-31","2025-26"),
    ("TDS Q2 (Jul-Sep 25)","TDS","2025-10-31","2025-26"),
    ("TDS Q3 (Oct-Dec 25)","TDS","2026-01-31","2025-26"),
    ("TDS Q4 (Jan-Mar 26)","TDS","2026-05-31","2025-26"),
    ("ROC Annual Return 25-26","ROC","2025-11-29","2025-26"),
    ("Income Tax Return 25-26","ITR","2025-10-31","2025-26"),
    ("Advance Tax Q1 25-26","ADV","2025-06-15","2025-26"),
    ("Advance Tax Q2 25-26","ADV","2025-09-15","2025-26"),
    ("Advance Tax Q3 25-26","ADV","2025-12-15","2025-26"),
    ("Advance Tax Q4 25-26","ADV","2026-03-15","2025-26"),
    # ── FY 2026-27 ────────────────────────────────────────────────────────────
    ("GST GSTR-3B (Apr 26)","GST","2026-05-20","2026-27"),
    ("GST GSTR-3B (May 26)","GST","2026-06-20","2026-27"),
    ("GST GSTR-3B (Jun 26)","GST","2026-07-20","2026-27"),
    ("GST GSTR-3B (Jul 26)","GST","2026-08-20","2026-27"),
    ("GST GSTR-3B (Aug 26)","GST","2026-09-20","2026-27"),
    ("GST GSTR-3B (Sep 26)","GST","2026-10-20","2026-27"),
    ("GST GSTR-3B (Oct 26)","GST","2026-11-20","2026-27"),
    ("GST GSTR-3B (Nov 26)","GST","2026-12-20","2026-27"),
    ("GST GSTR-3B (Dec 26)","GST","2027-01-20","2026-27"),
    ("GST GSTR-3B (Jan 27)","GST","2027-02-20","2026-27"),
    ("GST GSTR-3B (Feb 27)","GST","2027-03-20","2026-27"),
    ("GST GSTR-3B (Mar 27)","GST","2027-04-20","2026-27"),
    ("GSTR-1 (Apr 26)","GST","2026-05-11","2026-27"),
    ("GSTR-1 (May 26)","GST","2026-06-11","2026-27"),
    ("GSTR-1 (Jun 26)","GST","2026-07-11","2026-27"),
    ("GSTR-1 (Jul 26)","GST","2026-08-11","2026-27"),
    ("GSTR-1 (Aug 26)","GST","2026-09-11","2026-27"),
    ("GSTR-1 (Sep 26)","GST","2026-10-11","2026-27"),
    ("GSTR-1 (Oct 26)","GST","2026-11-11","2026-27"),
    ("GSTR-1 (Nov 26)","GST","2026-12-11","2026-27"),
    ("GSTR-1 (Dec 26)","GST","2027-01-11","2026-27"),
    ("GSTR-1 (Jan 27)","GST","2027-02-11","2026-27"),
    ("GSTR-1 (Feb 27)","GST","2027-03-11","2026-27"),
    ("GSTR-1 (Mar 27)","GST","2027-04-11","2026-27"),
    ("TDS Q1 (Apr-Jun 26)","TDS","2026-07-31","2026-27"),
    ("TDS Q2 (Jul-Sep 26)","TDS","2026-10-31","2026-27"),
    ("TDS Q3 (Oct-Dec 26)","TDS","2027-01-31","2026-27"),
    ("TDS Q4 (Jan-Mar 27)","TDS","2027-05-31","2026-27"),
    ("ROC Annual Return 26-27","ROC","2026-11-29","2026-27"),
    ("Income Tax Return 26-27","ITR","2026-10-31","2026-27"),
    ("Advance Tax Q1 26-27","ADV","2026-06-15","2026-27"),
    ("Advance Tax Q2 26-27","ADV","2026-09-15","2026-27"),
    ("Advance Tax Q3 26-27","ADV","2026-12-15","2026-27"),
    ("Advance Tax Q4 26-27","ADV","2027-03-15","2026-27"),
]

# Alias for UI labels showing count
DEADLINES_FY2526 = ALL_DEADLINES


def compute_status(due_date_str):
    """
    Smart status logic:
    - Dates before the 1st of the CURRENT month → overdue
    - Dates from this month onward → upcoming
    - Once CA marks doc_status as 'filed' → that overrides to 'filed'
    This means a new client added in June 2026 sees Apr/May as overdue
    and June onward as upcoming — which is correct.
    """
    today = date.today()
    due   = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    first_of_month = today.replace(day=1)
    if due < first_of_month:
        return "overdue"
    return "upcoming"

# ══════════════════════════════════════════════════════════════════════════════
# DB HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def db_auth(username, password):
    pw = hash_pw(password)
    if USE_SUPABASE:
        r = supabase.table("users").select("*").eq("username",username).eq("password",pw).eq("active",True).execute()
        return r.data[0] if r.data else None
    else:
        conn=get_conn()
        r=conn.execute("SELECT * FROM users WHERE username=? AND password=? AND active=1",(username,pw)).fetchone()
        conn.close()
        return dict(r) if r else None

def log_action(user_id, username, action, detail=""):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if USE_SUPABASE:
        supabase.table("usage_logs").insert({"user_id":user_id,"username":username,
            "action":action,"detail":detail,"logged_at":ts}).execute()
    else:
        conn=get_conn()
        conn.execute("INSERT INTO usage_logs(user_id,username,action,detail,logged_at) VALUES(?,?,?,?,?)",
            (user_id,username,action,detail,ts))
        conn.commit(); conn.close()

def db_get_users():
    if USE_SUPABASE:
        r=supabase.table("users").select("*").neq("role","admin").order("firm").execute()
        return r.data or []
    else:
        conn=get_conn()
        rows=conn.execute("SELECT * FROM users WHERE role!='admin' ORDER BY firm").fetchall()
        conn.close()
        return [dict(r) for r in rows]

def db_add_user(username,password,firm,phone):
    ts=str(date.today())
    if USE_SUPABASE:
        supabase.table("users").insert({"username":username,"password":hash_pw(password),
            "role":"ca","firm":firm,"phone":phone,"active":True,"created":ts}).execute()
    else:
        conn=get_conn()
        conn.execute("INSERT INTO users(username,password,role,firm,phone,active,created) VALUES(?,?,?,?,?,1,?)",
            (username,hash_pw(password),"ca",firm,phone,ts))
        conn.commit(); conn.close()

def db_toggle_user(uid, active):
    if USE_SUPABASE:
        supabase.table("users").update({"active":active}).eq("id",uid).execute()
    else:
        conn=get_conn()
        conn.execute("UPDATE users SET active=? WHERE id=?",(1 if active else 0,uid))
        conn.commit(); conn.close()

def db_get_clients(user_id):
    if USE_SUPABASE:
        r=supabase.table("clients").select("*").eq("user_id",user_id).order("name").execute()
        cls=r.data or []
        for c in cls:
            dl=supabase.table("deadlines").select("status,doc_status").eq("client_id",c["id"]).execute().data or []
            c["overdue_count"] =sum(1 for d in dl if d["status"]=="overdue")
            c["upcoming_count"]=sum(1 for d in dl if d["status"]=="upcoming" and d["doc_status"]!="filed")
            c["filed_count"]   =sum(1 for d in dl if d["doc_status"]=="filed")
        return cls
    else:
        conn=get_conn()
        rows=conn.execute("""
            SELECT c.*,
                COUNT(CASE WHEN d.status='overdue' THEN 1 END) AS overdue_count,
                COUNT(CASE WHEN d.status='upcoming' AND d.doc_status!='filed' THEN 1 END) AS upcoming_count,
                COUNT(CASE WHEN d.doc_status='filed' THEN 1 END) AS filed_count
            FROM clients c LEFT JOIN deadlines d ON c.id=d.client_id
            WHERE c.user_id=? GROUP BY c.id ORDER BY c.name
        """,(user_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

def db_get_summary(user_id):
    clients=db_get_clients(user_id)
    cids=[c["id"] for c in clients]
    if not cids: return {"overdue":0,"upcoming":0,"filed":0}
    if USE_SUPABASE:
        dl=[]
        for cid in cids:
            r=supabase.table("deadlines").select("status,doc_status").eq("client_id",cid).execute()
            dl+=(r.data or [])
    else:
        conn=get_conn()
        ph=",".join("?"*len(cids))
        dl=[dict(r) for r in conn.execute(f"SELECT status,doc_status FROM deadlines WHERE client_id IN ({ph})",cids).fetchall()]
        conn.close()
    return {
        "overdue": sum(1 for d in dl if d["status"]=="overdue"),
        "upcoming":sum(1 for d in dl if d["status"]=="upcoming" and d["doc_status"]!="filed"),
        "filed":   sum(1 for d in dl if d["doc_status"]=="filed"),
    }

def db_get_deadlines(client_id, smart=False):
    """
    smart=False → all deadlines (used in All Deadlines page, CSV export)
    smart=True  → only show:
        - Current month and future (upcoming/overdue from this month)
        - Past months ONLY if doc_status != 'filed' (unfiled overdue items)
        Hides past months that are already filed — CA doesn't need to see those
    """
    if USE_SUPABASE:
        r = supabase.table("deadlines").select("*").eq("client_id", client_id).order("due_date").execute()
        rows = r.data or []
    else:
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM deadlines WHERE client_id=? ORDER BY due_date",
            (client_id,)
        ).fetchall()
        conn.close()
        rows = [dict(r) for r in rows]

    if smart:
        today = date.today()
        # Show from previous month start onwards
        if today.month == 1:
            show_from = date(today.year - 1, 12, 1)
        else:
            show_from = date(today.year, today.month - 1, 1)

        filtered = []
        for d in rows:
            try:
                due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
                if due < show_from:
                    # Very old — only show if somehow not filed (data issue)
                    if d["doc_status"] not in ("filed",):
                        d["_note"] = "old_unfiled"
                        filtered.append(d)
                else:
                    # Previous month + current + future — always show
                    if d["doc_status"] != "filed":
                        filtered.append(d)
                    # Filed ones in this window → hide (CA marked it done)
            except:
                filtered.append(d)

        # Sort: overdue unfiled first → then by date
        filtered.sort(key=lambda d: (
            0 if d["status"] == "overdue" else 1,
            d["due_date"]
        ))
        return filtered

    # Full list — sort overdue first
    rows.sort(key=lambda d: (
        0 if d["status"] == "overdue" else 1 if d["status"] == "upcoming" else 2,
        d["due_date"]
    ))
    return rows

def db_add_client(user_id,name,phone,email,gstin):
    ts=str(date.today())
    if USE_SUPABASE:
        r=supabase.table("clients").insert({"user_id":user_id,"name":name,"phone":phone,
            "email":email,"gstin":gstin,"created":ts}).execute()
        return r.data[0]["id"]
    else:
        conn=get_conn()
        cur=conn.execute("INSERT INTO clients(user_id,name,phone,email,gstin,created) VALUES(?,?,?,?,?,?)",
            (user_id,name,phone,email,gstin,ts))
        cid=cur.lastrowid; conn.commit(); conn.close(); return cid

def seed_deadlines(client_id):
    """
    Smart seeding when a new client is added.

    Logic (based on CA workflow analysis):
    - Deadlines older than 1 month → marked as 'filed' automatically
      Reason: CA was filing before your tool existed. You don't know what
              they filed, so assume they handled it. Showing Apr 2025 to a
              CA adding a client in June 2026 is noise, not signal.
    - Previous 1 month (May 2026 if added in June 2026) → kept as 'pending'
      Reason: Safety net. May deadline just passed — CA might not have filed
              it yet. Better to show it and let CA mark it filed than hide it.
    - Current month onwards → 'upcoming' or 'overdue' based on date
      Reason: These are the actual actionable deadlines.

    This mirrors how Taxmann/ClearTax handle new client onboarding.
    """
    today = date.today()
    # Cutoff: beginning of previous month
    # e.g. in June 2026 → cutoff = May 1 2026
    # Anything before May 1 → auto-filed
    # May and June onwards → pending/upcoming
    if today.month == 1:
        prev_month_start = date(today.year - 1, 12, 1)
    else:
        prev_month_start = date(today.year, today.month - 1, 1)

    for (ct, cat, dd, fy) in ALL_DEADLINES:
        due = datetime.strptime(dd, "%Y-%m-%d").date()

        if due < prev_month_start:
            # Older than 1 month → assume CA already handled it
            dl_status  = "filed"
            doc_status = "filed"
        else:
            # Previous month + current month + future → pending, compute status
            dl_status  = compute_status(dd)
            doc_status = "pending"

        if USE_SUPABASE:
            supabase.table("deadlines").insert({
                "client_id": client_id,
                "compliance_type": ct,
                "category": cat,
                "due_date": dd,
                "status": dl_status,
                "doc_status": doc_status
            }).execute()
        else:
            conn = get_conn()
            conn.execute(
                "INSERT INTO deadlines(client_id,compliance_type,category,due_date,status,doc_status) VALUES(?,?,?,?,?,?)",
                (client_id, ct, cat, dd, dl_status, doc_status)
            )
            conn.commit(); conn.close()

def db_reseed_missing(client_id):
    """Add any deadlines from ALL_DEADLINES that this client doesn't have yet.
    Safe to call multiple times — only adds missing ones."""
    if USE_SUPABASE:
        existing = supabase.table("deadlines").select("compliance_type").eq("client_id", client_id).execute()
        existing_types = {r["compliance_type"] for r in (existing.data or [])}
    else:
        conn = get_conn()
        rows = conn.execute("SELECT compliance_type FROM deadlines WHERE client_id=?", (client_id,)).fetchall()
        conn.close()
        existing_types = {r["compliance_type"] for r in rows}

    added = 0
    for (ct, cat, dd, fy) in ALL_DEADLINES:
        if ct not in existing_types:
            st2 = compute_status(dd)
            if USE_SUPABASE:
                supabase.table("deadlines").insert({
                    "client_id": client_id, "compliance_type": ct,
                    "category": cat, "due_date": dd,
                    "status": st2, "doc_status": "pending"
                }).execute()
            else:
                conn = get_conn()
                conn.execute(
                    "INSERT INTO deadlines(client_id,compliance_type,category,due_date,status,doc_status) VALUES(?,?,?,?,?,'pending')",
                    (client_id, ct, cat, dd, st2)
                )
                conn.commit(); conn.close()
            added += 1
    return added


    update={"doc_status":doc_status}
    if doc_status=="filed": update["status"]="filed"
    if USE_SUPABASE:
        supabase.table("deadlines").update(update).eq("id",did).execute()
    else:
        conn=get_conn()
        if doc_status=="filed":
            conn.execute("UPDATE deadlines SET doc_status=?,status='filed' WHERE id=?",(doc_status,did))
        else:
            conn.execute("UPDATE deadlines SET doc_status=? WHERE id=?",(doc_status,did))
        conn.commit(); conn.close()

def db_delete_client(cid):
    if USE_SUPABASE:
        supabase.table("deadlines").delete().eq("client_id",cid).execute()
        supabase.table("clients").delete().eq("id",cid).execute()
    else:
        conn=get_conn()
        conn.execute("DELETE FROM deadlines WHERE client_id=?",(cid,))
        conn.execute("DELETE FROM clients WHERE id=?",(cid,))
        conn.commit(); conn.close()

def db_get_logs(username=None, limit=100):
    if USE_SUPABASE:
        q=supabase.table("usage_logs").select("*").order("logged_at",desc=True).limit(limit)
        if username: q=q.eq("username",username)
        return q.execute().data or []
    else:
        conn=get_conn()
        if username:
            rows=conn.execute("SELECT * FROM usage_logs WHERE username=? ORDER BY logged_at DESC LIMIT ?",(username,limit)).fetchall()
        else:
            rows=conn.execute("SELECT * FROM usage_logs ORDER BY logged_at DESC LIMIT ?",(limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

def db_get_user_stats():
    users=db_get_users()
    stats=[]
    for u in users:
        logs=db_get_logs(username=u["username"], limit=1000)
        last=logs[0]["logged_at"] if logs else "Never"
        stats.append({
            "CA Firm":      u.get("firm") or u["username"],
            "Username":     u["username"],
            "Phone":        u.get("phone") or "—",
            "Active":       "✅ Yes" if u.get("active") else "❌ Suspended",
            "Total Logins": sum(1 for l in logs if l["action"]=="login"),
            "Total Actions":len(logs),
            "Last Seen":    last,
            "Joined":       u.get("created") or "—",
            "_uid":         u["id"],
            "_active":      u.get("active",1),
        })
    return stats

# ══════════════════════════════════════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div style="max-width:440px;margin:48px auto 0;animation:fadeSlideIn 0.5s ease">
      <div style="text-align:center;margin-bottom:28px">
        <div style="font-size:56px;margin-bottom:12px">📋</div>
        <div style="font-size:30px;font-weight:800;color:#1a237e;letter-spacing:-0.5px">CA Compliance OS</div>
        <div style="color:#888;font-size:14px;margin-top:6px">FY 2025-26 · Multi-client compliance dashboard</div>
        <div style="display:flex;justify-content:center;gap:12px;margin-top:14px">
          <span style="background:#e8eaf6;color:#3949ab;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">GST</span>
          <span style="background:#e8f5e9;color:#2e7d32;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">TDS</span>
          <span style="background:#fff8e1;color:#f57f17;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">ROC</span>
          <span style="background:#fce4ec;color:#c62828;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600">ITR</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col = st.columns([1, 2, 1])[1]
    with col:
        with st.form("login_form"):
            st.markdown("<div style='font-size:17px;font-weight:700;color:#1a237e;margin-bottom:16px'>🔐 Sign in to your account</div>", unsafe_allow_html=True)
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")
            if submitted:
                user = db_auth(username.strip(), password.strip())
                if user:
                    st.session_state["user"] = dict(user)
                    log_action(user["id"], user["username"], "login", "Logged in")
                    st.rerun()
                else:
                    st.error("❌ Wrong username or password, or account suspended.")
        st.markdown("<div style='text-align:center;font-size:12px;color:#aaa;margin-top:8px'>Contact your admin if you forgot your credentials</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# GATE
# ══════════════════════════════════════════════════════════════════════════════
if "user" not in st.session_state:
    show_login()
    st.stop()

USER = st.session_state["user"]
IS_ADMIN = USER.get("role") == "admin"

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style='padding:4px 0 16px'>
      <div style='font-size:20px;font-weight:800;color:#fff;letter-spacing:-0.3px'>📋 CA Compliance OS</div>
      <div style='font-size:11px;color:rgba(255,255,255,0.55);margin-top:3px'>FY 2025-26</div>
    </div>
    <div style='background:rgba(255,255,255,0.1);border-radius:10px;padding:10px 12px;margin-bottom:16px'>
      <div style='font-size:11px;color:rgba(255,255,255,0.6);margin-bottom:2px'>Logged in as</div>
      <div style='font-size:14px;font-weight:700;color:#fff'>{"⚙️ Admin" if IS_ADMIN else "👤 " + (USER.get("firm") or USER["username"])}</div>
    </div>
    """, unsafe_allow_html=True)

    if IS_ADMIN:
        pages=["🏠 Admin Dashboard","👥 Manage CAs","📊 Usage Analytics","➕ Add CA Account"]
    else:
        pages=["🏠 Dashboard","👥 My Clients","📅 All Deadlines","➕ Add Client"]

    page=st.radio("nav", pages, label_visibility="collapsed")
    st.markdown("---")

    if not IS_ADMIN:
        s=db_get_summary(USER["id"])
        st.markdown(f"""
        <div style='display:flex;flex-direction:column;gap:6px'>
          <div style='background:rgba(229,57,53,0.18);border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center'>
            <span style='color:rgba(255,255,255,0.8);font-size:12px'>🔴 Overdue</span>
            <span style='color:#ff8a80;font-weight:700;font-size:16px'>{s['overdue']}</span>
          </div>
          <div style='background:rgba(251,140,0,0.18);border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center'>
            <span style='color:rgba(255,255,255,0.8);font-size:12px'>🟡 Upcoming</span>
            <span style='color:#ffd54f;font-weight:700;font-size:16px'>{s['upcoming']}</span>
          </div>
          <div style='background:rgba(67,160,71,0.18);border-radius:8px;padding:8px 12px;display:flex;justify-content:space-between;align-items:center'>
            <span style='color:rgba(255,255,255,0.8);font-size:12px'>🟢 Filed</span>
            <span style='color:#a5d6a7;font-weight:700;font-size:16px'>{s['filed']}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

    db_label="☁️ Supabase (Cloud)" if USE_SUPABASE else "💾 SQLite (local)"
    st.markdown(f"<div style='font-size:11px;color:rgba(255,255,255,0.4);margin-bottom:10px'>{db_label}</div>", unsafe_allow_html=True)

    # Logout button — white outlined, clearly visible
    st.markdown("""
    <style>
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.12) !important;
        color: #fff !important;
        border: 1.5px solid rgba(255,255,255,0.5) !important;
        border-radius: 8px !important;
        width: 100% !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 0 !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.22) !important;
        border-color: rgba(255,255,255,0.8) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        log_action(USER["id"], USER["username"], "logout","Logged out")
        del st.session_state["user"]
        st.rerun()

def db_refresh_statuses(user_id):
    """Re-compute overdue/upcoming for all deadlines based on today. Call once per session."""
    today = date.today()
    first_of_month = today.replace(day=1)
    clients = db_get_clients(user_id)
    cids = [c["id"] for c in clients]
    if not cids: return
    for cid in cids:
        dls = db_get_deadlines(cid)
        for d in dls:
            if d["doc_status"] == "filed":
                continue
            due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
            new_status = "overdue" if due < first_of_month else "upcoming"
            if new_status != d["status"]:
                if USE_SUPABASE:
                    supabase.table("deadlines").update({"status": new_status}).eq("id", d["id"]).execute()
                else:
                    conn = get_conn()
                    conn.execute("UPDATE deadlines SET status=? WHERE id=?", (new_status, d["id"]))
                    conn.commit(); conn.close()

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PAGES
# ══════════════════════════════════════════════════════════════════════════════
if IS_ADMIN:

    # ── Admin Dashboard ───────────────────────────────────────────────────────
    if page == "🏠 Admin Dashboard":
        st.markdown("""<div class="page-header">
          <div class="page-title">⚙️ Admin Dashboard</div>
          <div class="page-sub">Your product at a glance — all CAs, all activity, real-time</div>
        </div>""", unsafe_allow_html=True)

        stats = db_get_user_stats()
        logs  = db_get_logs(limit=200)

        total_cas    = len(stats)
        active_cas   = sum(1 for s in stats if "✅" in s["Active"])
        total_logins = sum(s["Total Logins"] for s in stats)
        active_today = len(set(l["username"] for l in logs
                               if l["logged_at"][:10]==str(date.today())))

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("👥 Total CAs",       total_cas)
        c2.metric("✅ Active CAs",       active_cas)
        c3.metric("🔑 Total Logins",    total_logins)
        c4.metric("📅 Active Today",    active_today)

        st.markdown("---")
        st.markdown("### 📋 CA Status Overview")

        if not stats:
            st.info("No CA accounts yet. Go to ➕ Add CA Account.")
        else:
            for s in stats:
                last_seen = s["Last Seen"]
                if last_seen == "Never":
                    health = "Never logged in"
                    card_c = "red"; health_color="#e53935"; health_bg="#fdecea"
                else:
                    try:
                        last_dt = datetime.strptime(last_seen[:10], "%Y-%m-%d").date()
                        days_ago = (date.today() - last_dt).days
                        if days_ago == 0:    health="Active today";     card_c="green"; health_color="#2e7d32"; health_bg="#e8f5e9"
                        elif days_ago <= 3:  health="Active recently";  card_c="green"; health_color="#2e7d32"; health_bg="#e8f5e9"
                        elif days_ago <= 7:  health=f"Inactive {days_ago}d";  card_c="amber"; health_color="#e65100"; health_bg="#fff8e1"
                        elif days_ago <= 14: health=f"Inactive {days_ago}d";  card_c="amber"; health_color="#e65100"; health_bg="#fff8e1"
                        else:                health=f"Inactive {days_ago}d";  card_c="red";   health_color="#c62828"; health_bg="#fdecea"
                    except: health="Unknown"; card_c=""; health_color="#888"; health_bg="#f5f5f5"

                st.markdown(f"""
                <div class="ca-card {card_c}">
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
                    <div class="ca-card-name">🏢 {s['CA Firm']}</div>
                    <span class="badge" style="background:{health_bg};color:{health_color}">{health}</span>
                  </div>
                  <div class="ca-card-meta">
                    👤 {s['Username']} &nbsp;·&nbsp;
                    📱 {s['Phone']} &nbsp;·&nbsp;
                    🔑 <b>{s['Total Logins']}</b> logins &nbsp;·&nbsp;
                    ⚡ <b>{s['Total Actions']}</b> actions &nbsp;·&nbsp;
                    🕐 {last_seen[:16] if last_seen!='Never' else 'Never'}
                  </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Manage CAs ────────────────────────────────────────────────────────────
    elif page == "👥 Manage CAs":
        st.markdown("""<div class="page-header">
          <div class="page-title">👥 Manage CA Accounts</div>
          <div class="page-sub">Suspend non-paying CAs instantly · Restore on payment · Full control</div>
        </div>""", unsafe_allow_html=True)

        stats = db_get_user_stats()
        if not stats:
            st.info("No CA accounts yet.")
        else:
            for s in stats:
                with st.expander(f"{'✅' if '✅' in s['Active'] else '❌'}  {s['CA Firm']}  —  {s['Username']}"):
                    c1,c2,c3 = st.columns([3,2,2])
                    c1.markdown(f"**🏢 Firm:** {s['CA Firm']}")
                    c1.markdown(f"**📱 Phone:** {s['Phone']}")
                    c1.markdown(f"**📅 Joined:** {s['Joined']}")
                    c2.markdown(f"**🔑 Total Logins:** {s['Total Logins']}")
                    c2.markdown(f"**⚡ Total Actions:** {s['Total Actions']}")
                    c2.markdown(f"**🕐 Last Seen:** {s['Last Seen'][:16] if s['Last Seen']!='Never' else 'Never'}")

                    is_active = "✅" in s["Active"]
                    if is_active:
                        if c3.button("🔴 Suspend Access", key=f"sus_{s['_uid']}"):
                            db_toggle_user(s["_uid"], False)
                            st.success(f"Suspended {s['CA Firm']}. They cannot login now.")
                            st.rerun()
                    else:
                        if c3.button("🟢 Restore Access", key=f"res_{s['_uid']}"):
                            db_toggle_user(s["_uid"], True)
                            st.success(f"Restored {s['CA Firm']}. They can login again.")
                            st.rerun()
                    logs = db_get_logs(username=s["Username"], limit=10)
                    if logs:
                        st.markdown("**Recent Activity:**")
                        for l in logs:
                            st.markdown(f"""<div class="log-row">
                                🕐 {l['logged_at'][:16]} &nbsp;·&nbsp;
                                <b>{l['action']}</b> &nbsp;·&nbsp; {l.get('detail','')}
                            </div>""", unsafe_allow_html=True)

    # ── Usage Analytics ───────────────────────────────────────────────────────
    elif page == "📊 Usage Analytics":
        st.markdown("""<div class="page-header">
          <div class="page-title">📊 Usage Analytics</div>
          <div class="page-sub">Every action timestamped · Proof of usage · Export anytime</div>
        </div>""", unsafe_allow_html=True)

        stats = db_get_user_stats()
        all_logs = db_get_logs(limit=500)

        # Filter
        ca_names = ["All CAs"] + [s["CA Firm"] for s in stats]
        col1,col2 = st.columns([2,3])
        sel_ca   = col1.selectbox("Filter by CA", ca_names)
        sel_days = col2.slider("Last N days", 1, 30, 7)

        cutoff = (datetime.now() - timedelta(days=sel_days)).strftime("%Y-%m-%d")
        filtered = [l for l in all_logs if l["logged_at"][:10] >= cutoff]
        if sel_ca != "All CAs":
            firm_username = next((s["Username"] for s in stats if s["CA Firm"]==sel_ca), None)
            if firm_username:
                filtered = [l for l in filtered if l["username"]==firm_username]

        st.markdown(f"**{len(filtered)} actions** in last {sel_days} days")
        st.markdown("---")

        if not filtered:
            st.info("No activity in this period.")
        else:
            for l in filtered:
                action_icon = {
                    "login":"🔑","logout":"🚪","add_client":"➕",
                    "whatsapp":"📲","update_status":"✏️","delete_client":"🗑️",
                    "view_deadlines":"👁️"
                }.get(l["action"],"⚡")
                st.markdown(f"""<div class="log-row">
                    {action_icon} &nbsp;
                    <b>{l['username']}</b> &nbsp;·&nbsp;
                    {l['action'].replace('_',' ').title()} &nbsp;·&nbsp;
                    {l.get('detail','')} &nbsp;·&nbsp;
                    <span style='color:#999'>{l['logged_at'][:16]}</span>
                </div>""", unsafe_allow_html=True)

            # Download CSV — plain Python, no pandas needed
            if filtered:
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=filtered[0].keys())
                writer.writeheader()
                writer.writerows(filtered)
                st.download_button("⬇️ Export Logs CSV",
                    buf.getvalue().encode(), "usage_logs.csv", "text/csv")

    # ── Add CA Account ────────────────────────────────────────────────────────
    elif page == "➕ Add CA Account":
        st.markdown("""<div class="page-header">
          <div class="page-title">➕ Add CA Account</div>
          <div class="page-sub">Create login credentials for a paying CA firm · Share & start earning</div>
        </div>""", unsafe_allow_html=True)

        with st.form("add_ca_form", clear_on_submit=True):
            c1,c2=st.columns(2)
            firm    =c1.text_input("CA Firm Name *",  placeholder="e.g. Sharma & Associates")
            username=c2.text_input("Username *",       placeholder="e.g. sharma_ca")
            password=c1.text_input("Password *",       placeholder="min 8 characters")
            phone   =c2.text_input("WhatsApp Number",  placeholder="10-digit mobile")

            submitted=st.form_submit_button("✅ Create CA Account", use_container_width=True, type="primary")
            if submitted:
                if not firm or not username or not password:
                    st.error("Firm name, username and password are required.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    try:
                        db_add_user(username.strip(), password.strip(), firm.strip(), phone.strip())
                        st.success(f"✅ Account created for **{firm}**")
                        st.info(f"Share these credentials:\n\n**Username:** `{username}`\n**Password:** `{password}`\n\n🔗 Share your app link with them.")
                    except Exception as e:
                        st.error(f"Username already exists. Choose a different one.")
else:
    # Auto-refresh deadline statuses once per session
    if not st.session_state.get("statuses_refreshed"):
        db_refresh_statuses(USER["id"])
        st.session_state["statuses_refreshed"] = True

    s = db_get_summary(USER["id"])

    # ── CA Dashboard ──────────────────────────────────────────────────────────
    if page == "🏠 Dashboard":
        today = date.today()
        this_month = today.strftime("%B %Y")  # e.g. "June 2026"

        st.markdown(f"""<div class="page-header">
          <div class="page-title">🏠 Command Centre</div>
          <div class="page-sub">Welcome back, {USER.get('firm') or USER['username']} · {this_month} · All clients · All deadlines</div>
        </div>""", unsafe_allow_html=True)
        log_action(USER["id"],USER["username"],"view_dashboard","Viewed dashboard")

        c1,c2,c3,c4=st.columns(4)
        clients=db_get_clients(USER["id"])
        c1.metric("👥 My Clients", len(clients))
        c2.metric("🔴 Overdue",    s["overdue"])
        c3.metric("🟡 Upcoming",   s["upcoming"])
        c4.metric("🟢 Filed",      s["filed"])

        st.markdown("""<div class="alert-box">
          ⚠️ Due dates are indicative. Always verify extensions at <b>gstn.org.in</b> before filing.
        </div>""", unsafe_allow_html=True)

        # Check if any client is missing FY 2026-27 deadlines and show fix button
        if clients:
            clients_needing_fix = [c for c in clients if (c.get("filed_count",0) + c.get("overdue_count",0) + c.get("upcoming_count",0)) < len(ALL_DEADLINES)]
            # Simpler check — count actual deadlines
            needs_fix = []
            for c in clients:
                dls = db_get_deadlines(c["id"])
                if len(dls) < len(ALL_DEADLINES):
                    needs_fix.append(c)

            if needs_fix:
                st.markdown(f"""
                <div style='background:#e3f2fd;border-radius:10px;padding:12px 16px;
                  margin-bottom:14px;border:1px solid #90caf9;display:flex;
                  align-items:center;justify-content:space-between'>
                  <div>
                    <div style='font-size:13px;font-weight:700;color:#1565c0'>
                      🔄 {len(needs_fix)} client(s) missing FY 2026-27 deadlines
                    </div>
                    <div style='font-size:11px;color:#888;margin-top:2px'>
                      Click Fix to add the missing deadlines automatically
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"🔄 Fix all {len(needs_fix)} clients — add missing deadlines", type="primary"):
                    total_added = 0
                    for c in needs_fix:
                        total_added += db_reseed_missing(c["id"])
                    st.session_state["statuses_refreshed"] = False  # force re-refresh
                    st.success(f"✅ Added {total_added} missing deadlines across {len(needs_fix)} clients!")
                    st.rerun()


        if clients:
            end_30 = today + timedelta(days=30)
            urgent_deadlines = []
            cids = [c["id"] for c in clients]
            cmap = {c["id"]: c["name"] for c in clients}
            for cid in cids:
                for d in db_get_deadlines(cid):
                    if d["doc_status"] == "filed":
                        continue
                    try:
                        due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
                        if today <= due <= end_30:
                            d["client_name"] = cmap.get(cid, "")
                            d["due_date_obj"] = due
                            urgent_deadlines.append(d)
                    except: pass
            urgent_deadlines.sort(key=lambda x: x["due_date_obj"])

            if urgent_deadlines:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#fff3e0,#fff8e1);border-radius:14px;
                  padding:16px 20px;margin-bottom:16px;border:1px solid #ffcc02'>
                  <div style='font-size:15px;font-weight:700;color:#e65100;margin-bottom:4px'>
                    🔥 Due in next 30 days — {len(urgent_deadlines)} filings need attention
                  </div>
                  <div style='font-size:12px;color:#888'>Act now to avoid penalties</div>
                </div>""", unsafe_allow_html=True)

                for d in urgent_deadlines:
                    due_obj = d["due_date_obj"]
                    days_left = (due_obj - today).days
                    if days_left == 0:     urgency = "🔴 Due TODAY"
                    elif days_left <= 3:   urgency = f"🔴 Due in {days_left} days"
                    elif days_left <= 7:   urgency = f"🟡 Due in {days_left} days"
                    else:                  urgency = f"🟢 Due in {days_left} days"

                    st.markdown(f"""
                    <div style='background:#fff;border-radius:10px;padding:10px 16px;
                      margin-bottom:6px;border:1px solid #ffe0b2;border-left:4px solid #fb8c00;
                      display:flex;align-items:center;justify-content:space-between'>
                      <div>
                        <span style='font-size:13px;font-weight:600;color:#1a237e'>{d['client_name']}</span>
                        &nbsp;·&nbsp;
                        <span style='font-size:13px;color:#333'>{d['compliance_type']}</span>
                      </div>
                      <div style='display:flex;align-items:center;gap:12px'>
                        <span style='font-size:12px;color:#888'>{d['due_date']}</span>
                        <span style='font-size:12px;font-weight:600'>{urgency}</span>
                      </div>
                    </div>""", unsafe_allow_html=True)
                st.markdown("---")

        if not clients:
            st.info("No clients yet. Click **➕ Add Client** in the sidebar to get started.")
        else:
            st.markdown("<div style='font-size:15px;font-weight:700;color:#1a237e;margin-bottom:12px'>📋 All Clients</div>", unsafe_allow_html=True)
            for c in clients:
                ov=c.get("overdue_count") or 0
                up=c.get("upcoming_count") or 0
                fi=c.get("filed_count") or 0
                cc="red" if ov else "amber" if up else "green"
                badge=(f'<span class="badge red">🔴 {ov} Overdue</span>' if ov
                       else f'<span class="badge amber">🟡 {up} Upcoming</span>' if up
                       else f'<span class="badge green">🟢 All Clear</span>')
                st.markdown(f"""
                <div class="ca-card {cc}">
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">
                    <div class="ca-card-name">🏢 {c['name']}</div>{badge}
                  </div>
                  <div class="ca-card-meta">
                    📱 {c.get('phone') or '—'} &nbsp;·&nbsp;
                    ✉️ {c.get('email') or '—'} &nbsp;·&nbsp;
                    GSTIN: {c.get('gstin') or '—'} &nbsp;&nbsp;|&nbsp;&nbsp;
                    🔴 {ov} overdue &nbsp; 🟡 {up} upcoming &nbsp; 🟢 {fi} filed
                  </div>
                </div>""", unsafe_allow_html=True)

    # ── My Clients ────────────────────────────────────────────────────────────
    elif page == "👥 My Clients":
        today = date.today()
        this_month_str = today.strftime("%B %Y")
        st.markdown(f"""<div class="page-header">
          <div class="page-title">👥 My Clients</div>
          <div class="page-sub">Showing current & upcoming deadlines · {this_month_str} onwards · Expand to manage</div>
        </div>""", unsafe_allow_html=True)
        log_action(USER["id"],USER["username"],"view_clients","Viewed clients page")

        clients=db_get_clients(USER["id"])
        if not clients:
            st.info("No clients yet. Click **➕ Add Client**.")
        else:
            for c in clients:
                ov=c.get("overdue_count") or 0
                up=c.get("upcoming_count") or 0
                fi=c.get("filed_count") or 0
                icon="🔴" if ov else "🟡" if up else "🟢"

                with st.expander(f"{icon}  {c['name']}  —  🔴 {ov} overdue · 🟡 {up} upcoming · 🟢 {fi} filed"):
                    ci,cw,cd=st.columns([3,2,1])
                    ci.markdown(f"**📱 Phone:** {c.get('phone') or '—'}")
                    ci.markdown(f"**✉️ Email:** {c.get('email') or '—'}")
                    ci.markdown(f"**🏷️ GSTIN:** {c.get('gstin') or '—'}")

                    with cw:
                        if st.button(f"📲 WhatsApp Reminder", key=f"wa_{c['id']}", type="primary", use_container_width=True):
                            st.session_state[f"show_wa_{c['id']}"]=True
                            log_action(USER["id"],USER["username"],"whatsapp",f"Drafted WA for {c['name']}")

                        if st.session_state.get(f"show_wa_{c['id']}"):
                            # Smart WhatsApp — only current month + next 2 months unfiled
                            all_dls = db_get_deadlines(c["id"])
                            end_60 = today + timedelta(days=60)
                            first_of_month = today.replace(day=1)

                            wa_lines = []
                            for d in all_dls:
                                if d["doc_status"] == "filed":
                                    continue
                                try:
                                    due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
                                    # Show: current month overdue + next 60 days upcoming
                                    if due >= first_of_month and due <= end_60:
                                        wa_lines.append(d)
                                except: pass
                            wa_lines = wa_lines[:6]  # max 6 items

                            if not wa_lines:
                                st.success("✅ No pending deadlines in next 60 days for this client!")
                            else:
                                lines = [f"Dear {c['name']},\n",
                                         f"Compliance reminders for {this_month_str}:\n"]
                                for d in wa_lines:
                                    try:
                                        due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
                                        days_left = (due - today).days
                                        if days_left < 0:
                                            urgency = "⚠️ OVERDUE"
                                        elif days_left == 0:
                                            urgency = "⚠️ DUE TODAY"
                                        elif days_left <= 7:
                                            urgency = f"🔴 Due in {days_left} days"
                                        else:
                                            urgency = f"🟡 Due on {d['due_date']}"
                                        lines.append(f"{urgency} — {d['compliance_type']}")
                                    except:
                                        lines.append(f"• {d['compliance_type']} — {d['due_date']}")

                                lines += ["", "Please send the required documents at the earliest to avoid penalties.",
                                          "", "Regards,", "Your CA"]
                                msg = "\n".join(lines)
                                st.markdown(f'<div class="wa-box">{msg}</div>', unsafe_allow_html=True)

                                if c.get("phone"):
                                    enc = urllib.parse.quote(msg)
                                    phone = c['phone'].strip().replace(" ","").replace("+","").replace("-","")
                                    if not phone.startswith("91"): phone = "91" + phone
                                    st.markdown(f"""<a href="https://wa.me/{phone}?text={enc}" target="_blank"
                                        style="display:inline-block;margin-top:8px;padding:8px 20px;
                                        background:#25d366;color:#fff;border-radius:8px;font-size:13px;
                                        font-weight:700;text-decoration:none">
                                        🟢 Open in WhatsApp →</a>""", unsafe_allow_html=True)
                                else:
                                    st.warning("Add phone number to use WhatsApp.")

                    with cd:
                        if st.button("🗑️ Delete", key=f"del_{c['id']}"):
                            st.session_state[f"confirm_{c['id']}"]=True
                        if st.session_state.get(f"confirm_{c['id']}"):
                            st.warning("Delete?")
                            if st.button("✅ Yes", key=f"yes_{c['id']}"):
                                db_delete_client(c["id"])
                                log_action(USER["id"],USER["username"],"delete_client",f"Deleted {c['name']}")
                                st.rerun()
                        st.markdown("---")
                        total_dls = len(db_get_deadlines(c["id"]))
                        if total_dls < len(ALL_DEADLINES):
                            st.markdown(f"<div style='font-size:10px;color:#e65100;margin-bottom:4px'>⚠️ {total_dls}/{len(ALL_DEADLINES)}</div>", unsafe_allow_html=True)
                            if st.button("🔄 Fix", key=f"fix_{c['id']}"):
                                added = db_reseed_missing(c["id"])
                                st.success(f"+{added} deadlines added!")
                                st.rerun()

                    # ── Smart deadline table ──────────────────────────────────
                    st.markdown("---")

                    # Toggle between smart view and full history
                    show_all_key = f"show_all_{c['id']}"
                    col_title, col_toggle = st.columns([3, 1])
                    show_all = st.session_state.get(show_all_key, False)

                    with col_title:
                        if show_all:
                            st.markdown("**📅 Full deadline history**")
                        else:
                            st.markdown(f"**📅 Current & upcoming deadlines** *(from {this_month_str})*")
                    with col_toggle:
                        if show_all:
                            if st.button("📅 Current only", key=f"tog_{c['id']}"):
                                st.session_state[show_all_key] = False
                                st.rerun()
                        else:
                            if st.button("📋 Full history", key=f"tog_{c['id']}"):
                                st.session_state[show_all_key] = True
                                st.rerun()

                    # Get deadlines — smart or full
                    dls = db_get_deadlines(c["id"], smart=not show_all)

                    if not dls:
                        st.success("✅ No pending deadlines to show. All current deadlines are filed!")
                    else:
                        # Header
                        h0,h1,h2,h3 = st.columns([4,2,2,3])
                        for col, label in zip([h0,h1,h2,h3],["Compliance","Due Date","Status","Doc Status"]):
                            col.markdown(f"<span style='font-size:11px;font-weight:700;color:#888;text-transform:uppercase;letter-spacing:0.5px'>{label}</span>", unsafe_allow_html=True)

                        for d in dls:
                            cols = st.columns([4,2,2,3])
                            sl = {"overdue":"🔴 Overdue","upcoming":"🟡 Upcoming","filed":"🟢 Filed"}.get(d["status"], d["status"])

                            # Highlight current month rows
                            try:
                                due = datetime.strptime(d["due_date"], "%Y-%m-%d").date()
                                is_current = due.year == today.year and due.month == today.month
                                name_style = "font-weight:700;color:#1a237e" if is_current else "font-weight:500"
                            except:
                                name_style = "font-weight:500"
                                is_current = False

                            cols[0].markdown(f"<span style='{name_style}'>{d['compliance_type']}</span>", unsafe_allow_html=True)
                            cols[1].markdown(f"<span style='color:#666;font-size:13px'>{d['due_date']}</span>", unsafe_allow_html=True)
                            cols[2].markdown(sl)

                            doc_labels = {
                                "pending":            "📂 Pending",
                                "documents_received": "📥 Docs Received",
                                "filed":              "✅ Filed"
                            }
                            opts_keys   = ["pending","documents_received","filed"]
                            opts_labels = [doc_labels[k] for k in opts_keys]
                            cur_idx = opts_keys.index(d["doc_status"]) if d["doc_status"] in opts_keys else 0
                            chosen_label = cols[3].selectbox(
                                "", options=opts_labels, index=cur_idx,
                                key=f"ds_{d['id']}", label_visibility="collapsed"
                            )
                            chosen_key = opts_keys[opts_labels.index(chosen_label)]
                            if chosen_key != d["doc_status"]:
                                db_update_doc_status(d["id"], chosen_key)
                                log_action(USER["id"],USER["username"],"update_status",
                                           f"{c['name']} → {d['compliance_type']} → {chosen_key}")
                                st.rerun()

    # ── All Deadlines ─────────────────────────────────────────────────────────
    elif page == "📅 All Deadlines":
        st.markdown("""<div class="page-header">
          <div class="page-title">📅 All Deadlines — FY 2025-26</div>
          <div class="page-sub">Filter by status · Search by client · Export to CSV</div>
        </div>""", unsafe_allow_html=True)
        log_action(USER["id"],USER["username"],"view_deadlines","Viewed all deadlines")

        clients=db_get_clients(USER["id"])
        cids=[c["id"] for c in clients]
        if not cids:
            st.info("No clients yet.")
        else:
            f1,f2,f3=st.columns(3)
            fs=f1.selectbox("Status",["All","overdue","upcoming","filed"])
            fc=f2.selectbox("Category",["All","GST","TDS","ROC","ITR","ADV"])
            fq=f3.text_input("Search client",placeholder="Type name…")

            all_rows=[]
            cmap={c["id"]:c["name"] for c in clients}
            for cid in cids:
                for d in db_get_deadlines(cid):
                    d["client_name"]=cmap.get(cid,"")
                    all_rows.append(d)

            # Filter with plain Python — no pandas needed
            rows = all_rows
            if fs!="All": rows=[r for r in rows if r["status"]==fs]
            if fc!="All": rows=[r for r in rows if r["category"]==fc]
            if fq: rows=[r for r in rows if fq.lower() in r["client_name"].lower()]

            st.markdown(f"**{len(rows)} deadlines**")
            st.markdown("---")
            for row in rows:
                si={"overdue":"🔴","upcoming":"🟡","filed":"🟢"}.get(row["status"],"⚪")
                di={"pending":"📂 Pending","documents_received":"📥 Docs In","filed":"✅ Filed"}.get(row["doc_status"],row["doc_status"])
                cols=st.columns([2,4,2,2,2])
                cols[0].markdown(f"**{row['client_name']}**")
                cols[1].markdown(row["compliance_type"])
                cols[2].markdown(row["due_date"])
                cols[3].markdown(f"{si} {str(row['status']).title()}")
                cols[4].markdown(di)

            st.markdown("---")
            # CSV export — plain Python
            if rows:
                buf = io.StringIO()
                writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
                st.download_button("⬇️ Download CSV",
                    buf.getvalue().encode(),
                    f"deadlines_{date.today()}.csv","text/csv")

    # ── Add Client ────────────────────────────────────────────────────────────
    elif page == "➕ Add Client":
        st.markdown("""<div class="page-header">
          <div class="page-title">➕ Add New Client</div>
          <div class="page-sub">34 FY 2025-26 deadlines auto-loaded instantly · GST · TDS · ROC · ITR · Advance Tax</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="info-banner">✅ Every new client automatically gets {len(DEADLINES_FY2526)} pre-loaded statutory deadlines for FY 2025-26. Nothing to configure.</div>', unsafe_allow_html=True)

        with st.form("add_client_form", clear_on_submit=True):
            c1,c2=st.columns(2)
            name =c1.text_input("Client / Company Name *", placeholder="e.g. ABC Pvt Ltd")
            phone=c2.text_input("WhatsApp Number",          placeholder="9876543210")
            email=c1.text_input("Email Address",            placeholder="client@example.com")
            gstin=c2.text_input("GSTIN (optional)",         placeholder="22AAAAA0000A1Z5")
            submitted=st.form_submit_button("✅ Add Client & Load All Deadlines",
                                            use_container_width=True, type="primary")
            if submitted:
                if not name.strip():
                    st.error("Client name is required.")
                else:
                    cid=db_add_client(USER["id"],name.strip(),phone.strip(),email.strip(),gstin.strip())
                    seed_deadlines(cid)
                    log_action(USER["id"],USER["username"],"add_client",f"Added {name}")
                    st.success(f"✅ **{name}** added with {len(DEADLINES_FY2526)} deadlines!")
                    st.balloons()