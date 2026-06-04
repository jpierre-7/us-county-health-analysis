# US County Health Analysis

A full-stack data analytics project analyzing county-level public health trends across the United States. Built on 293,714 observations spanning 12 health measures and ~3,000 counties from the County Health Rankings dataset.

**Live demo:** https://us-county-health-dashboard.onrender.com (*may take 5min to load)

---

## Stack

| Layer | Tool |
|---|---|
| Data cleaning & ETL | Python + pandas |
| Database | PostgreSQL (Supabase) |
| Backend API | Python + Flask |
| Visualization | Plotly Dash |
| Deployment | Render |

---

## Project Structure

```
us-county-health-analysis/
├── data/
│   ├── County_Health_Rankings.csv
│   └── cleaned_county_health_rankings.csv
├── sql/
│   ├── schema.sql
│   ├── obesity_by_state.sql
│   ├── county_obesity_rank_by_state.sql
│   ├── premature_death_nationally.sql
│   ├── unemployment_vs_uninsured_by_state.sql
│   └── best_improvement_counties.sql
├── api/
│   └── app.py
├── dashboard/
│   └── dashboard.py
├── load_data.py
├── eda.ipynb
├── connection_test.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/measures` | List all health measures |
| GET | `/api/states` | List all states |
| GET | `/api/measures/<name>/by_state` | Average value per state for a measure |
| GET | `/api/measures/<name>/trend` | National trend over time for a measure |

---

## Running Locally

1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/your-username/us-county-health-analysis.git
   cd us-county-health-analysis
   python -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Add a `.env` file with your Supabase connection string:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```

3. Set up the database schema:
   ```bash
   psql $DATABASE_URL -f sql/schema.sql
   ```

4. Run the ETL pipeline to clean and load the data:
   ```bash
   python load_data.py
   ```

5. Start the Flask API:
   ```bash
   python api/app.py
   ```

6. In a separate terminal, start the Dash dashboard:
   ```bash
   python dashboard/dashboard.py
   ```

   The dashboard will be available at `http://localhost:8050`.

---

## Data Notes

- The raw dataset contains 303,864 rows; **9,581 rows** were dropped due to missing FIPS codes. The two affected measures (`Uninsured` and `Children in poverty`) are still partially represented by rows with valid codes.
- **561 state/national aggregate rows** were dropped as out of scope for county-level analysis.
- **10 rows** for Kalawao County, HI (population ~82) were dropped due to unparseable year spans — analytically negligible.
- Duplicate FIPS codes from Alaska's borough reorganization were resolved by keeping the first occurrence per code.
- `Data Release Year` was dropped (50% null). `Numerator`, `Denominator`, and confidence intervals have high missingness by design — not all measures report them.
- The cleaned dataset contains **293,714 observations** across **12 health measures** and **~3,000 counties**.
- You will see **52 "states"** in the data. This is expected — Washington D.C. and Puerto Rico are treated as their own entities for census and public health purposes.
- A full description for measures is available [here](https://www.countyhealthrankings.org/health-data/county-health-rankings-measures). It should also be noted that 3 measures are no longer used by County Health Rankings & Roadmaps (Violent Crime Rate, Diabetic Screening, and Daily Fine Particulate Matter) as of 2025. However they were used during the timeline of the data.

---

## Key Findings

- **Quitman County, GA** showed the largest reduction in premature death rate between 2003–2008, dropping from 18,422 to 7,124 YPLL per 100,000.
- States with the highest average adult obesity rates cluster in the South and Midwest.
- Nationally, premature death rates declined consistently across the full date range of the dataset.
- A strong positive correlation exists between unemployment and uninsured rates at the state level (2008 data).
