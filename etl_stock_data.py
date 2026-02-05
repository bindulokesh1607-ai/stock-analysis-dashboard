import os
import time
import requests
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# List of tickers to process
TICKERS = ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "NVDA"]


def get_engine():
    """Create a SQLAlchemy engine for Azure PostgreSQL."""
    host = os.getenv("PGHOST")
    user = os.getenv("PGUSER")
    password = os.getenv("PGPASSWORD")
    database = os.getenv("PGDATABASE")
    port = os.getenv("PGPORT")

    engine = create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )
    return engine


def ensure_metadata_table(engine):
    """Create the etl_metadata table if it does not exist."""
    create_query = """
    CREATE TABLE IF NOT EXISTS etl_metadata (
        ticker VARCHAR(10) PRIMARY KEY,
        last_loaded_date DATE,
        last_run_timestamp TIMESTAMP DEFAULT NOW(),
        rows_loaded INTEGER
    );
    """
    with engine.connect() as conn:
        conn.execute(text(create_query))
    print("✔ Ensured etl_metadata table exists.")


def extract_stock_data(ticker):
    """Extract daily stock data for a given ticker from Alpha Vantage."""
    print(f"\n📥 Extracting data for {ticker}...")

    url = (
        f"https://www.alphavantage.co/query?"
        f"function=TIME_SERIES_DAILY&symbol={ticker}&apikey={API_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"❌ Network/API error for {ticker}: {e}")
        return None

    if "Time Series (Daily)" not in data:
        print(f"❌ API limit reached or invalid response for {ticker}")
        return None

    df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index")
    df.index = pd.to_datetime(df.index)
    df.columns = ["open", "high", "low", "close", "volume"]
    df = df.reset_index().rename(columns={"index": "price_date"})
    df["ticker"] = ticker

    print(f"✔ Extracted {len(df)} rows for {ticker}")
    return df


def get_latest_date(engine, ticker):
    """Return the most recent loaded date for this ticker from etl_metadata."""
    query = text(
        """
        SELECT last_loaded_date
        FROM etl_metadata
        WHERE ticker = :ticker;
        """
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"ticker": ticker}).fetchone()

    latest_date = result[0] if result and result[0] is not None else None
    return latest_date


def update_metadata(engine, ticker, latest_date, rows_loaded):
    """Insert or update metadata for a ticker."""
    query = text(
        """
        INSERT INTO etl_metadata (ticker, last_loaded_date, last_run_timestamp, rows_loaded)
        VALUES (:ticker, :latest_date, NOW(), :rows_loaded)
        ON CONFLICT (ticker)
        DO UPDATE SET
            last_loaded_date = EXCLUDED.last_loaded_date,
            last_run_timestamp = NOW(),
            rows_loaded = EXCLUDED.rows_loaded;
        """
    )

    with engine.connect() as conn:
        conn.execute(
            query,
            {
                "ticker": ticker,
                "latest_date": latest_date,
                "rows_loaded": rows_loaded,
            },
        )


def load_to_postgres(engine, df):
    """Load a DataFrame into Azure PostgreSQL."""
    try:
        df.to_sql("fact_stock_prices", engine, if_exists="append", index=False)
        print("✔ Data loaded successfully!")
    except Exception as e:
        print(f"❌ Database load error: {e}")


if __name__ == "__main__":
    print("\n🚀 Starting ETL pipeline...\n")

    engine = get_engine()
    ensure_metadata_table(engine)

    for ticker in TICKERS:
        df = extract_stock_data(ticker)

        if df is None:
            print(f"⚠ Skipping {ticker} due to extraction error.")
            print("⏳ Waiting 15 seconds to avoid API rate limits...\n")
            time.sleep(15)
            continue

        latest_date = get_latest_date(engine, ticker)
        print(f"ℹ Latest date in metadata for {ticker}: {latest_date}")

        if latest_date is not None:
            latest_date_ts = pd.to_datetime(latest_date)
            df = df[df["price_date"] > latest_date_ts]

        if df.empty:
            print(f"✔ No new data for {ticker}. Skipping load.")
        else:
            print(f"📤 Loading {len(df)} new rows for {ticker}...")
            print(df.head())
            load_to_postgres(engine, df)

            newest_date = df["price_date"].max()
            update_metadata(engine, ticker, newest_date, len(df))
            print(f"✔ Metadata updated for {ticker} (last_loaded_date={newest_date})")

        print("⏳ Waiting 15 seconds to avoid API rate limits...\n")
        time.sleep(15)

    print("🎉 ETL pipeline completed for all tickers!")
