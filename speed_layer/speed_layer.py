import boto3

import json

import time

from datetime import datetime
 
REGION = "us-east-1"

STREAM_NAME = "luas-stream"

BUCKET_NAME = "luas-analytics-project-2026"
 
WINDOW_SECONDS = 10
 
kinesis = boto3.client("kinesis", region_name=REGION)

s3 = boto3.client("s3", region_name=REGION)
 
stream = kinesis.describe_stream(StreamName=STREAM_NAME)

shard_id = stream["StreamDescription"]["Shards"][0]["ShardId"]
 
iterator = kinesis.get_shard_iterator(

    StreamName=STREAM_NAME,

    ShardId=shard_id,

    ShardIteratorType="TRIM_HORIZON"

)["ShardIterator"]
 
print("Speed Layer Started")
 
while True:
 
    records_buffer = []
 
    window_start = datetime.utcnow()
 
    end_time = time.time() + WINDOW_SECONDS
 
    while time.time() < end_time:
 
        response = kinesis.get_records(

            ShardIterator=iterator,

            Limit=100

        )
 
        iterator = response["NextShardIterator"]
 
        for record in response["Records"]:
 
            payload = json.loads(record["Data"].decode("utf-8"))
 
            records_buffer.append(payload)
 
        time.sleep(1)
 
    red = [x for x in records_buffer if x["line"] == "Red Line"]

    green = [x for x in records_buffer if x["line"] == "Green Line"]
 
    result = {
 
        "window_start": window_start.isoformat(),
 
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
 
