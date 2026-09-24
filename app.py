import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from newsapi import NewsApiClient
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import datetime
import sqlite3
import math
import os
import pytz

IST = pytz.timezone('Asia/Kolkata')

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=60 * 1000, key="autorefresh")
except ImportError:
    pass

# ================================================================
# PAGE CONFIG & GLOBAL CSS
# ================================================================
st.set_page_config(
    page_title="SENTINEL · Stock Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=Bebas+Neue&display=swap');

/* ── ROOT TOKENS ── */
:root {
    --bg:        #080c14;
    --surface:   #0d1421;
    --card:      #111a2b;
    --border:    #1e2d45;
    --accent:    #00d4ff;
    --accent2:   #7b61ff;
    --green:     #00e676;
    --red:       #ff3b5c;
    --amber:     #ffb300;
    --muted:     #4a6080;
    --text:      #c8d8f0;
    --text-dim:  #6a8aaa;
    --font-mono: 'Space Mono', monospace;
    --font-body: 'DM Sans', sans-serif;
    --font-display: 'Bebas Neue', sans-serif;
}

/* ── BASE RESET ── */
html, body, [class*="css"], .stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-body) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, header, footer { visibility: hidden; }
.block-container {
    padding: 0 2rem 2rem 2rem !important;
    max-width: 1600px !important;
}

/* ── CUSTOM HEADER BAR ── */
.sentinel-header {
    background: linear-gradient(135deg, #0a0f1e 0%, #0d1a30 50%, #0a1525 100%);
    border-bottom: 1px solid var(--border);
    padding: 1.2rem 2rem;
    margin: -1rem -2rem 2rem -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.sentinel-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent2), var(--accent), var(--green));
}
.sentinel-logo {
    font-family: var(--font-display);
    font-size: 2.2rem;
    letter-spacing: 0.15em;
    color: var(--accent);
    text-shadow: 0 0 30px rgba(0,212,255,0.4);
    line-height: 1;
}
.sentinel-tagline {
    font-family: var(--font-mono);
    font-size: 0.62rem;
    color: var(--muted);
    letter-spacing: 0.25em;
    text-transform: uppercase;
    margin-top: 3px;
}
.sentinel-clock {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-dim);
    text-align: right;
    line-height: 1.8;
}
.sentinel-clock span {
    color: var(--accent);
}
.live-dot {
    display: inline-block;
    width: 7px; height: 7px;
    background: var(--green);
    border-radius: 50%;
    margin-right: 5px;
    animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 6px var(--green); }
    50% { opacity: 0.4; box-shadow: none; }
}

/* ── SECTION HEADERS ── */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 10px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}
.section-title {
    font-family: var(--font-display);
    font-size: 1.6rem;
    letter-spacing: 0.08em;
    color: var(--text);
    margin-bottom: 1.2rem;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent);
}
.metric-card.green::before { background: var(--green); }
.metric-card.red::before   { background: var(--red); }
.metric-card.amber::before { background: var(--amber); }
.metric-card:hover { border-color: var(--accent); }
.metric-symbol {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: var(--font-display);
    font-size: 2rem;
    letter-spacing: 0.05em;
    color: var(--text);
    line-height: 1.1;
}
.metric-delta {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    margin-top: 4px;
}
.metric-delta.pos { color: var(--green); }
.metric-delta.neg { color: var(--red); }

/* ── SCORE GAUGE ── */
.gauge-wrap {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.2rem;
    text-align: center;
}
.gauge-score {
    font-family: var(--font-display);
    font-size: 3rem;
    line-height: 1;
}
.gauge-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-top: 4px;
}
.action-pill {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    padding: 4px 16px;
    border-radius: 30px;
    margin-top: 8px;
}
.action-pill.BUY  { background: rgba(0,230,118,0.15); color: var(--green); border: 1px solid var(--green); }
.action-pill.SELL { background: rgba(255,59,92,0.15);  color: var(--red);   border: 1px solid var(--red); }
.action-pill.HOLD { background: rgba(255,179,0,0.15);  color: var(--amber); border: 1px solid var(--amber); }

/* ── NEWS ITEMS ── */
.news-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid var(--muted);
    transition: border-color 0.15s;
}
.news-item.pos { border-left-color: var(--green); }
.news-item.neg { border-left-color: var(--red); }
.news-item.neu { border-left-color: var(--muted); }
.news-item:hover { border-color: var(--accent); }
.news-title {
    font-size: 0.85rem;
    color: var(--text);
    font-weight: 500;
    line-height: 1.4;
}
.news-meta {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    color: var(--text-dim);
    margin-top: 4px;
    display: flex;
    gap: 12px;
}
.score-badge {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    padding: 1px 7px;
    border-radius: 3px;
}
.score-badge.pos { background: rgba(0,230,118,0.15); color: var(--green); }
.score-badge.neg { background: rgba(255,59,92,0.15);  color: var(--red); }
.score-badge.neu { background: rgba(74,96,128,0.3);   color: var(--muted); }

