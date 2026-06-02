# US County Health Analysis

A full-stack data analytics project built with Python, PostgreSQL, Flask, and Plotly Dash. Analyzes 300k+ rows of US county-level public health data from the County Health Rankings dataset.

\* You will see 52 states in the cleaned dataset. This isn't an error as both Washington DC and Puerto Rico are treated as their own entity for census and public health data purposes.

**Live demo:**
https://us-county-health-dashboard.onrender.com

---

## Stack

| Layer | Tool |
|---|---|
| Data cleaning | Python + pandas |
| Database | PostgreSQL (hosted on Supabase) |
| Backend API | Python + Flask |
| Visualization | Plotly Dash |
| Deployment | Render |

---

## Project Structure

```
us-county-health-analysis/
├── data/
│   └── County_Health_Rankings.csv
├── etl/
│   └── load_data.py
├── sql/
│   ├── schema.sql
│   ├── obesity_by_state.sql
│   └── county_rankings.sql
├── api/
│   └── app.py
├── dashboard/
│   └── dashboard.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Running locally

1. 

---

## Key findings

* Quitman County, GA showed the largest reduction in premature death rate between 2003-2008, dropping from 18,422 to 7,124 YPLL per 100,000.
