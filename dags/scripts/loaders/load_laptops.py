import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime

print("🚀 Loading LAPTOPS data")

DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
engine = create_engine(DB_URL)

BASE_DIR = Path(__file__).resolve().parents[3]
CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"

csv_files = sorted(CLEAN_DIR.glob("laptops_cleaned_*.csv"))
if not csv_files:
    raise FileNotFoundError("❌ No cleaned laptops CSV found")

df = pd.read_csv(csv_files[-1])

# Clean column names
df.columns = df.columns.str.lower().str.strip()

# Add timestamp
df["scrape_timestamp"] = datetime.now()

# Remove unwanted columns
df.drop(columns=["scrape_date", "category"], errors="ignore", inplace=True)

# Rename columns
df.rename(columns={"ram": "ram_gb", "storage": "storage_gb"}, inplace=True)

# Add category
df["category"] = "laptops"

# Remove duplicates
df = df.drop_duplicates(subset=["product_id"])

# Truncate table
with engine.begin() as conn:
    conn.execute("TRUNCATE TABLE laptops RESTART IDENTITY CASCADE")

# Load data
df.to_sql(
    name="laptops",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("✅ Laptops table refreshed successfully")
