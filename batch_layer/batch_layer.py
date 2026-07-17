from pyspark.sql import SparkSession

from pyspark.sql.functions import avg, max, min, sum, count
 
# ---------------------------------------------------

# Create Spark Session

# ---------------------------------------------------

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
 
# ---------------------------------------------------

# Read JSON files from S3

# ---------------------------------------------------

INPUT_PATH = "s3a://lambda-batch-data/raw/"

OUTPUT_PATH = "s3a://lambda-batch-data/processed/"
 
print(f"Reading data from: {INPUT_PATH}")
 
df = spark.read.option("multiLine", "true").json(INPUT_PATH)
 
print(f"Total Records: {df.count()}")
 
print("\nSchema:")

df.printSchema()
 
print("\nSample Data:")

df.show(10, truncate=False)
 
# ---------------------------------------------------

# Aggregate Data

# ---------------------------------------------------

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
 
# ---------------------------------------------------

# Save Results

# ---------------------------------------------------

print(f"Writing results to: {OUTPUT_PATH}")
 
(

    result

    .coalesce(1)

    .write

    .mode("overwrite")

    .json(OUTPUT_PATH)

)
 
print("=" * 60)

print("BATCH PROCESS COMPLETED SUCCESSFULLY")

print("=" * 60)
 
spark.stop()
 
