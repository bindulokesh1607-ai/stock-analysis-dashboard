# 📊 Stock Market Analysis Dashboard  
### Automated ETL Pipeline • PostgreSQL Data Warehouse • Tableau KPIs & Visualizations

This project is a complete end‑to‑end data engineering and analytics workflow that extracts stock market data, loads it into a PostgreSQL warehouse, computes technical indicators, and visualizes insights through a professional Tableau dashboard.

It demonstrates:
- ETL pipeline design  
- SQL schema modeling  
- Incremental loading  
- Metadata tracking  
- KPI engineering  
- Tableau dashboard development  
- Portfolio‑ready documentation  

---

# 🏗️ Architecture Overview

### Components
| Layer | Technology | Purpose |
|-------|------------|---------|
| Data Source | Yahoo Finance API | Raw stock OHLCV data |
| ETL | Python (requests, pandas, psycopg2) | Extract, transform, load |
| Storage | PostgreSQL | Fact table + metadata table |
| BI Layer | Tableau | KPIs, charts, dashboard |
| Metadata | etl_metadata table | Tracks load timestamps & row counts |

---

# 🗄️ Database Schema

## **fact_stock_prices**
Stores daily OHLCV data for each ticker.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Unique row ID |
| ticker | TEXT | Stock symbol |
| price_date | DATE | Trading date |
| open | NUMERIC | Opening price |
| high | NUMERIC | High price |
| low | NUMERIC | Low price |
| close | NUMERIC | Closing price |
| volume | BIGINT | Trading volume |
| created_at | TIMESTAMP | ETL insert timestamp |

Index:
```sql
CREATE INDEX idx_ticker_date ON fact_stock_prices(ticker, price_date);
etl_metadata
Tracks ETL runs for monitoring and debugging.

Column	Type	Description
ticker	TEXT	Stock symbol
last_loaded_date	DATE	Most recent date loaded
last_run_timestamp	TIMESTAMP	When ETL ran
rows_loaded	INT	Number of rows inserted
⚙️ ETL Pipeline (Python)
Responsibilities
Fetch OHLCV data for each ticker

Clean & validate data

Insert into PostgreSQL

Avoid duplicates (idempotent loads)

Update metadata table

Core ETL Steps
python
1. Define tickers = ["AAPL", "AMZN", "GOOGL", "MSFT", "NVDA", "TSLA"]
2. For each ticker:
      - Call Yahoo Finance API
      - Convert JSON → pandas DataFrame
      - Clean column names
      - Insert into fact_stock_prices
      - Count rows inserted
      - Update etl_metadata
Incremental Loading Logic
sql
SELECT MAX(price_date)
FROM fact_stock_prices
WHERE ticker = 'AAPL';
ETL only loads dates greater than this value.

📈 Tableau Calculations (Technical Indicators)
1. Daily Return
tableau
(SUM([close]) - LOOKUP(SUM([close]), -1)) / LOOKUP(SUM([close]), -1)
2. 10‑Day Moving Average (MA10)
tableau
WINDOW_AVG(SUM([close]), -9, 0)
3. 10‑Day Return
tableau
(SUM([close]) - LOOKUP(SUM([close]), -10)))
/
LOOKUP(SUM([close]), -10)
4. Latest Close (KPI)
tableau
IF LAST() = 0 THEN SUM([close]) END
5. Latest 10‑Day Return (KPI)
Using a filter:

tableau
LAST() = 0
📊 Dashboard Contents
1. KPI Bar
Latest Close Price (per ticker)

Latest 10‑Day Return (per ticker)

2. Price Over Time
Area chart of closing prices

Multi‑ticker comparison

3. Volume Over Time
Bar chart of trading volume

4. Daily Returns
Bar chart showing volatility

5. 10‑Day Moving Average
Trend smoothing indicator

6. ETL Metadata Panel
Shows pipeline health

Last run timestamps

Rows loaded

🧪 Data Quality Checks
1. Duplicate detection
sql
SELECT ticker, price_date, COUNT(*)
FROM fact_stock_prices
GROUP BY 1,2
HAVING COUNT(*) > 1;
2. Null checks
sql
SELECT *
FROM fact_stock_prices
WHERE close IS NULL;
3. Metadata validation
sql
SELECT *
FROM etl_metadata
ORDER BY last_run_timestamp DESC;
🚀 How to Run the Project
1. Clone the repo
bash
git clone https://github.com/<your-username>/stock-analysis-dashboard.git
cd stock-analysis-dashboard
2. Install dependencies
bash
pip install -r requirements.txt
3. Run ETL
bash
python etl_pipeline.py
4. Open Tableau workbook
Load dashboard.twbx and refresh the PostgreSQL connection.
