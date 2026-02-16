import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from datetime import datetime

print("🚀 Loading MOBILES data")

# ---------------- DATABASE ----------------
DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"
engine = create_engine(DB_URL)

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[3]
CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"

# ---------------- GET LATEST CSV ----------------
csv_files = sorted(CLEAN_DIR.glob("mobiles_cleaned_*.csv"))
if not csv_files:
    raise FileNotFoundError("❌ No cleaned mobiles CSV found")

df = pd.read_csv(csv_files[-1], engine="python", on_bad_lines="skip")


# ---------------- CLEAN COLUMN NAMES ----------------
df.columns = df.columns.str.lower().str.strip()

# ---------------- FIX PRODUCT_ID ----------------
df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce")
df = df.dropna(subset=["product_id"])
df["product_id"] = df["product_id"].astype(int)

# ---------------- ADD TIMESTAMP ----------------
df["scrape_timestamp"] = datetime.now()

# ---------------- REMOVE UNWANTED COLUMNS ----------------
df.drop(columns=["scrape_date", "category"], errors="ignore", inplace=True)

# ---------------- ADD CATEGORY ----------------
df["category"] = "mobiles"

# ---------------- REMOVE DUPLICATES ----------------
df = df.drop_duplicates(subset=["product_id"])

# ---------------- TRUNCATE TABLE ----------------
with engine.begin() as conn:
    conn.execute("TRUNCATE TABLE mobiles RESTART IDENTITY CASCADE")

# ---------------- LOAD DATA ----------------
df.to_sql(
    name="mobiles",
    con=engine,
    if_exists="append",
    index=False,
    method="multi"
)

print("✅ Mobiles table refreshed successfully")
