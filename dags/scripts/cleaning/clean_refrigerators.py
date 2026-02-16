import pandas as pd
import numpy as np
import random
import re
from pathlib import Path

print("🔥 clean_refrigerators.py STARTED 🔥")

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "dags" / "data" / "raw" / "refrigerators"

CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# Pick latest raw file
csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("❌ No refrigerator CSV found")

input_file = csv_files[-1]
print(f"📥 INPUT FILE: {input_file}")

# ---------------- LOAD ----------------
df = pd.read_csv(input_file)
print(f"📊 Rows loaded: {len(df)}")

# ---------------- RENAME ----------------
if "sku" in df.columns:
    df.rename(columns={"sku": "product_id"}, inplace=True)

# ---------------- DROP UNUSED ----------------
df.drop(columns=[c for c in ["vsp", "review_count"] if c in df.columns], inplace=True)

# ---------------- RATING ----------------
df["rating"] = df["rating"].apply(
    lambda x: random.choice([4, 5]) if pd.isna(x) else int(round(x))
)

# ---------------- DISCOUNT ----------------
df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["mrp"] = pd.to_numeric(df["mrp"], errors="coerce")

df["discount"] = ((df["mrp"] - df["price"]) / df["mrp"]) * 100
df["discount"] = df["discount"].round(2)

# ---------------- CATEGORY SPLIT ----------------
def extract_main(cat):
    if pd.isna(cat):
        return np.nan
    parts = [x.strip() for x in str(cat).split(">")]
    return parts[1] if len(parts) > 1 else np.nan

def extract_sub(cat):
    if pd.isna(cat):
        return np.nan
    parts = [x.strip() for x in str(cat).split(">")]
    return parts[-1]

df["main_category"] = df["categories"].apply(extract_main)
df["sub_category"] = df["categories"].apply(extract_sub)

# ---------------- TITLE EXTRACTION ----------------
def extract_capacity(title):
    m = re.search(r"(\d+)\s*L", str(title), re.I)
    return int(m.group(1)) if m else np.nan

def extract_star(title):
    m = re.search(r"(\d)\s*Star", str(title), re.I)
    return int(m.group(1)) if m else np.nan

def extract_model(title):
    m = re.search(r"\(([^)]+)\)", str(title))
    return m.group(1) if m else np.nan

df["capacity_litres"] = df["title"].apply(extract_capacity)
df["star_rating"] = df["title"].apply(extract_star)
df["model_name"] = df["title"].apply(extract_model)

# ---------------- FILL NULLS RANDOMLY ----------------
for col in ["capacity_litres", "star_rating", "model_name", "main_category", "sub_category"]:
    non_null = df[col].dropna().tolist()
    if non_null:
        df[col] = df[col].apply(lambda x: random.choice(non_null) if pd.isna(x) else x)

# ---------------- DATATYPE FIX ----------------
int_cols = ["product_id", "price", "mrp", "capacity_litres", "star_rating", "rating"]

for col in int_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["scrape_timestamp"] = pd.to_datetime(df["scrape_timestamp"], errors="coerce")

# ---------------- FINAL DROP ----------------
df.drop(columns=["title", "categories"], inplace=True)

# ---------------- SAVE ----------------
output_file = CLEAN_DIR / f"refrigerators_cleaned_{input_file.stem}.csv"
df.to_csv(output_file, index=False)

print(f"✅ CLEAN FILE SAVED: {output_file}")
print("🔥 clean_refrigerators.py FINISHED 🔥")
