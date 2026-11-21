import os
import sys
import psycopg2
import pyarrow.dataset as ds

month = sys.argv[1]
failures = []

# Layer 1: Silver files written by Spark
silver_rows = ds.dataset(f"data/silver/yellow/month={month}").count_rows()

# Layers 2 and 3: database tables
conn = psycopg2.connect(host=os.environ.get("PG_HOST", "localhost"), port=5432, dbname="taxi", user="taxi", password="taxi")
cur = conn.cursor()

cur.execute("SELECT count(*) FROM staging.trips_silver WHERE pickup_month = %s", (month,))
staged_rows = cur.fetchone()[0]

cur.execute("SELECT count(*), count(DISTINCT trip_id) FROM analytics.fct_trips")
fact_rows, distinct_ids = cur.fetchone()

cur.execute("""SELECT count(*) FROM analytics.fct_trips
               WHERE fare_amount < 0 OR trip_distance <= 0 OR dropoff_at < pickup_at""")
invalid_rows = cur.fetchone()[0]
conn.close()

print(f"silver_files={silver_rows} staging={staged_rows} fact={fact_rows}")
print(f"distinct_trip_ids={distinct_ids} invalid_rows={invalid_rows}")

if silver_rows != staged_rows:
    failures.append(f"Silver ({silver_rows}) != staging ({staged_rows})")
if staged_rows != fact_rows:
    failures.append(f"staging ({staged_rows}) != fact ({fact_rows})")
if fact_rows != distinct_ids:
    failures.append(f"duplicate trip_ids: {fact_rows - distinct_ids}")
if invalid_rows:
    failures.append(f"{invalid_rows} invalid rows in fact table")

if failures:
    for f in failures:
        print("FAIL:", f)
    sys.exit(1)
print("PASS: all layers reconcile")
