import boto3

import json

import time

from datetime import datetime
 
REGION = "us-east-1"

STREAM_NAME = "luas-speed-stream"

BUCKET_NAME = "luas-analytics-project-2026"

WINDOW_SECONDS = 10
 
kinesis = boto3.client("kinesis", region_name=REGION)

s3 = boto3.client("s3", region_name=REGION)
 
print("=" * 60)

print("Starting Luas Speed Layer")

print("=" * 60)
 
stream = kinesis.describe_stream(StreamName=STREAM_NAME)

shard_id = stream["StreamDescription"]["Shards"][0]["ShardId"]
 
iterator = kinesis.get_shard_iterator(

    StreamName=STREAM_NAME,

    ShardId=shard_id,

    ShardIteratorType="LATEST"      # <-- changed

)["ShardIterator"]
 
while True:
 
    records_buffer = []
 
    start_time = time.time()
 
    while time.time() - start_time < WINDOW_SECONDS:
 
        response = kinesis.get_records(

            ShardIterator=iterator,

            Limit=100

        )
 
        iterator = response["NextShardIterator"]
 
        if response["Records"]:
 
            print(f"Received {len(response['Records'])} records")
 
        for record in response["Records"]:
 
            payload = json.loads(record["Data"].decode("utf-8"))
 
            records_buffer.append(payload)
 
        time.sleep(1)
 
    red = [

        r for r in records_buffer

        if r["line"] == "Red Line"

    ]
 
    green = [

        g for g in records_buffer

        if g["line"] == "Green Line"

    ]
 
    result = {

        "window_start": datetime.utcnow().isoformat(),

        "window_end": datetime.utcnow().isoformat(),

        "red_records": len(red),

        "green_records": len(green),

        "red_total": sum(x["passenger_journeys"] for x in red),

        "green_total": sum(x["passenger_journeys"] for x in green),

        "red_average":

            sum(x["passenger_journeys"] for x in red) / len(red)

            if red else 0,

        "green_average":

            sum(x["passenger_journeys"] for x in green) / len(green)

            if green else 0

    }
 
    print("=" * 60)

    print(json.dumps(result, indent=4))
 
    filename = (

        "speed-results/window_"

        + datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        + ".json"

    )
 
    s3.put_object(

        Bucket=BUCKET_NAME,

        Key=filename,

        Body=json.dumps(result, indent=4)

    )
 
    print("Saved:", filename)
 
