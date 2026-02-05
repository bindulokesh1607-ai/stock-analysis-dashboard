import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE"),
    port=os.getenv("PGPORT")
)

cursor = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS fact_stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    price_date DATE NOT NULL,
    open NUMERIC(12,4),
    high NUMERIC(12,4),
    low NUMERIC(12,4),
    close NUMERIC(12,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

cursor.execute(create_table_query)
conn.commit()

print("Table created successfully!")

cursor.close()
conn.close()
