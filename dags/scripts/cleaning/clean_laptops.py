import pandas as pd
import numpy as np
import random
import re
from pathlib import Path

print("🔥 clean_laptops.py STARTED 🔥")

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "dags" / "data" / "raw" / "laptops"
CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- PICK LATEST LAPTOP RAW FILE ----------------
csv_files = sorted(RAW_DIR.glob("*.csv"))
if not csv_files:
    raise FileNotFoundError("❌ No raw laptop CSV files found")

input_file = csv_files[-1]
print(f"📥 INPUT FILE: {input_file}")

# ---------------- LOAD ----------------
df = pd.read_csv(input_file)
print(f"📊 Rows loaded: {len(df)}")

# ---------------- BASIC FIXES ----------------
if "sku" in df.columns:
    df.rename(columns={"sku": "product_id"}, inplace=True)

df.drop(columns=[c for c in ["vsp", "review_count"] if c in df.columns], inplace=True)

# ---------------- RATING ----------------
df["rating"] = df["rating"].apply(
    lambda x: random.choice([4, 5]) if pd.isna(x) else int(round(x))
)

# ---------------- PRICE & DISCOUNT ----------------
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["mrp"] = pd.to_numeric(df["mrp"], errors="coerce")

df["discount"] = np.where(
    df["mrp"] > 0,
    ((df["mrp"] - df["price"]) / df["mrp"]) * 100,
    0
).round(2)

# ---------------- CATEGORY SPLIT ----------------
def extract_categories(cat):
    if pd.isna(cat):
        return None, None
    parts = [p.strip() for p in str(cat).split(">")]
    main_cat = parts[1] if len(parts) > 1 else None
    sub_cat = parts[-1] if len(parts) > 0 else None
    return main_cat, sub_cat

df[["main_category", "sub_category"]] = df["categories"].apply(
    lambda x: pd.Series(extract_categories(x))
)

# ---------------- TITLE PARSING ----------------
def extract_ram(title):
    m = re.search(r"(\d+)\s*GB\s*RAM", str(title), re.I)
    return int(m.group(1)) if m else None

def extract_storage(title):
    m = re.search(r"(\d+)\s*GB\s*(SSD|HDD)", str(title), re.I)
    return int(m.group(1)) if m else None

def extract_display(title):
    m = re.search(r"(\d+(\.\d+)?)\s*inch", str(title), re.I)
    return float(m.group(1)) if m else None

def extract_processor(title):
    m = re.search(
        r"(Intel Core i[3579]|Ryzen\s*[3579]|Snapdragon\s*X|Apple\s*M\d)",
        str(title),
        re.I
    )
    return m.group(1) if m else None

df["ram"] = df["title"].apply(extract_ram)
df["storage"] = df["title"].apply(extract_storage)
df["display_inch"] = df["title"].apply(extract_display)
df["processor"] = df["title"].apply(extract_processor)

# ---------------- NULL HANDLING ----------------
def fill_random(series):
    values = series.dropna().tolist()
    if not values:
        return series
    return series.apply(lambda x: random.choice(values) if pd.isna(x) else x)

for col in ["ram", "storage", "display_inch", "processor"]:
    df[col] = fill_random(df[col])

# ---------------- TYPE FIX ----------------
df["product_id"] = pd.to_numeric(df["product_id"], errors="coerce").fillna(0).astype(int)
df["price"] = pd.to_numeric(df["price"], errors="coerce").fillna(0).astype(int)
df["mrp"] = pd.to_numeric(df["mrp"], errors="coerce").fillna(0).astype(int)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)

df["display_inch"] = pd.to_numeric(df["display_inch"], errors="coerce").round(1)

df["scrape_timestamp"] = pd.to_datetime(df["scrape_timestamp"], errors="coerce")
df["scrape_date"] = pd.to_datetime(df["scrape_date"], errors="coerce").dt.date

# ---------------- FINAL DROP ----------------
df.drop(columns=["categories", "title"], inplace=True)

# ---------------- SAVE ----------------
output_file = CLEAN_DIR / f"laptops_cleaned_{input_file.stem}.csv"
df.to_csv(output_file, index=False)

print(f"✅ CLEAN FILE SAVED: {output_file}")
print("🔥 clean_laptops.py FINISHED 🔥")
