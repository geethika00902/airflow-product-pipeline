import psycopg2

print("🚀 Loading PRODUCTS_MAIN table")

conn = psycopg2.connect(
    host="postgres",
    database="airflow",
    user="airflow",
    password="airflow"
)

cur = conn.cursor()

# 1️⃣ Clear old data
cur.execute("TRUNCATE TABLE products_main;")

# 2️⃣ Insert merged data WITH CATEGORY
insert_sql = """
INSERT INTO products_main (
    scrape_timestamp,
    brand,
    product_id,
    category,
    price,
    mrp,
    discount,
    rating,
    availability,
    product_url,
    image_url,
    main_category,
    sub_category
)
SELECT scrape_timestamp, brand, product_id, category, price, mrp,
       discount, rating, availability, product_url,
       image_url, main_category, sub_category
FROM mobiles

UNION ALL
SELECT scrape_timestamp, brand, product_id, category, price, mrp,
       discount, rating, availability, product_url,
       image_url, main_category, sub_category
FROM laptops

UNION ALL
SELECT scrape_timestamp, brand, product_id, category, price, mrp,
       discount, rating, availability, product_url,
       image_url, main_category, sub_category
FROM refrigerators

UNION ALL
SELECT scrape_timestamp, brand, product_id, category, price, mrp,
       discount, rating, availability, product_url,
       image_url, main_category, sub_category
FROM televisions;
"""

cur.execute(insert_sql)
conn.commit()

cur.close()
conn.close()

print("✅ products_main table loaded successfully")
