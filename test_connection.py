import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE"),
    port=os.getenv("PGPORT")
)

print("Connected successfully!")
conn.close()

