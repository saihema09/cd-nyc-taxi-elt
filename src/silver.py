
















import sys
from pyspark.sql import SparkSession, functions as F

month = sys.argv[1]

spark = (SparkSession.builder
         .appName("nyc-taxi-silver")
         .master("local[*]")
         .config("spark.sql.session.timeZone", "UTC")
         .getOrCreate())
spark.sparkContext.setLogLevel("WARN")

bronze = spark.read.parquet(f"data/bronze/yellow/month={month}/trips.parquet")

silver = (bronze
    .filter(F.col("tpep_pickup_datetime").isNotNull())
    .filter(F.col("tpep_dropoff_datetime") >= F.col("tpep_pickup_datetime"))
    .filter(F.col("trip_distance") > 0)
    .filter(F.col("fare_amount") >= 0)
    .filter(F.col("passenger_count").isNotNull())
    .dropDuplicates()
    .withColumn("trip_id", F.sha2(F.concat_ws("|",
        F.col("VendorID").cast("string"),
        F.col("tpep_pickup_datetime").cast("string"),
        F.col("tpep_dropoff_datetime").cast("string"),
        F.col("PULocationID").cast("string"),
        F.col("DOLocationID").cast("string"),
        F.col("passenger_count").cast("string"),
        F.col("trip_distance").cast("string"),
        F.col("fare_amount").cast("string"),
        F.col("total_amount").cast("string")), 256))
    .withColumn("pickup_month", F.lit(month))
)

out = f"data/silver/yellow/month={month}"
silver.write.mode("overwrite").parquet(out)

print(f"Bronze rows: {bronze.count()}")
print(f"Silver rows: {silver.count()}")
spark.stop()
