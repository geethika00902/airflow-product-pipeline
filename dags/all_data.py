import requests
import csv
import math
import time
import logging
from datetime import datetime
from pathlib import Path

# ---------------- CONFIG ----------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "raw"

CATEGORIES = {
    "mobiles": "mobiles",
    "laptops": "laptops",
    "television": "tvs",
    "refrigerator": "refrigerators"
}

SEARCH_URL = "https://mdm.vijaysales.com/web/api/search/unbxd-search/v1"
REVIEWS_URL = "https://mdm.vijaysales.com/web/api/get-reviews-summary.json"

HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0",
    "origin": "https://www.vijaysales.com",
    "referer": "https://www.vijaysales.com"
}

ROWS_PER_PAGE = 30
REVIEW_BATCH_SIZE = 30
SLEEP_TIME = 0.3

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- SEARCH ----------------
def fetch_products(query, page):
    params = {
        "q": query,
        "rows": ROWS_PER_PAGE,
        "page": page,
        "filter": "price=price:[0 TO 1000000]"
    }
    r = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()

# ---------------- REVIEWS ----------------
def fetch_reviews(sku_list):
    params = {"sku": ",".join(sku_list)}
    r = requests.get(REVIEWS_URL, headers=HEADERS, params=params)
    r.raise_for_status()

    review_map = {}
    for item in r.json().get("data", []):
        review_map[item["sku"]] = {
            "rating": item.get("averageRating"),
            "review_count": item.get("totalReviewCount")
        }
    return review_map

# ---------------- MAIN SCRAPER ----------------
def scrape_category(query, folder_name):
    logging.info(f"Starting scrape for category: {query}")

    category_dir = DATA_DIR / folder_name
    category_dir.mkdir(parents=True, exist_ok=True)

    scrape_date = datetime.now().date().isoformat()
    scrape_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    first = fetch_products(query, 0)
    total_products = first["response"]["numberOfProducts"]
    total_pages = math.ceil(total_products / ROWS_PER_PAGE)

    all_rows = []
    all_skus = []

    # STEP 1: PRODUCTS
    for page in range(total_pages):
        logging.info(f"{query}: Page {page + 1}/{total_pages}")
        data = fetch_products(query, page)

        for p in data["response"]["products"]:
            sku = p.get("sku")

            all_rows.append({
                "scrape_date": scrape_date,
                "scrape_timestamp": scrape_timestamp,
                "category": query,
                "sku": sku,
                "title": p.get("title"),
                "brand": ", ".join(p.get("brand", [])),
                "price": p.get("price"),
                "mrp": p.get("mrp"),
                "vsp": p.get("vsp"),
                "availability": p.get("cityId_1_status_unx_ts"),
                "product_url": p.get("productUrl"),
                "image_url": p.get("imageUrl", [""])[0],
                "categories": p.get("categories"),
                "rating": None,
                "review_count": None
            })

            all_skus.append(sku)

        time.sleep(SLEEP_TIME)

    # STEP 2: REVIEWS
    logging.info(f"{query}: Fetching reviews")

    reviews_map = {}
    for i in range(0, len(all_skus), REVIEW_BATCH_SIZE):
        batch = all_skus[i:i + REVIEW_BATCH_SIZE]
        reviews_map.update(fetch_reviews(batch))
        time.sleep(SLEEP_TIME)

    # STEP 3: MERGE REVIEWS
    for row in all_rows:
        sku = row["sku"]
        if sku in reviews_map:
            row["rating"] = reviews_map[sku]["rating"]
            row["review_count"] = reviews_map[sku]["review_count"]

    # STEP 4: SAVE CSV
    filename = f"{query}_{scrape_date}.csv"
    filepath = category_dir / filename

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_rows[0].keys())
        writer.writeheader()
        writer.writerows(all_rows)

    logging.info(f"{query}: Saved {len(all_rows)} rows to {filepath}")

# ---------------- ENTRY ----------------
def main():
    logging.info("===== SCRAPING STARTED =====")

    for query, folder in CATEGORIES.items():
        scrape_category(query, folder)

    logging.info("===== SCRAPING FINISHED =====")

if __name__ == "__main__":
    main()
