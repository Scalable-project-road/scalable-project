from pyspark.sql import SparkSession

from pyspark.sql.functions import avg, max, min, sum, count
 
# ==========================================================

# CREATE SPARK SESSION

# ==========================================================
 
spark = (

    SparkSession.builder

    .appName("Luas Batch Layer")

    .config(

        "spark.hadoop.fs.s3a.aws.credentials.provider",

        "com.amazonaws.auth.InstanceProfileCredentialsProvider"

    )

    .config(

        "spark.hadoop.fs.s3a.impl",

        "org.apache.hadoop.fs.s3a.S3AFileSystem"

    )

    .getOrCreate()

)
 
spark.sparkContext.setLogLevel("WARN")
 
print("=" * 60)

print("LUAS BATCH PROCESSING STARTED")

print("=" * 60)
 
# ==========================================================

# PATHS

# ==========================================================
 
INPUT_PATH = "s3a://lambda-batch-data/raw/"

OUTPUT_PATH = "s3a://lambda-batch-data/processed/"
 
print(f"Reading data from: {INPUT_PATH}")
 
# ==========================================================

# READ JSON FILES

# ==========================================================
 
df = (

    spark.read

    .option("recursiveFileLookup", "true")

    .option("multiLine", "true")

    .json(INPUT_PATH)

)
 
print("\nSchema inferred by Spark:")

df.printSchema()
 
print("\nFiles detected by Spark:")

files = df.inputFiles()
 
for f in files:

    print(f)
 
print(f"\nTotal files found: {len(files)}")
 
total_records = df.count()
 
print(f"\nTotal Records : {total_records}")
 
if total_records == 0:

    print("\nERROR: Spark found no records.")

    spark.stop()

    exit()
 
print("\nSample Data")

df.show(10, truncate=False)
 
# ==========================================================

# AGGREGATION

# ==========================================================
 
result = (

    df.groupBy("line")

      .agg(

          count("*").alias("records"),

          sum("passenger_journeys").alias("total_passengers"),

          avg("passenger_journeys").alias("average_passengers"),

          max("passenger_journeys").alias("maximum_passengers"),

          min("passenger_journeys").alias("minimum_passengers")

      )

      .orderBy("line")

)
 
print("=" * 60)

print("BATCH RESULTS")

print("=" * 60)
 
result.show(truncate=False)
 
# ==========================================================

# SAVE RESULTS

# ==========================================================
 
print(f"\nWriting results to {OUTPUT_PATH}")
 
(

    result.coalesce(1)

    .write

    .mode("overwrite")

    .json(OUTPUT_PATH)

)
 
print("\nOutput written successfully.")
 
print("=" * 60)

print("LUAS BATCH PROCESS COMPLETED")

print("=" * 60)
 
spark.stop()
 
