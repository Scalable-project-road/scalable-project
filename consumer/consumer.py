import boto3
import time
from datetime import datetime
 
# AWS Configuration
REGION = "us-east-1"
STREAM_NAME = "luas-stream"
BUCKET_NAME = "luas-analytics-project-2026"
 
# Number of records to buffer before uploading to S3
BUFFER_SIZE = 100
 
# AWS Clients
kinesis = boto3.client("kinesis", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)
 
print("=" * 60)
print("Starting Luas Kinesis Consumer")
print("=" * 60)
 
# Get stream description
response = kinesis.describe_stream(StreamName=STREAM_NAME)
 
shard_id = response["StreamDescription"]["Shards"][0]["ShardId"]
 
print(f"Connected to Stream: {STREAM_NAME}")
print(f"Using Shard: {shard_id}")
 
# Get shard iterator
iterator_response = kinesis.get_shard_iterator(
    StreamName=STREAM_NAME,
    ShardId=shard_id,
    ShardIteratorType="LATEST"
)
 
shard_iterator = iterator_response["ShardIterator"]
 
print("\nWaiting for incoming records...\n")
 
buffer = []
 
while True:
 
    response = kinesis.get_records(
        ShardIterator=shard_iterator,
        Limit=100
    )
 
    shard_iterator = response["NextShardIterator"]
 
    records = response["Records"]
 
    if records:
 
        for record in records:
 
            payload = record["Data"].decode("utf-8")
 
            # Store JSON string in buffer
            buffer.append(payload)
 
        print(f"Received {len(records)} records | Buffer: {len(buffer)}")
 
        # Upload once buffer reaches BUFFER_SIZE
        if len(buffer) >= BUFFER_SIZE:
 
            filename = (
                "raw-data/batch_"
                + datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                + ".json"
            )
 
            # JSON Lines format (one JSON object per line)
            body = "\n".join(buffer)
 
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=filename,
                Body=body
            )
 
            print("=" * 60)
            print(f"Uploaded {len(buffer)} records")
            print(f"S3 File: {filename}")
            print("=" * 60)
 
            # Clear buffer
            buffer.clear()
 
    else:
        print("Waiting for new records...")
 
    time.sleep(2)
