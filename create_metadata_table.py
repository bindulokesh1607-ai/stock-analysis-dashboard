import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE"),
    port=os.getenv("PGPORT"),
    sslmode="require"
)


cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS etl_metadata (
    ticker VARCHAR(10) PRIMARY KEY,
    last_loaded_date DATE,
    last_run_timestamp TIMESTAMP DEFAULT NOW(),
    rows_loaded INTEGER
);
""")

conn.commit()
cursor.close()
conn.close()

print("Metadata table created successfully!")
