import os
import sys
import psycopg2
from pyspark.sql import SparkSession

month = sys.argv[1]
URL = "jdbc:postgresql://" + os.environ.get("PG_HOST", "localhost") + ":5432/taxi"
PROPS = {"user": "taxi", "password": "taxi", "driver": "org.postgresql.Driver"}

# Step 1: remove this month's rows if the table already exists
conn = psycopg2.connect(host=os.environ.get("PG_HOST", "localhost"), port=5432, dbname="taxi", user="taxi", password="taxi")
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE SCHEMA IF NOT EXISTS staging")
cur.execute("SELECT to_regclass('staging.trips_silver') IS NOT NULL")
exists = cur.fetchone()[0]
if exists:
    cur.execute("DELETE FROM staging.trips_silver WHERE pickup_month = %s", (month,))
    print(f"Removed existing rows for {month}")
conn.close()

# Step 2: write Silver with Spark
spark = (SparkSession.builder
         .appName("nyc-taxi-load")
         .master("local[*]")
         .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

df = spark.read.parquet(f"data/silver/yellow/month={month}")

# First run creates the table (overwrite); later runs append
mode = "append" if exists else "overwrite"
PROPS["socketTimeout"] = "600"
PROPS["connectTimeout"] = "60"
df.coalesce(1).write.mode(mode).option("batchsize", "10000").jdbc(URL, "staging.trips_silver", properties=PROPS)

print(f"Loaded rows for {month} using mode={mode}")
spark.stop()