/* ── REDDIT POSTS ── */
.reddit-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.4rem;
    border-left: 3px solid #ff4500;
}
.reddit-title {
    font-size: 0.82rem;
    color: var(--text);
    line-height: 1.4;
}
.reddit-meta {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--text-dim);
    margin-top: 3px;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stSelectbox select {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    border-radius: 4px !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p {
    color: var(--text-dim) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
    font-family: var(--font-display) !important;
    letter-spacing: 0.1em !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    color: var(--text) !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── DATAFRAME ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 4px; }

/* ── DISCLAIMER ── */
.disclaimer-box {
    background: rgba(255,179,0,0.06);
    border: 1px solid rgba(255,179,0,0.25);
    border-left: 3px solid var(--amber);
    border-radius: 4px;
    padding: 0.9rem 1.2rem;
    font-size: 0.78rem;
    color: var(--text-dim);
    line-height: 1.6;
    margin-top: 1rem;
}

/* ── DIVIDER ── */
.sentinel-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 2rem 0;
}

/* ── OVERRIDES for native streamlit elements ── */
.stMetric { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 6px !important; padding: 0.8rem !important; }
.stMetric label { font-family: var(--font-mono) !important; font-size: 0.6rem !important; letter-spacing: 0.2em !important; color: var(--text-dim) !important; }
.stMetric [data-testid="metric-container"] > div:nth-child(2) { font-family: var(--font-display) !important; color: var(--text) !important; }
div[data-testid="stSpinner"] { color: var(--accent) !important; }
</style>
""", unsafe_allow_html=True)

# ================================================================
# MATPLOTLIB DARK THEME
# ================================================================
plt.rcParams.update({
    "figure.facecolor":  "#111a2b",
    "axes.facecolor":    "#0d1421",
    "axes.edgecolor":    "#1e2d45",
    "axes.labelcolor":   "#6a8aaa",
    "axes.titlecolor":   "#c8d8f0",
    "axes.titlesize":    9,
    "axes.labelsize":    7,
    "axes.titleweight":  "bold",
    "axes.grid":         True,
    "grid.color":        "#1e2d45",
    "grid.linewidth":    0.6,
    "xtick.color":       "#4a6080",
    "ytick.color":       "#4a6080",
    "xtick.labelsize":   6,
    "ytick.labelsize":   6,
    "legend.facecolor":  "#111a2b",
    "legend.edgecolor":  "#1e2d45",
    "legend.fontsize":   6,
    "legend.labelcolor": "#c8d8f0",
    "lines.linewidth":   1.8,
    "text.color":        "#c8d8f0",
    "font.family":       "monospace",
})

PALETTE = ["#00d4ff", "#7b61ff", "#00e676", "#ffb300", "#ff3b5c"]

# ================================================================
# DATABASE SETUP
# ================================================================
DB_FILE = "sentinel_dashboard.db"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS sentiment_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL,
        date TEXT NOT NULL, time TEXT NOT NULL, score REAL NOT NULL, run_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS news_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL, title TEXT NOT NULL,
        source TEXT, polarity REAL, fetched_at TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reddit_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT NOT NULL, title TEXT NOT NULL,
        subreddit TEXT, upvotes INTEGER, polarity REAL, fetched_at TEXT NOT NULL)""")
    conn.commit()
    conn.close()

init_db()

