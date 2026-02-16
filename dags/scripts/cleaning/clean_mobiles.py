import pandas as pd
import random
import re
from pathlib import Path
from datetime import datetime

print("🔥 clean_mobiles.py STARTED 🔥")

# ---------------- PATHS ----------------
BASE_DIR = Path(__file__).resolve().parents[3]

RAW_DIR = BASE_DIR / "dags" / "data" / "raw" / "mobiles"
CLEAN_DIR = BASE_DIR / "dags" / "data" / "clean"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- LOAD LATEST FILE ----------------
csv_files = sorted(RAW_DIR.glob("*.csv"), key=lambda x: x.stat().st_mtime, reverse=True)
if not csv_files:
    raise FileNotFoundError("❌ No raw mobiles CSV found")

input_file = csv_files[0]
print(f"📥 INPUT FILE: {input_file}")

df = pd.read_csv(input_file)
print(f"📊 Rows loaded: {len(df)}")

# ---------------- RENAME & DROP ----------------
df.rename(columns={"sku": "product_id"}, inplace=True)

df.drop(columns=[c for c in ["vsp", "review_count"] if c in df.columns], inplace=True)

# ---------------- TYPE CONVERSION ----------------
num_cols = ["product_id", "price", "mrp", "rating"]
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["scrape_timestamp"] = pd.to_datetime(df["scrape_timestamp"], errors="coerce")

# ---------------- RATING ----------------
df["rating"] = df["rating"].apply(
    lambda x: random.choice([4, 5]) if pd.isna(x) else x
)

# ---------------- DISCOUNT ----------------
df["discount"] = ((df["mrp"] - df["price"]) / df["mrp"]) * 100
df["discount"] = df["discount"].round(2)

# ---------------- CATEGORY SPLIT ----------------
def extract_main_category(cat):
    if pd.isna(cat):
        return None
    parts = [p.strip() for p in str(cat).split(">")]
    return parts[1] if len(parts) > 1 else None

df["main_category"] = df["categories"].apply(extract_main_category)

# ---------------- SUB CATEGORY ----------------
df["sub_category"] = df["brand"].apply(
    lambda x: "ios" if isinstance(x, str) and "apple" in x.lower() else "android"
)

# ---------------- TITLE PARSING ----------------
def extract_storage(title):
    m = re.search(r"(\d+)\s*GB", str(title), re.I)
    return int(m.group(1)) if m else None

def extract_ram(title):
    m = re.search(r"(\d+)\s*GB\s*RAM", str(title), re.I)
    return int(m.group(1)) if m else None

def extract_battery(title):
    m = re.search(r"(\d{4,5})\s*mAh", str(title), re.I)
    return int(m.group(1)) if m else None

def extract_processor(title):
    patterns = [
        r"(Snapdragon\s*\d+)",
        r"(Apple\s*A\d+)",
        r"(Dimensity\s*\d+)",
        r"(Exynos\s*\d+)",
        r"(Helio\s*\w+)"
    ]
    for p in patterns:
        m = re.search(p, str(title), re.I)
        if m:
            return m.group(1)
    return None

df["storage_gb"] = df["title"].apply(extract_storage)
df["ram_gb"] = df["title"].apply(extract_ram)
df["battery_mah"] = df["title"].apply(extract_battery)
df["processor"] = df["title"].apply(extract_processor)

# ---------------- FIX PROCESSOR NULLS (IMPORTANT PART) ----------------
processor_values = df["processor"].dropna().unique().tolist()

if processor_values:
    df["processor"] = df["processor"].apply(
        lambda x: random.choice(processor_values) if pd.isna(x) else x
    )
else:
    df["processor"] = "Unknown"

# ---------------- FILL OTHER NULLS ----------------
def fill_random(series):
    values = series.dropna().tolist()
    if not values:
        return series
    return series.apply(lambda x: random.choice(values) if pd.isna(x) else x)

for col in ["storage_gb", "ram_gb", "battery_mah", "main_category"]:
    df[col] = fill_random(df[col])

# ---------------- DROP UNUSED ----------------
df.drop(columns=["title", "categories"], inplace=True)

# ---------------- SAVE ----------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = CLEAN_DIR / f"mobiles_cleaned_{timestamp}.csv"

df.to_csv(output_file, index=False, encoding="utf-8")

print(f"✅ CLEANED FILE SAVED AT:\n{output_file}")
print("🔥 clean_mobiles.py FINISHED 🔥")
