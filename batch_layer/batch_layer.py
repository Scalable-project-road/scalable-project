from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, sum, count
 
# Create Spark Session
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
 
print("Reading data from S3...")
 
# Read JSON files from S3
df = spark.read.json("s3a://luas-analytics-project-2026/raw-data/")
 
print("Number of records:", df.count())
 
df.printSchema()
 
df.show(5, truncate=False)
 
# Aggregate data
result = (
    df.groupBy("line")
      .agg(
          count("*").alias("records"),
          sum("passenger_journeys").alias("total_passengers"),
          avg("passenger_journeys").alias("average_passengers"),
          max("passenger_journeys").alias("maximum_passengers"),
          min("passenger_journeys").alias("minimum_passengers")
      )
)
 
print("Batch Results")
result.show()
 
# Write results to S3
result.write.mode("overwrite").json(
    "s3a://luas-analytics-project-2026/batch-results/"
)
 
print("Results written successfully.")
 
spark.stop()