def record_sentiment(symbol, score):
    now = datetime.now(IST)
    conn = get_db()
    conn.execute("INSERT INTO sentiment_history (symbol,date,time,score,run_at) VALUES (?,?,?,?,?)",
        (symbol, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
         round(score, 4), now.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()

def load_history(symbol):
    conn = get_db()
    rows = conn.execute(
        "SELECT date,time,score,run_at FROM sentiment_history WHERE symbol=? ORDER BY run_at ASC LIMIT 500",
        (symbol,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_news_to_db(symbol, articles_data):
    fetched_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute("DELETE FROM news_cache WHERE symbol=?", (symbol,))
    for a in articles_data:
        conn.execute("INSERT INTO news_cache (symbol,title,source,polarity,fetched_at) VALUES (?,?,?,?,?)",
            (symbol, a["title"], a.get("label",""), a["polarity"], fetched_at))
    conn.commit(); conn.close()

def save_reddit_to_db(symbol, posts, scores):
    fetched_at = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute("DELETE FROM reddit_cache WHERE symbol=?", (symbol,))
    for p, score in zip(posts, scores):
        conn.execute("INSERT INTO reddit_cache (symbol,title,subreddit,upvotes,polarity,fetched_at) VALUES (?,?,?,?,?,?)",
            (symbol, p["title"], p["subreddit"], p["score"], score, fetched_at))
    conn.commit(); conn.close()

def load_news_from_db(symbol):
    conn = get_db()
    rows = conn.execute("SELECT title,source,polarity,fetched_at FROM news_cache WHERE symbol=? ORDER BY fetched_at DESC", (symbol,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def load_reddit_from_db(symbol):
    conn = get_db()
    rows = conn.execute("SELECT title,subreddit,upvotes,polarity,fetched_at FROM reddit_cache WHERE symbol=? ORDER BY fetched_at DESC", (symbol,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ================================================================
# HEADER
# ================================================================
now_utc = datetime.utcnow()
now_ist = datetime.now(IST)

st.markdown(f"""
<div class="sentinel-header">
    <div>
        <div class="sentinel-logo">SENTINEL</div>
        <div class="sentinel-tagline">Stock Intelligence & Sentiment Analysis Platform</div>
    </div>
    <div class="sentinel-clock">
        <div><span class="live-dot"></span><span>LIVE</span> · Auto-refresh 60s</div>
        <div>IST &nbsp;<span>{now_ist.strftime('%Y-%m-%d %H:%M:%S')}</span></div>
        <div>UTC &nbsp;<span>{now_utc.strftime('%Y-%m-%d %H:%M:%S')}</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# SIDEBAR
# ================================================================
with st.sidebar:
    st.markdown("## SENTINEL")
    st.markdown("---")

    raw_input = st.text_input(
        "SYMBOLS",
        "AAPL",
        help="Comma-separated symbols: AAPL, MSFT, NVDA"
    )
    stock_symbols = [s.strip().upper() for s in raw_input.split(",") if s.strip()]
    if not stock_symbols:
        st.error("Enter at least one symbol.")
        st.stop()
    if len(stock_symbols) > 5:
        st.warning("Max 5 symbols.")
        stock_symbols = stock_symbols[:5]

    st.markdown("---")
    period_options = {"1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y", "2Y": "2y"}
    selected_period_label = st.selectbox("PERIOD", list(period_options.keys()), index=2)
    selected_period = period_options[selected_period_label]

    st.markdown("---")
    st.markdown("""
    <div style="font-family:monospace;font-size:0.6rem;color:#4a6080;line-height:2;">
    SCORE THRESHOLDS<br>
    <span style="color:#00e676">▲ BUY</span>  &nbsp;&nbsp;score &gt; +0.10<br>
    <span style="color:#ffb300">◆ HOLD</span> &nbsp;−0.10 to +0.10<br>
    <span style="color:#ff3b5c">▼ SELL</span> &nbsp;score &lt; −0.10
    </div>
    """, unsafe_allow_html=True)

# ================================================================
# NEWS API
# ================================================================
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    st.error("NEWS_API_KEY is not configured. Add it to your environment before running the dashboard.")
    st.stop()
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

# ================================================================
# CACHED FETCHERS
# ================================================================
@st.cache_data(ttl=60, show_spinner=False)
def fetch_stock_data(symbol, period):
    return yf.download(symbol, period=period, auto_adjust=True)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_news(symbol):
    try:
        news = newsapi.get_everything(q=f"{symbol} stock", language="en", sort_by="publishedAt", page_size=10)
        return news["articles"], None
    except Exception as e:
        return [], str(e)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_google_news(symbol):
    try:
        url = f"https://news.google.com/rss/search?q={symbol}+stock"
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, features="xml")
        items = soup.find_all("item")[:10]
        return [{"title": i.title.text, "description": i.description.text if i.description else "",
                 "publishedAt": i.pubDate.text if i.pubDate else None} for i in items], None
    except Exception as e:
        return [], str(e)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_reddit(symbol):
    headers = {"User-Agent": "StockSentimentDashboard/1.0"}
    posts = []
    for sub in ["wallstreetbets", "stocks", "investing"]:
        try:
            url = f"https://www.reddit.com/r/{sub}/search.json?q={symbol}&sort=new&limit=10&restrict_sr=1"
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code != 200: continue
            data = resp.json()
            for item in data.get("data", {}).get("children", []):
                p = item.get("data", {})
                posts.append({"title": p.get("title",""), "body": p.get("selftext",""),
                              "score": p.get("score",0), "num_comments": p.get("num_comments",0),
                              "created_utc": p.get("created_utc",None), "subreddit": sub,
                              "url": p.get("url","")})
        except Exception:
            continue
    return posts, None if posts else "No Reddit posts found"

def compute_reddit_sentiment(posts):
    scores, positive, negative, neutral = [], 0, 0, 0
    now = datetime.now(IST)
    for p in posts:
        text = p["title"] + " " + p["body"]
        polarity = TextBlob(text).sentiment.polarity
        weight = 1.0
        if p["created_utc"]:
            try:
                pub = datetime.fromtimestamp(p["created_utc"], tz=pytz.UTC).astimezone(IST)
                hours_old = max((now - pub).total_seconds() / 3600, 0)
                weight = max(0.5 ** (hours_old / 24), 0.1)
            except Exception:
                weight = 1.0
        weight *= 1 + math.log1p(max(p["score"], 0)) / 10
        if polarity > 0.05: positive += 1
        elif polarity < -0.05: negative += 1
        else: neutral += 1
        scores.append(polarity * weight)
    avg = sum(scores) / len(scores) if scores else 0
    return avg, positive, negative, neutral, len(posts)

def compute_weighted_sentiment(articles):
    sentiments, weights, labels = [], [], []
    seen_titles, article_data = set(), []
    now = datetime.now(IST)
    for article in articles:
        title = article.get("title","") if isinstance(article, dict) else article.title.text
        if not title or title in seen_titles: continue
        seen_titles.add(title)
        content = title + " " + str(article.get("description","") or "") if isinstance(article, dict) else title
        polarity = TextBlob(content).sentiment.polarity
        pub_date_str = article.get("publishedAt") if isinstance(article, dict) else None
        weight = 1.0
        if pub_date_str:
            try:
                pub_date = datetime.strptime(pub_date_str[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.UTC)
                hours_old = max((now - pub_date.astimezone(IST)).total_seconds() / 3600, 0)
                weight = max(0.5 ** (hours_old / 24), 0.1)
            except Exception:
                weight = 1.0
        sentiments.append(polarity); weights.append(weight)
        label = "Positive" if polarity > 0.05 else ("Negative" if polarity < -0.05 else "Neutral")
        labels.append(label)
        article_data.append({"title": title, "polarity": polarity, "weight": weight, "label": label})
    total_weight = sum(weights)
    weighted_avg = sum(s * w for s, w in zip(sentiments, weights)) / total_weight if total_weight else 0
    return weighted_avg, labels, article_data

# ================================================================
# FETCH STOCK DATA
# ================================================================
all_close, all_data = {}, {}
with st.spinner("Fetching market data..."):
    for sym in stock_symbols:
        try:
            d = fetch_stock_data(sym, selected_period)
            if d.empty: st.warning(f"No data for {sym}."); continue
            if isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            d.index = pd.to_datetime(d.index)
            d = d.sort_index().ffill()
            all_data[sym] = d
            all_close[sym] = d["Close"]
        except Exception as e:
            st.warning(f"Failed to fetch {sym}: {e}")

if not all_data:
    st.error("Could not load data for any symbol.")
    st.stop()

# ================================================================
# SECTION 1 — PRICE & TECHNICALS
# ================================================================
st.markdown('<div class="section-label">01 · Market Data</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">PRICE & TECHNICALS</div>', unsafe_allow_html=True)

# Metric cards
cols = st.columns(len(all_data))
for col, (sym, d) in zip(cols, all_data.items()):
    close = d["Close"]
    latest = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    change = latest - prev
    pct = (change / prev) * 100
    direction = "pos" if change >= 0 else "neg"
    arrow = "▲" if change >= 0 else "▼"
    top_color = "green" if change >= 0 else "red"
    col.markdown(f"""
    <div class="metric-card {top_color}">
        <div class="metric-symbol">{sym}</div>
        <div class="metric-value">${latest:,.2f}</div>
        <div class="metric-delta {direction}">{arrow} {change:+.2f} ({pct:+.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    if len(stock_symbols) > 1:
        fig, ax = plt.subplots(figsize=(6, 3))
        for i, (sym, close) in enumerate(all_close.items()):
            normalized = (close / close.iloc[0]) * 100
            ax.plot(normalized.index, normalized, label=sym, color=PALETTE[i % len(PALETTE)], linewidth=2)
        ax.set_title(f"NORMALIZED PRICE — BASE 100  [{selected_period_label}]")
        ax.set_ylabel("Indexed (start = 100)")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
        ax.legend(); fig.tight_layout(); st.pyplot(fig)
    else:
        sym = list(all_data.keys())[0]
        d = all_data[sym]
        close = d["Close"]
        d["MA20"] = close.rolling(20).mean()
        d["MA50"] = close.rolling(50).mean()
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.fill_between(d.index, close, alpha=0.08, color="#00d4ff")
        ax.plot(d.index, close, label="Close", color="#00d4ff", linewidth=2)
        ax.plot(d.index, d["MA20"], label="MA20", linestyle="--", color="#7b61ff", linewidth=1.2)
        ax.plot(d.index, d["MA50"], label="MA50", linestyle="--", color="#ffb300", linewidth=1.2)
        ax.set_title(f"{sym} PRICE CHART  [{selected_period_label}]")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right")
        ax.legend(); fig.tight_layout(); st.pyplot(fig)

with chart_col2:
    # Volume chart for first symbol
    sym = list(all_data.keys())[0]
    d = all_data[sym]
    if "Volume" in d.columns:
        fig_v, ax_v = plt.subplots(figsize=(4, 3))
        colors_vol = ["#00e676" if d["Close"].iloc[i] >= d["Close"].iloc[i-1] else "#ff3b5c"
                      for i in range(len(d))]
        ax_v.bar(d.index, d["Volume"], color=colors_vol, alpha=0.8, width=1.5)
        ax_v.set_title(f"{sym} VOLUME")
        ax_v.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
        ax_v.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax_v.xaxis.get_majorticklabels(), rotation=30, ha="right")
        ax_v.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x/1e6:.0f}M'))
        fig_v.tight_layout(); st.pyplot(fig_v)

# RSI
st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
rsi_cols = st.columns(len(all_data))
for col, (i, (sym, d)) in zip(rsi_cols, enumerate(all_data.items())):
    close = d["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0); loss = -delta.clip(upper=0)
    rs = gain.rolling(14).mean() / loss.rolling(14).mean()
    rsi = (100 - (100 / (1 + rs))).clip(0, 100).ffill()
    fig_r, ax_r = plt.subplots(figsize=(4, 1.8))
    ax_r.plot(rsi.index, rsi, color=PALETTE[i % len(PALETTE)], linewidth=1.4, label="RSI")
    ax_r.axhline(70, linestyle="--", color="#ff3b5c", linewidth=0.8)
    ax_r.axhline(30, linestyle="--", color="#00e676", linewidth=0.8)
    ax_r.fill_between(rsi.index, rsi, 70, where=(rsi >= 70), alpha=0.15, color="#ff3b5c")
    ax_r.fill_between(rsi.index, rsi, 30, where=(rsi <= 30), alpha=0.15, color="#00e676")
    ax_r.set_ylim(0, 100); ax_r.set_title(f"{sym} · RSI (14)")
    ax_r.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    ax_r.xaxis.set_major_locator(mdates.MonthLocator())
    plt.setp(ax_r.xaxis.get_majorticklabels(), rotation=30, ha="right")
    fig_r.tight_layout(); col.pyplot(fig_r)

st.markdown('<hr class="sentinel-divider">', unsafe_allow_html=True)

# ================================================================
# SECTION 2 — SENTIMENT ANALYSIS
# ================================================================
st.markdown('<div class="section-label">02 · Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">SENTIMENT ANALYSIS</div>', unsafe_allow_html=True)

summary_rows = []

for sym_idx, sym in enumerate(all_data.keys()):
    sym_color = PALETTE[sym_idx % len(PALETTE)]
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;margin-top:1.5rem;">
        <div style="width:3px;height:24px;background:{sym_color};border-radius:2px;"></div>
        <div style="font-family:'Space Mono',monospace;font-size:1rem;font-weight:700;color:{sym_color};letter-spacing:0.15em;">{sym}</div>
        <div style="flex:1;height:1px;background:#1e2d45;"></div>
    </div>
    """, unsafe_allow_html=True)

    news_col, reddit_col = st.columns([1, 1])

    # ── NEWS ──
    with news_col:
        st.markdown('<div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.2em;color:#6a8aaa;margin-bottom:0.6rem;">NEWSFLOW</div>', unsafe_allow_html=True)
        with st.spinner(f"Fetching news..."):
            articles, err = fetch_news(sym)
            if not articles:
                articles, _ = fetch_google_news(sym)

        news_avg = 0.0
        news_labels = []
        if not articles:
            st.warning("No news articles found.")
        else:
            news_avg, news_labels, article_data = compute_weighted_sentiment(articles)
            save_news_to_db(sym, article_data)
            for a in article_data[:8]:
                css_cls = "pos" if a["label"]=="Positive" else ("neg" if a["label"]=="Negative" else "neu")
                badge_cls = css_cls
                st.markdown(f"""
                <div class="news-item {css_cls}">
                    <div class="news-title">{a['title']}</div>
                    <div class="news-meta">
                        <span class="score-badge {badge_cls}">{a['label'].upper()} {a['polarity']:+.2f}</span>
                        <span>wt: {a['weight']:.2f}x</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:monospace;font-size:0.7rem;color:#6a8aaa;margin-top:0.5rem;">AVG NEWS SCORE &nbsp;<span style="color:#c8d8f0;font-weight:700;">{news_avg:+.4f}</span></div>', unsafe_allow_html=True)

    # ── REDDIT ──
    with reddit_col:
        st.markdown('<div style="font-family:monospace;font-size:0.65rem;letter-spacing:0.2em;color:#6a8aaa;margin-bottom:0.6rem;">SOCIAL PULSE · REDDIT</div>', unsafe_allow_html=True)
        with st.spinner(f"Fetching Reddit..."):
            posts, rd_err = fetch_reddit(sym)

        rd_avg = 0.0
        positive_count = negative_count = neutral_count = 0
        if not posts:
            st.warning("No Reddit posts found.")
        else:
            rd_avg, positive_count, negative_count, neutral_count, total = compute_reddit_sentiment(posts)
            reddit_polarities = [TextBlob(p["title"]+" "+p["body"]).sentiment.polarity for p in posts]
            save_reddit_to_db(sym, posts, reddit_polarities)

            # Mini metrics
            m1, m2, m3, m4 = st.columns(4)
            for mc, lbl, val, color in [
                (m1, "TOTAL", total, "#c8d8f0"),
                (m2, "POS", positive_count, "#00e676"),
                (m3, "NEG", negative_count, "#ff3b5c"),
                (m4, "NEU", neutral_count, "#ffb300"),
            ]:
                mc.markdown(f"""<div style="text-align:center;background:#111a2b;border:1px solid #1e2d45;border-radius:4px;padding:0.4rem;">
                    <div style="font-family:monospace;font-size:0.55rem;color:#4a6080;letter-spacing:0.15em;">{lbl}</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:{color};line-height:1.1;">{val}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            for p in posts[:6]:
                polarity = TextBlob(p["title"]+" "+p["body"]).sentiment.polarity
                css_cls = "pos" if polarity > 0.05 else ("neg" if polarity < -0.05 else "neu")
                st.markdown(f"""
                <div class="reddit-item">
                    <div class="reddit-title">{p['title'][:100]}{'...' if len(p['title'])>100 else ''}</div>
                    <div class="reddit-meta">r/{p['subreddit']} · ⬆ {p['score']} · <span class="score-badge {css_cls}">{polarity:+.2f}</span></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:monospace;font-size:0.7rem;color:#6a8aaa;margin-top:0.5rem;">AVG REDDIT SCORE &nbsp;<span style="color:#c8d8f0;font-weight:700;">{rd_avg:+.4f}</span></div>', unsafe_allow_html=True)

    # ── COMBINED SCORE ──
    if articles and posts:
        combined_avg = round(0.6 * news_avg + 0.4 * rd_avg, 4)
        source_note = "60% News · 40% Reddit"
    elif articles:
        combined_avg = round(news_avg, 4)
        source_note = "News only"
    elif posts:
        combined_avg = round(rd_avg, 4)
        source_note = "Reddit only"
    else:
        combined_avg = 0.0
        source_note = "No data"

    action = "BUY" if combined_avg > 0.1 else ("SELL" if combined_avg < -0.1 else "HOLD")
    score_color = "#00e676" if action == "BUY" else ("#ff3b5c" if action == "SELL" else "#ffb300")

    st.markdown(f"""
    <div style="background:#111a2b;border:1px solid #1e2d45;border-radius:6px;padding:1rem 1.5rem;
                margin-top:1rem;display:flex;align-items:center;justify-content:space-between;">
        <div>
            <div style="font-family:monospace;font-size:0.6rem;letter-spacing:0.2em;color:#4a6080;">COMBINED SIGNAL · {source_note}</div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:2.5rem;color:{score_color};line-height:1.1;margin-top:2px;">{combined_avg:+.4f}</div>
        </div>
        <div style="text-align:right;">
            <div class="action-pill {action}">{action}</div>
            <div style="font-family:monospace;font-size:0.6rem;color:#4a6080;margin-top:6px;">RECOMMENDED ACTION</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    record_sentiment(sym, combined_avg)
    summary_rows.append({
        "Symbol": sym, "Weighted Sentiment": combined_avg, "Action": action,
        "Labels": news_labels, "Positive": positive_count, "Negative": negative_count,
        "Color": sym_color,
    })

st.markdown('<hr class="sentinel-divider">', unsafe_allow_html=True)

# ================================================================
# SECTION 3 — COMPARISON DASHBOARD
# ================================================================
if len(summary_rows) > 1:
    st.markdown('<div class="section-label">03 · Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">CROSS-SYMBOL OVERVIEW</div>', unsafe_allow_html=True)

    comp_cols = st.columns(len(summary_rows))
    for col, row in zip(comp_cols, summary_rows):
        score = row["Weighted Sentiment"]
        action = row["Action"]
        score_color = "#00e676" if action=="BUY" else ("#ff3b5c" if action=="SELL" else "#ffb300")
        col.markdown(f"""
        <div class="gauge-wrap" style="border-top: 2px solid {row['Color']};">
            <div style="font-family:monospace;font-size:0.6rem;letter-spacing:0.2em;color:#4a6080;">{row['Symbol']}</div>
            <div class="gauge-score" style="color:{score_color};">{score:+.2f}</div>
            <div class="gauge-label">Sentiment Score</div>
            <div><span class="action-pill {action}">{action}</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Sentiment distribution
    st.markdown("<br>", unsafe_allow_html=True)
    dist_cols = st.columns(len(summary_rows))
    for col, row in zip(dist_cols, summary_rows):
        if not row.get("Labels"): continue
        df_labels = pd.DataFrame(row["Labels"], columns=["Sentiment"])
        counts = df_labels["Sentiment"].value_counts().reindex(["Positive","Neutral","Negative"]).fillna(0)
        fig_d, ax_d = plt.subplots(figsize=(2.8, 2))
        bars = ax_d.bar(["POS","NEU","NEG"],
                        [counts.get("Positive",0), counts.get("Neutral",0), counts.get("Negative",0)],
                        color=["#00e676","#4a6080","#ff3b5c"], width=0.5)
        ax_d.set_title(f"{row['Symbol']} NEWS SPLIT")
        for bar, val in zip(bars, [counts.get("Positive",0), counts.get("Neutral",0), counts.get("Negative",0)]):
            if val > 0:
                ax_d.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                          f'{int(val)}', ha='center', va='bottom', fontsize=6, color='#c8d8f0')
        ax_d.set_ylim(0, max(counts.max() + 1, 3))
        fig_d.tight_layout(); col.pyplot(fig_d, clear_figure=True)

    st.markdown('<hr class="sentinel-divider">', unsafe_allow_html=True)

# ================================================================
# SECTION 4 — HISTORICAL TREND
# ================================================================
st.markdown('<div class="section-label">04 · History</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">SENTIMENT TREND</div>', unsafe_allow_html=True)

tracked_symbols = list(all_data.keys())
has_history = any(len(load_history(s)) > 0 for s in tracked_symbols)

if not has_history:
    st.markdown("""
    <div style="background:#111a2b;border:1px solid #1e2d45;border-left:3px solid #00d4ff;
                border-radius:4px;padding:1rem 1.4rem;font-family:monospace;font-size:0.75rem;color:#6a8aaa;">
        No historical data yet. Sentiment scores are saved on each run.<br>
        Come back later to see your first trend chart.
    </div>
    """, unsafe_allow_html=True)
else:
    fig_h, ax_h = plt.subplots(figsize=(10, 3.5))
    all_dates = []
    for i, sym in enumerate(tracked_symbols):
        entries = load_history(sym)
        if not entries: continue
        dates = [IST.localize(datetime.strptime(e["run_at"], "%Y-%m-%d %H:%M:%S")) for e in entries]
        scores = [e["score"] for e in entries]
        all_dates.extend(dates)
        ax_h.plot(dates, scores, marker="o", markersize=4, label=sym,
                  color=PALETTE[i % len(PALETTE)], linewidth=2)
        ax_h.fill_between(dates, scores, alpha=0.05, color=PALETTE[i % len(PALETTE)])

    ax_h.axhline(0.1, linestyle="--", color="#00e676", linewidth=0.8, alpha=0.7, label="BUY +0.10")
    ax_h.axhline(-0.1, linestyle="--", color="#ff3b5c", linewidth=0.8, alpha=0.7, label="SELL -0.10")
    ax_h.axhline(0, linestyle="-", color="#4a6080", linewidth=0.5, alpha=0.4)
    ax_h.fill_between(ax_h.get_xlim() if not all_dates else [min(all_dates), max(all_dates)],
                      0.1, 1, alpha=0.03, color="#00e676")
    ax_h.fill_between(ax_h.get_xlim() if not all_dates else [min(all_dates), max(all_dates)],
                      -1, -0.1, alpha=0.03, color="#ff3b5c")
    ax_h.set_ylim(-1, 1)
    ax_h.set_ylabel("Weighted Sentiment Score")
    ax_h.set_title("SENTIMENT SCORE OVER TIME")
    if all_dates:
        ax_h.set_xlim(min(all_dates) - pd.Timedelta(days=1), max(all_dates) + pd.Timedelta(days=1))
        date_range_days = (max(all_dates) - min(all_dates)).days if len(all_dates) > 1 else 1
        if date_range_days <= 14:
            ax_h.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax_h.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        elif date_range_days <= 60:
            ax_h.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0))
            ax_h.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        else:
            ax_h.xaxis.set_major_locator(mdates.MonthLocator())
            ax_h.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
    plt.setp(ax_h.xaxis.get_majorticklabels(), rotation=30, ha="right")
    ax_h.legend(); fig_h.tight_layout(); st.pyplot(fig_h)

    # DB Expanders
    with st.expander("◈  SENTIMENT HISTORY DATABASE"):
        all_entries = []
        for sym in tracked_symbols:
            for e in load_history(sym):
                all_entries.append({"Symbol": sym, "Date": e["date"], "Time (IST)": e["time"],
                                    "Run At": e["run_at"], "Score": e["score"]})
        if all_entries:
            st.dataframe(pd.DataFrame(all_entries).sort_values("Run At", ascending=False), use_container_width=True)

    with st.expander("◈  CACHED NEWS DATABASE"):
        for sym in tracked_symbols:
            rows = load_news_from_db(sym)
            if rows:
                st.markdown(f"**{sym}**")
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with st.expander("◈  CACHED REDDIT DATABASE"):
        for sym in tracked_symbols:
            rows = load_reddit_from_db(sym)
            if rows:
                st.markdown(f"**{sym}**")
                st.dataframe(pd.DataFrame(rows), use_container_width=True)

st.markdown('<hr class="sentinel-divider">', unsafe_allow_html=True)

# ================================================================
# SECTION 5 — INVESTMENT SIGNALS
# ================================================================
st.markdown('<div class="section-label">05 · Signals</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">INVESTMENT SIGNALS</div>', unsafe_allow_html=True)

sig_cols = st.columns(len(summary_rows))
for col, row in zip(sig_cols, summary_rows):
    score = row["Weighted Sentiment"]
    action = row["Action"]
    score_color = "#00e676" if action=="BUY" else ("#ff3b5c" if action=="SELL" else "#ffb300")
    icon = "▲" if action=="BUY" else ("▼" if action=="SELL" else "◆")
    col.markdown(f"""
    <div style="background:#111a2b;border:1px solid #1e2d45;border-radius:6px;padding:1.2rem;
                border-left:4px solid {score_color};text-align:center;">
        <div style="font-family:monospace;font-size:0.6rem;letter-spacing:0.2em;color:#4a6080;margin-bottom:4px;">{row['Symbol']}</div>
        <div style="font-size:1.8rem;color:{score_color};">{icon}</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:1.8rem;color:{score_color};letter-spacing:0.1em;">{action}</div>
        <div style="font-family:monospace;font-size:0.7rem;color:#6a8aaa;">score: {score:+.4f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer-box" style="margin-top:1.5rem;">
⚠ <strong>DISCLAIMER</strong> &mdash; Signals are derived from news and social media sentiment analysis only.
They do not constitute financial advice. Sentiment analysis has inherent limitations and should never be
the sole basis for investment decisions. Past sentiment does not predict future performance.
Consult a qualified financial advisor before acting on any information shown here.
</div>
""", unsafe_allow_html=True)

# ── FOOTER ──
st.markdown(f"""
<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #1e2d45;">
    <div style="font-family:'Bebas Neue',sans-serif;font-size:1.4rem;color:#1e2d45;letter-spacing:0.3em;">SENTINEL</div>
    <div style="font-family:monospace;font-size:0.55rem;color:#2a3d55;letter-spacing:0.2em;margin-top:4px;">
        Stock Intelligence Platform · Data refreshes every 60 seconds · {now_ist.strftime('%Y-%m-%d')}
    </div>
</div>
""", unsafe_allow_html=True)