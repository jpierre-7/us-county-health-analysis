# Project Context: US County Health Analysis

## 1. Project Overview
- **Repository:** `jpierre-7/us-county-health-analysis`
- **Location:** `/home/john/Projects/us-county-health-analysis`
- **Purpose:** A full-stack data analytics and visualization platform analyzing county-level public health metrics and socio-economic indicators across ~3,000 U.S. counties.
- **Dataset:** ~293,714 cleaned observations spanning 12 public health measures from County Health Rankings.

---

## 2. System Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│               PostgreSQL Database (Supabase)           │
│   - Tables: county, measure, fact_observations         │
└───────────────────────────▲────────────────────────────┘
                            │ SQL Queries (SQLAlchemy)
┌───────────────────────────┴────────────────────────────┐
│            Backend REST API (Flask on Render)          │
│   - us-county-health-api.onrender.com                  │
│   - Endpoints: /health, /api/measures,                 │
│                /api/measures/<name>/by_state, etc.     │
└───────────────────────────▲────────────────────────────┘
                            │ HTTP JSON API Requests
┌───────────────────────────┴────────────────────────────┐
│          Frontend Dashboard (Plotly Dash on Render)    │
│   - us-county-health-dashboard.onrender.com            │
│   - Visualizations: Bar chart, Line chart, Choropleth  │
└────────────────────────────────────────────────────────┘
```

### Core Technologies
- **ETL & Data Processing:** Python 3.14, pandas, NumPy
- **Database:** PostgreSQL (hosted on Supabase Free Tier)
- **Backend API:** Flask 3.1, SQLAlchemy 2.0, psycopg2-binary, python-dotenv
- **Frontend / Visualization:** Plotly Dash 4.1, Plotly Express
- **Deployment Platform:** Render (Free Tier Web Services)
- **Automation / Cron:** GitHub Actions (`.github/workflows/keep-awake.yml`)

---

## 3. Directory Structure & Key Files

| Path | Purpose |
|---|---|
| `api/app.py` | Flask REST API connecting to Supabase PostgreSQL, exposing health checks and measure endpoints. |
| `dashboard/dashboard.py` | Plotly Dash application consuming the Flask API and rendering charts/maps. |
| `load_data.py` | ETL script that cleans the raw CSV data and populates Supabase PostgreSQL tables. |
| `connection_test.py` | Standalone script to test database connectivity using psycopg2. |
| `eda.ipynb` | Exploratory data analysis Jupyter notebook for initial data discovery. |
| `sql/schema.sql` | PostgreSQL schema definitions (`county`, `measure`, `fact_observations`). |
| `sql/*.sql` | Analytical SQL queries for specific public health insights (obesity, premature death, etc.). |
| `.github/workflows/keep-awake.yml` | GitHub Actions cron workflow to keep Supabase DB active by pinging the API every 3 days. |
| `requirements.txt` | Python dependencies for local development and Render deployment. |
| `README.md` | Comprehensive project documentation and local setup instructions. |

---

## 4. API Endpoints

- `GET /health` and `GET /api/health`: Executes `SELECT 1` against Supabase to verify DB connectivity; returns 200 (healthy) or 503 (unhealthy).
- `GET /api/measures`: Retrieves distinct health measures (`measure_id`, `measure_name`).
- `GET /api/states`: Retrieves distinct list of states.
- `GET /api/measures/<measure_name>/by_state`: Aggregates average metric values per state.
- `GET /api/measures/<measure_name>/trend`: Aggregates national average values over time by year.

---

## 5. Deployment & Infrastructure Details

### Render Free Tier Constraints:
- **Spin-Down on Inactivity:** Free web services spin down after 15 minutes of inactivity.
- **Cold Start Delays:** Cold starts on Render take ~30–60 seconds to boot up containers and accept HTTP connections.
- **Inter-service Dependency:** The Dash frontend depends on the Flask API, which in turn depends on Supabase PostgreSQL.

### Supabase Free Tier Constraints:
- **Auto-Pausing:** Projects auto-pause after 7 days of inactivity.
- **Keep-Alive:** Mitigated via GitHub Actions cron job executing every 3 days.
