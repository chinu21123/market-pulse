# 📈 Market Pulse — Smart Watchlist with Market Memory
**Built for CODE 2026 Hackathon**

> *"Don't show users everything that changed. Show them what deserves their attention."*

---

## 🌟 The Core Problem & Differentiator

Most financial watchlists bombard users with arbitrary green and red tickers, raw percentage changes, and noisy fluctuations. Users returning to their screen after 4 hours or overnight are forced to manually inspect dozens of tickers to figure out if anything truly significant occurred.

**Market Pulse solves this with Market Memory:**
1. **Remembers Last Known State:** Captures an exact snapshot of the user's watchlist every time they leave or check the application.
2. **"While You Were Away" Dashboard:** Upon returning, calculates the exact delta since the user's last meaningful visit (e.g. *"You were away for 4h 23m. 3 stocks changed meaningfully. 2 require attention. 26 showed no unusual movement"*).
3. **Deterministic Meaningful Change Engine:** Computes an objective **Attention Score (0–100)** using 5 statistical factors—**not** LLM hallucinations.
4. **Zero-Hallucination AI Intelligence:** Feeds only verified numerical facts into **Google Gemini** to craft executive market narratives, per-stock explanations, and persona adaptations (*Beginner*, *Intermediate*, *Advanced*).
5. **"Why Wasn't I Alerted?" Trust Engine:** Provides an objective mathematical proof explaining why quiet stocks were deemed normal (e.g. price stayed within 1-sigma ATR bounds, volume at 0.8x pace), building deep user trust.
6. **Data Confidence Monitor:** Displays real-time data freshness badges (`LIVE`, `DELAYED`, `STALE`), latency metrics, and discrepancy checks.

---

## ⚙️ Architecture & Tech Stack

- **Frontend:** Next.js 14 (App Router), React, TypeScript, Tailwind CSS, Lucide Icons, Recharts.
- **Backend:** Python 3.11, FastAPI, SQLAlchemy (dual-mode PostgreSQL with instant local SQLite fallback).
- **AI Intelligence:** Google Gemini (`google-genai` SDK) with structured JSON output and persona adaptation.
- **Market Data:** Live financial market data engine via `yfinance` with in-memory TTL caching and ATR baseline analytics.

---

## 🧮 Meaningful Change Engine (Attention Score: 0–100)

The backend deterministically calculates:
$$S_{attention} = \min\left(100, \sum_{i=1}^5 w_i \cdot f_i\right)$$

1. **Snapshot Delta ($w_1 = 30\%$)**: Absolute percentage change from user's last snapshot price.
2. **Volatility Deviation ($w_2 = 25\%$)**: Movement normalized against 14-day Average True Range (ATR) Z-score.
3. **Volume Anomaly Ratio ($w_3 = 20\%$)**: Actual volume relative to 20-day historical average.
4. **Session Extremes & Gaps ($w_4 = 15\%$)**: Breach of session channel or new extreme price levels.
5. **Benchmark Divergence ($w_5 = 10\%$)**: Decoupling from broader S&P 500 benchmark (SPY).

### Classification Tiers:
- **0 – 30**: `Normal` (Routine noise, preserved attention)
- **31 – 60**: `Worth Watching` (Mild divergence or volume tick)
- **61 – 80**: `Significant` (Clear statistical shift)
- **81 – 100**: `High Attention` (Multi-sigma breakout, urgent review)

---

## 🚀 Quick Start Guide

### 1. Backend Setup (FastAPI)

```bash
cd backend

# (Optional) Create virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run server (starts on http://localhost:8000)
uvicorn app.main:app --reload --port 8000
```

*Interactive Swagger API Docs available at `http://localhost:8000/docs`.*

### 2. Frontend Setup (Next.js)

```bash
cd frontend

# Install dependencies (if not already installed)
npm install

# Start development server (starts on http://localhost:3000)
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## 🏆 Hackathon Demo Accelerators

We built special tools directly into the application for judges and evaluators:

1. **Pre-Seeded Demo Account:**
   - Email: `demo@marketpulse.com`
   - Password: `demo1234`
   - Automatically pre-seeded with a diversified watchlist (`NVDA`, `AAPL`, `TSLA`, `MSFT`, `AMD`, `AMZN`, `SPY`) and an active snapshot.
2. **Time Machine Simulator:**
   - Click the **"Time Machine Simulator"** button in the top navbar.
   - Choose a simulated time jump (e.g. *4h 23m* or *1 Day*) and a market scenario (*Tech Earnings Divergence*, *Broad Volatility Shock*, or *Calm Market*).
   - Instantly triggers the Market Memory and Meaningful Change Engine without waiting 4 hours in real time!
3. **Persona Adaptation Toggle:**
   - Toggle between **Beginner**, **Intermediate**, and **Advanced** in the header or on the AI Market Story card to see Gemini adapt its explanations dynamically without changing verified market facts.
4. **"Why Wasn't I Alerted?" Inspection:**
   - Switch to the "Normal Movement" tab and click the **"Why wasn't I alerted?"** button on any normal stock to view the transparent mathematical proof.
