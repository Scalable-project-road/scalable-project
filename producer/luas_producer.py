import boto3

import json

import time

import requests

from datetime import datetime
 
# ==========================================================

# AWS CONFIGURATION

# ==========================================================
 
REGION = "us-east-1"
 
BATCH_STREAM = "luas-stream"

SPEED_STREAM = "luas-speed-stream"
 
BUCKET_NAME = "lambda-batch-data"

RAW_PREFIX = "raw"
 
BATCH_SIZE = 100
 
kinesis = boto3.client("kinesis", region_name=REGION)

s3 = boto3.client("s3", region_name=REGION)
 
# ==========================================================

# DATASET

# ==========================================================
 
CSO_ENDPOINT_URL = (

    "https://ws.cso.ie/public/api.restful/"

    "PxStat.Data.Cube_API.ReadDataset/"

    "TII03/JSON-stat/1.0/en"

)
 
# ==========================================================

# WRITE BATCH TO S3

# ==========================================================
 
def upload_batch(batch):
 
    if not batch:

        return
 
    filename = (

        f"{RAW_PREFIX}/batch_"

        f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_"

        f"{int(time.time())}.json"

    )
 
    s3.put_object(

        Bucket=BUCKET_NAME,

        Key=filename,

        Body=json.dumps(batch, indent=2),

        ContentType="application/json"

    )
 
    print(f"\nUploaded batch file -> s3://{BUCKET_NAME}/{filename}")

    print(f"Records in batch : {len(batch)}\n")
 
# ==========================================================

# PRODUCER

# ==========================================================
 
def start_luas_stream():
 
    print("=" * 60)

    print("Downloading CSO Dataset")

    print("=" * 60)
 
    response = requests.get(CSO_ENDPOINT_URL)
 
    response.raise_for_status()
 
    json_data = response.json()
 
    dataset = json_data["dataset"]
 
    weeks = list(

        dataset["dimension"]["TLIST(W1)"]["category"]["label"].values()

    )
 
    lines = list(

        dataset["dimension"]["C03132V03784"]["category"]["label"].values()

    )
 
    values = dataset["value"]
 
    print(f"Loaded {len(values)} values")
 
    batch = []
 
    while True:
 
        print("=" * 60)

        print("Starting New Streaming Cycle")

        print("=" * 60)
 
        idx = 0
 
        for week in weeks:
 
            for line in lines:
 
                if line == "All Luas lines":

                    idx += 1

                    continue
 
                journeys = values[idx]
 
                if journeys is None:

                    journeys = 0

                else:

                    journeys = int(journeys)
 
                payload = {
 
                    "statistic": "Passenger Journeys",
 
                    "week": str(week),
 
                    "line": str(line),
 
                    "passenger_journeys": journeys,
 
                    "timestamp": int(time.time())
 
                }
 
                json_payload = json.dumps(payload)
 
                # --------------------------------------------------

                # Send EVERY record to Batch Stream

                # --------------------------------------------------
 
                kinesis.put_record(

                    StreamName=BATCH_STREAM,

                    Data=json_payload,

                    PartitionKey=payload["line"]

                )
 
                # --------------------------------------------------

                # Send EVERY record to Speed Stream

                # --------------------------------------------------
 
                kinesis.put_record(

                    StreamName=SPEED_STREAM,

                    Data=json_payload,

                    PartitionKey=payload["line"]

                )
 
                # --------------------------------------------------

                # Store in batch

                # --------------------------------------------------
 
                batch.append(payload)
 
                # --------------------------------------------------

                # Upload every 100 records

                # --------------------------------------------------
 
                if len(batch) >= BATCH_SIZE:
 
                    upload_batch(batch)
 
                    batch.clear()
 
                print(

                    f"{payload['week']} | "

                    f"{payload['line']} | "

                    f"{payload['passenger_journeys']} | "

                    "Sent to Kinesis"

                )
 
                idx += 1
 
                time.sleep(1)
 
        # Upload remaining records
 
        if batch:
 
            upload_batch(batch)
 
            batch.clear()
 
        print("\nDataset completed")

        print("Restarting...\n")
 
        time.sleep(2)
 
 
if __name__ == "__main__":
 
    try:

        start_luas_stream()
 
    except KeyboardInterrupt:

        print("\nProducer stopped.")
 
