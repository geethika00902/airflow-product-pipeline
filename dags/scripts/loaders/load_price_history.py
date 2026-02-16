import psycopg2

print("🚀 Loading PRICE_HISTORY table (APPEND MODE)")

conn = psycopg2.connect(
    host="postgres",
    database="airflow",
    user="airflow",
    password="airflow"
)

cur = conn.cursor()

tables = ["mobiles", "laptops", "refrigerators", "televisions"]

for table in tables:
    insert_sql = f"""
        INSERT INTO price_history
        (
            scrape_timestamp,
            category,
            product_id,
            brand,
            price,
            mrp,
            discount
        )
        SELECT
            scrape_timestamp,
            category,
            product_id,
            brand,
            price,
            mrp,
            discount
        FROM {table}
        ON CONFLICT (product_id, scrape_timestamp)
        DO NOTHING;
    """
    cur.execute(insert_sql)

conn.commit()
cur.close()
conn.close()

print("✅ price_history updated successfully")
