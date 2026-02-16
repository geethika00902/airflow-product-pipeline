import pandas as pd
import numpy as np
import random
import re
from pathlib import Path

print("🔥 clean_tvs.py STARTED 🔥")

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "dags" / "data" / "raw" / "tvs"

CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# Pick latest raw file
csv_files = sorted(RAW_DIR.glob("*.csv"))

if not csv_files:
    raise FileNotFoundError("❌ No TV CSV file found")

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
def extract_screen_size(title):
    m = re.search(r"(\d{2})\s*(?:inch|\"|inches)", str(title), re.I)
    return int(m.group(1)) if m else np.nan

def extract_resolution(title):
    title = str(title).lower()
    if "8k" in title:
        return "8K"
    if "4k" in title or "uhd" in title:
        return "4K UHD"
    if "full hd" in title:
        return "Full HD"
    if "hd ready" in title:
        return "HD Ready"
    if "oled" in title:
        return "OLED"
    if "qled" in title:
        return "QLED"
    return np.nan

df["screen_size"] = df["title"].apply(extract_screen_size)
df["resolution"] = df["title"].apply(extract_resolution)

# ---------------- FILL NULLS RANDOMLY ----------------
for col in ["screen_size", "resolution", "main_category", "sub_category"]:
    non_null = df[col].dropna().tolist()
    if non_null:
        df[col] = df[col].apply(lambda x: random.choice(non_null) if pd.isna(x) else x)

# ---------------- DATATYPE FIX ----------------
int_cols = ["product_id", "price", "mrp", "rating", "screen_size"]

for col in int_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

df["scrape_timestamp"] = pd.to_datetime(df["scrape_timestamp"], errors="coerce")

# ---------------- FINAL DROP ----------------
df.drop(columns=["categories", "title"], inplace=True)

# ---------------- SAVE ----------------
output_file = CLEAN_DIR / f"tvs_cleaned_{input_file.stem}.csv"
df.to_csv(output_file, index=False)

print(f"✅ CLEAN FILE SAVED: {output_file}")
print("🔥 clean_tvs.py FINISHED 🔥")
